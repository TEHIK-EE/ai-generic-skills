---
name: release
description: "Complete release cycle: create a release branch, update CHANGELOG, bump version, run tests, create MRs, and tag. Use this whenever the user says 'release X.Y.Z', 'cut a release', 'prepare a release', 'create release branch', 'bump version for release', 'tag a release', or wants to promote develop to main with a version."
---

# Release preparation

Complete cycle for preparing a release. Follows the branch strategy defined in `/create-branch` and Semantic Versioning.

> **Before you start:** Ensure the `develop` branch is stable—all planned MRs are merged and CI passes.

---

## Safety rules

- **Confirmation gate:** the version number is confirmed with the user at the end of Phase 1 before the release branch is created.
- Never merge directly to `main` — always go through an MR.
- Always create both MRs: `release/<version>` → `main` AND `release/<version>` → `develop`.
- The `develop` branch must be stable (CI passing, all planned MRs merged) before cutting a release.
- Never push with `--force` to `main` or `develop`.

---

## Phase 1 — Version number

1. Review the `CHANGELOG.md` `[Unreleased]` section and identify the types of changes:

| Change type | Version |
|---------------|----------|
| Breaking change (`BREAKING CHANGE` in commits) | **MAJOR** (e.g. 1.0.0 → 2.0.0) |
| New functionality (`Added`) | **MINOR** (e.g. 1.2.0 → 1.3.0) |
| Bug fixes and minor changes only | **PATCH** (e.g. 1.3.0 → 1.3.1) |

2. Read the latest version: `git describe --tags --abbrev=0` or the latest release in `CHANGELOG.md`
3. Compute the new version according to the table above

> Ask the user to confirm the version number before continuing.

---

## Phase 2 — Release branch creation

1. Run the **`/create-branch`** skill with type `release` and version as the name (`release/<version>`).
   - Base branch: `develop`

---

## Phase 3 — Finalizing CHANGELOG

1. Update `CHANGELOG.md`:
   - Replace `[Unreleased]` → `[<version>] - <date>` (ISO 8601)
   - Add a new empty `[Unreleased]` section above it
   - Verify that all descriptions are **clear to end users**

```markdown
## [Unreleased]

## [1.4.0] - 2024-03-20
### Added
- ...
```

---

## Phase 4 — Version bump

1. Detect the project type and update the version in the appropriate config file:

```bash
# Node.js (package.json present)
npm version <version> --no-git-tag-version

# Java/Maven (pom.xml present)
./mvnw versions:set -DnewVersion=<version>

# Python (pyproject.toml present)
# update __version__ in pyproject.toml or the package __init__.py
```

Look for `package.json`, `pom.xml`, or `pyproject.toml` to determine which applies — run only the matching command.

---

## Phase 5 — Test verification

1. Run the **`/run-tests`** skill
   - All tests must pass
   - ❌ If tests fail: fix on the release branch; do not go back to `develop`

---

## Phase 6 — Commit, push, and MR

1. Run the **`/conventional-commit`** skill:
   - Type: `chore`
   - Message: `chore(release): prepare release <version>`

2. Push the release branch to remote:
```bash
git push -u origin release/<version>
```

3. Create **two MRs:**
    - `release/<version>` → `main` (release merge)
    - `release/<version>` → `develop` (back-merge CHANGELOG and version changes)

---

## Phase 7 — Tag creation (after merge to main)

1. After the MR is approved and `main` is merged:
```bash
git checkout main
git pull origin main
git tag -a v<version> -m "Release <version>"
git push origin v<version>
```

---

## Phase 8 — Cleanup

1. After both MRs are merged, delete the release branch:
```bash
git branch -d release/<version>
git push origin --delete release/<version>
```

---

## Phase 9 — Confirmation

Report:
```
✅ Release <version> prepared:
- CHANGELOG.md updated
- Version updated
- Tag v<version> created
- MRs to main and develop ready
- Release branch cleaned up
```
