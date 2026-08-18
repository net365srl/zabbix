# Contributing

Thanks for helping improve the Cato Networks Zabbix template! Contributions of all sizes are welcome.

## Ways to contribute

- Report bugs or unsupported items (open an [issue](../../issues)).
- Suggest new metrics or dashboard widgets.
- Improve documentation.
- Submit pull requests with fixes or new features.

## Development setup

You only need Python (for validation) and a Zabbix 7.4 instance to test imports.

```bash
# Validate the template is well-formed YAML
python3 -c "import yaml; yaml.safe_load(open('templates/template_cato_networks_http.yaml')); print('YAML OK')"

# Check every uuid is a valid UUIDv4
python3 - <<'PY'
import re
s=open('templates/template_cato_networks_http.yaml').read()
u=re.findall(r'uuid:\s*([0-9a-f]{32})',s)
bad=[x for x in u if not(len(x)==32 and x[12]=='4' and x[16] in '89ab')]
dups=set(x for x in u if u.count(x)>1)
print('total',len(u),'invalid',bad,'dups',dups)
assert not bad and not dups, 'UUID problems'
print('UUIDs OK')
PY
```

## Editing rules

1. **UUIDs.** Every new element needs a **unique UUIDv4**. Generate with
   `python3 -c "import uuid; print(uuid.uuid4().hex)"`. Never reuse an existing UUID.
2. **Keys.** Item keys must be unique per template. Follow the `cato.<area>.<metric>[params]` convention.
3. **Defensive parsing.** New dependent items must not break siblings if a field is missing (wrap lookups,
   use `error_handler`, or `try/catch` in JavaScript).
4. **Schema fidelity.** Only request fields that exist in the Cato GraphQL schema. Verify with the
   [GraphQL Playground](https://knowledge.catonetworks.com/docs/connecting-to-the-cato-api-from-the-graphql-playground).
5. **Docs.** Update [docs/METRICS.md](docs/METRICS.md) and [CHANGELOG.md](CHANGELOG.md) with any change.
6. **Test import.** Import into a real Zabbix 7.4 before opening the PR.

## Commit & PR conventions

- Use clear, present-tense commit messages (e.g. `add BGP prefix-limit trigger`).
- Reference issues with `Fixes #123` where relevant.
- Keep PRs focused; one logical change per PR.
- Bump the template `version` and add a `CHANGELOG.md` entry using
  [Semantic Versioning](https://semver.org/).

## Versioning

- **PATCH** — fixes, doc updates, no behavioral change.
- **MINOR** — new items/LLD/dashboards, backward compatible.
- **MAJOR** — breaking changes (renamed keys, restructured LLD).

By contributing, you agree that your contributions are licensed under the [MIT-0](LICENSE) license.
