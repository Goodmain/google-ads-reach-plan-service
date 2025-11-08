from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from app.config import settings
import logging
import time
import random

logger = logging.getLogger(__name__)


class GoogleAdsService:
    def __init__(self):
        self.client = None
        # Only initialize client if all required credentials are provided
        if self._has_required_credentials():
            self._initialize_client()
        else:
            logger.warning("Google Ads credentials not found. Client will be initialized when credentials are available.")
    
    def _has_required_credentials(self):
        """Check if all required credentials are available."""
        try:
            return all([
                settings.google_ads_developer_token and settings.google_ads_developer_token.strip(),
                settings.google_ads_client_id and settings.google_ads_client_id.strip(),
                settings.google_ads_client_secret and settings.google_ads_client_secret.strip(),
                settings.google_ads_refresh_token and settings.google_ads_refresh_token.strip()
            ])
        except Exception:
            return False
    
    def _initialize_client(self):
        """Initialize the Google Ads client with credentials from environment variables."""
        try:
            credentials = {
                "developer_token": settings.google_ads_developer_token,
                "client_id": settings.google_ads_client_id,
                "client_secret": settings.google_ads_client_secret,
                "refresh_token": settings.google_ads_refresh_token,
                "use_proto_plus": True,  # Required for Google Ads API v28+
            }
            
            # Add optional customer IDs if provided
            if settings.google_ads_customer_id:
                credentials["customer_id"] = settings.google_ads_customer_id
            if settings.google_ads_login_customer_id:
                credentials["login_customer_id"] = settings.google_ads_login_customer_id
            
            self.client = GoogleAdsClient.load_from_dict(credentials)
            logger.info("Google Ads client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            raise
    
    def get_reach_plan_service(self):
        """Get the Reach Plan Service from Google Ads API."""
        if not self.client:
            raise Exception("Google Ads client not initialized")
        return self.client.get_service("ReachPlanService")
    
    def list_plannable_products(self, plannable_location_id: str):
        """
        List plannable products for a given location.
        
        Args:
            plannable_location_id (str): The plannable location ID
            
        Returns:
            List of plannable products
        """
        if not self.client:
            if not self._has_required_credentials():
                raise Exception("Google Ads API credentials are not configured. Please check your environment variables.")
            else:
                # Try to initialize client if credentials are now available
                self._initialize_client()
        
        try:
            reach_plan_service = self.get_reach_plan_service()
            
            # Create the request using the client's types
            request = self.client.get_type("ListPlannableProductsRequest")
            request.plannable_location_id = plannable_location_id
            
            # Make the API call
            response = reach_plan_service.list_plannable_products(request=request)
            
            # Format the response
            products = []
            for product in response.product_metadata:
                products.append({
                    "name": product.plannable_product_name,
                    "code": product.plannable_product_code
                })
            
            logger.info(f"Retrieved {len(products)} plannable products for location {plannable_location_id}")
            return products
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex}")
            # Handle different types of GoogleAdsException
            if hasattr(ex, 'error') and hasattr(ex.error, 'message'):
                error_message = ex.error.message
            elif hasattr(ex, 'failure') and ex.failure.errors:
                error_message = ex.failure.errors[0].message
            else:
                error_message = str(ex)
            raise Exception(f"Google Ads API error: {error_message}")
        except Exception as e:
            logger.error(f"Error retrieving plannable products: {str(e)}")
            raise

    def search_customers(self, customer_id: str):
        """
        Search for customer clients using Google Ads API.
        
        Args:
            customer_id (str): The customer ID to search within
            
        Returns:
            List of customer clients
        """
        if not self.client:
            if not self._has_required_credentials():
                raise Exception("Google Ads API credentials are not configured. Please check your environment variables.")
            else:
                # Try to initialize client if credentials are now available
                self._initialize_client()

        try:
            google_ads_service = self.client.get_service("GoogleAdsService")
            
            # GAQL query to get customer clients
            query = """
                SELECT 
                    customer_client.id, 
                    customer_client.resource_name, 
                    customer_client.client_customer, 
                    customer_client.manager, 
                    customer_client.descriptive_name 
                FROM customer_client
            """
            
            # Make the search request
            search_request = self.client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            response = google_ads_service.search(request=search_request)
            
            # Format the response
            customers = []
            for row in response:
                customer_client = row.customer_client
                customers.append({
                    "id": str(customer_client.id),
                    "name": customer_client.descriptive_name or f"Customer {customer_client.id}"
                })
            
            logger.info(f"Retrieved {len(customers)} customers for customer ID {customer_id}")
            return customers
            
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex}")
            # Handle different types of GoogleAdsException
            if hasattr(ex, 'error') and hasattr(ex.error, 'message'):
                error_message = ex.error.message
            elif hasattr(ex, 'failure') and ex.failure.errors:
                error_message = ex.failure.errors[0].message
            else:
                error_message = str(ex)
            raise Exception(f"Google Ads API error: {error_message}")
        except Exception as e:
            logger.error(f"Error searching customers: {str(e)}")
            raise

    def generate_reach_forecast(self, request_params: dict):
        """
        Generate reach forecast using Google Ads API with exponential backoff for timeout errors.
        
        Args:
            request_params: Dictionary containing request parameters including start_date and end_date
            
        Returns:
            Dictionary containing reach forecast data
        """
        if not self._has_required_credentials():
            raise Exception("Google Ads credentials not configured")
        
        if not self.client:
            self._initialize_client()
        
        max_attempts = 3
        base_delay = 1  # Base delay in seconds
        
        for attempt in range(max_attempts):
            try:
                # Get the reach plan service
                reach_plan_service = self.client.get_service("ReachPlanService")
                
                # Create the request
                request = self.client.get_type("GenerateReachForecastRequest")
                request.customer_id = request_params["customer_id"]
                
                # Set campaign duration using dateRange with DateRange object
                campaign_duration = self.client.get_type("CampaignDuration")
                date_range = self.client.get_type("DateRange")
                date_range.start_date = request_params["start_date"]
                date_range.end_date = request_params["end_date"]
                campaign_duration.date_range = date_range
                request.campaign_duration = campaign_duration
                
                # Set currency code
                request.currency_code = request_params["currency_code"]
                
                # Set targeting
                # Set plannable location IDs
                request.targeting.plannable_location_ids.append(request_params["plannable_location_id"])
                
                # Set network
                request.targeting.network = self.client.enums.ReachPlanNetworkEnum[request_params["network"]]
                
                # Set audience targeting with user lists
                if request_params.get("user_list_id"):
                    user_list_info = self.client.get_type("UserListInfo")
                    user_list_info.user_list = f"customers/{request_params['customer_id']}/userLists/{request_params['user_list_id']}"
                    request.targeting.audience_targeting.user_lists.append(user_list_info)
                
                # Set planned products
                planned_products = [
                    {
                        "plannable_product_code": "TRUEVIEW_IN_STREAM",
                        "budget_micros": 1000000000000
                    },
                    {
                        "plannable_product_code": "NON_SKIP_AUCTION", 
                        "budget_micros": 1000000000000
                    }
                ]
                
                for product_data in planned_products:
                    planned_product = self.client.get_type("PlannedProduct")
                    planned_product.plannable_product_code = product_data["plannable_product_code"]
                    planned_product.budget_micros = product_data["budget_micros"]
                    request.planned_products.append(planned_product)
                
                # Make the API call
                logger.info(f"Generating reach forecast for customer {request_params['customer_id']} (attempt {attempt + 1})")
                response = reach_plan_service.generate_reach_forecast(request=request)
                
                # Process the response
                reach_curve_points = []
                for point in response.reach_curve.reach_forecasts:
                    reach_curve_points.append({
                        "cost_micros": point.cost_micros,
                        "reach": point.forecast_metrics.reach,
                        "impressions": point.forecast_metrics.impressions,
                        "frequency": point.forecast_metrics.frequency
                    })
                
                processed_planned_products = []
                for product in response.planned_products:
                    processed_planned_products.append({
                        "plannable_product_code": product.plannable_product_code,
                        "budget_micros": product.budget_micros
                    })
                
                result = {
                    "reach_curve": reach_curve_points,
                    "planned_products": processed_planned_products,
                    "currency_code": request_params["currency_code"],
                    "customer_id": request_params["customer_id"]
                }
                
                logger.info(f"Successfully generated reach forecast with {len(reach_curve_points)} curve points")
                return result
                
            except Exception as ex:
                # Check if it's a timeout or retryable error
                is_timeout = "timeout" in str(ex).lower() or "deadline" in str(ex).lower()
                is_last_attempt = attempt == max_attempts - 1
                
                if is_timeout and not is_last_attempt:
                    # Calculate exponential backoff delay with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Timeout error on attempt {attempt + 1}, retrying in {delay:.2f} seconds: {str(ex)}")
                    time.sleep(delay)
                    continue
                else:
                    # Handle non-timeout errors or final attempt
                    if isinstance(ex, GoogleAdsException):
                        logger.error(f"Google Ads API error: {ex}")
                        # Handle different types of GoogleAdsException
                        if hasattr(ex, 'error') and hasattr(ex.error, 'message'):
                            error_message = ex.error.message
                        elif hasattr(ex, 'failure') and ex.failure.errors:
                            error_message = ex.failure.errors[0].message
                        else:
                            error_message = str(ex)
                        raise Exception(f"Google Ads API error: {error_message}") from ex
                    else:
                        logger.error(f"Error generating reach forecast: {str(ex)}")
                        raise Exception(f"Error generating reach forecast: {str(ex)}") from ex
        
        # This should never be reached due to the loop structure, but just in case
        raise Exception("Max retry attempts exceeded for reach forecast generation")


# Global instance
google_ads_service = GoogleAdsService()