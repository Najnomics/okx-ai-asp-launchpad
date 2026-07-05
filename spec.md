# ASP LaunchPad Specification

## 1. Summary

ASP LaunchPad helps builders convert an existing script, API, prompt workflow, dataset, or service into a monetized OKX.AI Agent Service Provider.

It is a builder platform for launching ASPs faster during and after the OKX.AI Genesis hackathon.

## 2. Goals

- Reduce time from idea to live ASP.
- Generate reliable MCP/A2MCP scaffolds.
- Produce marketplace-ready listing copy.
- Add readiness checks before submission.
- Help builders price and package services.

## 3. Non-Goals

- MVP does not generate every possible framework.
- MVP does not guarantee OKX.AI listing approval.
- MVP does not execute arbitrary user code without sandboxing.

## 4. Users

| User | Need |
|---|---|
| Hackathon builder | Ship an ASP quickly. |
| API owner | Wrap an API as paid MCP tools. |
| Workflow operator | Turn repeatable work into a service. |
| Agency | Launch multiple ASPs from reusable templates. |

## 5. Service Modes

| Capability | Mode |
|---|---|
| `analyze_project` | A2MCP |
| `generate_asp_scaffold` | A2MCP |
| `create_listing_copy` | A2MCP |
| `launch_readiness_check` | A2MCP |
| done-for-you setup | A2A |
| growth/revenue optimization | A2A |

## 6. Public API

### 6.1 `analyze_project`

```json
{
  "source_type": "github_repo",
  "source_url": "https://github.com/user/project",
  "builder_goal": "Turn this API into an OKX.AI A2MCP service",
  "preferred_language": "python"
}
```

### 6.2 `generate_asp_scaffold`

```json
{
  "project_profile_id": "profile_123",
  "mode": "A2MCP",
  "template": "fastapi-mcp-a2mcp",
  "service_name": "Lead Verifier ASP",
  "tools": ["verify_lead", "enrich_company"]
}
```

### 6.3 `create_listing_copy`

```json
{
  "service_name": "Lead Verifier ASP",
  "target_users": ["sales agents", "research agents"],
  "tools": [
    {"name": "verify_lead", "price": "0.05 USDT"}
  ],
  "tone": "clear and practical"
}
```

### 6.4 `launch_readiness_check`

```json
{
  "repo_url": "https://github.com/user/generated-asp",
  "endpoint_url": "https://api.example.com/mcp",
  "expected_tools": ["verify_lead", "enrich_company"]
}
```

## 7. Core Components

### 7.1 Project Intake

Accepts:

- GitHub repo URL.
- OpenAPI spec.
- REST endpoint.
- Python/Node script.
- Prompt/workflow description.
- Dataset or schema.
- Service category and pricing goal.

### 7.2 Repo/API/Workflow Analyzer

For repos:

- Detect language/framework.
- Find routes/functions.
- Identify tests/build commands.
- Detect secrets.
- Suggest MCP tools.

For OpenAPI:

- Parse endpoints.
- Identify billable tools.
- Recommend schemas.
- Flag unsafe admin/private endpoints.

For workflows:

- Define inputs and outputs.
- Recommend deterministic tool contracts.
- Add quality guardrails.

### 7.3 ASP Architecture Planner

Selects A2MCP, A2A, or hybrid based on repeatability, task length, customization, and pricing model.

### 7.4 Template Engine

MVP template:

```text
fastapi-mcp-a2mcp
```

Generated files:

```text
src/server.py
src/tools/*.py
src/payment_adapter.py
tests/test_tools.py
Dockerfile
README.md
.env.example
openapi.json
mcp.json
okx-ai-listing.md
DEMO_SCRIPT.md
```

### 7.5 Code Generator

Generates:

- Tool schemas.
- API wrappers.
- Input validation.
- Error handling.
- Usage hooks.
- Logging.
- Test stubs.
- Deployment docs.

### 7.6 Build/Test Sandbox

Runs dependency install, tests, linting, endpoint probes, example tool calls, and payment-flow dry run where available.

### 7.7 Marketplace Listing Generator

Creates:

- service name.
- short and long descriptions.
- tool list.
- pricing recommendation.
- example prompts.
- demo script.
- FAQ.
- X launch thread.

## 8. Data Model

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  owner_agent_id TEXT,
  name TEXT,
  source_type TEXT,
  source_uri TEXT,
  recommended_mode TEXT,
  status TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE generated_assets (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  asset_type TEXT,
  storage_uri TEXT,
  content_hash TEXT,
  created_at TIMESTAMP
);

CREATE TABLE readiness_checks (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  build_status TEXT,
  test_status TEXT,
  payment_status TEXT,
  endpoint_status TEXT,
  readiness_score INT,
  findings JSONB,
  created_at TIMESTAMP
);
```

## 9. MVP Scope

- Analyze OpenAPI spec or simple Python script.
- Generate FastAPI MCP wrapper.
- Generate README, OKX.AI listing, and demo script.
- Run local readiness checks.
- Recommend pricing.
- Show generated assets in dashboard.

## 10. V1 Scope

- GitHub repo analyzer.
- One-click deploy.
- Multiple templates.
- Payment dry run.
- Revenue/review ingestion.
- A2A service generation.

## 11. Security Requirements

- Do not expose admin endpoints.
- Do not include secrets in generated code.
- Require environment variables.
- Secret-scan uploaded projects.
- Run untrusted code only in disposable sandboxes.

## 12. Hackathon Milestones

| Day | Target |
|---|---|
| 1 | Project intake and normalized profile. |
| 2 | OpenAPI/script analyzer. |
| 3 | FastAPI/MCP template. |
| 4 | Generator and tests. |
| 5 | Readiness checker. |
| 6 | Listing generator and demo. |
| 7 | Deploy, list, record walkthrough. |

