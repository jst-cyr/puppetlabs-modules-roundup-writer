# Puppetlabs Modules Roundup – January 2026

**Tags:** #puppet

Welcome back to the Puppetlabs Modules Roundup! This series is all about keeping you in the loop on what’s new and updated in the Perforce Puppet ‘puppetlabs’ modules on the Forge. This month we look back at the latest updates from January 2026.

If you want a quick look at the latest developments across the Puppet module ecosystem, this is the place to catch up!

## Highlighted Updates

### New Continuous Delivery releases!

New releases for v5.14.0 and v4.39.0 brought updates to the CD modules, including dropping support for Puppet 7 and Ruby 2.7. See details in the release notes:

- v5.14.0 👉 [Continuous Delivery (CD) release notes | Continuous Delivery (CD) | 5.14.0](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm#Version5140)

- v4.39 👉 [Continuous Delivery for PE release notes](https://www.puppet.com/docs/continuous-delivery/4.x/cd_release_notes#version-4-39-0)

### Continued Deprecation of Puppet 7 in New Releases

A few more modules received updates to have better alignment with Puppet Core and stop supporting Puppet 7 in the new releases, in line with changes to other modules from previous months.

- cd4peadm
- wsus_client

## What Updates Happened to Puppetlabs Modules in January 2026?

The following is an alphabetical listing of modules which received updates in January 2026. If a module had multiple versions released the updates are collected together, numbered with the ‘latest’ version available.  

---

### cd4peadm 5.14.0

📅 Latest release: 2026-01-27 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4peadm/readme))

The v5.14.0 release had several improvements, including multiple security updates to resolve vulnerabilities. Puppet 7 and Ruby 2.7 support was also dropped in the new releases for both the v5 and v4 streams. Check the release notes for the full details!

- v5.14.0 👉 [Continuous Delivery (CD) release notes | Continuous Delivery (CD) | 5.14.0](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm#Version5140)

  
---

### peadm 3.35.0

📅 Latest release: 2026-01-22 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm/readme))

Minor updates to add support for the latest Puppet Enterprise releases for 2023.8.8 and 2025.8.

---

### wsus_client 6.3.0

📅 Latest release: 2026-01-23 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/wsus_client/readme))

Several updates to support Puppet Core better, including PDK and Puppet version updates:

- Support added for configuring Active Hours in WSUS client module
    - New parameters `active_hours_start` and `active_hours_end`
- Puppet 7 support removed
- Target ruby version updated to 3.1 (2.7 removed)
- Changes to better support PDK latest releases
- Puppet Agent outdated pin removed

---

### zone_core 2.0.2

📅 Latest release: 2026-01-05 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/zone_core/readme))

Mostly under-the-hood maintenance changes here, including an update to allow more recent versions of `puppetlabs/zfs_core`

---

## Until Next Time!

That’s a wrap for this roundup! If you want to dive deeper into any of these modules, check out the module documentation [on the Forge](https://forge.puppet.com) or explore the individual module repos on GitHub for more details.

Got feedback or ideas for future updates? We’d love to hear from you! Add a comment here or join the conversation in the [Perforce Community Slack](https://slack.puppet.com/).

Catch you at the next roundup in March!