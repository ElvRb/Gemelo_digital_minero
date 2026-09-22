"""
Configuration settings for the Digital Twin Mining Platform.
Supports PostgreSQL with transparent SQLite fallback for local zero-config execution.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Resilience-Driven Digital Twin for Underground Mining")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_mining_digital_twin_jwt_token_2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mining_digital_twin.db")
    
    # Scientific Simulation & Statistics Settings
    DEFAULT_RANDOM_SEED: int = int(os.getenv("DEFAULT_RANDOM_SEED", "42"))
    MONTE_CARLO_RUNS: int = int(os.getenv("MONTE_CARLO_RUNS", "500"))
    SIMULATION_HORIZON_DAYS: int = int(os.getenv("SIMULATION_HORIZON_DAYS", "365"))
    BOOTSTRAP_ITERATIONS: int = int(os.getenv("BOOTSTRAP_ITERATIONS", "10000"))
    
    # API & Streamlit Ports
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))

settings = Settings()
