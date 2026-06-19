# TECH_SPEC.md  

**Project:** test-orchestra  
**Domain:** Automated testing platform for web and mobile applications  
**Owner:** Axentx – Product Engineering  
**Status:** Draft (ready for review)  

---  

## 1. Overview  

`test-orchestra` is a cloud‑native, extensible platform that enables teams to define, execute, and analyze automated UI tests for web and mobile apps with **minimal setup** and **low ongoing maintenance**.  

Key goals:  

| Goal | Success Metric |
|------|----------------|
| **Fast onboarding** | New test suite created & runnable in ≤ 5 minutes |
| **Low maintenance** | < 5 % of test failures are flaky (as measured over 30 days) |
| **Reliability** | 99 % pass‑rate for stable test suites (CI/CD integration) |
| **Scalability** | Support ≥ 10 000 concurrent test executions across mixed browsers & devices |
| **Extensibility** | Plug‑in model for custom reporters, device farms, and test frameworks |

The platform consists of three logical layers:  

1. **Orchestration Service** – schedules, distributes, and monitors test runs.  
2. **Execution Workers** – lightweight containers that run tests using supported frameworks (Playwright, Appium, Selenium, etc.).  
3. **Result Store & Dashboard** – persists raw logs, screenshots, video, and provides a UI/REST API for reporting and analytics.  

---  

## 2. Architecture Diagram  

```
+-------------------+          +-------------------+          +-------------------+
|   CI/CD / CLI    |  HTTP    |  Orchestration    |  gRPC    |  Execution Worker |
| (GitHub Actions, |--------->|  Service (API)   |--------->|  (Docker/K8s pod) |
|  Jenkins, etc.)  |          |  + Scheduler     |          |  + Test Runner    |
+-------------------+          +-------------------+          +-------------------+
          |                               |                           |
          |                               |                           |
          |                               v                           v
          |                     +-------------------+      +-------------------+
          |                     |  Result Store     |<-----|  Artifact Upload  |
          |                     |  (PostgreSQL +   |      |  (S3 / MinIO)      |
          |                     |   TimescaleDB)   |      +-------------------+
          |                     +-------------------+
          |                               |
          |                               v
          |                     +-------------------+
          |                     |  Dashboard UI     |
          |                     |  (React + GraphQL)|
          |                     +-------------------+
```

---  

## 3. Core Components  

| Component | Responsibility | Tech Stack | Key Interfaces |
|-----------|----------------|-----------|----------------|
| **Orchestration Service** | - Auth & RBAC <br> - Test suite CRUD <br> - Scheduling & queue management <br> - Dispatch to workers | Python 3.11, FastAPI, Celery, Redis (broker), PostgreSQL | REST / JSON API (`/api/v1/*`), WebSocket for live logs |
| **Scheduler** | Prioritises jobs, handles retries, enforces concurrency limits | Celery beat + custom priority queue | Internal Celery tasks |
| **Execution Worker** | Pulls job definition, spins up container with selected framework, streams logs, uploads artifacts | Docker (runtime), Go 1.22 (lightweight agent), gRPC client to Orchestration | gRPC (`RunTest`, `CancelTest`), HTTP health checks |
| **Test Runner Plugins** | Abstracts concrete test frameworks (Playwright, Appium, Selenium) | Node 20 (Playwright), Java 17 (Appium), Python 3.11 (Selenium) | Standardised CLI (`orchestra-runner --suite <id>`) |
| **Result Store** | Persists test metadata, logs, screenshots, video, performance metrics | PostgreSQL 15, TimescaleDB extension, S3‑compatible object store (MinIO) | SQL + REST `/results/*` |
| **Dashboard UI** | Visualises test runs, flake detection, trend analytics | React 18, TypeScript, Apollo GraphQL, TailwindCSS | GraphQL (`query TestRun { … }`) |
| **Auth Provider** | Centralised identity (SSO) | Keycloak (OIDC) | OIDC token introspection |

---  

## 4. Data Model  

### 4.1 Relational Schema (PostgreSQL)

| Table | Primary Key | Important Columns |
|-------|-------------|-------------------|
| `users` | `id` (UUID) | `email`, `name`, `role` (admin/dev/viewer) |
| `projects` | `id` (UUID) | `name`, `owner_id`, `created_at` |
| `test_suites` | `id` (UUID) | `project_id`, `name`, `framework` (playwright/appium/selenium), `config_json` |
| `test_cases` | `id` (UUID) | `suite_id`, `name`, `file_path`, `tags` |
| `test_runs` | `id` (UUID) | `suite_id`, `status` (queued/running/passed/failed/flaky), `started_at`, `ended_at`, `worker_id` |
| `test_results` | `id` (UUID) | `run_id`, `case_id`, `status`, `duration_ms`, `log_url`, `screenshot_url`, `video_url` |
| `flaky_detection` | `id` (UUID) | `case_id`, `failure_rate`, `last_checked_at` |

### 4.2 Timeseries (TimescaleDB)

- Table `run_metrics` (hypertable) – stores per‑run CPU, memory, network usage for performance analysis.

### 4.3 Object Store Layout  

```
/artifacts/
   {run_id}/
       logs.txt
       screenshots/
           {case_id}.png
       videos/
           {case_id}.webm
```

---  

## 5. Key APIs  

### 5.1 REST API (FastAPI)  

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/v1/projects` | Create a new project | RBAC (admin/dev) |
| `GET`  | `/api/v1/projects/{id}` | Retrieve project details | RBAC (any) |
| `POST` | `/api/v1/suites` | Register a test suite (upload config) | RBAC (dev) |
| `GET`  | `/api/v1/suites/{id}` | Get suite definition | RBAC (any) |
| `POST` | `/api/v1/runs` | Enqueue a test run | RBAC (dev) |
| `GET`  | `/api/v1/runs/{id}` | Get run status & metrics | RBAC (any) |
| `GET`  | `/api/v1/runs/{id}/artifacts` | List artifact URLs | RBAC (any) |
| `DELETE`| `/api/v1/runs/{id}` | Cancel a running test | RBAC (dev) |

All endpoints return JSON with standard envelope:

```json
{
  "status": "success",
  "data": {...},
  "error": null
}
```

### 5.2 gRPC (Worker ↔ Orchestrator)

```proto
service Worker {
  rpc RunTest(RunRequest) returns (stream LogChunk);
  rpc CancelTest(CancelRequest) returns (CancelResponse);
}

message RunRequest {
  string run_id = 1;
  string suite_id = 2;
  map<string, string> env = 3;
}

message LogChunk {
  string run_id = 1;
  bytes data = 2;
  bool is_error = 3;
}
```

---  

## 6. Technology Stack  

| Layer | Technology | Reason |
|-------|------------|--------|
| **API** | FastAPI (Python) | High performance, async, easy OpenAPI generation |
| **Task Queue** | Celery + Redis | Proven pattern for distributed job scheduling |
| **Workers** | Go binary + Docker runtime | Low overhead, fast start‑up, easy cross‑platform |
| **Test Frameworks** | Playwright (Node), Appium (Java), Selenium (Python) | Covers modern web & native mobile |
| **Database** | PostgreSQL 15 + TimescaleDB | Strong ACID guarantees + native time‑series |
| **Object Store** | MinIO (S3‑compatible) | Cloud‑agnostic, easy local dev |
| **Auth** | Keycloak (OIDC) | Enterprise‑grade SSO, LDAP, social login |
| **Frontend** | React 18 + TypeScript + Apollo GraphQL | Rich interactive UI, type safety |
| **Infrastructure** | Kubernetes (EKS/AKS/GKE) + Helm charts | Auto‑scaling workers, rolling updates |
| **Observability** | Prometheus + Grafana (metrics), Loki (logs) | End‑to‑end visibility |
| **CI/CD** | GitHub Actions (build, test, publish Docker images) | Integrated with repo workflow |

---  

## 7. Dependencies  

| Dependency | Version | License |
|------------|---------|---------|
| fastapi | 0.110.0 | MIT |
| uvicorn | 0.27.0 | BSD |
| celery | 5.4.0 | BSD |
| redis-py | 5.0.1 | MIT |
| sqlalchemy | 2.0.25 | MIT |
| psycopg2-binary | 2.9.9 | LGPL‑2.1 |
| timescaledb‑psycopg2 | 0.5.0 | PostgreSQL |
| go | 1.22 | BSD |
| playwright | 1.44.0 | Apache‑2.0 |
| appium-java-client | 9.2.0 | Apache‑2.0 |
| selenium | 4.18.0 | Apache‑2.0 |
| react | 18.2.0 | MIT |
| apollo-client | 3.9.9 | MIT |
| keycloak | 24.0.2 | Apache‑2.0 |
| minio | 8.0.0 | Apache‑2.0 |

All third‑party libraries are vetted for compatibility with Axentx’s open‑source policy.

---  

## 8. Deployment Architecture  

### 8.1 Kubernetes Namespace `test-orchestra`  

| Resource | Replicas | CPU | Memory |
|----------|----------|-----|--------|
| `orchestrator` (FastAPI) | 2 (HA) | 500 m | 512 Mi |
| `celery-worker` | 4 | 300 m each | 256 Mi each |
| `redis` | 1 (stateful) | 250 m | 256 Mi |
| `postgres` | 1 (primary) + 1 (replica) | 1 CPU | 2 Gi |
| `minio` | 1 (distributed mode) | 500 m | 1 Gi |
| `worker‑agent` (Go) | Autoscale (0‑20) | 200 m | 128 Mi |
| `dashboard` (React) | 2 | 250 m | 256 Mi |
| `keycloak` | 1 | 500 m | 512 Mi |

All services expose internal ClusterIP; `orchestrator` and `dashboard` have Ingress (TLS terminated).  

### 8.2 CI/CD Pipeline  

1. **Lint & Unit Tests** – Run on PR push (GitHub Actions).  
2. **Integration Tests** – Spin up a temporary k8s cluster (kind) and execute a sample suite.  
3. **Docker Build** – Multi‑stage Dockerfiles for API, worker, dashboard.  
4. **Helm Release** – `helm upgrade --install test-orchestra ./helm` to target environment (dev / staging / prod).  
5. **Smoke Test** – Trigger a minimal test run; verify success via API.  

---  

## 9. Security & Compliance  

| Concern | Mitigation |
|---------|------------|
| **Authentication** | OIDC tokens validated by Keycloak; short‑lived access tokens (5 min). |
| **Authorization** | RBAC enforced at API gateway; fine‑grained permissions per project. |
| **Data at Rest** | PostgreSQL encrypted with AWS KMS (or equivalent); MinIO bucket encryption. |
| **Data in Transit** | All HTTP endpoints served over TLS 1.3; gRPC uses mTLS. |
| **Secret Management** | Kubernetes Secrets + SealedSecrets for CI/CD injection. |
| **Audit Logging** | Every API call logged to Loki with user ID and request ID. |
| **Compliance** | Licenses tracked via `license-checker`; no GPL components. |

---  

## 10. Observability  

- **Metrics**: Prometheus scrapes `/metrics` from API, workers, Celery, Redis. Exported metrics include `test_run_total`, `test_run_duration_seconds`, `worker_queue_length`.  
- **Logs**: Structured JSON logs shipped to Loki; correlated via `run_id`.  
- **Dashboards**: Grafana dashboards for system health, test flakiness heatmap, resource utilization.  

---  

## 11. Extensibility  

1. **Plugin Interface** – Test runner plugins implement a small CLI contract (`orchestra-runner`). New frameworks can be added by shipping a Docker image with the plugin and registering it in the `frameworks` table.  
2. **Reporter Hooks** – Post‑run webhook system (configurable per project) to push results to external tools (Jira, Slack, Azure DevOps).  
3. **Device Farm Integration** – Abstracted `DeviceProvider` interface; existing adapters for BrowserStack, Sauce Labs, and a self‑hosted Android/iOS farm.  

---  

## 12. Risks & Mitigations  

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Flaky tests overwhelm CI pipelines | Reduced developer confidence | Medium | Built‑in flake detection, auto‑retry, quarantine mode |
| Scaling worker pods leads to resource contention | Service degradation | High (during peak) | Horizontal pod autoscaler + resource quotas; pre‑warm pool of idle workers |
| Vendor lock‑in to a specific cloud provider | Future migration cost | Low | All components are cloud‑agnostic (K8s, S3‑compatible storage) |
| Security breach via compromised test artifacts | Data leakage | Low | Encrypted object store, signed artifact URLs, short‑lived access tokens |

---  

## 13. Milestones  

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| MVP – Core orchestration & worker execution | 2026‑07‑31 | API, Docker images, basic dashboard, Playwright support |
| Mobile support (Appium) | 2026‑09‑15 | Added Android/iOS device provider, sample mobile suite |
| Flake detection & auto‑quarantine | 2026‑10‑10 | Metrics, UI view, CI integration |
| Enterprise SSO & RBAC | 2026‑11‑05 | Keycloak integration, per‑project permissions |
| Public SaaS beta launch | 2026‑12‑01 | Multi‑tenant deployment, billing hooks, documentation |

---  

## 14. Glossary  

- **Suite** – Collection of test cases sharing configuration (framework, env).  
- **Run** – Single execution of a suite.  
- **Flake** – Test that intermittently fails without code change.  
- **Orchestrator** – Central service handling API, scheduling, and coordination.  

---  

*Prepared by:* Senior Product/Engineering Lead – Axentx  
*Date:* 2026‑06‑19
