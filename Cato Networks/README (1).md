<div align="center">

# Cato Networks — Zabbix Template

**Monitor a Cato Networks SASE account in Zabbix 7.4 over the Cato GraphQL API (HTTP agent).**

[![Zabbix](https://img.shields.io/badge/Zabbix-7.4-red.svg)](https://www.zabbix.com/)
[![API](https://img.shields.io/badge/Cato%20API-GraphQL-blueviolet.svg)](https://api.catonetworks.com/documentation/)
[![License: MIT-0](https://img.shields.io/badge/License-MIT--0-green.svg)](LICENSE)
[![Template version](https://img.shields.io/badge/template-v2.0.1-blue.svg)](CHANGELOG.md)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## Overview

Cato Networks is a cloud-native SASE platform: it **does not expose SNMP or MIBs**. The only supported way to
extract state and telemetry is the **Cato GraphQL API**, queried over HTTPS. This template therefore uses the
Zabbix **HTTP agent** item type, not SNMP.

The design follows the idiomatic Zabbix pattern of **master item + Low-Level Discovery (LLD) + dependent items**:
a handful of API calls populate dozens of metrics per collection cycle, which keeps you well within
[Cato API rate limits](https://support.catonetworks.com/hc/en-us/articles/360014905918-Cato-API-AccountMetrics).

### What it monitors

| Area | Examples |
|------|----------|
| **Availability** | Sites connected/disconnected, operational status, connected PoP, host counts |
| **Sockets / HA** | Per-Socket connectivity, HA role, uptime, firmware version & change detection |
| **Network quality** | Throughput (up/down/total), packet loss, jitter, RTT, discarded packets, health score |
| **Dynamic routing (BGP)** | Peer state, advertised/received routes, session uptime & flap detection |
| **Inventory & drift** | Configured site count (entityLookup) vs. live snapshot |
| **Events** | Account event volume trending (eventsFeed) |
| **SLA** | Rolling 24h / 7d / 30d site availability, health trends |

---

## Architecture

```
                         ┌──────────────────────────────────────────────┐
                         │            Cato GraphQL API (HTTPS)            │
                         │   https://api.catonetworks.com/api/v1/graphql2 │
                         └──────────────────────────────────────────────┘
                                              ▲   x-api-key
        ┌──────────────┬───────────────┬──────┴───────┬───────────────┐
        │              │               │              │               │
 accountSnapshot  accountMetrics    bgpStatus    entityLookup     eventsFeed     ← 5 HTTP master items
        │              │               │              │               │
        ▼              ▼               ▼              ▼               ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │                     Zabbix host = ONE Cato account                     │
  │                                                                        │
  │   LLD: Sites ──► per-site items + triggers                             │
  │   LLD: WAN interfaces ──► per-link quality items + triggers + graphs   │
  │   LLD: Sockets/HA ──► per-Socket items + triggers                      │
  │   LLD: BGP peers ──► per-peer routing items + triggers + graphs        │
  │                                                                        │
  │   Calculated: SLA 24h/7d/30d, health, inventory drift                  │
  │   Dashboard: 5 pages (Overview, Quality, Sites&Sockets, BGP, SLA)      │
  └───────────────────────────────────────────────────────────────────────┘
```

**Host model:** one Zabbix host represents one Cato account. Every site, WAN link and BGP peer becomes a set
of discovered items on that same host. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the trade-offs of
this model (and when to switch to *host prototypes*).

---

## Requirements

- **Zabbix 7.4** server or proxy, compiled with cURL (libcurl) support (required by the HTTP agent).
- A **Cato API key** (Cato Management Application → *Resources → API Keys*) with read access to
  **Sites**, **Sites Overview** and **Events**.
- Your **CMA account ID** (Cato Management Application → *Account Info*).
- Outbound HTTPS (443) from the Zabbix server/proxy to `api*.catonetworks.com`.

> **Security tip:** restrict the API key to the source IP of your Zabbix server/proxy directly in the CMA.

---

## Quick start

1. **Import the template**
   - In Zabbix: *Data collection → Templates → Import*.
   - Select [`templates/template_cato_networks_http.yaml`](templates/template_cato_networks_http.yaml).

2. **Create a host** (e.g. `Cato Account - ACME`) and link the template **Cato Networks by HTTP**.

3. **Set the macros** on the host:

   | Macro | Required | Example |
   |-------|:--------:|---------|
   | `{$CATO.API.KEY}` | ✅ | `abcdef123456...` (stored as *Secret text*) |
   | `{$CATO.ACCOUNT.ID}` | ✅ | `12345` |
   | `{$CATO.API.URL}` | ⛔ (default OK) | `https://api.us1.catonetworks.com/api/v1/graphql2` if your CMA has a region prefix |

4. **Wait one or two polling cycles**, then open the **Cato Networks - Overview** dashboard.

Full walkthrough (with screenshots checklist and permission matrix) in
[docs/INSTALL.md](docs/INSTALL.md).

---

## Regional endpoints

If your CMA URL contains a region prefix (e.g. `cc.us1.catonetworks.com`), update `{$CATO.API.URL}` accordingly:

| CMA prefix | API endpoint |
|------------|--------------|
| `cc.catonetworks.com` (none) | `https://api.catonetworks.com/api/v1/graphql2` |
| `cc.us1.catonetworks.com` | `https://api.us1.catonetworks.com/api/v1/graphql2` |

---

## What you get

- **5 API master items** · **27 account/SLA items** · **4 LLD rules** (23 item prototypes)
- **5 dashboard pages** · **17 user macros** · **2 value maps**
- Ready-to-tune triggers for site/Socket/BGP down, packet loss, jitter, RTT, low health and SLA breaches.

See the complete inventory in [docs/METRICS.md](docs/METRICS.md).

---

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/INSTALL.md](docs/INSTALL.md) | Step-by-step install, API key creation, permission matrix |
| [docs/METRICS.md](docs/METRICS.md) | Full list of items, LLD, triggers and macros |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design rationale, host model, rate-limiting math |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues (unsupported items, schema drift, 401/429) |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [SECURITY.md](SECURITY.md) | Reporting vulnerabilities |

---

## Compatibility notes

- Fields tagged **EA/Beta** by Cato (some BGP status fields) may differ per account. All JSON parsing in this
  template is **defensive**: a missing field does not break sibling items. If an item goes *Not supported*,
  validate the field name in the [Cato GraphQL Playground](https://knowledge.catonetworks.com/docs/connecting-to-the-cato-api-from-the-graphql-playground)
  and adjust the query. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
- `lastMilePacketLoss` and `tunnelAge` are **not** valid fields of `Metrics` (they exist only as *timeseries*
  metrics), so they are intentionally **not** requested to avoid unsupported items.

---

## Disclaimer

This is a **community project** and is **not affiliated with, endorsed by, or supported by Cato Networks Ltd.**
"Cato", "Cato Networks" and related marks belong to their respective owners. Use at your own risk.

## License

Released under the [MIT-0](LICENSE) license (MIT No Attribution) — free to use, modify and redistribute.
