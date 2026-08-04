---
description: Validate a finished roundup post against the AGENTS.md checklist and count contributions
argument-hint: [post path] — omit to check the most recent post in posts/
---

Verify the roundup post: **$ARGUMENTS**

If no path was given, use the most recently modified file in `posts/`. Report the path you
picked.

Do not rewrite the post as part of this check. Report findings, then ask before fixing
anything.

1. Walk the pre-ship checklist in the `monthly-roundup` skill's
   [post-polish reference](../skills/monthly-roundup/references/post-polish.md): leftover
   `{{` / `}}` tokens, alphabetical module order, version + date + Forge URL + at least one
   bullet per module, `🌟 ***New Module:***` wording on new modules and
   `📅 Latest release:` elsewhere, all template headings present, month/year consistent
   throughout, factual tone, correct filename.
2. Check the recurring copy errors listed in that same reference — "Puppetcore" for
   "Puppet Core" being the usual one.
3. Confirm the AI Disclosure text matches `AI_DISCLOSURE` in
   `scripts/04_generate_roundup.py` verbatim.
4. Count contributions:

   ```powershell
   .venv\Scripts\python.exe scripts\05_count_contributions.py --post "<path>"
   ```

   Report the internal vs. community split and list every **Unknown** handle that needs
   adding to `config/internal_contributors.yaml`.
5. Summarize as a pass/fail list, most serious first.
