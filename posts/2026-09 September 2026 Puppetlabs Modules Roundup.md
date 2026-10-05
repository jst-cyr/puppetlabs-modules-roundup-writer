# Puppetlabs Modules Roundup – September 2026

**Tags:** #puppet

September 2026 brought 41 Puppetlabs module releases in the Puppetlabs Forge catalog, and this roundup pulls the most important changes into one place.

Across the month, the clearest themes were puppet 9 support rolls out across nearly the whole catalog and puppetcore prep drops puppet 7 support in five modules, so the summary below focuses on support changes, maintenance work, and operational impact.

## Highlighted Updates

### Puppet 9 support rolls out across nearly the whole catalog

Thirty-nine of the forty-one modules released this month shipped explicit Puppet 9 compatibility work — metadata bumps, new CI lanes, and in several cases a parallel Ruby 4.0 compatibility pass. The releases range from flagship modules (puppetdb, mysql, postgresql, stdlib) to the full set of Bolt task-helper and cloud-inventory modules, making this the single largest coordinated update the puppetlabs namespace has shipped in one month. facts 1.8.0 is part of the same push, after first correcting an accidental major-version bump to 2.0.0 back down to a minor release.

- Affected modules: puppetdb, mysql, kubernetes, security_policy, java_ks, docker, haproxy, iis, facter_task, yaml, vault, terraform, secure_env_vars, ruby_task_helper, ruby_plugin_helper, python_task_helper, powershell_task_helper, pkcs7, http_request, gcloud_inventory, bash_task_helper, azure_inventory, aws_inventory, chocolatey, audit_policy, sce_linux, wsus_client, powershell, apt, dsc_lite, postgresql, pwshlib, stdlib, motd, registry, windows_env, ntp, acl, facts.

### Puppetcore prep drops Puppet 7 support in five modules

As part of preparing for Puppetcore, puppetdb, registry, acl, and facter_task shipped major version bumps that drop Puppet 7 support outright; java_ks dropped it too, but in a minor release rather than a major one. Because registry 6.0.0 is a breaking change, four of its dependents — chocolatey, wsus_client, windows_eventlog, and motd — had to widen their puppetlabs/registry dependency bound to allow the new major version.

- Affected modules: puppetdb, registry, acl, facter_task, java_ks, chocolatey, wsus_client, windows_eventlog, motd.

### Breaking changes to review

A small number of releases include compatibility-impacting changes that may need extra review before rollout.

- puppetdb: puppetdb 9.0.0 drops Puppet 7 support, changes the default postgres_version from 14 to 17 to match what Puppet Enterprise now installs, and adds strict Puppet data-type validation across module parameters that may reject previously-accepted invalid values.
- registry: registry 6.0.0 drops Puppet 7 support as part of its Puppetcore update, a major-version change that required chocolatey, wsus_client, windows_eventlog, and motd to widen their dependency bounds to allow it.

### Security-related updates

The following releases include security-relevant fixes or related maintenance work.

- sce_linux: sce_linux 2.9.0 fixes three Ubuntu enforcement gaps: PAM profiles were enabled but not applied (causing 5.3.x controls to fail on nodes reported as compliant), rsyslog's hard-coded working directory broke logging on Ubuntu 22.04 and 24.04, and AIDE failed to initialize correctly.

## What Updates Happened to Puppetlabs Modules in September 2026?

The following is an alphabetical listing of modules which received updates in September 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### acl 6.0.0

📅 Latest release: 2026-09-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/acl))

This release focuses on prepare module for Puppetcore / Drop Support for Puppet 7 while also addressing add Puppet 9 support.

- (CAT-2360) Prepare module for Puppetcore / Drop Support for Puppet 7 [#310](https://github.com/puppetlabs/puppetlabs-acl/pull/310) ([david22swan](https://github.com/david22swan))
- MODULES-11712: Add Puppet 9 support [#315](https://github.com/puppetlabs/puppetlabs-acl/pull/315) ([span786](https://github.com/span786))

---

### apt 11.4.0

📅 Latest release: 2026-09-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/apt))

This release focuses on add support for puppet 9.

- (MODULES-11701) Add support for puppet 9 [#1275](https://github.com/puppetlabs/puppetlabs-apt/pull/1275) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### audit_policy 1.2.1

📅 Latest release: 2026-09-10 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/audit_policy))

This release focuses on [MODULES-11879] Fix misleading ensure-change reports when only flag differs while also addressing fix(MODULES-11932): Add puppet 9 support in puppetlabs-audit_policy.

Includes monthly releases: 1.2.1 (2026-09-10), 1.2.0 (2026-09-08), 1.1.0 (2026-09-02).

- [MODULES-11879] Fix misleading ensure-change reports when only flag differs [#31](https://github.com/puppetlabs/puppetlabs-audit_policy/pull/31) ([mehul-jain1](https://github.com/mehul-jain1))
- fix(MODULES-11932): Add puppet 9 support in puppetlabs-audit_policy [#28](https://github.com/puppetlabs/puppetlabs-audit_policy/pull/28) ([SugatD](https://github.com/SugatD))
- [MODULES-11839] Implement manifest init and add specs [#26](https://github.com/puppetlabs/puppetlabs-audit_policy/pull/26) ([SugatD](https://github.com/SugatD))
- [MODULES-11794] Reformat CHANGELOG.md to Keep a Changelog format [#24](https://github.com/puppetlabs/puppetlabs-audit_policy/pull/24) ([SugatD](https://github.com/SugatD))

---

### aws_inventory 0.9.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/aws_inventory))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.9.0) while also addressing aws_inventory Pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.9.0) [#33](https://github.com/puppetlabs/puppetlabs-aws_inventory/pull/33) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193) aws_inventory Pdk update to puppet 9 [#28](https://github.com/puppetlabs/puppetlabs-aws_inventory/pull/28) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### azure_inventory 0.6.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/azure_inventory))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.6.0) while also addressing azure_inventory pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.6.0) [#21](https://github.com/puppetlabs/puppetlabs-azure_inventory/pull/21) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193) azure_inventory pdk update to puppet 9 [#18](https://github.com/puppetlabs/puppetlabs-azure_inventory/pull/18) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### bash_task_helper 2.3.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/bash_task_helper))

This release focuses on revert version bump from major to minor (3.0.0 -> 2.3.0) while also addressing bash_task_helper pdk update to puppet 9.

- Revert version bump from major to minor (3.0.0 -> 2.3.0) [#40](https://github.com/puppetlabs/puppetlabs-bash_task_helper/pull/40) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193) bash_task_helper pdk update to puppet 9 [#37](https://github.com/puppetlabs/puppetlabs-bash_task_helper/pull/37) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### chocolatey 9.1.0

📅 Latest release: 2026-09-10 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/chocolatey))

This release focuses on add Puppet 9 support while also addressing widen puppetlabs/registry dependency to allow 6.x.

- (MODULES-11731) Add Puppet 9 support [#390](https://github.com/puppetlabs/puppetlabs-chocolatey/pull/390) ([shubhamshinde360](https://github.com/shubhamshinde360))
- (MODULES-11708) Widen puppetlabs/registry dependency to allow 6.x [#392](https://github.com/puppetlabs/puppetlabs-chocolatey/pull/392) ([span786](https://github.com/span786))

---

### docker 10.5.0

📅 Latest release: 2026-09-23 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/docker))

This release focuses on add puppet 9 support in puppetlabs-docker while also addressing point EL7 at the centos Docker CE repo path.

- (MODULES-11718) Add puppet 9 support in puppetlabs-docker [#1065](https://github.com/puppetlabs/puppetlabs-docker/pull/1065) ([imaqsood](https://github.com/imaqsood))
- (MODULES-11929) Point EL7 at the centos Docker CE repo path [#1067](https://github.com/puppetlabs/puppetlabs-docker/pull/1067) ([imaqsood](https://github.com/imaqsood))

---

### dsc_lite 5.1.0

📅 Latest release: 2026-09-08 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/dsc_lite))

This release focuses on add Puppet 9 support.

- Add Puppet 9 support [#243](https://github.com/puppetlabs/puppetlabs-dsc_lite/pull/243) ([LukasAud](https://github.com/LukasAud))

---

### facter_task 3.0.0

📅 Latest release: 2026-09-15 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/facter_task))

This release focuses on prepare module for Puppetcore / Drop Support for Puppet 7 while also addressing add Puppet 9 support.

- (CAT-2372) Prepare module for Puppetcore / Drop Support for Puppet 7 [#243](https://github.com/puppetlabs/puppetlabs-facter_task/pull/243) ([SugatD](https://github.com/SugatD))
- (MODULES-11722) Add Puppet 9 support [#246](https://github.com/puppetlabs/puppetlabs-facter_task/pull/246) ([shubhamshinde360](https://github.com/shubhamshinde360))
- (CAT-2296) Update github runner image to ubuntu-24.04 [#242](https://github.com/puppetlabs/puppetlabs-facter_task/pull/242) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### facts 1.8.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/facts))

This release focuses on revert version bump from major to minor (2.0.0 -> 1.8.0) while also addressing : facts pdk update for Puppet 9 compatibility.

- Revert version bump from major to minor (2.0.0 -> 1.8.0) [#74](https://github.com/puppetlabs/puppetlabs-facts/pull/74) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): facts pdk update for Puppet 9 compatibility [#71](https://github.com/puppetlabs/puppetlabs-facts/pull/71) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### gcloud_inventory 0.4.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/gcloud_inventory))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.4.0) while also addressing : gcloud_inventory pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.4.0) [#19](https://github.com/puppetlabs/puppetlabs-gcloud_inventory/pull/19) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): gcloud_inventory pdk update to puppet 9 [#16](https://github.com/puppetlabs/puppetlabs-gcloud_inventory/pull/16) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### haproxy 9.2.0

📅 Latest release: 2026-09-16 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/haproxy))

This release focuses on feat(MODULES-11716) Add puppet 9 support while also addressing add haproxy::http_errors and haproxy::ring resources.

- feat(MODULES-11716) Add puppet 9 support [#654](https://github.com/puppetlabs/puppetlabs-haproxy/pull/654) ([imaqsood](https://github.com/imaqsood))
- Add haproxy::http_errors and haproxy::ring resources [#651](https://github.com/puppetlabs/puppetlabs-haproxy/pull/651) ([UiP9AV6Y](https://github.com/UiP9AV6Y))
- (CAT-2125) Add Ubuntu 24.04 support [#620](https://github.com/puppetlabs/puppetlabs-haproxy/pull/620) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### http_request 0.4.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/http_request))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.4.0) while also addressing : http_request pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.4.0) [#24](https://github.com/puppetlabs/puppetlabs-http_request/pull/24) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): http_request pdk update to puppet 9 [#20](https://github.com/puppetlabs/puppetlabs-http_request/pull/20) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### iis 11.1.0

📅 Latest release: 2026-09-15 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/iis))

This release focuses on add Puppet 9 support.

- (MODULES-11733) Add Puppet 9 support [#420](https://github.com/puppetlabs/puppetlabs-iis/pull/420) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### java_ks 6.1.0

📅 Latest release: 2026-09-23 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/java_ks))

This release focuses on make keytool path configureable while also addressing prepare module for Puppetcore / Drop Support for Puppet 7.

Includes monthly releases: 6.1.0 (2026-09-23), 6.0.0 (2026-09-16).

- Make keytool path configureable [#477](https://github.com/puppetlabs/puppetlabs-java_ks/pull/477) ([bastelfreak](https://github.com/bastelfreak))
- (CAT-2377) Prepare module for Puppetcore / Drop Support for Puppet 7 [#471](https://github.com/puppetlabs/puppetlabs-java_ks/pull/471) ([shubhamshinde360](https://github.com/shubhamshinde360))
- MODULES-11721: Add Puppet 9 support [#475](https://github.com/puppetlabs/puppetlabs-java_ks/pull/475) ([span786](https://github.com/span786))
- Fix boolean parameters [#469](https://github.com/puppetlabs/puppetlabs-java_ks/pull/469) ([alexjfisher](https://github.com/alexjfisher))
- Fix race condition by memoizing `Tempfile` objects [#461](https://github.com/puppetlabs/puppetlabs-java_ks/pull/461) ([alexjfisher](https://github.com/alexjfisher))

---

### kubernetes 8.2.0

📅 Latest release: 2026-09-24 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/kubernetes))

This release focuses on add Puppet 9 support.

- MODULES-11735: Add Puppet 9 support [#723](https://github.com/puppetlabs/puppetlabs-kubernetes/pull/723) ([span786](https://github.com/span786))

---

### motd 8.1.1

📅 Latest release: 2026-09-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/motd))

This release focuses on widen puppetlabs/registry dependency to allow 6.x while also addressing add Puppet 9 support.

Includes monthly releases: 8.1.1 (2026-09-04), 8.1.0 (2026-09-02).

- (MODULES-11708) Widen puppetlabs/registry dependency to allow 6.x [#571](https://github.com/puppetlabs/puppetlabs-motd/pull/571) ([span786](https://github.com/span786))
- (MODULES-11702) Add Puppet 9 support [#561](https://github.com/puppetlabs/puppetlabs-motd/pull/561) ([imaqsood](https://github.com/imaqsood))

---

### mysql 17.3.0

📅 Latest release: 2026-09-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/mysql))

This release focuses on add ability to use hex hash with caching_sha2_password plugin while also addressing correct Fact mysqld_version on FreeBSD.

Includes monthly releases: 17.3.0 (2026-09-28), 17.2.0 (2026-09-16), 17.1.1 (2026-09-02).

- Add ability to use hex hash with caching_sha2_password plugin [#1612](https://github.com/puppetlabs/puppetlabs-mysql/pull/1612) ([C24-AK](https://github.com/C24-AK))
- Correct Fact mysqld_version on FreeBSD [#1654](https://github.com/puppetlabs/puppetlabs-mysql/pull/1654) ([kapouik](https://github.com/kapouik))
- feat(MODULES-11715) Add puppet 9 support [#1742](https://github.com/puppetlabs/puppetlabs-mysql/pull/1742) ([imaqsood](https://github.com/imaqsood))
- Restrict mysql::server::purge_conf_dir type to valid values (#1740) [#1741](https://github.com/puppetlabs/puppetlabs-mysql/pull/1741) ([jst-cyr](https://github.com/jst-cyr))
- Use deferrable_epp for .my.cnf to ensure root password resolve correctly [#1698](https://github.com/puppetlabs/puppetlabs-mysql/pull/1698) ([jiayuchen888](https://github.com/jiayuchen888))
- Update conditional logic xtrabackup.pp to properly... [#1609](https://github.com/puppetlabs/puppetlabs-mysql/pull/1609) ([ndelic0](https://github.com/ndelic0))
- allow metacharacters * and ? in sql file path [#1544](https://github.com/puppetlabs/puppetlabs-mysql/pull/1544) ([zivis](https://github.com/zivis))

---

### ntp 11.2.0

📅 Latest release: 2026-09-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/ntp))

This release focuses on add Puppet 9 support.

- (MODULES-11705) Add Puppet 9 support [#745](https://github.com/puppetlabs/puppetlabs-ntp/pull/745) ([skyamgarp](https://github.com/skyamgarp))

---

### peadm 3.38.3

📅 Latest release: 2026-09-15 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm))

This release focuses on adding support for PE 2023.8.11 and 2025.11.3 while also addressing complete CA storage migration for split topologies.

Includes monthly releases: 3.38.3 (2026-09-15), 3.38.2 (2026-09-01).

- Adding support for PE 2023.8.11 and 2025.11.3 [#702](https://github.com/puppetlabs/puppetlabs-peadm/pull/702) ([Jade2153](https://github.com/Jade2153))
- (PE-45431) Complete CA storage migration for split topologies [#696](https://github.com/puppetlabs/puppetlabs-peadm/pull/696) ([Jade2153](https://github.com/Jade2153))
- (PE-43490) Surface provision_replica failures in add_replica plan [#677](https://github.com/puppetlabs/puppetlabs-peadm/pull/677) ([CharithaDunuwille](https://github.com/CharithaDunuwille))
- (PE-45885) Add code-manager to the managed database list [#698](https://github.com/puppetlabs/puppetlabs-peadm/pull/698) ([Magisus](https://github.com/Magisus))
- (PE-45110) Ruby 4.0 compatibility: fix missing default-gem deps, document upstream blockers maintenance [#685](https://github.com/puppetlabs/puppetlabs-peadm/pull/685) ([CharithaDunuwille](https://github.com/CharithaDunuwille))
- (PE-45390) Add code coverage reporting to CI [#686](https://github.com/puppetlabs/puppetlabs-peadm/pull/686) ([seamymckenna](https://github.com/seamymckenna))
- Adding support for PE 2025.11.2 [#694](https://github.com/puppetlabs/puppetlabs-peadm/pull/694) ([Jade2153](https://github.com/Jade2153))

---

### pkcs7 0.2.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/pkcs7))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.2.0) while also addressing : pkcs7 pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.2.0) [#19](https://github.com/puppetlabs/puppetlabs-pkcs7/pull/19) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): pkcs7 pdk update to puppet 9 [#15](https://github.com/puppetlabs/puppetlabs-pkcs7/pull/15) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### postgresql 10.7.0

📅 Latest release: 2026-09-08 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/postgresql))

This release focuses on add puppet 9 support in puppetlabs-postgresql while also addressing allow puppet/systemd 10.x.

- (MODULES-11720) Add puppet 9 support in puppetlabs-postgresql [#1700](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1700) ([imaqsood](https://github.com/imaqsood))
- Allow puppet/systemd 10.x [#1691](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1691) ([deric](https://github.com/deric))
- (MODULES-11935) Fix default_privileges idempotency on PostgreSQL 17 [#1701](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1701) ([imaqsood](https://github.com/imaqsood))

---

### powershell 6.2.0

📅 Latest release: 2026-09-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/powershell))

This release focuses on add support for Puppet 9.

- (MODULES-11706) Add support for Puppet 9 [#440](https://github.com/puppetlabs/puppetlabs-powershell/pull/440) ([shubhamshinde360](https://github.com/shubhamshinde360))

---

### powershell_task_helper 0.2.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/powershell_task_helper))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.2.0) while also addressing powershell_task_helper pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.2.0) [#10](https://github.com/puppetlabs/puppetlabs-powershell_task_helper/pull/10) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193) powershell_task_helper pdk update to puppet 9 [#7](https://github.com/puppetlabs/puppetlabs-powershell_task_helper/pull/7) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### puppetdb 9.0.0

📅 Latest release: 2026-09-30 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppetdb))

This release focuses on add strict Puppet data type validation across module parameters (String, Integer, Boolean, Enum, Array, Hash, Absolutepath, Stdlib::Host, etc.), including port validation restricted to the unprivileged range (1024-49151) while also addressing support for Puppet 9.

- Add strict Puppet data type validation across module parameters (String, Integer, Boolean, Enum, Array, Hash, Absolutepath, Stdlib::Host, etc.), including port validation restricted to the unprivileged range (1024-49151) [#411](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/411) ([chambersmp](https://github.com/chambersmp))
- Support for Puppet 9
- **Breaking:** Default `postgres_version` bumped from `14` to `17` to match the version installed by the latest Puppet Enterprise
- Use the `Sensitive` data type for secrets (passwords) [#331](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/331) ([cocker-cc](https://github.com/cocker-cc))
- Extend the `puppetdb_version` fact to handle Debian packages [#416](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/416) ([rwaffen](https://github.com/rwaffen))
- Updated to PDK 3.8.0, dropped Puppet 7 support, and tightened version requirements on module dependencies
- Update CI workflows (maint) [#410](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/410) ([h0tw1r3](https://github.com/h0tw1r3))
- Update CODEOWNERS [#417](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/417) ([chambersmp](https://github.com/chambersmp))
- Correct spelling of "certificates" [#414](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/414) ([viscountstyx](https://github.com/viscountstyx))
- Lower the `stdlib` requirement back down, since `puppetdb` depends on `puppetlabs/postgresql`, which depends on `puppet/systemd`, and `puppet/systemd` does not yet support `stdlib >= 10.0.0`
- Correct stale `postgres_version` documentation in `puppetdb::init` and `puppetdb::database::postgresql` that still referenced the old `11`/`9.6` defaults
- Set `open_ssl_port` to default `false` instead of `undef` in unit test shared examples
- Prepare module for Puppet 9 [#438](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/438) ([gavindidrichsen](https://github.com/gavindidrichsen))
- Feature maintenance [#436](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/436) ([klab-systems](https://github.com/klab-systems))
- Update storeconfig ini section with masters [#432](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/432) ([XMol](https://github.com/XMol))
- Issue 430: Fix Datatype for listen_addresses [#431](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/431) ([cocker-cc](https://github.com/cocker-cc))
- Only include 'firewall' module when necessary [#415](https://github.com/puppetlabs/puppetlabs-puppetdb/pull/415) ([Geod24](https://github.com/Geod24))

---

### pwshlib 2.1.1

📅 Latest release: 2026-09-07 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/pwshlib))

This release focuses on declare Puppet 9 support in metadata.json requirements while also addressing add Ruby 4.0 / Puppet 9 lane, source gems from puppetcore.

Includes monthly releases: 2.1.1 (2026-09-07), 2.1.0 (2026-09-07).

- Declare Puppet 9 support in metadata.json requirements [#393](https://github.com/puppetlabs/ruby-pwsh/pull/393) ([LukasAud](https://github.com/LukasAud))
- (CAT-2589) Add Ruby 4.0 / Puppet 9 lane, source gems from puppetcore [#385](https://github.com/puppetlabs/ruby-pwsh/pull/385) ([LukasAud](https://github.com/LukasAud))

---

### python_task_helper 0.7.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/python_task_helper))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.7.0) while also addressing : python_task_helper pdk update to pupet 9.

- Revert version bump from major to minor (1.0.0 -> 0.7.0) [#25](https://github.com/puppetlabs/puppetlabs-python_task_helper/pull/25) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): python_task_helper pdk update to pupet 9 [#22](https://github.com/puppetlabs/puppetlabs-python_task_helper/pull/22) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### registry 6.0.0

📅 Latest release: 2026-09-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/registry))

This release focuses on puppetcore update / Drop puppet 7 support while also addressing add Puppet 9 support.

- (CAT-2389) Puppetcore update / Drop puppet 7 support [#315](https://github.com/puppetlabs/puppetlabs-registry/pull/315) ([LukasAud](https://github.com/LukasAud))
- MODULES-11708: Add Puppet 9 support [#320](https://github.com/puppetlabs/puppetlabs-registry/pull/320) ([span786](https://github.com/span786))
- (PA-8354): Add support for Sensitive data in registry_value [#319](https://github.com/puppetlabs/puppetlabs-registry/pull/319) ([span786](https://github.com/span786))
- Update link to Puppet modules contribution documentation [#318](https://github.com/puppetlabs/puppetlabs-registry/pull/318) ([jst-cyr](https://github.com/jst-cyr))

---

### ruby_plugin_helper 0.4.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/ruby_plugin_helper))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.4.0) while also addressing ruby_plugin_helper pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.4.0) [#13](https://github.com/puppetlabs/puppetlabs-ruby_plugin_helper/pull/13) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193) ruby_plugin_helper pdk update to puppet 9 [#10](https://github.com/puppetlabs/puppetlabs-ruby_plugin_helper/pull/10) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### ruby_task_helper 1.1.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/ruby_task_helper))

This release focuses on revert version bump from major to minor (2.0.0 -> 1.1.0) while also addressing : ruby_task_helper pdk update to puppet 9.

- Revert version bump from major to minor (2.0.0 -> 1.1.0) [#31](https://github.com/puppetlabs/puppetlabs-ruby_task_helper/pull/31) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): ruby_task_helper pdk update to puppet 9 [#26](https://github.com/puppetlabs/puppetlabs-ruby_task_helper/pull/26) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### sce_linux 2.9.0

📅 Latest release: 2026-09-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_linux))

A few highlights from this release:
- **Crypto controls incorrectly configured on** Rocky Linux **8.** Crypto controls are intended to prevent the use of weak Message Authentication Code (MAC) algorithms. On Rocky Linux 8, the controls were not working as designed. The manage_crypto_policies block was updated to resolve the issue and enforce strong algorithms.
- **Error occurs when specifying active zone target for firewalld.** Previously, an error occurred when users set an active zone target for the firewalld solution by specifying {"public"=>{"target"=>"DROP"}}. The "unable to parse" error was displayed because the {"public"=>{"target"=>"DROP"}} example shown on the Puppet Forge **Reference** page was invalid. To resolve the issue, the **Reference** page was updated to display only the valid example:.
- **PAM profiles not applied on** Ubuntu Linux. Previously, pluggable authentication module (PAM) profiles were enabled but not applied, causing some 5.3.x controls to fail on nodes reported as compliant. The issue was resolved to ensure that the profiles are applied and the PAM stack is hardened.

Check the official [release notes for sce_linux 2.9.0](https://help.puppet.com/sce/current/linux/scel_relnotes_v290.htm) for the full details.

---

### secure_env_vars 0.3.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/secure_env_vars))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.3.0) while also addressing : secure_env_vars pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.3.0) [#8](https://github.com/puppetlabs/puppetlabs-secure_env_vars/pull/8) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): secure_env_vars pdk update to puppet 9 [#5](https://github.com/puppetlabs/puppetlabs-secure_env_vars/pull/5) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### security_policy 1.2.0

📅 Latest release: 2026-09-24 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/security_policy))

This release focuses on [MODULES-11933] Add Puppet 9 support while also addressing [MODULES-11947] Isolate per-SID translation failures from the whole batch.

Includes monthly releases: 1.2.0 (2026-09-23), 1.1.2 (2026-09-18), 1.1.1 (2026-09-01).

- [MODULES-11933] Add Puppet 9 support [#57](https://github.com/puppetlabs/puppetlabs-security_policy/pull/57) ([SugatD](https://github.com/SugatD))
- [MODULES-11947] Isolate per-SID translation failures from the whole batch [#55](https://github.com/puppetlabs/puppetlabs-security_policy/pull/55) ([mehul-jain1](https://github.com/mehul-jain1))
- Fix security_option provider missing out-of-band security policy drift [#50](https://github.com/puppetlabs/puppetlabs-security_policy/pull/50) ([mehul-jain1](https://github.com/mehul-jain1))

---

### stdlib 10.1.0

📅 Latest release: 2026-09-07 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/stdlib))

This release focuses on add Puppet 9 support.

- (MODULES-11710) Add Puppet 9 support [#1482](https://github.com/puppetlabs/puppetlabs-stdlib/pull/1482) ([skyamgarp](https://github.com/skyamgarp))

---

### terraform 0.8.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/terraform))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.8.0) while also addressing terraform pdk update to Puppet 9 (Ruby 4).

- Revert version bump from major to minor (1.0.0 -> 0.8.0) [#46](https://github.com/puppetlabs/puppetlabs-terraform/pull/46) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193) terraform pdk update to Puppet 9 (Ruby 4) [#43](https://github.com/puppetlabs/puppetlabs-terraform/pull/43) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### vault 0.5.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/vault))

This release focuses on fix metadata versionRevert version bump from major to minor (1.0.0 -> 0.5.0) while also addressing : vault pdk update to puppet 9.

- Fix metadata versionRevert version bump from major to minor (1.0.0 -> 0.5.0) [#24](https://github.com/puppetlabs/puppetlabs-vault/pull/24) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): vault pdk update to puppet 9 [#21](https://github.com/puppetlabs/puppetlabs-vault/pull/21) ([gavindidrichsen](https://github.com/gavindidrichsen))

---

### windows_env 6.2.0

📅 Latest release: 2026-09-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/windows_env))

This release focuses on add support for Puppet 9.

- (MODULES-11728) Add support for Puppet 9 [#117](https://github.com/puppetlabs/puppetlabs-windows_env/pull/117) ([SugatD](https://github.com/SugatD))

---

### windows_eventlog 5.2.1

📅 Latest release: 2026-09-04 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/windows_eventlog))

This release focuses on widen puppetlabs/registry dependency to allow 6.x while also addressing configure Mend for GitHub.com.

- (MODULES-11708) Widen puppetlabs/registry dependency to allow 6.x [#103](https://github.com/puppetlabs/puppetlabs-windows_eventlog/pull/103) ([span786](https://github.com/span786))
- Configure Mend for GitHub.com [#92](https://github.com/puppetlabs/puppetlabs-windows_eventlog/pull/92) ([mend-for-github-com](https://github.com/mend-for-github-com))

---

### wsus_client 6.4.0

📅 Latest release: 2026-09-09 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/wsus_client))

This release focuses on add Puppet 9 support while also addressing widen puppetlabs/registry dependency to allow 6.x.

- MODULES-11737: Add Puppet 9 support [#240](https://github.com/puppetlabs/puppetlabs-wsus_client/pull/240) ([span786](https://github.com/span786))
- (MODULES-11708) Widen puppetlabs/registry dependency to allow 6.x [#241](https://github.com/puppetlabs/puppetlabs-wsus_client/pull/241) ([span786](https://github.com/span786))

---

### yaml 0.3.0

📅 Latest release: 2026-09-11 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/yaml))

This release focuses on revert version bump from major to minor (1.0.0 -> 0.3.0) while also addressing : yaml pdk update to puppet 9.

- Revert version bump from major to minor (1.0.0 -> 0.3.0) [#11](https://github.com/puppetlabs/puppetlabs-yaml/pull/11) ([gavindidrichsen](https://github.com/gavindidrichsen))
- (BOLT-193): yaml pdk update to puppet 9 [#8](https://github.com/puppetlabs/puppetlabs-yaml/pull/8) ([gavindidrichsen](https://github.com/gavindidrichsen))

## Until Next Time!

That wraps up the September 2026 roundup. If any of puppetdb, mysql intersect with your environment, the linked Forge pages and release notes are worth a closer look.

Feedback on the series is always useful, especially if there are module families or release-note patterns that deserve more attention in future editions.

More updates coming next month when the October 2026 releases land.

## 🤖 AI Disclosure

This roundup is produced by a mostly-automated pipeline, with some AI sprinkled in for orchestration and enrichment (or 'Combobulating' and 'Finagling'), followed by a human review (that would be me) before publishing.

The automation is an [open-source project](https://github.com/jst-cyr/puppetlabs-modules-roundup-writer) with deterministic python scripts to crawl the Forge and determine which `puppetlabs` modules were released during a specific month (and catching when a module gets more than one release in a month). By combining a template, automation scripts, and some AI orchestration the content all gets pulled together for a structured markdown document. I then jump in to double-check the content and update any wording that seems repetitive or irrelevant (and sometimes I need to add some extra context that isn't in the changelog notes).
