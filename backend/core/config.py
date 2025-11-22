# ===================================
# core/config.py
# ===================================
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "MT5 Copy Trading Backend"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    MONGODB_URL: str = "mongodb+srv://kapardhikannekanti_db_user:3XoNc2gtr9lGY4oi@mt5-cluster.njyntuk.mongodb.net/?retryWrites=true&w=majority&appName=mt5-cluster"

    DATABASE_NAME: str = "mt5_copy_trading"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # OTP Settings
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6
    
    # SMS Settings (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    
    # Email Settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    
    # Trade Copier Integration
    TRADE_COPIER_BASE_URL: str = "http://localhost:8001"
    TRADE_COPIER_API_KEY: str = ""
    # IP restrictions for sensitive endpoints. Use ["0"] to allow all.
    RESTRICTED_IPS: List[str] = ["0"]

    # Maximum number of master folders/accounts allowed
    MAX_MASTER_FOLDER: int = 100
    
    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
print("DEBUG: config file executing...")
print("DEBUG: BASE_DIR ->", BASE_DIR)
print("DEBUG: Looking for env file at:", BASE_DIR / ".env")
print("DEBUG: Exists?", (BASE_DIR / ".env").exists())


settings = Settings()