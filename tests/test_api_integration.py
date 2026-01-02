"""
Integration tests for API endpoints that were reported as broken.
Tests: Procurement, Operations, Sectors APIs
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


# =============================================================================
# Procurement API Tests
# =============================================================================

class TestProcurementAPI:
    """Test Procurement API endpoints."""

    def test_get_catalog(self, client):
        """Test getting weapons catalog."""
        response = client.get("/api/procurement/catalog")
        assert response.status_code == 200
        data = response.json()
        assert "catalog" in data

    def test_get_catalog_with_category(self, client):
        """Test getting weapons catalog filtered by category."""
        response = client.get("/api/procurement/catalog?category=aircraft")
        assert response.status_code == 200
        data = response.json()
        assert "catalog" in data

    def test_get_orders(self, client):
        """Test getting procurement orders."""
        response = client.get("/api/procurement/ISR/orders")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data

    def test_check_purchase(self, client):
        """Test checking purchase eligibility."""
        response = client.post("/api/procurement/ISR/check", json={
            "weapon_id": "f35",
            "quantity": 1
        })
        assert response.status_code == 200
        data = response.json()
        # Should have either 'eligible' or 'success' key
        assert "eligible" in data or "success" in data or "error" in data


# =============================================================================
# Operations API Tests
# =============================================================================

class TestOperationsAPI:
    """Test Operations API endpoints."""

    def test_get_operation_types(self, client):
        """Test getting operation types."""
        response = client.get("/api/operations/types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert "details" in data

    def test_plan_operation(self, client):
        """Test planning an operation."""
        response = client.post("/api/operations/ISR/plan", json={
            "operation_type": "air_strike",
            "target_country": "SYR",
            "target_description": "Test target"
        })
        assert response.status_code == 200
        data = response.json()
        # Should return feasibility info
        assert isinstance(data, dict)

    def test_set_readiness(self, client):
        """Test setting readiness level."""
        response = client.post("/api/operations/ISR/readiness?level=normal")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "level" in data or "error" in data


# =============================================================================
# Map Operations API Tests
# =============================================================================

class TestMapOperationsAPI:
    """Test Map Operations API endpoints."""

    def test_get_operations(self, client):
        """Test getting map operations."""
        response = client.get("/api/map/operations/ISR")
        assert response.status_code == 200
        data = response.json()
        assert "operations" in data

    def test_get_units(self, client):
        """Test getting units."""
        response = client.get("/api/map/units/ISR")
        assert response.status_code == 200
        data = response.json()
        assert "units" in data


# =============================================================================
# Sectors API Tests
# =============================================================================

class TestSectorsAPI:
    """Test Sectors API endpoints."""

    def test_get_sectors(self, client):
        """Test getting sectors."""
        response = client.get("/api/country/ISR/sectors")
        assert response.status_code == 200
        data = response.json()
        assert "sectors" in data

    def test_get_projects(self, client):
        """Test getting active projects."""
        response = client.get("/api/sectors/ISR/projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data

    def test_invest_in_sector(self, client):
        """Test investing in a sector."""
        response = client.post("/api/sectors/ISR/invest", json={
            "sector_name": "technology",
            "investment_billions": 0.5,
            "target_improvement": 5
        })
        assert response.status_code == 200
        data = response.json()
        # Check response structure
        assert "success" in data or "error" in data or "message" in data

    def test_start_infrastructure(self, client):
        """Test starting infrastructure project."""
        response = client.post("/api/sectors/ISR/infrastructure", json={
            "project_type": "highway",
            "custom_name": "Test Highway"
        })
        assert response.status_code == 200
        data = response.json()
        # Check response structure
        assert "success" in data or "error" in data or "message" in data


# =============================================================================
# Budget API Tests
# =============================================================================

class TestBudgetAPI:
    """Test Budget API endpoints."""

    def test_get_budget(self, client):
        """Test getting budget."""
        response = client.get("/api/budget/ISR")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


# =============================================================================
# Regression Tests for Bug Fixes (2026-01-02)
# =============================================================================

class TestProcurementOrdersProgressField:
    """Test that procurement orders include progress field (Bug Fix #1)."""

    def test_orders_include_progress_field(self, client):
        """Verify orders response includes progress field."""
        response = client.get("/api/procurement/ISR/orders")
        assert response.status_code == 200
        data = response.json()
        # Even if no orders, check structure
        if data.get("orders"):
            for order in data["orders"]:
                assert "progress" in order, "Order missing 'progress' field"
                assert "order_id" in order, "Order missing 'order_id' field"
                assert "delivery_date" in order, "Order missing 'delivery_date' field"

    def test_orders_progress_is_number(self, client):
        """Verify progress field is a number."""
        response = client.get("/api/procurement/ISR/orders")
        data = response.json()
        if data.get("orders"):
            for order in data["orders"]:
                assert isinstance(order.get("progress"), (int, float))


class TestProjectsProgressField:
    """Test that projects include both progress and progress_percent (Bug Fix #2)."""

    def test_projects_include_both_progress_fields(self, client):
        """Verify projects response includes both progress fields."""
        response = client.get("/api/sectors/ISR/projects")
        assert response.status_code == 200
        data = response.json()
        if data.get("projects"):
            for project in data["projects"]:
                assert "progress" in project, "Project missing 'progress' field"
                assert "progress_percent" in project, "Project missing 'progress_percent' field"
                assert "eta" in project, "Project missing 'eta' field"
                assert "project_type" in project, "Project missing 'project_type' field"


class TestSectorInvestmentWithValidSectors:
    """Test that sector investment works with correct sector names (Bug Fix #3)."""

    def test_invest_in_valid_sectors(self, client):
        """Test investment in sectors that exist in backend."""
        valid_sectors = [
            "technology", "finance", "manufacturing", "agriculture",
            "tourism", "healthcare_sector", "construction", "defense_industry",
            "energy", "retail"
        ]

        for sector in valid_sectors:
            response = client.post("/api/sectors/ISR/invest", json={
                "sector_name": sector,
                "investment_billions": 0.1,
                "target_improvement": 1
            })
            assert response.status_code == 200
            # Response should have success field or error (not 500)
            data = response.json()
            assert "success" in data or "error" in data

    def test_invalid_sector_returns_error(self, client):
        """Test that invalid sector names return proper error."""
        response = client.post("/api/sectors/ISR/invest", json={
            "sector_name": "services",  # Old invalid name
            "investment_billions": 0.1,
            "target_improvement": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "error" in data


class TestInfrastructureWithValidTypes:
    """Test that infrastructure works with correct project types (Bug Fix #4)."""

    def test_start_valid_infrastructure_types(self, client):
        """Test starting infrastructure with valid types."""
        valid_types = [
            "power_plant", "highway", "port", "airport",
            "university", "hospital", "military_factory",
            "research_center", "data_center", "desalination_plant"
        ]

        for project_type in valid_types:
            response = client.post("/api/sectors/ISR/infrastructure", json={
                "project_type": project_type,
                "custom_name": f"Test {project_type}"
            })
            assert response.status_code == 200
            data = response.json()
            # Should have success or error (budget might be insufficient)
            assert "success" in data or "error" in data

    def test_invalid_infrastructure_type_returns_error(self, client):
        """Test that invalid infrastructure types return proper error."""
        response = client.post("/api/sectors/ISR/infrastructure", json={
            "project_type": "school",  # Old invalid name
            "custom_name": "Test School"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False


class TestProcurementCheckResponseFormat:
    """Test procurement check returns correct response format for frontend (Bug Fix #5)."""

    def test_check_returns_constraints_array(self, client):
        """Verify check response includes constraints array with message field."""
        response = client.post("/api/procurement/ISR/check", json={
            "weapon_id": "armor.mbt",
            "quantity": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "eligible" in data
        assert "constraints" in data
        assert isinstance(data["constraints"], list)
        # Each constraint should have message field
        for constraint in data["constraints"]:
            assert "message" in constraint
            assert "satisfied" in constraint


class TestOperationsPlanResponseFormat:
    """Test operations plan returns correct response format for frontend (Bug Fix #6)."""

    def test_plan_returns_valid_field(self, client):
        """Verify plan response uses 'valid' not 'feasible'."""
        response = client.post("/api/operations/ISR/plan", json={
            "operation_type": "reconnaissance",
            "target_country": "SYR",
            "target_description": "Test target"
        })
        assert response.status_code == 200
        data = response.json()
        # Should have 'valid' field, not 'feasible'
        assert "valid" in data
        # When invalid, should have error info
        if not data.get("valid"):
            assert "error" in data or "missing" in data

    def test_execute_returns_message_field(self, client):
        """Verify execute response includes message field for errors."""
        response = client.post("/api/operations/ISR/execute", json={
            "operation_type": "reconnaissance",
            "target_country": "SYR",
            "target_description": "Test target",
            "location": {"lat": 33.5, "lng": 36.3}
        })
        assert response.status_code == 200
        data = response.json()
        # Should have success and message fields
        assert "success" in data
        if not data.get("success"):
            assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
