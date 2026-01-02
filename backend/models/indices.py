from pydantic import BaseModel


class Indices(BaseModel):
    happiness: int  # 0-100
    hdi: float  # 0-1 (Human Development Index)
    inequality_gini: float  # 0-1 (lower = more equal)
    corruption: int  # 0-100 (lower = cleaner)
    stability: int  # 0-100
    public_trust: int  # 0-100
    press_freedom: int  # 0-100
    ease_of_business: int  # 0-100
