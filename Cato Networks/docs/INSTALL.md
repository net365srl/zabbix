# Installation Guide

This guide walks you through deploying the **Cato Networks by HTTP** template on Zabbix 7.4.

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| Zabbix **7.4** server or proxy | The HTTP agent runs on the server, or on the proxy if the host is proxied |
| cURL (libcurl) support | Zabbix server/proxy must be compiled with cURL (default in official packages) |
| Outbound HTTPS (443) | From the Zabbix server/proxy to `api*.catonetworks.com` |
| Cato API key | See section 2 |
| CMA account ID | CMA → *Account Info* (the number in the CMA URL, e.g. `.../#!/12345/topology` → `12345`) |

---

## 2. Create the Cato API key

1. Sign in to the **Cato Management Application (CMA)**.
2. Go to **Resources → API Keys** and create a new key.
3. Assign a role/permissions with **read** access to the surfaces the template uses (see the matrix below).
4. **Restrict the key to the source IP** of your Zabbix server/proxy.
5. Copy the key value — you will paste it into `{$CATO.API.KEY}`.

### Permission matrix

| Template feature | Master item | Cato permission needed |
|------------------|-------------|------------------------|
| Availability (sites, Sockets, hosts) | `cato.snapshot.raw` | Sites / Sites Overview |
| Network quality (loss/jitter/RTT/health) | `cato.metrics.raw` | Sites Overview (or SDP Users Overview / Users & User Groups) |
| BGP / dynamic routing | `cato.bgp.raw` | Sites (BGP status) |
| Inventory & drift | `cato.entities.raw` | Accounts / Sites |
| Event trending | `cato.events.raw` | Events |

> If a permission is missing, only the related items go *Not supported* — the rest of the template keeps
> working. `cato.snapshot.errors` and `cato.events.errors` surface the API error message for quick diagnosis.

---

## 3. Import the template

1. In Zabbix: **Data collection → Templates → Import**.
2. Choose the file `templates/template_cato_networks_http.yaml`.
3. Keep the default *Create new* / *Update existing* rules and click **Import**.

The template **Cato Networks by HTTP** appears under the template group **Templates/Network devices**.

---

## 4. Create and configure the host

1. **Data collection → Hosts → Create host**.
2. **Host name**: e.g. `Cato Account - ACME`.
3. **Templates**: link **Cato Networks by HTTP**.
4. **Host groups**: any group you use (e.g. `Cato`).
5. No agent interface is required (HTTP agent connects out to the Cato API).
6. Open the **Macros** tab → *Inherited and host macros* and set:

   | Macro | Value |
   |-------|-------|
   | `{$CATO.API.KEY}` | your API key (type: **Secret text**) |
   | `{$CATO.ACCOUNT.ID}` | your CMA account ID |
   | `{$CATO.API.URL}` | only if you use a regional endpoint (see README) |

7. Click **Add** / **Update**.

---

## 5. Verify

- Go to **Monitoring → Latest data**, filter by your host.
- Within one or two polling cycles you should see `Cato: Sites total`, `Cato: Sites connected`, etc.
- If items are empty, check `Cato: API errors (snapshot)` — a non-empty value means the API returned an
  `errors[]` array (usually a permission or account-ID issue).
- Open **Monitoring → Dashboards → Cato Networks - Overview**.

---

## 6. Tune thresholds (optional)

Adjust these macros on the host to match your SLAs:

| Macro | Default | Meaning |
|-------|---------|---------|
| `{$CATO.LOSS.WARN}` | `3` | Packet loss warning (%) |
| `{$CATO.JITTER.WARN}` | `30` | Jitter warning (ms) |
| `{$CATO.RTT.WARN}` | `150` | RTT warning (ms) |
| `{$CATO.HEALTH.WARN}` | `70` | Link health warning (score below) |
| `{$CATO.SLA.TARGET}` | `99.9` | 24h availability SLA objective (%) |

Polling intervals (`{$CATO.*.INTERVAL}`) and timeframes (`{$CATO.*.TIMEFRAME}`) can also be tuned to balance
freshness against Cato API rate limits — see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 7. Filtering which sites are monitored

- `{$CATO.SITE.NAME.MATCHES}` (default `.*`) — only discover sites whose name matches this regex.
- `{$CATO.SITE.NAME.NOT_MATCHES}` (default `CHANGE_IF_NEEDED`) — exclude sites whose name matches this regex.

Set these at host or template level to scope discovery in large accounts.
