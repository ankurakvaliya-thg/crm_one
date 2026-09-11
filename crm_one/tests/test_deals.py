import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_deal_pipeline_and_analytics(client: AsyncClient, admin_headers: dict):
    # 1. Create a Deal
    deal_payload = {
        "title": "SaaS Platform Enterprise Deal",
        "amount": 50000.0,
        "stage": "QUALIFICATION",
        "probability": 20
    }
    res_create = await client.post("/api/v1/deals", json=deal_payload, headers=admin_headers)
    assert res_create.status_code == 201
    deal_id = res_create.json()["id"]

    # 2. Progress deal to CLOSED_WON
    res_update = await client.put(
        f"/api/v1/deals/{deal_id}",
        json={"stage": "CLOSED_WON", "probability": 100},
        headers=admin_headers
    )
    assert res_update.status_code == 200
    assert res_update.json()["stage"] == "CLOSED_WON"

    # 3. Check dashboard analytics metrics
    res_analytics = await client.get("/api/v1/analytics/dashboard", headers=admin_headers)
    assert res_analytics.status_code == 200
    analytics_data = res_analytics.json()
    assert analytics_data["closed_won_amount"] == 50000.0
