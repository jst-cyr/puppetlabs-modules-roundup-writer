# Puppetlabs Modules Roundup – December 2025

**Tags:** #puppet

Happy New Year and welcome back to the **Puppetlabs Modules Roundup**! This series is all about keeping you in the loop on what’s new and updated in the Perforce Puppet official module ecosystem. This first update of 2026 will look back at the latest updates from **December 2025**.

Whether you are just getting started with Puppet, or managing a long-lived solution with thousands of nodes, or just curious about what has changed in the module ecosystem, this is the place to find out what's new!

## Highlighted Updates

### Big Upgrades for Observability

Operations Dashboards needed some big updates to work on the latest versions of Grafana. Modules for **influxdb** and **puppet_operational_dashboards** have both received new releases.

The Observability Data Connector also received updates to support the new real-time web hook events available in Puppet Enterprise 2025.7.

### Security Compliance Enforcement Now Supports Windows Server 2025

The sce_windows module latest release will now enforce CIS Benchmarks on Windows Server 2025.

### Puppet 7 Support Removed in a few Modules

With Puppet 7 now end-of-life, a few more modules removed Puppet 7 support in December. See notes for these modules:

   - influxdb
   - puppet_operational_dashboards

## What’s New in Puppetlabs Modules?

The following is an alphabetical listing of modules which received updates in **December 2025**. Some of these modules had multiple versions released so updates are collected together, numbered with the ‘latest’ version available.  
  

---

### apt 11.2.0

📅 **Latest release: 2025-12-17** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/apt/readme))  

Small update in this release to add support for Ubuntu 24.04.

---

### comply 3.6.0

📅 **Latest release: 2025-12-17** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/comply/readme))

### complyadm 3.6.0

📅 **Latest release: 2025-12-17** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/complyadm/readme))

Several updates in Security Compliance Management are detailed in the [official release notes](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm#SecurityComplianceManagement360), including new CIS-CAT Pro Assessor benchmarks and several security fixes for vulnerabilities.

---

### cron_core 2.0.2

📅 **Latest release: 2025-12-02** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cron_core/readme))

This small update specifies the correct supported Puppet version as version 8.x only. This change functionally occurred in previous releases but was not marked in the metadata.

---

### influxdb 3.0.0

📅 **Latest release: 2025-12-04** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/influxdb/readme))

The influxdb module received a few updates from the community as well as some breaking changes to better support the latest versions of Puppet:

   - **Puppet 7 support removed.**  Starting with 3.x, this module will be used for Puppet 8+.

   - Dependencies were updated to more recent versions and now align with PDK 3.x

   - toml-rb was updated from 2.1.1 to 4.0.0

   - Several fixes including PDK versions, APT module dependency, tokens with named buckets, and metadata dependencies on puppet-archive.

---

### peadm 3.34.0

📅 **Latest release: 2025-12-19** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm/readme))

This small update to PEADM resolved a few issues and added support for the new Puppet Enterprise 2025.7 and 2023.8.7.

   - Timeouts have been added around puppet run on db targets.

   - The order that “Convert” plans uses for final puppet runs has changed and now will run the primary node after all the other nodes.

   - The correct environment is now assigned to node groups. The environment is now configurable, defaulting to production.

   - Versions updated to support new 2023.8.7 and 2025.7 releases.

---

### postgresql 10.6.1

📅 **Latest release: 2025-12-26** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/postgresql/readme))

This small update to the PostgreSQL database module includes some community-provided fixes for the module.

   - The systemctl `status` calls are replaced with systemctl `is-active` to correct issues with Unicode output.

   - Fixes applied to handle issues with the `postgresql_password` parameter and type aliases.

---

### puppet_data_connector 2.0.0

📅 **Latest release: 2025-12-19** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_data_connector/readme))

The latest version of the Observability Data Connector now supports webhook handlers to allow for more real-time reporting on Puppet-sourced metrics data. Starting in PE 2025.7, you can use the Observability Data Connector to set up alerts for patching operations. These alerts provide visibility into key job-level and node-level events, such as when a patch job completes or when a node encounters an error during patching.

---

### puppet_operational_dashboards 3.0.0

📅 **Latest release: 2025-12-08** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_operational_dashboards/readme))

This major update to the Ops Dashboard module brings about updates for Ubuntu, new versions of Grafana, and retires Puppet 7 support:

   - Added ability to edit datasource buckets, enabling bucket deletion.

   - Added support for Ubuntu 22.04 in metadata.json

   - Updated datasource setup to include firewall rules.

   - Removed Puppet 7 from the list of supported releases.

   - Upgraded Grafana to version 11.8.6

   - Updated plans ingest limit to 90 days.

   - Fixed Ubuntu Hiera YAML formatting issue

---

### sce_windows 2.2.0

📅 **Latest release: 2025-12-09** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_windows/readme))

SCE for Windows now enforces Center for Internet Security (CIS) controls on the Windows Server 2025 operating system. This supports CIS Microsoft Server 2025 Benchmark v1.0.0, Server Level 1.  
  

---

### zone_core 2.0.1

📅 **Latest release: 2025-12-01** (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/zone_core/readme))

This small update specifies the correct supported Puppet version as version 8.x only. This change functionally occurred in previous releases but the metadata had not been updated to include it.

---

## Until Next Time!

That’s a wrap for this roundup! If you want to dive deeper into any of these modules, check out the module documentation [on the Forge](https://forge.puppet.com) or explore the individual module repos on GitHub for more details.

Got feedback or ideas for future updates? We’d love to hear from you! Add a comment here or join the conversation in the [Perforce Community Slack](https://slack.puppet.com/).

Catch you at the next roundup in February!