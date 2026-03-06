# Puppetlabs Modules Roundup – February 2026

**Tags:** #puppet

Welcome back to the Puppetlabs Modules Roundup! This series is all about keeping you in the loop on what’s new and updated in the Perforce Puppet `puppetlabs` modules on the Forge. This month we look back at the latest updates from February 2026.

If you want a quick look at the latest developments across the Puppet module ecosystem, this is the place to catch up!

## Highlighted Updates

### SQL Server 2025 and DSC Reporting Fixes

- The latest sqlserver module release now supports SQL Server 2025
- The latest sce_windows module corrects DSC reporting issues.

### Continued Deprecation of Puppet 7 in New Releases

A few more modules received updates to have better alignment with Puppet Core and have stopped supporting Puppet 7 in the new releases, in line with changes to other modules from previous months.

- Docker
- firewall
- inifile
- sqlserver

## What Updates Happened to Puppetlabs Modules in February 2026?

The following is an alphabetical listing of modules which received updates in February 2026. If a module had multiple versions released the updates are collected together, numbered with the "latest" version available.  

---

### docker 10.4.0

📅 Latest release: 2026-02-10 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/docker))

Several updates to support Puppet Core better and updates for APT keyrings:

- Now uses puppetlabs-apt for modern APT keyrings on Debian family (by [kenyon](https://github.com/kenyon))

- APT keyring used to manage GPG key (by [techsk8](https://github.com/techsk8))

- Dependency on `cgroupfs-mount` for Debian Trixie has been removed (by [zen-fu](https://github.com/zen-fu))

- Services with restart `no` are now ignored in the `exists?` method

- Puppet 7 support removed

- Target ruby version updated to 3.1 (2.7 removed)

- Changes to better support PDK latest releases

- CI tests now run against Ubuntu 24.04 (replacing Ubuntu 20.04)

---

### firewall 8.3.0

📅 Latest release: 2026-02-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/firewall))

Several updates to support Puppet Core better and updates for SUSE IPv6:

- IPv6 rule saving command added for SUSE in utility

- Puppet 7 support removed

- Target ruby version updated to 3.1 (2.7 removed)

- Changes to better support PDK latest releases

- CI tests now run against Debian 12 instead of Debian 10 for primary testing

---

### influxdb 3.0.1

📅 Latest release: 2026-02-05 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/influxdb))

Small release here to provide an updated GPG key.

---

### inifile 6.3.1

📅 Latest release: 2026-02-17 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/inifile))

Several updates to support Puppet Core better and updates for handling empty sections:

- Removing the last setting of a section will no longer remove the “empty” section (by [smortex](https://github.com/smortex))

- Puppet 7 support removed

- Target ruby version updated to 3.1 (2.7 removed)

- Changes to better support PDK latest releases

---

### puppet_agent 4.27.0

📅 Latest release: 2026-02-24 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_agent/readme))

Debian 13 (Trixie) acceptance tests added for ARM and x86_64

---

### pwshlib 2.0.1

📅 Latest release: 2026-02-24 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/pwshlib/readme))

This release fixes per-property change event reporting in PE when using DSC resources with custom_insync.

---

### sce_windows 2.2.1

📅 Latest release: 2026-02-24 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_windows/readme))

SCE for Windows now supports the latest versions of the puppetlabs‑pwshlib dependency, including a fix for DSC reporting issues. In addition, resource names are updated to correctly reference SCE instead of the legacy CEM name.

- Check the official [release notes for Security Compliance Enforcement 2.2.1](https://help.puppet.com/sce/current/windows/scew_relnotes_v221.htm)

---

### sqlserver 5.1.0

📅 Latest release: 2026-02-26 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sqlserver/readme))

Support was added for SQL Server 2025 along with changes to better support Puppet Core.

- Support added for SQL Server 2025

- Several changes to match with requirements for Puppet Core

- Puppet 7 support removed

- Target ruby version updated to 3.1 (2.6 removed)

- Changes to better support PDK latest releases

---

## Until Next Time!

That’s a wrap for this roundup! If you want to dive deeper into any of these modules, check out the module documentation [on the Forge](https://forge.puppet.com) or explore the individual module repos on GitHub for more details.

Got feedback or ideas for future updates? We’d love to hear from you! Add a comment here or join the conversation in the [Perforce Community Slack](https://slack.puppet.com/).

Catch you at the next roundup!