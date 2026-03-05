# Agent Instructions (LLM)

If you are an agent generating a new monthly roundup, treat [MONTHLY_ROUNDUP_TEMPLATE.md](MONTHLY_ROUNDUP_TEMPLATE.md) as the source structure and fill all placeholders using verified release data.

## Required Input Data

Collect the following before writing:

- Target month and year (for the post title and intro)
- List of updated `puppetlabs` modules for that month
- Latest release version and release date for each module
- Forge URL for each module
- 1–5 notable changes per module from release notes/changelog
- Any major cross-module themes for “Highlighted Updates”

## Generation Rules

- Preserve all section headings and overall order from the template.
- Replace every `{{PLACEHOLDER}}`; do not leave unresolved placeholders in final output.
- Keep module entries in alphabetical order by module name.
- Keep summary language factual and concise; avoid speculation.
- Use Markdown bullets for changes, matching the existing style.
- Include external links only when they add clear value (Forge/release notes).
- Keep tone consistent with prior roundup posts in `posts/`.

## Output Procedure

1. Copy [MONTHLY_ROUNDUP_TEMPLATE.md](MONTHLY_ROUNDUP_TEMPLATE.md).
2. Fill title, intro month/year, and highlighted updates.
3. Add one module block per updated module.
4. Remove optional placeholder lines if unused (for example, release notes lines).
5. Save the completed post in `posts/` with the existing naming pattern.

## Validation Checklist

Before finalizing, verify:

- No placeholder tokens remain (search for `{{` or `}}`).
- Module list is alphabetical.
- Version/date/URL fields are present for every module.
- Each module has at least one concrete change item.
- The “Until Next Time!” section remains present and complete.
