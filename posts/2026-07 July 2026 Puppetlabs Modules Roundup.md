# Puppetlabs Modules Roundup – July 2026

**Tags:** #puppet

July 2026 brought 17 Puppetlabs module releases, headlined by the largest Continuous Delivery release of the year: cd4peadm 5.16.0 adds external PostgreSQL database support and a configurable image pull policy, and closes 11 CVEs, alongside a breaking change to commit status contexts. Elsewhere, five modules continued the Puppet Core alignment pass by dropping Puppet 7 support, four more modules picked up the stdlib 10.x rollout that started in June, and three Windows-focused modules added Windows Server 2025 support. This roundup pulls the most important changes into one place.

## Highlighted Updates

### Continuous Delivery Adds External Databases, Configurable Image Pull Policies, and Closes 11 CVEs

cd4peadm 5.16.0 is the biggest release of the month. It adds support for pointing Continuous Delivery at an externally managed PostgreSQL database — a self-managed instance, Amazon RDS for PostgreSQL, or Amazon Aurora — instead of the database CD manages internally, giving operators control over durability, backups, and high availability. It also adds a configurable `image_pull_policy` option for job templates (`Always`/`IfNotPresent`/`Never`) and removes the `docker.io` fallback when using Podman; the matching cd4pe_jobs 1.7.4 release adds the same task parameter and fallback removal, so upgrade both together.

- **BREAKING:** Commit status contexts now include the pipeline name (`cd-pe/<pipelineName>/stage-<N>` instead of `cd-pe/stage-<N>`) — review any branch protection rules or required status checks that reference the old format.
- Closes 11 CVEs across opentelemetry, NGINX, jetty, jackson, log4j, postgresql, golang.org/x/sys, and react-router.

### Puppet Core Alignment / Puppet 7 Support Dropped

Five modules completed Puppet Core alignment passes this month, dropping Puppet 7 support in major version bumps as Puppet 7 nears end-of-life.

- Affected modules: haproxy, iis, mount_iso, scheduled_task, sslcertificate.

Unlike June's postgresql misstep — where the Puppet 7 removal shipped in a patch release instead of a major one — this month's Puppet Core work all landed in proper major version bumps. Speaking of which, postgresql 10.6.3 restores the Puppet 7 support that 10.6.2 broke; see its entry below.

### stdlib 10.x Rollout Continues

Following June's stdlib 10.x rollout — which noted more modules would follow in July — four more modules now allow the puppetlabs-stdlib dependency to move to 10.x: haproxy, mount_iso, puppet_authorization, and sslcertificate. haproxy also widens its concat constraint to 10.x.

- Affected modules: haproxy, mount_iso, puppet_authorization, sslcertificate.

### Windows Server 2025 Support Added

Three Windows-focused modules — scheduled_task, windows_env, and windows_eventlog — add support for Windows Server 2025 this month.

- Affected modules: scheduled_task, windows_env, windows_eventlog.

## What Updates Happened to Puppetlabs Modules in July 2026?

The following is an alphabetical listing of modules which received updates in July 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### apache 13.3.0

📅 Latest release: 2026-07-23 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/apache))

Scaffolds OWASP ModSecurity Core Rule Set v4 support on EL10 via a new `crs_source` enum — a foundational step, not full CRS v4 support yet.

- (MODULES-11857) Scaffold OWASP CRS v4 support on EL10 via crs_source enum [#2637](https://github.com/puppetlabs/puppetlabs-apache/pull/2637) ([SugatD](https://github.com/SugatD))

---

### cd4pe_jobs 1.7.4

📅 Latest release: 2026-07-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4pe_jobs))

Adds the same configurable `image_pull_policy` task parameter and Podman fallback removal shipping in cd4peadm 5.16.0 — upgrade both together to get matching behavior.

- A new optional `image_pull_policy` task parameter controls whether the container image is pulled before a job runs: `Always` (the default, and the previous behavior) pulls on every run; `IfNotPresent` pulls only when the image is absent from the local runtime; `Never` skips the pull entirely and relies on the locally present image. Presence is checked with `docker image inspect` / `podman image exists`. Omitting the parameter keeps the existing pull-every-run behavior.
- The module no longer retries a failed image pull against `docker.io`. Image names are now pulled exactly as given. If you rely on unqualified image names (e.g. `nginx`, `myuser/myimage`) on a Podman host, add `docker.io` to `unqualified-search-registries` in `registries.conf`, or use a fully-qualified name.

---

### cd4peadm 5.16.0

📅 Latest release: 2026-07-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4peadm))

The largest Continuous Delivery release of the month: adds external PostgreSQL database support, a configurable image pull policy, source control token management improvements, and closes 11 CVEs. Also ships a breaking change to commit status contexts — see below.

- Added support for external databases. You can now point Continuous Delivery at a PostgreSQL instance you operate yourself, Amazon RDS for PostgreSQL, Amazon Aurora (PostgreSQL-compatible), or a self-managed PostgreSQL server, instead of the database CD manages for you. This gives you control over durability, backups, and high availability. You can configure external mode on a fresh install or migrate an existing managed install.
- Added a feature to Continuous Delivery job templates so you can set an image pull policy per job (`Always`, `IfNotPresent`, or `Never`). In an air-gapped environment, for example, setting the policy to `Never` stops Continuous Delivery's attempts to reach out to the internet for the image.
- Updated the **Source Control** settings page to show when a configured Personal Access Token (PAT) expires on each connected GitHub, GitHub Enterprise, and GitLab integration card. Tokens that have already expired or will expire within 30 days are clearly flagged so you can renew them before they cause failures.
- **BREAKING:** Commit status contexts now include the pipeline name (`cd-pe/<pipelineName>/stage-<N>` instead of `cd-pe/stage-<N>`), which prevents collisions when multiple pipelines report status for the same commit. Review any branch protection rules or required status checks that reference the old format.
- 11 CVEs addressed, including opentelemetry, NGINX, jetty, jackson, log4j, postgresql, golang.org/x/sys, and react-router.

Check the official [release notes for cd4peadm 5.16.0](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm#Version5160) for the full details.

---

### comply 3.8.1

📅 Latest release: 2026-07-03 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/comply))

A Security Compliance Management maintenance release — no new CVE fixes this time, mostly operational and licensing improvements.

- Increased the CIS-CAT Pro Assessor license expiry time; licenses are now good for a full year.
- Added a `license_path` parameter to update the CIS-CAT Pro Assessor license without upgrading SCM.
- Added an `assessor_scan_timeout` option to control the task timeout for Windows 2022 domain controllers.
- Added a background scan sweeper that detects and cancels scans stuck in a "running" state.
- Increased the default **Max graphql requests limit** to 300 requests per window; use the `complyadm::configure` Bolt plan to customize.

Check the official [release notes for comply 3.8.1](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm#SecurityComplianceManagement381) for the full details.

---

### haproxy 9.1.0

📅 Latest release: 2026-07-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/haproxy))

Two releases this month: 9.0.0 drops Puppet 7 support (**BREAKING**) and adds `cache` resource support, while 9.1.0 removes a sensitive-data workaround and allows both stdlib and concat to move to their 10.x releases.

Includes monthly releases: 9.1.0 (2026-07-28), 9.0.0 (2026-07-20).

- Eliminate Workaround for Sensitive Data; raises minimum `puppetlabs/concat` requirement to `7.4.0` [#607](https://github.com/puppetlabs/puppetlabs-haproxy/pull/607) ([cocker-cc](https://github.com/cocker-cc))
- Add support for running programs [#604](https://github.com/puppetlabs/puppetlabs-haproxy/pull/604) ([deric](https://github.com/deric))
- Pass install_options to package installer [#603](https://github.com/puppetlabs/puppetlabs-haproxy/pull/603) ([deric](https://github.com/deric))
- examples: disable default stats listener [#640](https://github.com/puppetlabs/puppetlabs-haproxy/pull/640) ([bastelfreak](https://github.com/bastelfreak))
- make picking haproxy::globals::sort_options_alphabetic work [#573](https://github.com/puppetlabs/puppetlabs-haproxy/pull/573) ([trefzer](https://github.com/trefzer))
- **Remove Puppet 7 support (BREAKING); the module now requires `puppet >= 8.0.0 < 9.0.0`** [#631](https://github.com/puppetlabs/puppetlabs-haproxy/pull/631) ([gavindidrichsen](https://github.com/gavindidrichsen))
- Add support for `cache` resource, extra backend options, and docs [#626](https://github.com/puppetlabs/puppetlabs-haproxy/pull/626) ([matejzero](https://github.com/matejzero))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#642](https://github.com/puppetlabs/puppetlabs-haproxy/pull/642) ([imaqsood](https://github.com/imaqsood))
- Allow puppetlabs/concat 10.x [#641](https://github.com/puppetlabs/puppetlabs-haproxy/pull/641) ([bastelfreak](https://github.com/bastelfreak))
- dependency: create mapfile before configfile [#572](https://github.com/puppetlabs/puppetlabs-haproxy/pull/572) ([trefzer](https://github.com/trefzer))

---

### iis 11.0.0

📅 Latest release: 2026-07-01 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/iis))

Drops Puppet 7 support (**BREAKING**) as part of the module's Puppet Core update, and marks the `iis_application_pool` password parameter as sensitive so it no longer leaks into Puppet reports.

- (CAT-2374) Puppet Core update (BREAKING) — drops Puppet 7 support [#414](https://github.com/puppetlabs/puppetlabs-iis/pull/414) ([LukasAud](https://github.com/LukasAud))
- (MODULES-11595) Mark iis_application_pool password as sensitive to stop report leak [#418](https://github.com/puppetlabs/puppetlabs-iis/pull/418) ([imaqsood](https://github.com/imaqsood))

---

### mount_iso 5.0.0

📅 Latest release: 2026-07-22 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/mount_iso))

Drops Puppet 7 support (**BREAKING**) as part of a Puppet Core update, and allows the stdlib dependency to move to 10.x.

- (CAT-2380) Update for Puppet Core / Drop Support for Puppet 7 (BREAKING) [#58](https://github.com/puppetlabs/puppetlabs-mount_iso/pull/58) ([david22swan](https://github.com/david22swan))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#59](https://github.com/puppetlabs/puppetlabs-mount_iso/pull/59) ([imaqsood](https://github.com/imaqsood))

---

### mysql 17.1.0

📅 Latest release: 2026-07-02 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/mysql))

Adds support for RHEL 10.

- (MODULES-11802) Add support for RHEL 10 [#1712](https://github.com/puppetlabs/puppetlabs-mysql/pull/1712) ([skyamgarp](https://github.com/skyamgarp))

---

### node_encrypt 3.2.0

📅 Latest release: 2026-07-22 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/node_encrypt))

Adds Ubuntu 24 and Debian 12 support, and upgrades rexml to address a CVE.

- (CAT-2124) Add support for Ubuntu 24 [#120](https://github.com/puppetlabs/puppetlabs-node_encrypt/pull/120) ([skyamgarp](https://github.com/skyamgarp))
- (CAT-2100) Add Debian 12 support [#119](https://github.com/puppetlabs/puppetlabs-node_encrypt/pull/119) ([shubhamshinde360](https://github.com/shubhamshinde360))
- (CAT-2158) Upgrade rexml to address CVE-2024-49761 [#121](https://github.com/puppetlabs/puppetlabs-node_encrypt/pull/121) ([amitkarsale](https://github.com/amitkarsale))

---

### peadm 3.38.1

📅 Latest release: 2026-07-08 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm))

Restores public-schema privileges on PostgreSQL 15+ in `restore.pp`, fixing a bug that could affect PE restores on newer PostgreSQL versions.

- (PE-44867) Restore public-schema privileges on PostgreSQL 15+ in restore.pp [#676](https://github.com/puppetlabs/puppetlabs-peadm/pull/676) ([CharithaDunuwille](https://github.com/CharithaDunuwille))

---

### postgresql 10.6.3

📅 Latest release: 2026-07-07 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/postgresql))

Restores Puppet 7 support that was unintentionally dropped in the 10.6.2 patch release last month.

**NOTE:** As flagged in June's roundup, the Puppet 7 removal in 10.6.2 shipped in a patch release rather than a major one. 10.6.3 restores Puppet 7 support; the removal will happen again, correctly, in a future major release.

- (MODULES-11858) Restore Puppet 7 support broken by 10.6.2 [#1686](https://github.com/puppetlabs/puppetlabs-postgresql/pull/1686) ([imaqsood](https://github.com/imaqsood))

---

### puppet_authorization 1.0.1

📅 Latest release: 2026-07-21 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_authorization))

A maintenance release: allows both the stdlib and concat dependencies to move to 10.x, tweaks a CI workflow flag, and adds a LICENSE file.

- Change flag option in CI workflow [#56](https://github.com/puppetlabs/puppetlabs-puppet_authorization/pull/56) ([zaben903](https://github.com/zaben903))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#57](https://github.com/puppetlabs/puppetlabs-puppet_authorization/pull/57) ([imaqsood](https://github.com/imaqsood))
- puppetlabs/concat: Allow 10.x [#55](https://github.com/puppetlabs/puppetlabs-puppet_authorization/pull/55) ([bastelfreak](https://github.com/bastelfreak))
- Create LICENSE [#52](https://github.com/puppetlabs/puppetlabs-puppet_authorization/pull/52) ([binford2k](https://github.com/binford2k))

---

### sce_linux 2.8.0

📅 Latest release: 2026-07-28 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_linux))

Updates CIS Benchmarks from v3.0.0 to v4.0.0 for RHEL 8, AlmaLinux 8, and Oracle Linux 8, with matching control updates for each, and fixes three bugs affecting benchmark enforcement.

- **Updated CIS Benchmarks.** RHEL 8, AlmaLinux 8, and Oracle Linux 8 move from CIS Benchmark v3.0.0 to v4.0.0, with matching control updates for each operating system.
- **Updated dependency.** SCE for Linux now supports puppetlabs-stdlib >= 9.2.0 < 11.0.0; avoid using earlier stdlib versions.
- **Fixed:** the user-specified `default_zone` setting was not enforced for CIS control 3.4.1.2; it is now enforced correctly.
- **Fixed:** `aide --init` failed on RHEL/AlmaLinux/Oracle Linux/Rocky Linux 8 hosts shipping AIDE 0.17.x, which renamed the `database=` directive to `database_in=`.
- **Fixed:** CIS control 6.2.2.2 (journald log-forwarding) did not work as designed on RHEL/AlmaLinux/Oracle Linux/Rocky Linux 9 and 10; control 6.2.3.3 was also added.

Check the official [release notes for sce_linux 2.8.0](https://help.puppet.com/sce/current/linux/scel_relnotes_280.htm) for the full details.

---

### scheduled_task 5.0.0

📅 Latest release: 2026-07-13 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/scheduled_task))

Drops Puppet 7 support (**BREAKING**) as part of a Puppet Core upgrade, and adds Windows Server 2025 support.

- (CAT-2391) Puppet Core upgrade (BREAKING) — drops Puppet 7 support [#271](https://github.com/puppetlabs/puppetlabs-scheduled_task/pull/271) ([LukasAud](https://github.com/LukasAud))
- [MODULES-11616] Adding Windows 2025 support to module [#275](https://github.com/puppetlabs/puppetlabs-scheduled_task/pull/275) ([jst-cyr](https://github.com/jst-cyr))
- Update link to contributing documentation [#273](https://github.com/puppetlabs/puppetlabs-scheduled_task/pull/273) ([jst-cyr](https://github.com/jst-cyr))

---

### sslcertificate 6.0.0

📅 Latest release: 2026-07-22 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/sslcertificate))

Drops Puppet 7 support (**BREAKING**) as part of a Puppet Core update, and allows the stdlib dependency to move to 10.x.

- (CAT-2394) Puppet Core update (BREAKING) — drops Puppet 7 support [#142](https://github.com/puppetlabs/puppetlabs-sslcertificate/pull/142) ([LukasAud](https://github.com/LukasAud))
- (MODULES-11840) Allow puppetlabs/stdlib 10.x [#143](https://github.com/puppetlabs/puppetlabs-sslcertificate/pull/143) ([imaqsood](https://github.com/imaqsood))

---

### windows_env 6.1.0

📅 Latest release: 2026-07-21 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/windows_env))

Adds Windows Server 2025 support.

- (MODULES-11891) Add Windows Server 2025 support [#115](https://github.com/puppetlabs/puppetlabs-windows_env/pull/115) ([imaqsood](https://github.com/imaqsood))

---

### windows_eventlog 5.1.0

📅 Latest release: 2026-07-22 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/windows_eventlog))

Adds Windows Server 2025 support.

- (MODULES-11892) Add Windows Server 2025 support [#98](https://github.com/puppetlabs/puppetlabs-windows_eventlog/pull/98) ([imaqsood](https://github.com/imaqsood))

## Until Next Time!

That wraps up the July 2026 roundup. If any of these modules intersect with your environment — especially the cd4peadm breaking change to commit status contexts, and the Puppet 7 removals across haproxy, iis, mount_iso, scheduled_task, and sslcertificate — the linked Forge pages and release notes are worth a closer look before upgrading.

Feedback on the series is always useful, especially if there are module families or release-note patterns that deserve more attention in future editions.

More updates coming next month when the August 2026 releases land.

## 🤖 AI Disclosure

<!-- Static text — emitted verbatim by scripts/04_generate_roundup.py (AI_DISCLOSURE). Keep the two in sync. -->

This roundup is produced by a mostly-automated pipeline, with some AI sprinkled in for orchestration and enrichment (or 'Combobulating' and 'Finagling'), followed by a human review (that would be me) before publishing.

The automation is an [open-source project](https://github.com/jst-cyr/puppetlabs-modules-roundup-writer) with deterministic python scripts to crawl the Forge and determine which `puppetlabs` modules were released during a specific month (and catching when a module gets more than one release in a month). By combining a template, automation scripts, and some AI orchestration the content all gets pulled together for a structured markdown document. I then jump in to double-check the content and update any wording that seems repetitive or irrelevant (and sometimes I need to add some extra context that isn't in the changelog notes).
