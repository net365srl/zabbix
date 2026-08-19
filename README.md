# Zabbix Templates for Smart‑Managed Switches & SASE

![Zabbix](https://img.shields.io/badge/Zabbix-7.4-CC0000?logo=zabbix&logoColor=white) ![SNMP](https://img.shields.io/badge/SNMP-v2c%20%7C%20v3-0A66C2) ![API](https://img.shields.io/badge/Cato%20API-GraphQL-blueviolet) ![Format](https://img.shields.io/badge/format-YAML-1A7C11) ![Templates](https://img.shields.io/badge/templates-3-2774A4) ![License](https://img.shields.io/badge/license-MIT-blue) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen) ![Maintained](https://img.shields.io/badge/maintained-yes-success)
![Platform](https://img.shields.io/badge/platform-network%20switches%20%7C%20SASE-555555) ![Vendors](https://img.shields.io/badge/vendors-HPE%20%7C%20Netgear%20%7C%20Cato-orange) ![Monitoring](https://img.shields.io/badge/monitoring-SNMP%20%7C%20HTTP-9cf) ![Discovery](https://img.shields.io/badge/LLD-interfaces%20%7C%20sites-blueviolet) ![Dashboard](https://img.shields.io/badge/dashboard-Full%20HD-ff69b4)
[![CI](https://github.com/net365srl/zabbix/actions/workflows/validate.yml/badge.svg)](https://github.com/net365srl/zabbix/actions/workflows/validate.yml) [![Stars](https://img.shields.io/github/stars/net365srl/zabbix?style=social)](https://github.com/net365srl/zabbix/stargazers) [![Forks](https://img.shields.io/github/forks/net365srl/zabbix?style=social)](https://github.com/net365srl/zabbix/network/members)
[![License](https://img.shields.io/github/license/net365srl/zabbix)](./LICENSE) [![Issues](https://img.shields.io/github/issues/net365srl/zabbix)](https://github.com/net365srl/zabbix/issues) [![Pull Requests](https://img.shields.io/github/issues-pr/net365srl/zabbix)](https://github.com/net365srl/zabbix/pulls) [![Last Commit](https://img.shields.io/github/last-commit/net365srl/zabbix)](https://github.com/net365srl/zabbix/commits/main) [![Repo Size](https://img.shields.io/github/repo-size/net365srl/zabbix)](https://github.com/net365srl/zabbix) [![Contributors](https://img.shields.io/github/contributors/net365srl/zabbix)](https://github.com/net365srl/zabbix/graphs/contributors)

A collection of **community Zabbix 7.4 templates** to monitor **smart‑managed switches over SNMP** and **Cato Networks SASE accounts over the Cato GraphQL API (HTTP)**. Each SNMP template ships with vendor‑aware items, low‑level discovery (LLD) of network interfaces, ready‑to‑use triggers, per‑interface graphs and a Full‑HD overview dashboard. All SNMP OIDs are **numeric**, so no external MIB files need to be loaded into Zabbix. The Cato template uses the **HTTP agent** with GraphQL and discovers **sites, WAN links and Sockets** automatically.

---

## Table of Contents

1. [Available Templates](#available-templates)
2. [Feature Matrix](#feature-matrix)
3. [Quick Start](#quick-start)
4. [Repository Structure](#repository-structure)
5. [Common Design Choices](#common-design-choices)
6. [Compatibility](#compatibility)
7. [Contributing](#contributing)
8. [Trademarks & Disclaimer](#trademarks--disclaimer)
9. [License](#license)

---

## Available Templates

| Template | Vendor / OS | Model(s) | Transport | Docs | File |
|----------|-------------|----------|-----------|------|------|
| **HPE Instant On 1930 by SNMP** | HPE / Aruba – RADLAN "Smart Managed" | Instant On 1930 series (8/24/48‑port, PoE & non‑PoE) | SNMP | [README](./hpe-instanton-1930/README.md) | [`hpe_instanton_1930_snmp_zabbix74.yaml`](./hpe-instanton-1930/hpe_instanton_1930_snmp_zabbix74.yaml) |
| **Netgear GS748Tv5 by SNMP** | Netgear – FastPath / Broadcom | GS748Tv5 (+ many FastPath GSxxxT models) | SNMP | [README](./netgear-gs748tv5/README.md) | [`netgear_gs748tv5_snmp_zabbix74.yaml`](./netgear-gs748tv5/netgear_gs748tv5_snmp_zabbix74.yaml) |
| **Cato Networks by HTTP** | Cato Networks – SASE (GraphQL API) | Any Cato account (multi‑site) | HTTP / GraphQL | [README](./Cato%20Networks/README.md) · [INSTALL](./Cato%20Networks/INSTALL.md) | [`template_cato_networks_http.yaml`](./Cato%20Networks/template_cato_networks_http.yaml) |

## Feature Matrix

### SNMP switch templates

| Capability | HPE Instant On 1930 | Netgear GS748Tv5 |
|------------|:-------------------:|:----------------:|
| System info (SNMPv2‑MIB) | ✅ | ✅ |
| Inventory (model/serial/versions) | ⚠️ partial (HW/boot version, MAC) | ✅ full |
| CPU utilization | ✅ | ✅ |
| **Memory utilization** | ❌ *(not exposed by firmware)* | ✅ |
| Hardware health sensor | ✅ (aggregate) | ❌ |
| Interface discovery (LLD) | ✅ | ✅ |
| 64‑bit traffic counters | ✅ | ✅ |
| Errors / discards per port | ✅ | ✅ |
| Total switch throughput | ✅ | ✅ |
| Per‑interface graphs | ✅ | ✅ |
| Overview dashboard | ✅ | ✅ |
| **Link‑down alert** | edge‑triggered · **High** | edge‑triggered · **Information** |
| PoE monitoring | ❌ | ❌ (non‑PoE model) |

> **Legend:** ✅ supported · ⚠️ partial · ❌ not available. See each template's README for the exact OIDs, thresholds and limitations.

### Cato Networks (SASE) template

| Capability | Cato Networks by HTTP | Default |
|------------|:---------------------:|:-------:|
| Site availability (connected / operational status, PoP, host count) | ✅ | on |
| Socket / HA (connectivity, HA role, uptime, firmware change) | ✅ | on |
| Network quality **per link, per site** (throughput, loss, jitter, RTT, discards) | ✅ | on |
| Multi‑site discovery (LLD of sites, WAN links, Sockets) | ✅ | on |
| Inventory & drift (configured vs. live sites) | ✅ | on |
| Event volume trending (eventsFeed) | ✅ | on¹ |
| SLA (rolling 24h / 7d / 30d availability) | ✅ | on |
| Dynamic routing (BGP: peer state, routes, uptime) | ✅ | **off**² |
| Multi‑page dashboard (Overview, Quality per‑site, Sites & Sockets, BGP, SLA) | ✅ | on |
| "API errors" sentinel per master item | ✅ | on |

> ¹ Requires **Event Feed** enabled in the Cato Management Application. ² **Disabled by default** — the BGP status field is not part of the stable/universal Cato schema; enable it after verifying the query for your account (see the [Cato README](./Cato%20Networks/README.md)).

## Quick Start

### SNMP switches

1. In Zabbix, go to **Data collection → Templates → Import**.
2. Select the `*.yaml` file of the switch you want to monitor and keep **Create new** checked.
3. Open the target host (**Data collection → Hosts**) and add an **SNMP interface** (UDP/161).
4. On the **Templates** tab, link the imported template.
5. On the **Macros** tab, set **`{$SNMP.COMMUNITY}`** (default `public`) and adjust thresholds if needed.
6. Wait for the interface discovery to run, then open **Monitoring → Hosts → Dashboards**.

For **SNMPv3**, switch the host SNMP interface to v3 and fill in the standard security fields — the templates do not hard‑code any credentials.

### Cato Networks (SASE)

1. In Zabbix, go to **Data collection → Templates → Import** and select [`template_cato_networks_http.yaml`](./Cato%20Networks/template_cato_networks_http.yaml).
2. Create a host (e.g. `Cato Account - ACME`), **no SNMP interface needed** (the HTTP agent connects out to the Cato API).
3. Link the **Cato Networks by HTTP** template.
4. On the **Macros** tab set **`{$CATO.API.KEY}`** (Secret text) and **`{$CATO.ACCOUNT.ID}`**; set `{$CATO.API.URL}` only if your CMA uses a regional endpoint.
5. Wait a couple of polling cycles, then open the **Cato Networks - Overview** dashboard.

👉 Full walkthrough (read‑only API key via a Service Principal, permission matrix, regional endpoints, enabling BGP) in the [**Cato Networks INSTALL guide**](./Cato%20Networks/INSTALL.md).

## Repository Structure

```
.
├── README.md                       ← this file
├── LICENSE
├── CONTRIBUTING.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── new_device_request.yml
│   │   └── config.yml
│   ├── workflows/
│   │   └── validate.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── scripts/
│   └── validate_templates.py
├── hpe-instanton-1930/
│   ├── README.md
│   └── hpe_instanton_1930_snmp_zabbix74.yaml
├── netgear-gs748tv5/
│   ├── README.md
│   └── netgear_gs748tv5_snmp_zabbix74.yaml
└── Cato Networks/
    ├── README.md
    ├── INSTALL.md
    └── template_cato_networks_http.yaml
```

> The individual template files and their READMEs are provided in this bundle; simply place each pair (or, for Cato, the trio) into the sub‑folder shown above before pushing to your repository.

## Common Design Choices

These conventions are shared by the **SNMP** templates in this repository:

- **Numeric OIDs only** — no MIB files to install on the Zabbix server/proxy.
- **Low‑level discovery** for interfaces, filtered by default to Ethernet ports (`ifType=6`) that are administratively up. Behaviour is fully tunable via `{$IF.*}` macros.
- **Edge‑triggered link‑down** — the *Link down* trigger fires **only on an up→down transition** (it compares the last two samples), so ports left permanently disconnected do **not** create standing problems. It auto‑resolves when the port returns up. Toggle with `{$IFCONTROL}`.
- **Aggregate throughput** — total in/out switch throughput via `sum(last_foreach(...))`.
- **Full‑HD dashboard** — throughput, CPU (and memory where available), uptime, availability and an active‑problems widget.

The **Cato Networks** template follows the idiomatic HTTP‑agent pattern instead:

- **Master item + LLD + dependent items** — a handful of GraphQL calls populate dozens of metrics per cycle, staying within Cato API rate limits.
- **One Zabbix host = one Cato account** — every site, WAN link and Socket is discovered automatically; dashboards are **multi‑site aware** (wildcard item patterns plot one line per site/link, honeycombs show one cell per site).
- **Defensive parsing** — missing fields never break sibling items; count/inventory items fall back to `0` so a missing permission can't cascade into "not supported" calculated items.
- **"API errors" sentinels** — each master item exposes any GraphQL error in plain text for quick diagnosis.
- **Secret macro** for the API key, source‑IP restricted in the Cato Management Application.

Shared across all templates:

- **Zabbix 7.x schema** — template‑level triggers live at the root of `zabbix_export`, and every UUID is a valid RFC 4122 **UUIDv4**.
- **Continuous integration** — every push and pull request is automatically checked for YAML syntax, correct Zabbix structure and the absence of private data (see [`.github/workflows/validate.yml`](./.github/workflows/validate.yml)).

## Compatibility

- **Zabbix:** 7.4 (export schema `version: 7.4`). Imports on **7.0 LTS** in most cases.
- **SNMP (switch templates):** v1 / v2c / v3. Templates ship configured for **v2c**. Transport UDP/161; ICMP (`fping`) for availability.
- **HTTP (Cato template):** outbound HTTPS (443) from the Zabbix server/proxy to `api*.catonetworks.com`. Requires a read‑only Cato API key and the CMA account ID. No SNMP interface is used.

Related switch models that share the same firmware/OID layout are often compatible — see the "Hardware Compatibility" section of each template's README before relying on the vendor‑specific items, and always confirm with an SNMP walk. For Cato, some fields are EA/Beta and may differ per account; the template is defensive and surfaces any schema error via its sentinel items.

## Contributing

Contributions are very welcome — bug fixes, new device families, extra items/triggers, or documentation improvements.

👉 **Please read the full [CONTRIBUTING.md](./CONTRIBUTING.md) before opening an issue or pull request.** It covers reporting bugs, requesting new devices, the PR workflow, template conventions, the validation checklist and privacy/legal notes.

Issue and pull‑request templates are provided under [`.github/`](./.github) to guide you through the required information (model, firmware, Zabbix version, redacted SNMP walk — or, for Cato, the redacted GraphQL error and account region). All contributions are automatically validated by the CI workflow before merge.

In short:

- **Search first**, then open an issue for anything larger than a small fix.
- For SNMP devices include **model + firmware + Zabbix version** and a **redacted SNMP walk**; for Cato include the **redacted API error** and CMA region.
- Follow the **template conventions** (numeric OIDs / defensive GraphQL, macros for thresholds, no private data).
- **Validate** the import, discovery and triggers before submitting.
- Contributions are accepted under the project's **MIT License**.

## Trademarks & Disclaimer

This is an **unofficial, community‑maintained** project. It is **not affiliated with, endorsed by, or sponsored by** Hewlett Packard Enterprise (HPE), Aruba Networks, NETGEAR, Broadcom, Cato Networks, or Zabbix.

- **HPE**, **Aruba**, **Instant On**, and related names and logos are trademarks or registered trademarks of **Hewlett Packard Enterprise Development LP** and/or its affiliates.
- **NETGEAR**, **ProSAFE**, and related names and logos are trademarks or registered trademarks of **NETGEAR, Inc.**
- **Broadcom** and **FastPath** are trademarks or registered trademarks of **Broadcom Inc.** and/or its affiliates.
- **Cato Networks** and related names and logos are trademarks or registered trademarks of **Cato Networks Ltd.**
- **Zabbix** is a registered trademark of **Zabbix SIA**.

All product names, logos, and brands are the property of their respective owners. They are used in this repository **for identification and descriptive purposes only**, and their use does not imply any affiliation or endorsement.

The vendor **MIB files** referenced during the creation of the SNMP templates remain the intellectual property of their respective owners and are **subject to the licensing terms of each vendor**. They are **not redistributed** in this repository — only original template code using numeric OIDs is provided. Obtain the MIBs from the official vendor sources if you need them.

This software is provided **"as is"**, without warranty of any kind (see the [License](#license)). Always test in a non‑production environment first. The maintainers are not responsible for any damage, data loss, or service disruption arising from its use.

## License

Released under the **MIT License** — free to use, modify and redistribute. See [`LICENSE`](./LICENSE) for details.

Copyright (c) 2026 NET365 Srl.
