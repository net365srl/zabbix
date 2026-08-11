<!--
  Thank you for your contribution! 🙌
  Please fill in the sections below. PRs that keep one device / one logical change
  per pull request are reviewed faster. See CONTRIBUTING.md for full guidelines.
-->

## Description

<!-- What does this PR change and why? -->


## Type of change

- [ ] 🐛 Bug fix (correcting an OID, expression, threshold or import error)
- [ ] ✨ New feature (new item, trigger, graph or dashboard widget)
- [ ] 🌐 New device template
- [ ] 📖 Documentation only
- [ ] ♻️ Refactor (no behaviour change)

## Affected template(s)

- [ ] HPE Instant On 1930 by SNMP
- [ ] Netgear GS748Tv5 by SNMP
- [ ] New / other: <!-- name -->

## Tested on

| Field | Value |
|-------|-------|
| Switch model | <!-- e.g. Aruba Instant On 1930 JL683A --> |
| Firmware version | <!-- e.g. 2.9.0.4 --> |
| Zabbix version | <!-- e.g. 7.4.0 --> |
| SNMP version | <!-- v2c / v3 --> |

## Validation checklist

- [ ] The YAML **imports cleanly** into Zabbix 7.4 (*Create new* / *Update existing*).
- [ ] All items collect data on **real hardware**.
- [ ] Discovery finds the expected interfaces; prototypes, graphs and dashboard render correctly.
- [ ] Triggers **fire and recover** as intended (especially the link‑down transition logic).
- [ ] No private or sensitive data is present (I ran `grep` on my changes).
- [ ] Template `README.md` and the root tables are updated (for new devices/features).
- [ ] I followed the [template conventions](../CONTRIBUTING.md#template-conventions).

## Additional notes

<!-- Anything reviewers should know: caveats, follow-ups, screenshots, etc. -->
