import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        res_prov = await client.get("/health/providers")
        assert res_prov.status_code == 200
        assert "gemini" in res_prov.json()
        assert "groq" in res_prov.json()
        assert "tavily" in res_prov.json()

@pytest.mark.asyncio
async def test_create_and_fetch_profile():
    # Test profile creation and capability token authorization
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        profile_payload = {
            "full_name": "Rahul Sharma",
            "nationality": "India",
            "degree_level_target": "master",
            "field_of_study": "Computer Science",
            "target_countries": ["Germany", "Canada"],
            "grade": {"value": 8.2, "scale": 10.0},
        }

        # 1. Create profile
        create_res = await client.post("/api/v1/profiles", json=profile_payload)
        assert create_res.status_code == 201
        data = create_res.json()
        profile_id = data["id"]
        token = data["access_token"]
        assert len(token) > 20

        # 2. Fetch with valid token
        headers = {"X-Access-Token": token}
        fetch_res = await client.get(f"/api/v1/profiles/{profile_id}", headers=headers)
        assert fetch_res.status_code == 200
        assert fetch_res.json()["profile"]["full_name"] == "Rahul Sharma"

        # 3. Reject invalid token with 404 per security rule
        bad_headers = {"X-Access-Token": "invalid_wrong_token"}
        bad_res = await client.get(f"/api/v1/profiles/{profile_id}", headers=bad_headers)
        assert bad_res.status_code == 404

@pytest.mark.asyncio
async def test_cancel_and_retry_job():
    # Test research job cancellation and retry endpoints
    from unittest.mock import patch, AsyncMock
    transport = ASGITransport(app=app)
    with patch("app.application.start_research.execute_research_job", new_callable=AsyncMock), \
         patch("app.api.routers.research_jobs.execute_research_job", new_callable=AsyncMock):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Create a test profile
            profile_payload = {
                "full_name": "Test Student",
                "nationality": "India",
                "degree_level_target": "master",
            }
            res_prof = await client.post("/api/v1/profiles", json=profile_payload)
            assert res_prof.status_code == 201
            profile_id = res_prof.json()["id"]

            # Start research job
            res_job = await client.post("/api/v1/research-jobs", json={"profile_id": profile_id})
            assert res_job.status_code == 202
            job_id = res_job.json()["id"]

            # Cancel research job
            cancel_res = await client.post(f"/api/v1/research-jobs/{job_id}/cancel")
            assert cancel_res.status_code == 200
            assert cancel_res.json()["status"] == "cancelled"

            # Retry cancelled job
            retry_res = await client.post(f"/api/v1/research-jobs/{job_id}/retry")
            assert retry_res.status_code == 202
            assert retry_res.json()["status"] == "running"
