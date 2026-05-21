"""
tests/test_api.py — Smoke tests for the FastAPI layer.

Run with:
    pytest tests/test_api.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


# ---------------------------------------------------------------------------
# POST /v1/agent/generate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_returns_queued(client: AsyncClient):
    response = await client.post(
        "/v1/agent/generate",
        json={"company_name": "Siemens"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "queued"
    assert body["company_name"] == "Siemens"
    assert "run_id" in body
    assert body["progress"] == 0


@pytest.mark.asyncio
async def test_generate_rejects_empty_company(client: AsyncClient):
    response = await client.post(
        "/v1/agent/generate",
        json={"company_name": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_rejects_missing_field(client: AsyncClient):
    response = await client.post("/v1/agent/generate", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /v1/agent/status/{run_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_status_returns_run(client: AsyncClient):
    # First create a run
    create_resp = await client.post(
        "/v1/agent/generate",
        json={"company_name": "TestCorp"},
    )
    run_id = create_resp.json()["run_id"]

    # Then fetch its status
    status_resp = await client.get(f"/v1/agent/status/{run_id}")
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["run_id"] == run_id
    assert body["company_name"] == "TestCorp"


@pytest.mark.asyncio
async def test_get_status_404_on_unknown_run(client: AsyncClient):
    response = await client.get("/v1/agent/status/nonexistent-run-id")
    assert response.status_code == 404
    body = response.json()
    assert "run_id" in body


# ---------------------------------------------------------------------------
# GET /v1/agent/status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_runs_returns_list(client: AsyncClient):
    response = await client.get("/v1/agent/status")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
