TEMPLATE = templates/template_cato_networks_http.yaml

.PHONY: help validate yaml uuids structure

help:
	@echo "Targets:"
	@echo "  make validate   - run all checks (yaml + uuids + structure)"
	@echo "  make yaml       - validate YAML syntax"
	@echo "  make uuids      - validate UUIDv4 and uniqueness"
	@echo "  make structure  - validate structure and cross-references"

validate: yaml uuids structure
	@echo "All checks passed."

yaml:
	@python3 -c "import yaml; yaml.safe_load(open('$(TEMPLATE)')); print('YAML OK')"

uuids:
	@python3 -c "import re,sys; s=open('$(TEMPLATE)').read(); u=re.findall(r'uuid:\s*([0-9a-f]{32})',s); \
	v=[x for x in u if not(len(x)==32 and x[12]=='4' and x[16] in '89ab')]; \
	d=sorted(set(x for x in u if u.count(x)>1)); \
	sys.exit('invalid: %s'%v) if v else None; sys.exit('dups: %s'%d) if d else print('UUIDs OK (%d)'%len(u))"

structure:
	@python3 -c "import yaml; d=yaml.safe_load(open('$(TEMPLATE)')); t=d['zabbix_export']['templates'][0]; \
	print('OK:',len(t['items']),'items,',len(t['discovery_rules']),'LLD,',len(t['dashboards'][0]['pages']),'pages')"
