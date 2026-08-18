# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 2.0.x | ✅ |
| < 2.0 | ❌ |

## Reporting a vulnerability

If you discover a security issue in this template (for example, a way it could leak the API key or credentials),
please **do not open a public issue**. Instead:

1. Use GitHub's **Private vulnerability reporting** (Security tab → *Report a vulnerability*), or
2. Contact the maintainers privately.

Please include a description, reproduction steps and the potential impact. We aim to acknowledge reports within
a few business days.

## Handling of secrets

- The Cato API key is stored in the `{$CATO.API.KEY}` macro as **Secret text**. Keep it that way.
- **Restrict the API key to the Zabbix source IP** in the Cato Management Application.
- Grant the key **read-only** permissions limited to the surfaces the template uses (see
  [docs/INSTALL.md](docs/INSTALL.md#permission-matrix)).
- Do not commit real API keys, account IDs or exported configs containing secrets to the repository.

## Scope

This is a community template and is **not affiliated with Cato Networks Ltd.** Vulnerabilities in the Cato
platform or API itself should be reported to Cato Networks through their official channels.
