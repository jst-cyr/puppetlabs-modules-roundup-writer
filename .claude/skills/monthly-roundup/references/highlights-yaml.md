# Authoring the highlights YAML (Stage 3)

Write `data/{month}_{year}_highlights_candidates.yaml` from the `release_notes` array in
`data/{month}_{year}_release_notes_raw.json`. Stage 4 turns this file into the
"Highlighted Updates" section, so it decides what the post leads with.

## Schema

All five keys must be present. An empty list is valid and preferred over a weak entry.

```yaml
themes:
  - title: "Theme name"
    description: "What this theme means and why it matters"
    affected_modules: "module1, module2, module3"
    modules: ["module1", "module2", "module3"]

breaking_changes:
  - module: "module_name"
    version: "x.y.z"
    title: "Breaking change title"
    bullet: "One-sentence, standalone summary of the change — this is what renders."
    description: "What changed and the impact"

major_features:
  - module: "module_name"
    version: "x.y.z"
    title: "Feature name"
    bullet: "One-sentence, standalone summary of the feature — this is what renders."
    description: "Why this feature is important"

security_updates:
  - module: "module_name"
    version: "x.y.z"
    title: "Security fix"
    bullet: "One-sentence, standalone summary of the fix — this is what renders."
    description: "CVE or vulnerability addressed"

single_important_updates:
  - module: "module_name"
    version: "x.y.z"
    title: "Update title"
    bullet: "One-sentence, standalone summary — used only if a theme's `modules` list pulls it in."
    description: "Why it matters"
```

`affected_modules` is a comma-separated string, not a list. Module names are bare slugs
(`postgresql`), not `puppetlabs-postgresql`.

**`bullet` is required on every `breaking_changes`, `major_features`, `security_updates`, and
`single_important_updates` entry — not just `description`.** `04_generate_roundup.py` reads
`item['bullet']`, not `description`, when rendering the "Highlighted Updates" section; an entry
without one is silently dropped from that section (Stage 3 validation does not currently catch
this — read the generated post's Highlighted Updates section, not just the validator's exit
code, to confirm `breaking_changes`/`security_updates` actually rendered). Each `bullet` should
read as a complete, standalone sentence, since it may be quoted verbatim next to other modules'
bullets under a generic combined heading.

A theme's `modules` list (plain module-slug strings, distinct from the human-readable
`affected_modules` string) is what lets the generator pull a matching `major_features` or
`single_important_updates` bullet into that theme's section. Without it, the theme falls back to
rendering only the `affected_modules` list as a single bullet — still valid, just less specific.

Regardless of what the generator auto-renders, the Step 6 polish pass rewrites the "Highlighted
Updates" section by hand anyway (see [post-polish.md](post-polish.md)) — past posts have never
shipped with the generator's generic section titles ("Breaking changes to review",
"Security-related updates"). Treat the raw Stage 4 output as a scaffold to confirm content made
it in, not as finished prose.

## Selection rules

- **A theme spans multiple modules.** One module doing something interesting is a
  `single_important_updates` entry, never a theme. Coordinated dependency bumps, a shared
  platform-support push, or an org-wide deprecation are themes.
- **`breaking_changes`**: removals, deprecations, dropped platform or Puppet versions, and
  anything that changes behavior on upgrade. Name the version that carries it.
- **`security_updates`**: CVE fixes and security-relevant changes. When a release closes a
  large batch, give the count and the notable components rather than listing every CVE.
- **`major_features`**: genuinely new capability, not a parameter addition.
- **`single_important_updates`**: standout one-offs — a brand-new module, a major version
  bump, a long-requested fix.
- Be factual and concise. Describe what shipped and its consequence; skip adjectives, skip
  speculation about roadmap, skip anything the changelog doesn't support.
- Prefer fewer, stronger entries. Four or five highlights carry a post; a dozen buries them.

## Cross-checks before validating

- Every module named in the YAML actually appears in the release notes JSON.
- A module dropping Puppet or OS support is in `breaking_changes`, not only in a theme.
- A `1.0.0` release with no prior history is called out — it's a new module, and the post
  renders it with the `🌟 ***New Module:***` line.
- A version bump that reads like a breaking change but shipped in a patch or minor release is
  worth flagging to the user; past roundups have noted that discrepancy in the prose.
