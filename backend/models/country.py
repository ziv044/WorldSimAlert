from pydantic import BaseModel
from typing import Dict

from .meta import Meta
from .demographics import Demographics
from .workforce import Workforce
from .infrastructure import Infrastructure
from .economy import Economy
from .budget import Budget
from .sectors import Sector
from .military import Military
from .military_inventory import MilitaryInventory
from .relations import BilateralRelation
from .indices import Indices


class CountryState(BaseModel):
    meta: Meta
    demographics: Demographics
    workforce: Workforce
    infrastructure: Infrastructure
    economy: Economy
    budget: Budget
    sectors: Dict[str, Sector]
    military: Military
    military_inventory: MilitaryInventory
    relations: Dict[str, BilateralRelation]
    indices: Indices
