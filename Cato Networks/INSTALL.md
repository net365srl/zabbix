# Installation Guide

Deploy the **Cato Networks by HTTP** template (v2.0.7) on Zabbix 7.4.

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| Zabbix **7.4** server or proxy | HTTP agent runs on the server, or on the proxy if the host is proxied |
| cURL (libcurl) support | Default in official Zabbix packages |
| Outbound HTTPS (443) | From the Zabbix server/proxy to `api*.catonetworks.com` |
| A Cato **admin** in the CMA | With permission to generate API keys |
| Cato API key | See [section 2](#2-create-the-cato-api-key) |
| CMA account ID | See [section 3](#3-find-your-account-id) |

---

## 2. Create the Cato API key

Cato offers **two kinds of API key**. For monitoring you want a **read-only** key.

| Key type | Tied to | Best for |
|----------|---------|----------|
| **Service API Key** (recommended) | a *Service Principal* (a non-login API identity) | integrations, unattended monitoring |
| **Admin API Key** | your personal admin login | quick tests; deactivated if your admin is disabled |

> **Recommendation:** use a **Service API Key** with **read-only** permissions, restricted to the Zabbix source IP.

### Option A — Service API Key (recommended)

**Step 1 — Create a Service Principal** (skip if you already have one)

1. **Account → Administrators → New**.
2. Select **Create New**, then **Create as Service Principal**.
3. **Service Principal name**: this is just a **label** to identify the API identity in the *Administrators*
   page — it is not a technical value and has no format requirements. Use something descriptive, e.g.
   `svc-zabbix-monitoring`.
4. Assign a **read-only role** (Viewer), scoped to the sites you want to monitor. *(This role — not the name —
   is what the API key inherits, so make sure it is read-only.)*
5. Click **Apply**. The Service Principal is created and activated.

**Step 2 — Generate the Service API Key**

1. **Resources → Service API Keys → New**.
2. Select the **Service Principal** you created.
3. Enter a **Key Name** (e.g. `zabbix-cato`).
4. Select **Downgrade to View** (read-only). ✅
5. *(Recommended)* **Allow access from IPs → Specific IP list** → the Zabbix server/proxy public IP.
6. *(Optional)* Set an **Expires at** date and rotate before it lapses.
7. **Apply**, then **copy the key value** from the pop-up — it is shown **only once** — and click **OK**.

### Option B — Admin API Key (personal / quick)

1. **Resources → Admin API Keys → New**.
2. **Key Name** → **Downgrade to View** (read-only) → *(optional)* restrict source IP → *(optional)* expiry.
3. **Apply**, copy the key value (shown once), **OK**.

> ⚠️ **The key value is displayed only once.** If lost, revoke it (delete icon) and create a new one.

### Enable the Event Feed (only if you want the events metric)

The `Cato: Get events summary` item uses `eventsFeed`, which requires the Event Feed to be on:

1. **Administration → API & Integrations → Events Integration**.
2. Enable **Enable integration with Cato events**. Wait ~30 minutes for the queue to populate.

If you don’t need it, simply disable the `cato.events.raw` item.

### Permission matrix

| Template feature | Master item | Cato permission needed |
|------------------|-------------|------------------------|
| Availability (sites, Sockets, hosts) | `cato.snapshot.raw` | Sites / Sites Overview (read) |
| Network quality (loss/jitter/RTT) | `cato.metrics.raw` | Sites Overview (read) |
| Inventory & drift | `cato.entities.raw` | Accounts / Sites (read) |
| Event trending | `cato.events.raw` | Events (read) **+ Event Feed enabled** |
| BGP (disabled by default) | `cato.bgp.raw` | Sites (BGP status, read) |

> A missing permission only makes the related items go *Not supported* — the rest keeps working. Each master
> item has a matching **“API errors”** sentinel (`cato.*.errors`) that shows the exact API message.

---

## 3. Find your Account ID

Your **CMA account ID** is the number in the Cato Management Application URL. The account subdomain does not
matter:

```
https://company.cc.catonetworks.com/#!/26/topology
                                       ^^
                                   account ID = 26
```

Paste this into `{$CATO.ACCOUNT.ID}`.

---

## 4. Import the template

1. **Data collection → Templates → Import**.
2. Choose `templates/template_cato_networks_http.yaml`.
3. Keep the default *Create new* / *Update existing* rules and click **Import**.

The template **Cato Networks by HTTP** appears under **Templates/Network devices**.

> **Updating from a previous version?** On import, tick **Update existing** for *Templates, Items, Triggers,
> Discovery rules and Dashboards*. Your host macros (API key, account ID) are kept.

---

## 5. Create and configure the host

1. **Data collection → Hosts → Create host**.
2. **Host name**: e.g. `Cato Account - ACME`.
3. **Templates**: link **Cato Networks by HTTP**.
4. **Host groups**: any group (e.g. `Cato`). No agent interface is required.
5. Open the **Macros** tab and set:

   | Macro | Value |
   |-------|-------|
   | `{$CATO.API.KEY}` | your API key value (type: **Secret text**) |
   | `{$CATO.ACCOUNT.ID}` | your CMA account ID |
   | `{$CATO.API.URL}` | only if you use a regional endpoint (see below) |

6. Click **Add** / **Update**.

### Regional endpoint

Only the part between `cc.` and `catonetworks.com` selects the region (the account subdomain is irrelevant):

| CMA URL | `{$CATO.API.URL}` |
|---------|-------------------|
| `company.cc.catonetworks.com` | `https://api.catonetworks.com/api/v1/graphql2` *(default)* |
| `company.cc.us1.catonetworks.com` | `https://api.us1.catonetworks.com/api/v1/graphql2` |

---

## 6. Verify

1. **Monitoring → Latest data**, filter by your host.
2. Within one or two cycles you should see `Cato: Sites total`, `Cato: Sites connected`, etc.
3. If items are empty, check the sentinels:
   `Cato: API errors (snapshot)`, `Cato: Metrics API errors`, `Cato: Entity inventory API errors`,
   `Cato: Events API errors`. A non-empty value means the API returned an error (permission, IP restriction,
   account ID, or an EA/Beta field).
4. Open **Monitoring → Dashboards → Cato Networks - Overview**.

The dashboard has 5 pages:

- **Overview** — account KPIs, sites pie, throughput, site & Socket honeycombs, problems.
- **Network quality (per site/link)** — throughput/RTT/jitter/loss with **one line per site/link**.
- **Sites & sockets** — full-size honeycombs + connected-hosts-per-site graph.
- **BGP / dynamic routing** — populated only if you enable the BGP module.
- **SLA & availability** — 24h/7d/30d availability + history.

---

## 7. Tune thresholds (optional)

| Macro | Default | Meaning |
|-------|---------|---------|
| `{$CATO.LOSS.WARN}` | `3` | Packet loss warning (%) |
| `{$CATO.JITTER.WARN}` | `30` | Jitter warning (ms) |
| `{$CATO.RTT.WARN}` | `150` | RTT warning (ms) |
| `{$CATO.SLA.TARGET}` | `99.9` | 24h availability SLA objective (%) |

Polling intervals (`{$CATO.*.INTERVAL}`) and `{$CATO.METRICS.TIMEFRAME}` balance freshness vs. API rate limits.

---

## 8. Filtering which sites are monitored

- `{$CATO.SITE.NAME.MATCHES}` (default `.*`) — only discover sites whose name matches this regex.
- `{$CATO.SITE.NAME.NOT_MATCHES}` (default `CHANGE_IF_NEEDED`) — exclude sites whose name matches this regex.

---

## 9. Enabling BGP monitoring (optional)

BGP is **disabled by default** (its status field is not universal across accounts). To enable:

1. In the [GraphQL Playground](https://knowledge.catonetworks.com/docs/connecting-to-the-cato-api-from-the-graphql-playground),
   run introspection and find the BGP status query valid for **your** account.
2. Replace the query in the **`Cato: Get BGP status`** item.
3. Enable the **`Cato: Get BGP status`** item **and** the **`Cato: BGP peer discovery`** LLD rule.

---

## Troubleshooting quick reference

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| A `*.errors` item is non-empty | API returned an error | Read the message: permission / IP / account ID / field |
| `Cannot query field "X"` | EA/Beta field not on your account | Remove/adjust the field in the master item’s query |
| HTTP 401 / 403 | Bad/expired key or source IP not allowed | Re-issue key; whitelist Zabbix IP in the CMA |
| HTTP 429 | Rate limited | Increase `{$CATO.*.INTERVAL}`; shorten `{$CATO.METRICS.TIMEFRAME}` |
| Empty on regional CMA | Wrong endpoint | Set `{$CATO.API.URL}` to your region |
| SLA items “not supported” at first | History not accumulated yet | Wait a couple of cycles |
