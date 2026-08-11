# Zabbix SNMP Templates for Smart‑Managed Switches

![Zabbix](https://img.shields.io/badge/Zabbix-7.4-CC0000?logo=zabbix&logoColor=white)
![SNMP](https://img.shields.io/badge/SNMP-v2c%20%7C%20v3-0A66C2)
![Format](https://img.shields.io/badge/format-YAML-1A7C11)
![Templates](https://img.shields.io/badge/templates-2-2774A4)
![License](https://img.shields.io/badge/license-MIT-blue)
![Contributions](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Maintenance](https://img.shields.io/badge/maintained-yes-success)

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
8. [License](#license)

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

Contributions are welcome! When opening an issue or pull request, please include:

- Switch **model** and **firmware version**.
- The **Zabbix version** you are running.
- A short **SNMP walk** snippet for any OID‑related problem (e.g. `snmpwalk -v2c -c public <ip> <oid>`).

Ideas for new device families and improvements to the existing templates are appreciated.

## License

Released under the **MIT License** — free to use, modify and redistribute. See [`LICENSE`](./LICENSE) for details.
