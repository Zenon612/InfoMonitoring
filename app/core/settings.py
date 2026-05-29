from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    API_HOST: str = Field(..., validation_alias="API_HOST")
    API_PORT: str = Field(..., validation_alias="API_PORT")

    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")


    OPENAI_API_KEY: str | None = Field(None, validation_alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(..., validation_alias="OPENAI_MODEL")

    OUTPUT_DIR: str = Field(..., validation_alias="OUTPUT_DIR")


settings = Settings()

