---
description: Run the full monthly Puppetlabs Modules Roundup pipeline for a target month
argument-hint: [Month] [Year] — e.g. "July 2026"; omit to use last month
---

Run the monthly roundup pipeline for: **$ARGUMENTS**

If no month/year was given above, target the previous calendar month and state that inference
in one line before starting.

Follow the `monthly-roundup` skill from Step 0 through Step 7. In particular:

- Run every stage from the repo root using `.venv\Scripts\python.exe`.
- Read the output of Stages 3 and 4 carefully — they report problems as warnings and still
  exit 0.
- **Stop at the Step 4 curator gate** and wait for approval of the highlights before
  generating the post.
- Do the Step 6 polish pass; the raw generated file is not shippable.
- Leave the post uncommitted and report what's unresolved.
