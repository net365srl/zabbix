# Zabbix SNMP Templates for Smart‑Managed Switches

![Zabbix](https://img.shields.io/badge/Zabbix-7.4-CC0000?logo=zabbix&logoColor=white)
![SNMP](https://img.shields.io/badge/SNMP-v2c%20%7C%20v3-0A66C2)
![Format](https://img.shields.io/badge/format-YAML-1A7C11)
![Templates](https://img.shields.io/badge/templates-2-2774A4)
![License](https://img.shields.io/badge/license-MIT-blue)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Maintained](https://img.shields.io/badge/maintained-yes-success)
<br>
![Platform](https://img.shields.io/badge/platform-network%20switches-555555)
![Vendors](https://img.shields.io/badge/vendors-HPE%20%7C%20Netgear-orange)
![Monitoring](https://img.shields.io/badge/monitoring-SNMP%20polling-9cf)
![Discovery](https://img.shields.io/badge/LLD-interfaces-blueviolet)
![Dashboard](https://img.shields.io/badge/dashboard-Full%20HD-ff69b4)
![Contributions](https://img.shields.io/badge/contributions-welcome-8A2BE2)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

A collection of **community Zabbix 7.4 templates** to monitor smart‑managed switches over **SNMP**. Each template ships with vendor‑aware items, low‑level discovery (LLD) of network interfaces, ready‑to‑use triggers, per‑interface graphs and a Full‑HD overview dashboard. All OIDs are **numeric**, so no external MIB files need to be loaded into Zabbix.

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

| Template | Vendor / OS | Model(s) | Docs | File |
|----------|-------------|----------|------|------|
| **HPE Instant On 1930 by SNMP** | HPE / Aruba – RADLAN "Smart Managed" | Instant On 1930 series (8/24/48‑port, PoE & non‑PoE) | [README](./hpe-instanton-1930/README.md) | [`hpe_instanton_1930_snmp_zabbix74.yaml`](./hpe-instanton-1930/hpe_instanton_1930_snmp_zabbix74.yaml) |
| **Netgear GS748Tv5 by SNMP** | Netgear – FastPath / Broadcom | GS748Tv5 (+ many FastPath GSxxxT models) | [README](./netgear-gs748tv5/README.md) | [`netgear_gs748tv5_snmp_zabbix74.yaml`](./netgear-gs748tv5/netgear_gs748tv5_snmp_zabbix74.yaml) |

## Feature Matrix

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

## Quick Start

1. In Zabbix, go to **Data collection → Templates → Import**.
2. Select the `*.yaml` file of the switch you want to monitor and keep **Create new** checked.
3. Open the target host (**Data collection → Hosts**) and add an **SNMP interface** (UDP/161).
4. On the **Templates** tab, link the imported template.
5. On the **Macros** tab, set **`{$SNMP.COMMUNITY}`** (default `public`) and adjust thresholds if needed.
6. Wait for the interface discovery to run, then open **Monitoring → Hosts → Dashboards**.

For **SNMPv3**, switch the host SNMP interface to v3 and fill in the standard security fields — the templates do not hard‑code any credentials.

## Repository Structure

```
.
├── README.md                     ← this file
├── LICENSE
├── CONTRIBUTING.md
├── hpe-instanton-1930/
│   ├── README.md
│   └── hpe_instanton_1930_snmp_zabbix74.yaml
└── netgear-gs748tv5/
    ├── README.md
    └── netgear_gs748tv5_snmp_zabbix74.yaml
```

> The individual template files and their READMEs are provided in this bundle; simply place each pair into the sub‑folder shown above before pushing to your repository.

## Common Design Choices

These conventions are shared by every template in this repository:

- **Numeric OIDs only** — no MIB files to install on the Zabbix server/proxy.
- **Low‑level discovery** for interfaces, filtered by default to Ethernet ports (`ifType=6`) that are administratively up. Behaviour is fully tunable via `{$IF.*}` macros.
- **Edge‑triggered link‑down** — the *Link down* trigger fires **only on an up→down transition** (it compares the last two samples), so ports left permanently disconnected do **not** create standing problems. It auto‑resolves when the port returns up. Toggle with `{$IFCONTROL}`.
- **Aggregate throughput** — total in/out switch throughput via `sum(last_foreach(...))`.
- **Full‑HD dashboard** — throughput, CPU (and memory where available), uptime, availability and an active‑problems widget.
- **Zabbix 7.x schema** — template‑level triggers live at the root of `zabbix_export`, as required by Zabbix 6.0+.

## Compatibility

- **Zabbix:** 7.4 (export schema `version: 7.4`). Imports on **7.0 LTS** in most cases.
- **SNMP:** v1 / v2c / v3. Templates ship configured for **v2c**.
- **Transport:** UDP/161 to the switch; ICMP (`fping`) for availability triggers.

Related switch models that share the same firmware/OID layout are often compatible — see the "Hardware Compatibility" section of each template's README before relying on the vendor‑specific items, and always confirm with an SNMP walk.

## Contributing

Contributions are very welcome — bug fixes, new device families, extra items/triggers, or documentation improvements.

👉 **Please read the full [CONTRIBUTING.md](./CONTRIBUTING.md) before opening an issue or pull request.** It covers reporting bugs, requesting new devices, the PR workflow, template conventions, the validation checklist and privacy/legal notes.

In short:

- **Search first**, then open an issue for anything larger than a small fix.
- Include **model + firmware + Zabbix version** and a **redacted SNMP walk** in bug reports.
- Follow the **template conventions** (numeric OIDs, macros for thresholds, no private data).
- **Validate** the import, discovery and triggers before submitting.
- Contributions are accepted under the project's **MIT License**.

## Trademarks & Disclaimer

This is an **unofficial, community‑maintained** project. It is **not affiliated with, endorsed by, or sponsored by** Hewlett Packard Enterprise (HPE), Aruba Networks, NETGEAR, Broadcom, or Zabbix.

- **HPE**, **Aruba**, **Instant On**, and related names and logos are trademarks or registered trademarks of **Hewlett Packard Enterprise Development LP** and/or its affiliates.
- **NETGEAR**, **ProSAFE**, and related names and logos are trademarks or registered trademarks of **NETGEAR, Inc.**
- **Broadcom** and **FastPath** are trademarks or registered trademarks of **Broadcom Inc.** and/or its affiliates.
- **Zabbix** is a registered trademark of **Zabbix SIA**.

All product names, logos, and brands are the property of their respective owners. They are used in this repository **for identification and descriptive purposes only**, and their use does not imply any affiliation or endorsement.

The vendor **MIB files** referenced during the creation of these templates remain the intellectual property of their respective owners and are **subject to the licensing terms of each vendor**. They are **not redistributed** in this repository — only original template code using numeric OIDs is provided. Obtain the MIBs from the official vendor sources if you need them.

This software is provided **"as is"**, without warranty of any kind (see the [License](#license)). Always test in a non‑production environment first. The maintainers are not responsible for any damage, data loss, or service disruption arising from its use.

## License

Released under the **MIT License** — free to use, modify and redistribute. See [`LICENSE`](./LICENSE) for details.

Copyright (c) 2026 NET365 Srl.
