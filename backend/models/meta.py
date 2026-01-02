from pydantic import BaseModel
from datetime import date


class TimeConfig(BaseModel):
    real_seconds_per_game_day: float = 1.0
    paused: bool = False


class GameDate(BaseModel):
    year: int = 2024
    month: int = 1
    day: int = 1

    @property
    def as_date(self) -> date:
        return date(self.year, self.month, self.day)


class Meta(BaseModel):
    country_code: str  # "ISR", "USA", etc.
    country_name: str  # "Israel"
    government_type: str  # "Parliamentary Democracy"
    game_start_year: int = 2024
    current_date: GameDate
    time_config: TimeConfig
    total_game_days_elapsed: int = 0
