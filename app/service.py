import hashlib
import json
import re
from typing import Any
from uuid import uuid4

import httpx

from .schemas import (
    AnalyzeProjectRequest,
    GenerateScaffoldRequest,
    GeneratedAsset,
    ListingCopyRequest,
    ProjectProfile,
    ReadinessCheckRequest,
    ScaffoldResponse,
)


SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=")
PY_FUNC_RE = re.compile(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", re.MULTILINE)
JS_FUNC_RE = re.compile(r"(?:function\s+|export\s+(?:async\s+)?function\s+)([a-zA-Z_][a-zA-Z0-9_]*)")
ROUTE_RE = re.compile(r"@(?:app|router)\.(get|post|put|delete)\(['\"]([^'\"]+)")


def stable_id(prefix: str, payload: Any) -> str:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:12]
    return f"{prefix}_{digest}"


def candidate_tool_names(source_type: str, text: str | None) -> list[str]:
    text = text or ""
    if source_type == "python_script":
        names = PY_FUNC_RE.findall(text)
    elif source_type == "node_script":
        names = JS_FUNC_RE.findall(text)
    elif source_type == "openapi_spec":
        names = [path.strip("/").replace("/", "_").replace("{", "").replace("}", "") for path in re.findall(r'["\'](/[^"\']+)["\']\s*:', text)]
    else:
        names = ROUTE_RE.findall(text)
        names = [path.strip("/").replace("/", "_") or method for method, path in names]
    cleaned = [name for name in names if not name.startswith("_")]
    return cleaned[:8] or ["run_service"]


def analyze_project(payload: AnalyzeProjectRequest) -> dict[str, Any]:
    text = payload.source_text or ""
    tools = candidate_tool_names(payload.source_type, text)
    secrets = sorted(set(match.group(1).upper() for match in SECRET_RE.finditer(text)))
    risk = "high" if secrets else "medium" if payload.source_type in {"github_repo", "rest_api"} else "low"
    mode = "A2MCP" if payload.source_type in {"openapi_spec", "python_script", "node_script", "rest_api"} else "A2A"
    findings = [
        f"Detected {len(tools)} candidate tool(s).",
        f"Recommended service mode: {mode}.",
        "Expose the generated API over HTTPS before OKX.AI registration.",
    ]
    if secrets:
        findings.append("Potential secret references detected; move them to environment variables before deployment.")
    profile = ProjectProfile(
        id=stable_id("profile", payload.model_dump(mode="json")),
        project_type=payload.source_type,
        language=payload.preferred_language,
        candidate_tools=tools,
        recommended_mode=mode,
        monetization_fit="Per-call A2MCP pricing is suitable for repeatable structured tools.",
        risk_level=risk,
        required_secrets=secrets,
        deployment_complexity="medium" if payload.source_url else "low",
        findings=findings,
    )
    return profile.model_dump()


def generate_scaffold(payload: GenerateScaffoldRequest) -> dict[str, Any]:
    tools = payload.tools or ["run_service"]
    routes = "\n".join(
        f'''@app.post("/tools/{tool}")\ndef {tool}(payload: dict) -> dict:\n    return {{"tool": "{tool}", "status": "ok", "input": payload}}\n'''
        for tool in tools
    )
    mcp_tools = ",\n    ".join(f'{{"name": "{tool}", "endpoint": "/tools/{tool}"}}' for tool in tools)
    assets = [
        GeneratedAsset(path="app/main.py", content=f"from fastapi import FastAPI\n\napp = FastAPI(title=\"{payload.service_name}\")\n\n@app.get(\"/health\")\ndef health():\n    return {{\"status\": \"ok\"}}\n\n{routes}"),
        GeneratedAsset(path="mcp.json", content="{\n  \"name\": \"" + payload.service_name + "\",\n  \"tools\": [\n    " + mcp_tools + "\n  ]\n}\n"),
        GeneratedAsset(path="README.md", content=f"# {payload.service_name}\n\nGenerated OKX.AI ASP scaffold with {len(tools)} tool(s).\n"),
        GeneratedAsset(path=".env.example", content="API_KEY=\nPAYMENT_WEBHOOK_SECRET=\n"),
        GeneratedAsset(path="Dockerfile", content="FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nRUN pip install fastapi uvicorn\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"),
    ]
    response = ScaffoldResponse(
        id=f"scaffold_{uuid4().hex[:12]}",
        service_name=payload.service_name,
        template=payload.template,
        generated_assets=assets,
        readiness_notes=[
            "Review generated schemas before exposing paid tools.",
            "Add OKX Payment SDK/APP adapter before listing.",
            "Deploy behind HTTPS and test with MCP Inspector.",
        ],
    )
    return response.model_dump()


def create_listing_copy(payload: ListingCopyRequest) -> dict[str, Any]:
    tool_lines = "\n".join(f"- {tool.get('name')}: {tool.get('price', 'TBD')}" for tool in payload.tools)
    users = ", ".join(payload.target_users)
    return {
        "id": f"listing_{uuid4().hex[:12]}",
        "kind": "listing_copy",
        "status": "generated",
        "service_name": payload.service_name,
        "short_description": f"{payload.service_name} helps {users} complete repeatable agent tasks through OKX.AI.",
        "long_description": f"{payload.service_name} is an OKX.AI Agent Service Provider built for {users}. It exposes structured tools, clear pricing, and auditable outputs for agent workflows.",
        "pricing": tool_lines,
        "example_prompt": f"Use {payload.service_name} to run the right tool for my task and return a concise result with evidence.",
        "x_post": f"Launching {payload.service_name} for #OKXAI: structured ASP tools for {users}. Demo walkthrough below.",
    }


async def launch_readiness_check(payload: ReadinessCheckRequest) -> dict[str, Any]:
    findings: list[str] = []
    score = 0
    for label, ok in [
        ("README present", payload.has_readme),
        ("Dockerfile present", payload.has_dockerfile),
        ("Environment example present", payload.has_env_example),
        ("Tests present", payload.has_tests),
    ]:
        if ok:
            score += 15
            findings.append(f"PASS: {label}.")
        else:
            findings.append(f"FAIL: {label}.")
    if payload.expected_tools:
        score += 15
        findings.append(f"PASS: {len(payload.expected_tools)} expected tool(s) declared.")
    if payload.payment_adapter_status == "configured":
        score += 20
        findings.append("PASS: payment adapter configured.")
    elif payload.payment_adapter_status == "stubbed":
        score += 10
        findings.append("PARTIAL: payment adapter is stubbed for hackathon testing.")
    else:
        findings.append("FAIL: payment adapter missing.")

    endpoint_status = "not_checked"
    if payload.endpoint_url:
        try:
            async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
                response = await client.get(str(payload.endpoint_url))
            endpoint_status = f"http_{response.status_code}"
            if response.status_code < 500:
                score += 10
                findings.append(f"PASS: endpoint reachable with {endpoint_status}.")
        except Exception as exc:
            endpoint_status = "unreachable"
            findings.append(f"FAIL: endpoint unreachable: {exc.__class__.__name__}.")

    return {
        "id": f"readiness_{uuid4().hex[:12]}",
        "kind": "readiness_check",
        "status": "pass" if score >= 80 else "needs_work" if score >= 50 else "fail",
        "readiness_score": min(score, 100),
        "endpoint_status": endpoint_status,
        "findings": findings,
    }

