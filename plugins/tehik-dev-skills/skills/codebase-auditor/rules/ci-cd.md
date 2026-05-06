---
trigger: always_on
---

# CI/CD PIPELINE

## Pipeline stages (mandatory order)

```
┌──────────┐   ┌─────────┐   ┌────────────┐   ┌───────────────┐   ┌──────────┐
│  1. lint │ → │ 2. test │ → │  3. build  │ → │ 4. sec-scan   │ → │ 5. deploy│
└──────────┘   └─────────┘   └────────────┘   └───────────────┘   └──────────┘
```

| Stage | Contents | Blocking |
|-------|------|-----------|
| `lint` | Code style, static analysis (ESLint, Checkstyle, Ruff) | ✅ |
| `test` | Unit and integration tests, coverage checks | ✅ |
| `build` | Compilation, Docker image build | ✅ |
| `security-scan` | Dependency audit, SAST (Semgrep/SonarQube), container scan | ✅ |
| `deploy` | Deployment to an environment (only after prior stages pass) | ✅ |

## Environment hierarchy

```
feature/*  →  develop  →  staging  →  production
              (auto)      (auto)      (manual approval)
```

* **dev/feature**: every push runs `lint` + `test`
* **develop**: all stages, automatic deploy to the `development` environment
* **staging**: all stages, automatic deploy to the `staging` environment
* **production (main)**: all stages + **manual approval** before deploy

## Environment variables

* All environment-specific values go in CI/CD variables (GitLab: Settings → CI/CD → Variables)
* **Masked** for all secrets and tokens
* **Protected** for production variables (only on the `main` branch)
* `.env.example` documents all required variables
* Do not duplicate variables by hardcoding them in pipeline YAML

## Docker and artifacts

* Each build produces a versioned Docker image:
  * `registry.example.com/app:${CI_COMMIT_SHA}` — per commit
  * `registry.example.com/app:${VERSION}` — for a release tag  
  * `registry.example.com/app:latest` — only from the `main` branch
* Multi-stage Dockerfile (build stage separate from runtime stage)
* Base image: prefer distroless/slim variants
* Image scan (Trivy) required before deploy

## Rollback strategy

* Each deploy tracks the previous successful image tag
* Rollback is triggered manually: `docker pull registry.example.com/app:<previous-sha>`
* **Blue-green** or **canary** deploy in production (high traffic) — plan ahead
* DB migrations must be **reversible** (backward-compatible releases)

## Deploy idempotency

* **Each deploy step must be idempotent** — running the same deploy twice must not produce additional side effects
* Use `--set-if-not-exists` / `upsert` patterns when applying configuration
* Infrastructure as code (IaC): Terraform, Helm — `plan` before `apply`
* CI retry mechanism: if deploy fails, the pipeline must be safe to rerun without a manual cleanup step

## Principles for writing pipelines

```yaml
# Good: environment explicit, artifacts retained
test:
  stage: test
  script:
    - npm ci
    - npm run test:ci
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    expire_in: 1 week
```

* Declare `needs:` explicitly (parallelism where possible)
* All scripts use `set -e` (bash) — errors stop the pipeline
* Cache dependencies (npm, pip, maven) for faster builds
* The pipeline must not contain business logic — orchestration only

## Smoke tests after deploy

* After each deploy an **automatic smoke test** runs that verifies:
  * Health endpoints (`/health`, `/health/ready`) return `200`
  * Critical API endpoints respond (at least one `GET` check)
  * Database connectivity works
* If the smoke test fails → **automatic rollback** to the previous version

## Monitoring and notifications after deploy

* After deploy, watch **5xx error rate** and **response time** for at least 15 minutes
* If error rate exceeds the threshold (e.g. >1%) → alert and consider rollback
* Detailed rules: see `observability.md`

## Feature Flags

* New functionality can be turned on safely with **feature flags** — the flag lives in configuration, not scattered `if` statements in code
* Use a centralized feature flag service (e.g. Unleash, LaunchDarkly, GitLab Feature Flags)
* Remove stale flags after functionality stabilizes (do not accumulate technical debt)
* Feature flag state must be environment-specific (dev, staging, production)

## Sample pipeline template (GitLab CI)

```yaml
stages:
  - lint
  - test
  - build
  - security-scan
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

lint:
  stage: lint
  script:
    - npm ci
    - npm run lint

test:
  stage: test
  script:
    - npm ci
    - npm run test:ci
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    expire_in: 1 week

build:
  stage: build
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE
  needs: [lint, test]

security-scan:
  stage: security-scan
  script:
    - npm audit --audit-level=high
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $DOCKER_IMAGE
  needs: [build]

deploy-staging:
  stage: deploy
  script:
    - deploy-to-env staging $DOCKER_IMAGE
    - curl -f https://staging.example.com/health
  needs: [security-scan]
  environment:
    name: staging
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

deploy-production:
  stage: deploy
  script:
    - deploy-to-env production $DOCKER_IMAGE
    - curl -f https://api.example.com/health
  needs: [security-scan]
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
```

> **Note:** adapt the `deploy-to-env` script and URLs to your project needs. The GitHub Actions template is analogous (with a `jobs:` section).

## Prohibited practices

* ❌ Deploying without passing all prior stages
* ❌ Secrets in pipeline YAML files (including in base64)
* ❌ `allow_failure: true` on blocking stages (especially security scanning)
* ❌ Using the `latest` tag for production deploy (use SHA)
