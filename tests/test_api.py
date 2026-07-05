from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_python_script_detects_tool() -> None:
    response = client.post(
        "/tools/analyze_project",
        json={
            "source_type": "python_script",
            "source_text": "def verify_lead(company):\n    return True\n",
            "preferred_language": "python",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "verify_lead" in body["candidate_tools"]
    assert body["recommended_mode"] == "A2MCP"


def test_generate_scaffold_returns_assets() -> None:
    response = client.post(
        "/tools/generate_asp_scaffold",
        json={
            "project_profile_id": "profile_demo",
            "service_name": "Lead Verifier ASP",
            "tools": ["verify_lead"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    paths = {asset["path"] for asset in body["generated_assets"]}
    assert "app/main.py" in paths
    assert "mcp.json" in paths


def test_readiness_check_passes_with_expected_artifacts() -> None:
    response = client.post(
        "/tools/launch_readiness_check",
        json={
            "expected_tools": ["verify_lead"],
            "payment_adapter_status": "configured",
        },
    )
    assert response.status_code == 200
    assert response.json()["readiness_score"] >= 80

