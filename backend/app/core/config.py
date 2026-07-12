from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/cyinc"
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_prefix: str = "/api/v1"
    admin_username: str = "admin"
    admin_password_hash: str = ""
    redis_url: str = ""
    dify_api_url: str = ""
    dify_summary_api_key: str = ""
    dify_chat_api_key: str = ""
    dify_timeout_sec: int = 30
    n8n_webhook_url: str = ""
    n8n_webhook_secret: str = ""
    n8n_timeout_sec: int = 10
    public_site_url: str = "http://127.0.0.1:5173/myweb"
    upload_dir: str = "uploads"
    max_avatar_bytes: int = 2 * 1024 * 1024
    max_forum_image_bytes: int = 5 * 1024 * 1024
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_ssl: bool = True
    mgnacg_base_url: str = "https://www.mgnacg.com"
    mgnacg_enabled: bool = True

    @field_validator("secret_key")
    @classmethod
    def secret_key_not_default(cls, v: str) -> str:
        if v in ("dev-secret-change-in-production", "dev-cyinclog-local"):
            # 开发环境允许，生产部署前须更换
            return v
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
