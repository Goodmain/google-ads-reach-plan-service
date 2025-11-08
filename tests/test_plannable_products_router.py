from app.services import google_ads_client


def test_get_plannable_products_success(client, monkeypatch):
    # Stub service return
    fake_products = [
        {"name": "YouTube Videos", "code": "YOUTUBE_VIDEOS"},
        {"name": "YouTube Shorts", "code": "YOUTUBE_SHORTS"},
    ]

    monkeypatch.setattr(
        google_ads_client.google_ads_service,
        "list_plannable_products",
        lambda loc_id: fake_products,
    )

    resp = client.get(
        "/api/v1/plannable-products",
        params={"plannable_location_id": "2840"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0] == fake_products[0]
    assert data[1] == fake_products[1]


def test_get_plannable_products_empty_id(client):
    # Passing empty string should trigger 400 from router validation
    resp = client.get(
        "/api/v1/plannable-products",
        params={"plannable_location_id": ""},
    )
    assert resp.status_code == 400
    assert "plannable_location_id" in resp.json()["detail"]