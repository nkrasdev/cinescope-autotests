from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_url: str = Field(default="https://api.dev-cinescope.coconutqa.ru")
    base_ui_url: str = Field(default="https://dev-cinescope.coconutqa.ru")
    base_auth_url: str = Field(default="https://auth.dev-cinescope.coconutqa.ru")

    admin_email: str = Field(default=None)
    admin_password: str = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
