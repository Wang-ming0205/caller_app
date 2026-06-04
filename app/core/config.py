from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Barbershop CRM"
    SECRET_KEY: str = "change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    DATABASE_URL: str = "sqlite:///./barbershop.db"
    ENV: str = "dev"  # dev / prod
    ENABLE_SEED: bool = True
    CORS_ALLOW_ORIGINS_RAW: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def CORS_ALLOW_ORIGINS(self) -> list[str]:
        if self.CORS_ALLOW_ORIGINS_RAW.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS_RAW.split(",") if origin.strip()]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str):
        # Dev can run with a weak key; prod cannot.
        return value

settings = Settings()

if settings.ENV.lower() == "prod" and settings.SECRET_KEY in {"change_me", "change_this_to_a_long_random_secret"}:
    raise RuntimeError("Production ENV requires a strong SECRET_KEY in .env")
