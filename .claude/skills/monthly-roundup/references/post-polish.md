# Polishing the generated post (Step 6)

Stage 4 produces a structurally valid post with generic template prose. Every published
roundup in `posts/` has been rewritten past that point. Read the two most recent posts before
editing — they define the voice.

## What to rewrite

**Intro paragraph.** The template ships a generic "Welcome back…" opener. Replace it with a
real summary of the month: the total module count, the single biggest story, and the shape of
the rest. Link out to related articles when one exists.

**Closing ("Until Next Time!").** Replace the boilerplate with something specific to this
month — which changes deserve a closer look and why — and end by pointing at next month.

**Highlight sections.** Add the connective context a changelog can't supply: that a rollout
continues next month, that a breaking change shipped in the wrong release type and is being
corrected, that a module supersedes a manual process. A short paragraph after the bullets is
the established pattern.

**Module summaries.** Cut repetition. When fifteen modules all say "allows stdlib 10.x," vary
the phrasing or lean on the theme section instead of restating it per module. Add missing
context where a bullet is cryptic on its own.

## Recurring copy errors to fix

- **"Puppetcore" → "Puppet Core"** — appears in upstream changelog text and has needed
  correcting before.
- Product names: **Security Compliance Management** (not `comply`/`complyadm`) and
  **Continuous Delivery for PE** in prose; module slugs stay as slugs in headings.
- Bare CVE dumps and ticket IDs with no context — keep the ID, add what it fixed.
- Changelog bullets that are pure release chores ("bump version", "update README") — drop
  them if the module has better bullets.

## Leave alone

- Module ordering, version numbers, release dates, Forge URLs, and PR/author attribution
  links — all script-generated from verified data. If one looks wrong, fix the upstream JSON
  and regenerate rather than editing the post.
- The **AI Disclosure** section. Its text is emitted verbatim by `AI_DISCLOSURE` in
  `scripts/04_generate_roundup.py` and mirrored in `MONTHLY_ROUNDUP_TEMPLATE.md`. If it ever
  needs changing, change both and say so — they must stay identical.

## Pre-ship checklist

Per `AGENTS.md`, verify:

- [ ] No `{{` or `}}` tokens remain anywhere in the file.
- [ ] Module sections are in alphabetical order.
- [ ] Every module has a version, a release date, a Forge URL, and at least one concrete
      change bullet.
- [ ] New modules use `🌟 ***New Module:*** YYYY-MM-DD` with **"New Module"** wording — not
      "New Release" — and everything else uses `📅 Latest release: YYYY-MM-DD`.
- [ ] All template section headings are present and in the template's order, including
      "Until Next Time!" and the AI Disclosure.
- [ ] Title and every in-body month/year reference name the target month.
- [ ] Tone is factual, not promotional.
- [ ] Filename is `{year}-{MM} {Month} {year} Puppetlabs Modules Roundup.md` with the target
      month's `MM`.
