# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2026-08-18

### Fixed
- Regenerated all 80 element identifiers as **RFC 4122 UUIDv4** values. Previous builds used random hex
  strings that failed Zabbix import validation with `Invalid parameter "/…/uuid": UUIDv4 is expected.`

### Changed
- Template `version` bumped to 2.0.1; no functional changes versus 2.0.0.

## [2.0.0] - 2026-08-18

### Added
- **BGP / dynamic routing** monitoring via a dedicated master item and `Cato: BGP peer discovery` LLD:
  peer state, advertised/received routes and session uptime, with defensive parsing for non-BGP accounts.
- **SLA & availability** items: `cato.sla.instant` plus rolling `24h`, `7d`, `30d` calculated averages and a
  24h SLA-breach trigger driven by `{$CATO.SLA.TARGET}`.
- **entityLookup** master item + `cato.sites.configured` and `cato.sites.missing` (inventory drift detection).
- **eventsFeed** master item + `cato.events.total` event-volume trending and `cato.events.errors`.
- **Health score** metric (`health`) per WAN link and as an account average, with a low-health trigger.
- New dashboard pages: **BGP / dynamic routing** and **SLA & availability** (total 5 pages).
- New macros: `{$CATO.BGP.INTERVAL}`, `{$CATO.INVENTORY.INTERVAL}`, `{$CATO.EVENTS.INTERVAL}`,
  `{$CATO.EVENTS.TIMEFRAME}`, `{$CATO.HEALTH.WARN}`, `{$CATO.SLA.TARGET}`.
- New value map `Cato BGP state`.

### Changed
- Enriched the **Overview** dashboard with a second KPI row, pie chart, throughput graph and honeycombs.
- Extended the WAN interface LLD with `bytesTotal`, `packetsDiscardedDownstream/Upstream`.

## [1.0.0] - 2026-08-18

### Added
- Initial release. Zabbix 7.4 HTTP-agent template for Cato Networks.
- Master items `accountSnapshot` (availability) and `accountMetrics` (quality).
- LLD for **sites**, **WAN interfaces** and **Sockets/HA**.
- Per-site and per-link items, triggers and graph prototypes.
- Single-page **Cato Networks - Overview** dashboard.
- 11 user macros and the `Cato connectivity` value map.

[2.0.1]: https://github.com/OWNER/zabbix-cato-networks/releases/tag/v2.0.1
[2.0.0]: https://github.com/OWNER/zabbix-cato-networks/releases/tag/v2.0.0
[1.0.0]: https://github.com/OWNER/zabbix-cato-networks/releases/tag/v1.0.0
