# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| `1.0.x` (latest release) | Yes |
| `0.7.x` | Security fixes only |
| `< 0.7.0` | No |

## Reporting a vulnerability

Please report security issues **privately** via
[GitHub Security Advisories](https://github.com/ananddw24/safe_investment_researcher/security/advisories/new)
for this repository.

Do **not** open a public issue for vulnerabilities that could expose
contributors or users to harm (for example, compromised CI secrets — though
this project should never store secrets in the repo).

### Disclosure timeline

- We aim to acknowledge reports within **7 days**.
- We aim to publish a fix or mitigation within **90 days**, coordinating
  disclosure with the reporter when practical.
- No bug bounty is offered.

## Scope notes

This repository is primarily static documentation and YAML data. Typical
concerns include supply-chain issues in GitHub Actions, malicious PRs, and
link abuse in curated resources — not application RCE.
