from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .schemas import AnalyzeProjectRequest, GenerateScaffoldRequest, ListingCopyRequest, ReadinessCheckRequest
from .service import analyze_project, create_listing_copy, generate_scaffold, launch_readiness_check
from .storage import ProjectStore

app = FastAPI(title="ASP LaunchPad", version="0.1.0", description="Generate OKX.AI ASP scaffolds, listings, and readiness reports.")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_origins == "*" else [item.strip() for item in settings.cors_origins.split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
store = ProjectStore(settings.data_dir)


def require_api_key(x_api_key: str | None = Header(default=None), config: Settings = Depends(get_settings)) -> None:
    if config.api_key and x_api_key != config.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def persist(record: dict, kind: str | None = None) -> dict:
    if "id" in record:
        store.insert({"id": record["id"], "kind": kind or record.get("kind", "project"), "status": record.get("status", "generated"), **record})
    return record


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "asp-launchpad", "mode": "A2MCP"}


@app.get("/mcp")
def mcp_manifest() -> dict:
    return {
        "name": "ASP LaunchPad",
        "version": "0.1.0",
        "service_mode": "A2MCP",
        "tools": [
            {"name": "analyze_project", "endpoint": "/tools/analyze_project"},
            {"name": "generate_asp_scaffold", "endpoint": "/tools/generate_asp_scaffold"},
            {"name": "create_listing_copy", "endpoint": "/tools/create_listing_copy"},
            {"name": "launch_readiness_check", "endpoint": "/tools/launch_readiness_check"},
        ],
    }


@app.post("/tools/analyze_project", dependencies=[Depends(require_api_key)])
def tool_analyze_project(payload: AnalyzeProjectRequest) -> dict:
    return persist(analyze_project(payload), kind="project_profile")


@app.post("/tools/generate_asp_scaffold", dependencies=[Depends(require_api_key)])
def tool_generate_asp_scaffold(payload: GenerateScaffoldRequest) -> dict:
    return persist(generate_scaffold(payload), kind="scaffold")


@app.post("/tools/create_listing_copy", dependencies=[Depends(require_api_key)])
def tool_create_listing_copy(payload: ListingCopyRequest) -> dict:
    return persist(create_listing_copy(payload), kind="listing_copy")


@app.post("/tools/launch_readiness_check", dependencies=[Depends(require_api_key)])
async def tool_launch_readiness_check(payload: ReadinessCheckRequest) -> dict:
    return persist(await launch_readiness_check(payload), kind="readiness_check")


@app.get("/history", dependencies=[Depends(require_api_key)])
def history(limit: int = 50) -> dict:
    return {"items": store.list_recent(limit=limit)}


@app.get("/demo")
def demo() -> dict:
    return {
        "lead_verifier_script": {
            "endpoint": "/tools/analyze_project",
            "payload": {
                "source_type": "python_script",
                "preferred_language": "python",
                "source_text": "def verify_lead(company, website, contact_email):\n    return {'valid': bool(company and website and contact_email)}\n",
                "builder_goal": "Turn this lead verifier into an OKX.AI A2MCP service",
            },
        }
    }

