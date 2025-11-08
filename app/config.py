from pydantic_settings import BaseSettings
import logging


class Settings(BaseSettings):
    # Google Ads API Configuration
    google_ads_developer_token: str | None = None
    google_ads_client_id: str | None = None
    google_ads_client_secret: str | None = None
    google_ads_refresh_token: str | None = None
    google_ads_customer_id: str | None = None
    google_ads_login_customer_id: str | None = None
    
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