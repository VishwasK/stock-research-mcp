from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mcp_api_key: str = "dev-only-change-me"
    jawsdb_url: str | None = None
    database_url: str | None = None
    allowed_origins: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def resolved_database_url(self) -> str:
        url = self.jawsdb_url or self.database_url or "sqlite:///./stock_research.db"
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    @property
    def origin_allowlist(self) -> set[str]:
        return {x.strip() for x in self.allowed_origins.split(",") if x.strip()}

@lru_cache
def get_settings() -> Settings:
    return Settings()
