from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""
    
    # App Info
    APP_NAME: str = "CV Screening Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,tiff,doc,docx"
    
    # OCR Settings
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    OCR_DPI: int = 300
    OCR_LANGUAGES: str = "eng"
    POPPLER_PATH: str = "/usr/bin"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # CRM Integration
    CRM_TYPE: str = "salesforce"
    CRM_API_URL: str = ""
    CRM_CLIENT_ID: str = ""
    CRM_CLIENT_SECRET: str = ""
    CRM_OAUTH_TOKEN_URL: str = ""
    
    # Matching Weights (must sum to 100)
    DEFAULT_SKILL_WEIGHT: int = 40
    DEFAULT_ROLE_WEIGHT: int = 20
    DEFAULT_TOOL_WEIGHT: int = 15
    DEFAULT_EXPERIENCE_WEIGHT: int = 15
    DEFAULT_PORTFOLIO_WEIGHT: int = 10
    DEFAULT_QUALITY_WEIGHT: int = 5
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed file extensions as a list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
