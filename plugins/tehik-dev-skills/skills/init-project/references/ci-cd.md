# CI/CD Standards (init-project reference)

Source of truth: `codebase-auditor/rules/ci-cd.md`

## Pipeline stages (mandatory order)

```
lint → test → build → security-scan → deploy
```

All stages are blocking — no `allow_failure: true` on any of them.

## Environment hierarchy

```
feature/*  →  develop  →  staging  →  production
              (auto)      (auto)      (manual approval)
```

- **feature/*:** `lint` + `test` only
- **develop:** all stages, automatic deploy to `development` environment
- **staging:** all stages, automatic deploy to `staging` environment
- **production (main):** all stages + **manual approval** before deploy

## Docker image conventions

- Per-commit tag: `registry.example.com/app:${CI_COMMIT_SHA}`
- Release tag: `registry.example.com/app:${VERSION}`
- `latest` only from `main` branch
- Multi-stage Dockerfile (build stage separate from runtime stage)
- Prefer distroless/slim base images
- Trivy image scan required before deploy

## GitLab CI template

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

Adapt `deploy-to-env` script and URLs to project needs. The GitHub Actions equivalent uses a `jobs:` section with the same logical flow.

## Environment variables

- All secrets go in CI/CD settings (GitLab: Settings → CI/CD → Variables), **not** in pipeline YAML
- Mask all secrets and tokens
- Protect production variables (main branch only)
- `.env.example` documents all required variable names

## Prohibited

- ❌ Deploying without all prior stages passing
- ❌ Secrets in YAML (including base64)
- ❌ `allow_failure: true` on blocking stages
- ❌ Using `latest` tag for production deploy (use SHA)
