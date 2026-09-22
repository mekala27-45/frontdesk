from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = (
        "postgresql+psycopg://frontdesk:local-development-only@127.0.0.1:55432/frontdesk"
    )
    app_secret: str = "local-meta-secret"
    verify_token: str = "local-verify-token"
    ops_token: str = "local-ops-token"
    simulator_secret: str = "local-simulator-secret"
    reminder_secret: str = "local-reminder-secret"
    meta_token: str = ""
    meta_phone_id: str = ""
    meta_graph_version: str = "v23.0"
    google_calendar_id: str = ""
    google_application_credentials: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    llm_model: str = ""
    llm_budget_usd: float = 0.05
    public_demo: bool = False
