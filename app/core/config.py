from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically find the absolute path to the 'app' directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):

    google_api_key: str

    exa_api_key: str 

    crawler_mode: Literal["cdp", "builtin"] = "builtin"
    
    crawler_cdp_url: str | None = None

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]