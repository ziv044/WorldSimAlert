"""
Tests for map service.
"""
import pytest
import json
import tempfile
from pathlib import Path

from backend.services.map_service import MapService
from backend.models.map import Coordinates
from backend.models.cities import City, CityList, CityType
from backend.models.bases import MilitaryBase, BaseList, BaseType
from backend.models.units import MilitaryUnit, UnitList, UnitCategory, UnitStatus


class TestMapService:
    """Tests for MapService."""

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database directory."""
        map_dir = tmp_path / "map"
        map_dir.mkdir()
        return tmp_path

    @pytest.fixture
    def map_service(self, temp_db, monkeypatch):
        """Create MapService with temp directory."""
        from backend import config
        monkeypatch.setattr(config.config, "DB_PATH", temp_db)

        service = MapService()
        service.db_path = temp_db
        service.map_path = temp_db / "map"
        return service

    @pytest.fixture
    def sample_cities_data(self):
        """Sample cities JSON data."""
        return {
            "country_code": "TST",
            "total_urban_population": 700000,
            "cities": [
                {
                    "id": "city_1",
                    "name": "Test City",
                    "country_code": "TST",
                    "location": {"lat": 31.0, "lng": 35.0},
                    "population": 500000,
                    "city_type": "capital",
                    "is_capital": True
                },
                {
                    "id": "city_2",
                    "name": "Port City",
                    "country_code": "TST",
                    "location": {"lat": 32.0, "lng": 34.5},
                    "population": 200000,
                    "city_type": "major",
                    "is_port": True
                }
            ]
        }

    @pytest.fixture
    def sample_bases_data(self):
        """Sample bases JSON data."""
        return {
            "country_code": "TST",
            "bases": [
                {
                    "id": "base_1",
                    "name": "Air Base",
                    "country_code": "TST",
                    "location": {"lat": 31.0, "lng": 35.0},
                    "base_type": "air_base",
                    "status": "operational",
                    "capabilities": {
                        "max_aircraft": 50,
                        "has_runway": True
                    }
                }
            ]
        }

    @pytest.fixture
    def sample_units_data(self):
        """Sample units JSON data."""
        return {
            "country_code": "TST",
            "units": [
                {
                    "id": "unit_1",
                    "name": "Test Squadron",
                    "country_code": "TST",
                    "unit_type": "F-35",
                    "category": "aircraft",
                    "quantity": 20,
                    "location": {"lat": 31.0, "lng": 35.0},
                    "home_base_id": "base_1",
                    "status": "idle"
                }
            ]
        }

    # ==================== Cities Tests ====================

    def test_load_cities_creates_empty_list_if_no_file(self, map_service):
        """Test loading cities when file doesn't exist."""
        cities = map_service.load_cities("NONEXISTENT")
        assert cities.country_code == "NONEXISTENT"
        assert len(cities.cities) == 0

    def test_load_cities_from_file(self, map_service, sample_cities_data):
        """Test loading cities from file."""
        file_path = map_service.map_path / "cities_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        cities = map_service.load_cities("TST")
        assert len(cities.cities) == 2
        assert cities.cities[0].id == "city_1"
        assert cities.cities[0].is_capital is True

    def test_save_cities(self, map_service):
        """Test saving cities."""
        city_list = CityList(
            country_code="TST",
            cities=[
                City(
                    id="new_city",
                    name="New City",
                    country_code="TST",
                    location=Coordinates(lat=31.0, lng=35.0),
                    population=100000,
                    city_type=CityType.SMALL
                )
            ]
        )

        map_service.save_cities(city_list)

        # Verify file was created
        file_path = map_service.map_path / "cities_TST.json"
        assert file_path.exists()

        # Verify content
        with open(file_path, "r") as f:
            data = json.load(f)
        assert data["country_code"] == "TST"
        assert len(data["cities"]) == 1

    def test_get_city(self, map_service, sample_cities_data):
        """Test getting specific city."""
        file_path = map_service.map_path / "cities_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        city = map_service.get_city("TST", "city_1")
        assert city is not None
        assert city.name == "Test City"

    def test_get_city_not_found(self, map_service, sample_cities_data):
        """Test getting non-existent city."""
        file_path = map_service.map_path / "cities_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        city = map_service.get_city("TST", "nonexistent")
        assert city is None

    # ==================== Bases Tests ====================

    def test_load_bases_from_file(self, map_service, sample_bases_data):
        """Test loading bases from file."""
        file_path = map_service.map_path / "bases_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_bases_data, f)

        bases = map_service.load_bases("TST")
        assert len(bases.bases) == 1
        assert bases.bases[0].id == "base_1"
        assert bases.bases[0].base_type == BaseType.AIR_BASE

    def test_save_bases(self, map_service):
        """Test saving bases."""
        base_list = BaseList(
            country_code="TST",
            bases=[
                MilitaryBase(
                    id="new_base",
                    name="New Base",
                    country_code="TST",
                    location=Coordinates(lat=31.0, lng=35.0),
                    base_type=BaseType.NAVAL_BASE
                )
            ]
        )

        map_service.save_bases(base_list)

        file_path = map_service.map_path / "bases_TST.json"
        assert file_path.exists()

    # ==================== Units Tests ====================

    def test_load_units_from_file(self, map_service, sample_units_data):
        """Test loading units from file."""
        file_path = map_service.map_path / "units_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_units_data, f)

        units = map_service.load_units("TST")
        assert len(units.units) == 1
        assert units.units[0].id == "unit_1"
        assert units.units[0].category == UnitCategory.AIRCRAFT

    def test_update_unit(self, map_service, sample_units_data):
        """Test updating a unit."""
        file_path = map_service.map_path / "units_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_units_data, f)

        # Load and modify unit
        unit = map_service.get_unit("TST", "unit_1")
        assert unit is not None

        unit.status = UnitStatus.DEPLOYED
        unit.location = Coordinates(lat=32.0, lng=34.0)
        map_service.update_unit("TST", unit)

        # Reload and verify
        map_service.clear_cache("TST")
        updated = map_service.get_unit("TST", "unit_1")
        assert updated.status == UnitStatus.DEPLOYED
        assert updated.location.lat == 32.0

    # ==================== Full Map Data Tests ====================

    def test_get_full_map_data(self, map_service, sample_cities_data, sample_bases_data, sample_units_data):
        """Test getting complete map data."""
        # Setup files
        with open(map_service.map_path / "cities_TST.json", "w") as f:
            json.dump(sample_cities_data, f)
        with open(map_service.map_path / "bases_TST.json", "w") as f:
            json.dump(sample_bases_data, f)
        with open(map_service.map_path / "units_TST.json", "w") as f:
            json.dump(sample_units_data, f)

        data = map_service.get_full_map_data("TST")

        assert data["country_code"] == "TST"
        assert len(data["cities"]) == 2
        assert len(data["bases"]) == 1
        assert len(data["units"]) == 1

    # ==================== Cache Tests ====================

    def test_cache_is_used(self, map_service, sample_cities_data):
        """Test that cache is used on second load."""
        file_path = map_service.map_path / "cities_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        # First load
        cities1 = map_service.load_cities("TST")

        # Modify file (but cache should be used)
        sample_cities_data["cities"][0]["name"] = "Modified Name"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        # Second load should use cache
        cities2 = map_service.load_cities("TST")
        assert cities2.cities[0].name == "Test City"  # Original name

    def test_clear_cache(self, map_service, sample_cities_data):
        """Test clearing cache."""
        file_path = map_service.map_path / "cities_TST.json"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        # First load
        cities1 = map_service.load_cities("TST")

        # Modify file
        sample_cities_data["cities"][0]["name"] = "Modified Name"
        with open(file_path, "w") as f:
            json.dump(sample_cities_data, f)

        # Clear cache
        map_service.clear_cache("TST")

        # Second load should read from file
        cities2 = map_service.load_cities("TST")
        assert cities2.cities[0].name == "Modified Name"
