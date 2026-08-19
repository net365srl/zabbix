<div align="center">

# Cato Networks — Zabbix Template

**Monitor a Cato Networks SASE account in Zabbix 7.4 over the Cato GraphQL API (HTTP agent).**

[![Zabbix](https://img.shields.io/badge/Zabbix-7.4-red.svg)](https://www.zabbix.com/)
[![API](https://img.shields.io/badge/Cato%20API-GraphQL-blueviolet.svg)](https://api.catonetworks.com/documentation/)
[![License: MIT-0](https://img.shields.io/badge/License-MIT--0-green.svg)](#license)
[![Template version](https://img.shields.io/badge/template-v2.0.7-blue.svg)](#)

</div>

---

## Overview

Cato Networks is a cloud-native SASE platform: it **does not expose SNMP or MIBs**. The only supported way to
extract state and telemetry is the **Cato GraphQL API**, queried over HTTPS. This template therefore uses the
Zabbix **HTTP agent** item type, not SNMP.

The design follows the idiomatic Zabbix pattern of **master item + Low-Level Discovery (LLD) + dependent items**:
a handful of API calls populate dozens of metrics per collection cycle, which keeps you well within
[Cato API rate limits](https://knowledge.catonetworks.com/docs/understanding-cato-api-rate-limiting).

### Multi-site by design

One Zabbix host represents **one whole Cato account**. Every **site**, **WAN link** and **Socket** is discovered
automatically and becomes its own set of items. Dashboards are **multi-site aware**: honeycombs show one cell per
site/Socket, and telemetry graphs use wildcard item patterns so **every site/link is plotted as its own line**.

### What it monitors

| Area | Examples | Default |
|------|----------|:------:|
| **Availability** | Sites connected/disconnected, operational status, connected PoP, host counts | ✅ |
| **Sockets / HA** | Per-Socket connectivity, HA role, uptime, firmware version & change detection | ✅ |
| **Network quality** | Throughput (up/down/total), packet loss, jitter, RTT, discarded packets — **per link, per site** | ✅ |
| **Inventory & drift** | Configured site count (entityLookup) vs. live snapshot | ✅ |
| **Events** | Account event volume trending (eventsFeed) | ✅¹ |
| **SLA** | Rolling 24h / 7d / 30d site availability | ✅ |
| **Dynamic routing (BGP)** | Peer state, advertised/received routes, session uptime | ⏸️² |

¹ Requires **Event Feed** enabled in the CMA. ² **Disabled by default** — the BGP status field is not part of
the stable/universal Cato schema; enable it after verifying the query for your account (see below).

---

## Architecture

```
                         ┌──────────────────────────────────────────────┐
                         │            Cato GraphQL API (HTTPS)            │
                         │  https://api.catonetworks.com/api/v1/graphql2  │
                         └──────────────────────────────────────────────┘
                                              ▲   x-api-key
        ┌──────────────┬───────────────┬──────┴───────┬───────────────┐
 accountSnapshot  accountMetrics    (BGP)⏸️      entityLookup     eventsFeed     ← 5 HTTP master items
        │              │                             │               │
        ▼              ▼                             ▼               ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │                     Zabbix host = ONE Cato account                     │
  │   LLD: Sites / WAN interfaces / Sockets(HA) / BGP peers                │
  │   Calculated: SLA 24h/7d/30d, inventory drift                         │
  │   Dashboard: 5 pages (Overview, Quality per-site, Sites&Sockets, BGP, SLA) │
  └───────────────────────────────────────────────────────────────────────┘
```

Each master item also has an **“API errors” sentinel** dependent item, so any GraphQL error (missing permission,
schema difference) is surfaced in plain text instead of cascading into “not supported” items.

---

## Requirements

- **Zabbix 7.4** server or proxy compiled with cURL (libcurl).
- A **Cato API key** (read-only recommended) — see [INSTALL.md](INSTALL.md#2-create-the-cato-api-key).
- Your **CMA account ID** (the number in the CMA URL).
- Outbound HTTPS (443) from the Zabbix server/proxy to `api*.catonetworks.com`.

---

## Quick start

1. **Import** `template_cato_networks_http.yaml` via *Data collection → Templates → Import*.
2. **Create a host** (e.g. `Cato Account - ACME`) and link **Cato Networks by HTTP**.
3. **Set macros** `{$CATO.API.KEY}` (Secret) and `{$CATO.ACCOUNT.ID}`.
4. Wait a couple of cycles, then open the **Cato Networks - Overview** dashboard.

Full walkthrough — including **how to create the API key step by step** (Service Principal), the permission
matrix and regional endpoints — in [INSTALL.md](INSTALL.md).

---

## Regional endpoint

If your CMA URL has a region prefix, set `{$CATO.API.URL}` accordingly. The **account subdomain does not count** —
only the part between `cc.` and `catonetworks.com` matters:

| CMA URL | `{$CATO.API.URL}` |
|---------|-------------------|
| `company.cc.catonetworks.com` (no region) | `https://api.catonetworks.com/api/v1/graphql2` *(default)* |
| `company.cc.us1.catonetworks.com` | `https://api.us1.catonetworks.com/api/v1/graphql2` |

---

## Enabling BGP monitoring (optional)

BGP is **disabled by default** because the BGP status field is EA/Beta and differs per account (e.g. `bgpStatus`
is not present on `DeviceSnapshot` for all accounts). To enable it:

1. Open the [Cato GraphQL Playground](https://knowledge.catonetworks.com/docs/connecting-to-the-cato-api-from-the-graphql-playground)
   and run introspection to find the correct BGP status query for **your** account.
2. Replace the query in the **`Cato: Get BGP status`** item.
3. Enable the **`Cato: Get BGP status`** item **and** the **`Cato: BGP peer discovery`** LLD rule.

The BGP item prototypes, triggers and graphs are already built — they populate as soon as the master item
returns valid data.

---

## Compatibility notes

- All JSON parsing is **defensive**: a missing field does not break sibling items, and count/inventory items
  fall back to `0` so a missing permission never cascades into “not supported” calculated items.
- The **`health`** link-score metric is **not** collected by default (EA/Beta field; querying it can make the
  whole `accountMetrics` query fail). Re-add it only if your account exposes it.
- **`eventsFeed`** uses **marker-based pagination** (not `timeFrame`) and needs the Event Feed enabled in the CMA.
- `lastMilePacketLoss` / `tunnelAge` are **timeseries-only** metrics and are intentionally not requested.

---

## Repository contents

| File | Purpose |
|------|---------|
| `template_cato_networks_http.yaml` | The Zabbix 7.4 template (import this) |
| `README.md` | This file |
| `INSTALL.md` | Step-by-step install, API key creation, permission matrix, endpoints |

---

## Disclaimer

This is a **community project** and is **not affiliated with, endorsed by, or supported by Cato Networks Ltd.**
"Cato", "Cato Networks" and related marks belong to their respective owners. Use at your own risk.

## License

Released under the **MIT-0** license (MIT No Attribution) — free to use, modify and redistribute without
attribution.
