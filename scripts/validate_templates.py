#!/usr/bin/env python3
"""
Validate Zabbix SNMP template YAML files.

Checks performed for every *.yaml under the template folders:
  1. Valid YAML syntax.
  2. Correct Zabbix export structure (zabbix_export -> version/templates).
  3. Template-level triggers live at the ROOT of zabbix_export (Zabbix 6.0+),
     never nested inside a template object.
  4. No private/sensitive data (names, sample IPs, etc.) via a denylist.
  5. Basic sanity: each template has a uuid, name and at least one item.

Exit code 0 = all good, 1 = at least one problem found.
Usage:
    python scripts/validate_templates.py [file1.yaml file2.yaml ...]
If no files are passed, it scans the two template sub-folders.
"""
import sys
import glob
import re

try:
    import yaml
except ImportError:
    print("::error::PyYAML is not installed (pip install pyyaml)")
    sys.exit(1)

# Case-insensitive denylist of private/sensitive tokens that must never appear.
# Keep this list generic; add project-specific tokens if needed.
PRIVATE_DENYLIST = [
    "bonaldo", "rossano veneto", "erika", "poretto",
    "TODO-PRIVATE", "CONFIDENTIAL",
]

# Default locations to scan when no explicit file list is given.
DEFAULT_GLOBS = [
    "hpe-instanton-1930/*.yaml",
    "netgear-gs748tv5/*.yaml",
    "*/*.yaml",
]


def find_files(argv):
    if argv:
        return argv
    found = []
    for pattern in DEFAULT_GLOBS:
        found.extend(glob.glob(pattern))
    # de-duplicate while preserving order
    seen, result = set(), []
    for f in found:
        if f not in seen and f.endswith((".yaml", ".yml")):
            seen.add(f)
            result.append(f)
    return result


def check_file(path):
    """Return a list of error strings for a single file (empty = OK)."""
    errors = []
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    # 4. Private data denylist (raw text, case-insensitive)
    low = raw.lower()
    for token in PRIVATE_DENYLIST:
        if token.lower() in low:
            errors.append(f"private/sensitive token found: '{token}'")

    # 1. YAML syntax
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"invalid YAML: {exc}")
        return errors  # cannot continue structural checks

    # 2. Zabbix export structure
    if not isinstance(data, dict) or "zabbix_export" not in data:
        errors.append("missing top-level 'zabbix_export' key")
        return errors
    export = data["zabbix_export"]

    if "version" not in export:
        errors.append("missing 'zabbix_export.version'")
    templates = export.get("templates")
    if not templates:
        errors.append("missing 'zabbix_export.templates'")
        return errors

    # 5. Per-template sanity + 3. triggers must NOT be nested in a template
    for i, tpl in enumerate(templates):
        name = tpl.get("template") or tpl.get("name") or f"#{i}"
        if "uuid" not in tpl:
            errors.append(f"template '{name}': missing uuid")
        if "items" not in tpl or not tpl["items"]:
            errors.append(f"template '{name}': no items defined")
        if "triggers" in tpl:
            errors.append(
                f"template '{name}': template-level 'triggers' are nested "
                "inside the template; move them to the root of 'zabbix_export' "
                "(Zabbix 6.0+ schema)."
            )

    return errors


def main():
    files = find_files(sys.argv[1:])
    if not files:
        print("::warning::no YAML template files found to validate")
        return 0

    total_errors = 0
    for path in files:
        errs = check_file(path)
        if errs:
            total_errors += len(errs)
            for e in errs:
                # GitHub Actions annotation format
                print(f"::error file={path}::{e}")
            print(f"[FAIL] {path} ({len(errs)} problem(s))")
        else:
            print(f"[ OK ] {path}")

    print("-" * 50)
    if total_errors:
        print(f"Validation FAILED: {total_errors} problem(s) across {len(files)} file(s).")
        return 1
    print(f"Validation PASSED: {len(files)} file(s) checked, no problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
