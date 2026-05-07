# Puppetlabs Modules Roundup – April 2026

**Tags:** #puppet

In April 2026, the Puppetlabs module lineup saw 8 Puppetlabs module releases, with the most notable updates collected here for a quick review.

The overall pattern in these releases was event forwarding enhancements and security and compliance platform updates, which makes this month’s roundup a useful quick scan for teams planning upgrades or routine maintenance.

## Highlighted Updates

### Event Forwarding Enhancements

Coordinated updates to Splunk HEC and PE Event Forwarding modules add support for orchestrator_plan event type, improving visibility into Puppet orchestrator activities with enhanced filtering and integration capabilities.

- Affected modules: splunk_hec, pe_event_forwarding.

### Security and Compliance Platform Updates

Comply and Comply Admin modules received coordinated releases, advancing the Security Compliance Management platform capabilities.

- Affected modules: comply, complyadm.

## What Updates Happened to Puppetlabs Modules in April 2026?

The following is an alphabetical listing of modules which received updates in April 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### cd4peadm 5.15.0

📅 Latest release: 2026-04-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4peadm))

This release focuses on added a Hiera configuration option, external_webhook_url , that allows you to set the webhook URL that Continuous Delivery sends to your VCS provider. This is useful if you are using a proxy between your VCS and CD .

- Check the official [release notes for cd4peadm 5.15.0](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm#Version5150)

---

### comply 3.7.1

📅 Latest release: 2026-04-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/comply))

This release focuses on fixed a stale image which resulted in checksum and benchmark issues upon install.

- Check the official [release notes for comply 3.7.1](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm)

---

### complyadm 3.7.1

📅 Latest release: 2026-04-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/complyadm))

This release focuses on fixed a stale image which resulted in checksum and benchmark issues upon install.

- Check the official [release notes for complyadm 3.7.1](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm)

---

### lvm 4.0.1

📅 Latest release: 2026-04-30 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/lvm))

This release focuses on wait for udev to settle after lvcreate while also addressing pass converted boolean parameter.

- (MODULES-11756) Wait for udev to settle after lvcreate [#380](https://github.com/puppetlabs/puppetlabs-lvm/pull/380) ([imaqsood](https://github.com/imaqsood))
- (MODULES-11788) Pass converted boolean parameter [#379](https://github.com/puppetlabs/puppetlabs-lvm/pull/379) ([joshcooper](https://github.com/joshcooper))

---

### pe_event_forwarding 2.3.0

📅 Latest release: 2026-04-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/pe_event_forwarding))

This release focuses on see release notes on Puppet Forge.

- See release notes on Puppet Forge

---

### peadm 3.37.0

📅 Latest release: 2026-04-01 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm))

This release focuses on add support for PE 2025.10.0.

- (PE-43654) Add support for PE 2025.10.0 [#661](https://github.com/puppetlabs/puppetlabs-peadm/pull/661) ([davidmalloncares](https://github.com/davidmalloncares))

---

### sce_linux 2.6.1

📅 Latest release: 2026-04-06 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_linux))

This release focuses on error message: comparison of NilClass with <number> failed . Some users saw this error message and experienced catalog compilation failures when attempting to manage mounted file system options with SCE for Linux . The issue was caused by /etc/fstab files that did not have at least one comment line or blank line. The internal parser was updated to avoid the issue and help prevent compilation errors.

- Check the official [release notes for sce_linux 2.6.1](https://help.puppet.com/sce/current/linux/scel_relnotes_261.htm)

---

### splunk_hec 2.2.0

📅 Latest release: 2026-04-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/splunk_hec))

This release focuses on added support for the `orchestrator_plan` event type from the **puppetlabs-pe_event_forwarding** module while also addressing added `orchestrator_plan` to index mappings in util_splunk_hec template.

- Added support for the `orchestrator_plan` event type from the **puppetlabs-pe_event_forwarding** module.
- Added `orchestrator_plan` to index mappings in util_splunk_hec template.
- New PE Event Forwarding filter `orchestrator_plan_data_filter` to allow filtering orchestrator plan event payloads.
- Module dependency updated to ensure `pe_event_forwarding` v2.3.0+ is installed.
- Removed support for Debian platform and EOL operating system versions.

## Until Next Time!

That’s the full pass through the 8 Puppetlabs module releases from April 2026. The Forge links above are the quickest path to the underlying release details.

If there is a part of the Puppetlabs ecosystem that would benefit from more context in future roundups, that feedback is worth sending along.

Catch you in the next roundup for May 2026.
