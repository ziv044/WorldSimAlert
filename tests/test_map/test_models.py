"""
Tests for map-related data models.
"""
import pytest
from backend.models.map import Coordinates, BoundingBox, MapRegion, TerrainType
from backend.models.cities import City, CityList, CityType, CityInfrastructure
from backend.models.bases import MilitaryBase, BaseList, BaseType, BaseStatus, BaseCapabilities
from backend.models.units import MilitaryUnit, UnitList, UnitCategory, UnitStatus


class TestCoordinates:
    """Tests for Coordinates model."""

    def test_create_valid_coordinates(self):
        """Test creating valid coordinates."""
        coord = Coordinates(lat=31.7683, lng=35.2137)
        assert coord.lat == 31.7683
        assert coord.lng == 35.2137

    def test_coordinates_bounds_validation(self):
        """Test that coordinates validate lat/lng bounds."""
        with pytest.raises(ValueError):
            Coordinates(lat=91, lng=0)  # lat > 90

        with pytest.raises(ValueError):
            Coordinates(lat=0, lng=181)  # lng > 180

    def test_distance_to_same_point(self):
        """Test distance to same point is zero."""
        coord = Coordinates(lat=31.7683, lng=35.2137)
        assert coord.distance_to(coord) == pytest.approx(0, abs=0.01)

    def test_distance_to_different_point(self):
        """Test distance calculation between two points."""
        jerusalem = Coordinates(lat=31.7683, lng=35.2137)
        tel_aviv = Coordinates(lat=32.0853, lng=34.7818)

        distance = jerusalem.distance_to(tel_aviv)
        # Jerusalem to Tel Aviv is approximately 54-60 km
        assert 50 < distance < 70

    def test_distance_is_symmetric(self):
        """Test that distance is symmetric (A to B == B to A)."""
        coord1 = Coordinates(lat=31.7683, lng=35.2137)
        coord2 = Coordinates(lat=32.0853, lng=34.7818)

        assert coord1.distance_to(coord2) == pytest.approx(coord2.distance_to(coord1), rel=0.01)


class TestBoundingBox:
    """Tests for BoundingBox model."""

    def test_create_bounding_box(self):
        """Test creating a bounding box."""
        bbox = BoundingBox(north=33.3, south=29.5, east=35.9, west=34.3)
        assert bbox.north == 33.3
        assert bbox.south == 29.5

    def test_contains_point_inside(self):
        """Test that contains returns True for point inside."""
        bbox = BoundingBox(north=33.0, south=30.0, east=36.0, west=34.0)
        coord = Coordinates(lat=31.5, lng=35.0)
        assert bbox.contains(coord) is True

    def test_contains_point_outside(self):
        """Test that contains returns False for point outside."""
        bbox = BoundingBox(north=33.0, south=30.0, east=36.0, west=34.0)
        coord = Coordinates(lat=29.0, lng=35.0)  # South of bbox
        assert bbox.contains(coord) is False


class TestCity:
    """Tests for City model."""

    def test_create_city(self):
        """Test creating a city."""
        city = City(
            id="tel_aviv",
            name="Tel Aviv",
            country_code="ISR",
            location=Coordinates(lat=32.0853, lng=34.7818),
            population=460000,
            city_type=CityType.MAJOR
        )
        assert city.id == "tel_aviv"
        assert city.name == "Tel Aviv"
        assert city.population == 460000
        assert city.is_capital is False

    def test_city_with_infrastructure(self):
        """Test city with custom infrastructure."""
        infra = CityInfrastructure(
            power_reliability=95,
            water_supply=90,
            healthcare_access=88
        )
        city = City(
            id="test",
            name="Test City",
            country_code="TST",
            location=Coordinates(lat=31.0, lng=35.0),
            population=100000,
            city_type=CityType.MEDIUM,
            infrastructure=infra
        )
        assert city.infrastructure.power_reliability == 95


class TestCityList:
    """Tests for CityList model."""

    @pytest.fixture
    def sample_cities(self):
        """Create sample city list."""
        return CityList(
            country_code="TST",
            cities=[
                City(
                    id="capital",
                    name="Capital City",
                    country_code="TST",
                    location=Coordinates(lat=31.0, lng=35.0),
                    population=500000,
                    city_type=CityType.CAPITAL,
                    is_capital=True
                ),
                City(
                    id="port",
                    name="Port City",
                    country_code="TST",
                    location=Coordinates(lat=32.0, lng=34.5),
                    population=200000,
                    city_type=CityType.MAJOR,
                    is_port=True
                )
            ],
            total_urban_population=700000
        )

    def test_get_capital(self, sample_cities):
        """Test getting capital city."""
        capital = sample_cities.get_capital()
        assert capital is not None
        assert capital.id == "capital"
        assert capital.is_capital is True

    def test_get_by_id(self, sample_cities):
        """Test getting city by ID."""
        city = sample_cities.get_by_id("port")
        assert city is not None
        assert city.name == "Port City"

    def test_get_by_id_not_found(self, sample_cities):
        """Test getting non-existent city returns None."""
        city = sample_cities.get_by_id("nonexistent")
        assert city is None

    def test_get_cities_in_radius(self, sample_cities):
        """Test getting cities in radius."""
        center = Coordinates(lat=31.5, lng=34.75)
        nearby = sample_cities.get_cities_in_radius(center, 100)
        assert len(nearby) == 2  # Both cities within 100km


class TestMilitaryBase:
    """Tests for MilitaryBase model."""

    def test_create_base(self):
        """Test creating a military base."""
        base = MilitaryBase(
            id="air_base_1",
            name="Test Air Base",
            country_code="TST",
            location=Coordinates(lat=31.0, lng=35.0),
            base_type=BaseType.AIR_BASE,
            capabilities=BaseCapabilities(
                max_aircraft=50,
                has_runway=True,
                runway_length_m=3000
            )
        )
        assert base.id == "air_base_1"
        assert base.base_type == BaseType.AIR_BASE
        assert base.capabilities.max_aircraft == 50
        assert base.status == BaseStatus.OPERATIONAL


class TestBaseList:
    """Tests for BaseList model."""

    @pytest.fixture
    def sample_bases(self):
        """Create sample base list."""
        return BaseList(
            country_code="TST",
            bases=[
                MilitaryBase(
                    id="air_1",
                    name="Air Base 1",
                    country_code="TST",
                    location=Coordinates(lat=31.0, lng=35.0),
                    base_type=BaseType.AIR_BASE
                ),
                MilitaryBase(
                    id="naval_1",
                    name="Naval Base 1",
                    country_code="TST",
                    location=Coordinates(lat=32.0, lng=34.5),
                    base_type=BaseType.NAVAL_BASE
                ),
                MilitaryBase(
                    id="air_2",
                    name="Air Base 2",
                    country_code="TST",
                    location=Coordinates(lat=31.5, lng=35.5),
                    base_type=BaseType.AIR_BASE,
                    status=BaseStatus.MAINTENANCE
                )
            ]
        )

    def test_get_by_type(self, sample_bases):
        """Test getting bases by type."""
        air_bases = sample_bases.get_by_type(BaseType.AIR_BASE)
        assert len(air_bases) == 2

        naval_bases = sample_bases.get_by_type(BaseType.NAVAL_BASE)
        assert len(naval_bases) == 1

    def test_get_operational(self, sample_bases):
        """Test getting operational bases."""
        operational = sample_bases.get_operational()
        assert len(operational) == 2  # One is in maintenance


class TestMilitaryUnit:
    """Tests for MilitaryUnit model."""

    def test_create_unit(self):
        """Test creating a military unit."""
        unit = MilitaryUnit(
            id="squadron_1",
            name="Test Squadron",
            country_code="TST",
            unit_type="F-35I",
            category=UnitCategory.AIRCRAFT,
            quantity=25,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="air_base_1"
        )
        assert unit.id == "squadron_1"
        assert unit.quantity == 25
        assert unit.status == UnitStatus.IDLE
        assert unit.health_percent == 100.0

    def test_can_deploy_healthy_unit(self):
        """Test that healthy unit can deploy."""
        unit = MilitaryUnit(
            id="unit_1",
            name="Test Unit",
            country_code="TST",
            unit_type="Tank",
            category=UnitCategory.GROUND,
            quantity=10,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="base_1",
            health_percent=80,
            readiness_percent=75,
            fuel_percent=60,
            ammo_percent=70
        )
        assert unit.can_deploy() is True

    def test_cannot_deploy_damaged_unit(self):
        """Test that heavily damaged unit cannot deploy."""
        unit = MilitaryUnit(
            id="unit_1",
            name="Damaged Unit",
            country_code="TST",
            unit_type="Tank",
            category=UnitCategory.GROUND,
            quantity=10,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="base_1",
            health_percent=40  # Below 50%
        )
        assert unit.can_deploy() is False

    def test_cannot_deploy_in_combat(self):
        """Test that unit in combat cannot deploy elsewhere."""
        unit = MilitaryUnit(
            id="unit_1",
            name="Combat Unit",
            country_code="TST",
            unit_type="Tank",
            category=UnitCategory.GROUND,
            quantity=10,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="base_1",
            status=UnitStatus.IN_COMBAT
        )
        assert unit.can_deploy() is False

    def test_effective_strength_calculation(self):
        """Test effective strength calculation."""
        unit = MilitaryUnit(
            id="unit_1",
            name="Test Unit",
            country_code="TST",
            unit_type="Tank",
            category=UnitCategory.GROUND,
            quantity=10,
            location=Coordinates(lat=31.0, lng=35.0),
            home_base_id="base_1",
            health_percent=100,
            readiness_percent=100,
            fuel_percent=100,
            ammo_percent=100,
            morale=100,
            experience_level=100
        )
        # Max experience factor is 1.0 (0.5 + 100/200)
        # All other factors are 1.0
        assert unit.get_effective_strength() == pytest.approx(1.0, rel=0.01)


class TestUnitList:
    """Tests for UnitList model."""

    @pytest.fixture
    def sample_units(self):
        """Create sample unit list."""
        return UnitList(
            country_code="TST",
            units=[
                MilitaryUnit(
                    id="air_1",
                    name="Air Squadron 1",
                    country_code="TST",
                    unit_type="F-35",
                    category=UnitCategory.AIRCRAFT,
                    quantity=20,
                    location=Coordinates(lat=31.0, lng=35.0),
                    home_base_id="base_1",
                    current_base_id="base_1",
                    status=UnitStatus.IDLE
                ),
                MilitaryUnit(
                    id="ground_1",
                    name="Tank Brigade",
                    country_code="TST",
                    unit_type="Merkava",
                    category=UnitCategory.GROUND,
                    quantity=50,
                    location=Coordinates(lat=31.5, lng=35.5),
                    home_base_id="base_2",
                    status=UnitStatus.DEPLOYED,
                    assigned_operation_id="op_1"
                ),
                MilitaryUnit(
                    id="air_2",
                    name="Air Squadron 2",
                    country_code="TST",
                    unit_type="F-16",
                    category=UnitCategory.AIRCRAFT,
                    quantity=30,
                    location=Coordinates(lat=32.0, lng=34.5),
                    home_base_id="base_1",
                    current_base_id="base_1",
                    status=UnitStatus.MAINTENANCE,
                    health_percent=40
                )
            ]
        )

    def test_get_by_category(self, sample_units):
        """Test getting units by category."""
        aircraft = sample_units.get_by_category(UnitCategory.AIRCRAFT)
        assert len(aircraft) == 2

        ground = sample_units.get_by_category(UnitCategory.GROUND)
        assert len(ground) == 1

    def test_get_available(self, sample_units):
        """Test getting available units."""
        available = sample_units.get_available()
        # air_1 is idle and healthy, ground_1 is deployed but healthy
        # air_2 is in maintenance with low health
        assert len(available) == 2

    def test_get_at_base(self, sample_units):
        """Test getting units at base."""
        at_base_1 = sample_units.get_at_base("base_1")
        assert len(at_base_1) == 2  # Both aircraft are at base_1

    def test_get_in_operation(self, sample_units):
        """Test getting units in operation."""
        in_op = sample_units.get_in_operation("op_1")
        assert len(in_op) == 1
        assert in_op[0].id == "ground_1"
