from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sistema Carvao"
    environment: str = "development"
    database_url: str = "sqlite:///./carvao.db"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    whatsapp_provider: str = "mock"
    whatsapp_api_url: str = ""
    whatsapp_token: str = ""
    manager_whatsapp: str = "+5599999999999"
    cors_origins: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET e obrigatoria. Gere um segredo forte antes de iniciar a aplicacao.")
    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    if not origins:
        raise RuntimeError("CORS_ORIGINS e obrigatoria. Informe a origem exata do frontend.")
    if "*" in origins:
        raise RuntimeError("CORS_ORIGINS nao pode usar '*'. Informe origens explicitas.")
    if settings.environment.lower() == "production" and len(origins) != 1:
        raise RuntimeError("Em producao, CORS_ORIGINS deve conter somente o dominio do frontend.")
    return settings
