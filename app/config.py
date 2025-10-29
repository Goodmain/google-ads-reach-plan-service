from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    # Google Ads API Configuration
    google_ads_developer_token: Optional[str] = None
    google_ads_client_id: Optional[str] = None
    google_ads_client_secret: Optional[str] = None
    google_ads_refresh_token: Optional[str] = None
    google_ads_customer_id: Optional[str] = None
    google_ads_login_customer_id: Optional[str] = None
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # Docker/Container Configuration
    container_mode: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def configure_logging(self):
        """Configure logging for the application"""
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler()
            ]
        )


settings = Settings()
settings.configure_logging()