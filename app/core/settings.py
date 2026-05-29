from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    API_HOST: str = Field(
        default="0.0.0.0",  # nosec: для разработки; в продакшене ограничить до localhost
        validation_alias="API_HOST",
    )
    API_PORT: str = Field(default="8000", validation_alias="API_PORT")

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost/infomon",
        validation_alias="DATABASE_URL",
    )

    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo", validation_alias="OPENAI_MODEL")

    OUTPUT_DIR: str = Field(default="./outputs", validation_alias="OUTPUT_DIR")


settings = Settings()

