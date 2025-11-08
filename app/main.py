from fastapi import FastAPI
from app.routers import plannable_products, customers, reach_forecast

app = FastAPI(
    title="Google Ads Reach Plan Service",
    description="A microservice for retrieving YouTube Reach Curve data via Google Ads API",
    version="1.0.0"
)

# Include routers
app.include_router(plannable_products.router, prefix="/api/v1", tags=["plannable-products"])
app.include_router(customers.router, prefix="/api/v1", tags=["customers"])
app.include_router(reach_forecast.router, prefix="/api/v1", tags=["reach-forecast"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)