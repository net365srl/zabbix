# Contributing Guidelines

First off, thank you for taking the time to contribute! 🎉

This project is a collection of **community Zabbix SNMP templates** for smart‑managed switches. Contributions of all kinds are welcome: bug fixes, new device families, additional items/triggers, dashboard improvements, and documentation.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Ways to Contribute](#ways-to-contribute)
3. [Before You Start](#before-you-start)
4. [Reporting Bugs](#reporting-bugs)
5. [Requesting a New Device](#requesting-a-new-device)
6. [Submitting a Pull Request](#submitting-a-pull-request)
7. [Template Conventions](#template-conventions)
8. [Validation Checklist](#validation-checklist)
9. [Commit & Branch Naming](#commit--branch-naming)
10. [Privacy & Legal](#privacy--legal)

---

## Code of Conduct

Be respectful, constructive and patient. We welcome contributors of every background and experience level. Harassment, personal attacks or discriminatory language will not be tolerated. Assume good faith and help others learn.

## Ways to Contribute

- 🐛 **Report a bug** — an item returns "Not supported", a wrong value, or an import error.
- 🌐 **Request or add a new device** — a switch model not yet covered.
- ✨ **Improve a template** — new items, triggers, graphs, or better thresholds.
- 📖 **Improve documentation** — clarify a README, fix a typo, add examples.
- 🧪 **Test on real hardware** — confirm compatibility and report firmware/model results.

## Before You Start

- **Search existing issues and pull requests** to avoid duplicating work.
- For anything larger than a small fix, **open an issue first** to discuss the approach.
- By contributing, you agree that your contribution is licensed under the project's **MIT License**.

## Reporting Bugs

When opening an **issue**, please include:

- Switch **model** and exact **firmware version**.
- The **Zabbix version** you are running (e.g. 7.4).
- **What you expected** vs. **what happened** (items "Not supported", wrong values, import errors, …).
- A short **SNMP walk** snippet for any OID‑related problem, for example:
  ```bash
  snmpwalk -v2c -c public <switch-ip> 1.3.6.1.2.1.1        # system group
  snmpwalk -v2c -c public <switch-ip> <vendor-enterprise-oid>
  ```
- **Redact** community strings, IP addresses and serial numbers before posting.

## Requesting a New Device

Adding a switch family is one of the most valuable contributions. Please provide:

- Vendor, model and firmware/OS.
- The device **`sysObjectID`** and **`sysDescr`**.
- A full or partial **SNMP walk** of the vendor enterprise branch (CPU, memory, inventory, sensors).
- Whether it uses the standard **IF‑MIB** (`ifTable`/`ifXTable`) for interfaces (almost all do).

With that information a template can be drafted following the [conventions](#template-conventions) below.

## Submitting a Pull Request

1. **Fork** the repository and create a topic branch:
   `git checkout -b feat/<device>-<short-description>`.
2. Make your changes following the [Template Conventions](#template-conventions).
3. **Validate** the template locally (see the [Validation Checklist](#validation-checklist)).
4. Commit with a clear message ([Conventional Commits](#commit--branch-naming) style appreciated).
5. Open a PR against `main` and fill in the description:
   - **What changed** and **why**.
   - **Model / firmware** it was tested on.
   - **How** you validated it (import, discovery, triggers).

Keep PRs focused: one device or one logical change per pull request makes review faster.

## Template Conventions

To stay consistent with the existing templates:

- **Numeric OIDs only** — never require external MIB files to be loaded into Zabbix.
- **Naming:**
  - Template name ends with `by SNMP` (e.g. `Netgear GS748Tv5 by SNMP`).
  - Item keys are lowercase, dotted (e.g. `system.cpu.util`, `vm.memory.util`).
  - Interface prototypes use the pattern `Interface [{#IFNAME}({#IFALIAS})]: …`.
- **Macros** for every threshold and credential (`{$SNMP.COMMUNITY}`, `{$CPU.UTIL.CRIT}`, `{$IF.*}`, …). **No hard‑coded secrets.**
- **Tags** on items and triggers (`component`, `scope`, `interface`).
- **Triggers** at template level go at the **root** of `zabbix_export` (Zabbix 6.0+ schema), not nested inside the template. Trigger prototypes stay inside the discovery rule.
- **Edge‑triggered link‑down** — keep the transition‑based logic (fire only on up→down, with a recovery expression). Do not revert to a plain "is down" check.
- **Value maps** for enumerations (`ifOperStatus`, `ifAdminStatus`, vendor status codes).
- **No private data** — no personal names, IPs, serials, community strings or internal hostnames anywhere in the YAML or docs. Set `vendor: name: Community`.
- Every new template must include its own **`README.md`** (compatibility, macros, items, triggers, limitations, OID reference) and be added to the **Available Templates** and **Feature Matrix** tables in the root `README.md`.

## Validation Checklist

Before submitting, please confirm:

- [ ] The YAML **imports cleanly** into Zabbix 7.4 (*Create new* / *Update existing*).
- [ ] All items collect data on **real hardware** (state the model/firmware in the PR).
- [ ] Discovery finds the expected interfaces; prototypes, graphs and dashboard render correctly.
- [ ] Triggers fire **and recover** as intended (especially the link‑down transition logic).
- [ ] No private or sensitive data is present (`grep` your changes).
- [ ] The template `README.md` and the root tables are updated.

> **Tip:** lint the file quickly to catch YAML syntax errors before importing:
> ```bash
> python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" your_template.yaml
> ```

## Commit & Branch Naming

We appreciate (but do not strictly require) [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Use for |
|------|---------|
| `feat:` | a new template, item, trigger or dashboard widget |
| `fix:` | correcting an OID, expression, threshold or import error |
| `docs:` | README / documentation changes |
| `refactor:` | restructuring without changing behaviour |
| `chore:` | tooling, formatting, housekeeping |

**Branch names:** `feat/<device>-<short-description>`, `fix/<device>-<short-description>`, `docs/<topic>`.

**Examples:**
```
feat/aruba-2930f-add-template
fix/gs748tv5-cpu-regex
docs/root-readme-badges
```

## Privacy & Legal

- **Do not commit vendor MIB files.** They remain the intellectual property of their respective owners and are subject to each vendor's licensing terms. This project ships **only original template code using numeric OIDs**. Obtain MIBs from the official vendor sources if you need them.
- **Do not commit private or sensitive data** (real IPs, serials, community strings, internal hostnames, personal names).
- All product names, logos and brands are the property of their respective owners and are referenced for **identification purposes only** (see the *Trademarks & Disclaimer* section of the root `README.md`).
- Contributions are accepted under the project's **MIT License**.

---

Thank you again for helping make these templates better for the whole community! 🙌
