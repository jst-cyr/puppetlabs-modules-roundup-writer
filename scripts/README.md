# Puppetlabs Module Roundup Automation Scripts

Four-stage pipeline for semi-automated generation of monthly roundup posts.

## Overview

This pipeline automates the mechanical parts of the roundup process while preserving editorial judgment:

1. **Stage 1 (Discover)**: Crawl Puppet Forge to find modules released in target month
2. **Stage 2 (Parse)**: Fetch and extract release notes from Forge and external docs
3. **Stage 3 (Curate)**: Auto-detect themes/highlights for human review
4. **Stage 4 (Generate)**: Fill template with curated highlights and module entries

## Prerequisites

Install dependencies:

```bash
pip install -r requirements.txt
```

**No API keys needed!** Stage 3 uses GitHub Copilot (Opus model) in VS Code. Just use `Ctrl+I` to invoke it.

## Usage

### Stage 1: Discover Modules

Crawl Puppet Forge listing to find all puppetlabs modules released in target month.

```bash
python scripts/01_discover_modules.py --month March --year 2026
```

**Output:**
- `data/march_2026_modules_discovered.json`

**What it does:**
- Fetches https://forge.puppet.com/modules/puppetlabs (up to 50 modules/page)
- Extracts: name, slug, version, release_date, Forge URL
- Filters for modules with `release_date` in target month
- Looks up each module in `config/release_notes_sources.yaml` to determine where to fetch release notes
- Outputs JSON with `released_in_target_month` flag for downstream stages

### Stage 2: Fetch Release Notes

Fetch and parse release notes for discovered modules.

```bash
python scripts/02_fetch_release_notes.py --input data/march_2026_modules_discovered.json
```

**Output:**
- `data/march_2026_release_notes_raw.json`
- `data/raw_html/{module}_{version}.html` (raw HTML snapshots for audit trail)

**What it does:**
- For each module where `released_in_target_month == true`:
  - Fetches Forge changelog (default) or external docs (help.puppet.com) based on config
  - Parses HTML to extract 3-5 bullet points
  - Stores raw HTML snapshot for reproducibility
- Outputs JSON with parsed bullets per module

**Source mapping** (from `config/release_notes_sources.yaml`):
- Most modules: Forge changelog (default)
- SCE modules (sce_linux, sce_windows): help.puppet.com with version-specific URL patterns
- CD modules (cd4peadm, comply): help.puppet.com with fixed URLs
- Others: manual_review (for complex cases)

### Stage 3: Extract Highlights (GitHub Copilot Analysis)

Use GitHub Copilot to intelligently analyze release notes and identify trends, themes, and highlights.

```bash
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json
```

**Output:**
- `data/march_2026_highlights_candidates.yaml` (for curator to review and edit)

**What it does:**
1. Reads all release notes from Stage 2
2. Generates a detailed analysis task/prompt
3. Displays the prompt for you to copy
4. You paste the prompt into GitHub Copilot (Ctrl+I)
5. Copilot analyzes and returns structured YAML results
6. You run the script again with `--from-file` to save results

**Step-by-step workflow:**

```bash
# Step 1: Generate analysis prompt
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json

# Step 2: In VS Code, press Ctrl+I to open GitHub Copilot
# Then paste the prompt from the terminal output

# Step 3: Copilot returns YAML—copy it to a temporary file
# (e.g., highlight_results.yaml)

# Step 4: Load the results
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --from-file highlight_results.yaml

# Step 5: Results saved to data/march_2026_highlights_candidates.yaml
```

**Why this approach?**
- No external API keys needed—uses your existing Copilot access
- Copilot's Opus model is excellent at semantic analysis
- Highlights are **dynamically determined** based on actual content
- Curator maintains editorial control before final generation

**Copilot identifies:**
- **Cross-module themes**: Patterns in multiple modules (e.g., "Puppet 8 support appears in 5 modules")
- **Breaking changes**: Removals, deprecations, incompatibilities
- **Major features**: Significant new capabilities
- **Security updates**: CVE fixes and vulnerabilities
- **Important one-offs**: Standout single-module changes

**Editor mode (optional):**
After loading the results, you can directly edit `data/march_2026_highlights_candidates.yaml` to:
- ✅ Keep highlights that are noteworthy
- ❌ Delete trivial or module-specific items
- 📝 Edit descriptions to match your wording
- ➕ Add new highlights if Copilot missed important patterns

### Stage 4: Generate Roundup

Fill template with curated highlights and module entries.

```bash
python scripts/04_generate_roundup.py \
  --highlights data/march_2026_highlights_candidates.yaml \
  --release-notes data/march_2026_release_notes_raw.json
```

**Output:**
- `posts/2026-03 March 2026 Puppetlabs Modules Roundup.md`

**What it does:**
- Reads curated highlights YAML (after curator has deleted rows)
- Reads release notes JSON
- Fills `MONTHLY_ROUNDUP_TEMPLATE.md` with:
  - Title: "Puppetlabs Modules Roundup – Month Year"
  - Intro: Month/year paragraph
  - Highlighted Updates: Themes, breaking changes, security updates (from curated YAML)
  - Module entries: Alphabetical list with version, date, URL, and bullets
  - New module entries: Automatically uses `🌟 ***New Module:***` (instead of `Latest release`) when a module appears to be a brand new release (typically `1.0.0`)
  - Closing: Standard closing paragraph
- Validates per `AGENTS.md` checklist:
  - ✓ No unresolved `{{PLACEHOLDERS}}`
  - ✓ Modules in alphabetical order
  - ✓ All Forge URLs present
  - ✓ At least 1 bullet per module
- Saves final markdown to `posts/`

## Full Workflow Example

Generate roundup for March 2026:

```bash
# Stage 1: Discover modules released in March 2026
python scripts/01_discover_modules.py --month March --year 2026

# Stage 2: Fetch release notes for those modules
python scripts/02_fetch_release_notes.py --input data/march_2026_modules_discovered.json

# Stage 3a: Generate analysis prompt for GitHub Copilot
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json

# ✨ Copy the prompt that appeared in the terminal
# Open GitHub Copilot in VS Code with Ctrl+I
# Paste the prompt and wait for Copilot to respond
# Copy the YAML results to a file (e.g., highlight_results.yaml)

# Stage 3b: Load the Copilot results
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --from-file highlight_results.yaml

# 📝 (Optional) Curator review: Edit data/march_2026_highlights_candidates.yaml
# Delete rows you don't want, add new patterns if you spot them

# Stage 4: Generate final roundup
python scripts/04_generate_roundup.py \
  --highlights data/march_2026_highlights_candidates.yaml \
  --release-notes data/march_2026_release_notes_raw.json
```

Once complete, the final roundup markdown is in `posts/2026-03 March 2026 Puppetlabs Modules Roundup.md`.

## Configuration

### Release Notes Source Mapping

Edit `config/release_notes_sources.yaml` to control where release notes are fetched from:

```yaml
release_notes_sources:
  forge_changelog:
    # Default: fetch from Forge changelog tab
    modules: [apache, docker, firewall, ...]
  
  external_docs:
    sce_linux:
      type: help_puppet_versioned
      base_url: https://help.puppet.com/sce/current/linux/
      url_pattern: scel_relnotes_{version_underscore}.htm
    sce_windows:
      type: help_puppet_versioned
      version_transform: v
      url_pattern: scew_relnotes_{version_underscore}.htm
    cd4peadm:
      type: help_puppet_fixed_url
      url: https://help.puppet.com/cd4peadm/...
```

**Version underscore examples:**
- `2.6.0` → `260`
- `2.2.1` → `221`
- With transform `v`: `2.2.1` → `v221`

## Data Schema

See `data/SCHEMA.md` for complete documentation of:
- Module Discovery JSON format
- Release Notes Raw JSON format
- Highlights Candidates YAML format
- File naming conventions
- Raw HTML snapshot storage

## Troubleshooting

**Stage 1: No modules discovered**
- Check Forge URL is accessible
- Verify release_date filtering logic (modules must have release in target month)
- Check user-agent headers aren't being blocked

**Stage 2: Missing release notes**
- Verify Forge changelog URLs are correct
- For external docs modules, check config/release_notes_sources.yaml for correct URL pattern
- Check raw_html/ directory for downloaded HTML (debug what was parsed)

**Stage 3: Copilot not responding**
- Verify GitHub Copilot is installed in VS Code
- Press Ctrl+I to open the Copilot chat panel
- Check VS Code is signed in (bottom-left profile icon)
- If prompts are truncated, manually save the full prompt from terminal output to a text file and paste into Copilot

**Stage 3: YAML parsing fails**
- Check that Copilot returned pure YAML (no markdown code blocks)
- If Copilot wrapped it in ```yaml ... ```, remove the code block markers before saving
- Validate YAML with: `python -m yaml <file.yaml>`

**Stage 3: Highlights incomplete**
- Copilot analyzes intelligently—different patterns each month based on content
- If important themes missing: edit YAML manually to add them
- You can also re-run Copilot with a slightly modified prompt asking specifically about those themes

**Stage 4: Validation errors**
- Script will print warnings if modules aren't alphabetical or URLs missing
- Check release_notes_raw.json has all required fields
- Ensure highlights_candidates.yaml was hand-curated before running Stage 4

## Manual Import Workflow (if Stages 1-2 Fail)

If Forge crawling fails, you can manually populate the JSON files:

1. Open https://forge.puppet.com/modules/puppetlabs (in browser)
2. For each module listed:
   - Copy name, version, release_date
   - Create manual entry in `data/march_2026_modules_discovered.json`
3. Run Stage 2 (fetch_release_notes.py) as normal
4. Continue with Stages 3-4

This preserves the benefits of Stages 2-4 (parsing, curation, validation) even if web scraping is problematic.
