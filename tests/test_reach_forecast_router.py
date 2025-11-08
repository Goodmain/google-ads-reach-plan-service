from app.services import google_ads_client


def test_reach_forecast_success(client, monkeypatch):
    fake_forecast = {
        "reach_curve": [
            {
                "cost_micros": 1000,
                "reach": 10,
                "impressions": 20,
                "frequency": 2.0,
            }
        ],
        "planned_products": [
            {"plannable_product_code": "TRUEVIEW_IN_STREAM", "budget_micros": 100},
            {"plannable_product_code": "NON_SKIP_AUCTION", "budget_micros": 100},
        ],
        "currency_code": "USD",
        "customer_id": "1234567890",
    }

    monkeypatch.setattr(
        google_ads_client.google_ads_service,
        "generate_reach_forecast",
        lambda params: fake_forecast,
    )

    params = {
        "start_date": "2025-11-01",
        "end_date": "2025-12-01",
        "customer_id": "1234567890",
        "user_list_id": "123456789",
        "plannable_location_id": "2840",
        "network": "YOUTUBE",
        "currency_code": "USD",
    }
    resp = client.get("/api/v1/reach-forecast", params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert data["request_parameters"]["customer_id"] == "1234567890"
    assert data["forecast"]["currency_code"] == "USD"
    assert len(data["forecast"]["reach_curve"]) == 1


def test_reach_forecast_invalid_dates(client):
    params = {
        "start_date": "2025-11-1",  # invalid length/format
        "end_date": "2025-12-01",
        "customer_id": "1234567890",
        "user_list_id": "123456789",
        "plannable_location_id": "2840",
        "network": "YOUTUBE",
        "currency_code": "USD",
    }
    resp = client.get("/api/v1/reach-forecast", params=params)
    assert resp.status_code == 400
    assert "Date format" in resp.json()["detail"]


def test_reach_forecast_invalid_network(client):
    params = {
        "start_date": "2025-11-01",
        "end_date": "2025-12-01",
        "customer_id": "1234567890",
        "user_list_id": "123456789",
        "plannable_location_id": "2840",
        "network": "INVALID",
        "currency_code": "USD",
    }
    resp = client.get("/api/v1/reach-forecast", params=params)
    assert resp.status_code == 400
    assert "Network must be" in resp.json()["detail"]


def test_reach_forecast_invalid_currency(client):
    params = {
        "start_date": "2025-11-01",
        "end_date": "2025-12-01",
        "customer_id": "1234567890",
        "user_list_id": "123456789",
        "plannable_location_id": "2840",
        "network": "YOUTUBE",
        "currency_code": "US",
    }
    resp = client.get("/api/v1/reach-forecast", params=params)
    assert resp.status_code == 400
    assert "Currency code" in resp.json()["detail"]