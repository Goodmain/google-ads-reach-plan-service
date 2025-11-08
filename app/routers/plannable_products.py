from fastapi import APIRouter, HTTPException, Query
import logging

from app.services.google_ads_client import google_ads_service
from app.models.responses import PlannableProduct, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/plannable-products",
    response_model=list[PlannableProduct],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Get Plannable Products",
    description="Retrieve plannable products for YouTube Reach Curve via Google Ads API"
)
async def get_plannable_products(
    plannable_location_id: str = Query(
        ..., 
        description="The plannable location ID for which to retrieve products",
        example="2840"  # US location ID
    )
):
    """
    Get plannable products for a specific location.
    
    Args:
        plannable_location_id: The plannable location ID (required)
        
    Returns:
        List of plannable products with name and code
    """
    try:
        logger.info(f"Fetching plannable products for location: {plannable_location_id}")
        
        # Validate input
        if not plannable_location_id or not plannable_location_id.strip():
            raise HTTPException(
                status_code=400,
                detail="plannable_location_id is required and cannot be empty"
            )
        
        # Call the Google Ads service
        products = google_ads_service.list_plannable_products(plannable_location_id.strip())
        
        # Convert to response format
        response_products = [
            PlannableProduct(name=product["name"], code=product["code"])
            for product in products
        ]
        
        logger.info(f"Successfully retrieved {len(response_products)} products")
        return response_products
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching plannable products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve plannable products: {str(e)}"
        )