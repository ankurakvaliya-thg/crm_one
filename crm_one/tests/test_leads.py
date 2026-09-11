import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_lead_lifecycle_and_conversion(client: AsyncClient, admin_headers: dict):
    # 1. Create a Lead
    lead_payload = {
        "title": "Cloud Migration Project",
        "company_name": "Wayne Industries",
        "first_name": "Bruce",
        "last_name": "Wayne",
        "email": "bruce@wayne.com",
        "phone": "+1-555-9999",
        "source": "Website",
        "status": "QUALIFIED",
        "estimated_value": 150000.0
    }
    res_create = await client.post("/api/v1/leads", json=lead_payload, headers=admin_headers)
    assert res_create.status_code == 201
    lead_data = res_create.json()
    lead_id = lead_data["id"]
    assert lead_data["status"] == "QUALIFIED"

    # 2. Convert Lead to Account + Contact + Deal
    res_convert = await client.post(f"/api/v1/leads/{lead_id}/convert", headers=admin_headers)
    assert res_convert.status_code == 200
    conv_data = res_convert.json()
    assert conv_data["lead_id"] == lead_id
    assert "account_id" in conv_data
    assert "contact_id" in conv_data
    assert "deal_id" in conv_data

    # 3. Verify lead status is now CONVERTED
    res_get = await client.get(f"/api/v1/leads/{lead_id}", headers=admin_headers)
    assert res_get.status_code == 200
    assert res_get.json()["status"] == "CONVERTED"

    # 4. Verify Account was created
    account_id = conv_data["account_id"]
    res_acc = await client.get(f"/api/v1/accounts/{account_id}", headers=admin_headers)
    assert res_acc.status_code == 200
    assert res_acc.json()["name"] == "Wayne Industries"
