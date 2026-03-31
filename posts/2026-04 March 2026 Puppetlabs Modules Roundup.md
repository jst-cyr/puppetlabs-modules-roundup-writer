# Puppetlabs Modules Roundup – March 2026

**Tags:** #puppet

March 2026 brought 4 Puppetlabs module releases in the Puppetlabs Forge catalog. Read along to see what changed this month!

Across the month, the clearest themes were compatibility updates across Puppet Enterprise (PE), supported platforms, and operational hardening and troubleshooting improvements.

## Highlighted Updates

### Compatibility updates across PE and supported platforms

March releases leaned toward version-alignment work, with updates for newer Puppet Enterprise releases, Ubuntu 24.04 benchmark coverage, and dependency ranges that allow newer supporting modules.

- Added support for PE 2023.8.9 and 2025.9.0.
- Added CIS Benchmark support for Ubuntu 24.04 Server Levels 1 and 2.

### Operational hardening and troubleshooting improvements

Several releases focused on making "Day Two" operations safer and easier to debug through better validation, more useful logging, and targeted runtime fixes.

- Added installer `untar` checks and deduplicated hosts in the legacy compiler group.
- Moved most SCE-specific logging into the Puppet agent run log for easier debugging.

## What Updates Happened to Puppetlabs Modules in March 2026?

The following is an alphabetical listing of modules which received updates in March 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### cd4pe 3.4.0

📅 Latest release: 2026-03-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4pe))

This release focuses on updated puppetlabs-docker and puppetlabs-hocon dependencies to allow usage of newer versions while also addressing updated module with PDK 3.6.1.

- Updated puppetlabs-docker and puppetlabs-hocon dependencies to allow usage of newer versions
- Updated module with PDK 3.6.1

---

### peadm 3.36.0

📅 Latest release: 2026-03-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm))

This release focuses on adding support for PE 2023.8.9 and 2025.9.0 #657 (Jade2153) while also addressing (PE-43572) deduplicate hosts in legacy compiler group #658 (davidmalloncares).

- Adding support for PE 2023.8.9 and 2025.9.0 [#657](https://github.com/puppetlabs/puppetlabs-peadm/pull/657) ([Jade2153](https://github.com/Jade2153))
- (PE-43572) deduplicate hosts in legacy compiler group [#658](https://github.com/puppetlabs/puppetlabs-peadm/pull/658) ([davidmalloncares](https://github.com/davidmalloncares))
- (PE-42686) Add checks to installer untar command [#654](https://github.com/puppetlabs/puppetlabs-peadm/pull/654) ([davidmalloncares](https://github.com/davidmalloncares))

---

### sce_linux 2.6.0

📅 Latest release: 2026-03-17 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_linux))

This release focuses on support for Ubuntu 24.04. You can use SCE to enforce the Center for Internet Security (CIS) Benchmark for Ubuntu Linux 24.04, v1.0.0, Server Levels 1 and 2 while also addressing support for Puppet module dependencies. To take advantage of fixes and improvements in Puppet modules, SCE for Linux now supports the latest versions of the following Puppet module dependencies: puppet/systemd : >= 3.5.0 < 10.0.0 puppet/logrotate : >= 5.0.0 < 10.0.0 puppetlabs/augeas_core : >= 1.1.1 < 3.0.0.

- Support for Ubuntu 24.04. You can use SCE to enforce the Center for Internet Security (CIS) Benchmark for Ubuntu Linux 24.04, v1.0.0, Server Levels 1 and 2.
- Support for Puppet module dependencies. To take advantage of fixes and improvements in Puppet modules, SCE for Linux now supports the latest versions of the following Puppet module dependencies: puppet/systemd : >= 3.5.0 < 10.0.0 puppet/logrotate : >= 5.0.0 < 10.0.0 puppetlabs/augeas_core : >= 1.1.1 < 3.0.0
- SCE -specific information in logs . SCE now sends most of its logs to the Puppet agent run log, instead of the puppetserver.log file on the Puppet primary server. Because of this update, users can now run the Puppet agent in debug mode and get more SCE -specific information in the run log.
- Additional information about mount points. The custom fact sce_mount_info is updated to provide insight into all mounted file systems. Previously, the fact covered only file systems that were listed in the /etc/fstab configuration file. As in previous releases, you can use SCE to manage USB drives. However, SCE now issues an informational message if a USB drive is detected but not listed in fstab .
- Puppet run failures related to auditd . Previously, SCE for Linux users experienced Puppet run failures in environments where the rsyslog package was not installed. The issue occurred because the auditd service processed an audit_files list that erroneously included rsyslogd . The rsyslogd entry was removed to resolve the issue.

- Check the official [release notes for sce_linux 2.6.0](https://help.puppet.com/sce/current/linux/scel_relnotes_260.htm)

---

### sqlserver 5.1.1

📅 Latest release: 2026-03-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sqlserver))

This release focuses on (MODULES-11613) Set permission variable in permission sql EPP #500 (shubhamshinde360).

- (MODULES-11613) Set permission variable in permission sql EPP [#500](https://github.com/puppetlabs/puppetlabs-sqlserver/pull/500) ([shubhamshinde360](https://github.com/shubhamshinde360))

## Until Next Time!

That wraps up the March 2026 roundup. If any of peadm, sce_linux intersect with your environment, the linked Forge pages and release notes are worth a closer look.

Feedback on the series is always useful, especially if there are module families or release-note patterns that deserve more attention in future editions.

More updates coming next month when the April 2026 releases land.
