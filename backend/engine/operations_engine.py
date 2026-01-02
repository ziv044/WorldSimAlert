"""
Operations Engine - Phase 7

Allows player to conduct military operations.
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class OperationType(Enum):
    """Types of military operations."""
    AIR_STRIKE = "air_strike"
    AIR_INTERCEPT = "air_intercept"
    GROUND_ASSAULT = "ground_assault"
    GROUND_DEFENSE = "ground_defense"
    NAVAL_PATROL = "naval_patrol"
    NAVAL_BLOCKADE = "naval_blockade"
    CYBER_ATTACK = "cyber_attack"
    SPECIAL_OPS = "special_ops"
    RECONNAISSANCE = "reconnaissance"


@dataclass
class OperationResult:
    """Result of a military operation."""
    success: bool
    operation_type: OperationType
    objective_achieved: bool
    friendly_losses: Dict[str, int]
    enemy_losses: Dict[str, int]
    munitions_used: Dict[str, int]
    political_cost: int
    relations_impact: Dict[str, int]
    message: str

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "operation_type": self.operation_type.value,
            "objective_achieved": self.objective_achieved,
            "friendly_losses": self.friendly_losses,
            "enemy_losses": self.enemy_losses,
            "munitions_used": self.munitions_used,
            "political_cost": self.political_cost,
            "relations_impact": self.relations_impact,
            "message": self.message
        }


class OperationsEngine:
    """
    Manages military operations.

    Operation types:
    - Air strike: Attack ground targets
    - Air intercept: Defend against air threats
    - Ground assault: Capture territory
    - Ground defense: Hold territory
    - Naval patrol: Maritime security
    - Naval blockade: Restrict enemy trade
    - Cyber attack: Disrupt enemy systems
    - Special ops: High-risk targeted missions
    - Reconnaissance: Gather intelligence
    """

    # Operation definitions
    OPERATIONS = {
        OperationType.AIR_STRIKE: {
            'required_assets': {'fighters': 4, 'munitions': 8},
            'base_success_rate': 0.75,
            'base_loss_rate': 0.05,
            'political_cost': 10,
            'relations_penalty': -15,
            'munition_types': ['bombs', 'missiles']
        },
        OperationType.AIR_INTERCEPT: {
            'required_assets': {'fighters': 2, 'air_defense': 1},
            'base_success_rate': 0.80,
            'base_loss_rate': 0.02,
            'political_cost': 2,
            'relations_penalty': -5,
            'munition_types': ['interceptors']
        },
        OperationType.GROUND_ASSAULT: {
            'required_assets': {'tanks': 10, 'infantry': 500, 'artillery': 5},
            'base_success_rate': 0.60,
            'base_loss_rate': 0.15,
            'political_cost': 20,
            'relations_penalty': -25,
            'munition_types': ['shells', 'fuel']
        },
        OperationType.GROUND_DEFENSE: {
            'required_assets': {'infantry': 200, 'artillery': 3},
            'base_success_rate': 0.85,
            'base_loss_rate': 0.08,
            'political_cost': 5,
            'relations_penalty': 0,
            'munition_types': ['shells']
        },
        OperationType.NAVAL_PATROL: {
            'required_assets': {'ships': 2},
            'base_success_rate': 0.95,
            'base_loss_rate': 0.01,
            'political_cost': 1,
            'relations_penalty': 0,
            'munition_types': ['fuel']
        },
        OperationType.NAVAL_BLOCKADE: {
            'required_assets': {'ships': 5, 'submarines': 1},
            'base_success_rate': 0.70,
            'base_loss_rate': 0.03,
            'political_cost': 15,
            'relations_penalty': -20,
            'munition_types': ['fuel', 'torpedoes']
        },
        OperationType.CYBER_ATTACK: {
            'required_assets': {'cyber_units': 1},
            'base_success_rate': 0.65,
            'base_loss_rate': 0.0,  # No physical losses
            'political_cost': 5,
            'relations_penalty': -10,
            'munition_types': []
        },
        OperationType.SPECIAL_OPS: {
            'required_assets': {'special_forces': 20},
            'base_success_rate': 0.55,
            'base_loss_rate': 0.10,
            'political_cost': 8,
            'relations_penalty': -12,
            'munition_types': ['small_arms']
        },
        OperationType.RECONNAISSANCE: {
            'required_assets': {'uavs': 2},
            'base_success_rate': 0.90,
            'base_loss_rate': 0.05,
            'political_cost': 2,
            'relations_penalty': -3,
            'munition_types': []
        }
    }

    def __init__(self, country_data: dict):
        self.data = country_data

    def plan_operation(
        self,
        operation_type: str,
        target_country: str,
        target_description: str,
        assets_committed: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        Plan an operation and get estimated outcomes.

        Does not execute the operation.
        """
        try:
            op_type = OperationType(operation_type)
        except ValueError:
            return {
                'valid': False,
                'error': f'Unknown operation type: {operation_type}',
                'available_types': [t.value for t in OperationType]
            }

        op_def = self.OPERATIONS[op_type]

        # Check if assets are available
        asset_check = self._check_assets(op_def['required_assets'], assets_committed)
        if not asset_check['sufficient']:
            return {
                'valid': False,
                'error': 'Insufficient assets',
                'missing': asset_check['missing'],
                'required': op_def['required_assets']
            }

        # Check relations (can't attack allies easily)
        relations = self.data.get('relations', {})
        target_relations = relations.get(target_country, {}).get('score', 0)

        if target_relations > 50 and op_def['relations_penalty'] < -10:
            return {
                'valid': False,
                'error': f'Cannot conduct offensive operations against ally ({target_country}: {target_relations})',
                'suggestion': 'Relations must be below 50 for major offensive operations'
            }

        # Calculate success probability
        readiness = self.data.get('military', {}).get('readiness', {})
        overall_readiness = readiness.get('overall', 80) / 100

        success_rate = op_def['base_success_rate'] * overall_readiness

        # Estimate losses
        loss_rate = op_def['base_loss_rate']
        if overall_readiness < 0.7:
            loss_rate *= 1.5  # Higher losses if low readiness

        return {
            'valid': True,
            'operation_type': operation_type,
            'target': target_country,
            'target_description': target_description,
            'estimated_success_rate': round(success_rate * 100, 1),
            'estimated_loss_rate': round(loss_rate * 100, 1),
            'political_cost': op_def['political_cost'],
            'relations_impact': op_def['relations_penalty'],
            'assets_required': op_def['required_assets'],
            'assets_committed': assets_committed or op_def['required_assets'],
            'munitions_required': op_def['munition_types'],
            'warning': 'This operation may have significant diplomatic consequences' if op_def['relations_penalty'] < -10 else None
        }

    def execute_operation(
        self,
        operation_type: str,
        target_country: str,
        target_description: str,
        assets_committed: Optional[Dict[str, int]] = None
    ) -> OperationResult:
        """
        Execute a military operation.

        Args:
            operation_type: Type of operation
            target_country: Target country code
            target_description: Description of target
            assets_committed: Assets to use (defaults to minimum required)

        Returns:
            OperationResult with outcomes
        """
        try:
            op_type = OperationType(operation_type)
        except ValueError:
            return OperationResult(
                success=False,
                operation_type=OperationType.RECONNAISSANCE,
                objective_achieved=False,
                friendly_losses={},
                enemy_losses={},
                munitions_used={},
                political_cost=0,
                relations_impact={},
                message=f"Unknown operation type: {operation_type}"
            )

        op_def = self.OPERATIONS[op_type]

        # Check assets
        assets_to_use = assets_committed or op_def['required_assets']
        asset_check = self._check_assets(op_def['required_assets'], assets_to_use)

        if not asset_check['sufficient']:
            return OperationResult(
                success=False,
                operation_type=op_type,
                objective_achieved=False,
                friendly_losses={},
                enemy_losses={},
                munitions_used={},
                political_cost=0,
                relations_impact={},
                message=f"Insufficient assets: {asset_check['missing']}"
            )

        # Calculate success
        readiness = self.data.get('military', {}).get('readiness', {})
        overall_readiness = readiness.get('overall', 80) / 100

        # More assets = better chance
        asset_bonus = sum(assets_to_use.values()) / max(1, sum(op_def['required_assets'].values()))
        asset_bonus = min(1.2, max(1.0, asset_bonus))

        success_rate = op_def['base_success_rate'] * overall_readiness * asset_bonus
        roll = random.random()
        objective_achieved = roll < success_rate

        # Calculate losses
        loss_rate = op_def['base_loss_rate']
        if not objective_achieved:
            loss_rate *= 1.5  # Higher losses on failure

        if overall_readiness < 0.7:
            loss_rate *= 1.3

        friendly_losses = {}
        for asset_type, count in assets_to_use.items():
            losses = int(count * loss_rate * (0.5 + random.random()))
            if losses > 0:
                friendly_losses[asset_type] = losses

        # Enemy losses (estimated)
        enemy_losses = {}
        if objective_achieved:
            enemy_losses = {
                'personnel': random.randint(10, 100),
                'equipment': random.randint(1, 10)
            }

        # Munitions used
        munitions_used = {}
        for munition in op_def['munition_types']:
            munitions_used[munition] = random.randint(5, 20)

        # Political and relations impact
        political_cost = op_def['political_cost']
        if not objective_achieved:
            political_cost *= 2

        relations_impact = {target_country: op_def['relations_penalty']}

        # Apply effects
        self._apply_losses(friendly_losses)
        self._apply_political_cost(political_cost)
        self._apply_relations_impact(relations_impact)
        self._consume_munitions(munitions_used)

        # Build message
        if objective_achieved:
            message = f"Operation successful! Target '{target_description}' achieved."
        else:
            message = f"Operation failed. Target '{target_description}' not achieved."

        if friendly_losses:
            message += f" Friendly losses: {friendly_losses}"

        return OperationResult(
            success=True,
            operation_type=op_type,
            objective_achieved=objective_achieved,
            friendly_losses=friendly_losses,
            enemy_losses=enemy_losses,
            munitions_used=munitions_used,
            political_cost=political_cost,
            relations_impact=relations_impact,
            message=message
        )

    def _check_assets(
        self,
        required: Dict[str, int],
        committed: Optional[Dict[str, int]]
    ) -> Dict:
        """Check if required assets are available."""
        inventory = self.data.get('military_inventory', {})
        personnel = self.data.get('military', {}).get('personnel', {})

        to_check = committed or required
        missing = {}

        for asset_type, count in to_check.items():
            available = self._get_asset_count(asset_type, inventory, personnel)
            if available < count:
                missing[asset_type] = count - available

        return {
            'sufficient': len(missing) == 0,
            'missing': missing
        }

    def _get_asset_count(
        self,
        asset_type: str,
        inventory: Dict,
        personnel: Dict
    ) -> int:
        """Get count of a specific asset type."""
        # Personnel-based assets
        if asset_type == 'infantry':
            return personnel.get('active_duty', 0)
        if asset_type == 'special_forces':
            return personnel.get('special_forces', 1000)

        # Equipment-based assets
        asset_mapping = {
            'fighters': ('aircraft', 'fighters'),
            'tanks': ('ground', 'tanks'),
            'artillery': ('ground', 'artillery'),
            'ships': ('naval', 'surface'),
            'submarines': ('naval', 'submarines'),
            'uavs': ('aircraft', 'uavs'),
            'air_defense': ('air_defense', 'missile_systems'),
            'cyber_units': ('cyber', 'units')
        }

        if asset_type in asset_mapping:
            category, subcategory = asset_mapping[asset_type]
            items = inventory.get(category, {}).get(subcategory, [])
            return sum(item.get('quantity', 0) for item in items if isinstance(item, dict))

        return 0

    def _apply_losses(self, losses: Dict[str, int]) -> None:
        """Apply equipment/personnel losses."""
        inventory = self.data.get('military_inventory', {})
        personnel = self.data.get('military', {}).get('personnel', {})

        for asset_type, count in losses.items():
            if asset_type == 'infantry':
                personnel['active_duty'] = max(0, personnel.get('active_duty', 0) - count)
            elif asset_type == 'special_forces':
                personnel['special_forces'] = max(0, personnel.get('special_forces', 0) - count)
            else:
                # Find and reduce equipment
                self._reduce_equipment(inventory, asset_type, count)

    def _reduce_equipment(self, inventory: Dict, asset_type: str, count: int) -> None:
        """Reduce equipment count in inventory."""
        asset_mapping = {
            'fighters': ('aircraft', 'fighters'),
            'tanks': ('ground', 'tanks'),
            'ships': ('naval', 'surface'),
            'uavs': ('aircraft', 'uavs')
        }

        if asset_type in asset_mapping:
            category, subcategory = asset_mapping[asset_type]
            items = inventory.get(category, {}).get(subcategory, [])

            remaining = count
            for item in items:
                if remaining <= 0:
                    break
                qty = item.get('quantity', 0)
                reduction = min(qty, remaining)
                item['quantity'] = qty - reduction
                remaining -= reduction

    def _apply_political_cost(self, cost: int) -> None:
        """Apply political cost to indices."""
        indices = self.data.get('indices', {})
        indices['political_capital'] = max(0, indices.get('political_capital', 50) - cost)
        indices['public_trust'] = max(0, indices.get('public_trust', 60) - cost * 0.5)

    def _apply_relations_impact(self, impact: Dict[str, int]) -> None:
        """Apply relations changes."""
        relations = self.data.get('relations', {})

        for country, change in impact.items():
            if country in relations:
                current = relations[country].get('score', 0)
                relations[country]['score'] = max(-100, min(100, current + change))

    def _consume_munitions(self, munitions: Dict[str, int]) -> None:
        """Consume munitions from stockpile."""
        # For now, just track usage - munitions system could be expanded
        stockpile = self.data.get('munitions_stockpile', {})
        for munition, count in munitions.items():
            stockpile[munition] = max(0, stockpile.get(munition, 1000) - count)
        self.data['munitions_stockpile'] = stockpile

    def set_readiness_level(self, level: str) -> Dict:
        """
        Set overall military readiness level.

        Args:
            level: 'low', 'normal', 'high', 'maximum'
        """
        readiness_levels = {
            'low': {'value': 50, 'cost_multiplier': 0.7, 'response_time': 'days'},
            'normal': {'value': 75, 'cost_multiplier': 1.0, 'response_time': 'hours'},
            'high': {'value': 90, 'cost_multiplier': 1.5, 'response_time': 'minutes'},
            'maximum': {'value': 100, 'cost_multiplier': 2.0, 'response_time': 'immediate'}
        }

        if level not in readiness_levels:
            return {
                'success': False,
                'error': f'Unknown level: {level}',
                'available': list(readiness_levels.keys())
            }

        config = readiness_levels[level]
        readiness = self.data.get('military', {}).get('readiness', {})
        old_level = readiness.get('overall', 75)

        readiness['overall'] = config['value']
        readiness['response_time'] = config['response_time']

        # Adjust military budget for maintenance
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})
        defense = allocation.get('defense', {})
        if 'breakdown' in defense:
            base_maintenance = defense['breakdown'].get('maintenance_base', 5)
            defense['breakdown']['maintenance'] = base_maintenance * config['cost_multiplier']

        return {
            'success': True,
            'old_level': old_level,
            'new_level': config['value'],
            'cost_multiplier': config['cost_multiplier'],
            'response_time': config['response_time']
        }

    def get_military_summary(self) -> Dict:
        """Get summary of military capabilities."""
        military = self.data.get('military', {})
        inventory = self.data.get('military_inventory', {})
        personnel = military.get('personnel', {})
        readiness = military.get('readiness', {})

        return {
            'personnel': {
                'active_duty': personnel.get('active_duty', 0),
                'reserves': personnel.get('reserves', 0),
                'conscription': personnel.get('conscription_based', False)
            },
            'readiness': {
                'overall': readiness.get('overall', 0),
                'ground': readiness.get('ground_forces', 0),
                'air': readiness.get('air_force', 0),
                'naval': readiness.get('navy', 0)
            },
            'equipment_summary': self._summarize_equipment(inventory),
            'available_operations': [op.value for op in OperationType]
        }

    def _summarize_equipment(self, inventory: Dict) -> Dict:
        """Get summary of equipment counts."""
        summary = {}

        for category, subcategories in inventory.items():
            if not isinstance(subcategories, dict):
                continue
            category_total = 0
            for items in subcategories.values():
                if isinstance(items, list):
                    category_total += sum(
                        item.get('quantity', 0) for item in items
                        if isinstance(item, dict)
                    )
            summary[category] = category_total

        return summary
