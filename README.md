# ASP LaunchPad

ASP LaunchPad turns scripts, APIs, prompts, datasets, and workflows into monetized OKX.AI Agent Service Providers.

It outputs an MCP wrapper, A2MCP endpoint skeleton, listing copy, pricing recommendation, demo script, and readiness report.

## OKX.AI Genesis Hackathon Fit

- Category: Software Utility / Creative Genius
- Service mode: A2MCP for scaffold generation, A2A for done-for-you ASP launches
- Core value: helps more builders become OKX.AI ASPs quickly
- Demo target: upload a simple script and generate a ready-to-register ASP project

Hackathon notes:

- Campaign: OKX.AI Genesis, part of the X Layer Build X series.
- Build goal: create an Agent Service Provider that solves a clear real-world use case.
- Submission flow: list the ASP on OKX.AI, post a short X walkthrough with `#OKXAI`, then submit the project form before the deadline.
- Official context: https://www.okx.com/xlayer/build-x-hackathon

## Problem

Many builders have useful scripts, APIs, or workflows, but packaging them as paid ASPs takes too long. The hackathon rewards live, useful services, so teams need a faster route from raw capability to listed ASP.

## MVP Tools

### `analyze_project`

Analyzes a GitHub repo, OpenAPI spec, script, API endpoint, prompt workflow, or dataset.

### `generate_asp_scaffold`

Generates a FastAPI + MCP/A2MCP wrapper with schemas, tests, docs, and deployment files.

### `create_listing_copy`

Creates OKX.AI marketplace copy, pricing, example prompts, FAQ, and X launch post.

### `launch_readiness_check`

Checks endpoint health, expected tools, docs, test status, secrets, and registration readiness.

## Architecture

```text
Builder
  -> LaunchPad UI / MCP Tools
  -> Project Intake
  -> Repo/API/Workflow Analyzer
  -> ASP Architecture Planner
  -> Template Engine
  -> Code Generator
  -> Build/Test Sandbox
  -> Listing Generator
  -> Readiness Report
```

## Hackathon Demo

1. Upload a simple lead-verification script.
2. LaunchPad generates an MCP/A2MCP project.
3. Run readiness check.
4. Generate OKX.AI listing copy and demo script.
5. Show a paid call to the generated service.
6. Show metrics in a Revenue Rocket dashboard.

## Repository Contents

- `spec.md` - full product and technical specification
- `README.md` - project overview and hackathon framing
- `app/` - FastAPI service implementation
- `tests/` - API tests
- `Dockerfile` - production container
- `okx-ai-listing.md` - marketplace listing draft
- `DEMO_SCRIPT.md` - 90-second walkthrough script

## Run Locally

```bash
uv run uvicorn app.main:app --reload
```

Then open:

- API docs: `http://127.0.0.1:8000/docs`
- MCP-style manifest: `http://127.0.0.1:8000/mcp`
- Demo payloads: `http://127.0.0.1:8000/demo`

## Test

```bash
uv run --extra dev pytest
```

## Production Notes

- Set `LAUNCHPAD_API_KEY` before exposing paid endpoints.
- Deploy behind HTTPS before OKX.AI registration.
- Use `LAUNCHPAD_DATA_DIR` for persistent project/report storage.
- Generated scaffolds should be reviewed before production deployment.

## Contributor

- eosadolor382@gmail.com
- @Ikpia

## Status

Production-shaped MVP: analyzer, scaffold generator, listing generator, readiness checker, persistence, tests, Dockerfile, listing copy, and demo script are implemented.
