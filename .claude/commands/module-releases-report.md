---
description: Generate a CSV report of puppetlabs module releases between two dates
argument-hint: [start-date] [end-date] [--all-publishers] — e.g. "2026-01-01 2026-08-17 --all-publishers"; omit dates for defaults
---

Run the module-releases-report skill for: **$ARGUMENTS**

If no dates were given above, do not compute "today" or "January 1st" yourself — offer to run
the script with defaults (it resolves and reports the exact range) or ask the user for a
custom range.
