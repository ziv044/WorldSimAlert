"""
Budget Engine - Phase 4

Allows player to adjust budget allocation, taxes, and debt.
"""

from typing import Dict, List, Optional
from backend.engine.constraint_engine import ConstraintEngine


class BudgetEngine:
    """
    Manages government budget operations.

    Player actions:
    - Reallocate budget percentages
    - Raise/lower taxes
    - Take/repay debt
    - Adjust specific category funding
    """

    # Budget categories that can be adjusted
    ADJUSTABLE_CATEGORIES = [
        'defense', 'healthcare', 'education', 'infrastructure',
        'social_welfare', 'pensions', 'research', 'foreign_affairs',
        'internal_security', 'administration'
    ]

    # Categories that cannot be reduced to zero
    MINIMUM_ALLOCATION = {
        'defense': 1.0,
        'healthcare': 2.0,
        'education': 2.0,
        'social_welfare': 1.0,
        'pensions': 3.0,
        'administration': 1.0
    }

    def __init__(self, country_data: dict):
        self.data = country_data
        self.constraint_engine = ConstraintEngine(country_data)

    def adjust_allocation(
        self,
        category: str,
        new_percent: float,
        funding_source: str = "rebalance"
    ) -> Dict:
        """
        Adjust budget allocation for a category.

        Args:
            category: Budget category to adjust
            new_percent: New percentage of budget (0-100)
            funding_source: How to fund increase
                - 'rebalance': Take from other categories
                - 'debt': Increase spending with debt
                - 'taxes': Increase revenue with taxes

        Returns:
            Dict with success status and details
        """
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})

        if category not in allocation:
            return {'success': False, 'error': f'Unknown category: {category}'}

        # Check minimum allocation
        min_alloc = self.MINIMUM_ALLOCATION.get(category, 0)
        if new_percent < min_alloc:
            return {
                'success': False,
                'error': f'{category} cannot go below {min_alloc}%'
            }

        old_percent = allocation[category].get('percent_of_budget', 0)
        delta = new_percent - old_percent

        if abs(delta) < 0.01:
            return {'success': False, 'error': 'No significant change'}

        if funding_source == "rebalance":
            return self._rebalance_budget(category, new_percent, delta)
        elif funding_source == "debt":
            return self._fund_from_debt(category, new_percent, delta)
        elif funding_source == "taxes":
            return self._fund_from_taxes(category, new_percent, delta)
        else:
            return {'success': False, 'error': f'Unknown funding source: {funding_source}'}

    def _rebalance_budget(
        self,
        category: str,
        new_percent: float,
        delta: float
    ) -> Dict:
        """Redistribute budget from other categories."""
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})

        # Find categories that can be reduced
        reducible = {}
        for k, v in allocation.items():
            if k == category or k == 'debt_service':
                continue
            current = v.get('percent_of_budget', 0)
            minimum = self.MINIMUM_ALLOCATION.get(k, 0)
            reducible_amount = current - minimum
            if reducible_amount > 0:
                reducible[k] = reducible_amount

        if delta > 0:
            # Need to take from others
            total_reducible = sum(reducible.values())
            if total_reducible < delta:
                return {
                    'success': False,
                    'error': f'Cannot free up {delta:.1f}% from other categories (only {total_reducible:.1f}% available)'
                }

            # Proportionally reduce others
            changes = {}
            for k, available in reducible.items():
                reduction = (available / total_reducible) * delta
                new_val = allocation[k]['percent_of_budget'] - reduction
                allocation[k]['percent_of_budget'] = new_val
                allocation[k]['amount'] = budget['total_expenditure_billions'] * (new_val / 100)
                changes[k] = -reduction
        else:
            # Giving back to others
            changes = {}
            others = [k for k in allocation.keys() if k != category and k != 'debt_service']
            increase_each = abs(delta) / len(others)
            for k in others:
                new_val = allocation[k]['percent_of_budget'] + increase_each
                allocation[k]['percent_of_budget'] = new_val
                allocation[k]['amount'] = budget['total_expenditure_billions'] * (new_val / 100)
                changes[k] = increase_each

        # Apply new allocation
        allocation[category]['percent_of_budget'] = new_percent
        allocation[category]['amount'] = budget['total_expenditure_billions'] * (new_percent / 100)

        return {
            'success': True,
            'category': category,
            'old_percent': new_percent - delta,
            'new_percent': new_percent,
            'method': 'rebalance',
            'other_changes': changes
        }

    def _fund_from_debt(
        self,
        category: str,
        new_percent: float,
        delta: float
    ) -> Dict:
        """Increase budget via debt."""
        if delta <= 0:
            return {'success': False, 'error': 'Debt funding only for increases'}

        budget = self.data.get('budget', {})
        economy = self.data.get('economy', {})
        allocation = budget.get('allocation', {})

        additional_spending = budget['total_expenditure_billions'] * (delta / 100)

        # Check debt limits
        debt = economy.get('debt', {})
        current_ratio = debt.get('debt_to_gdp_percent', 60)
        new_debt = debt.get('total_billions', 0) + additional_spending
        gdp = economy.get('gdp_billions_usd', 500)
        new_ratio = (new_debt / gdp) * 100

        # Warn if debt getting high
        warning = None
        if new_ratio > 100:
            warning = 'CRITICAL: Debt exceeds 100% of GDP - high default risk'
        elif new_ratio > 80:
            warning = 'WARNING: Debt above 80% of GDP - credit rating at risk'
        elif new_ratio > 60:
            warning = 'CAUTION: Debt approaching sustainability limits'

        # Update totals
        budget['total_expenditure_billions'] += additional_spending
        budget['deficit_billions'] = (
            budget.get('deficit_billions', 0) + additional_spending
        )
        budget['deficit_to_gdp_percent'] = (budget['deficit_billions'] / gdp) * 100

        # Update allocation
        allocation[category]['percent_of_budget'] = new_percent
        allocation[category]['amount'] += additional_spending

        # Update debt
        debt['total_billions'] = new_debt
        debt['debt_to_gdp_percent'] = new_ratio

        return {
            'success': True,
            'category': category,
            'additional_spending': additional_spending,
            'new_deficit': budget['deficit_billions'],
            'new_debt_ratio': new_ratio,
            'method': 'debt',
            'warning': warning
        }

    def _fund_from_taxes(
        self,
        category: str,
        new_percent: float,
        delta: float
    ) -> Dict:
        """Increase budget via tax increase."""
        if delta <= 0:
            return {'success': False, 'error': 'Tax funding only for increases'}

        budget = self.data.get('budget', {})
        indices = self.data.get('indices', {})
        economy = self.data.get('economy', {})
        allocation = budget.get('allocation', {})

        additional_revenue = budget['total_revenue_billions'] * (delta / 100)

        # Update revenue
        budget['total_revenue_billions'] += additional_revenue

        # Happiness penalty for tax increase
        happiness_penalty = delta * 0.5
        public_trust_penalty = delta * 0.3

        old_happiness = indices.get('happiness', 70)
        old_trust = indices.get('public_trust', 60)

        indices['happiness'] = max(0, old_happiness - happiness_penalty)
        indices['public_trust'] = max(0, old_trust - public_trust_penalty)

        # GDP growth penalty (taxes reduce economic activity)
        economy['gdp_growth_potential'] = max(0,
            economy.get('gdp_growth_potential', 3.0) - delta * 0.1
        )

        # Update allocation
        allocation[category]['percent_of_budget'] = new_percent
        allocation[category]['amount'] += additional_revenue

        return {
            'success': True,
            'category': category,
            'additional_revenue': additional_revenue,
            'happiness_change': -happiness_penalty,
            'trust_change': -public_trust_penalty,
            'method': 'taxes'
        }

    def set_tax_rate(self, new_rate: float) -> Dict:
        """
        Set overall tax rate.

        Args:
            new_rate: New tax rate as percentage (15-50)
        """
        if new_rate < 15:
            return {'success': False, 'error': 'Tax rate cannot go below 15%'}
        if new_rate > 50:
            return {'success': False, 'error': 'Tax rate cannot exceed 50%'}

        budget = self.data.get('budget', {})
        economy = self.data.get('economy', {})
        indices = self.data.get('indices', {})

        old_rate = budget.get('tax_rate', 30)
        delta = new_rate - old_rate

        # Calculate revenue change
        gdp = economy.get('gdp_billions_usd', 500)
        old_revenue = budget.get('total_revenue_billions', 100)
        new_revenue = gdp * (new_rate / 100)
        revenue_change = new_revenue - old_revenue

        # Apply changes
        budget['tax_rate'] = new_rate
        budget['total_revenue_billions'] = new_revenue
        budget['deficit_billions'] = (
            budget.get('total_expenditure_billions', 100) - new_revenue
        )
        budget['deficit_to_gdp_percent'] = (budget['deficit_billions'] / gdp) * 100

        # Happiness effects
        if delta > 0:
            happiness_change = -delta * 0.8
            growth_change = -delta * 0.2
        else:
            happiness_change = abs(delta) * 0.5
            growth_change = abs(delta) * 0.1

        indices['happiness'] = max(0, min(100,
            indices.get('happiness', 70) + happiness_change
        ))
        economy['gdp_growth_potential'] = max(0, min(10,
            economy.get('gdp_growth_potential', 3) + growth_change
        ))

        return {
            'success': True,
            'old_rate': old_rate,
            'new_rate': new_rate,
            'revenue_change': revenue_change,
            'new_revenue': new_revenue,
            'happiness_change': happiness_change,
            'growth_change': growth_change
        }

    def take_debt(self, amount_billions: float) -> Dict:
        """
        Take on additional debt.

        Args:
            amount_billions: Amount to borrow
        """
        economy = self.data.get('economy', {})
        debt = economy.get('debt', {})
        reserves = economy.get('reserves', {})

        gdp = economy.get('gdp_billions_usd', 500)
        current_debt = debt.get('total_billions', 0)
        current_ratio = debt.get('debt_to_gdp_percent', 60)
        credit_rating = debt.get('credit_rating', 'A')

        # Check if can borrow based on credit rating
        max_debt_ratio = {
            'AAA': 120, 'AA': 100, 'A': 80,
            'BBB': 60, 'BB': 40, 'B': 30,
            'CCC': 20, 'D': 0
        }

        limit = max_debt_ratio.get(credit_rating, 60)
        new_debt = current_debt + amount_billions
        new_ratio = (new_debt / gdp) * 100

        if new_ratio > limit:
            return {
                'success': False,
                'error': f'Credit rating {credit_rating} limits borrowing. Max debt ratio: {limit}%'
            }

        # Apply debt
        debt['total_billions'] = new_debt
        debt['debt_to_gdp_percent'] = new_ratio

        # Add to reserves (immediate cash)
        reserves['foreign_reserves_billions'] = (
            reserves.get('foreign_reserves_billions', 100) + amount_billions
        )

        # Check for credit rating change
        rating_change = self._check_credit_rating_change(new_ratio)

        return {
            'success': True,
            'amount': amount_billions,
            'new_debt_total': new_debt,
            'new_debt_ratio': new_ratio,
            'rating_change': rating_change
        }

    def repay_debt(self, amount_billions: float) -> Dict:
        """
        Repay existing debt.

        Args:
            amount_billions: Amount to repay
        """
        economy = self.data.get('economy', {})
        budget = self.data.get('budget', {})
        debt = economy.get('debt', {})
        reserves = economy.get('reserves', {})

        current_debt = debt.get('total_billions', 0)
        available_reserves = reserves.get('foreign_reserves_billions', 0)

        if amount_billions > current_debt:
            return {'success': False, 'error': f'Cannot repay more than owed (${current_debt:.1f}B)'}

        if amount_billions > available_reserves:
            return {'success': False, 'error': f'Insufficient reserves (${available_reserves:.1f}B)'}

        # Apply repayment
        gdp = economy.get('gdp_billions_usd', 500)
        new_debt = current_debt - amount_billions
        new_ratio = (new_debt / gdp) * 100

        debt['total_billions'] = new_debt
        debt['debt_to_gdp_percent'] = new_ratio
        reserves['foreign_reserves_billions'] -= amount_billions

        # Check for credit rating improvement
        rating_change = self._check_credit_rating_change(new_ratio)

        return {
            'success': True,
            'amount': amount_billions,
            'new_debt_total': new_debt,
            'new_debt_ratio': new_ratio,
            'rating_change': rating_change
        }

    def _check_credit_rating_change(self, debt_ratio: float) -> Optional[Dict]:
        """Check if credit rating should change."""
        economy = self.data.get('economy', {})
        debt = economy.get('debt', {})
        current_rating = debt.get('credit_rating', 'A')

        rating_thresholds = [
            ('AAA', 30), ('AA', 45), ('A', 60),
            ('BBB', 75), ('BB', 90), ('B', 105),
            ('CCC', 120), ('D', 999)
        ]

        # Find appropriate rating
        new_rating = 'D'
        for rating, threshold in rating_thresholds:
            if debt_ratio <= threshold:
                new_rating = rating
                break

        if new_rating != current_rating:
            debt['credit_rating'] = new_rating
            return {
                'old_rating': current_rating,
                'new_rating': new_rating,
                'improved': rating_thresholds.index((new_rating, None)) <
                           rating_thresholds.index((current_rating, None))
                           if any(r[0] == new_rating for r in rating_thresholds) else False
            }

        return None

    def get_budget_summary(self) -> Dict:
        """Get summary of current budget state."""
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})

        return {
            'total_revenue': budget.get('total_revenue_billions', 0),
            'total_expenditure': budget.get('total_expenditure_billions', 0),
            'deficit': budget.get('deficit_billions', 0),
            'deficit_to_gdp': budget.get('deficit_to_gdp_percent', 0),
            'tax_rate': budget.get('tax_rate', 30),
            'allocation': {
                k: {
                    'percent': v.get('percent_of_budget', 0),
                    'amount': v.get('amount', 0)
                }
                for k, v in allocation.items()
            }
        }
