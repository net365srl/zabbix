# Metrics Reference

Complete inventory of everything the **Cato Networks by HTTP** template collects.

**Summary:** 5 API master items · 27 account/SLA items · 4 LLD rules (23 item prototypes) ·
16 triggers / trigger prototypes · 5 graph prototypes · 17 macros · 2 value maps.

---

## 1. API master items (HTTP agent)

These items call the Cato GraphQL API and store the raw JSON that every dependent item parses.

| Key | Cato query | Default interval | Purpose |
|-----|------------|:---------------:|---------|
| `cato.snapshot.raw` | `accountSnapshot` | `60s` | Near real-time availability |
| `cato.metrics.raw` | `accountMetrics` | `5m` | Network quality (loss/jitter/RTT/health) |
| `cato.bgp.raw` | `accountSnapshot{…bgpStatus}` | `2m` | BGP peer status |
| `cato.entities.raw` | `entityLookup(type:site)` | `1h` | Authoritative site inventory |
| `cato.events.raw` | `eventsFeed` | `5m` | Event volume trending |

---

## 2. Account-level items

### Availability (from `accountSnapshot`)

| Key | Type | Description |
|-----|------|-------------|
| `cato.sites.total` | dependent | Number of sites in the snapshot |
| `cato.sites.connected` | dependent | Sites connected to the Cato Cloud |
| `cato.sites.disconnected` | dependent | Sites disconnected |
| `cato.sites.notactive` | dependent | Sites whose operational status ≠ `active` |
| `cato.hosts.total` | dependent | Sum of connected hosts across all sites |
| `cato.sockets.total` | dependent | Total Socket devices (includes HA pairs) |
| `cato.sockets.disconnected` | dependent | Sockets currently down — **trigger: HIGH** |

### Quality (from `accountMetrics`)

| Key | Type | Unit | Description |
|-----|------|------|-------------|
| `cato.traffic.total.down` | dependent | Bps | Aggregated downstream throughput |
| `cato.traffic.total.up` | dependent | Bps | Aggregated upstream throughput |
| `cato.rtt.avg` | dependent | ms | Average RTT across all links |
| `cato.loss.max` | dependent | % | Worst packet loss across all links |
| `cato.health.avg` | dependent | — | Average link health score (0–100) |

### Inventory & events

| Key | Type | Description |
|-----|------|-------------|
| `cato.sites.configured` | dependent | Configured sites (`entityLookup` total) |
| `cato.sites.missing` | calculated | `configured − snapshot` — **trigger: AVERAGE** (drift) |
| `cato.events.total` | dependent | Events over the events timeframe |
| `cato.events.errors` | dependent | Non-empty if `eventsFeed` returns errors |
| `cato.snapshot.errors` | dependent | Non-empty if `accountSnapshot` returns errors |

### SLA (calculated)

| Key | Type | Unit | Description |
|-----|------|------|-------------|
| `cato.sla.instant` | calculated | % | `100 × connected / total` (SLA basis) |
| `cato.sla.24h` | calculated | % | Rolling 24h availability — **trigger: HIGH** if `< {$CATO.SLA.TARGET}` |
| `cato.sla.7d` | calculated | % | Rolling 7-day availability |
| `cato.sla.30d` | calculated | % | Rolling 30-day availability |
| `cato.health.24h` | calculated | — | Rolling 24h average health score |

---

## 3. Low-Level Discovery

### 3.1 `Cato: Site discovery` — master `cato.snapshot.raw`

Macros: `{#SITE.ID}`, `{#SITE.NAME}`, `{#SITE.TYPE}`, `{#POP.NAME}`

| Item prototype | Trigger |
|----------------|---------|
| `cato.site.connectivity[{#SITE.ID}]` | HIGH — site disconnected |
| `cato.site.operational[{#SITE.ID}]` | WARNING — not `active` |
| `cato.site.pop[{#SITE.ID}]` | — |
| `cato.site.hostcount[{#SITE.ID}]` | — |
| `cato.site.connectedsince[{#SITE.ID}]` | — |

Graph prototype: *Connected hosts*.

### 3.2 `Cato: WAN interface discovery` — master `cato.metrics.raw`

Macros: `{#SITE.ID}`, `{#SITE.NAME}`, `{#IF.NAME}`

| Item prototype | Unit | Trigger |
|----------------|------|---------|
| `cato.if.bytes.down[…]` | Bps | — |
| `cato.if.bytes.up[…]` | Bps | — |
| `cato.if.bytes.total[…]` | Bps | — |
| `cato.if.loss.down[…]` | % | WARNING — `> {$CATO.LOSS.WARN}` |
| `cato.if.loss.up[…]` | % | WARNING — `> {$CATO.LOSS.WARN}` |
| `cato.if.jitter.down[…]` | ms | — |
| `cato.if.jitter.up[…]` | ms | WARNING — `> {$CATO.JITTER.WARN}` |
| `cato.if.rtt[…]` | ms | WARNING — `> {$CATO.RTT.WARN}` |
| `cato.if.discarded.down[…]` | pps | — |
| `cato.if.discarded.up[…]` | pps | — |
| `cato.if.health[…]` | — | WARNING — `< {$CATO.HEALTH.WARN}` |

Graph prototypes: *Traffic*, *Packet loss*, *Latency and jitter*.

### 3.3 `Cato: Socket / device discovery` — master `cato.snapshot.raw`

Macros: `{#SITE.ID}`, `{#SITE.NAME}`, `{#DEVICE.ID}`, `{#DEVICE.NAME}`, `{#HA.ROLE}`

| Item prototype | Trigger |
|----------------|---------|
| `cato.device.connected[{#DEVICE.ID}]` | HIGH — Socket down |
| `cato.device.uptime[{#DEVICE.ID}]` | INFO — rebooted (uptime < 10m) |
| `cato.device.version[{#DEVICE.ID}]` | INFO — firmware changed |

### 3.4 `Cato: BGP peer discovery` — master `cato.bgp.raw`

Macros: `{#SITE.ID}`, `{#SITE.NAME}`, `{#PEER.NAME}`, `{#PEER.IP}`, `{#PEER.ASN}`

| Item prototype | Unit | Trigger |
|----------------|------|---------|
| `cato.bgp.state[…]` | — | HIGH — not Established |
| `cato.bgp.advertised[…]` | routes | — |
| `cato.bgp.received[…]` | routes | AVERAGE — Established but 0 routes received |
| `cato.bgp.uptime[…]` | uptime | WARNING — recently flapped (< 5m) |

Graph prototype: *BGP routes (received vs advertised)*.

---

## 4. Macros

| Macro | Default | Description |
|-------|---------|-------------|
| `{$CATO.API.URL}` | `https://api.catonetworks.com/api/v1/graphql2` | GraphQL endpoint (add region prefix if needed) |
| `{$CATO.API.KEY}` | *(secret)* | Cato API key |
| `{$CATO.ACCOUNT.ID}` | — | CMA account ID |
| `{$CATO.SNAPSHOT.INTERVAL}` | `60s` | accountSnapshot polling |
| `{$CATO.METRICS.INTERVAL}` | `5m` | accountMetrics polling |
| `{$CATO.METRICS.TIMEFRAME}` | `last.PT5M` | accountMetrics timeframe |
| `{$CATO.BGP.INTERVAL}` | `2m` | BGP status polling |
| `{$CATO.INVENTORY.INTERVAL}` | `1h` | entityLookup polling |
| `{$CATO.EVENTS.INTERVAL}` | `5m` | events polling |
| `{$CATO.EVENTS.TIMEFRAME}` | `last.PT5M` | events timeframe |
| `{$CATO.LOSS.WARN}` | `3` | Packet loss warning (%) |
| `{$CATO.JITTER.WARN}` | `30` | Jitter warning (ms) |
| `{$CATO.RTT.WARN}` | `150` | RTT warning (ms) |
| `{$CATO.HEALTH.WARN}` | `70` | Link health warning (below) |
| `{$CATO.SLA.TARGET}` | `99.9` | Availability SLA objective (%) |
| `{$CATO.SITE.NAME.MATCHES}` | `.*` | Discover sites matching regex |
| `{$CATO.SITE.NAME.NOT_MATCHES}` | `CHANGE_IF_NEEDED` | Exclude sites matching regex |

---

## 5. Value maps

| Value map | 0 | 1 |
|-----------|---|---|
| `Cato connectivity` | Disconnected | Connected |
| `Cato BGP state` | Not established | Established |

---

## 6. Dashboard pages

1. **Overview** — KPI tiles, sites pie chart, throughput graph, site & Socket honeycombs, problems.
2. **Network quality** — throughput, RTT & loss gauges and trends.
3. **Sites & sockets** — full-size connectivity honeycombs.
4. **BGP / dynamic routing** — BGP state honeycomb, BGP problems, dynamic routes learned.
5. **SLA & availability** — 24h/7d/30d availability, SLA gauge, availability & health history.
