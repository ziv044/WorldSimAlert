"""
Constraint Engine - Phase 2

Validates player actions against prerequisites (budget, workforce, relations, etc.).
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


class ConstraintType(Enum):
    """Types of constraints that can block player actions."""
    BUDGET = "budget"
    WORKFORCE = "workforce"
    INFRASTRUCTURE = "infrastructure"
    RELATIONS = "relations"
    SECTOR_LEVEL = "sector_level"
    EXCLUSION = "exclusion"
    POLITICAL = "political"
    TIME = "time"
    COOLDOWN = "cooldown"


@dataclass
class ConstraintResult:
    """Result of a constraint check."""
    satisfied: bool
    constraint_type: ConstraintType
    message: str
    current_value: Optional[float] = None
    required_value: Optional[float] = None
    missing_items: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "satisfied": self.satisfied,
            "constraint_type": self.constraint_type.value,
            "message": self.message,
            "current_value": self.current_value,
            "required_value": self.required_value,
            "missing_items": self.missing_items
        }


class ConstraintEngine:
    """
    Validates player actions against game constraints.

    Supports checking:
    - Budget availability
    - Workforce requirements
    - Infrastructure prerequisites
    - Diplomatic relations
    - Sector development levels
    - System exclusions (e.g., can't buy F-35 if operating S-400)
    - Political capital
    - Cooldown timers
    """

    def __init__(self, country_data: dict):
        self.data = country_data

    def check_budget(
        self,
        amount_billions: float,
        budget_category: str = "procurement"
    ) -> ConstraintResult:
        """
        Check if budget is available for a purchase.

        Args:
            amount_billions: Required amount in billions USD
            budget_category: Which budget pool to check ('procurement', 'development', etc.)
        """
        available = self._get_available_budget(budget_category)

        return ConstraintResult(
            satisfied=available >= amount_billions,
            constraint_type=ConstraintType.BUDGET,
            message=f"Need ${amount_billions:.2f}B, have ${available:.2f}B available in {budget_category}",
            current_value=available,
            required_value=amount_billions
        )

    def check_workforce(
        self,
        requirements: Dict[str, int]
    ) -> ConstraintResult:
        """
        Check if workforce requirements are met.

        Args:
            requirements: Dict of {pool_name: required_count}
        """
        pools = self.data.get('workforce', {}).get('expertise_pools', {})
        missing = []

        for pool_name, required_count in requirements.items():
            if pool_name not in pools:
                missing.append(f"{pool_name}: pool not found")
                continue

            pool = pools[pool_name]
            available = pool.get('available', 0) - pool.get('employed', 0)
            if available < required_count:
                missing.append(f"{pool_name}: need {required_count:,}, have {available:,} free")

        return ConstraintResult(
            satisfied=len(missing) == 0,
            constraint_type=ConstraintType.WORKFORCE,
            message="Workforce requirements " + ("met" if not missing else "not met"),
            missing_items=missing if missing else None
        )

    def check_infrastructure(
        self,
        requirements: Dict[str, float]
    ) -> ConstraintResult:
        """
        Check infrastructure requirements using dot notation paths.

        Args:
            requirements: Dict of {path: min_value}
                         e.g., {'digital.internet_penetration': 80}
        """
        missing = []

        for path, required_value in requirements.items():
            current = self._get_nested_value(self.data.get('infrastructure', {}), path)
            if current is None:
                missing.append(f"{path}: not found")
            elif current < required_value:
                missing.append(f"{path}: need {required_value}, have {current}")

        return ConstraintResult(
            satisfied=len(missing) == 0,
            constraint_type=ConstraintType.INFRASTRUCTURE,
            message="Infrastructure requirements " + ("met" if not missing else "not met"),
            missing_items=missing if missing else None
        )

    def check_relations(
        self,
        country_code: str,
        min_score: int
    ) -> ConstraintResult:
        """
        Check if relations with a country are high enough.

        Args:
            country_code: Target country code (e.g., 'USA')
            min_score: Minimum required relation score (-100 to 100)
        """
        relations = self.data.get('relations', {})
        country_relations = relations.get(country_code, {})
        current_score = country_relations.get('score', 0)

        return ConstraintResult(
            satisfied=current_score >= min_score,
            constraint_type=ConstraintType.RELATIONS,
            message=f"Relations with {country_code}: {current_score} (need {min_score})",
            current_value=current_score,
            required_value=min_score
        )

    def check_sector_level(
        self,
        sector_name: str,
        min_level: int
    ) -> ConstraintResult:
        """
        Check if a sector is developed enough.

        Args:
            sector_name: Name of the sector (e.g., 'technology')
            min_level: Minimum required level (0-100)
        """
        sectors = self.data.get('sectors', {})
        sector = sectors.get(sector_name, {})
        current_level = sector.get('level', 0)

        return ConstraintResult(
            satisfied=current_level >= min_level,
            constraint_type=ConstraintType.SECTOR_LEVEL,
            message=f"Sector {sector_name}: level {current_level} (need {min_level})",
            current_value=current_level,
            required_value=min_level
        )

    def check_exclusion(
        self,
        forbidden_systems: List[str]
    ) -> ConstraintResult:
        """
        Check if country operates forbidden/incompatible systems.

        Args:
            forbidden_systems: List of system model names that would conflict
                              e.g., ['S-400', 'Su-35'] for F-35 purchase
        """
        inventory = self.data.get('military_inventory', {})
        operating = self._get_all_system_models(inventory)

        conflicts = [sys for sys in forbidden_systems if sys in operating]

        return ConstraintResult(
            satisfied=len(conflicts) == 0,
            constraint_type=ConstraintType.EXCLUSION,
            message="No conflicting systems" if not conflicts else f"Operating conflicting systems: {conflicts}",
            missing_items=conflicts if conflicts else None
        )

    def check_political_capital(
        self,
        required: int
    ) -> ConstraintResult:
        """
        Check if enough political capital is available.

        Args:
            required: Amount of political capital needed
        """
        indices = self.data.get('indices', {})
        current = indices.get('political_capital', 50)

        return ConstraintResult(
            satisfied=current >= required,
            constraint_type=ConstraintType.POLITICAL,
            message=f"Political capital: {current} (need {required})",
            current_value=current,
            required_value=required
        )

    def check_cooldown(
        self,
        action_type: str,
        cooldown_months: int
    ) -> ConstraintResult:
        """
        Check if an action is on cooldown.

        Args:
            action_type: Type of action to check
            cooldown_months: Required months since last use
        """
        cooldowns = self.data.get('cooldowns', {})
        last_used = cooldowns.get(action_type)

        if last_used is None:
            return ConstraintResult(
                satisfied=True,
                constraint_type=ConstraintType.COOLDOWN,
                message=f"{action_type}: ready (never used)"
            )

        current_date = self.data.get('meta', {}).get('current_date', {})
        current_months = current_date.get('year', 2024) * 12 + current_date.get('month', 1)
        last_months = last_used.get('year', 2024) * 12 + last_used.get('month', 1)
        months_passed = current_months - last_months

        return ConstraintResult(
            satisfied=months_passed >= cooldown_months,
            constraint_type=ConstraintType.COOLDOWN,
            message=f"{action_type}: {months_passed} months passed (need {cooldown_months})",
            current_value=months_passed,
            required_value=cooldown_months
        )

    def check_all(
        self,
        constraints: Dict[str, Any]
    ) -> Tuple[bool, List[ConstraintResult]]:
        """
        Check multiple constraints at once.

        Args:
            constraints: Dict of constraint specifications:
                {
                    'budget': {'amount_billions': 2.4, 'budget_category': 'procurement'},
                    'workforce': {'engineers': 1000, 'technicians': 500},
                    'infrastructure': {'digital.internet_penetration': 80},
                    'relations': {'USA': 70, 'GER': 50},
                    'sector_level': {'technology': 60},
                    'exclusion': ['S-400', 'Su-35'],
                    'political': 20,
                    'cooldown': {'action_type': 'aid_send', 'cooldown_months': 3}
                }

        Returns:
            Tuple of (all_satisfied: bool, results: List[ConstraintResult])
        """
        results = []

        if 'budget' in constraints:
            results.append(self.check_budget(**constraints['budget']))

        if 'workforce' in constraints:
            results.append(self.check_workforce(constraints['workforce']))

        if 'infrastructure' in constraints:
            results.append(self.check_infrastructure(constraints['infrastructure']))

        if 'relations' in constraints:
            for country, min_score in constraints['relations'].items():
                results.append(self.check_relations(country, min_score))

        if 'sector_level' in constraints:
            for sector, min_level in constraints['sector_level'].items():
                results.append(self.check_sector_level(sector, min_level))

        if 'exclusion' in constraints:
            results.append(self.check_exclusion(constraints['exclusion']))

        if 'political' in constraints:
            results.append(self.check_political_capital(constraints['political']))

        if 'cooldown' in constraints:
            results.append(self.check_cooldown(**constraints['cooldown']))

        all_satisfied = all(r.satisfied for r in results)
        return all_satisfied, results

    def get_failed_constraints(
        self,
        constraints: Dict[str, Any]
    ) -> List[ConstraintResult]:
        """Get only the failed constraints."""
        _, results = self.check_all(constraints)
        return [r for r in results if not r.satisfied]

    # Helper methods

    def _get_available_budget(self, category: str) -> float:
        """Get available budget for a category."""
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})

        if category == 'procurement':
            defense = allocation.get('defense', {})
            breakdown = defense.get('breakdown', {})
            return breakdown.get('procurement', 0)
        elif category == 'development':
            # Sum of infrastructure and sector investment budgets
            infra = allocation.get('infrastructure', {}).get('amount', 0)
            return infra * 0.5  # Assume 50% available for new projects
        elif category == 'aid':
            foreign = allocation.get('foreign_affairs', {})
            return foreign.get('amount', 0) * 0.3  # 30% for aid
        else:
            # Generic: check if category exists in allocation
            cat_data = allocation.get(category, {})
            return cat_data.get('amount', 0)

    def _get_nested_value(self, data: dict, path: str) -> Optional[float]:
        """Get value from nested dict using dot notation."""
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        if isinstance(current, (int, float)):
            return float(current)
        return None

    def _get_all_system_models(self, inventory: dict) -> List[str]:
        """Extract all weapon model names from military inventory."""
        models = []

        for category in inventory.values():
            if isinstance(category, dict):
                for subcategory in category.values():
                    if isinstance(subcategory, list):
                        for item in subcategory:
                            if isinstance(item, dict) and 'model' in item:
                                models.append(item['model'])
                    elif isinstance(subcategory, dict):
                        # Handle nested dicts
                        for subsubcat in subcategory.values():
                            if isinstance(subsubcat, list):
                                for item in subsubcat:
                                    if isinstance(item, dict) and 'model' in item:
                                        models.append(item['model'])

        return models
