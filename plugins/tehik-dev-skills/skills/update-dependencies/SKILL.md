---
name: update-dependencies
description: "Audit and safely update project dependencies (npm, pip, Gradle/Maven). Use whenever the user mentions outdated packages, security vulnerabilities in dependencies, npm/pip audit results, Dependabot alerts, or any request to update, bump, or upgrade library versions."
---

# Dependency Updates

Regularly updating dependencies reduces security risk and technical debt.

> **Cadence:** at least once a month (ideally via Dependabot / Renovate Bot automatically). Critical security fixes — immediately.

---

## Safety rules

- **Confirmation gate:** review audit results in Phase 1 before making any changes.
- Handle major version upgrades one at a time — never batch them. Batching makes rollback and root-cause analysis much harder.
- Always verify the lock file is updated and committed after dependency changes.
- If a dependency update causes test failures, diagnose whether it is a breaking change before proceeding.
- Never use `--legacy-peer-deps` or `--force` to bypass peer dependency conflicts without understanding the impact.

---

## Phase 1 — Audit

1. Run a security audit:

```bash
# Node.js
npm audit

# Python
pip-audit

# Java/Kotlin
./gradlew dependencyCheckAnalyze || ./mvnw org.owasp:dependency-check-maven:check
```

2. Identify:
   - **Critical** vulnerabilities (high/critical) → fix immediately
   - **Outdated** dependencies (major versions behind) → plan an update
   - **Deprecated** dependencies → find a replacement

---

## Phase 2 — Create branch

3. Run the **`/create-branch`** skill with type `feature`:
   - Branch name: `feature/<ticket-id>-update-dependencies`
   - If it is a security fix and urgent: `hotfix/<ticket-id>-security-update-<package>`

---

## Phase 3 — Update

4. Update dependencies — keep patch/minor and major updates separate so rollbacks are easy:

```bash
# Node.js — check what would change first
npx npm-check-updates

# Apply patch/minor updates in one batch
npx npm-check-updates -u --target minor
npm install

# Handle each major update individually
npx npm-check-updates -u --filter <package>
npm install

# Python (pip-tools)
pip-compile --upgrade requirements.in

# Python (Poetry)
poetry update <package>

# Python (plain pip — legacy projects)
pip install --upgrade <package>
pip freeze > requirements.txt

# Java/Kotlin — list outdated versions
./gradlew dependencyUpdates
# Then manually bump version numbers in build.gradle / build.gradle.kts
# and run: ./gradlew build
```

> ⚠️ Always handle major version upgrades one at a time — batching them makes rollback and root-cause analysis much harder.

**Rules:**
- **Patch/minor** updates: may be batched (one commit)
- **Major** updates: one at a time, separate commit (easier rollback)
- Check **CHANGELOG/release notes** for each major update — are there breaking changes?
- Lock file (`package-lock.json`, `poetry.lock`, `gradle.lockfile`) **must** be updated and committed

---

## Phase 4 — Verify tests

5. Run the **`/run-tests`** skill
   - All tests must pass
   - If a test fails: determine whether it is a breaking change from a dependency → fix the code accordingly

---

## Phase 5 — Audit after update

6. Run the security audit again — confirm vulnerabilities are addressed:

```bash
# Node.js
npm audit --audit-level=high

# Python
pip-audit

# Java/Kotlin
./gradlew dependencyCheckAnalyze || ./mvnw org.owasp:dependency-check-maven:check
```

---

## Phase 6 — Commit

7. Run the **`/conventional-commit`** skill
   - Type: `chore`
   - Example: `chore(deps): update spring-boot to 3.2.4`
   - For major updates, add a body with notable changes

---

Report:
```
Dependency update:
- Updated: [list of packages and versions]
- Security audit: ✅ clean / ⚠️ [X] known (low risk)
- Tests: ✅ passed
- Branch: <name> is ready for opening an MR
```
