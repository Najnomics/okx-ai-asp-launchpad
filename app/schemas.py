from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeProjectRequest(BaseModel):
    source_type: Literal["github_repo", "openapi_spec", "python_script", "node_script", "workflow_description", "rest_api"] = "python_script"
    source_url: HttpUrl | None = None
    source_text: str | None = None
    builder_goal: str = "Turn this into an OKX.AI A2MCP service"
    preferred_language: Literal["python", "typescript"] = "python"


class ProjectProfile(BaseModel):
    id: str
    project_type: str
    language: str
    candidate_tools: list[str]
    recommended_mode: Literal["A2MCP", "A2A", "hybrid"]
    monetization_fit: str
    risk_level: Literal["low", "medium", "high"]
    required_secrets: list[str]
    deployment_complexity: Literal["low", "medium", "high"]
    findings: list[str]


class GenerateScaffoldRequest(BaseModel):
    project_profile_id: str
    mode: Literal["A2MCP", "A2A", "hybrid"] = "A2MCP"
    template: str = "fastapi-mcp-a2mcp"
    service_name: str
    tools: list[str] = Field(default_factory=list)


class GeneratedAsset(BaseModel):
    path: str
    content: str


class ScaffoldResponse(BaseModel):
    id: str
    service_name: str
    template: str
    generated_assets: list[GeneratedAsset]
    readiness_notes: list[str]


class ListingCopyRequest(BaseModel):
    service_name: str
    target_users: list[str]
    tools: list[dict[str, str]]
    tone: str = "clear and practical"


class ReadinessCheckRequest(BaseModel):
    repo_url: HttpUrl | None = None
    endpoint_url: HttpUrl | None = None
    expected_tools: list[str] = Field(default_factory=list)
    has_readme: bool = True
    has_dockerfile: bool = True
    has_env_example: bool = True
    has_tests: bool = True
    payment_adapter_status: Literal["missing", "stubbed", "configured"] = "stubbed"

