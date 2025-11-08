# Google Ads Reach Plan Service

A Python microservice for retrieving YouTube Reach Curve data via Google Ads API. This service provides a simple REST API to get plannable products for specific locations.

## Features

- **FastAPI-based microservice** with automatic API documentation
- **Google Ads API integration** for retrieving plannable products
- **Environment-based configuration** for secure credential management
- **Structured error handling** with proper HTTP status codes
- **Health check endpoint** for monitoring

## API Endpoints

### GET /api/v1/plannable-products

Retrieves plannable products for a specific location.

**Parameters:**
- `plannable_location_id` (string, required): The plannable location ID

**Response Format:**
```json
[
  {
    "name": "YouTube Videos",
    "code": "YOUTUBE_VIDEOS"
  },
  {
    "name": "YouTube Shorts",
    "code": "YOUTUBE_SHORTS"
  }
]
```

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/plannable-products?plannable_location_id=2840"
```

### GET /health

Health check endpoint that returns the service status.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Google Ads API access with valid credentials
- pip package manager

### 1. Clone and Setup

```bash
# Navigate to your project directory
cd /path/to/py-google-reach-plan-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your Google Ads API credentials
nano .env
```

Required environment variables:
- `GOOGLE_ADS_DEVELOPER_TOKEN`: Your Google Ads API developer token
- `GOOGLE_ADS_CLIENT_ID`: OAuth2 client ID
- `GOOGLE_ADS_CLIENT_SECRET`: OAuth2 client secret
- `GOOGLE_ADS_REFRESH_TOKEN`: OAuth2 refresh token

Optional variables:
- `GOOGLE_ADS_CUSTOMER_ID`: Specific customer account ID
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`: Login customer ID for manager accounts

### 3. Google Ads API Setup

To get your Google Ads API credentials:

1. Go to the [Google Ads API documentation](https://developers.google.com/google-ads/api/docs/first-call/overview)
2. Follow the "Get started" guide to:
   - Enable the Google Ads API
   - Create OAuth2 credentials
   - Generate a developer token
   - Obtain refresh token

### 4. Run the Service

```bash
# Run with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or run the main.py file
python app/main.py
```

The service will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Project Structure

```
py-google-reach-plan-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── responses.py       # Pydantic response models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── plannable_products.py  # API endpoints
│   └── services/
│       ├── __init__.py
│       └── google_ads_client.py   # Google Ads API client
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## Usage Examples

### Get Plannable Products for US (Location ID: 2840)

```bash
curl "http://localhost:8000/api/v1/plannable-products?plannable_location_id=2840"
```

### Using Python requests

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/plannable-products",
    params={"plannable_location_id": "2840"}
)

products = response.json()
print(f"Found {len(products)} plannable products")
for product in products:
    print(f"- {product['name']} ({product['code']})")
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid or missing parameters)
- `500`: Internal Server Error (Google Ads API errors, configuration issues)

Error responses include detailed messages:

```json
{
  "detail": "plannable_location_id is required and cannot be empty"
}
```

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once the service is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Location IDs

- United States: `2840`
- United Kingdom: `2826`
- Canada: `2124`
- Australia: `2036`
- Germany: `2276`

For a complete list of location IDs, refer to the [Google Ads API documentation](https://developers.google.com/google-ads/api/reference/data/geotargets).

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify your Google Ads API credentials in the `.env` file
2. **Permission Denied**: Ensure your developer token has the necessary permissions
3. **Invalid Location ID**: Check that the `plannable_location_id` is valid for your account

### Logs

The service logs important events. Check the console output for detailed error messages and debugging information.

## License

This project is for educational and development purposes. Please ensure compliance with Google Ads API terms of service.

## Linting

- Run lint: `ruff check .`
- Auto-fix simple issues: `ruff check . --fix`
- Config is in `pyproject.toml` under `[tool.ruff]`.
- Default rules selected: `E`, `F`, `I`, `UP`, `B`; `E501` is ignored and line-length is `100`.