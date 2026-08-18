# Installation Guide

This guide walks you through deploying the **Cato Networks by HTTP** template on Zabbix 7.4.

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| Zabbix **7.4** server or proxy | The HTTP agent runs on the server, or on the proxy if the host is proxied |
| cURL (libcurl) support | Zabbix server/proxy must be compiled with cURL (default in official packages) |
| Outbound HTTPS (443) | From the Zabbix server/proxy to `api*.catonetworks.com` |
| A Cato **admin** account in the CMA | With permission to generate API keys |
| Cato API key | See [section 2](#2-create-the-cato-api-key) |
| CMA account ID | See [section 3](#3-find-your-account-id) |

---

## 2. Create the Cato API key

Cato offers **two kinds of API key**. For a monitoring integration like this one you want a **read-only**
key. Pick the option that fits your organization:

| Key type | Tied to | Best for | How permissions work |
|----------|---------|----------|----------------------|
| **Service API Key** (recommended) | a *Service Principal* (a non-login API identity) | integrations, automation, unattended monitoring | inherits the Service Principal's role |
| **Admin API Key** | your personal admin login | quick tests, personal workflows | inherits *your* admin role; deactivated if your admin is disabled/deleted |

> **Recommendation:** use a **Service API Key** with **read-only (Viewer / "Downgrade to View")** permissions,
> restricted to the Zabbix source IP. It is decoupled from any personal login and survives admin changes.

### Option A — Service API Key (recommended)

**Step 1 — Create a Service Principal (skip if you already have one)**

1. In the Cato Management Application, go to **Account → Administrators**.
2. Click **New**.
3. Select **Create New**, then choose **Create as Service Principal**.
4. Enter the general settings (name, e.g. `zabbix-monitoring`).
5. Assign a **read-only role** (Viewer), scoped to the sites you want to monitor.
6. Click **Apply**. The Service Principal is created and activated.

**Step 2 — Generate the Service API Key**

1. Go to **Resources → Service API Keys**.
2. Click **New**. The *Create API Key* panel opens.
3. Select the **Service Principal** you created.
4. Enter a **Key Name** (e.g. `zabbix-cato`).
5. Select **Downgrade to View** to force read-only permissions. ✅ *(recommended)*
6. *(Optional but recommended)* Under **Allow access from IPs**, select **Specific IP list** and enter the
   **Zabbix server/proxy public IP** (or CIDR).
7. *(Optional)* Set an **Expires at** date and remember to rotate the key before it lapses.
8. Click **Apply**.
9. A pop-up shows the **API key value**. **Copy it now and store it securely** — it cannot be retrieved again.
10. Click **OK**.

### Option B — Admin API Key (personal / quick)

1. Go to **Resources → Admin API Keys**.
2. Click **New**.
3. Enter a **Key Name**.
4. Select **Downgrade to View** for read-only. ✅ *(recommended)*
5. *(Optional)* **Allow access from IPs → Specific IP list** → your Zabbix source IP.
6. *(Optional)* Set an **Expires at** date.
7. Click **Apply**, then **copy the key value** from the pop-up (shown only once) and click **OK**.

> ⚠️ **The key value is displayed only once.** If you lose it, revoke the key and create a new one
> (*Resources → Admin/Service API Keys → delete icon*).

### Enable the Event Feed (only if you want the events metrics)

The `Cato: Get events summary` item uses `eventsFeed`, which requires the **Event Feed** to be switched on:

1. In the navigation menu, open **API Access Management** (under *System* / *Administration*, depending on
   your CMA version).
2. Enable **Event Feed Enabled**.

If you don't need event trending, you can leave this off and simply disable the `cato.events.raw` item.

### Permission matrix

| Template feature | Master item | Cato permission needed |
|------------------|-------------|------------------------|
| Availability (sites, Sockets, hosts) | `cato.snapshot.raw` | Sites / Sites Overview (read) |
| Network quality (loss/jitter/RTT/health) | `cato.metrics.raw` | Sites Overview (read) |
| BGP / dynamic routing | `cato.bgp.raw` | Sites (BGP status, read) |
| Inventory & drift | `cato.entities.raw` | Accounts / Sites (read) |
| Event trending | `cato.events.raw` | Events (read) **+ Event Feed enabled** |

> A missing permission only makes the related items go *Not supported* — the rest keeps working.
> `cato.snapshot.errors` and `cato.events.errors` surface the exact API error for quick diagnosis.

---

## 3. Find your Account ID

Your **CMA account ID** is the number in the Cato Management Application URL:

```
https://cc.catonetworks.com/#!/26/topology
                              ^^
                          account ID = 26
```

You will paste this into `{$CATO.ACCOUNT.ID}`.

---

## 4. Import the template

1. In Zabbix: **Data collection → Templates → Import**.
2. Choose the file `templates/template_cato_networks_http.yaml`.
3. Keep the default *Create new* / *Update existing* rules and click **Import**.

The template **Cato Networks by HTTP** appears under **Templates/Network devices**.

---

## 5. Create and configure the host

1. **Data collection → Hosts → Create host**.
2. **Host name**: e.g. `Cato Account - ACME`.
3. **Templates**: link **Cato Networks by HTTP**.
4. **Host groups**: any group you use (e.g. `Cato`).
5. No agent interface is required (the HTTP agent connects out to the Cato API).
6. Open the **Macros** tab → *Inherited and host macros* and set:

   | Macro | Value |
   |-------|-------|
   | `{$CATO.API.KEY}` | your API key value (type: **Secret text**) |
   | `{$CATO.ACCOUNT.ID}` | your CMA account ID |
   | `{$CATO.API.URL}` | only if you use a regional endpoint (see below) |

7. Click **Add** / **Update**.

### Regional endpoint

If your CMA URL has a region prefix, set `{$CATO.API.URL}` accordingly:

| CMA prefix | API endpoint |
|------------|--------------|
| `cc.catonetworks.com` (none) | `https://api.catonetworks.com/api/v1/graphql2` |
| `cc.us1.catonetworks.com` | `https://api.us1.catonetworks.com/api/v1/graphql2` |

---

## 6. Verify

1. **Monitoring → Latest data**, filter by your host.
2. Within one or two polling cycles you should see `Cato: Sites total`, `Cato: Sites connected`, etc.
3. If items are empty, check `Cato: API errors (snapshot)` — a non-empty value means the API returned an
   `errors[]` array (usually a permission, IP-restriction or account-ID issue).
4. Open **Monitoring → Dashboards → Cato Networks - Overview**.

---

## 7. Tune thresholds (optional)

| Macro | Default | Meaning |
|-------|---------|---------|
| `{$CATO.LOSS.WARN}` | `3` | Packet loss warning (%) |
| `{$CATO.JITTER.WARN}` | `30` | Jitter warning (ms) |
| `{$CATO.RTT.WARN}` | `150` | RTT warning (ms) |
| `{$CATO.HEALTH.WARN}` | `70` | Link health warning (score below) |
| `{$CATO.SLA.TARGET}` | `99.9` | 24h availability SLA objective (%) |

Polling intervals (`{$CATO.*.INTERVAL}`) and timeframes (`{$CATO.*.TIMEFRAME}`) can be tuned to balance
freshness against Cato API rate limits — see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 8. Filtering which sites are monitored

- `{$CATO.SITE.NAME.MATCHES}` (default `.*`) — only discover sites whose name matches this regex.
- `{$CATO.SITE.NAME.NOT_MATCHES}` (default `CHANGE_IF_NEEDED`) — exclude sites whose name matches this regex.
