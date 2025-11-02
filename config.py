from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    BOT_TOKEN: str
    CHANNEL_ID: str  # Channel username or ID
    ADMIN_IDS: Optional[str] = None  # Comma-separated string of admin IDs
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  #
    
    def get_admin_ids(self) -> List[int]:
        """Parse ADMIN_IDS from environment variable (comma-separated)"""
        if not self.ADMIN_IDS:
            return []
        try:
            return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]
        except (ValueError, AttributeError):
            return []


settings = Settings()

