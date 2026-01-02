"""
Tests for Unit Engine.
"""
import pytest
import json
from datetime import datetime, timedelta

from backend.engine.unit_engine import UnitEngine, MovementResult
from backend.models.map import Coordinates
from backend.models.units import MilitaryUnit, UnitCategory, UnitStatus
from backend.models.bases import MilitaryBase, BaseType, BaseCapabilities


class TestUnitEngine:
    """Tests for UnitEngine."""

    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database directory."""
        map_dir = tmp_path / "map"
        map_dir.mkdir()
        return tmp_path

    @pytest.fixture
    def setup_map_service(self, temp_db, monkeypatch):
        """Setup map service with temp directory."""
        from backend import config
        from backend.services import map_service as ms_module

        monkeypatch.setattr(config.config, "DB_PATH", temp_db)

        # Reset singleton
        ms_module.map_service.db_path = temp_db
        ms_module.map_service.map_path = temp_db / "map"
        ms_module.map_service.clear_cache()

        return ms_module.map_service

    @pytest.fixture
    def sample_units_data(self):
        """Sample units data."""
        return {
            "country_code": "TST",
            "units": [
                {
                    "id": "aircraft_1",
                    "name": "Fighter Squadron",
                    "country_code": "TST",
                    "unit_type": "F-35",
                    "category": "aircraft",
                    "quantity": 20,
                    "location": {"lat": 31.0, "lng": 35.0},
                    "home_base_id": "base_1",
                    "current_base_id": "base_1",
                    "status": "idle",
                    "health_percent": 95,
                    "readiness_percent": 90,
                    "fuel_percent": 80,
                    "ammo_percent": 85,
                    "combat_radius_km": 1000,
                    "speed_kmh": 1500
                },
                {
                    "id": "ground_1",
                    "name": "Tank Brigade",
                    "country_code": "TST",
                    "unit_type": "Merkava",
                    "category": "ground",
                    "quantity": 50,
                    "location": {"lat": 31.5, "lng": 35.5},
                    "home_base_id": "base_2",
                    "current_base_id": "base_2",
                    "status": "idle",
                    "health_percent": 90,
                    "fuel_percent": 70,
                    "ammo_percent": 75,
                    "speed_kmh": 60
                },
                {
                    "id": "damaged_1",
                    "name": "Damaged Unit",
                    "country_code": "TST",
                    "unit_type": "APC",
                    "category": "ground",
                    "quantity": 10,
                    "location": {"lat": 31.2, "lng": 35.2},
                    "home_base_id": "base_2",
                    "status": "maintenance",
                    "health_percent": 30,
                    "fuel_percent": 50,
                    "ammo_percent": 40
                }
            ]
        }

    @pytest.fixture
    def sample_bases_data(self):
        """Sample bases data."""
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
                        "has_runway": True,
                        "repair_capability": True
                    }
                },
                {
                    "id": "base_2",
                    "name": "Army Base",
                    "country_code": "TST",
                    "location": {"lat": 31.5, "lng": 35.5},
                    "base_type": "army_base",
                    "status": "operational",
                    "capabilities": {
                        "max_ground_vehicles": 200,
                        "repair_capability": True
                    }
                }
            ]
        }

    @pytest.fixture
    def unit_engine(self, setup_map_service, sample_units_data, sample_bases_data):
        """Create unit engine with test data."""
        map_path = setup_map_service.map_path

        with open(map_path / "units_TST.json", "w") as f:
            json.dump(sample_units_data, f)

        with open(map_path / "bases_TST.json", "w") as f:
            json.dump(sample_bases_data, f)

        return UnitEngine("TST")

    # ==================== Basic Tests ====================

    def test_get_unit(self, unit_engine):
        """Test getting a unit."""
        unit = unit_engine.get_unit("aircraft_1")
        assert unit is not None
        assert unit.name == "Fighter Squadron"

    def test_get_unit_not_found(self, unit_engine):
        """Test getting non-existent unit."""
        unit = unit_engine.get_unit("nonexistent")
        assert unit is None

    def test_get_all_units(self, unit_engine):
        """Test getting all units."""
        units = unit_engine.get_all_units()
        assert len(units.units) == 3

    def test_get_available_units(self, unit_engine):
        """Test getting available units."""
        available = unit_engine.get_available_units()
        # Only aircraft_1 and ground_1 are available (damaged_1 is in maintenance)
        assert len(available) == 2

    # ==================== Movement Validation Tests ====================

    def test_can_unit_move_healthy(self, unit_engine):
        """Test healthy unit can move."""
        unit = unit_engine.get_unit("aircraft_1")
        can_move, reason = unit_engine.can_unit_move(unit)
        assert can_move is True

    def test_can_unit_move_maintenance(self, unit_engine):
        """Test unit in maintenance cannot move."""
        unit = unit_engine.get_unit("damaged_1")
        can_move, reason = unit_engine.can_unit_move(unit)
        assert can_move is False
        assert "maintenance" in reason.lower()

    # ==================== Deployment Tests ====================

    def test_deploy_unit_instant(self, unit_engine):
        """Test instant unit deployment."""
        destination = Coordinates(lat=32.0, lng=34.5)

        result, details = unit_engine.deploy_unit("aircraft_1", destination, instant=True)

        assert result == MovementResult.SUCCESS
        assert details["unit_id"] == "aircraft_1"
        assert details["status"] == "deployed"

        # Verify unit was moved
        unit = unit_engine.get_unit("aircraft_1")
        assert unit.location.lat == 32.0
        assert unit.location.lng == 34.5
        assert unit.status == UnitStatus.DEPLOYED

    def test_deploy_unit_transit(self, unit_engine):
        """Test unit deployment with transit."""
        destination = Coordinates(lat=32.0, lng=34.5)

        result, details = unit_engine.deploy_unit("aircraft_1", destination, instant=False)

        assert result == MovementResult.SUCCESS
        assert "travel_time_hours" in details

        # Verify unit is in transit
        unit = unit_engine.get_unit("aircraft_1")
        assert unit.status == UnitStatus.IN_TRANSIT
        assert unit.movement is not None

    def test_deploy_unit_not_found(self, unit_engine):
        """Test deploying non-existent unit."""
        destination = Coordinates(lat=32.0, lng=34.5)
        result, details = unit_engine.deploy_unit("nonexistent", destination)

        assert result == MovementResult.UNIT_NOT_FOUND

    def test_deploy_damaged_unit_fails(self, unit_engine):
        """Test deploying damaged unit fails."""
        destination = Coordinates(lat=32.0, lng=34.5)
        result, details = unit_engine.deploy_unit("damaged_1", destination)

        assert result == MovementResult.UNIT_CANNOT_MOVE

    # ==================== Return to Base Tests ====================

    def test_return_to_base_instant(self, unit_engine):
        """Test instant return to base."""
        # First deploy unit
        destination = Coordinates(lat=32.0, lng=34.5)
        unit_engine.deploy_unit("aircraft_1", destination, instant=True)

        # Return to base
        result, details = unit_engine.return_to_base("aircraft_1", instant=True)

        assert result == MovementResult.SUCCESS
        assert details["base_id"] == "base_1"

        # Verify unit is back at base
        unit = unit_engine.get_unit("aircraft_1")
        assert unit.status == UnitStatus.IDLE
        assert unit.current_base_id == "base_1"

    # ==================== Transfer Tests ====================

    def test_transfer_to_base(self, unit_engine):
        """Test transferring unit to different base."""
        result, details = unit_engine.transfer_to_base("aircraft_1", "base_2", instant=True)

        assert result == MovementResult.SUCCESS
        assert details["target_base_id"] == "base_2"

        unit = unit_engine.get_unit("aircraft_1")
        assert unit.current_base_id == "base_2"

    def test_transfer_to_nonexistent_base(self, unit_engine):
        """Test transferring to non-existent base fails."""
        result, details = unit_engine.transfer_to_base("aircraft_1", "nonexistent", instant=True)

        assert result == MovementResult.BASE_NOT_FOUND

    # ==================== Movement Processing Tests ====================

    def test_process_unit_movements(self, unit_engine):
        """Test processing unit movements."""
        # Deploy unit (non-instant)
        destination = Coordinates(lat=32.0, lng=34.5)
        unit_engine.deploy_unit("aircraft_1", destination, instant=False)

        # Get ETA
        unit = unit_engine.get_unit("aircraft_1")
        eta = unit.movement.eta

        # Process before ETA - no completion
        completed = unit_engine.process_unit_movements(eta - timedelta(minutes=1))
        assert len(completed) == 0

        # Process after ETA - should complete
        completed = unit_engine.process_unit_movements(eta + timedelta(minutes=1))
        assert len(completed) == 1
        assert completed[0]["unit_id"] == "aircraft_1"

        # Verify unit arrived
        unit = unit_engine.get_unit("aircraft_1")
        assert unit.status == UnitStatus.DEPLOYED
        assert unit.movement is None

    # ==================== Status Update Tests ====================

    def test_update_unit_status(self, unit_engine):
        """Test updating unit stats."""
        success, details = unit_engine.update_unit_status(
            "aircraft_1",
            health_delta=-10,
            fuel_delta=-20,
            morale_delta=5
        )

        assert success is True

        unit = unit_engine.get_unit("aircraft_1")
        assert unit.health_percent == 85  # 95 - 10
        assert unit.fuel_percent == 60  # 80 - 20

    def test_update_unit_destroyed(self, unit_engine):
        """Test unit becomes destroyed when health reaches 0."""
        success, details = unit_engine.update_unit_status(
            "aircraft_1",
            health_delta=-100
        )

        assert success is True

        unit = unit_engine.get_unit("aircraft_1")
        assert unit.health_percent == 0
        assert unit.status == UnitStatus.DESTROYED

    # ==================== Resupply Tests ====================

    def test_resupply_unit_at_base(self, unit_engine):
        """Test resupplying unit at base."""
        # First deplete some resources
        unit_engine.update_unit_status("aircraft_1", fuel_delta=-50, ammo_delta=-50)

        success, details = unit_engine.resupply_unit("aircraft_1")

        assert success is True
        assert details["fuel"] == 100
        assert details["ammo"] == 100

        unit = unit_engine.get_unit("aircraft_1")
        assert unit.fuel_percent == 100
        assert unit.ammo_percent == 100

    def test_resupply_deployed_unit_fails(self, unit_engine):
        """Test resupplying deployed unit fails."""
        # Deploy unit
        destination = Coordinates(lat=32.0, lng=34.5)
        unit_engine.deploy_unit("aircraft_1", destination, instant=True)

        success, details = unit_engine.resupply_unit("aircraft_1")
        assert success is False
        assert "base" in details["error"].lower()

    # ==================== Repair Tests ====================

    def test_repair_unit(self, unit_engine):
        """Test repairing unit."""
        # First damage the unit
        unit_engine.update_unit_status("aircraft_1", health_delta=-30)

        success, details = unit_engine.repair_unit("aircraft_1", repair_amount=15)

        assert success is True
        assert details["new_health"] == 80  # 65 + 15

    def test_repair_not_at_base_fails(self, unit_engine):
        """Test repair fails when not at base."""
        # Deploy unit
        destination = Coordinates(lat=32.0, lng=34.5)
        unit_engine.deploy_unit("aircraft_1", destination, instant=True)

        success, details = unit_engine.repair_unit("aircraft_1")
        assert success is False

    # ==================== Summary Tests ====================

    def test_get_unit_summary(self, unit_engine):
        """Test getting unit summary."""
        summary = unit_engine.get_unit_summary()

        assert summary["total_units"] == 3
        assert "aircraft" in summary["by_category"]
        assert "ground" in summary["by_category"]
        assert "idle" in summary["by_status"]
        assert summary["available_for_deployment"] == 2


class TestUnitEngineCalculations:
    """Tests for unit engine calculations."""

    def test_travel_time_calculation(self):
        """Test travel time calculation."""
        engine = UnitEngine("TST")

        unit = MilitaryUnit(
            id="test",
            name="Test",
            country_code="TST",
            unit_type="Tank",
            category=UnitCategory.GROUND,
            quantity=10,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="base",
            speed_kmh=60
        )

        # 60 km at 60 km/h = 1 hour
        travel_time = engine._calculate_travel_time(unit, 60)
        assert travel_time.total_seconds() == 3600  # 1 hour

    def test_fuel_consumption_calculation(self):
        """Test fuel consumption calculation."""
        engine = UnitEngine("TST")

        unit = MilitaryUnit(
            id="test",
            name="Test",
            country_code="TST",
            unit_type="Tank",
            category=UnitCategory.GROUND,
            quantity=10,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="base"
        )

        # Ground units consume 2% per hour
        fuel = engine._calculate_fuel_consumption(unit, 5)  # 5 hours
        assert fuel == 10.0  # 2% * 5 = 10%
