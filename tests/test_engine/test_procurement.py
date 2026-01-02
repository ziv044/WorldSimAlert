# tests/test_engine/test_procurement.py
import pytest
from copy import deepcopy
from backend.engine.procurement_engine import ProcurementEngine


class TestCatalogAccess:
    """Test weapons catalog access"""

    def test_get_full_catalog(self, sample_country_data, sample_weapons_catalog):
        """Should return full catalog"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        catalog = engine.get_catalog()

        assert len(catalog) == 3
        assert "F-35" in catalog
        assert "S-400" in catalog
        assert "Leopard-2" in catalog

    def test_get_catalog_by_category(self, sample_country_data, sample_weapons_catalog):
        """Should filter catalog by category"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        aircraft = engine.get_catalog("aircraft")

        assert len(aircraft) == 1
        assert "F-35" in aircraft


class TestPurchaseEligibility:
    """Test purchase eligibility checking"""

    def test_check_eligible_purchase(self, sample_country_data, sample_weapons_catalog):
        """Should return eligibility info for valid purchase"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.check_purchase_eligibility("F-35", 10)

        assert result['weapon']['id'] == "F-35"
        assert result['quantity'] == 10
        assert 'eligible' in result
        assert 'constraints' in result

    def test_unknown_weapon_eligibility(self, sample_country_data, sample_weapons_catalog):
        """Should handle unknown weapon"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.check_purchase_eligibility("UnknownWeapon", 1)

        assert result['eligible'] is False
        assert 'Unknown weapon' in result['error']


class TestPurchaseValidation:
    """Test weapon purchase validation"""

    def test_valid_purchase(self, sample_country_data, sample_weapons_catalog):
        """Should allow valid purchase"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 10)

        assert result['success'] is True
        assert result['order']['quantity'] == 10
        assert result['order']['weapon_id'] == "F-35"

    def test_insufficient_budget(self, sample_country_data, sample_weapons_catalog):
        """Should reject if budget insufficient"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 100)  # Way too many

        assert result['success'] is False
        assert 'failed_constraints' in result
        assert any('budget' in str(c).lower() for c in result.get('failed_constraints', []))

    def test_insufficient_relations(self, sample_country_data, sample_weapons_catalog):
        """Should reject if relations too low"""
        sample_country_data['relations']['USA']['score'] = 50  # Below 70

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 1)

        assert result['success'] is False
        assert any('relations' in str(c).lower() for c in result.get('failed_constraints', []))

    def test_not_allowed_buyer(self, sample_country_data, sample_weapons_catalog):
        """Should reject if not in allowed buyers list"""
        sample_country_data['meta']['country_code'] = 'XXX'

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 1)

        assert result['success'] is False
        assert 'not an approved buyer' in result['error']

    def test_exclusion_conflict(self, sample_country_data, sample_weapons_catalog):
        """Should reject if operating incompatible system"""
        # Add S-400 to inventory
        sample_country_data['military_inventory']['air_defense']['systems'].append({
            "model": "S-400",
            "type": "air_defense_system",
            "batteries": 2
        })

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 1)

        assert result['success'] is False

    def test_unknown_weapon(self, sample_country_data, sample_weapons_catalog):
        """Should reject unknown weapon"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("UnknownWeapon", 1)

        assert result['success'] is False
        assert 'Unknown weapon' in result['error']

    def test_purchase_deducts_budget(self, sample_country_data, sample_weapons_catalog):
        """Purchase should deduct from procurement budget"""
        old_budget = sample_country_data['budget']['allocation']['defense']['breakdown']['procurement']

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)  # 10 * $120M = $1.2B

        new_budget = sample_country_data['budget']['allocation']['defense']['breakdown']['procurement']
        assert new_budget < old_budget

    def test_purchase_adds_to_projects(self, sample_country_data, sample_weapons_catalog):
        """Purchase should add order to active projects"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)

        assert len(sample_country_data['active_projects']) == 1
        assert sample_country_data['active_projects'][0]['weapon_id'] == "F-35"


class TestDeliveries:
    """Test weapon delivery processing"""

    def test_delivery_starts_on_time(self, sample_country_data, sample_weapons_catalog):
        """Deliveries should start in expected year"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)

        # Move to delivery year (3-5 years delivery, so try year 2028)
        delivered = engine.process_deliveries(2028)

        assert len(delivered) > 0
        assert delivered[0]['weapon'] == "F-35 Lightning II"

    def test_no_delivery_before_time(self, sample_country_data, sample_weapons_catalog):
        """No deliveries before scheduled"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)

        delivered = engine.process_deliveries(2025)  # Too early

        assert len(delivered) == 0

    def test_inventory_updated(self, sample_country_data, sample_weapons_catalog):
        """Inventory should be updated on delivery"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 5)

        engine.process_deliveries(2028)

        # Check inventory
        fighters = sample_country_data['military_inventory']['aircraft']['fighters']
        f35 = next((f for f in fighters if f['model'] == "F-35 Lightning II"), None)

        assert f35 is not None
        assert f35['quantity'] > 0

    def test_partial_delivery(self, sample_country_data, sample_weapons_catalog):
        """Large orders should be delivered in batches"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 20)

        # Process first year of deliveries
        delivered_year1 = engine.process_deliveries(2028)

        # Should not deliver all at once
        assert delivered_year1[0]['remaining'] > 0

    def test_order_completes(self, sample_country_data, sample_weapons_catalog):
        """Order should be marked complete when fully delivered"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 4)

        # Process multiple years
        for year in range(2027, 2035):
            engine.process_deliveries(year)

        # Active projects should be cleared
        active_orders = engine.get_active_orders()
        assert len(active_orders) == 0


class TestActiveOrders:
    """Test active order tracking"""

    def test_get_active_orders(self, sample_country_data, sample_weapons_catalog):
        """Should return list of active orders"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)

        orders = engine.get_active_orders()

        assert len(orders) == 1
        assert orders[0]['weapon'] == "F-35 Lightning II"
        assert orders[0]['quantity'] == 10

    def test_active_orders_empty(self, sample_country_data, sample_weapons_catalog):
        """Should return empty list when no orders"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        orders = engine.get_active_orders()

        assert len(orders) == 0


class TestOrderCancellation:
    """Test order cancellation"""

    def test_cancel_order(self, sample_country_data, sample_weapons_catalog):
        """Should cancel order and provide partial refund"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 10)
        order_id = result['order']['id']

        cancel_result = engine.cancel_order(order_id)

        assert cancel_result['success'] is True
        assert 'refund' in cancel_result
        assert cancel_result['refund'] > 0

    def test_cancel_nonexistent_order(self, sample_country_data, sample_weapons_catalog):
        """Should fail for nonexistent order"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.cancel_order("nonexistent_order")

        assert result['success'] is False
        assert 'not found' in result['error']

    def test_cancel_damages_relations(self, sample_country_data, sample_weapons_catalog):
        """Cancellation should damage relations with manufacturer"""
        old_relations = sample_country_data['relations']['USA']['score']

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 10)
        order_id = result['order']['id']

        engine.cancel_order(order_id)

        new_relations = sample_country_data['relations']['USA']['score']
        assert new_relations < old_relations


class TestWeaponSales:
    """Test selling weapons from inventory"""

    def test_sell_weapons(self, sample_country_data, sample_weapons_catalog):
        """Should sell weapons from inventory"""
        # Add a friendly buyer
        sample_country_data['relations']['DEU'] = {
            'country_code': 'DEU',
            'score': 60
        }

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.sell_weapons("F-16C", 10, "DEU")

        assert result['success'] is True
        assert result['quantity'] == 10
        assert result['revenue_billions'] > 0

    def test_sell_insufficient_quantity(self, sample_country_data, sample_weapons_catalog):
        """Should fail if not enough weapons"""
        sample_country_data['relations']['DEU'] = {'score': 60}

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.sell_weapons("F-16C", 1000, "DEU")

        assert result['success'] is False
        assert 'Not enough' in result['error']

    def test_sell_to_hostile_nation(self, sample_country_data, sample_weapons_catalog):
        """Should refuse to sell to hostile nations"""
        sample_country_data['relations']['ENM'] = {
            'country_code': 'ENM',
            'score': -50
        }

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.sell_weapons("F-16C", 10, "ENM")

        assert result['success'] is False
        assert 'hostile' in result['error'].lower()

    def test_sell_nonexistent_weapon(self, sample_country_data, sample_weapons_catalog):
        """Should fail for weapons not in inventory"""
        sample_country_data['relations']['DEU'] = {'score': 60}

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.sell_weapons("Nonexistent Weapon", 1, "DEU")

        assert result['success'] is False
        assert 'not found' in result['error']

    def test_sell_improves_relations(self, sample_country_data, sample_weapons_catalog):
        """Selling weapons should improve relations"""
        sample_country_data['relations']['DEU'] = {
            'country_code': 'DEU',
            'score': 50
        }

        old_score = sample_country_data['relations']['DEU']['score']

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.sell_weapons("F-16C", 10, "DEU")

        new_score = sample_country_data['relations']['DEU']['score']
        assert new_score > old_score

    def test_sell_adds_revenue(self, sample_country_data, sample_weapons_catalog):
        """Selling weapons should add revenue"""
        sample_country_data['relations']['DEU'] = {'score': 60}
        old_revenue = sample_country_data['budget']['total_revenue_billions']

        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.sell_weapons("F-16C", 10, "DEU")

        new_revenue = sample_country_data['budget']['total_revenue_billions']
        assert new_revenue > old_revenue
