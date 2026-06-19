import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    Uses Pydantic Settings for validation and type safety.
    """
    # Base path of the project
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Browser Automation Settings
    BROWSER_HEADLESS: bool = False
    BROWSER_TIMEOUT: int = 30000  # in milliseconds
    SCREENSHOTS_DIR: Path = Path("screenshots")
    LOGS_DIR: Path = Path("logs")

    # OpenRouter LLM Configurations
    DEFAULT_LLM_PROVIDER: str = "openrouter"
    DEFAULT_LLM_MODEL: str = "google/gemini-2.5-flash"
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Configuration for loading from .env
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_absolute_screenshots_dir(self) -> Path:
        """Returns resolved absolute path to the screenshots directory, ensuring it exists."""
        resolved = self.BASE_DIR / self.SCREENSHOTS_DIR
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    def get_absolute_logs_dir(self) -> Path:
        """Returns resolved absolute path to the logs directory, ensuring it exists."""
        resolved = self.BASE_DIR / self.LOGS_DIR
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

# Global settings instance
settings = Settings()
