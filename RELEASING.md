# Releasing FinancialLibrary

How to cut a release so every version reference moves together.
This project follows [Semantic Versioning](https://semver.org/)
and keeps a [Keep a Changelog](https://keepachangelog.com/)
changelog.

## Checklist

1. **Decide the bump.** Patch for fixes and record corrections,
   minor for new countries, guides, or tooling, major for schema
   or taxonomy breaks (see `GOVERNANCE.md` for the 7-day rule on
   breaking changes).
2. **Bump the version everywhere, in one change:**
   - `pyproject.toml` — `version`
   - `CITATION.cff` — `version` and `date-released`
   - `README.md` — the Status section
   - `SECURITY.md` — the supported-versions table

   These four drifted apart at v0.5.0 (October 2026): the tag and
   changelog said 0.5.0 while pyproject still said 0.1.0 and
   CITATION said 0.4.0. Bumping them separately is how it
   happened; bump them together.
3. **Roll the changelog.** Move the `## [Unreleased]` entries in
   `CHANGELOG.md` into a new `## [X.Y.Z] - YYYY-MM-DD` section,
   leave a fresh empty `[Unreleased]` section above it, and add
   the compare/tag link definitions at the bottom of the file.
4. **Verify locally, all green:**

   ```bash
   make validate
   mkdocs build --strict
   make test
   ```

5. **Merge to `main`** through the normal PR flow.
6. **Tag and push the tag:**

   ```bash
   git checkout main
   git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

   The `release` workflow creates the GitHub Release
   automatically, using the matching `CHANGELOG.md` section as
   its notes.
7. **Verify the outputs.** The Release appears under the repo's
   Releases with the changelog notes, and the `deploy-pages`
   workflow has redeployed the docs site from the tagged `main`.

## Notes

- Never move or re-tag a published release tag; publish a new
  patch release instead (see `GOVERNANCE.md`).
- The repository name and visibility are owner decisions and are
  not part of a release.
