from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    app_name:str="LifeVerse"; environment:str="development"; database_url:str="sqlite:///./lifeverse.db"; log_level:str="INFO"
    model_config=SettingsConfigDict(env_prefix="LIFEVERSE_",env_file=".env",extra="ignore")
@lru_cache
def get_settings()->Settings:return Settings()
