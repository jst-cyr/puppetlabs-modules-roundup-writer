# Puppetlabs Modules Roundup – June 2026

**Tags:** #puppet

June 2026 brought 24 Puppetlabs module releases to the Forge, ranging from a brand-new Windows security policy module to a large batch of third-party CVE fixes in Security Compliance Management. This roundup pulls the most important changes into one place.

Across the month, the clearest patterns were a coordinated stdlib 10.x compatibility pass and the ongoing Puppetcore alignment work dropping Puppet 7 support, so most of the module list below is maintenance and compatibility work rather than large feature launches.

## Highlighted Updates

### New Module: Windows Local Security Policy Management

The new [security_policy module](https://forge.puppet.com/modules/puppetlabs/security_policy/readme) manages Windows local security policy using the Puppet Resource API, replacing manual `secedit`/Local Security Policy editor work.

- Provides the `security_option` and `user_right_assignment` resource types, covering all 45 Windows Privilege Rights and the System Access settings.
- Ships a well-known SID map with a PowerShell fallback for domain and custom accounts.

### stdlib 10.x Compatibility Pass

A coordinated maintenance pass loosened the puppetlabs/stdlib dependency constraint across the module set to allow stdlib 10.x, clearing the way for downstream modules to pick up stdlib's latest release.

- Affected modules: accounts, apache, apt, chocolatey, concat, docker, firewall, haproxy, inifile, lvm, motd, mysql, ntp, postgresql, wsus_client.

### Puppetcore Alignment / Puppet 7 Support Dropped

Several modules completed their Puppetcore alignment pass this month, dropping Puppet 7 support in favor of Puppet 8 as Puppet 7 reaches end-of-life.

- Affected modules: accounts, chocolatey, haproxy, java, motd, mysql, postgresql, stdlib.

### Security Compliance Management Patches ~40 CVEs

Security Compliance Management 3.8.0, shipped as both `comply` and `complyadm`, updates a long list of bundled third-party components — Gorm.io, Protobuf, several Netty codec libraries, react-router, and KeyCloak — to close out roughly 40 CVEs.

- Also updates the bundled CIS-CAT Pro Assessor to v4.63.0, adding new STIG benchmarks for Amazon Linux 2023, Windows 11, Oracle Linux 9, and RHEL 10.

## What Updates Happened to Puppetlabs Modules in June 2026?

The following is an alphabetical listing of modules which received updates in June 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### accounts 9.0.0

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/accounts))

This release drops Puppet 7 support (**BREAKING**) as part of the module's Puppetcore alignment work, and allows the stdlib dependency to move to 10.x.

- (CAT-2352) Drop Puppet 7 support (BREAKING) — Puppetcore alignment [#509](https://github.com/puppetlabs/puppetlabs-accounts/pull/509) ([LukasAud](https://github.com/LukasAud))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#513](https://github.com/puppetlabs/puppetlabs-accounts/pull/513) ([imaqsood](https://github.com/imaqsood))

---

### apache 13.2.0

📅 Latest release: 2026-06-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/apache))

Adds RHEL 10 support, restores the ModSecurity engine on RHEL 10 via EPEL, and allows both stdlib and concat to move to their 10.x releases.

- Add missing parameters to mod_md [#2621](https://github.com/puppetlabs/puppetlabs-apache/pull/2621) ([smortex](https://github.com/smortex))
- (MODULES-11851) Restore ModSecurity engine on RHEL 10 via EPEL [#2635](https://github.com/puppetlabs/puppetlabs-apache/pull/2635) ([SugatD](https://github.com/SugatD))
- (MODULES-11739) Add RHEL 10 support [#2629](https://github.com/puppetlabs/puppetlabs-apache/pull/2629) ([SugatD](https://github.com/SugatD))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#2632](https://github.com/puppetlabs/puppetlabs-apache/pull/2632) ([imaqsood](https://github.com/imaqsood))
- puppetlabs/concat: Allow 10.x [#2630](https://github.com/puppetlabs/puppetlabs-apache/pull/2630) ([bastelfreak](https://github.com/bastelfreak))

---

### apt 11.3.2

📅 Latest release: 2026-06-26 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/apt))

A small release that only bumps the stdlib dependency to allow 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#1288](https://github.com/puppetlabs/puppetlabs-apt/pull/1288) ([imaqsood](https://github.com/imaqsood))

---

### aws_inventory 0.8.0

📅 Latest release: 2026-06-17 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/aws_inventory))

This release allows the ruby_task_helper dependency to move to 1.x.

- Allow ruby_task_helper 1.x

---

### chocolatey 9.0.0

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/chocolatey))

Completes its Puppetcore alignment pass, improves package prefetch caching with case-insensitive matching, and allows stdlib 10.x.

- (CAT-2369) Puppetcore update [#378](https://github.com/puppetlabs/puppetlabs-chocolatey/pull/378) ([LukasAud](https://github.com/LukasAud))
- (MODULES-11769) Cache prefetch results and match packages case-insensitively [#388](https://github.com/puppetlabs/puppetlabs-chocolatey/pull/388) ([skyamgarp](https://github.com/skyamgarp))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#387](https://github.com/puppetlabs/puppetlabs-chocolatey/pull/387) ([imaqsood](https://github.com/imaqsood))

---

### comply 3.8.0

📅 Latest release: 2026-06-12 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/comply))

Security Compliance Management 3.8.0 addresses roughly 40 CVEs across bundled third-party components, alongside operational fixes and licensing improvements.

- Increased the CIS-CAT Pro Assessor license expiry time to a full year.
- Added a `license_path` parameter to update the CIS-CAT Pro Assessor license without upgrading SCM.
- Added an `assessor_scan_timeout` option to control the task timeout for Windows 2022 domain controllers.
- Added a background scan sweeper to detect and cancel scans stuck in the "running" state.
- Fixed a race condition where timed-out PE job status polls could leave scans permanently stuck.
- Updated Gorm.io, Protobuf, multiple Netty codec libraries, react-router, and KeyCloak to address roughly 40 CVEs.

Check the official [release notes for comply 3.8.0](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm#SecurityComplianceManagement380) for the full details.

---

### complyadm 3.8.0

📅 Latest release: 2026-06-12 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/complyadm))

Ships the same Security Compliance Management 3.8.0 update as `comply`, covering the same ~40 CVE remediations and operational fixes.

- Increased the CIS-CAT Pro Assessor license expiry time to a full year.
- Added a `license_path` parameter to update the CIS-CAT Pro Assessor license without upgrading SCM.
- Added an `assessor_scan_timeout` option to control the task timeout for Windows 2022 domain controllers.
- Added a background scan sweeper to detect and cancel scans stuck in the "running" state.
- Fixed a race condition where timed-out PE job status polls could leave scans permanently stuck.
- Updated Gorm.io, Protobuf, multiple Netty codec libraries, react-router, and KeyCloak to address roughly 40 CVEs.

Check the official [release notes for complyadm 3.8.0](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm#SecurityComplianceManagement380) for the full details.

---

### concat 10.0.1

📅 Latest release: 2026-06-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/concat))

A small release that only bumps the stdlib dependency to allow 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#837](https://github.com/puppetlabs/puppetlabs-concat/pull/837) ([imaqsood](https://github.com/imaqsood))

---

### docker 10.4.1

📅 Latest release: 2026-06-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/docker))

Removes the upper version limit on the puppetlabs/apt dependency, fixes `compose up` argument ordering, and allows stdlib 10.x.

- Do not limit puppetlabs/apt requirement < v12 [#1056](https://github.com/puppetlabs/puppetlabs-docker/pull/1056) ([mpdude](https://github.com/mpdude))
- Fix argument order on compose up [#1037](https://github.com/puppetlabs/puppetlabs-docker/pull/1037) ([deligatedgeek](https://github.com/deligatedgeek))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#1057](https://github.com/puppetlabs/puppetlabs-docker/pull/1057) ([imaqsood](https://github.com/imaqsood))

---

### edgeops 1.1.0

📅 Latest release: 2026-06-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/edgeops))

Adds host key fingerprint verification for Bolt 5.1.0+ targets, along with a large batch of NETCONF/SSH hardening fixes.

- (PE-43703) Verify host key fingerprints supplied as `host-key-fingerprint` in the target hash; takes precedence over `host-key-check` and requires Bolt 5.1.0+. [#38](https://github.com/puppetlabs/puppetlabs-edgeops/pull/38) ([owenbeckles](https://github.com/owenbeckles))
- (PE-42584) Correctly handle host key verification parameter [#23](https://github.com/puppetlabs/puppetlabs-edgeops/pull/23) ([Ziaunys](https://github.com/Ziaunys))
- (PE-43619) Clean up SSH on timeout and always raise instead of returning partial data [#33](https://github.com/puppetlabs/puppetlabs-edgeops/pull/33) ([Ziaunys](https://github.com/Ziaunys))
- (PE-43614) Add mutex synchronization for RPC message ID allocation [#29](https://github.com/puppetlabs/puppetlabs-edgeops/pull/29) ([Ziaunys](https://github.com/Ziaunys))
- (PE-43652) Rename netconf_lock task to netconf_check_lock [#35](https://github.com/puppetlabs/puppetlabs-edgeops/pull/35) ([Ziaunys](https://github.com/Ziaunys))

---

### firewall 8.5.0

📅 Latest release: 2026-06-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/firewall))

Two releases this month: 8.4.0 added CONNMARK-based policy routing support and several bugfixes, while 8.5.0 allows stdlib 10.x, drops `iptables-services` from EL9+ package defaults, and fixes several ipset and chain-detection edge cases.

Includes monthly releases: 8.5.0 (2026-06-25), 8.4.0 (2026-06-10).

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#1288](https://github.com/puppetlabs/puppetlabs-firewall/pull/1288) ([imaqsood](https://github.com/imaqsood))
- (#1254) Remove iptables-services from EL9+ package defaults [#1296](https://github.com/puppetlabs/puppetlabs-firewall/pull/1296) ([david22swan](https://github.com/david22swan))
- (feat) Add restore_mark, nfmask, ctmask support for CONNMARK-based policy routing [#1291](https://github.com/puppetlabs/puppetlabs-firewall/pull/1291) ([david22swan](https://github.com/david22swan))
- (bugfix) Fix ipset idempotency: single-element array not in sync with String equivalent [#1286](https://github.com/puppetlabs/puppetlabs-firewall/pull/1286) ([david22swan](https://github.com/david22swan))
- (bugfix) Fix log_level idempotency when explicitly setting the iptables default value [#1284](https://github.com/puppetlabs/puppetlabs-firewall/pull/1284) ([david22swan](https://github.com/david22swan))

---

### haproxy 8.2.1

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/haproxy))

Completes the module's Puppet 8 upgrade work, drops Puppet 7 support, and allows stdlib 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#642](https://github.com/puppetlabs/puppetlabs-haproxy/pull/642) ([imaqsood](https://github.com/imaqsood))
- (CAT-2373) Remove puppet 7 [#631](https://github.com/puppetlabs/puppetlabs-haproxy/pull/631) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (CAT-2373)(02) Upgrade module to puppet 8 [#629](https://github.com/puppetlabs/puppetlabs-haproxy/pull/629) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### inifile 6.4.1

📅 Latest release: 2026-06-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/inifile))

A small release that only bumps the stdlib dependency to allow 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#570](https://github.com/puppetlabs/puppetlabs-inifile/pull/570) ([imaqsood](https://github.com/imaqsood))

---

### java 12.0.0

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/java))

Completes its Puppetcore update, adds CentOS 9 and Debian 13 support, allows stdlib 10.x, and adds support for downloading from a login/password-protected URL.

- (CAT-2376) Puppetcore update [#614](https://github.com/puppetlabs/puppetlabs-java/pull/614) ([LukasAud](https://github.com/LukasAud))
- (CAT-2152) Add support for CentOS 9 [#606](https://github.com/puppetlabs/puppetlabs-java/pull/606) ([skyamgarp](https://github.com/skyamgarp))
- Add support for Debian 13 (trixie) [#613](https://github.com/puppetlabs/puppetlabs-java/pull/613) ([mika](https://github.com/mika))
- Feat: Allow downloading from a login/password protected URL [#588](https://github.com/puppetlabs/puppetlabs-java/pull/588) ([JGodin-C2C](https://github.com/JGodin-C2C))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#626](https://github.com/puppetlabs/puppetlabs-java/pull/626) ([imaqsood](https://github.com/imaqsood))

---

### lvm 4.0.2

📅 Latest release: 2026-06-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/lvm))

A small release that only bumps the stdlib dependency to allow 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#384](https://github.com/puppetlabs/puppetlabs-lvm/pull/384) ([imaqsood](https://github.com/imaqsood))

---

### motd 8.0.0

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/motd))

Completes its Puppetcore update, adds Bolt 5.0 support, and allows stdlib 10.x.

- (CAT-2352) Puppetcore update [#531](https://github.com/puppetlabs/puppetlabs-motd/pull/531) ([LukasAud](https://github.com/LukasAud))
- (CAT-2463) Add bolt 5.0 support [#535](https://github.com/puppetlabs/puppetlabs-motd/pull/535) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#558](https://github.com/puppetlabs/puppetlabs-motd/pull/558) ([imaqsood](https://github.com/imaqsood))

---

### mysql 17.0.0

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/mysql))

Completes its Puppetcore update, fixes the RHEL/CentOS Stream 10 version check, and allows stdlib 10.x.

- (CAT-2381) Puppetcore update [#1688](https://github.com/puppetlabs/puppetlabs-mysql/pull/1688) ([LukasAud](https://github.com/LukasAud))
- Fix version check for RHEL/CentOS Stream 10 [#1686](https://github.com/puppetlabs/puppetlabs-mysql/pull/1686) ([kajinamit](https://github.com/kajinamit))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#1707](https://github.com/puppetlabs/puppetlabs-mysql/pull/1707) ([imaqsood](https://github.com/imaqsood))

---

### ntp 11.1.1

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/ntp))

A small release that only bumps the stdlib dependency to allow 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#742](https://github.com/puppetlabs/puppetlabs-ntp/pull/742) ([imaqsood](https://github.com/imaqsood))

---

### peadm 3.38.0

📅 Latest release: 2026-06-30 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm))

Adds support for installing and upgrading to Puppet Enterprise 2023.8.10 and 2025.11.0, along with a cloud_database_host parameter for cloud-DB-backed installs.

- Adding support for PE 2023.8.10 and 2025.11.0 [#673](https://github.com/puppetlabs/puppetlabs-peadm/pull/673) ([CharithaDunuwille](https://github.com/CharithaDunuwille))
- (PE-44022) Add cloud_database_host parameter for cloud-DB-backed installs [#665](https://github.com/puppetlabs/puppetlabs-peadm/pull/665) ([mcdonaldseanp](https://github.com/mcdonaldseanp))
- (PE-44247) Add peadm-path PG-major HA upgrade coverage for replica pe-puppetdb [#666](https://github.com/puppetlabs/puppetlabs-peadm/pull/666) ([steveax](https://github.com/steveax))
- (PE-44595) Don't emit empty dns_alt_names flag in subplans::install [#672](https://github.com/puppetlabs/puppetlabs-peadm/pull/672) ([steveax](https://github.com/steveax))

---

### postgresql 10.6.2

📅 Latest release: 2026-06-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/postgresql))

Adds basic EL10 support, allows both stdlib and concat to move to their 10.x releases, and fixes a bug where `postgresql_conf` resources set to absent were handled incorrectly.

- add EL10 basic support - align EL10 PGSQL 16 default package version [#1650](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1650) ([ikonia](https://github.com/ikonia))
- fix: ignore postgresql_conf resource value when set to absent [#1657](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1657) ([davidassigbi](https://github.com/davidassigbi))
- grant creation via hiera through server::grant.pp [#1668](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1668) ([ikonia](https://github.com/ikonia))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#1681](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1681) ([imaqsood](https://github.com/imaqsood))
- puppetlabs/concat: Allow 10.x [#1669](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1669) ([bastelfreak](https://github.com/bastelfreak))

---

### sce_linux 2.7.0

📅 Latest release: 2026-06-16 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_linux))

Adds CIS Benchmark support for the RHEL 10 family, fixes an rsyslog configuration file that was unconditionally overwritten, and drops RHEL 7 now that it's end of life.

- **Support for RHEL 10, AlmaLinux 10, Oracle Linux 10, and Rocky Linux 10.** Enforces the CIS Benchmark for RHEL 10 (v1.0.1, Server Levels 1 and 2) and CIS Benchmark v1.0.0 for AlmaLinux 10, Oracle Linux 10, and Rocky Linux 10.
- **rsyslog.conf file unconditionally overwritten.** Previously overwritten on every Puppet run even when logging configuration was set to ignore, affecting RHEL 7/8/9 and derivatives. No action required from users.
- **Advanced Intrusion Detection Environment (AIDE) utility class.** Fixed incorrect configuration options generated for AIDE 0.19.x on RHEL 9 that caused `aide --init` to fail.
- RHEL **7.** RHEL 7 is end of life and no longer supported.

Check the official [release notes for sce_linux 2.7.0](https://help.puppet.com/sce/current/linux/scel_relnotes_270.htm) for the full details.

---

### security_policy 1.0.0

🌟 ***New Module:*** 2026-06-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/security_policy))

Brand-new module for managing Windows local security policy. Provides the `security_option` and `user_right_assignment` resource types (Puppet Resource API), covering all 45 Windows Privilege Rights and System Access settings. Initial release contains:

- `security_option` and `user_right_assignment` resource types for managing Windows local security policy settings via `secedit`.
- `security_policy` class exposing 45 `Optional[Array[String]]` parameters (one per privilege right), matching the layout of the legacy `dsc/securitypolicydsc` module.
- `PuppetX::Sid` module: a static well-known SID map covering the 19 standard SIDs, with a PowerShell fallback via `Pwsh::Manager` for domain and custom accounts.
- YAML-driven setting metadata loader (`PuppetX::SecurityPolicy.all_settings`) instead of a hardcoded settings hash.
- Puppet requirement pinned to >= 8.0.0 < 9.0.0.

---

### stdlib 10.0.1

📅 Latest release: 2026-06-30 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/stdlib))

Completes its Puppetcore upgrade by dropping Puppet 7 support, adds CentOS 9 support, extends Sensitive value support to more functions, and fixes `has_ip_address`/`has_ip_network`.

- (CAT-2395) Puppetcore upgrade - drop support for Puppet 7 [#1457](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1457) ([LukasAud](https://github.com/LukasAud))
- (CAT-2152) Add support for CentOS 9 [#1442](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1442) ([skyamgarp](https://github.com/skyamgarp))
- Support `Sensitive` values in more functions [#1463](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1463) ([alexjfisher](https://github.com/alexjfisher))
- Support sensitive values in `to_json_pretty` [#1418](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1418) ([alexjfisher](https://github.com/alexjfisher))
- Fix `has_ip_address` and `has_ip_network` functions [#1448](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1448) ([alexjfisher](https://github.com/alexjfisher))

---

### wsus_client 6.3.1

📅 Latest release: 2026-06-25 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/wsus_client))

A small release that only bumps the stdlib dependency to allow 10.x.

- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#238](https://github.com/puppetlabs/puppetlabs-wsus_client/pull/238) ([imaqsood](https://github.com/imaqsood))

## Until Next Time!

That wraps up the June 2026 roundup. If any of these modules intersect with your environment — especially the Security Compliance Management CVE fixes — the linked Forge pages and release notes are worth a closer look.

Feedback on the series is always useful, especially if there are module families or release-note patterns that deserve more attention in future editions.

More updates coming next month when the July 2026 releases land.
