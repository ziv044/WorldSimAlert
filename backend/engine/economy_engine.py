"""
Economy Engine - Phase 3

Processes monthly economic calculations: GDP, revenue, expenditure, debt, inflation, trade.
"""

from typing import Dict, Optional


class EconomyEngine:
    """
    Manages economic simulation.

    Monthly tick updates:
    - GDP growth based on sectors, workforce, infrastructure
    - Government revenue from taxation
    - Government expenditure from budget
    - Debt changes from deficit/surplus
    - Inflation adjustments
    - Trade balance and reserves
    """

    def __init__(self, country_data: dict):
        self.data = country_data

    def process_monthly_tick(self) -> Dict:
        """
        Process all monthly economic changes.

        Returns:
            Dict of all changes made
        """
        changes = {}

        # 1. Calculate GDP change
        gdp_change = self._calculate_gdp_change()
        changes['gdp_growth_monthly'] = gdp_change

        # 2. Process government revenue
        revenue = self._calculate_revenue()
        changes['monthly_revenue'] = revenue

        # 3. Process expenditures
        expenditure = self._calculate_expenditure()
        changes['monthly_expenditure'] = expenditure

        # 4. Update debt
        debt_change = self._update_debt(revenue, expenditure)
        changes['debt_change'] = debt_change

        # 5. Inflation adjustment
        inflation = self._calculate_inflation()
        changes['inflation_rate'] = inflation

        # 6. Trade balance
        trade = self._calculate_trade_balance()
        changes['trade_balance_monthly'] = trade

        # 7. Reserves change
        reserves_change = self._update_reserves(trade)
        changes['reserves_change'] = reserves_change

        # 8. Update unemployment
        unemployment_change = self._calculate_unemployment()
        changes['unemployment_change'] = unemployment_change

        # Apply all changes
        self._apply_changes(changes)

        return changes

    def _calculate_gdp_change(self) -> float:
        """
        Calculate monthly GDP growth rate.

        Factors:
        - Base growth potential
        - Sector performance
        - Unemployment penalty
        - Infrastructure quality
        - Policy effects
        """
        economy = self.data.get('economy', {})
        sectors = self.data.get('sectors', {})
        workforce = self.data.get('workforce', {})
        infrastructure = self.data.get('infrastructure', {})

        # Base growth potential (annual)
        base_growth = economy.get('gdp_growth_potential', 3.0)

        # Sector contribution (average level affects growth)
        if sectors:
            sector_levels = [s.get('level', 50) for s in sectors.values()]
            sector_avg = sum(sector_levels) / len(sector_levels)
            sector_bonus = (sector_avg - 50) * 0.02  # +/- 0.02% per level from 50
        else:
            sector_bonus = 0

        # Unemployment penalty
        unemployment = workforce.get('unemployment_rate', 5.0)
        unemployment_penalty = max(0, (unemployment - 5) * 0.15)  # -0.15% per % above 5%

        # Infrastructure bonus
        digital_level = infrastructure.get('digital', {}).get('internet_penetration', 50)
        transport_level = infrastructure.get('transport', {}).get('quality_index', 50)
        infra_bonus = ((digital_level - 50) * 0.01 + (transport_level - 50) * 0.01) / 2

        # Calculate annual rate then convert to monthly
        annual_growth = base_growth + sector_bonus + infra_bonus - unemployment_penalty
        monthly_growth = annual_growth / 12

        return monthly_growth

    def _calculate_revenue(self) -> float:
        """
        Calculate monthly government revenue.

        Based on GDP, tax rates, and economic activity.
        """
        budget = self.data.get('budget', {})
        economy = self.data.get('economy', {})

        annual_revenue = budget.get('total_revenue_billions', 100)

        # Revenue scales with GDP relative to baseline
        baseline_gdp = 500  # Reference point
        current_gdp = economy.get('gdp_billions_usd', 500)
        gdp_ratio = current_gdp / baseline_gdp

        # Monthly revenue adjusted for GDP
        monthly_revenue = (annual_revenue * gdp_ratio) / 12

        return monthly_revenue

    def _calculate_expenditure(self) -> float:
        """Calculate monthly government expenditure."""
        budget = self.data.get('budget', {})
        return budget.get('total_expenditure_billions', 100) / 12

    def _update_debt(self, revenue: float, expenditure: float) -> float:
        """
        Update debt based on monthly deficit/surplus.

        Returns:
            Change in debt (positive = debt increased)
        """
        monthly_deficit = expenditure - revenue

        # Add interest on existing debt
        economy = self.data.get('economy', {})
        debt = economy.get('debt', {})
        total_debt = debt.get('total_billions', 0)
        interest_rate = debt.get('average_interest_rate', 3.0)

        # Monthly interest
        monthly_interest = (total_debt * interest_rate / 100) / 12

        return monthly_deficit + monthly_interest

    def _calculate_inflation(self) -> float:
        """
        Calculate current inflation rate.

        Factors:
        - Base inflation
        - Debt pressure
        - Growth pressure
        - Money supply (simplified)
        """
        economy = self.data.get('economy', {})

        base_inflation = economy.get('base_inflation', 2.5)

        # High debt increases inflation
        debt = economy.get('debt', {})
        debt_ratio = debt.get('debt_to_gdp_percent', 60)
        debt_pressure = max(0, (debt_ratio - 60) * 0.03)  # +0.03% per % above 60%

        # Strong growth can increase inflation
        growth_rate = economy.get('gdp_growth_rate', 3.0)
        growth_pressure = max(0, (growth_rate - 3) * 0.15)  # +0.15% per % growth above 3%

        # Low unemployment increases inflation (wage pressure)
        workforce = self.data.get('workforce', {})
        unemployment = workforce.get('unemployment_rate', 5.0)
        wage_pressure = max(0, (5 - unemployment) * 0.1)  # +0.1% per % below 5%

        total_inflation = base_inflation + debt_pressure + growth_pressure + wage_pressure

        # Clamp to reasonable range
        return max(0, min(25, total_inflation))

    def _calculate_trade_balance(self) -> float:
        """
        Calculate monthly trade balance from relations.

        Sums trade balances from all trading partners.
        """
        relations = self.data.get('relations', {})
        total_balance = 0

        for country, rel_data in relations.items():
            trade = rel_data.get('trade', {})
            annual_balance = trade.get('balance_billions', 0)
            total_balance += annual_balance

        return total_balance / 12  # Monthly

    def _update_reserves(self, trade_balance: float) -> float:
        """
        Update foreign reserves based on trade.

        Positive trade balance increases reserves.
        """
        # Trade surplus/deficit affects reserves
        return trade_balance

    def _calculate_unemployment(self) -> float:
        """
        Calculate change in unemployment rate.

        Based on GDP growth, sector employment, policy effects.
        """
        economy = self.data.get('economy', {})
        sectors = self.data.get('sectors', {})

        # GDP growth reduces unemployment
        growth_rate = economy.get('gdp_growth_rate', 3.0)
        growth_effect = -growth_rate * 0.3  # -0.3% unemployment per 1% growth

        # Sector investment creates jobs
        total_investment = sum(
            s.get('recent_investment', 0) for s in sectors.values()
        )
        investment_effect = -total_investment * 0.01  # Each $1B creates jobs

        # Natural drift toward equilibrium (5%)
        workforce = self.data.get('workforce', {})
        current = workforce.get('unemployment_rate', 5.0)
        equilibrium_pull = (5.0 - current) * 0.1

        # Monthly change
        change = (growth_effect + investment_effect + equilibrium_pull) / 12

        return change

    def _apply_changes(self, changes: Dict) -> None:
        """Apply calculated changes to country data."""
        economy = self.data.get('economy', {})
        workforce = self.data.get('workforce', {})

        # GDP
        gdp_growth = changes['gdp_growth_monthly']
        old_gdp = economy.get('gdp_billions_usd', 500)
        new_gdp = old_gdp * (1 + gdp_growth / 100)
        economy['gdp_billions_usd'] = new_gdp
        economy['gdp_growth_rate'] = gdp_growth * 12  # Annualize for display

        # GDP per capita
        population = self.data.get('demographics', {}).get('total_population', 10_000_000)
        economy['gdp_per_capita_usd'] = (new_gdp * 1e9) / population

        # Debt
        debt = economy.get('debt', {})
        debt['total_billions'] = debt.get('total_billions', 0) + changes['debt_change']
        debt['debt_to_gdp_percent'] = (debt['total_billions'] / new_gdp) * 100

        # Inflation
        economy['inflation_rate'] = changes['inflation_rate']

        # Reserves
        reserves = economy.get('reserves', {})
        reserves['foreign_reserves_billions'] = (
            reserves.get('foreign_reserves_billions', 100) + changes['reserves_change']
        )

        # Calculate months of imports covered
        budget = self.data.get('budget', {})
        monthly_imports = budget.get('total_expenditure_billions', 100) * 0.25 / 12
        if monthly_imports > 0:
            reserves['months_of_imports_covered'] = (
                reserves['foreign_reserves_billions'] / monthly_imports
            )

        # Unemployment
        current_unemployment = workforce.get('unemployment_rate', 5.0)
        new_unemployment = max(0, min(30, current_unemployment + changes['unemployment_change']))
        workforce['unemployment_rate'] = new_unemployment

        # Update budget deficit
        budget = self.data.get('budget', {})
        budget['deficit_billions'] = (
            budget.get('total_expenditure_billions', 100) -
            budget.get('total_revenue_billions', 100)
        )
        budget['deficit_to_gdp_percent'] = (budget['deficit_billions'] / new_gdp) * 100

    def get_economic_summary(self) -> Dict:
        """Get a summary of current economic state."""
        economy = self.data.get('economy', {})
        budget = self.data.get('budget', {})
        workforce = self.data.get('workforce', {})

        return {
            "gdp_billions": economy.get('gdp_billions_usd', 0),
            "gdp_per_capita": economy.get('gdp_per_capita_usd', 0),
            "gdp_growth_rate": economy.get('gdp_growth_rate', 0),
            "inflation_rate": economy.get('inflation_rate', 0),
            "unemployment_rate": workforce.get('unemployment_rate', 0),
            "debt_to_gdp": economy.get('debt', {}).get('debt_to_gdp_percent', 0),
            "deficit_to_gdp": budget.get('deficit_to_gdp_percent', 0),
            "foreign_reserves": economy.get('reserves', {}).get('foreign_reserves_billions', 0),
            "credit_rating": economy.get('debt', {}).get('credit_rating', 'A')
        }

    def project_future(self, months: int) -> Dict:
        """
        Project economic state N months into the future.

        Does not modify actual data, just simulates.
        """
        import copy
        simulated_data = copy.deepcopy(self.data)
        simulated_engine = EconomyEngine(simulated_data)

        projections = []
        for i in range(months):
            changes = simulated_engine.process_monthly_tick()
            projections.append({
                "month": i + 1,
                "changes": changes,
                "summary": simulated_engine.get_economic_summary()
            })

        return {
            "months_projected": months,
            "final_state": simulated_engine.get_economic_summary(),
            "monthly_projections": projections
        }
