# Puppetlabs Modules Roundup – May 2026

**Tags:** #puppet

This time around we look back at May 2026 and the 11 Puppetlabs module releases on the Forge, with an emphasis on the changes most likely to matter in active environments.

## Highlighted Updates

### New Windows audit policy module released!

The new [audit_policy module](https://forge.puppet.com/modules/puppetlabs/audit_policy/readme) has been released by Perforce as a Ruby replacement for the generated [DSC community auditpolicydsc module](https://forge.puppet.com/modules/dsc/auditpolicydsc/readme).

This module uses Puppet Resources API for managing Windows audit policy using `auditpol.exe`

### ruby_task_helper Dependency Bound Update

Five Bolt-adjacent modules all bumped the ruby_task_helper upper bound to < 2.0.0 in a coordinated maintenance pass, ensuring forward compatibility with the upcoming 2.x release.

- Affected modules: vault, terraform, http_request, gcloud_inventory, azure_inventory.

### CentOS 9 Support

Multiple modules added explicit CentOS 9 compatibility, expanding the Linux platform coverage in line with the broader Puppet ecosystem push.

- Affected modules: concat, inifile.

## What Updates Happened to Puppetlabs Modules in May 2026?

The following is an alphabetical listing of modules which received updates in May 2026. If a module had multiple versions released, the updates are collected together, numbered with the "latest" version available.

---

### apt 11.3.1

📅 Latest release: 2026-05-19 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/apt))

This release introduced an explicit hash value syntax while also adding a param to support purging keyrings and other community contributions.

Includes monthly releases: 11.3.1 (2026-05-19), 11.3.0 (2026-05-18).

- Use explicit hash value syntax instead of shorthand [#1285](https://github.com/puppetlabs/puppetlabs-apt/pull/1285) ([SugatD](https://github.com/SugatD))
- Add param for purging keyrings [#1266](https://github.com/puppetlabs/puppetlabs-apt/pull/1266) ([bwitt](https://github.com/bwitt))
- Include components when suite does not end with slash [#1259](https://github.com/puppetlabs/puppetlabs-apt/pull/1259) ([bwitt](https://github.com/bwitt))
- Bugfix - sources format and ensure => absent fails [#1243](https://github.com/puppetlabs/puppetlabs-apt/pull/1243) ([traylenator](https://github.com/traylenator))
- fix: allow plus signs in ppa [#1222](https://github.com/puppetlabs/puppetlabs-apt/pull/1222) ([moritz-makandra](https://github.com/moritz-makandra))
- Fix and improve DEB822-style template [#1212](https://github.com/puppetlabs/puppetlabs-apt/pull/1212) ([smortex](https://github.com/smortex))

---

### audit_policy 1.0.0

🌟 ***New Module:*** 2026-05-29 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/audit_policy))

This new module allows you to manage Windows audit policy with auditpol.exe as a replacement for the generated DSC community module. Initial release contains:

- audit_policy_subcategory: manage Windows audit policy subcategories by display name using auditpol.exe
- audit_policy_guid: manage Windows audit policy subcategories by GUID using auditpol.exe
- audit_policy_option: manage global Windows audit policy options (CrashOnAuditFail, FullPrivilegeAuditing, AuditBaseObjects, AuditBaseDirectories)
- audit_policy_csv: manage Windows audit policy by importing settings from an auditpol /backup CSV file
- Support for Windows Server 2016, 2019, 2022, and 2025
- Pure Ruby implementation — no PowerShell dependency; replaces the dsc-auditpolicydsc community module
- Puppet requirement pinned to >= 8.0.0 < 9.0.0

---

### azure_inventory 0.5.1

📅 Latest release: 2026-05-14 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/azure_inventory))

This release bumped the ruby_task_helper upper bound to **< 2.0.0**.

- **Bump ruby_task_helper upper bound to < 2.0.0** ([#16](https://github.com/puppetlabs/puppetlabs-azure_inventory/pull/16))

---

### cd4peadm 5.15.1

📅 Latest release: 2026-05-07 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4peadm))

A few highlights from this release:
- Fixed an issue where SAML logins were failing.
- Fixed an issue where CD would not use the configured HTTP timeouts when making calls to the Azure DevOps API, resulting in unexpected timeout failures.
- Fixed an issue where GitLab merge request updates that do not involve code changes would trigger CD pipelines.
- **CVE-2026-42198.** Updated to address this vulnerability.

Check the official [release notes for cd4peadm 5.15.1](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm#Version5151) for the full details.

---

### concat 10.0.0

📅 Latest release: 2026-05-19 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/concat))

This release added support for CentOS 9 while also addressing runner images for Ubuntu 24.04.

- Redact sensitive content [#828](https://github.com/puppetlabs/puppetlabs-concat/pull/828) ([smortex](https://github.com/smortex))
- (CAT-2296) Update github runner image to ubuntu-24.04 [#823](https://github.com/puppetlabs/puppetlabs-concat/pull/823) ([shubhamshinde360](https://github.com/shubhamshinde360))
- (CAT-2152) Add support for CentOS 9 [#818](https://github.com/puppetlabs/puppetlabs-concat/pull/818) ([skyamgarp](https://github.com/skyamgarp))
- Allow user defined tag or list of tags [#790](https://github.com/puppetlabs/puppetlabs-concat/pull/790) ([Lightning-](https://github.com/Lightning-))
- Use explicit hash value syntax instead of shorthand [#835](https://github.com/puppetlabs/puppetlabs-concat/pull/835) ([SugatD](https://github.com/SugatD))

---

### gcloud_inventory 0.3.1

📅 Latest release: 2026-05-14 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/gcloud_inventory))

This release bumped the ruby_task_helper upper bound to **< 2.0.0**.

- **Bump ruby_task_helper upper bound to < 2.0.0** ([#14](https://github.com/puppetlabs/puppetlabs-gcloud_inventory/pull/14))

---

### http_request 0.3.2

📅 Latest release: 2026-05-14 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/http_request))

This release bumped the ruby_task_helper upper bound to **< 2.0.0**.

- **Bump ruby_task_helper upper bound to < 2.0.0** ([#18](https://github.com/puppetlabs/puppetlabs-http_request/pull/18))

---

### inifile 6.4.0

📅 Latest release: 2026-05-19 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/inifile))

The inifile module now supports multiple values per key while also adding support for CentOS 9.

- Add support for multiple values per key [#555](https://github.com/puppetlabs/puppetlabs-inifile/pull/555) ([bwitt](https://github.com/bwitt))
- (CAT-2152) Add support for CentOS 9 [#549](https://github.com/puppetlabs/puppetlabs-inifile/pull/549) ([skyamgarp](https://github.com/skyamgarp))

---

### puppet_agent 4.28.0

📅 Latest release: 2026-05-07 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_agent))

Updates to new tooling (Bolt, PDK Templates) as well as support for MacOS 26 and some pre-work for the upcoming Puppet Core 9.

- (PA-7824) Use newest Bolt [#829](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/829) ([mhashizume](https://github.com/mhashizume))
- (PA-7897) Update to pdk-templates 3.6.1.1 [#825](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/825) ([joshcooper](https://github.com/joshcooper))
- (PA-8250) Allow installation of puppetcore9-nightly packages [#822](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/822) ([joshcooper](https://github.com/joshcooper))
- (PA-8238) Add support for MacOS 26 in install_shell.sh [#821](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/821) ([shubhamshinde360](https://github.com/shubhamshinde360))
- (PA-8250) Restore windows command to check puppet service [#826](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/826) ([joshcooper](https://github.com/joshcooper))
- (PA-8041) Fix puppetcore8-nightly installs on rpm and mac [#824](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/824) ([joshcooper](https://github.com/joshcooper))
- (PA-8247) Add guard against other ruby process when installing [#823](https://github.com/puppetlabs/puppetlabs-puppet_agent/pull/823) ([AriaXLi](https://github.com/AriaXLi))

---

### terraform 0.7.2

📅 Latest release: 2026-05-14 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/terraform))

This release bumped the ruby_task_helper upper bound to **< 2.0.0**.

- **Bump ruby_task_helper upper bound to < 2.0.0** ([#37](https://github.com/puppetlabs/puppetlabs-terraform/pull/37))

---

### vault 0.4.1

📅 Latest release: 2026-05-14 (🌐 [View on the Forge](https://forge.puppet.com/modules/puppetlabs/vault))

This release bumped the ruby_task_helper upper bound to **< 2.0.0**.

- **Bump ruby_task_helper upper bound to < 2.0.0** ([#19](https://github.com/puppetlabs/puppetlabs-vault/pull/19))

## Until Next Time!

That closes out the May 2026 update set. For deeper implementation detail, the linked module pages and release notes remain the best source of truth.

If you have feedback on the roundup format or want a deeper look at a specific module area, the Perforce Community Slack is still the best place to continue the conversation.

See you next month with a roundup for June releases!
