from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DB_HOST: str = Field(..., env='DB_HOST')
    DB_PORT: str = Field(..., env='DB_PORT')
    DB_NAME: str = Field(..., env='DB_NAME')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')


settings = Settings()
