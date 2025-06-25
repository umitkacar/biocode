"""Configuration management"""
import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="BioCode", env="BIOCODE_APP_NAME")
    environment: str = Field(default="development", env="BIOCODE_ENVIRONMENT")
    debug: bool = Field(default=True, env="BIOCODE_DEBUG")
    
    # API
    api_host: str = Field(default="0.0.0.0", env="BIOCODE_API_HOST")
    api_port: int = Field(default=8000, env="BIOCODE_API_PORT")
    api_prefix: str = Field(default="/api/v1", env="BIOCODE_API_PREFIX")
    
    # Database
    db_url: str = Field(default="sqlite:///./biocode.db", env="BIOCODE_DB_URL")
    db_echo: bool = Field(default=False, env="BIOCODE_DB_ECHO")
    
    # Redis
    redis_url: Optional[str] = Field(default=None, env="BIOCODE_REDIS_URL")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="BIOCODE_PROMETHEUS_ENABLED")
    metrics_port: int = Field(default=9090, env="BIOCODE_METRICS_PORT")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="BIOCODE_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="BIOCODE_JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="BIOCODE_JWT_EXPIRE_MINUTES")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="BIOCODE_ALLOWED_ORIGINS"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "env_prefix": "BIOCODE_",
        "extra": "ignore"
    }


settings = Settings()