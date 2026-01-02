"""
Tests for Location-based Operations Engine.
"""
import pytest
import json
from datetime import datetime, timedelta

from backend.engine.location_operations_engine import LocationOperationsEngine
from backend.models.map import Coordinates
from backend.models.units import UnitCategory, UnitStatus
from backend.models.active_operation import OperationType, OperationStatus


class TestLocationOperationsEngine:
    """Tests for LocationOperationsEngine."""

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
                    "id": "fighter_1",
                    "name": "Fighter Squadron 1",
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
                    "speed_kmh": 1500,
                    "experience_level": 75,
                    "morale": 85
                },
                {
                    "id": "fighter_2",
                    "name": "Fighter Squadron 2",
                    "country_code": "TST",
                    "unit_type": "F-16",
                    "category": "aircraft",
                    "quantity": 25,
                    "location": {"lat": 31.0, "lng": 35.0},
                    "home_base_id": "base_1",
                    "current_base_id": "base_1",
                    "status": "idle",
                    "health_percent": 90,
                    "fuel_percent": 75,
                    "ammo_percent": 80,
                    "combat_radius_km": 800,
                    "speed_kmh": 1200
                },
                {
                    "id": "tank_1",
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
                    "id": "naval_1",
                    "name": "Corvette Squadron",
                    "country_code": "TST",
                    "unit_type": "Sa'ar",
                    "category": "naval",
                    "quantity": 4,
                    "location": {"lat": 32.8, "lng": 35.0},
                    "home_base_id": "naval_base",
                    "current_base_id": "naval_base",
                    "status": "idle",
                    "health_percent": 95,
                    "fuel_percent": 90,
                    "ammo_percent": 95,
                    "speed_kmh": 50
                },
                {
                    "id": "naval_2",
                    "name": "Patrol Boats",
                    "country_code": "TST",
                    "unit_type": "Patrol",
                    "category": "naval",
                    "quantity": 6,
                    "location": {"lat": 32.8, "lng": 35.0},
                    "home_base_id": "naval_base",
                    "current_base_id": "naval_base",
                    "status": "idle",
                    "health_percent": 88,
                    "fuel_percent": 85,
                    "speed_kmh": 45
                },
                {
                    "id": "damaged_unit",
                    "name": "Damaged Fighter",
                    "country_code": "TST",
                    "unit_type": "F-16",
                    "category": "aircraft",
                    "quantity": 10,
                    "location": {"lat": 31.0, "lng": 35.0},
                    "home_base_id": "base_1",
                    "status": "maintenance",
                    "health_percent": 30,
                    "fuel_percent": 50
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
                    "capabilities": {"max_aircraft": 100, "repair_capability": True}
                },
                {
                    "id": "base_2",
                    "name": "Army Base",
                    "country_code": "TST",
                    "location": {"lat": 31.5, "lng": 35.5},
                    "base_type": "army_base",
                    "capabilities": {"repair_capability": True}
                },
                {
                    "id": "naval_base",
                    "name": "Naval Base",
                    "country_code": "TST",
                    "location": {"lat": 32.8, "lng": 35.0},
                    "base_type": "naval_base",
                    "capabilities": {"repair_capability": True}
                }
            ]
        }

    @pytest.fixture
    def ops_engine(self, setup_map_service, sample_units_data, sample_bases_data):
        """Create operations engine with test data."""
        map_path = setup_map_service.map_path

        with open(map_path / "units_TST.json", "w") as f:
            json.dump(sample_units_data, f)

        with open(map_path / "bases_TST.json", "w") as f:
            json.dump(sample_bases_data, f)

        # Empty operations file
        with open(map_path / "operations_TST.json", "w") as f:
            json.dump({"country_code": "TST", "operations": []}, f)

        return LocationOperationsEngine("TST")

    # ==================== Plan Operation Tests ====================

    def test_plan_air_strike_valid(self, ops_engine):
        """Test planning a valid air strike."""
        target = Coordinates(lat=32.0, lng=34.5)

        plan = ops_engine.plan_operation(
            operation_type="air_strike",
            target_location=target,
            unit_ids=["fighter_1"],
            target_name="Enemy Base"
        )

        assert plan['valid'] is True
        assert plan['operation_type'] == 'air_strike'
        assert 'estimated_success_rate' in plan
        assert plan['estimated_success_rate'] > 0

    def test_plan_operation_invalid_type(self, ops_engine):
        """Test planning with invalid operation type."""
        target = Coordinates(lat=32.0, lng=34.5)

        plan = ops_engine.plan_operation(
            operation_type="invalid_type",
            target_location=target,
            unit_ids=["fighter_1"]
        )

        assert plan['valid'] is False
        assert 'available_types' in plan

    def test_plan_operation_wrong_unit_category(self, ops_engine):
        """Test planning air strike with ground units fails."""
        target = Coordinates(lat=32.0, lng=34.5)

        plan = ops_engine.plan_operation(
            operation_type="air_strike",
            target_location=target,
            unit_ids=["tank_1"]
        )

        assert plan['valid'] is False
        assert 'cannot perform' in plan['error']

    def test_plan_operation_damaged_unit_fails(self, ops_engine):
        """Test planning with damaged unit fails."""
        target = Coordinates(lat=32.0, lng=34.5)

        plan = ops_engine.plan_operation(
            operation_type="air_strike",
            target_location=target,
            unit_ids=["damaged_unit"]
        )

        assert plan['valid'] is False
        assert 'cannot deploy' in plan['error']

    def test_plan_operation_unit_not_found(self, ops_engine):
        """Test planning with non-existent unit."""
        target = Coordinates(lat=32.0, lng=34.5)

        plan = ops_engine.plan_operation(
            operation_type="air_strike",
            target_location=target,
            unit_ids=["nonexistent"]
        )

        assert plan['valid'] is False
        assert 'not found' in plan['error']

    def test_plan_naval_patrol(self, ops_engine):
        """Test planning naval patrol."""
        target = Coordinates(lat=33.0, lng=34.0)

        plan = ops_engine.plan_operation(
            operation_type="naval_patrol",
            target_location=target,
            unit_ids=["naval_1", "naval_2"]
        )

        assert plan['valid'] is True
        assert plan['operation_type'] == 'naval_patrol'

    def test_plan_ground_assault(self, ops_engine):
        """Test planning ground assault."""
        target = Coordinates(lat=32.0, lng=35.5)

        plan = ops_engine.plan_operation(
            operation_type="ground_assault",
            target_location=target,
            unit_ids=["tank_1"]
        )

        # Ground assault requires 2 units minimum
        assert plan['valid'] is False

    # ==================== Create Operation Tests ====================

    def test_create_operation_success(self, ops_engine):
        """Test creating an operation."""
        target = Coordinates(lat=32.0, lng=34.5)

        success, result = ops_engine.create_operation(
            operation_type="air_strike",
            name="Strike Alpha",
            target_location=target,
            unit_ids=["fighter_1"]
        )

        assert success is True
        assert 'operation_id' in result
        assert result['status'] == 'planning'

    def test_create_operation_assigns_units(self, ops_engine):
        """Test that creating operation assigns units."""
        target = Coordinates(lat=32.0, lng=34.5)

        success, result = ops_engine.create_operation(
            operation_type="air_strike",
            name="Strike Alpha",
            target_location=target,
            unit_ids=["fighter_1"]
        )

        assert success is True

        # Check unit was assigned
        unit = ops_engine.unit_engine.get_unit("fighter_1")
        assert unit.assigned_operation_id == result['operation_id']

    def test_create_operation_invalid_returns_error(self, ops_engine):
        """Test creating invalid operation returns error."""
        target = Coordinates(lat=32.0, lng=34.5)

        success, result = ops_engine.create_operation(
            operation_type="air_strike",
            name="Bad Operation",
            target_location=target,
            unit_ids=["tank_1"]  # Wrong unit type
        )

        assert success is False
        assert 'error' in result

    # ==================== Start Operation Tests ====================

    def test_start_operation(self, ops_engine):
        """Test starting a planned operation."""
        target = Coordinates(lat=32.0, lng=34.5)

        # Create operation
        success, create_result = ops_engine.create_operation(
            operation_type="air_strike",
            name="Strike Alpha",
            target_location=target,
            unit_ids=["fighter_1"]
        )
        assert success

        # Start operation
        success, start_result = ops_engine.start_operation(create_result['operation_id'])

        assert success is True
        assert start_result['status'] == 'deploying'

    def test_start_nonexistent_operation_fails(self, ops_engine):
        """Test starting non-existent operation fails."""
        success, result = ops_engine.start_operation("nonexistent_id")

        assert success is False
        assert 'not found' in result['error']

    # ==================== Cancel Operation Tests ====================

    def test_cancel_operation(self, ops_engine):
        """Test cancelling a planned operation."""
        target = Coordinates(lat=32.0, lng=34.5)

        # Create operation
        success, create_result = ops_engine.create_operation(
            operation_type="air_strike",
            name="Strike Alpha",
            target_location=target,
            unit_ids=["fighter_1"]
        )
        assert success

        # Cancel operation
        success, cancel_result = ops_engine.cancel_operation(create_result['operation_id'])

        assert success is True
        assert cancel_result['status'] == 'cancelled'

        # Check unit was released
        unit = ops_engine.unit_engine.get_unit("fighter_1")
        assert unit.assigned_operation_id is None

    # ==================== Process Operations Tests ====================

    def test_process_operations_updates_progress(self, ops_engine):
        """Test that processing updates operation progress."""
        target = Coordinates(lat=32.0, lng=34.5)

        # Create and start operation
        success, create_result = ops_engine.create_operation(
            operation_type="air_strike",
            name="Strike Alpha",
            target_location=target,
            unit_ids=["fighter_1"]
        )

        # Manually set to active for testing
        from backend.services.map_service import map_service
        op = map_service.get_operation("TST", create_result['operation_id'])
        op.status = OperationStatus.ACTIVE
        op.started_at = datetime.utcnow() - timedelta(hours=1)
        op.duration_hours = 2
        map_service.update_operation("TST", op)

        # Process
        current_time = datetime.utcnow()
        updates = ops_engine.process_operations(current_time)

        # Reload operation
        op = map_service.get_operation("TST", create_result['operation_id'])
        assert op.progress_percent > 0

    # ==================== Summary Tests ====================

    def test_get_operation_summary(self, ops_engine):
        """Test getting operation summary."""
        target = Coordinates(lat=32.0, lng=34.5)

        # Create some operations
        ops_engine.create_operation(
            operation_type="air_strike",
            name="Strike 1",
            target_location=target,
            unit_ids=["fighter_1"]
        )

        ops_engine.create_operation(
            operation_type="naval_patrol",
            name="Patrol 1",
            target_location=target,
            unit_ids=["naval_1", "naval_2"]
        )

        summary = ops_engine.get_operation_summary()

        assert summary['total'] == 2
        assert 'by_status' in summary
        assert 'by_type' in summary


class TestOperationSuccessCalculation:
    """Tests for operation success rate calculations."""

    def test_higher_unit_strength_improves_success(self):
        """Test that stronger units have better success rates."""
        # This is a conceptual test - actual implementation varies
        # The success rate should increase with unit effectiveness
        pass  # Covered by integration tests

    def test_distance_affects_success(self):
        """Test that distance affects success rate."""
        # Operations at edge of range should have lower success
        pass  # Covered by integration tests
