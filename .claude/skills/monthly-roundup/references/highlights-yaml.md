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

breaking_changes:
  - module: "module_name"
    title: "Breaking change title"
    description: "What changed and the impact"

major_features:
  - module: "module_name"
    title: "Feature name"
    description: "Why this feature is important"

security_updates:
  - module: "module_name"
    title: "Security fix"
    description: "CVE or vulnerability addressed"

single_important_updates:
  - module: "module_name"
    title: "Update title"
    description: "Why it matters"
```

`affected_modules` is a comma-separated string, not a list. Module names are bare slugs
(`postgresql`), not `puppetlabs-postgresql`.

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
