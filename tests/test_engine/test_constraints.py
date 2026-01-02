# tests/test_engine/test_constraints.py
import pytest
from backend.engine.constraint_engine import ConstraintEngine, ConstraintType


class TestBudgetConstraints:
    """Test budget availability checks"""

    def test_budget_available(self, sample_country_data):
        """Should pass when budget is available"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(2.0, "procurement")

        assert result.satisfied is True
        assert result.current_value == 4.0  # From fixture
        assert result.required_value == 2.0

    def test_budget_insufficient(self, sample_country_data):
        """Should fail when budget is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(10.0, "procurement")

        assert result.satisfied is False
        assert "Need $10.00B" in result.message

    def test_budget_exact_amount(self, sample_country_data):
        """Should pass when budget exactly matches"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(4.0, "procurement")

        assert result.satisfied is True

    def test_budget_zero(self, sample_country_data):
        """Should pass when requesting zero budget"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(0, "procurement")

        assert result.satisfied is True

    def test_budget_negative_request(self, sample_country_data):
        """Should handle negative budget requests"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(-1.0, "procurement")

        assert result.satisfied is True  # Negative is always satisfied


class TestWorkforceConstraints:
    """Test workforce availability checks"""

    def test_workforce_available(self, sample_country_data):
        """Should pass when workforce is available"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"engineering_software": 3_000}  # Have 5000 free
        result = engine.check_workforce(requirements)

        assert result.satisfied is True

    def test_workforce_insufficient(self, sample_country_data):
        """Should fail when workforce is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"engineering_software": 10_000}  # Only 5000 free
        result = engine.check_workforce(requirements)

        assert result.satisfied is False
        assert result.missing_items is not None
        assert any("engineering_software" in item for item in result.missing_items)

    def test_workforce_multiple_pools(self, sample_country_data):
        """Should check multiple pools"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {
            "engineering_software": 3_000,
            "military_pilots": 50
        }
        result = engine.check_workforce(requirements)

        assert result.satisfied is True

    def test_workforce_one_fails(self, sample_country_data):
        """Should fail if any pool is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {
            "engineering_software": 3_000,
            "military_pilots": 500  # Only 100 free
        }
        result = engine.check_workforce(requirements)

        assert result.satisfied is False
        assert any("military_pilots" in item for item in result.missing_items)

    def test_workforce_unknown_pool(self, sample_country_data):
        """Should fail for unknown pool"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"nonexistent_pool": 100}
        result = engine.check_workforce(requirements)

        assert result.satisfied is False
        assert "not found" in str(result.missing_items)

    def test_workforce_empty_requirements(self, sample_country_data):
        """Should pass with empty requirements"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_workforce({})

        assert result.satisfied is True


class TestRelationsConstraints:
    """Test diplomatic relations checks"""

    def test_relations_sufficient(self, sample_country_data):
        """Should pass when relations are high enough"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("USA", 70)

        assert result.satisfied is True
        assert result.current_value == 80

    def test_relations_insufficient(self, sample_country_data):
        """Should fail when relations are too low"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("RUS", 50)  # Score is 20

        assert result.satisfied is False
        assert result.current_value == 20
        assert result.required_value == 50

    def test_relations_unknown_country(self, sample_country_data):
        """Should fail for unknown country"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("XYZ", 50)

        assert result.satisfied is False
        assert result.current_value == 0

    def test_relations_exact_score(self, sample_country_data):
        """Should pass when relations exactly match requirement"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("USA", 80)  # Score is exactly 80

        assert result.satisfied is True

    def test_relations_negative_required(self, sample_country_data):
        """Should handle negative relation requirements"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("RUS", -50)  # Score is 20, need -50

        assert result.satisfied is True


class TestInfrastructureConstraints:
    """Test infrastructure level checks"""

    def test_infrastructure_sufficient(self, sample_country_data):
        """Should pass when infrastructure is sufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"digital.level": 70}
        result = engine.check_infrastructure(requirements)

        assert result.satisfied is True

    def test_infrastructure_insufficient(self, sample_country_data):
        """Should fail when infrastructure is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"digital.level": 95}
        result = engine.check_infrastructure(requirements)

        assert result.satisfied is False

    def test_infrastructure_nested_path(self, sample_country_data):
        """Should handle nested paths"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"industrial_facilities.military_factories": 15}
        result = engine.check_infrastructure(requirements)

        assert result.satisfied is True

    def test_infrastructure_invalid_path(self, sample_country_data):
        """Should fail for invalid path"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"nonexistent.path": 50}
        result = engine.check_infrastructure(requirements)

        assert result.satisfied is False

    def test_infrastructure_empty_requirements(self, sample_country_data):
        """Should pass with empty requirements"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_infrastructure({})

        assert result.satisfied is True


class TestExclusionConstraints:
    """Test system exclusion checks"""

    def test_no_conflicts(self, sample_country_data):
        """Should pass when no conflicting systems"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_exclusion(["S-400", "Su-35"])

        assert result.satisfied is True

    def test_has_conflict(self, sample_country_data):
        """Should fail when operating conflicting system"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_exclusion(["F-16C"])  # We have this

        assert result.satisfied is False
        assert "F-16C" in result.missing_items

    def test_empty_exclusion_list(self, sample_country_data):
        """Should pass with empty exclusion list"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_exclusion([])

        assert result.satisfied is True

    def test_multiple_conflicts(self, sample_country_data):
        """Should report all conflicts"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_exclusion(["F-16C", "M1A2 Abrams", "Su-35"])

        assert result.satisfied is False
        # Should find F-16C and M1A2 Abrams
        assert "F-16C" in result.missing_items


class TestSectorLevelConstraints:
    """Test sector development level checks"""

    def test_sector_sufficient(self, sample_country_data):
        """Should pass when sector level is high enough"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_sector_level("technology", 70)

        assert result.satisfied is True

    def test_sector_insufficient(self, sample_country_data):
        """Should fail when sector level is too low"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_sector_level("manufacturing", 80)

        assert result.satisfied is False
        assert result.current_value == 60

    def test_sector_unknown(self, sample_country_data):
        """Should handle unknown sector"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_sector_level("nonexistent_sector", 50)

        assert result.satisfied is False
        assert result.current_value == 0


class TestPoliticalCapitalConstraints:
    """Test political capital checks"""

    def test_political_capital_sufficient(self, sample_country_data):
        """Should pass when political capital is available"""
        sample_country_data['indices']['political_capital'] = 60
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_political_capital(50)

        assert result.satisfied is True

    def test_political_capital_insufficient(self, sample_country_data):
        """Should fail when political capital is insufficient"""
        sample_country_data['indices']['political_capital'] = 30
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_political_capital(50)

        assert result.satisfied is False

    def test_political_capital_default(self, sample_country_data):
        """Should use default value when not specified"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_political_capital(40)

        # Default is 50
        assert result.satisfied is True


class TestCooldownConstraints:
    """Test cooldown timer checks"""

    def test_no_cooldown(self, sample_country_data):
        """Should pass when action never used"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_cooldown("aid_send", 3)

        assert result.satisfied is True

    def test_cooldown_expired(self, sample_country_data):
        """Should pass when cooldown expired"""
        sample_country_data['cooldowns'] = {
            'aid_send': {'year': 2023, 'month': 6}
        }
        sample_country_data['meta']['current_date'] = {'year': 2024, 'month': 1}

        engine = ConstraintEngine(sample_country_data)
        result = engine.check_cooldown("aid_send", 3)

        assert result.satisfied is True

    def test_cooldown_active(self, sample_country_data):
        """Should fail when cooldown still active"""
        sample_country_data['cooldowns'] = {
            'aid_send': {'year': 2024, 'month': 1}
        }
        sample_country_data['meta']['current_date'] = {'year': 2024, 'month': 2}

        engine = ConstraintEngine(sample_country_data)
        result = engine.check_cooldown("aid_send", 3)

        assert result.satisfied is False


class TestCombinedConstraints:
    """Test checking multiple constraints together"""

    def test_all_pass(self, sample_country_data):
        """Should pass when all constraints are met"""
        engine = ConstraintEngine(sample_country_data)

        constraints = {
            "budget": {"amount_billions": 2.0, "budget_category": "procurement"},
            "relations": {"USA": 70},
            "workforce": {"engineering_software": 1_000}
        }

        all_satisfied, results = engine.check_all(constraints)

        assert all_satisfied is True
        assert all(r.satisfied for r in results)

    def test_one_fails(self, sample_country_data):
        """Should fail when any constraint fails"""
        engine = ConstraintEngine(sample_country_data)

        constraints = {
            "budget": {"amount_billions": 2.0, "budget_category": "procurement"},
            "relations": {"RUS": 70}  # Only 20
        }

        all_satisfied, results = engine.check_all(constraints)

        assert all_satisfied is False
        failed = [r for r in results if not r.satisfied]
        assert len(failed) == 1
        assert failed[0].constraint_type == ConstraintType.RELATIONS

    def test_multiple_fail(self, sample_country_data):
        """Should report all failed constraints"""
        engine = ConstraintEngine(sample_country_data)

        constraints = {
            "budget": {"amount_billions": 100.0, "budget_category": "procurement"},
            "relations": {"RUS": 70},
            "workforce": {"nonexistent_pool": 1000}
        }

        all_satisfied, results = engine.check_all(constraints)

        assert all_satisfied is False
        failed = [r for r in results if not r.satisfied]
        assert len(failed) >= 3

    def test_f35_purchase_scenario(self, sample_country_data):
        """Should correctly evaluate F-35 purchase constraints"""
        engine = ConstraintEngine(sample_country_data)

        # F-35 requirements
        constraints = {
            "budget": {"amount_billions": 2.4, "budget_category": "procurement"},
            "relations": {"USA": 70},
            "exclusion": ["S-400", "Su-35"]
        }

        all_satisfied, results = engine.check_all(constraints)

        assert all_satisfied is True

    def test_get_failed_constraints(self, sample_country_data):
        """Should return only failed constraints"""
        engine = ConstraintEngine(sample_country_data)

        constraints = {
            "budget": {"amount_billions": 2.0, "budget_category": "procurement"},
            "relations": {"RUS": 70}
        }

        failed = engine.get_failed_constraints(constraints)

        assert len(failed) == 1
        assert failed[0].constraint_type == ConstraintType.RELATIONS

    def test_empty_constraints(self, sample_country_data):
        """Should pass with empty constraints"""
        engine = ConstraintEngine(sample_country_data)

        all_satisfied, results = engine.check_all({})

        assert all_satisfied is True
        assert len(results) == 0
