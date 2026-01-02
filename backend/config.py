from pydantic_settings import BaseSettings
from pathlib import Path


class GameConfig(BaseSettings):
    # Paths
    DB_PATH: Path = Path("db")

    # Game Clock
    REAL_SECONDS_PER_GAME_DAY: float = 1.0  # 1 real second = 1 game day
    GAME_START_YEAR: int = 2024

    # Tick Intervals (in game days)
    ECONOMIC_TICK_DAYS: int = 30      # Monthly
    DEMOGRAPHIC_TICK_DAYS: int = 180  # Bi-annually
    DEVELOPMENT_TICK_DAYS: int = 90   # Quarterly
    POLITICAL_TICK_DAYS: int = 365    # Yearly
    EVENT_CHECK_DAYS: int = 30        # Monthly

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    class Config:
        env_file = ".env"


config = GameConfig()
