# Quick Start

Run a full monthly roundup in four stages.

## 1) Install dependencies

```powershell
pip install -r requirements.txt
```

## 2) Discover modules released in the target month

```powershell
python scripts/01_discover_modules.py --month March --year 2026
```

Expected output file:
- data/march_2026_modules_discovered.json

## 3) Fetch release notes and parse bullets

```powershell
python scripts/02_fetch_release_notes.py --input data/march_2026_modules_discovered.json
```

Expected output files:
- data/march_2026_release_notes_raw.json
- data/raw_html/*.html

Notes:
- Forge-backed modules are rolled up by month: if a module has multiple releases in the target month, Stage 2 aggregates bullets from all of them.
- The module `version` and `release_date` in `release_notes_raw.json` represent the latest release in that month.

## 4) Generate highlights candidates

### Option A: Claude (recommended)

Ask Claude to read `data/march_2026_release_notes_raw.json`, analyze the release notes, and write `data/march_2026_highlights_candidates.yaml` directly. See `CLAUDE.md` for the required YAML structure and analysis rules.

Then validate:

```powershell
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --from-file data/march_2026_highlights_candidates.yaml
```

### Option B: GitHub Copilot (original workflow)

```powershell
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json
```

Then:
- Copy the prompt from terminal output.
- Open Copilot chat in VS Code with Ctrl+I.
- Paste prompt and get YAML output.
- Save YAML to a file, then load it:

```powershell
python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --from-file highlight_results.yaml
```

Expected output file:
- data/march_2026_highlights_candidates.yaml

**Before running Stage 5:** Review and curate the YAML — delete or edit entries that are not worth featuring in the post.

## 5) Generate final post

```powershell
python scripts/04_generate_roundup.py --highlights data/march_2026_highlights_candidates.yaml --release-notes data/march_2026_release_notes_raw.json
```

Expected output file:
- posts/2026-03 March 2026 Puppetlabs Modules Roundup.md

Notes:
- Stage 4 uses a special release line for brand new modules (typically `1.0.0`): `🌟 ***New Module:*** YYYY-MM-DD (🌐 View on the Forge)`.

## Notes

- `config/release_notes_sources.yaml` is an override map plus a default source.
- `external_docs` should only contain modules that need non-Forge URLs.
- Any module not explicitly overridden uses `default_source: forge_changelog`.
