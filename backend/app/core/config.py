"""Application configuration via environment variables (pydantic-settings).

All pricing coefficients below are *default assumptions* used to seed the DB
pricing config; the active DB row overrides them at runtime. They are indicative
business assumptions, NOT verified market rates. See README section "Pricing".
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Metro Revenue Intelligence"
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # CORS: comma-separated origins allowed to call the API (dev frontend).
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # Default dev DB is SQLite so the stack runs with zero external setup.
    # Point DATABASE_URL at PostgreSQL for production, e.g.
    # postgresql+psycopg://user:pass@localhost:5432/metro
    database_url: str = "sqlite:///./metro_dev.db"

    # Timezone the stored dates/time-bands represent (naive local metro time).
    timezone: str = "Asia/Kolkata"

    # ---- AI provider (Anthropic Claude) for sales-proposal copy ----
    # Credentials stay server-side only; never exposed to the browser.
    anthropic_api_key: str | None = None
    ai_model: str = "claude-sonnet-4-5"
    ai_request_timeout: float = 30.0
    ai_max_tokens: int = 1500
    ai_max_retries: int = 2

    @property
    def ai_enabled(self) -> bool:
        return bool(self.anthropic_api_key)

    # ---- Default pricing assumptions (indicative, not market-verified) ----
    pricing_model_version: str = "v1.0-heuristic"
    base_rate_per_sqm: float = 1800.0  # INR / sqm / month, area-priced spaces
    base_panel_rate: float = 45000.0  # INR / month, unit-priced ad inventory
    reference_daily_footfall: int = 20000
    footfall_elasticity: float = 0.3
    min_footfall_factor: float = 0.6
    max_footfall_factor: float = 1.8
    reference_visibility: float = 5.0  # on a 1-10 scale
    visibility_weight: float = 0.08  # per point away from reference
    min_visibility_factor: float = 0.7
    max_visibility_factor: float = 1.4

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
