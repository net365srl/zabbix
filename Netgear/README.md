# Netgear GS748Tv5 – Zabbix Template (by SNMP)

A community Zabbix template to monitor the **Netgear GS748Tv5** (ProSAFE Smart Managed, **FastPath/Broadcom OS**) switch over **SNMP**. It collects inventory, CPU **and memory**, availability and full per‑interface metrics through low‑level discovery (LLD), and ships with ready‑to‑use triggers, graphs and an overview dashboard.

> **Template name:** `Netgear GS748Tv5 by SNMP`
> **Zabbix version:** 7.4 (export `version: 7.4`)
> **Data collection:** SNMPv2c (SNMPv3 supported by changing the interface/macros)
> **File:** `netgear_gs748tv5_snmp_zabbix74.yaml`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Hardware Compatibility](#2-hardware-compatibility)
3. [Requirements](#3-requirements)
4. [Installation](#4-installation)
5. [Configuration Macros](#5-configuration-macros)
6. [Collected Items](#6-collected-items)
7. [Low-Level Discovery (Interfaces)](#7-low-level-discovery-interfaces)
8. [Triggers](#8-triggers)
9. [Graphs and Dashboard](#9-graphs-and-dashboard)
10. [Limitations and Known Issues](#10-limitations-and-known-issues)
11. [SNMP OID Reference](#11-snmp-oid-reference)
12. [Troubleshooting](#12-troubleshooting)
13. [License and Contributing](#13-license-and-contributing)

---

## 1. Overview

The Netgear GS748Tv5 runs a **FastPath (Broadcom)** firmware. This template combines:

- **Standard MIBs** – `SNMPv2-MIB` (system group) and `IF-MIB`/`ifXTable` (interfaces).
- **Netgear private MIBs** – `NETGEAR-REF-MIB` (enterprise root `1.3.6.1.4.1.4526`) and `NETGEAR-SWITCHING-MIB` (`fastPathSwitching` under `ng700smartswitch`), used for inventory, CPU and memory.

Unlike many smart‑managed switches, the FastPath firmware **does expose CPU and memory**, so this template provides full compute‑resource visibility in addition to per‑port traffic, errors and discards.

## 2. Hardware Compatibility

| Attribute | Detail |
|-----------|--------|
| **Product** | Netgear GS748Tv5 (48‑port Gigabit ProSAFE Smart Managed) |
| **Operating system** | FastPath / Broadcom firmware |
| **Enterprise OID root** | `1.3.6.1.4.1.4526` (`netgear`) |
| **Model sysObjectID** | `1.3.6.1.4.1.4526.100.4.33` (`gs748tv5`) |
| **SNMP versions** | v1 / v2c / v3 (template ships with v2c) |

> **Note on related models:** other FastPath‑based Netgear smart switches (e.g. GS716Tv3, GS724Tv4, GS752TPS and various GSxxxT models) share the same `NETGEAR-SWITCHING-MIB` inventory/CPU/memory OIDs, so the **template will largely work on them too** — only the `sysObjectID` (used purely for documentation here) differs. Always confirm with an SNMP walk before relying on the vendor‑specific items.

### Enabling SNMP on the switch

1. Log in to the GS748Tv5 web UI.
2. Go to **System → SNMP → SNMP V1/V2**.
3. Enable SNMP, configure a **read‑only community** (default assumed here: `public`) and, ideally, restrict the allowed management stations.
4. Ensure the Zabbix server/proxy can reach the switch on **UDP/161**.

## 3. Requirements

- **Zabbix 7.4** server or proxy (the export targets schema `version: 7.4`; it also imports on 7.0 LTS in most cases).
- **SNMP poller** enabled on the Zabbix server/proxy (`StartSNMPPollers` > 0).
- Network reachability to the switch on **UDP/161** and, for the availability triggers, **ICMP** (`fping`).
- No custom MIB files need to be loaded into Zabbix: **all OIDs are numeric**.

## 4. Installation

1. In Zabbix, go to **Data collection → Templates**.
2. Click **Import** (top‑right).
3. Select `netgear_gs748tv5_snmp_zabbix74.yaml`, keep **Create new** checked and click **Import**.
4. Open the host you want to monitor (**Data collection → Hosts**).
5. Add an **SNMP interface** pointing to the switch IP (UDP/161).
6. On the **Templates** tab, link **`Netgear GS748Tv5 by SNMP`**.
7. On the **Macros** tab, set **`{$SNMP.COMMUNITY}`** (and adjust thresholds if needed).

For **SNMPv3**, set the interface to v3 and provide the security parameters via the standard Zabbix SNMPv3 interface fields (the template does not hard‑code SNMP credentials).

## 5. Configuration Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$SNMP.COMMUNITY}` | `public` | SNMP v2c community string. |
| `{$SNMP.TIMEOUT}` | `5m` | Evaluation window for the "No SNMP data collection" trigger. |
| `{$CPU.UTIL.CRIT}` | `90` | CPU utilization threshold (%). |
| `{$MEMORY.UTIL.MAX}` | `90` | Memory utilization threshold (%). |
| `{$ICMP.LOSS.WARN}` | `20` | ICMP packet‑loss warning threshold (%). |
| `{$IFCONTROL}` | `1` | Enables/disables the per‑interface **Link down** trigger (1=on, 0=off). |
| `{$IF.UTIL.MAX}` | `90` | Interface bandwidth utilization threshold (%). |
| `{$IF.ERRORS.WARN}` | `2` | Interface error threshold (packets/sec). |
| `{$IF.ADMINSTATUS.MATCHES}` | `^1$` | Discover only interfaces whose admin status = up(1). |
| `{$IF.TYPE.MATCHES}` | `^6$` | Discover only `ethernetCsmacd` interfaces (ifType=6). |
| `{$NET.IF.IFNAME.NOT_MATCHES}` | `(^$)` | Regex of interface names to exclude from discovery. |

## 6. Collected Items

**System (SNMPv2-MIB)** — description, name, location, contact, uptime.

**Inventory (NETGEAR-SWITCHING-MIB `agentInventoryGroup`)** — model, serial number, manufacturer, burned‑in MAC, operating system, software (firmware) version, hardware version.

**CPU** — total CPU utilization. The source OID returns a **string** with 5/60/300‑second values; the template extracts the **60‑second** figure via a regex preprocessing step.

**Memory** — memory available (total) and memory free, both reported in **KBytes** by the device and converted to bytes; plus a **calculated** *Memory utilization (%)*.

**Aggregate** — *Total incoming throughput* and *Total outgoing throughput* (sum of all discovered interfaces, in bps), computed with `sum(last_foreach(...))`.

**Availability** — ICMP ping / loss / response time and the internal SNMP agent availability item.

## 7. Low-Level Discovery (Interfaces)

A single LLD rule (`Network interfaces discovery`) walks the IF‑MIB and creates, **per interface**, the following item prototypes:

- **Bits received / sent** — 64‑bit counters `ifHCInOctets` / `ifHCOutOctets`, converted to bps.
- **Inbound / outbound errors** — `ifInErrors` / `ifOutErrors` (per second).
- **Inbound / outbound discards** — `ifInDiscards` / `ifOutDiscards` (per second).
- **Operational status** — `ifOperStatus` (value‑mapped).
- **Admin status** — `ifAdminStatus` (value‑mapped).
- **Speed** — `ifHighSpeed` (Mbit/s → bps).

**Discovery filters (AND):** admin status must match `{$IF.ADMINSTATUS.MATCHES}`, ifType must match `{$IF.TYPE.MATCHES}` (Ethernet only by default), and the interface name must not match `{$NET.IF.IFNAME.NOT_MATCHES}`.

## 8. Triggers

### Template‑level triggers

| Name | Severity | Fires when |
|------|----------|-----------|
| Unavailable by ICMP ping | High | 3 consecutive ICMP checks fail. |
| No SNMP data collection | Warning | SNMP agent unavailable for `{$SNMP.TIMEOUT}` (depends on the ICMP trigger). |
| High ICMP ping loss | Warning | ICMP loss above `{$ICMP.LOSS.WARN}` (and < 100 %). |
| Device has been restarted | Information | Uptime < 10 minutes. |
| High CPU utilization | Warning | CPU above `{$CPU.UTIL.CRIT}` % for 5 minutes. |
| High memory utilization | Average | Memory above `{$MEMORY.UTIL.MAX}` % for 5 minutes. |
| Firmware version has changed | Information | Software version value differs from the previous poll. |

### Per‑interface trigger prototypes

| Name | Severity | Behaviour |
|------|----------|-----------|
| **Link down** | **Information** | **Fires only on an up→down transition** (see below). |
| High bandwidth utilization | Warning | In or out avg over 15 min exceeds `{$IF.UTIL.MAX}` % of link speed. |
| High error rate | Warning | In or out error rate over 5 min exceeds `{$IF.ERRORS.WARN}`. |

#### "Link down" — transition‑based logic (severity: Information)

The Link down trigger is **edge‑triggered** and classified as **Information**: it raises an informational event only when a port *changes* from up to down, not for ports that are simply left disconnected.

```
{$IFCONTROL}=1 and
last(/Netgear GS748Tv5 by SNMP/net.if.status[ifOperStatus.{#SNMPINDEX}],#1)=2 and
last(/Netgear GS748Tv5 by SNMP/net.if.status[ifOperStatus.{#SNMPINDEX}],#2)=1 and
last(/Netgear GS748Tv5 by SNMP/net.if.adminstatus[ifAdminStatus.{#SNMPINDEX}])=1
```

- `,#1)=2` → the **latest** sample is *down*.
- `,#2)=1` → the **previous** sample was *up* → this is a genuine transition.
- A port that is **already down** has `#1=2` and `#2=2`, so the condition is false → **no alert**.

**Recovery** (recovery expression mode): the event clears when the port is operationally back up:

```
last(/Netgear GS748Tv5 by SNMP/net.if.status[ifOperStatus.{#SNMPINDEX}])<>2
```

> To disable Link down alerting entirely (e.g. on lab switches), set `{$IFCONTROL}=0`.

## 9. Graphs and Dashboard

- **Graph prototype** `Interface [{#IFNAME}({#IFALIAS})]: Traffic` — an in/out traffic graph created automatically for every discovered port.
- **Template dashboard** `Netgear GS748Tv5 - Overview` (optimized for Full HD) with:
  - Total switch throughput (in/out) SVG graph
  - CPU utilization, **Memory utilization**, Uptime, ICMP ping value widgets
  - Active problems widget
  - Per‑interface traffic SVG graph (pattern‑based, all ports)

## 10. Limitations and Known Issues

- **CPU value parsing.** The FastPath CPU OID returns a formatted string (`5 Secs (…%) 60 Secs (…%) 300 Secs (…%)`). The template extracts the **60‑second** value via regex; if a future firmware changes the string layout, adjust the regex in the *CPU utilization* item.
- **Memory units.** The device reports memory in **KBytes**; the template multiplies by 1024 to store bytes. *Total* here corresponds to `agentSwitchCpuProcessMemAvailable` and *free* to `agentSwitchCpuProcessMemFree`.
- **No per‑sensor environmental data.** The GS748Tv5 does not publish standard fan/PSU/temperature sensor tables via these MIBs, so environmental monitoring is not included.
- **PoE.** The GS748Tv5 is a non‑PoE model; no PoE items are provided. PoE‑capable FastPath models expose additional OIDs that are out of scope for this template.
- **Counters require 64‑bit support.** Traffic uses `ifHCInOctets/ifHCOutOctets` from ifXTable.
- **Discovery scope.** By default only Ethernet ports with admin status up are discovered. Adjust the `{$IF.*}` macros to widen or narrow the scope.

## 11. SNMP OID Reference

| Metric | OID | Source MIB |
|--------|-----|------------|
| sysDescr | `1.3.6.1.2.1.1.1.0` | SNMPv2-MIB |
| sysUpTime | `1.3.6.1.2.1.1.3.0` | SNMPv2-MIB |
| Model | `1.3.6.1.4.1.4526.11.1.1.1.3.0` | NETGEAR-SWITCHING-MIB (agentInventoryMachineModel) |
| Serial number | `1.3.6.1.4.1.4526.11.1.1.1.4.0` | agentInventorySerialNumber |
| Manufacturer | `1.3.6.1.4.1.4526.11.1.1.1.8.0` | agentInventoryManufacturer |
| Burned‑in MAC | `1.3.6.1.4.1.4526.11.1.1.1.9.0` | agentInventoryBurnedInMacAddress |
| Operating system | `1.3.6.1.4.1.4526.11.1.1.1.10.0` | agentInventoryOperatingSystem |
| Software version | `1.3.6.1.4.1.4526.11.1.1.1.13.0` | agentInventorySoftwareVersion |
| Hardware version | `1.3.6.1.4.1.4526.11.1.1.1.14.0` | agentInventoryHardwareVersion |
| CPU total utilization | `1.3.6.1.4.1.4526.11.1.1.4.9.0` | agentSwitchCpuProcessTotalUtilization |
| Memory available (KB) | `1.3.6.1.4.1.4526.11.1.1.4.2.0` | agentSwitchCpuProcessMemAvailable |
| Memory free (KB) | `1.3.6.1.4.1.4526.11.1.1.4.1.0` | agentSwitchCpuProcessMemFree |
| ifHCInOctets | `1.3.6.1.2.1.31.1.1.1.6.<idx>` | IF-MIB (ifXTable) |
| ifHCOutOctets | `1.3.6.1.2.1.31.1.1.1.10.<idx>` | IF-MIB (ifXTable) |
| ifOperStatus | `1.3.6.1.2.1.2.2.1.8.<idx>` | IF-MIB |
| ifAdminStatus | `1.3.6.1.2.1.2.2.1.7.<idx>` | IF-MIB |
| ifHighSpeed | `1.3.6.1.2.1.31.1.1.1.15.<idx>` | IF-MIB (ifXTable) |

## 12. Troubleshooting

- **All SNMP items are "Not supported".** Verify community/ACL, that UDP/161 is reachable, and that SNMP is enabled on the switch.
- **CPU item unsupported or empty.** Do an SNMP walk of `1.3.6.1.4.1.4526.11.1.1.4.9.0` and confirm the string format matches the regex; adjust if the firmware differs.
- **Memory utilization looks wrong.** Confirm that both *Memory free* and *Memory available (total)* return values; the calculated item needs both.
- **No interfaces discovered.** Loosen `{$IF.ADMINSTATUS.MATCHES}` / `{$IF.TYPE.MATCHES}`; some ports may be admin‑down or non‑Ethernet.
- **Import error mentioning an unexpected tag.** Ensure you are importing into Zabbix **7.0 or newer**; this export uses the 7.x schema where template‑level triggers live at the root of `zabbix_export`.

## 13. License and Contributing

Distributed as a community template — you are free to use, modify and redistribute it. Contributions (PRs/issues) are welcome: please include the switch model, firmware version and a short SNMP walk snippet when reporting OID‑related problems.
