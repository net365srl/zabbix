# HPE Networking / Aruba Instant On 1930 – Zabbix Template (by SNMP)

A community Zabbix template to monitor **HPE Networking (Aruba) Instant On 1930** smart‑managed switches over **SNMP**. It collects system health, CPU, hardware status and full per‑interface metrics through low‑level discovery (LLD), and ships with ready‑to‑use triggers, graphs and an overview dashboard.

> **Template name:** `HPE Instant On 1930 by SNMP`
> **Zabbix version:** 7.4 (export `version: 7.4`)
> **Data collection:** SNMPv2c (SNMPv3 supported by changing the interface/macros)
> **File:** `hpe_instanton_1930_snmp_zabbix74.yaml`

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

The HPE Instant On 1930 runs a **RADLAN‑based "Smart Managed" firmware**. This template combines:

- **Standard MIBs** – `SNMPv2-MIB` (system group) and `IF-MIB`/`ifXTable` (interfaces).
- **HPE private MIBs** – enterprise branch `1.3.6.1.4.1.11.2` (`nm`), used for CPU utilization and hardware health/inventory.

The result is vendor‑aware monitoring that goes beyond generic SNMP: CPU load, hardware sensor status, firmware/boot version tracking and per‑port traffic, errors and discards.

## 2. Hardware Compatibility

| Attribute | Detail |
|-----------|--------|
| **Product family** | HPE Networking / Aruba Instant On 1930 series |
| **Typical models** | JL680A, JL681A, JL682A, JL683A, JL684A, JG960A‑class PoE/non‑PoE variants (8/24/48‑port) |
| **Operating system** | Instant On "Smart Managed" firmware (RADLAN/Marvell lineage) |
| **Enterprise OID root** | `1.3.6.1.4.1.11.2` (`nm`) |
| **SNMP versions** | v1 / v2c / v3 (template ships with v2c) |

> **Note on related models:** the HPE Instant On **1960** and **1830** series use different firmware/OID layouts. The interface part (IF‑MIB) will still work on almost any SNMP switch, but the **CPU and hardware‑health items are specific to the 1930** and may return `No Such Object` elsewhere.

### Enabling SNMP on the switch

1. Log in to the Instant On switch web UI (or the Instant On cloud portal, if managed).
2. Go to **System → SNMP** (naming varies by firmware).
3. Enable SNMP, create a **read‑only community** (default assumed here: `public`), and, if available, restrict access by management IP/subnet.
4. Make sure the Zabbix server/proxy IP is allowed to poll the switch on **UDP/161**.

## 3. Requirements

- **Zabbix 7.4** server or proxy (the export targets schema `version: 7.4`; it also imports on 7.0 LTS in most cases).
- **SNMP poller** enabled on the Zabbix server/proxy (`StartSNMPPollers` > 0).
- Network reachability to the switch on **UDP/161** and, for the availability triggers, **ICMP** (`fping`).
- No custom MIB files need to be loaded into Zabbix: **all OIDs are numeric**.

## 4. Installation

1. In Zabbix, go to **Data collection → Templates**.
2. Click **Import** (top‑right).
3. Select `hpe_instanton_1930_snmp_zabbix74.yaml`, keep **Create new** checked and click **Import**.
4. Open the host you want to monitor (**Data collection → Hosts**).
5. Add an **SNMP interface** pointing to the switch IP (UDP/161).
6. On the **Templates** tab, link **`HPE Instant On 1930 by SNMP`**.
7. On the **Macros** tab, set **`{$SNMP.COMMUNITY}`** (and adjust thresholds if needed).

For **SNMPv3**, set the interface to v3 and provide the security parameters via the standard Zabbix SNMPv3 interface fields (the template does not hard‑code SNMP credentials).

## 5. Configuration Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$SNMP.COMMUNITY}` | `public` | SNMP v2c community string. |
| `{$SNMP.TIMEOUT}` | `5m` | Evaluation window for the "No SNMP data collection" trigger. |
| `{$CPU.UTIL.CRIT}` | `90` | CPU utilization threshold (%). |
| `{$ICMP.LOSS.WARN}` | `20` | ICMP packet‑loss warning threshold (%). |
| `{$IFCONTROL}` | `1` | Enables/disables the per‑interface **Link down** trigger (1=on, 0=off). |
| `{$IF.UTIL.MAX}` | `90` | Interface bandwidth utilization threshold (%). |
| `{$IF.ERRORS.WARN}` | `2` | Interface error threshold (packets/sec). |
| `{$IF.ADMINSTATUS.MATCHES}` | `^1$` | Discover only interfaces whose admin status = up(1). |
| `{$IF.TYPE.MATCHES}` | `^6$` | Discover only `ethernetCsmacd` interfaces (ifType=6). |
| `{$NET.IF.IFNAME.NOT_MATCHES}` | `(^$)` | Regex of interface names to exclude from discovery. |

## 6. Collected Items

**System (SNMPv2-MIB)** — description, name, location, contact, object ID, uptime.

**CPU (HPE enterprise)** — average CPU utilization and last‑second CPU utilization.

**Hardware & inventory (HPE-DEVICEPARAMS-MIB)** — hardware health status (`ok/hardwareProblems/notSupported`), boot version, hardware version, base MAC address.

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
| Hardware health is in problem state | High | `genGroupHWStatus` returns `hardwareProblems(2)`. |
| Firmware/boot version has changed | Information | Boot version value differs from the previous poll. |

### Per‑interface trigger prototypes

| Name | Severity | Behaviour |
|------|----------|-----------|
| **Link down** | High | **Fires only on an up→down transition** (see below). |
| High bandwidth utilization | Warning | In or out avg over 15 min exceeds `{$IF.UTIL.MAX}` % of link speed. |
| High error rate | Warning | In or out error rate over 5 min exceeds `{$IF.ERRORS.WARN}`. |

#### "Link down" — transition‑based logic

The Link down trigger is **edge‑triggered**: it raises a problem only when a port *changes* from up to down, not for ports that are simply left disconnected.

```
{$IFCONTROL}=1 and
last(/HPE Instant On 1930 by SNMP/net.if.status[ifOperStatus.{#SNMPINDEX}],#1)=2 and
last(/HPE Instant On 1930 by SNMP/net.if.status[ifOperStatus.{#SNMPINDEX}],#2)=1 and
last(/HPE Instant On 1930 by SNMP/net.if.adminstatus[ifAdminStatus.{#SNMPINDEX}])=1
```

- `,#1)=2` → the **latest** sample is *down*.
- `,#2)=1` → the **previous** sample was *up* → this is a genuine transition.
- A port that is **already down** has `#1=2` and `#2=2`, so the condition is false → **no alert**.

**Recovery** (recovery expression mode): the problem clears when the port is operationally back up:

```
last(/HPE Instant On 1930 by SNMP/net.if.status[ifOperStatus.{#SNMPINDEX}])<>2
```

> To disable Link down alerting entirely (e.g. on lab switches), set `{$IFCONTROL}=0`.

## 9. Graphs and Dashboard

- **Graph prototype** `Interface [{#IFNAME}({#IFALIAS})]: Traffic` — an in/out traffic graph created automatically for every discovered port.
- **Template dashboard** `HPE Instant On 1930 - Overview` (optimized for Full HD) with:
  - Total switch throughput (in/out) SVG graph
  - CPU utilization, Uptime, Hardware health, ICMP ping value widgets
  - Active problems widget
  - Per‑interface traffic SVG graph (pattern‑based, all ports)

## 10. Limitations and Known Issues

- **No RAM/memory monitoring.** The Instant On 1930 "Smart Managed" firmware **does not expose physical memory OIDs** via SNMP (only flash partitions appear in the host‑resources dump). There is therefore **no memory item** in this template by design. If you need RAM visibility, consider the FastPath‑based models (e.g. the companion Netgear GS748Tv5 template) which do expose it.
- **CPU OID is vendor/firmware specific.** CPU utilization relies on the HPE enterprise OIDs `1.3.6.1.4.1.11.2.1.8.0` / `...7.0`. These are confirmed on the 1930 line; on other HPE/Aruba families they may not exist.
- **Counters require 64‑bit support.** Traffic uses `ifHCInOctets/ifHCOutOctets`. Extremely old firmware without ifXTable would need the 32‑bit counters instead.
- **Hardware‑health granularity.** `genGroupHWStatus` is a single aggregate sensor state; the 1930 does not publish per‑fan/per‑PSU/temperature sensor tables, so fine‑grained environmental monitoring is not available.
- **Discovery scope.** By default only Ethernet ports with admin status up are discovered. Adjust the `{$IF.*}` macros to widen or narrow the scope.

## 11. SNMP OID Reference

| Metric | OID | Source MIB |
|--------|-----|------------|
| sysDescr | `1.3.6.1.2.1.1.1.0` | SNMPv2-MIB |
| sysUpTime | `1.3.6.1.2.1.1.3.0` | SNMPv2-MIB |
| CPU utilization (avg) | `1.3.6.1.4.1.11.2.1.8.0` | HPE enterprise (nm) |
| CPU utilization (last sec) | `1.3.6.1.4.1.11.2.1.7.0` | HPE enterprise (nm) |
| Hardware health status | `1.3.6.1.4.1.11.2.2.11.3.0` | HPE-DEVICEPARAMS-MIB (genGroupHWStatus) |
| Boot version | `1.3.6.1.4.1.11.2.2.10.0` | HPE-DEVICEPARAMS-MIB (rndBaseBootVersion) |
| Hardware version | `1.3.6.1.4.1.11.2.2.11.1.0` | HPE-DEVICEPARAMS-MIB (genGroupHWVersion) |
| Base MAC address | `1.3.6.1.4.1.11.2.2.12.0` | HPE-DEVICEPARAMS-MIB (rndBasePhysicalAddress) |
| ifHCInOctets | `1.3.6.1.2.1.31.1.1.1.6.<idx>` | IF-MIB (ifXTable) |
| ifHCOutOctets | `1.3.6.1.2.1.31.1.1.1.10.<idx>` | IF-MIB (ifXTable) |
| ifOperStatus | `1.3.6.1.2.1.2.2.1.8.<idx>` | IF-MIB |
| ifAdminStatus | `1.3.6.1.2.1.2.2.1.7.<idx>` | IF-MIB |
| ifHighSpeed | `1.3.6.1.2.1.31.1.1.1.15.<idx>` | IF-MIB (ifXTable) |

## 12. Troubleshooting

- **All SNMP items are "Not supported".** Verify community/ACL, that UDP/161 is reachable, and that SNMP is enabled on the switch.
- **CPU item unsupported.** Confirm the device is truly a 1930 (check `sysObjectID`/`sysDescr`); the CPU OID is model‑specific.
- **No interfaces discovered.** Loosen `{$IF.ADMINSTATUS.MATCHES}` / `{$IF.TYPE.MATCHES}`; some ports may be admin‑down or non‑Ethernet.
- **Import error mentioning an unexpected tag.** Ensure you are importing into Zabbix **7.0 or newer**; this export uses the 7.x schema where template‑level triggers live at the root of `zabbix_export`.

## 13. License and Contributing

Distributed as a community template — you are free to use, modify and redistribute it. Contributions (PRs/issues) are welcome: please include the switch model, firmware version and a short SNMP walk snippet when reporting OID‑related problems.
