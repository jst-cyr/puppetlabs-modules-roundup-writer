# Puppetlabs Modules Roundup Writer

This project automates the creation of monthly blog posts summarizing new releases in the [puppetlabs namespace on the Puppet Forge](https://forge.puppet.com/modules/puppetlabs). The pipeline fetches release data, parses changelogs, extracts highlights, and generates a finished Markdown post saved to `posts/`.

## Running the pipeline

**Use the `monthly-roundup` skill** — it holds the full procedure, the highlights YAML spec,
the polish pass, and the known failure modes. Do not reconstruct the workflow from the script
help text.

| Command | Purpose |
|---------|---------|
| `/roundup [Month] [Year]` | Run the whole pipeline for a target month (defaults to last month) |
| `/roundup-verify [post path]` | Audit a finished post against the `AGENTS.md` checklist and count contributions |
| `/module-releases-report [start] [end] [--all-publishers]` | Standalone CSV report of every module release in a date range, with per-release change/contribution counts (defaults to year-to-date). `--all-publishers` extends it to every Forge publisher, for comparing against Vox Pupuli / others |

Stages at a glance, for a target month/year:

| Stage | Script | Output |
|-------|--------|--------|
| 1 – Discover | `01_discover_modules.py --month March --year 2026` | `data/march_2026_modules_discovered.json` |
| 2 – Fetch notes | `02_fetch_release_notes.py --input <stage 1 json>` | `data/march_2026_release_notes_raw.json`, `data/raw_html/*.html` |
| 3 – Highlights | `03_extract_highlights.py --input <stage 2 json> --from-file <yaml>` | `data/march_2026_highlights_candidates.yaml` |
| 4 – Generate | `04_generate_roundup.py --highlights <yaml> --release-notes <stage 2 json>` | `posts/2026-03 March 2026 Puppetlabs Modules Roundup.md` |
| 5 – Contributions | `05_count_contributions.py --post <post md>` | Internal vs. community counts (stdout) |

Run from the repo root with `.venv\Scripts\python.exe`.

Stage 3 was originally a copy-paste handoff to GitHub Copilot; in this configuration Claude
writes the YAML directly and the script is used only to validate and install it. Stages 3 and
4 report problems as warnings and still exit 0 — read their output rather than trusting the
exit code.

Two steps need human sign-off: the curator review of the highlights YAML before Stage 4, and
the polish pass on the generated post before publishing.

`scripts/report_module_releases.py` is a **separate, standalone tool** — not a pipeline stage.
It reuses the same parsing/classification engine (`scripts/lib/`) but talks to Forge's
`v3/modules` JSON API directly instead of scraping HTML, and produces a CSV rather than a post.
See the `module-releases-report` skill and [MODULE_RELEASES_REPORT_SPEC.md](MODULE_RELEASES_REPORT_SPEC.md).

## Key Files

| File | Purpose |
|------|---------|
| `.claude/skills/monthly-roundup/` | Pipeline workflow, YAML spec, polish and validation guidance |
| `.claude/skills/module-releases-report/` | Standalone releases-report workflow |
| `AGENTS.md` | Generation rules and validation checklist for any LLM |
| `MONTHLY_ROUNDUP_TEMPLATE.md` | Post template with `{{PLACEHOLDER}}` tokens |
| `MODULE_RELEASES_REPORT_SPEC.md` | Design spec for the module-releases-report tool |
| `scripts/lib/` | Shared parsing/classification engine used by both the pipeline stages and the report |
| `config/release_notes_sources.yaml` | Overrides default Forge source for specific modules |
| `config/internal_contributors.yaml` | Hand-maintained internal vs. community handle map |
| `data/SCHEMA.md` | Schema for all intermediate JSON/YAML files and the releases-report CSV |
| `scripts/README.md` | Detailed per-stage script documentation |
| `posts/` | Final output — tracked in git |

## Setup

```powershell
pip install -r requirements.txt
```

No API keys required. Stage 3 uses Claude directly in this configuration.

## Notes

- `data/` is gitignored; `posts/` and `.claude/` are tracked.
- Raw HTML snapshots land in `data/raw_html/` for audit purposes.
- `config/release_notes_sources.yaml` maps modules that use external docs (help.puppet.com) instead of the default Forge changelog.
- Stage 1 automatically recovers modules whose *current* release lands just after the target month but which also shipped a release inside it — see `recover_overshot_releases()`. No manual patching of the discovery JSON should be needed.
- The AI Disclosure text is duplicated in `MONTHLY_ROUNDUP_TEMPLATE.md` and `AI_DISCLOSURE` in `scripts/04_generate_roundup.py`; keep the two identical.