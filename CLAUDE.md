# Puppetlabs Modules Roundup Writer

This project automates the creation of monthly blog posts summarizing new releases in the [puppetlabs namespace on the Puppet Forge](https://forge.puppet.com/modules/puppetlabs). The pipeline fetches release data, parses changelogs, extracts highlights, and generates a finished Markdown post saved to `posts/`.

## Pipeline Overview

Four stages run in sequence for a target month/year.

### Stage 1 – Discover Modules

```powershell
python scripts/01_discover_modules.py --month March --year 2026
```

Crawls the Forge listing and identifies all puppetlabs modules released in the target month.
Output: `data/march_2026_modules_discovered.json`

Automatically recovers modules whose *current* release lands just after the target month
but which also shipped a release inside it (e.g. a module released twice within days,
straddling a month boundary) — see `recover_overshot_releases()` in the script and the
note in `AGENTS.md`. No manual patching of the discovery JSON should be needed.

### Stage 2 – Fetch Release Notes

```powershell
python scripts/02_fetch_release_notes.py --input data/march_2026_modules_discovered.json
```

Parses changelogs from the Forge or from external docs (help.puppet.com) for each discovered module. Multi-release months are aggregated.
Output: `data/march_2026_release_notes_raw.json`, `data/raw_html/*.html`

### Stage 3 – Extract Highlights (Claude replaces Copilot)

This stage was originally designed for GitHub Copilot. **Claude handles it directly.**

Generate the prompt text (useful for reference):

```powershell
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json
```

**Instead of copy-pasting into Copilot, Claude should:**

1. Read `data/march_2026_release_notes_raw.json`
2. Analyze the `parsed_bullets` for each module in `release_notes` array
3. Write the highlights YAML directly to `data/march_2026_highlights_candidates.yaml`
4. Validate the YAML by running:

```powershell
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --from-file data/march_2026_highlights_candidates.yaml
```

**Required YAML structure:**

```yaml
themes:
  - title: "Theme name"
    description: "What this theme means and why it matters"
    affected_modules: "module1, module2, module3"

breaking_changes:
  - module: "module_name"
    title: "Breaking change title"
    description: "What changed and the impact"

major_features:
  - module: "module_name"
    title: "Feature name"
    description: "Why this feature is important"

security_updates:
  - module: "module_name"
    title: "Security fix"
    description: "CVE or vulnerability addressed"

single_important_updates:
  - module: "module_name"
    title: "Update title"
    description: "Why it matters"
```

**Analysis rules:**
- `themes` must span multiple modules — single-module findings are not themes.
- `breaking_changes`: removals, deprecations, or incompatible changes.
- `security_updates`: CVE fixes or security-related changes.
- Be concise and factual; avoid speculation.
- Empty lists are valid for categories with no findings.

After writing the YAML, the curator should review it — delete or edit entries that are not worth featuring — before running Stage 4.

### Stage 4 – Generate Final Post

```powershell
python scripts/04_generate_roundup.py \
  --highlights data/march_2026_highlights_candidates.yaml \
  --release-notes data/march_2026_release_notes_raw.json
```

Fills the template and writes the final post.
Output: `posts/2026-03 March 2026 Puppetlabs Modules Roundup.md`

## Full Pipeline Example (May 2026)

```powershell
python scripts/01_discover_modules.py --month May --year 2026
python scripts/02_fetch_release_notes.py --input data/may_2026_modules_discovered.json
# Claude: read data/may_2026_release_notes_raw.json, write data/may_2026_highlights_candidates.yaml
python scripts/03_extract_highlights.py --input data/may_2026_release_notes_raw.json --from-file data/may_2026_highlights_candidates.yaml
python scripts/04_generate_roundup.py --highlights data/may_2026_highlights_candidates.yaml --release-notes data/may_2026_release_notes_raw.json
```

## Post Generation Rules

See `AGENTS.md` for the full ruleset. Key points:

- Replace every `{{PLACEHOLDER}}` — none may remain in the final output.
- Modules must appear in **alphabetical order**.
- New modules (v1.0.0 with no prior monthly history): `🌟 ***New Module:*** YYYY-MM-DD (🌐 [View on the Forge](...))`.
- Regular modules: `📅 Latest release: YYYY-MM-DD (🌐 [View on the Forge](...))`.
- Match tone with existing posts in `posts/` — factual and concise, not promotional.
- Each module needs at least one concrete change bullet.

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Generation rules and validation checklist for any LLM |
| `MONTHLY_ROUNDUP_TEMPLATE.md` | Post template with `{{PLACEHOLDER}}` tokens |
| `config/release_notes_sources.yaml` | Overrides default Forge source for specific modules |
| `data/SCHEMA.md` | Schema for all intermediate JSON/YAML files |
| `scripts/README.md` | Detailed pipeline documentation |
| `posts/` | Final output — tracked in git |

## Setup

```powershell
pip install -r requirements.txt
```

No API keys required for stages 1, 2, or 4. Stage 3 uses Claude directly in this configuration.

## Notes

- `data/` is gitignored; `posts/` is tracked.
- Raw HTML snapshots land in `data/raw_html/` for audit purposes.
- `config/release_notes_sources.yaml` maps modules that use external docs (help.puppet.com) instead of the default Forge changelog.
