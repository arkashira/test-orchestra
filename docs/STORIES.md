# STORIES.md
## Test‑Orchestra – User Story Backlog

> **Product Vision**  
> An automated testing platform for web and mobile applications that delivers **fast setup**, **low‑maintenance**, and **reliable results**. Test‑Orchestra should let teams write, run, and analyze tests with minimal friction while supporting CI/CD pipelines and real‑device testing.

---

## Epics & Prioritized MVP Stories

| Epic | Description |
|------|-------------|
| **E1 – Quick Project Bootstrap** | Enable a new user to create a test project and have a runnable test suite in under 10 minutes. |
| **E2 – Cross‑Platform Test Execution** | Run the same test definitions on web browsers and native mobile devices (iOS/Android) with a single command. |
| **E3 – Reliable Result Reporting** | Provide deterministic, easy‑to‑read test reports with screenshots, logs, and flaky‑test detection. |
| **E4 – CI/CD Integration** | Allow Test‑Orchestra to be invoked from popular CI systems and expose results as build artifacts. |
| **E5 – Maintenance‑Friendly Test Authoring** | Offer a DSL / library that abstracts platform differences, supports reusable components, and auto‑updates selectors. |
| **E6 – Cloud Device Farm (Optional Future)** | Plug‑in architecture to connect to external device farms (e.g., BrowserStack, AWS Device Farm). |

> **MVP Scope** – Implement all stories in **E1**, **E2**, **E3**, and the core of **E4**. Stories in **E5** and **E6** are planned for later releases.

---

## User Stories

### Epic E1 – Quick Project Bootstrap

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E1‑01** | **As a new developer, I want a CLI wizard that scaffolds a Test‑Orchestra project, so that I can start writing tests immediately.** | 1. `test-orchestra init` prompts for project name, target platforms (web, iOS, Android). <br>2. Generates a folder structure (`/tests`, `/config`, `/reports`). <br>3. Installs required npm/ pip dependencies automatically. <br>4. Prints a “Ready to run” command (`test-orchestra run`). |
| **E1‑02** | **As a QA engineer, I want a sample test that runs on all selected platforms, so that I can verify the environment works.** | 1. Scaffold includes `sample.test.js` (or `.py`) with a simple navigation/assertion. <br>2. Running `test-orchestra run` executes the sample on each platform and produces a passing report. |
| **E1‑03** | **As a DevOps lead, I want the wizard to create a Dockerfile and a docker‑compose.yml, so that the whole stack can be containerised.** | 1. Dockerfile builds an image with all runtimes (Node, Python, browsers, Android SDK). <br>2. `docker-compose up` starts a service exposing a REST API on port 8080. <br>3. Documentation links to run the sample inside Docker. |

### Epic E2 – Cross‑Platform Test Execution

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E2‑01** | **As a test author, I want to declare a test once and run it on web, iOS, and Android, so that I avoid duplicate code.** | 1. Tests are written using the **Orchestra DSL** (JavaScript/TypeScript). <br>2. Platform‑agnostic commands (`orchestra.goto(url)`, `orchestra.tap(selector)`). <br>3. `test-orchestra run --platform web|ios|android` executes the same file on the chosen platform. |
| **E2‑02** | **As a mobile tester, I want the platform layer to automatically map selectors to native UI elements, so that my tests stay readable.** | 1. Selector syntax supports `#id`, `.class`, `text="Login"` etc. <br>2. Under the hood, WebDriverIO is used for web, Appium for mobile. <br>3. A mapping file (`selectors.json`) can override platform‑specific locators. |
| **E2‑03** | **As a QA lead, I want parallel execution across multiple devices, so that test suites finish quickly.** | 1. `test-orchestra run --parallel N` spawns N workers. <br>2. Workers are isolated (different browser profiles / emulator instances). <br>3. Overall runtime scales roughly linearly up to the number of available devices. |

### Epic E3 – Reliable Result Reporting

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E3‑01** | **As a developer, I want an HTML report with pass/fail status, screenshots, and console logs, so that I can debug failures fast.** | 1. After a run, `reports/<timestamp>.html` is generated. <br>2. Each test case shows status, duration, and a collapsible log. <br>3. On failure, a screenshot (web) or device screenshot (mobile) is attached. |
| **E3‑02** | **As a QA manager, I want flaky‑test detection, so that we can triage unstable tests.** | 1. When a test fails but passes on a retry, it is marked “flaky”. <br>2. Flaky count appears in the summary section. <br>3. Exportable CSV of flaky tests is available. |
| **E3‑03** | **As a stakeholder, I want test results to be exportable as JSON, so that other tools can consume them.** | 1. `test-orchestra run --output json` writes `results.json`. <br>2. Schema includes test ID, platform, status, duration, artifacts URLs. |

### Epic E4 – CI/CD Integration

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E4‑01** | **As a CI engineer, I want a Docker image that can be used in GitHub Actions, GitLab CI, and Jenkins, so that I can run tests in pipelines.** | 1. Image `axentx/test-orchestra:<version>` is published to Docker Hub. <br>2. Image contains CLI, browsers, Android SDK, and default config. <br>3. Documentation shows a minimal workflow step (`docker run axentx/test-orchestra run`). |
| **E4‑02** | **As a release manager, I want test results to be uploaded as build artifacts, so that they are archived with each CI run.** | 1. CLI supports `--artifact-dir <path>` to copy reports. <br>2. Example snippets for GitHub Actions (`actions/upload-artifact`) and GitLab (`artifacts: paths`). |
| **E4‑03** | **As a developer, I want the CLI to return a non‑zero exit code on failures, so that CI pipelines can fail correctly.** | 1. `test-orchestra run` exits with code 0 if all tests pass, otherwise >0. <br>2. Exit code reflects number of failed tests (optional). |

### Epic E5 – Maintenance‑Friendly Test Authoring (Future)

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E5‑01** | **As a test author, I want a visual selector recorder, so that I can capture element locators without writing code.** | 1. Browser extension / mobile recorder captures clicks and generates selector JSON. <br>2. Recorded steps can be exported to the DSL. |
| **E5‑02** | **As a QA lead, I want a library of reusable page‑object components, so that tests stay DRY.** | 1. `orchestra.page('Login')` loads a component definition. <br>2. Component files live under `pages/` and can be imported. |

### Epic E6 – Cloud Device Farm Integration (Future)

| # | Story | Acceptance Criteria |
|---|-------|----------------------|
| **E6‑01** | **As a mobile tester, I want to run tests on BrowserStack devices via a plug‑in, so that I can cover many OS versions.** | 1. `test-orchestra run --cloud browserstack` authenticates via env vars. <br>2. Device selection is defined in `cloud-config.yml`. |
| **E6‑02** | **As a DevOps engineer, I want the platform to fallback to local emulators when cloud devices are unavailable, so that CI never blocks.** | 1. Detects cloud API failure and switches to local Docker‑based emulators automatically. |

---

## Ordering for MVP Release

1. **E1‑01, E1‑02, E1‑03** – Project bootstrap & containerisation.  
2. **E2‑01, E2‑02, E2‑03** – Cross‑platform single‑source test definition and parallelism.  
3. **E3‑01, E3‑02, E3‑03** – Reporting & flaky detection.  
4. **E4‑01, E4‑02, E4‑03** – CI/CD ready Docker image and proper exit codes.  

*Stories in E5 and E6 are slated for post‑MVP sprints.*

---

## Definition of Done (DoD) for All Stories

- Code passes unit tests (`npm test` / `pytest`).  
- End‑to‑end test runs successfully on at least one web browser and one mobile emulator.  
- Documentation updated (README, CLI help, example config).  
- Linting and formatting compliant (`eslint` / `black`).  
- All new dependencies have approved licenses (Apache‑2.0, MIT, CDLA‑Permissive‑2.0).  
- Story reviewed and approved by product owner and QA lead.  

--- 

*Prepared by the Test‑Orchestra product team – version 0.1.*
