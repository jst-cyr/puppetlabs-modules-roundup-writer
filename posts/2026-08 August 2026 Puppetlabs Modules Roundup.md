# Puppetlabs Modules Roundup – August 2026

**Tags:** #puppet

August 2026 brought 24 releases across 22 Puppetlabs modules (puppet_metrics_collector and cd4peadm each shipped twice), headlined by a broad Puppet 9 compatibility rollout. Continuous Delivery for PE also shipped a required upgrade, Security Compliance Management 3.9.0 closed out 117 CVEs, and several community contributions were rolled into modules as well. This roundup pulls the most important changes into one place.

## Highlighted Updates

### Puppet Core 9 Support Continues to be Added Across Modules

Fourteen `puppetlabs` modules added Puppet Core 9 compatibility this month, continuing the ongoing Puppet 9 rollout. Five of them (`package`, `node_encrypt`, `service`, `reboot`, and `tomcat`) paired the Puppet Core 9 addition with dropping Puppet 7 support in major version bumps as part of a broader Puppet Core modernization pass; see below.

- Affected modules: exec, package, node_encrypt, mount_iso, lvm, service, java, inifile, reboot, windows_eventlog, cd4pe, cd4pe_jobs, cd4peadm, tomcat.

### Puppet 7 Support Dropped

Five modules dropped Puppet 7 support in major version bumps this month as part of the same Puppet Core modernization pass: `package`, `node_encrypt`, `service`, `reboot`, and `tomcat`. `reboot` also picked up CentOS 9 support in the same release.

- Affected modules: package, node_encrypt, service, reboot, tomcat.

### Continuous Delivery for PE: Required Upgrade for Newer PE Versions

`cd4peadm` 5.17.0 is a required upgrade if you're integrating with PE 2023.8.11, 2025.12.0, or 2026.0.0+. Those PE versions now require cert-based auth on puppetserver's `/status/v1/services` endpoint, and CD's older unauthenticated calls to it fail with a 403 until you upgrade.

- The same release also adds Puppet 9 support and closes a second batch of CVEs (bouncycastle, react-router, nanoid, and others).

### Security Compliance Management Patches 117 CVEs

Security Compliance Management 3.9.0, shipped as both `comply` and `complyadm`, updates roughly 20 bundled third-party components to address 117 CVEs. These included curl/libcurl, OpenSSL, the Netty codec family, Jackson Databind, Keycloak services, and libxml2. — .

- Also restricts the Keycloak administration console and Admin REST API from public access by default, and adds support for pulling container images from a private or air-gapped registry instead of only the public default.

## What Updates Happened to Puppetlabs Modules in August 2026?

The following is an alphabetical listing of modules which received updates in August 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### cd4pe 3.4.1

📅 Latest release: 2026-08-13 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4pe))

Adds Puppet version 9 to the version requirements and updates the module with PDK 3.8.0, along with allowing the stdlib dependency to move to 10.x.

- Added version 9 to the Puppet version range.
- Updated module with PDK 3.8.0.
- Expanded the puppetlabs-stdlib dependency to allow stdlib 10.x.
- Removed unused/dead methods from cd4pe_client.rb.

---

### cd4pe_jobs 1.7.5

📅 Latest release: 2026-08-12 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4pe_jobs))

Adds Puppet version 9 support without dropping Puppet 7.

- Support for Puppet 9. The `puppet` requirement in `metadata.json` is now `>= 7.24 < 10.0.0`.

---

### cd4peadm 5.18.0

📅 Latest release: 2026-08-26 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4peadm))

Two releases this month for Continuous Delivery for PE: 5.17.0 is a **required upgrade** for anyone integrating with PE 2023.8.11, 2025.12.0, or 2026.0.0+ — those PE versions require cert-based auth on puppetserver's `/status/v1/services` endpoint, which CD previously called unauthenticated, and integration fails with a 403 until you upgrade. 5.17.0 also adds Puppet version 9 support. 5.18.0 follows up with a smaller set of fixes: ssl_cert_chain and ssl_crl in common.yaml can now reference file paths instead of requiring inline PEM contents, and several UI rendering bugs are fixed. Combined, the two releases close 42 CVEs.

Includes monthly releases: 5.18.0 (2026-08-26), 5.17.0 (2026-08-18).

- Added support for version 9 of Puppet.
- Fixed an issue where lastLoginTime data might not be current in some situations. The lastLoginTime field of the user details response from GET /v1/users/{userID} is now correctly updated for LDAP and SAML logins, as well as the initial login after account creation.
- Fixed an issue where some upgraded environments could show a blank Pipelines as Code view and a blank approval details page for module repo pipelines. These pages now render properly without recreating the pipeline.
- 42 CVEs addressed.

Check the official [release notes for cd4peadm 5.18.0](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm#Version5180) for the full details.

---

### comply 3.9.0

📅 Latest release: 2026-08-21 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/comply))

Security Compliance Management 3.9.0 addresses 117 CVEs across bundled third-party components, adds support for a private or air-gapped image registry, and restricts the Keycloak administration console and Admin REST API from public access by default.

- Supported benchmarks updated in this release: Microsoft Windows 11 Enterprise Benchmark v5.1.0 Microsoft Windows Server 2022 Benchmark v5.1.0 Microsoft Windows Server 2025 Benchmark v2.1.0.
- Fixed an issue where Assessor CLI downloads could fail if the assessor files were added after the comply-ui container started. Downloads now work after the files are deployed without requiring a manual container restart.
- Fixed an issue where default desired compliance could select different non-STIG benchmarks for the same operating system and version depending on database query ordering. SCM now uses a deterministic selection rule so the default benchmark is chosen consistently.
- 117 CVEs addressed.

Check the official [release notes for comply 3.9.0](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm#SecurityComplianceManagement390) for the full details.

---

### complyadm 3.9.0

📅 Latest release: 2026-08-21 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/complyadm))

Ships the same Security Compliance Management 3.9.0 update as comply, covering the same 117 CVE remediations, the new private/air-gapped image registry option, and the Keycloak admin console/API restriction.

- Supported benchmarks updated in this release: Microsoft Windows 11 Enterprise Benchmark v5.1.0 Microsoft Windows Server 2022 Benchmark v5.1.0 Microsoft Windows Server 2025 Benchmark v2.1.0.
- Fixed an issue where Assessor CLI downloads could fail if the assessor files were added after the comply-ui container started. Downloads now work after the files are deployed without requiring a manual container restart.
- Fixed an issue where default desired compliance could select different non-STIG benchmarks for the same operating system and version depending on database query ordering. SCM now uses a deterministic selection rule so the default benchmark is chosen consistently.
- 117 CVEs addressed.

Check the official [release notes for complyadm 3.9.0](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm#SecurityComplianceManagement390) for the full details.

---

### cron_core 2.0.3

📅 Latest release: 2026-08-12 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cron_core))

Fixes a bug where `CronParam#numfix` used the `=~` operator on non-String values, and updates the related spec tests.

- (PE-45112) Don't use =~ on non-String in CronParam#numfix and update spec tests [#94](https://github.com/puppetlabs/puppetlabs-cron_core/pull/94) ([AriaXLi](https://github.com/AriaXLi))

---

### exec 4.1.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/exec))

Adds support for Puppet Core 9.

- (MODULES-11713) Add Puppet 9 support [#250](https://github.com/puppetlabs/puppetlabs-exec/pull/250) ([imaqsood](https://github.com/imaqsood))

---

### inifile 6.5.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/inifile))

Adds Puppet Core 9 support, and fixes `array_matching` to return the first element when it isn't set to `:all`.

- (MODULES-11703) Add Puppet 9 support [#573](https://github.com/puppetlabs/puppetlabs-inifile/pull/573) ([imaqsood](https://github.com/imaqsood))
- Return the first element if `array_matching` is not `:all` [#571](https://github.com/puppetlabs/puppetlabs-inifile/pull/571) ([bwitt](https://github.com/bwitt))

---

### java 12.1.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/java))

Adds Puppet Core 9 support and defaults RHEL 10 nodes to OpenJDK 21.

- (MODULES-11704) Add Puppet 9 support [#630](https://github.com/puppetlabs/puppetlabs-java/pull/630) ([imaqsood](https://github.com/imaqsood))
- (MODULES-11917) Default RHEL 10 to OpenJDK 21 [#631](https://github.com/puppetlabs/puppetlabs-java/pull/631) ([imaqsood](https://github.com/imaqsood))

---

### kubernetes 8.1.1

📅 Latest release: 2026-08-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/kubernetes))

Bumps several dependency constraints (augeasproviders_sysctl, augeas core, stdlib) and moves the module to Puppet Core 8, alongside a fix for `kubernetes_version` matching and a batch of CI/environment maintenance work.

- fix(MODULES-11856): Bump augeasproviders_sysctl to <5.0.0 and core to <6.0.0 [#722](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/722) ([imaqsood](https://github.com/imaqsood))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#718](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/718) ([imaqsood](https://github.com/imaqsood))
- CAT-2378: Update puppetlabs-kubernetes to use Puppet Core 8 [#712](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/712) ([span786](https://github.com/span786))
- Fix kubernetes_version matching [#705](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/705) ([xbulat](https://github.com/xbulat))
- ci(MODULES-11557): add Twingate setup step to GitHub Actions workflow [#704](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/704) ([imaqsood](https://github.com/imaqsood))
- MODULES-11577 chore(ruby): upgrade Ruby from 2.7 to 3.1 [#702](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/702) ([imaqsood](https://github.com/imaqsood))
- (MAINT): Updated the version for puppetlabs-apt module in metadata.json file [#698](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/698) ([span786](https://github.com/span786))
- (CAT-2193): Fixed kubernetes environment setup for Debian. [#694](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/694) ([span786](https://github.com/span786))
- (CAT-2095): Fixed puppetlabs-kubernetes modules CI & nightly failures [#693](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/693) ([span786](https://github.com/span786))

---

### lvm 4.1.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/lvm))

Now supports Puppet Core 9.

- (MODULES-11719) Add Puppet 9 support [#391](https://github.com/puppetlabs/puppetlabs-lvm/pull/391) ([imaqsood](https://github.com/imaqsood))

---

### mount_iso 5.1.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/mount_iso))

Puppet Core 9 is now supported.

- (MODULES-11723) Add Puppet 9 support [#61](https://github.com/puppetlabs/puppetlabs-mount_iso/pull/61) ([imaqsood](https://github.com/imaqsood))

---

### node_encrypt 4.0.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/node_encrypt))

Drops Puppet 7 support (**BREAKING**) as part of a Puppet Core update, and adds version 9 support in the same release.

- (CAT-2382) Update for Puppet Core / Drop Support for Puppet 7 [#125](https://github.com/puppetlabs/puppetlabs-node_encrypt/pull/125) ([david22swan](https://github.com/david22swan))
- (MODULES-11724) Add Puppet 9 support [#126](https://github.com/puppetlabs/puppetlabs-node_encrypt/pull/126) ([imaqsood](https://github.com/imaqsood))

---

### package 4.0.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/package))

Puppet 7 support gets dropped (**BREAKING**) as part of a Puppet Core update and also adds Puppet Core 9 support. Also, Chocolatey bootstrap failures are now surfaced more clearly in Windows acceptance testing.

- (CAT-2384) Prepare module for Puppet Core / Drop Support for Puppet 7 [#346](https://github.com/puppetlabs/puppetlabs-package/pull/346) ([shubhamshinde360](https://github.com/shubhamshinde360))
- (MODULES-11927) Surface chocolatey bootstrap failures in Windows acceptance [#354](https://github.com/puppetlabs/puppetlabs-package/pull/354) ([imaqsood](https://github.com/imaqsood))
- (MODULES-11730) Add Puppet 9 support [#353](https://github.com/puppetlabs/puppetlabs-package/pull/353) ([imaqsood](https://github.com/imaqsood))
- (CAT-2296) Update github runner image to ubuntu-24.04 [#345](https://github.com/puppetlabs/puppetlabs-package/pull/345) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### puppet_metrics_collector 8.2.3

📅 Latest release: 2026-08-14 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_metrics_collector))

Fixes a PostgreSQL 17 checkpoints query and hardens version parsing, cleans up puppet-lint warnings, and removes a broken plaintext-port fallback in PuppetDB metrics collection.

Includes monthly releases: 8.2.3 (2026-08-14), 8.2.2 (2026-08-07).

- (PE-45849) Fix PG17 checkpoints query and harden version parsing [#213](https://github.com/puppetlabs/puppetlabs-puppet_metrics_collector/pull/213) ([beechtom](https://github.com/beechtom))
- Fix puppet-lint space_before_arrow and 140chars warnings [#210](https://github.com/puppetlabs/puppetlabs-puppet_metrics_collector/pull/210) ([jonathannewman](https://github.com/jonathannewman))
- Remove broken plaintext-port fallback in PuppetDB metrics collection [#209](https://github.com/puppetlabs/puppetlabs-puppet_metrics_collector/pull/209) ([jonathannewman](https://github.com/jonathannewman))

---

### reboot 6.0.0

📅 Latest release: 2026-08-26 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/reboot))

Drops Puppet 7 (**BREAKING**) amd adds support for Puppet Core 9 and CentOS 9.

- (CAT-2388) Puppet Core update and Remove Puppet 7 support [#378](https://github.com/puppetlabs/puppetlabs-reboot/pull/378) ([LukasAud](https://github.com/LukasAud))
- (MODULES-11707) Add Puppet 9 support [#381](https://github.com/puppetlabs/puppetlabs-reboot/pull/381) ([skyamgarp](https://github.com/skyamgarp))
- (CAT-7110) Add CentOS 9 support [#373](https://github.com/puppetlabs/puppetlabs-reboot/pull/373) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### security_policy 1.1.0

📅 Latest release: 2026-08-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/security_policy))

A `kerberos_policy` type/provider and a `new_guest_name` class parameter are added, expanding the module's native parity coverage ahead of SCE integration. 

- [MODULES-11883/MODULES-11884] Epic F: kerberos_policy type/provider (F.1) + new_guest_name parameter (F.2) [#45](https://github.com/puppetlabs/puppetlabs-security_policy/pull/45) ([mehul-jain1](https://github.com/mehul-jain1))
- [MODULES-11884] Add new_guest_name class parameter (Epic F.2) [#44](https://github.com/puppetlabs/puppetlabs-security_policy/pull/44) ([mehul-jain1](https://github.com/mehul-jain1))
- [MODULES-11848] plan: add Epic F (native parity superset for SCE integration) [#43](https://github.com/puppetlabs/puppetlabs-security_policy/pull/43) ([mehul-jain1](https://github.com/mehul-jain1))
- plan/: post-release cleanup — Epics A/B/D/E done, Epic C transferred to puppetlabs-sce_windows [#42](https://github.com/puppetlabs/puppetlabs-security_policy/pull/42) ([mehul-jain1](https://github.com/mehul-jain1))
- [MODULES-11804] CHANGELOG: rename Breaking Changes -> Changed (release-blocker) [#41](https://github.com/puppetlabs/puppetlabs-security_policy/pull/41) ([mehul-jain1](https://github.com/mehul-jain1))

---

### service 4.0.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/service))

Drops support for Puppet version 7 (**BREAKING**) and adds version 9 support.

- (CAT-2392) Puppet Core update / Drop support for puppet 7 [#263](https://github.com/puppetlabs/puppetlabs-service/pull/263) ([LukasAud](https://github.com/LukasAud))
- (MODULES-11709) Add Puppet 9 support [#268](https://github.com/puppetlabs/puppetlabs-service/pull/268) ([imaqsood](https://github.com/imaqsood))
- Update link for contributing documentation [#264](https://github.com/puppetlabs/puppetlabs-service/pull/264) ([jst-cyr](https://github.com/jst-cyr))
- (CAT-2296) Update github runner image to ubuntu-24.04 [#262](https://github.com/puppetlabs/puppetlabs-service/pull/262) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### sshkeys_core 3.0.2

📅 Latest release: 2026-08-05 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sshkeys_core))

Hardens the sshkey type by rejecting key values that contain embedded whitespace, preventing malformed authorized_keys entries.

- (PA-8911) Reject embedded whitespace in sshkey key [#1](https://github.com/puppetlabs/puppetlabs-sshkeys_core-private/pull/1) ([mhashizume](https://github.com/mhashizume))

---

### stdlib 10.0.2

📅 Latest release: 2026-08-06 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/stdlib))

Fixes a `stdlib::manage` parser bug that failed to parse `$type` resources.

- fix(stdlib::manage) parser fails `$type` resources [#1477](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1477) ([jcpunk](https://github.com/jcpunk))

---

### tomcat 8.0.0

📅 Latest release: 2026-08-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/tomcat))

Drops Puppet 7 support (**BREAKING**) as part of a Puppet Core update, and allows the stdlib dependency to move to 10.x.

- (CAT-2396) Prepare module for Puppet Core / Drop Support for Puppet 7 [#580](https://github.com/puppetlabs/puppetlabs-tomcat/pull/580) ([david22swan](https://github.com/david22swan))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#584](https://github.com/puppetlabs/puppetlabs-tomcat/pull/584) ([imaqsood](https://github.com/imaqsood))
- Update link for contributing documentation [#583](https://github.com/puppetlabs/puppetlabs-tomcat/pull/583) ([jst-cyr](https://github.com/jst-cyr))
- (CAT-2296) Update github runner image to ubuntu-24.04 [#579](https://github.com/puppetlabs/puppetlabs-tomcat/pull/579) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### windows_eventlog 5.2.0

📅 Latest release: 2026-08-31 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/windows_eventlog))

Adds Puppet Core 9 support to the module.

- (MODULES-11729) Add Puppet 9 support [#100](https://github.com/puppetlabs/puppetlabs-windows_eventlog/pull/100) ([imaqsood](https://github.com/imaqsood))

## Until Next Time!

That wraps up the August 2026 roundup. If any of these modules intersect with your environment,  especially the five modules that removed Puppet 7 support (`package`, `node_encrypt`, `service`, `reboot`, and `tomcat`), or some of the other breaking or required changes, the linked Forge pages and release notes are worth a closer look before upgrading.

Feedback on the series is always useful, especially if there are module families or release-note patterns that deserve more attention in future editions.

More updates coming next month when the September 2026 releases land, and you should expect to see continued Puppet Core 9 support rolling out across September!

## 🤖 AI Disclosure

This roundup is produced by a mostly-automated pipeline, with some AI sprinkled in for orchestration and enrichment (or 'Combobulating' and 'Finagling'), followed by a human review (that would be me) before publishing.

The automation is an [open-source project](https://github.com/jst-cyr/puppetlabs-modules-roundup-writer) with deterministic python scripts to crawl the Forge and determine which `puppetlabs` modules were released during a specific month (and catching when a module gets more than one release in a month). By combining a template, automation scripts, and some AI orchestration the content all gets pulled together for a structured markdown document. I then jump in to double-check the content and update any wording that seems repetitive or irrelevant (and sometimes I need to add some extra context that isn't in the changelog notes).
