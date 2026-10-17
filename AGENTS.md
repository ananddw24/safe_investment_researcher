# Agent guide — FinancialLibrary

This repository is an **educational** MkDocs + YAML hub. Agents must follow
these rules when proposing or applying changes.

## Non-negotiables

1. **Educational only** — never add personalized advice, buy/sell
   recommendations, account-opening flows, or KYC.
2. **Cite-first** — new resources/claims need `source_type` and `last_checked`.
3. **Do not weaken disclaimers** — keep the admonition block on content pages.
4. **Prefer official sources** — regulators, government, NGO, multilaterals.
5. **Scaffold vs content** — `v0.1.0` is structure; country deep-dives land in
   later releases (`v0.2.0` India first).

## Layout map

| Path | Role |
| --- | --- |
| `docs/` | MkDocs site (Guides, Vehicles, Pathways, About) |
| `data/resources/` | Curated resource YAML |
| `data/vehicles/` | Machine-readable vehicle stubs |
| `data/schemas/` | JSON Schema (validate before commit) |
| `scripts/` | `validate_data.py`, `check_ids.py`, `export_resources_json.py` |
| `.github/workflows/` | CI + Pages + release |

## Before finishing a change

```bash
make validate          # or: python scripts/validate_data.py && python scripts/check_ids.py
mkdocs build --strict
```

## Cursor rules

See [`.cursor/rules/financial-library.mdc`](.cursor/rules/financial-library.mdc).

## Licenses

MIT for code/scripts/schemas/workflows; CC BY 4.0 for educational prose and
curated metadata.
