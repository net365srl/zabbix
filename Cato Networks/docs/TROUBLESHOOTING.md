# Troubleshooting

## Import fails: `Invalid parameter "/…/uuid": UUIDv4 is expected`

Every element (template, item, LLD, trigger, dashboard, value map) needs an **RFC 4122 UUIDv4**. If you edited
the YAML by hand and added elements with invalid IDs, Zabbix rejects the import.

- **Fix:** leave the `uuid:` field out and let Zabbix generate one on save, or generate a valid one:
  ```bash
  python3 -c "import uuid; print(uuid.uuid4().hex)"
  # or
  uuidgen | tr -d '-'
  ```
- A valid UUIDv4 has the version nibble `4` (13th hex char) and a variant nibble in `8/9/a/b` (17th hex char).

## An item is *Not supported*

The Cato schema evolves; some fields are EA/Beta and may differ per account.

1. Open **Monitoring → Latest data**, hover the item, read the error.
2. If it is a `GRAPHQL_VALIDATION_FAILED` / `Cannot query field …` error, the field name is not valid for your
   account. Open the [Cato GraphQL Playground](https://knowledge.catonetworks.com/docs/connecting-to-the-cato-api-from-the-graphql-playground),
   run **introspection**, and adjust the query in the corresponding master item.
3. Remember: `lastMilePacketLoss` and `tunnelAge` are **timeseries-only** metrics — they are not valid inside
   `metrics{}` and are intentionally excluded.

## No data at all / HTTP errors

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `cato.snapshot.errors` non-empty | Wrong account ID or missing permission | Verify `{$CATO.ACCOUNT.ID}` and the API key role |
| HTTP `401` / `403` | Bad/expired API key, or source IP not allowed | Re-issue the key; whitelist the Zabbix source IP in the CMA |
| HTTP `429` | Rate limited | Increase `{$CATO.*.INTERVAL}` values; shorten `{$CATO.METRICS.TIMEFRAME}` |
| Timeout | Network/firewall to `api*.catonetworks.com:443` | Open outbound HTTPS from the Zabbix server/proxy |
| Empty on regional CMA | Wrong endpoint | Set `{$CATO.API.URL}` to your region (e.g. `api.us1…`) |

## BGP page is empty

- BGP items only appear for sites that **have BGP peers**. Accounts without BGP correctly discover **no**
  peers (defensive parsing).
- If you *do* run BGP but see nothing, verify the `cato.bgp.raw` item returns peers in the Playground and that
  the BGP status fields match the query (some are EA/Beta).

## SLA values look wrong right after import

The SLA items are **calculated averages over 24h/7d/30d**. They need history to accumulate; give them time.
`cato.sla.instant` should populate within the first couple of snapshot cycles.

## Firmware-change / flap triggers fire on first run

`change()`-based and low-uptime triggers can fire once as history seeds. They self-clear on the next normal
poll; for firmware changes the trigger is set to **manual close** by design.

## Verifying the YAML locally

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('templates/template_cato_networks_http.yaml')); print('YAML OK')"
```
