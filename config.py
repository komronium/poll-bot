from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    CHANNEL_ID: str
    ADMIN_IDS: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def get_admin_ids(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        try:
            return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]
        except (ValueError, AttributeError):
            return []


settings = Settings()
