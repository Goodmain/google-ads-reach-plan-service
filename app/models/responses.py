from pydantic import BaseModel


class PlannableProduct(BaseModel):
    name: str
    code: str


class PlannableProductsResponse(BaseModel):
    products: list[PlannableProduct]
    location_id: str
    total_count: int


class Customer(BaseModel):
    id: str
    name: str


class CustomersResponse(BaseModel):
    customers: list[Customer]
    customer_id: str
    total_count: int


class ReachForecastRequest(BaseModel):
    start_date: str
    end_date: str
    customer_id: str
    user_list_id: str
    plannable_location_id: str
    network: str
    currency_code: str


class PlannedProduct(BaseModel):
    plannable_product_code: str
    budget_micros: int


class ReachCurvePoint(BaseModel):
    cost_micros: int
    reach: int
    impressions: int
    frequency: float


class ReachForecast(BaseModel):
    reach_curve: list[ReachCurvePoint]
    planned_products: list[PlannedProduct]
    currency_code: str
    customer_id: str


class ReachForecastResponse(BaseModel):
    forecast: ReachForecast
    request_parameters: ReachForecastRequest


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int