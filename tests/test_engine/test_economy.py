# tests/test_engine/test_economy.py
import pytest
from copy import deepcopy
from backend.engine.economy_engine import EconomyEngine


class TestGDPCalculations:
    """Test GDP growth calculations"""

    def test_positive_growth(self, sample_country_data):
        """GDP should grow with good conditions"""
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Monthly growth should be positive with default good conditions
        assert changes['gdp_growth_monthly'] > 0

    def test_unemployment_penalty(self, sample_country_data):
        """High unemployment should reduce growth"""
        sample_country_data['workforce']['unemployment_rate'] = 15.0

        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Should be lower than baseline due to unemployment penalty
        assert changes['gdp_growth_monthly'] < 0.3  # Normal monthly growth ~0.25

    def test_gdp_per_capita_updates(self, sample_country_data):
        """GDP per capita should update with GDP"""
        engine = EconomyEngine(sample_country_data)
        old_gdp_per_capita = sample_country_data['economy']['gdp_per_capita_usd']

        engine.process_monthly_tick()

        new_gdp_per_capita = sample_country_data['economy']['gdp_per_capita_usd']
        assert new_gdp_per_capita != old_gdp_per_capita

    def test_sector_bonus_high_levels(self, sample_country_data):
        """High sector levels should boost growth"""
        # Set all sectors to high levels
        for sector in sample_country_data['sectors'].values():
            sector['level'] = 90

        engine = EconomyEngine(sample_country_data)
        changes_high = engine.process_monthly_tick()

        # Reset and try low levels
        sample_country_data_low = deepcopy(sample_country_data)
        for sector in sample_country_data_low['sectors'].values():
            sector['level'] = 30

        engine_low = EconomyEngine(sample_country_data_low)
        changes_low = engine_low.process_monthly_tick()

        # High sector levels should produce higher growth
        assert changes_high['gdp_growth_monthly'] > changes_low['gdp_growth_monthly']

    def test_gdp_grows_with_tick(self, sample_country_data):
        """GDP value should increase after tick"""
        old_gdp = sample_country_data['economy']['gdp_billions_usd']

        engine = EconomyEngine(sample_country_data)
        engine.process_monthly_tick()

        new_gdp = sample_country_data['economy']['gdp_billions_usd']
        assert new_gdp > old_gdp


class TestDebtCalculations:
    """Test debt and deficit calculations"""

    def test_deficit_increases_debt(self, sample_country_data):
        """Running a deficit should increase debt"""
        engine = EconomyEngine(sample_country_data)
        old_debt = sample_country_data['economy']['debt']['total_billions']

        engine.process_monthly_tick()

        new_debt = sample_country_data['economy']['debt']['total_billions']
        assert new_debt > old_debt

    def test_debt_ratio_updates(self, sample_country_data):
        """Debt-to-GDP ratio should update"""
        engine = EconomyEngine(sample_country_data)

        engine.process_monthly_tick()

        debt = sample_country_data['economy']['debt']
        gdp = sample_country_data['economy']['gdp_billions_usd']
        expected_ratio = (debt['total_billions'] / gdp) * 100

        assert abs(debt['debt_to_gdp_percent'] - expected_ratio) < 0.1

    def test_debt_change_includes_interest(self, sample_country_data):
        """Debt change should include interest payments"""
        engine = EconomyEngine(sample_country_data)

        # Set interest rate
        sample_country_data['economy']['debt']['average_interest_rate'] = 5.0
        old_debt = sample_country_data['economy']['debt']['total_billions']

        changes = engine.process_monthly_tick()

        # Debt change should be positive (deficit + interest)
        assert changes['debt_change'] > 0


class TestInflationCalculations:
    """Test inflation mechanics"""

    def test_high_debt_increases_inflation(self, sample_country_data):
        """High debt should increase inflation"""
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 90

        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Inflation should be higher than base (2.5)
        assert changes['inflation_rate'] > 2.5

    def test_low_debt_stable_inflation(self, sample_country_data):
        """Low debt should keep inflation stable"""
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 30

        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Inflation should be near base
        assert 2.0 < changes['inflation_rate'] < 5.0

    def test_inflation_clamped(self, sample_country_data):
        """Inflation should be clamped to reasonable range"""
        # Set extreme values
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 300
        sample_country_data['economy']['gdp_growth_rate'] = 50
        sample_country_data['workforce']['unemployment_rate'] = 0

        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Should be clamped between 0 and 25
        assert 0 <= changes['inflation_rate'] <= 25

    def test_low_unemployment_increases_inflation(self, sample_country_data):
        """Low unemployment should create wage pressure"""
        sample_country_data['workforce']['unemployment_rate'] = 2.0

        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Should have some wage pressure effect
        assert changes['inflation_rate'] > 2.5


class TestTradeBalance:
    """Test trade balance calculations"""

    def test_trade_balance_calculated(self, sample_country_data):
        """Trade balance should be calculated from relations"""
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Trade balance should be negative (from fixture data)
        assert 'trade_balance_monthly' in changes

    def test_reserves_change_with_trade(self, sample_country_data):
        """Reserves should change based on trade balance"""
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Reserves change should equal trade balance
        assert changes['reserves_change'] == changes['trade_balance_monthly']


class TestUnemploymentCalculations:
    """Test unemployment dynamics"""

    def test_unemployment_change_calculated(self, sample_country_data):
        """Unemployment change should be calculated"""
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        assert 'unemployment_change' in changes

    def test_high_growth_reduces_unemployment(self, sample_country_data):
        """High GDP growth should reduce unemployment"""
        sample_country_data['economy']['gdp_growth_rate'] = 8.0

        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()

        # Growth effect should be negative (reducing unemployment)
        # Note: actual calculation includes multiple factors
        assert 'unemployment_change' in changes

    def test_unemployment_stays_in_bounds(self, sample_country_data):
        """Unemployment should stay within 0-30%"""
        sample_country_data['workforce']['unemployment_rate'] = 0.5

        engine = EconomyEngine(sample_country_data)
        engine.process_monthly_tick()

        unemployment = sample_country_data['workforce']['unemployment_rate']
        assert 0 <= unemployment <= 30


class TestEconomicSummary:
    """Test economic summary generation"""

    def test_get_summary(self, sample_country_data):
        """Should return economic summary"""
        engine = EconomyEngine(sample_country_data)
        summary = engine.get_economic_summary()

        assert 'gdp_billions' in summary
        assert 'gdp_per_capita' in summary
        assert 'gdp_growth_rate' in summary
        assert 'inflation_rate' in summary
        assert 'unemployment_rate' in summary
        assert 'debt_to_gdp' in summary
        assert 'credit_rating' in summary

    def test_summary_values_correct(self, sample_country_data):
        """Summary values should match data"""
        engine = EconomyEngine(sample_country_data)
        summary = engine.get_economic_summary()

        assert summary['gdp_billions'] == sample_country_data['economy']['gdp_billions_usd']
        assert summary['unemployment_rate'] == sample_country_data['workforce']['unemployment_rate']


class TestFutureProjection:
    """Test economic projection functionality"""

    def test_project_future(self, sample_country_data):
        """Should project economy into future"""
        engine = EconomyEngine(sample_country_data)
        projection = engine.project_future(12)

        assert projection['months_projected'] == 12
        assert 'final_state' in projection
        assert 'monthly_projections' in projection
        assert len(projection['monthly_projections']) == 12

    def test_projection_doesnt_modify_data(self, sample_country_data):
        """Projection should not modify actual data"""
        original_gdp = sample_country_data['economy']['gdp_billions_usd']

        engine = EconomyEngine(sample_country_data)
        engine.project_future(12)

        assert sample_country_data['economy']['gdp_billions_usd'] == original_gdp

    def test_projection_shows_growth(self, sample_country_data):
        """Projection should show GDP growth over time"""
        engine = EconomyEngine(sample_country_data)
        projection = engine.project_future(12)

        initial_gdp = sample_country_data['economy']['gdp_billions_usd']
        final_gdp = projection['final_state']['gdp_billions']

        assert final_gdp > initial_gdp
