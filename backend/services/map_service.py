"""
Map service for loading and managing geographic data.
Handles cities, bases, units, and border data.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from backend.config import config
from backend.models.map import Coordinates, MapData, CountryBorders, BoundingBox
from backend.models.cities import City, CityList, CityType, CityInfrastructure
from backend.models.bases import MilitaryBase, BaseList, BaseType, BaseStatus, BaseCapabilities
from backend.models.units import MilitaryUnit, UnitList, UnitCategory, UnitStatus
from backend.models.active_operation import ActiveOperation, OperationsList


class MapService:
    """Service for map-related data operations."""

    def __init__(self):
        self.db_path = config.DB_PATH
        self.map_path = self.db_path / "map"
        self._cities_cache: Dict[str, CityList] = {}
        self._bases_cache: Dict[str, BaseList] = {}
        self._units_cache: Dict[str, UnitList] = {}
        self._borders_cache: Dict[str, CountryBorders] = {}
        self._operations_cache: Dict[str, OperationsList] = {}

    def _ensure_map_dir(self):
        """Ensure map directory exists."""
        self.map_path.mkdir(parents=True, exist_ok=True)

    # ==================== Cities ====================

    def load_cities(self, country_code: str) -> CityList:
        """Load cities for a country."""
        if country_code in self._cities_cache:
            return self._cities_cache[country_code]

        file_path = self.map_path / f"cities_{country_code.upper()}.json"
        if not file_path.exists():
            return CityList(country_code=country_code, cities=[])

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cities = []
        for city_data in data.get("cities", []):
            # Convert nested dicts to proper models
            city_data["location"] = Coordinates(**city_data["location"])
            city_data["city_type"] = CityType(city_data.get("city_type", "medium"))
            if "infrastructure" in city_data:
                city_data["infrastructure"] = CityInfrastructure(**city_data["infrastructure"])
            cities.append(City(**city_data))

        city_list = CityList(
            country_code=country_code,
            cities=cities,
            total_urban_population=data.get("total_urban_population", sum(c.population for c in cities))
        )
        self._cities_cache[country_code] = city_list
        return city_list

    def save_cities(self, city_list: CityList) -> None:
        """Save cities for a country."""
        self._ensure_map_dir()
        file_path = self.map_path / f"cities_{city_list.country_code.upper()}.json"

        data = {
            "country_code": city_list.country_code,
            "total_urban_population": city_list.total_urban_population,
            "cities": [city.model_dump() for city in city_list.cities]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self._cities_cache[city_list.country_code] = city_list

    def get_city(self, country_code: str, city_id: str) -> Optional[City]:
        """Get a specific city by ID."""
        city_list = self.load_cities(country_code)
        return city_list.get_by_id(city_id)

    # ==================== Bases ====================

    def load_bases(self, country_code: str) -> BaseList:
        """Load military bases for a country."""
        if country_code in self._bases_cache:
            return self._bases_cache[country_code]

        file_path = self.map_path / f"bases_{country_code.upper()}.json"
        if not file_path.exists():
            return BaseList(country_code=country_code, bases=[])

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        bases = []
        for base_data in data.get("bases", []):
            base_data["location"] = Coordinates(**base_data["location"])
            base_data["base_type"] = BaseType(base_data.get("base_type", "army_base"))
            base_data["status"] = BaseStatus(base_data.get("status", "operational"))
            if "capabilities" in base_data:
                base_data["capabilities"] = BaseCapabilities(**base_data["capabilities"])
            bases.append(MilitaryBase(**base_data))

        base_list = BaseList(country_code=country_code, bases=bases)
        self._bases_cache[country_code] = base_list
        return base_list

    def save_bases(self, base_list: BaseList) -> None:
        """Save military bases for a country."""
        self._ensure_map_dir()
        file_path = self.map_path / f"bases_{base_list.country_code.upper()}.json"

        data = {
            "country_code": base_list.country_code,
            "bases": [base.model_dump() for base in base_list.bases]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self._bases_cache[base_list.country_code] = base_list

    def get_base(self, country_code: str, base_id: str) -> Optional[MilitaryBase]:
        """Get a specific base by ID."""
        base_list = self.load_bases(country_code)
        return base_list.get_by_id(base_id)

    # ==================== Units ====================

    def load_units(self, country_code: str) -> UnitList:
        """Load military units for a country."""
        if country_code in self._units_cache:
            return self._units_cache[country_code]

        file_path = self.map_path / f"units_{country_code.upper()}.json"
        if not file_path.exists():
            return UnitList(country_code=country_code, units=[])

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        units = []
        for unit_data in data.get("units", []):
            unit_data["location"] = Coordinates(**unit_data["location"])
            unit_data["category"] = UnitCategory(unit_data.get("category", "ground"))
            unit_data["status"] = UnitStatus(unit_data.get("status", "idle"))
            units.append(MilitaryUnit(**unit_data))

        unit_list = UnitList(country_code=country_code, units=units)
        self._units_cache[country_code] = unit_list
        return unit_list

    def save_units(self, unit_list: UnitList) -> None:
        """Save military units for a country."""
        self._ensure_map_dir()
        file_path = self.map_path / f"units_{unit_list.country_code.upper()}.json"

        data = {
            "country_code": unit_list.country_code,
            "units": [unit.model_dump() for unit in unit_list.units]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self._units_cache[unit_list.country_code] = unit_list

    def get_unit(self, country_code: str, unit_id: str) -> Optional[MilitaryUnit]:
        """Get a specific unit by ID."""
        unit_list = self.load_units(country_code)
        return unit_list.get_by_id(unit_id)

    def update_unit(self, country_code: str, unit: MilitaryUnit) -> None:
        """Update a specific unit."""
        unit_list = self.load_units(country_code)
        for i, u in enumerate(unit_list.units):
            if u.id == unit.id:
                unit_list.units[i] = unit
                break
        self.save_units(unit_list)

    # ==================== Borders ====================

    def load_borders(self, country_code: str) -> Optional[CountryBorders]:
        """Load border data for a country."""
        if country_code in self._borders_cache:
            return self._borders_cache[country_code]

        file_path = self.map_path / f"borders_{country_code.upper()}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        borders = CountryBorders(
            country_code=data["country_code"],
            name=data["name"],
            bounding_box=BoundingBox(**data["bounding_box"]),
            center=Coordinates(**data["center"]),
            land_area_km2=data["land_area_km2"],
            neighbors=data.get("neighbors", [])
        )
        self._borders_cache[country_code] = borders
        return borders

    def get_neighbor_data(self, country_code: str) -> List[Dict[str, Any]]:
        """Get data about neighboring countries."""
        file_path = self.map_path / f"borders_{country_code.upper()}.json"
        if not file_path.exists():
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("neighbor_data", [])

    # ==================== Operations ====================

    def load_operations(self, country_code: str) -> OperationsList:
        """Load active operations for a country."""
        if country_code in self._operations_cache:
            return self._operations_cache[country_code]

        file_path = self.map_path / f"operations_{country_code.upper()}.json"
        if not file_path.exists():
            return OperationsList(country_code=country_code, operations=[])

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        operations = []
        for op_data in data.get("operations", []):
            # Convert string dates to datetime
            for date_field in ["created_at", "started_at", "estimated_completion", "completed_at"]:
                if op_data.get(date_field):
                    op_data[date_field] = datetime.fromisoformat(op_data[date_field])

            op_data["origin_location"] = Coordinates(**op_data["origin_location"])
            op_data["target_location"] = Coordinates(**op_data["target_location"])
            operations.append(ActiveOperation(**op_data))

        ops_list = OperationsList(country_code=country_code, operations=operations)
        self._operations_cache[country_code] = ops_list
        return ops_list

    def save_operations(self, ops_list: OperationsList) -> None:
        """Save operations for a country."""
        self._ensure_map_dir()
        file_path = self.map_path / f"operations_{ops_list.country_code.upper()}.json"

        data = {
            "country_code": ops_list.country_code,
            "operations": [op.model_dump() for op in ops_list.operations]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self._operations_cache[ops_list.country_code] = ops_list

    def add_operation(self, country_code: str, operation: ActiveOperation) -> None:
        """Add a new operation."""
        ops_list = self.load_operations(country_code)
        ops_list.operations.append(operation)
        self.save_operations(ops_list)

    def get_operation(self, country_code: str, operation_id: str) -> Optional[ActiveOperation]:
        """Get a specific operation by ID."""
        ops_list = self.load_operations(country_code)
        return ops_list.get_by_id(operation_id)

    def update_operation(self, country_code: str, operation: ActiveOperation) -> None:
        """Update an operation."""
        ops_list = self.load_operations(country_code)
        for i, op in enumerate(ops_list.operations):
            if op.id == operation.id:
                ops_list.operations[i] = operation
                break
        self.save_operations(ops_list)

    # ==================== Full Map Data ====================

    def get_full_map_data(self, country_code: str) -> Dict[str, Any]:
        """Get complete map data for a country."""
        cities = self.load_cities(country_code)
        bases = self.load_bases(country_code)
        units = self.load_units(country_code)
        borders = self.load_borders(country_code)
        operations = self.load_operations(country_code)
        neighbors = self.get_neighbor_data(country_code)

        return {
            "country_code": country_code,
            "borders": borders.model_dump() if borders else None,
            "cities": [c.model_dump() for c in cities.cities],
            "bases": [b.model_dump() for b in bases.bases],
            "units": [u.model_dump() for u in units.units],
            "active_operations": [op.model_dump() for op in operations.get_active()],
            "neighbors": neighbors
        }

    def clear_cache(self, country_code: Optional[str] = None) -> None:
        """Clear cached data."""
        if country_code:
            self._cities_cache.pop(country_code, None)
            self._bases_cache.pop(country_code, None)
            self._units_cache.pop(country_code, None)
            self._borders_cache.pop(country_code, None)
            self._operations_cache.pop(country_code, None)
        else:
            self._cities_cache.clear()
            self._bases_cache.clear()
            self._units_cache.clear()
            self._borders_cache.clear()
            self._operations_cache.clear()


# Singleton instance
map_service = MapService()
