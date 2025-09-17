# config.py
from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # Application Configuration
    app_name: str = Field(default="google-sdk-agent", description="Application name")
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_reload: bool = Field(default=False, description="Enable auto-reload in development")
    
    # Environment Configuration
    environment: str = Field(default="development", description="Deployment environment")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Google Cloud Configuration
    google_api_key: Optional[str] = Field(default=None, description="Google API key for Gemini")
    google_cloud_project: Optional[str] = Field(default=None, description="Google Cloud project ID")
    google_cloud_location: Optional[str] = Field(default=None, description="Google Cloud location/region")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model to use")
    google_use_vertex: bool = Field(default=False, description="Use Vertex AI instead of Google AI Studio")
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS Secret Access Key")
    aws_session_token: Optional[str] = Field(default=None, description="AWS Session Token")
    aws_region: Optional[str] = Field(default=None, description="AWS Region")
    
    # IBM Configuration
    x_ibm_client_id: Optional[str] = Field(default=None, description="IBM Client ID")
    x_ibm_client_secret: Optional[str] = Field(default=None, description="IBM Client Secret")
    
    # Other Configuration
    stage_name: str = Field(default="local", description="Stage name")
    llm_provider: str = Field(default="gemini", description="LLM Provider")
    claude_model_id: Optional[str] = Field(default=None, description="Claude Model ID")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    
    # MCP Configuration
    mcp_server_url: Optional[str] = Field(default=None, description="MCP server URL for HTTP streaming")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def is_cloud_run(self) -> bool:
        """Check if running on Google Cloud Run."""
        return os.getenv("K_SERVICE") is not None
    
    def is_aws_ecs(self) -> bool:
        """Check if running on AWS ECS."""
        return os.getenv("AWS_EXECUTION_ENV") is not None
    
    def is_local(self) -> bool:
        """Check if running locally."""
        return self.environment.lower() in ["local", "development"]

# Environment-specific settings
class DevelopmentSettings(Settings):
    environment: str = "development"
    api_reload: bool = True
    log_level: str = "DEBUG"
    
    class Config:
        env_file = ".env.development"

class StagingSettings(Settings):
    environment: str = "staging"
    api_reload: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env.staging"

class ProductionSettings(Settings):
    environment: str = "production"
    api_reload: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env.production"

def get_settings() -> Settings:
    """Factory function to get the right settings based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "staging":
        return StagingSettings()
    elif env == "development":
        return DevelopmentSettings()
    else:
        return Settings()

# Global settings instance
settings = get_settings()
