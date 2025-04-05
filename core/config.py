from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class DBSettings(BaseSettings):
    host: str
    port: int
    name: str
    user: str
    password: str

    model_config = SettingsConfigDict(env_prefix='DB_')


class SecuritySettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(env_prefix='SECURITY_')


db_settings = DBSettings()
security_settings = SecuritySettings()


