from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default="6379")

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    WAZZUP_API_KEY: str

    SECRET_KEY: str = Field(default="b2444904380b4eca7cb2cc5e12721d15b4ef32a9caa25df0e1b5839b1b5a16bf")
    ALGORITHM: str = Field(default="HS256")
    

settings = Settings()
