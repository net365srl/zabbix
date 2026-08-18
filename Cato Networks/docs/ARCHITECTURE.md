# Architecture & Design Notes

## Why HTTP agent (not SNMP)

Cato Networks is a cloud-native SASE platform. It **does not expose an SNMP agent or MIBs**. The only
supported integration surface is the **Cato GraphQL API** over HTTPS (POST with an `x-api-key` header).
Zabbix's **HTTP agent** item type is therefore the correct transport; SNMP is not an option.

## Master item + LLD + dependent items

Instead of one API call per metric, the template issues a **single API call per data source** and then uses
**dependent items** to extract every value from the stored JSON. Low-Level Discovery turns arrays (sites,
interfaces, Sockets, BGP peers) into per-entity items automatically.

Benefits:

- **Few API calls** → stays within Cato rate limits.
- **Auto-scaling** → new sites/links/peers are discovered without manual work; removed ones age out.
- **Resilience** → parsing is defensive; a missing field affects only its own item.

```
API JSON (master item)
      │  (stored once per cycle)
      ├── LLD rule ──► discovers entities ──► item prototypes (dependent)
      └── dependent items ──► JSONPath / JavaScript preprocessing ──► values
```

## Host model: one host = one Cato account

Every site, WAN link and BGP peer is a **discovered item on a single Zabbix host** that represents the whole
Cato account.

### Pros
- Simple to deploy and link.
- One place for credentials and macros.
- Account-wide KPIs and SLA are trivial to compute.

### Cons / things to watch
1. **Item density.** Large accounts (100+ sites, multiple WAN links each) produce thousands of items on one
   host; preprocessing and history concentrate there. Monitor the Zabbix preprocessing queue.
2. **Single auth point.** If the API key expires or the source IP is not whitelisted, the whole account stops
   collecting. `cato.snapshot.errors` / `cato.events.errors` surface the reason.
3. **No per-site isolation of permissions/actions** except via **tags** (the template tags items with
   `component` and `site`). If you need per-customer RBAC or separate escalation, switch to **host prototypes**
   (one Zabbix host per site). That is cleaner for MSP/multi-tenant setups but more complex; it is intentionally
   **not** the default here.

## Rate limiting & bucket math (`accountMetrics`)

Cato enforces a hard limit of **100,000 returned items per `accountMetrics` query**, computed as:

```
(sites + VPN users) × metrics × buckets  <  100,000
```

This template requests **aggregated metrics over a short timeframe** (`last.PT5M`) with **no multi-bucket
timeseries**, so the `buckets` factor is effectively 1 and you stay far below the limit even with hundreds of
sites. If you widen `{$CATO.METRICS.TIMEFRAME}` or add timeseries, recompute the minimum granularity.

### Suggested intervals

| Data source | Macro | Default | Rationale |
|-------------|-------|---------|-----------|
| Snapshot | `{$CATO.SNAPSHOT.INTERVAL}` | `60s` | Availability needs to be fresh |
| Metrics | `{$CATO.METRICS.INTERVAL}` | `5m` | Quality trends; heavier query |
| BGP | `{$CATO.BGP.INTERVAL}` | `2m` | Routing changes are relatively slow |
| Inventory | `{$CATO.INVENTORY.INTERVAL}` | `1h` | Configuration rarely changes |
| Events | `{$CATO.EVENTS.INTERVAL}` | `5m` | Volume trending |

## Defensive parsing

- JavaScript preprocessing wraps lookups so a missing site/interface/peer throws a clean per-item error
  without breaking siblings.
- The BGP discovery `try/catch`es the whole parse: accounts without BGP simply yield **no** peer prototypes.
- Fields known to be **timeseries-only** in the Cato schema (`lastMilePacketLoss`, `tunnelAge`) are **not**
  requested inside `metrics{}` to avoid `GRAPHQL_VALIDATION_FAILED` and unsupported items.

## Extending the template

Good candidates to add (kept out of the default to stay lean):
- `xdr.stories` — security incident correlation.
- `auditFeed` — admin/config change auditing.
- `appStats` / `appStatsTimeSeries` — application usage analytics.
- **Host prototypes** variant for one-host-per-site deployments.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to propose these.
