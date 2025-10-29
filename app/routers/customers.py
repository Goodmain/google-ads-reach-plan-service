from fastapi import APIRouter, HTTPException, Path
from app.services.google_ads_client import google_ads_service
from app.models.responses import CustomersResponse, Customer, ErrorResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=CustomersResponse, responses={
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_customers(
    customer_id: str = Path(..., description="The customer ID to search for customer clients")
):
    """
    Get customer clients for a specific customer ID using Google Ads API Search.
    
    This endpoint searches for customer clients within the specified customer account
    using the Google Ads API Search method with a GAQL query.
    
    Args:
        customer_id: The customer ID to search within
        
    Returns:
        CustomersResponse: List of customer clients with their IDs and names
        
    Raises:
        HTTPException: If the request fails or credentials are not configured
    """
    try:
        logger.info(f"Searching customers for customer ID: {customer_id}")
        
        # Validate customer_id format (should be numeric)
        if not customer_id.isdigit():
            raise HTTPException(
                status_code=400,
                detail="Customer ID must be numeric"
            )
        
        # Call the Google Ads service
        customers_data = google_ads_service.search_customers(customer_id)
        
        # Convert to response models
        customers = [Customer(id=customer["id"], name=customer["name"]) for customer in customers_data]
        
        response = CustomersResponse(
            customers=customers,
            customer_id=customer_id,
            total_count=len(customers)
        )
        
        logger.info(f"Successfully retrieved {len(customers)} customers for customer ID {customer_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching customers: {str(e)}"
        )