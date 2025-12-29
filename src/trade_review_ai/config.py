"""Configuration management for Trade Review AI."""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Application configuration."""
    
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    default_lookback_days: int = Field(default=30, description="Default analysis period in days")
    max_trades_per_analysis: int = Field(default=100, description="Maximum trades to analyze at once")
    
    class Config:
        extra = "allow"


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        Config object with application settings
        
    Raises:
        ValueError: If required configuration is missing
    """
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment. "
            "Please set it in .env file or environment variables."
        )
    
    return Config(
        openai_api_key=api_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4"),
        default_lookback_days=int(os.getenv("DEFAULT_LOOKBACK_DAYS", "30")),
        max_trades_per_analysis=int(os.getenv("MAX_TRADES_PER_ANALYSIS", "100"))
    )
