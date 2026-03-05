# Puppetlabs Modules Roundup – July to November 2025

**Tags:** #puppet

## Welcome to the first edition of the Puppetlabs Modules Roundup!
Usually, the product lines like Puppet Core and Puppet Enterprise get all the attention in the release notes, but this series is all about keeping you in the loop on what’s new and updated in the Perforce Puppet official module ecosystem. My goal is to publish a quick roundup every month (or maybe every few months) highlighting the modules that received updates during that period.

### What is covered?
For this inaugural post, we’re looking back at the **last six months** to catch you up on everything from **July 2025** through to the end of **November 2025**. That does mean that this is a bit of a MONSTER of an update, but I’ll try to keep incrementally updating so that we can keep it to a more reasonable size going forward. They won’t all be this huge!

Whether you are just getting started with Puppet, or managing a long-lived solution with thousands of nodes, or just curious about what has changed in the module ecosystem, this is the place to find out what’s new!

## Highlighted Updates

### Two new premium modules released!
As part of the Puppet Edge launch, two new premium modules were released to help support working with network devices.

* **[edgeops](https://forge.puppet.com/modules/puppetlabs/edgeops/readme)** allows you to create tasks that can work directly against network devices. This first version supports NETCONF as a protocol.

* **[playbook_runner](https://forge.puppet.com/modules/puppetlabs/playbook_runner/readme)** provides the capability to run YAML-based automation playbooks directly from Puppet tools like tasks, plans, and workflows.

### EOL Puppet 7.x support dropped in new versions of some modules
With Puppet 7 [reaching EOL in April 2025](https://help.puppet.com/core/current/Content/PuppetCore/platform_lifecycle.htm), several modules were updated in the last few quarters to now only support Puppet 8.x going forward. You will need to upgrade to version 8.x to use new versions of these modules. See notes for:

* apache

* apt

* augeas_core

* cron_core

* dsc_lite

* exec

* host_core

* mount_core

* ntp

* selinux_core

* sshkeys_core

* yumrepo_core

* zfs_core

* zone_core

### Ubuntu 24.04 support improved across some modules 
Modules have been updated to have better testing and support of Ubuntu 24.0.4. For some modules, this meant updating tests or GitHub runners, others had fixes applied. See the notes for these modules:

* accounts

* apache

* cd4peadm

* chocolatey

* exec

* java

* mysql

* ntp

* postgresql

* powershell

* puppet_data_connector

### Resolved vulnerabilities in modules
While Puppet Core and Puppet Enterprise have received numerous CVE resolutions, the following modules have also resolved specific reported vulnerabilities:

* cd4peadm: CVE-2025-4949

* peadm: CVE-2024-49761

* complyadm: CVE-2025-23419, CVE-2025-3501, CVE-2025-1094

## What’s New in Puppetlabs Modules?

The following is an alphabetical listing of modules which received updates since July 2025. Some of these modules had multiple versions released and are called out individually in the notes for the module.

---

### accounts 8.3.1

📅 ***Latest release:*** 2025-07-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/accounts/readme))

The accounts module received an iterative update which contains fixes to synchronize user defined resources with the corresponding type. Also included were some changes to update the GitHub runner image to Ubuntu 24.04.  

---

### apache 13.1.0 
📅 ***Latest release:*** 2025-11-18 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/apache/readme) )

The latest updates for the apache module introduce Debian 13 support and dropped support for Puppet 7, along with some other improvements:

* Added Debian 13 support

* Removed support for Puppet 7

* Removed apache::mod::info as default module for FreeBSD

* GitHub runner image moved to Ubuntu 24.04  

---

### apt 11.1.0

📅 ***Latest release:*** 2025-09-22 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/apt/readme))

In the last two quarters, versions 11.0.0 and 11.1.0 have been released which remove the support for Puppet 7 along with some more fixes to address customer requests:

* Removed support for Puppet 7

* Updates to support latest PDK and baseline needs for Puppet Core

* Resources added for auth.conf.d

* Fixes for list_keyring path generation with dir and key filenames

* Fixes for supporting Suites with a path and deb822 sources

* Replaced apt with apt-cache when using grep

---

### augeas_core 2.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/augeas_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 2.0.x versions, Puppet 7.x is no longer supported.

* Amazonflips added as a supported platform

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropped beaker-puppet_install_helper gem

* Added beaker-hostgenerator gem with dynamic version support

* Litmus has been removed from the Gem file  

---

### cd4pe_jobs 1.7.3

📅 ***Latest release:*** 2025-11-07 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4pe_jobs/readme))

A few releases made in the last few quarters (1.7.2 and 1.7.3).  These releases added logging for when image pulls fail and new description text to make it clear the module’s main task is not expected to be run directly by users.  

---

### cd4peadm 5.13.0

📅 ***Latest release:*** 2025-11-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/cd4peadm/readme))

Several releases made in the last few quarters (5.10.x, 5.11.x, 5.12.x, and 5.13.x).  Some highlights:

* Puppet 8 support added for puppet-dev-tools

* New Hiera settings for base hostname, job callback endpoint, and other general configuration improvements

* Improved air-gapped installation with a bundled puppet-dev-tools image tarball that can be downloaded from the local system

* Ubuntu 24.04 support added (requires Bolt 5.0.0 or later)

* Updated license_check plan to aid with troubleshooting license issues

* Removed podman-plugins package as requirement for installation

* Updated JGit to address CVE-2025-4949

Full details can for Continuous Delivery can be found in [the release notes](https://help.puppet.com/cdpe/current/Content/UserGuide/CDPE/ReleaseNotes/cd_release_notes.htm).  

---

### chocolatey 8.0.3

📅 ***Latest release:*** 2025-08-13 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/chocolatey/readme))

This incremental release updated the github runner image to Ubuntu 24.04 and added support for a newer ruby_task_helper (with related fixes).  

---

### comply 3.5.0

📅 ***Latest release:*** 2025-07-11 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/complyadm/readme))

---

### complyadm 3.5.0

📅 ***Latest release:*** 2025-07-11 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/complyadm/readme))

This update to the security compliance module adds in updates to several components such as nginx and postgres and assessor, along with improvements to upgrade flows and overall application updates. The component updates addressed several CVEs:

* CVE-2025-23419. Updated NGINX to 1.28.0 to address this vulnerability.
* CVE-2025-3501. Updated Keycloak to 26.2.5 to address this vulnerability.
* CVE-2025-1094. Updated PostgreSQL to 17.5.0 to address this vulnerability.

Release notes for Security Compliance Management 3.5.0 can be found on the [official release notes](https://help.puppet.com/scm/current/Content/UserGuide/SCM/Release_notes/release_notes.htm).

---

### cron_core 2.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/cron_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 2.0.x versions, Puppet 7.x is no longer supported.

* Amazonflips added as a supported platform

* Fixed idempotency for empty environments

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropped beaker-puppet_install_helper gem

* Added beaker-hostgenerator gem with dynamic version support

* Litmus has been removed from the Gem file  

---

### dsc_lite 5.0.0

📅 ***Latest release:*** 2025-11-04 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/dsc_lite/readme))

The new 5.x release removed support for Puppet 7, paving the way for better Puppet Core support in the module. Fixes were also added to correct deferred resource resolution in DSC and also address pwshlib dependency errors.

---

### edgeops 1.0.0

🌟 ***New Release:*** 2025-11-23 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/edgeops/readme))

This new premium module was released as part of the new Puppet Edge, supporting operations against network devices. In this initial version, the edgeops module focuses on NETCONF communication with network devices.  

---

### exec 4.0.0

📅 ***Latest release:*** 2025-09-01 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/exec/readme))

The new major version of this module contains mostly focuses on OS and version support:

* Now only supports 8.x. As of the 4.0.x versions, Puppet 7.x is no longer supported.

* Better support for Puppet Core going forward

* Support added for powershell CLI in exec::windows

* Github runner image updated to Ubuntu 24.04  

---

### firewall 8.2.0

📅 ***Latest release:*** 2025-08-11 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/firewall/readme))

This latest release resolves an issue where stderr and stdout were combined when scanning rules. This release disables the combination of stdout and stderr when parsing iptables rules.  

---

### host_core 2.0.1

📅 ***Latest release:*** 2025-11-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/host_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 2.0.x versions, Puppet 7.x is no longer supported.

* Amazonflips added as a supported platform

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropped beaker-puppet_install_helper gem

* Added beaker-hostgenerator gem with dynamic version support

* Litmus has been removed from the Gem file  

---

### iis 10.1.6

📅 ***Latest release:*** 2025-08-25 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/iis/readme))

This new incremental release adds redacting of password values in logs. The provider spec is also updated to correctly stub run and return a result hash, preventing NoMethodError during testing.  

---

### java 11.2.0

📅 ***Latest release:*** 2025-07-18 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/java/readme))

This module release now supports puppet/archive v8, along with updated GitHub runners on Ubuntu 24.04.  

---

### mount_core 2.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/mount_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 2.0.x versions, Puppet 7.x is no longer supported.

* Amazonflips added as a supported platform

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropped beaker-puppet_install_helper gem

* Added beaker-hostgenerator gem with dynamic version support

* Litmus has been removed from the Gem file  

---

### mysql 16.3.0

📅 ***Latest release:*** 2025-07-30 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/mysql/readme))

In this release, support was added for Mariadb 11.x along with some component and image updates:

* Support for Mariadb 11.x added

* Ruby upgraded from 2.7 to 3.1

* Update GitHub runner image to Ubuntu 24.04

* Fixes to support acceptance testing against SLES 15

---

### ntp 11.1.0

📅 ***Latest release:*** 2025-08-11 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/ntp/readme))

The latest release of the ntp module dropped Puppet 7 support, and also added Ubuntu 24.04 support, along with updating the GitHub runner image to Ubuntu 24.04.  

---

### pe_event_forwarding 2.2.0

📅 ***Latest release:*** 2025-07-24 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/pe_event_forwarding/readme))

For this release, a fix was released so that in the event the first collection run fails, subsequent runs are treated as the first until event counts are successfully saved to the index. In addition, GitHub integration tests have been updated to latest Ubuntu and Ruby 3.1  

---

### peadm 3.33.0

📅 ***Latest release:*** 2025-10-06 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/peadm/readme))

The peadm module has received several releases over the last few quarters (3.31, 3.32, and 3.33). Primarily, these updates address supporting new releases of Bolt and Puppet Enterprise. Here are some of the changes made in the module:

* REXML gem update to address CVE-2024-49761

* Added support for Puppet Enterprise 2023.8.5, 2023.8.6, 2025.5.0, and 2025.6.0

* Added support for Bolt v5  

---

### playbook_runner 1.1.0

🌟 ***New Release:*** 2025-11-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/playbook_runner/readme))

This new premium module was released as part of the new Puppet Edge, providing the ability to run YAML-based automation playbooks through Puppet tasks, plans, and workflows.  

---

### postgresql 10.6.0

📅 ***Latest release:*** 2025-10-13 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/postgresql))

The new release of the postgresql module addresses OS support and other fixes:

* Support added for Debian 13 (Trixie)

* Role now supports a valid_until parameter

* Version requirements updated to allow puppetlabs/apt 11.x and puppet/system 9.x

* Fixes Debian 11 tests and adds tests for Debian 12 and Debian 13.

* Debian dependency issues with custom encoding resolved.

* Github Runner Image updated to Ubuntu 24.0.4  

---

### powershell 6.1.0

📅 ***Latest release:*** 2025-11-19 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/powershell/readme))

Updates made to support latest versions of Puppet Core, PDK, and pwshlib. The GitHub runner image has also been updated to Ubuntu 24.04.  

---

### puppet_agent 4.26.0

📅 ***Latest release:*** 2025-10-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_agent/readme))

In the last two quarters, versions 4.25.0 and 4.26.0 were released to the Forge, with a general theme of better OS version support:

* Puppet Core support for Mac OS

* Updated task_spec to upgrade to Puppet 8 using artifactory to support Puppet Core installation updates

* Task acceptance tests updated for RedHat 10 (x86_64)

---

### puppet_data_connector 4.26.0

📅 ***Latest release:*** 2025-10-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/puppet_agent/readme))

The premium module in this release was renamed as the Observability Data Connector and updated to address several maintenance issues. Rubocop and lint issues have been addressed, as well as updated image links in the README file.  
New systems in metadata have also been updated:

* puppet/system v8

* AlmaLinux 7 dropped, AlmaLinux 9 added

* AmazonLinux 2023 added

* OracleLinux 7 dropped

* RedHat 7 dropped

* Ubuntu 18.04 dropped and Ubuntu 24.04 added

---

### sce_linux 2.5.0

📅 ***Latest release:*** 2025-10-28 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/sce_linux/changelog))

The release notes for this premium module are available on the official documentation site: [https://help.puppet.com/sce/current/linux/scel_relnotes.htm](https://help.puppet.com/sce/current/linux/scel_relnotes.htm)

Highlights include:

* Updated CIS Benchmarks

* File verification with AIDE issues resolved  

---

### scheduled_task 4.0.3

📅 ***Latest release:*** 2025-07-16 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/scheduled_task/readme))

Delay properties have been added to scheduled task triggers. In addition, Rubocop offenses and failing rspecs have been fixed and additional schedule options have been added to the REFERENCE markdown file.  

---

### selinux_core 2.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/selinux_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 2.0.x versions, Puppet 7.x is no longer supported.

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing  

---

### sshkeys_core 3.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/sshkeys_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 3.0.x versions, Puppet 7.x is no longer supported.

* Amazonflips was added as a supported platform

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropping beaker-puppet_install_helper gem  

---

### wsus_client 6.2.0

📅 ***Latest release:*** 2025-08-05 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/wsus_client/readme))

The 6.2.0 release is a rollup of many community improvements to update facts, fix broken URLs, update PDK support, and other small changes.

Of note, support for ‘option 7’ for auto_update_option is now available to notify for a restart in Windows Server 2016 and later.  

---

### yumrepo_core 3.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/yumrepo_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 3.0.x versions, Puppet 7.x is no longer supported.

* Amazonflips added as a supported platform

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropped beaker-puppet_install_helper gem

* Added beaker-hostgenerator gem with dynamic version support

* Litmus has been removed from the Gem file  

---

### zfs_core 2.0.1

📅 ***Latest release:*** 2025-11-26 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/zfs_core/readme))

Earlier this year, in July, version 1.6.x was released which introduced realtime support and support for nvme devices.  
The 2.0.x release in November contains:

* Now only supports Puppet 8.x. As of this version, Puppet 7.x is no longer supported.

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Litmus was removed from the Gemfile

* Dropping beaker-puppet_install_helper gem in the zfs-core module  

---

### zone_core 2.0.0

📅 ***Latest release:*** 2025-11-25 ([🌐 View on the Forge](https://forge.puppet.com/modules/puppetlabs/zone_core/readme))

Features several changes for better testing and supporting 8.x going forward:

* Now only supports Puppet 8.x. As of the 2.0.x versions, Puppet 7.x is no longer supported.

* Updates for PDK template 3.5.1

* Better support for Puppet Core testing

* Dropped beaker-puppet_install_helper gem

* Litmus has been removed from the Gem file

---

## Until Next Time!

That’s a wrap for this first roundup! If you want to dive deeper into any of these modules, check out their documentation [on the Forge](https://forge.puppet.com) or explore the individual module repos on GitHub for more details.

Got feedback or ideas for future updates? We’d love to hear from you! Add a comment here or join the conversation in the [Perforce Community Slack](https://slack.puppet.com/).

Catch you at the next roundup in January!
