from app.services import google_ads_client


def test_get_customers_success(client, monkeypatch):
    fake_customers = [
        {"id": "111", "name": "Alpha"},
        {"id": "222", "name": "Beta"},
    ]

    monkeypatch.setattr(
        google_ads_client.google_ads_service,
        "search_customers",
        lambda customer_id: fake_customers,
    )

    resp = client.get("/api/v1/customers/1234567890")
    assert resp.status_code == 200
    data = resp.json()
    assert data["customer_id"] == "1234567890"
    assert data["total_count"] == 2
    assert data["customers"][0] == fake_customers[0]


def test_get_customers_bad_id(client):
    resp = client.get("/api/v1/customers/abc")
    assert resp.status_code == 400
    assert "Customer ID" in resp.json()["detail"]