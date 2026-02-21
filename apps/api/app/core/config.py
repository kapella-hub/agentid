"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "AgentID"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/v1"

    # Database
    database_url: str = "postgresql+asyncpg://agentid:agentid@localhost:5432/agentid"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    agent_token_expire_minutes: int = 60

    # Mailgun
    mailgun_api_key: str = ""
    mailgun_domain: str = "agentid.io"
    mailgun_base_url: str = "https://api.mailgun.net/v3"
    mailgun_webhook_signing_key: str = ""

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_application_fee_pct: float = 2.0

    # Vault encryption
    vault_master_key: str = ""  # Base64-encoded 32-byte key (for local dev; use KMS in prod)

    # Webhook callback base URL (set to your public API URL in production)
    webhook_base_url: str = "https://api.agentid.io"

    # CORS
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    # Rate limiting
    rate_limit_per_minute: int = 60

    model_config = {"env_prefix": "AGENTID_", "env_file": ".env"}


settings = Settings()
