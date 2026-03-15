"""
HábitosFam – backend/config.py
Application settings via pydantic-settings + python-dotenv.
Supports SQLite, PostgreSQL (Supabase), and MySQL.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────
    app_name: str = "HábitosFam"
    app_version: str = "2.0.0"
    debug: bool = True
    secret_key: str = "dev-secret-change-in-production"

    # ── Admin ─────────────────────────────────────
    admin_pin: str = "1234"
    pin_length: int = 4
    token_prefix: str = "HFAM-"

    # ── Database ──────────────────────────────────
    # Default: SQLite (local file)
    database_url: str = "sqlite:///./habitosfam.db"

    # ── CORS ──────────────────────────────────────
    cors_origins: str = "http://localhost:8765,http://localhost:3000"

    # ── Server ────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8765

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def db_engine_type(self) -> str:
        """Returns 'sqlite', 'postgresql', or 'mysql'"""
        url = self.database_url.lower()
        if url.startswith("sqlite"):
            return "sqlite"
        if "postgresql" in url or "postgres" in url:
            return "postgresql"
        if "mysql" in url:
            return "mysql"
        return "unknown"

    @property
    def is_sqlite(self) -> bool:
        return self.db_engine_type == "sqlite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton settings instance
settings = Settings()
