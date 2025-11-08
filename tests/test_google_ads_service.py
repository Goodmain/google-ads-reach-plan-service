import types

from app.services.google_ads_client import GoogleAdsService


class FakeEnum:
    def __getitem__(self, key):
        return key


class FakeClient:
    def __init__(self, reach_plan_service=None, google_ads_service=None):
        self._reach_plan_service = reach_plan_service
        self._google_ads_service = google_ads_service
        self.enums = types.SimpleNamespace(ReachPlanNetworkEnum=FakeEnum())

    def get_service(self, name):
        if name == "ReachPlanService":
            return self._reach_plan_service
        if name == "GoogleAdsService":
            return self._google_ads_service
        raise ValueError(name)

    def get_type(self, name):
        # Minimal objects with attributes used in the code under test
        if name == "ListPlannableProductsRequest":
            return types.SimpleNamespace(plannable_location_id=None)
        if name == "SearchGoogleAdsRequest":
            return types.SimpleNamespace(customer_id=None, query=None)
        if name == "GenerateReachForecastRequest":
            # Nested structures used in the request building
            targeting = types.SimpleNamespace(
                plannable_location_ids=[],
                network=None,
                audience_targeting=types.SimpleNamespace(user_lists=[]),
            )
            return types.SimpleNamespace(
                customer_id=None,
                campaign_duration=None,
                currency_code=None,
                targeting=targeting,
                planned_products=[],
            )
        if name == "CampaignDuration":
            return types.SimpleNamespace(date_range=None)
        if name == "DateRange":
            return types.SimpleNamespace(start_date=None, end_date=None)
        if name == "UserListInfo":
            return types.SimpleNamespace(user_list=None)
        if name == "PlannedProduct":
            return types.SimpleNamespace(plannable_product_code=None, budget_micros=None)
        raise ValueError(name)


def test_has_required_credentials(monkeypatch):
    # Patch settings on the module to simulate credentials presence
    from app import config as config_mod
    monkeypatch.setattr(config_mod.settings, "google_ads_developer_token", "dev")
    monkeypatch.setattr(config_mod.settings, "google_ads_client_id", "id")
    monkeypatch.setattr(config_mod.settings, "google_ads_client_secret", "secret")
    monkeypatch.setattr(config_mod.settings, "google_ads_refresh_token", "refresh")

    # Prevent real client initialization during __init__
    monkeypatch.setattr(GoogleAdsService, "_initialize_client", lambda self: None)

    svc = GoogleAdsService()
    assert svc._has_required_credentials() is True

    # Missing refresh token
    monkeypatch.setattr(config_mod.settings, "google_ads_refresh_token", None)
    assert svc._has_required_credentials() is False


def test_list_plannable_products(monkeypatch):
    # Build fake response
    class FakeProduct:
        def __init__(self, name, code):
            self.plannable_product_name = name
            self.plannable_product_code = code

    class FakeResponse:
        def __init__(self):
            self.product_metadata = [
                FakeProduct("YouTube Videos", "YOUTUBE_VIDEOS"),
                FakeProduct("YouTube Shorts", "YOUTUBE_SHORTS"),
            ]

    class FakeReachPlanService:
        def list_plannable_products(self, request):
            return FakeResponse()

    svc = GoogleAdsService()
    svc.client = FakeClient(reach_plan_service=FakeReachPlanService())

    products = svc.list_plannable_products("2840")
    assert products[0]["name"] == "YouTube Videos"
    assert products[0]["code"] == "YOUTUBE_VIDEOS"
    assert products[1]["code"] == "YOUTUBE_SHORTS"


def test_search_customers(monkeypatch):
    # Build fake search response iterable
    class FakeCustomerClient:
        def __init__(self, cid, name=None):
            self.id = cid
            self.descriptive_name = name

    class FakeRow:
        def __init__(self, cid, name=None):
            self.customer_client = FakeCustomerClient(cid, name)

    class FakeSearchResponse:
        def __iter__(self):
            yield FakeRow(111, "Alpha")
            yield FakeRow(222, None)  # fallback to generated name

    class FakeGoogleAdsService:
        def search(self, request):
            return FakeSearchResponse()

    svc = GoogleAdsService()
    svc.client = FakeClient(google_ads_service=FakeGoogleAdsService())

    customers = svc.search_customers("1234567890")
    assert customers[0]["name"] == "Alpha"
    assert customers[1]["name"].startswith("Customer ")


def test_generate_reach_forecast_with_retry(monkeypatch):
    # Avoid actual sleeping during backoff
    monkeypatch.setattr("time.sleep", lambda s: None)

    calls = {"count": 0}

    class Metrics:
        def __init__(self, reach, impressions, frequency):
            self.reach = reach
            self.impressions = impressions
            self.frequency = frequency

    class Point:
        def __init__(self):
            self.cost_micros = 1000
            self.forecast_metrics = Metrics(10, 20, 2.0)

    class ReachCurve:
        def __init__(self):
            self.reach_forecasts = [Point()]

    class PlannedProduct:
        def __init__(self, code, budget):
            self.plannable_product_code = code
            self.budget_micros = budget

    class FakeResponse:
        def __init__(self):
            self.reach_curve = ReachCurve()
            self.planned_products = [
                PlannedProduct("TRUEVIEW_IN_STREAM", 100),
                PlannedProduct("NON_SKIP_AUCTION", 100),
            ]

    class FakeReachPlanService:
        def generate_reach_forecast(self, request):
            calls["count"] += 1
            if calls["count"] == 1:
                raise Exception("timeout occurred")
            return FakeResponse()

    svc = GoogleAdsService()
    svc.client = FakeClient(reach_plan_service=FakeReachPlanService())

    params = {
        "start_date": "2025-11-01",
        "end_date": "2025-12-01",
        "customer_id": "1234567890",
        "user_list_id": "123456789",
        "plannable_location_id": "2840",
        "network": "YOUTUBE",
        "currency_code": "USD",
    }

    result = svc.generate_reach_forecast(params)
    assert result["currency_code"] == "USD"
    assert len(result["reach_curve"]) == 1
    assert calls["count"] == 2  # retried once after timeout