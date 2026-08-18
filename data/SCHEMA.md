# Data Schema for Roundup Automation

## Overview

This directory contains intermediate data files used in the roundup generation pipeline:

1. **Module Discovery**: `{month}_{year}_modules_discovered.json` - Raw list of all puppetlabs modules from Forge listing, filtered for the target month.
2. **Release Notes**: `{month}_{year}_release_notes_raw.json` - Raw parsed bullets from Forge changelogs and external docs.
3. **Highlights Candidates**: `{month}_{year}_highlights_candidates.yaml` - Auto-detected themes and candidates for "Highlighted Updates" section (curator curates this).
4. **Final Output**: `posts/{year}-{month_num:02d} {Month_Name} {Year} Puppetlabs Modules Roundup.md` - Generated markdown post.

---

## 1. Module Discovery Schema

**File**: `march_2026_modules_discovered.json`

```json
{
  "metadata": {
    "target_month": "March",
    "target_year": 2026,
    "discovered_at": "2026-03-30T18:00:00Z",
    "query_url": "https://forge.puppet.com/modules/puppetlabs?limit=50&sort_by=latest_release&module_groups=base%20pe_only"
  },
  "modules": [
    {
      "name": "docker",
      "slug": "puppetlabs/docker",
      "forge_url": "https://forge.puppet.com/modules/puppetlabs/docker",
      "latest_version": "10.4.0",
      "release_date": "2026-02-10",
      "released_in_target_month": false,
      "release_notes_source": "forge_changelog",
      "changelog_url": "https://forge.puppet.com/modules/puppetlabs/docker/changelog"
    },
    {
      "name": "peadm",
      "slug": "puppetlabs/peadm",
      "forge_url": "https://forge.puppet.com/modules/puppetlabs/peadm",
      "latest_version": "3.36.0",
      "release_date": "2026-03-15",
      "released_in_target_month": true,
      "release_notes_source": "forge_changelog",
      "changelog_url": "https://forge.puppet.com/modules/puppetlabs/peadm/changelog"
    },
    {
      "name": "sce_linux",
      "slug": "puppetlabs/sce_linux",
      "forge_url": "https://forge.puppet.com/modules/puppetlabs/sce_linux",
      "latest_version": "2.6.0",
      "release_date": "2026-03-20",
      "released_in_target_month": true,
      "release_notes_source": "external_docs",
      "release_notes_url": "https://help.puppet.com/sce/current/linux/scel_relnotes_260.htm",
      "changelog_url": "https://forge.puppet.com/modules/puppetlabs/sce_linux/changelog"
    }
  ]
}
```

**Key Fields**:
- `latest_version`, `release_date`: From Forge listing
- `released_in_target_month`: Boolean, parsed from release_date
- `release_notes_source`: Type from `config/release_notes_sources.yaml`
- `release_notes_url`: Constructed if external_docs, else null
- `recovered_from_overshoot`: `true` if this entry was recovered because the module's
  current release postdates the target month but an earlier release that month was
  found by checking full release history (see `recover_overshot_releases()` in
  `scripts/01_discover_modules.py`). Absent/false for normally-discovered modules.

---

## 2. Release Notes Schema

**File**: `march_2026_release_notes_raw.json`

```json
{
  "metadata": {
    "target_month": "March",
    "target_year": 2026,
    "fetched_at": "2026-03-30T19:00:00Z"
  },
  "modules": {
    "docker": {
      "version": "10.4.0",
      "release_date": "2026-02-10",
      "released_in_target_month": false,
      "source": "forge_changelog",
      "source_url": "https://forge.puppet.com/modules/puppetlabs/docker/changelog",
      "raw_html_snapshot": "data/raw_html/docker_10.4.0.html",
      "parsed_bullets": []
    },
    "peadm": {
      "version": "3.36.0",
      "release_date": "2026-03-15",
      "released_in_target_month": true,
      "source": "forge_changelog",
      "source_url": "https://forge.puppet.com/modules/puppetlabs/peadm/changelog",
      "raw_html_snapshot": "data/raw_html/peadm_3.36.0.html",
      "parsed_bullets": [
        "Added support for Puppet Enterprise 2025.9",
        "Fixed timeout issues in cluster conversion",
        "Improved node group environment assignment"
      ]
    },
    "sce_linux": {
      "version": "2.6.0",
      "release_date": "2026-03-20",
      "released_in_target_month": true,
      "source": "external_docs",
      "source_url": "https://help.puppet.com/sce/current/linux/scel_relnotes_260.htm",
      "raw_html_snapshot": "data/raw_html/sce_linux_2.6.0.html",
      "parsed_bullets": [
        "Added support for Rocky Linux 9 CIS Benchmarks",
        "Fixed AIDE file verification issues",
        "Updated CIS benchmark definitions"
      ]
    }
  }
}
```

**Key Pattern**:
- Only include modules where `released_in_target_month == true`
- `parsed_bullets`: List of 1-5 key changes extracted from changelog/docs
- `raw_html_snapshot`: Path to archived HTML for reproducibility

---

## 3. Highlights Candidates Schema

**File**: `march_2026_highlights_candidates.yaml`

```yaml
# Auto-detected themes and highlights for curator review
# Delete rows you don't want in final post; keep ones that matter

themes:
  - title: "Puppet 7 Support Removed Across Multiple Modules"
    summary: "With Puppet 7 now reaching end-of-life, several modules have deprecated Puppet 7 support."
    modules:
      - docker
      - firewall
      - inifile
      - sqlserver
    frequency: 4
    candidate_reason: "Repeated pattern across 4+ modules"
    
  - title: "Ruby Version Standardization to 3.1"
    summary: "Modules standardizing on Ruby 3.1, dropping support for older versions."
    modules:
      - docker
      - firewall
      - inifile
    frequency: 3
    candidate_reason: "Appears in 3+ module updates"

breaking_changes:
  - module: peadm
    version: "3.36.0"
    bullet: "BREAKING: Cluster conversion now requires minimum PE 2023.8.x"
    severity: "high"
    
major_features:
  - module: sce_linux
    version: "2.6.0"
    bullet: "Added support for CIS Benchmarks for Rocky Linux 9"
    importance: "high"
    
  - module: sqlserver
    version: "5.1.0"
    bullet: "Support added for SQL Server 2025"
    importance: "high"

security_updates:
  - module: pwshlib
    version: "2.0.1"
    bullet: "Fixed per-property change event reporting in PE when using DSC resources with custom_insync"
    cves: []

single_important_updates:
  - module: docker
    version: "10.4.0"
    bullet: "Now uses puppetlabs-apt for modern APT keyrings on Debian family"
    reason: "Improves compatibility with latest Debian distributions"
```

**Curator's role**: Open this file, delete themes/updates that aren't important, keep the ones that make the roundup. This becomes the source for the "Highlighted Updates" section.

---

## 4. File Naming Convention

All data files follow this pattern for easy tracking:

```
{month_name_lower}_{year}_modules_discovered.json
{month_name_lower}_{year}_release_notes_raw.json
{month_name_lower}_{year}_highlights_candidates.yaml
```

Examples:
- `march_2026_modules_discovered.json`
- `march_2026_release_notes_raw.json`
- `march_2026_highlights_candidates.yaml`

---

## 5. Raw HTML Snapshots

Stored in `data/raw_html/{module}_{version}.html` for audit trail and reproducibility.

Each snapshot is a gzipped archive of the exact HTML fetched, so if a changelog URL changes or docs are updated, you can still reference what was actually parsed.

---

## 6. Module Releases Report Schema

**File**: `data/module_releases_report_{start:%Y%m%d}_{end:%Y%m%d}.csv` (e.g.
`module_releases_report_20260101_20260817.csv`), produced by
`scripts/report_module_releases.py` — a standalone tool, not one of the four pipeline stages
above. See [MODULE_RELEASES_REPORT_SPEC.md](../MODULE_RELEASES_REPORT_SPEC.md) for the full
design.

One row per release (not per module — a module with 3 releases in the date range gets 3 rows),
sorted by `publisher`, then `release_date` ascending, then `module_name`, then `version`
descending:

| Column | Type | Meaning |
|---|---|---|
| `publisher` | string | Raw Forge owner slug, e.g. `puppetlabs`, `puppet` (Vox Pupuli), or an individual maintainer's own username. Only populated with a value other than `puppetlabs` when run with `--all-publishers`. |
| `module_name` | string | e.g. `stdlib` |
| `version` | string | e.g. `10.0.2` |
| `release_date` | `YYYY-MM-DD` | **UTC** date of the release, matching the convention already used elsewhere in this pipeline (and what's published in `posts/`) |
| `num_changes` | int or blank | top-level changelog bullets found for this version |
| `num_community_contributions` | int or blank | subset of those bullets credited to a handle listed under `community` in `config/internal_contributors.yaml`. Only ever computed for `puppetlabs` rows — see below. |
| `num_unknown_contributions` | int or blank | subset credited to a handle in **neither** list — a to-do counter meaning `config/internal_contributors.yaml` needs updating, not a contribution type. Only ever computed for `puppetlabs` rows — see below. |

**Blank vs. `0` is meaningful, not incidental:**

- **Blank** = not knowable from the available source: no changelog section matched this
  release's version at all (`num_changes` only), or this module's release notes carry no
  GitHub attribution structure to count (`num_community_contributions` /
  `num_unknown_contributions`, for modules whose release notes are prose docs on
  help.puppet.com rather than a GitHub-hosted changelog) — **or**, in `--all-publishers` mode,
  the release's `publisher` simply isn't `puppetlabs`. The two contribution columns are never
  computed for other publishers: `config/internal_contributors.yaml` is curated against
  Puppet/Perforce staff and doesn't generalize to other publishers' contributors, and resolving
  attribution for the whole Forge catalog's changelog bullets would need far more live GitHub
  lookups than the unauthenticated 60/hour limit allows.
- **`0`** = knowable and genuinely zero — a changelog section was found and parsed
  successfully; it simply had no bullets, or no community/unknown-credited bullets.

The columns do not necessarily sum to `num_changes`: a bullet with no PR reference at all (a
pure-maintenance change with nobody to credit) counts toward `num_changes` only, not either
contribution column. The remainder after subtracting community + unknown from `num_changes` is
internal-authored changes plus unattributed ones.

Deleted/withdrawn releases (Forge's `deleted_at` set) are excluded entirely, never rowed.

**`--all-publishers`** drops the `owner=puppetlabs` filter on the Forge API query and pages the
entire catalog (~1,500 modules as of 2026-08) instead of just the ~108 puppetlabs modules. Use
it to compare puppetlabs against Vox Pupuli (`puppet`) or the rest of the Forge; the run
summary buckets rows into `puppetlabs` / `puppet (Vox Pupuli)` / `other` for a quick read, but
the CSV itself always carries the raw per-row `publisher` slug.
