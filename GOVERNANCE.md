# Governance

Lightweight governance for FinancialLibrary.

## Maintainers

- Primary: [@ananddw24](https://github.com/ananddw24)
- Additional maintainers may be added by consensus (1–3 people total initially).

There is **no board** and no separate steering committee.

## Decision making

- **Lazy consensus on PRs:** If no maintainer objects within a reasonable
  review window and CI is green, a maintainer may merge.
- **Breaking taxonomy changes** (schema required fields, nav structure,
  license change): open an issue first and allow **7 days** for discussion
  before merging.
- **Security:** Follow [SECURITY.md](SECURITY.md).

## Releases

Semantic version tags (`v0.1.0`, `v0.2.0`, …). Scaffold vs content milestones
are described in the strategic plan / CHANGELOG. Force-push is forbidden on
`main` and on published release tags.
