"""Application configuration loaded from environment variables.

Uses pydantic-settings so values can be supplied via .env, env vars, or
docker-compose. All settings have demo-safe defaults so the app boots
without any secrets configured.
"""

from __future__ import annotations

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    The `env_file=".env"` config means a local `.env` file is auto-loaded.
    Unknown env vars are ignored so adding new ones never breaks startup.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- LLM (TIP.AI / LiteLLM proxy) ---------------------------------------
    use_mock_llm: bool = True
    litellm_base_url: str = "https://d1t4hkdc2i746c.cloudfront.net"
    litellm_api_key: str = ""
    litellm_model: str = "us.anthropic.claude-sonnet-4-6"
    # Some models (e.g. claude-opus-4-7) reject `temperature`. Empty string => omit.
    litellm_temperature: str = "0.7"

    # --- Weather (OpenWeatherMap) -------------------------------------------
    openweather_api_key: str = ""

    # --- Tavily (live web search for the concierge agent) -------------------
    # When TAVILY_API_KEY is empty, the concierge agent transparently falls
    # back to seed-derived mock results so the demo always works offline.
    tavily_api_key: str = ""
    tavily_max_results: int = 5
    tavily_timeout_seconds: float = 8.0
    # Default value of `preferences.live_search_enabled` for guests that have
    # not toggled the flag explicitly. The demo runs the live concierge agent
    # by default so judges immediately see Tavily-grounded recommendations;
    # the agent transparently falls back to seed-derived mocks when
    # TAVILY_API_KEY is missing or the API call fails.
    live_search_enabled_default: bool = True

    # --- CORS ---------------------------------------------------------------
    # Stored as the raw env var (comma-separated) and exposed as a list via
    # the computed property below.
    allowed_origins_raw: str = Field(
        default="http://localhost:3000",
        validation_alias="ALLOWED_ORIGINS",
    )

    # --- Session ------------------------------------------------------------
    session_secret: str = Field(
        default="bonvoy-demo-session-secret-change-me",
        validation_alias="SESSION_SECRET",
    )

    # --- App ----------------------------------------------------------------
    debug: bool = True
    seeds_path: str = "../data/seeds"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated CORS origins into a list."""
        return [o.strip() for o in self.allowed_origins_raw.split(",") if o.strip()]

    @property
    def litellm_temperature_value(self) -> float | None:
        """Return the temperature as a float, or None if the env var is blank."""
        raw = self.litellm_temperature.strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None


settings = Settings()
