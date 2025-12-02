from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str = "crop-insurance-backend"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MODEL_SERVICE_URL: str = "http://localhost:8001/predict"
    UPLOAD_FOLDER: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
