---
name: module-releases-report
description: Generate a CSV report of every puppetlabs module released on the Forge between a start and end date, one row per release, with per-release change and contribution counts. Use when the user asks for a releases report, a CSV of module releases, "how many modules have been released" over some period, or a comparison against other Forge publishers (e.g. Vox Pupuli).
---

# Module Releases Report

A standalone report — not a stage of the `monthly-roundup` pipeline. It reuses that pipeline's
parsing/classification logic (via `scripts/lib/`) but talks to Forge's `v3/modules` JSON API
directly, since that API returns every module's full release history (and, for Forge-hosted
changelogs, the full changelog markdown) inline in ~2 requests total (puppetlabs-only) or ~16
requests total (`--all-publishers`, the whole Forge catalog).

By default this reports puppetlabs modules only. Pass `--all-publishers` when the user wants to
compare against other publishers (e.g. Vox Pupuli, or "everyone else on the Forge") — see
[All-publishers mode](#all-publishers-mode) below.

## Ground rules

- **Always run from the repo root.**
- **Use the project venv:** `.venv/Scripts/python.exe`. Fall back to `python` only if absent.
- The **script**, not you, computes date defaults. Never compute "today" or "January 1st"
  yourself — either pass explicit dates through, or omit the flag and let the script resolve
  and report the exact range it used.
- Output lands in the existing gitignored `data/` folder. Never commit it unless asked.

## Step 1 — Resolve the date range

If the user gave both a start and end date, normalize them to `YYYY-MM-DD` (turning "March 2026"
into `2026-03-01` is fine — that's text parsing, not date-math invention).

If either is missing, ask (don't guess):

> No date range given — use the default (January 1st of the current year through today) or
> specify a custom range?

If they want the default, don't compute it — just omit that flag and let the script fill it in.

## Step 2 — Run the script

```powershell
.venv\Scripts\python.exe scripts\report_module_releases.py --start-date <start> --end-date <end>
```

Omit `--start-date` and/or `--end-date` for whichever side should use the script's default.
Other useful flags:

- `--output <path>` — write somewhere other than the default `data/module_releases_report_<start>_<end>.csv`
- `--no-github-lookups` — skip live GitHub API calls entirely (fully offline; leaves some
  contribution counts unresolved rather than blank-vs-zero-classified)
- `--all-publishers` — report every Forge publisher, not just puppetlabs (see below)

## Step 3 — Read the resolved range back

The script prints `Resolved range: <start> to <end>` to stderr immediately, before doing any
network work. Quote that exact string back to the user — never restate a range you computed
yourself, even if it matches what you'd expect.

## Step 4 — Report the summary

The script's final stdout block has everything needed to report back:

- CSV path
- Total release rows and distinct module count
- Sums for `num_changes`, `num_community_contributions`, `num_unknown_contributions`
- Attribution resolution breakdown (inline credit / posts cache / live lookup / unresolved)
- Any **unknown handles** — flag these to the user as needing classification in
  `config/internal_contributors.yaml` (same convention as `05_count_contributions.py`)
- Any modules with blank counts (no automated bullet source) or blank `num_changes` (no
  matching changelog/docs section found) — call these out explicitly rather than letting them
  pass silently
- In `--all-publishers` mode, the **By publisher** breakdown (see above)

## All-publishers mode

Add `--all-publishers` to report releases across the entire Forge catalog (~1,500 modules,
~90+ publishers), not just puppetlabs — this is what "compare against Vox Pupuli" or "compare
against other publishers" means in practice. It adds a `publisher` column (see below) and
`_all_publishers` to the default output filename. Costs one extra minute or so of network time
(paging ~16 requests instead of ~2); attribution/rate-limit behavior is unchanged since
contribution counts still only run for puppetlabs rows.

The script's summary prints a **By publisher** breakdown (rows/modules/changes, and community
contributions where applicable) already bucketed into `puppetlabs` / `puppet (Vox Pupuli)` /
`other` — that bucketing is for the terminal summary only. Report that breakdown to the user
directly rather than re-deriving it from the CSV yourself.

## What the columns mean

One row per release. `publisher` is the **raw Forge owner slug** for that release (`puppetlabs`,
`puppet` for Vox Pupuli, or an individual maintainer's own username) — not pre-bucketed, so it
can be pivoted downstream however's useful. In puppetlabs-only mode (the default) every row is
`puppetlabs`.

Blank and `0` are **not** the same thing in the count columns:

- **blank** = not knowable from the available source — no changelog section matched this
  version, or (for the two contribution columns) this module's release notes carry no GitHub
  attribution structure at all (e.g. `sce_linux`, `sce_windows`, `cd4peadm` — prose docs on
  help.puppet.com with no PR credits to count) — **or** (in `--all-publishers` mode) this row's
  publisher simply isn't `puppetlabs`: `num_community_contributions`/`num_unknown_contributions`
  are never computed for other publishers, since `config/internal_contributors.yaml` is curated
  against Puppet/Perforce staff and doesn't generalize, and resolving attribution for the whole
  catalog would need far more live GitHub lookups than the unauthenticated rate limit allows.
- **`0`** = knowable and genuinely zero.

`num_unknown_contributions` counts bullets credited to a GitHub handle that isn't yet
classified in `config/internal_contributors.yaml` — it's a to-do counter, not a contribution
type. A nonzero value there means `num_community_contributions` may be an undercount until
someone files those handles.

## Troubleshooting

**A release shows blank `num_changes`** — no changelog section matched that version string, and
the module has no `external_docs` config entry either. Check
`https://forge.puppet.com/modules/puppetlabs/<slug>/releases` to see whether the changelog
really has no entry for that version (this happens; not every release gets changelog prose).

**Lots of `unknown` handles** — expected the first time this report is run over a range that
extends beyond what previous roundup posts have covered, since `config/internal_contributors.yaml`
was curated against the roundup's contributor list, not every contributor across all 108
puppetlabs modules' full history. Add real ones to the config as they come up.

**GitHub rate limit hit mid-run** — the script's circuit breaker stops making further live
lookups automatically and finishes the run; check the summary for `unresolved` count and
whether it says the breaker tripped. Re-run later, or with `--no-github-lookups` if you'd
rather skip that entirely.

## Reference

- [MODULE_RELEASES_REPORT_SPEC.md](../../../MODULE_RELEASES_REPORT_SPEC.md) — full design spec
- [scripts/report_module_releases.py](../../../scripts/report_module_releases.py) — the script
- [scripts/lib/](../../../scripts/lib/) — shared parsing/classification engine (also used by
  the numbered pipeline stages)
- [config/internal_contributors.yaml](../../../config/internal_contributors.yaml) — internal
  vs. community handle allowlist
- [config/release_notes_sources.yaml](../../../config/release_notes_sources.yaml) — where each
  module's release notes live
