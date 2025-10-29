from fastapi import APIRouter, Query, HTTPException
from app.models.responses import ReachForecastResponse, ReachForecastRequest, ReachForecast, ErrorResponse
from app.services.google_ads_client import google_ads_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/reach-forecast", response_model=ReachForecastResponse)
async def get_reach_forecast(
    start_date: str = Query(..., description="Campaign start date in YYYY-MM-DD format", example="2025-11-01"),
    end_date: str = Query(..., description="Campaign end date in YYYY-MM-DD format", example="2025-12-01"),
    customer_id: str = Query(..., description="Google Ads customer ID", example="1234567890"),
    user_list_id: str = Query(..., description="User list ID for targeting", example="123456789"),
    plannable_location_id: str = Query(..., description="Plannable location ID", example="2840"),
    network: str = Query(..., description="Network type", example="YOUTUBE"),
    currency_code: str = Query(..., description="Currency code", example="USD")
):
    """
    Generate reach forecast using Google Ads API.
    
    This endpoint calls the Google Ads API GenerateReachForecast method with the specified parameters
    and returns reach curve data with planned products.
    
    The request includes predefined planned products:
    - TRUEVIEW_IN_STREAM with budget of 1,000,000,000,000 micros
    - NON_SKIP_AUCTION with budget of 1,000,000,000,000 micros
    
    Implements exponential backoff retry logic for timeout errors (max 3 attempts).
    
    Request format matches Google Ads API structure:
    - targeting.plannableLocationIds: [plannable_location_id]
    - targeting.network: network type
    - targeting.audienceTargeting.userLists: user list targeting
    - campaignDuration: uses start_date and end_date
    """
    try:
        # Validate date format (basic validation)
        if len(start_date) != 10 or len(end_date) != 10:
            raise HTTPException(
                status_code=400,
                detail="Date format must be YYYY-MM-DD"
            )
        
        # Validate customer_id is numeric
        if not customer_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Customer ID must be numeric"
            )
        
        # Validate network
        valid_networks = ["YOUTUBE", "YOUTUBE_AND_GOOGLE_VIDEO_PARTNERS"]
        if network not in valid_networks:
            raise HTTPException(
                status_code=400,
                detail=f"Network must be one of: {', '.join(valid_networks)}"
            )
        
        # Validate currency code (basic validation)
        if len(currency_code) != 3:
            raise HTTPException(
                status_code=400,
                detail="Currency code must be 3 characters (e.g., USD, EUR)"
            )
        
        # Create request parameters
        request_params = {
            "start_date": start_date,
            "end_date": end_date,
            "customer_id": customer_id,
            "user_list_id": user_list_id,
            "plannable_location_id": plannable_location_id,
            "network": network,
            "currency_code": currency_code
        }
        
        logger.info(f"Generating reach forecast for customer {customer_id}")
        
        # Call the Google Ads service
        forecast_data = google_ads_service.generate_reach_forecast(request_params)
        
        # Create request object for response
        request_obj = ReachForecastRequest(
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            user_list_id=user_list_id,
            plannable_location_id=plannable_location_id,
            network=network,
            currency_code=currency_code
        )
        
        # Create forecast object
        forecast_obj = ReachForecast(**forecast_data)
        
        # Return the response
        return ReachForecastResponse(
            forecast=forecast_obj,
            request_parameters=request_obj
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating reach forecast: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating reach forecast: {str(e)}"
        )