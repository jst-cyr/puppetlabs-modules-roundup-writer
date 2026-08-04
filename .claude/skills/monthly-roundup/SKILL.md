---
name: monthly-roundup
description: Run the monthly Puppetlabs Modules Roundup pipeline end to end — discover Forge releases for a target month, fetch and parse changelogs, author the highlights YAML, generate the post into posts/, then polish and validate it. Use whenever the user asks to produce, run, generate, or redo a monthly roundup ("run the roundup for July 2026", "do this month's roundup", "regenerate the June post"), or to re-run a single stage of that pipeline.
---

# Monthly Roundup

Produces one blog post summarizing every `puppetlabs` module released on the Puppet Forge
during a target month. Five scripted stages plus two judgment steps that are yours: writing
the highlights YAML (Stage 3) and polishing the generated post (Step 6).

The scripts are deterministic and own all the mechanical work — crawling, parsing,
alphabetizing, template filling, validation. Do not hand-write anything a script produces.

## Ground rules

- **Always run from the repo root.** Every path the scripts take is relative to it.
- **Use the project venv:** `.venv/Scripts/python.exe`. Fall back to `python` only if it's absent.
- `data/` is gitignored scratch; `posts/` is tracked. Never commit unless asked.
- Stages 3 and 4 print validation problems as **warnings and still exit 0**. Read every line
  of their output — a silent success is not the same as a clean run.
- `{month}` below means the lowercase month name (`july`), `{Month}` the capitalized one (`July`).

## Step 0 — Resolve the target and preflight

Determine month and year. If the user didn't say, the target is the **previous calendar
month** (a roundup covers a month that has ended); confirm that inference in one line rather
than asking. Then:

```powershell
.venv\Scripts\python.exe -c "import requests, bs4, yaml; print('deps ok')"
```

If that fails, run `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

Check whether `posts/` already holds a post for this month. If it does, you're regenerating —
say so and confirm before overwriting, since the existing file may carry hand edits.

## Step 1 — Discover modules

```powershell
.venv\Scripts\python.exe scripts\01_discover_modules.py --month {Month} --year {year}
```

Writes `data/{month}_{year}_modules_discovered.json`.

Sanity-check the count before moving on. Recent months have landed in the ~15–25 module
range; **0 modules means the crawl failed, not a quiet month** — see Troubleshooting.

The script already recovers modules whose current Forge release postdates the target month
but which also shipped inside it (`recover_overshot_releases()`), so month-boundary
double-releases need no manual patching. If a module you'd expect is still missing, verify
against `https://forge.puppet.com/modules/puppetlabs/{slug}/releases` before touching the
JSON by hand.

## Step 2 — Fetch and parse release notes

```powershell
.venv\Scripts\python.exe scripts\02_fetch_release_notes.py --input data\{month}_{year}_modules_discovered.json
```

Writes `data/{month}_{year}_release_notes_raw.json` and HTML snapshots to `data/raw_html/`.

Then inspect the result for modules that came back with **no `parsed_bullets`** or that are
mapped to `manual_review` in `config/release_notes_sources.yaml`. Every module in the post
needs at least one concrete bullet, so resolve these now: read the saved HTML in
`data/raw_html/`, or fetch the module's Forge changelog / help.puppet.com release notes
directly, and fill the bullets into the JSON. If a module uses a non-Forge docs URL that
isn't mapped yet, add it to `config/release_notes_sources.yaml` so next month works
unattended — that config is the durable fix, the JSON edit is not.

## Step 3 — Author the highlights YAML

This stage's script was built to hand a prompt to Copilot. Skip that: you do the analysis.

Read `data/{month}_{year}_release_notes_raw.json`, analyze `parsed_bullets` across all
modules, and write `data/{month}_{year}_highlights_candidates.yaml` yourself.

See [references/highlights-yaml.md](references/highlights-yaml.md) for the required schema
and the rules on what does and doesn't earn a slot. Read it before writing the file.

Validate:

```powershell
.venv\Scripts\python.exe scripts\03_extract_highlights.py --input data\{month}_{year}_release_notes_raw.json --from-file data\{month}_{year}_highlights_candidates.yaml
```

Warnings here do not fail the command. Read them and fix the YAML.

## Step 4 — Curator gate (stop here)

The highlights are an editorial choice, so the user makes it. Summarize what you selected —
theme titles and the modules each spans, plus counts for breaking changes, security updates,
major features, and one-offs — and ask whether to keep, cut, or reword anything.

Do not run Stage 4 until they've answered. Apply their edits to the YAML, then continue.

## Step 5 — Generate the post

```powershell
.venv\Scripts\python.exe scripts\04_generate_roundup.py --highlights data\{month}_{year}_highlights_candidates.yaml --release-notes data\{month}_{year}_release_notes_raw.json
```

Writes `posts/{year}-{MM} {Month} {year} Puppetlabs Modules Roundup.md`, where `MM` is the
**target** month. That's the current convention; posts before April 2026 used the publication
month instead, so ignore the older filenames as precedent. Read the validation output.

## Step 6 — Polish and validate

The generated file is structurally complete but reads like a template. It is not shippable
as-is: rewrite the intro and closing, and add the cross-release context the changelogs don't
carry. [references/post-polish.md](references/post-polish.md) covers what to change, the
recurring copy errors to fix, and the full pre-ship checklist. Follow it.

Then count contributions:

```powershell
.venv\Scripts\python.exe scripts\05_count_contributions.py --post "posts\{year}-{MM} {Month} {year} Puppetlabs Modules Roundup.md"
```

Any handle reported as **Unknown** needs classifying into
`config/internal_contributors.yaml` — GitHub hides private org membership, so that allowlist
is hand-maintained and only stays accurate if you extend it each month. Ask the user when a
handle's affiliation isn't obvious from its PR history.

## Step 7 — Report

Tell the user: the post path, module count, internal vs. community contribution split, what
you polished by hand, and anything still unresolved (missing bullets, unknown handles,
modules you couldn't source). Leave the file uncommitted unless they ask.

## Troubleshooting

**Stage 1 finds 0 modules** — the Forge listing markup or a header check changed. Fetch
`https://forge.puppet.com/modules/puppetlabs` and compare against the parser before assuming
no releases shipped. As a last resort the discovery JSON can be populated by hand (schema in
`data/SCHEMA.md`); Stages 2–5 work fine on a hand-built file.

**A module's bullets are empty** — see Step 2. Check `data/raw_html/` first to see what was
actually parsed.

**Stage 4 reports unresolved `{{PLACEHOLDER}}` tokens** — the highlights YAML is short a
section the template expects, or a module lacks bullets. Fix the input, don't edit the output.

**External docs 404** — help.puppet.com URL patterns are version-derived
(`2.6.0` → `260`, with an optional `v` prefix). Confirm the pattern in
`config/release_notes_sources.yaml` against the live docs URL.

## Reference

- [AGENTS.md](../../../AGENTS.md) — canonical generation ruleset and validation checklist
- [MONTHLY_ROUNDUP_TEMPLATE.md](../../../MONTHLY_ROUNDUP_TEMPLATE.md) — post structure
- [data/SCHEMA.md](../../../data/SCHEMA.md) — intermediate file schemas
- [scripts/README.md](../../../scripts/README.md) — per-stage script detail
- `posts/` — prior posts; match their tone
