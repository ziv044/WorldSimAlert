"""
Procurement Engine - Phase 6

Allows player to purchase weapons and military equipment.
"""

from typing import Dict, List, Optional
from backend.engine.constraint_engine import ConstraintEngine


class ProcurementEngine:
    """
    Manages military procurement.

    Player actions:
    - Browse weapons catalog
    - Purchase weapons (with validation)
    - Track delivery schedules
    - Sell weapons
    """

    def __init__(self, country_data: dict, weapons_catalog: dict):
        self.data = country_data
        self.catalog = weapons_catalog
        self.constraint_engine = ConstraintEngine(country_data)

    def get_catalog(self, category: Optional[str] = None) -> Dict:
        """
        Get available weapons catalog.

        Args:
            category: Optional filter by category (aircraft, ground, naval, etc.)
        """
        if category:
            return {
                k: v for k, v in self.catalog.items()
                if v.get('category') == category
            }
        return self.catalog

    def check_purchase_eligibility(self, weapon_id: str, quantity: int) -> Dict:
        """
        Check if a weapon can be purchased without actually purchasing.

        Returns detailed eligibility info.
        """
        if weapon_id not in self.catalog:
            return {
                'eligible': False,
                'error': f'Unknown weapon: {weapon_id}'
            }

        weapon = self.catalog[weapon_id]
        total_cost = weapon.get('unit_cost_millions', 0) * quantity / 1000

        # Build constraints
        constraints = self._build_purchase_constraints(weapon, total_cost)

        # Check all constraints
        can_purchase, results = self.constraint_engine.check_all(constraints)

        # Check allowed buyers
        country_code = self.data.get('meta', {}).get('country_code', 'UNK')
        allowed_buyers = weapon.get('allowed_buyers', [])
        buyer_allowed = not allowed_buyers or country_code in allowed_buyers

        return {
            'eligible': can_purchase and buyer_allowed,
            'weapon': {
                'id': weapon_id,
                'name': weapon.get('name'),
                'category': weapon.get('category'),
                'unit_cost': weapon.get('unit_cost_millions'),
                'total_cost': total_cost
            },
            'quantity': quantity,
            'constraints': [r.to_dict() for r in results],
            'buyer_allowed': buyer_allowed,
            'manufacturer': weapon.get('manufacturer_country')
        }

    def request_purchase(
        self,
        weapon_id: str,
        quantity: int
    ) -> Dict:
        """
        Request to purchase a weapon system.

        Args:
            weapon_id: ID from weapons catalog
            quantity: Number to purchase

        Returns:
            Dict with order details or error
        """
        if weapon_id not in self.catalog:
            return {'success': False, 'error': f'Unknown weapon: {weapon_id}'}

        weapon = self.catalog[weapon_id]
        total_cost = weapon.get('unit_cost_millions', 0) * quantity / 1000

        # Build constraints from weapon definition
        constraints = self._build_purchase_constraints(weapon, total_cost)

        # Check all constraints
        can_purchase, results = self.constraint_engine.check_all(constraints)

        if not can_purchase:
            failed = [r for r in results if not r.satisfied]
            return {
                'success': False,
                'error': 'Cannot purchase - constraints not met',
                'failed_constraints': [r.to_dict() for r in failed]
            }

        # Check if allowed buyer
        country_code = self.data.get('meta', {}).get('country_code', 'UNK')
        allowed_buyers = weapon.get('allowed_buyers', [])
        if allowed_buyers and country_code not in allowed_buyers:
            return {
                'success': False,
                'error': f'{country_code} is not an approved buyer for {weapon["name"]}'
            }

        # Calculate delivery schedule
        delivery_time = weapon.get('delivery_time_years', '2-4')
        if isinstance(delivery_time, str) and '-' in delivery_time:
            min_years, max_years = map(int, delivery_time.split('-'))
        else:
            min_years = max_years = int(delivery_time) if delivery_time else 2

        avg_years = (min_years + max_years) // 2
        current_date = self.data.get('meta', {}).get('current_date', {})
        current_year = current_date.get('year', 2024)

        # Create procurement order
        order = {
            'id': f"order_{weapon_id}_{current_year}_{current_date.get('month', 1)}",
            'type': 'weapon_procurement',
            'weapon_id': weapon_id,
            'weapon_model': weapon.get('name'),
            'weapon_type': weapon.get('type'),
            'category': weapon.get('category'),
            'subcategory': weapon.get('subcategory', 'other'),
            'quantity': quantity,
            'total_cost_billions': total_cost,
            'source_country': weapon.get('manufacturer_country'),
            'start_date': current_date.copy(),
            'delivery_start_year': current_year + min_years,
            'delivery_end_year': current_year + max_years,
            'delivery_per_year': max(1, quantity // max(1, avg_years)),
            'delivered': 0,
            'status': 'ordered'
        }

        # Deduct from procurement budget
        self._deduct_procurement_budget(total_cost)

        # Add to active projects
        if 'active_projects' not in self.data:
            self.data['active_projects'] = []
        self.data['active_projects'].append(order)

        return {
            'success': True,
            'order': order
        }

    def _build_purchase_constraints(self, weapon: dict, total_cost: float) -> Dict:
        """Build constraints dict for a weapon purchase."""
        constraints = {
            'budget': {
                'amount_billions': total_cost,
                'budget_category': 'procurement'
            }
        }

        # Add relation constraints
        manufacturer = weapon.get('manufacturer_country')
        if manufacturer:
            prereqs = weapon.get('prerequisites_for_buyer', {})
            min_relations = prereqs.get('min_relations', 50)
            constraints['relations'] = {manufacturer: min_relations}

        # Add exclusion constraints
        prereqs = weapon.get('prerequisites_for_buyer', {})
        if 'not_operating' in prereqs:
            constraints['exclusion'] = prereqs['not_operating']

        return constraints

    def process_deliveries(self, current_year: int) -> List[Dict]:
        """
        Process weapon deliveries for current year.

        Called during yearly tick.
        """
        delivered = []
        projects = self.data.get('active_projects', [])

        for project in projects:
            if project.get('type') != 'weapon_procurement':
                continue

            if project.get('status') != 'ordered':
                continue

            if current_year >= project.get('delivery_start_year', 9999):
                # Deliver batch for this year
                to_deliver = min(
                    project.get('delivery_per_year', 1),
                    project.get('quantity', 0) - project.get('delivered', 0)
                )

                if to_deliver > 0:
                    # Add to inventory
                    self._add_to_inventory(
                        project['weapon_id'],
                        to_deliver,
                        project.get('source_country', 'UNK')
                    )
                    project['delivered'] = project.get('delivered', 0) + to_deliver

                    delivered.append({
                        'weapon': project.get('weapon_model'),
                        'quantity': to_deliver,
                        'remaining': project.get('quantity', 0) - project['delivered']
                    })

                # Check if order complete
                if project['delivered'] >= project.get('quantity', 0):
                    project['status'] = 'completed'

        # Clean up completed orders
        self.data['active_projects'] = [
            p for p in projects
            if not (p.get('type') == 'weapon_procurement' and p.get('status') == 'completed')
        ]

        return delivered

    def _add_to_inventory(self, weapon_id: str, quantity: int, source: str) -> None:
        """Add delivered weapons to military inventory."""
        if weapon_id not in self.catalog:
            return

        weapon = self.catalog[weapon_id]
        inventory = self.data.get('military_inventory', {})

        category = weapon.get('category', 'other')
        subcategory = weapon.get('subcategory', 'other')

        # Ensure category structure exists
        if category not in inventory:
            inventory[category] = {}
        if subcategory not in inventory[category]:
            inventory[category][subcategory] = []

        # Check if already have this model
        existing = None
        for item in inventory[category][subcategory]:
            if item.get('model') == weapon.get('name'):
                existing = item
                break

        if existing:
            existing['quantity'] = existing.get('quantity', 0) + quantity
            # Update average age (new equipment is age 0)
            old_qty = existing.get('quantity', 0) - quantity
            old_age = existing.get('avg_age_years', 0)
            if old_qty > 0:
                existing['avg_age_years'] = (old_age * old_qty) / existing['quantity']
        else:
            # Add new entry
            inventory[category][subcategory].append({
                'model': weapon.get('name'),
                'type': weapon.get('type'),
                'quantity': quantity,
                'source_country': source,
                'unit_cost_millions': weapon.get('unit_cost_millions'),
                'readiness_percent': 100,
                'avg_age_years': 0
            })

    def _deduct_procurement_budget(self, amount: float) -> None:
        """Deduct from procurement budget."""
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})
        defense = allocation.get('defense', {})

        if 'breakdown' in defense and 'procurement' in defense['breakdown']:
            defense['breakdown']['procurement'] = max(
                0,
                defense['breakdown'].get('procurement', 0) - amount
            )

    def sell_weapons(
        self,
        weapon_model: str,
        quantity: int,
        buyer_country: str
    ) -> Dict:
        """
        Sell weapons from inventory.

        Args:
            weapon_model: Name of weapon to sell
            quantity: Number to sell
            buyer_country: Country buying the weapons

        Returns:
            Dict with sale details or error
        """
        inventory = self.data.get('military_inventory', {})

        # Find the weapon in inventory
        found_item = None
        found_category = None
        found_subcategory = None

        for cat_name, category in inventory.items():
            if not isinstance(category, dict):
                continue
            for subcat_name, items in category.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if item.get('model') == weapon_model:
                        found_item = item
                        found_category = cat_name
                        found_subcategory = subcat_name
                        break

        if not found_item:
            return {'success': False, 'error': f'Weapon not found in inventory: {weapon_model}'}

        current_qty = found_item.get('quantity', 0)
        if current_qty < quantity:
            return {
                'success': False,
                'error': f'Not enough {weapon_model}: have {current_qty}, want to sell {quantity}'
            }

        # Calculate sale price (typically 60-80% of unit cost)
        unit_cost = found_item.get('unit_cost_millions', 50)
        sale_price = unit_cost * 0.7 * quantity / 1000  # In billions

        # Check relations with buyer
        relations = self.data.get('relations', {})
        buyer_relations = relations.get(buyer_country, {}).get('score', 0)

        if buyer_relations < 0:
            return {
                'success': False,
                'error': f'Cannot sell to hostile nation ({buyer_country}: {buyer_relations})'
            }

        # Execute sale
        found_item['quantity'] -= quantity
        if found_item['quantity'] <= 0:
            # Remove from inventory
            inventory[found_category][found_subcategory] = [
                i for i in inventory[found_category][found_subcategory]
                if i.get('model') != weapon_model
            ]

        # Add revenue
        budget = self.data.get('budget', {})
        budget['total_revenue_billions'] = budget.get('total_revenue_billions', 100) + sale_price

        # Improve relations
        if buyer_country in relations:
            relations[buyer_country]['score'] = min(100, buyer_relations + 3)

        return {
            'success': True,
            'weapon': weapon_model,
            'quantity': quantity,
            'revenue_billions': sale_price,
            'buyer': buyer_country,
            'relations_change': 3
        }

    def get_active_orders(self) -> List[Dict]:
        """Get all active procurement orders."""
        return [
            {
                'id': p.get('id'),
                'weapon': p.get('weapon_model'),
                'quantity': p.get('quantity'),
                'delivered': p.get('delivered', 0),
                'remaining': p.get('quantity', 0) - p.get('delivered', 0),
                'cost': p.get('total_cost_billions'),
                'source': p.get('source_country'),
                'delivery_start': p.get('delivery_start_year'),
                'delivery_end': p.get('delivery_end_year'),
                'status': p.get('status')
            }
            for p in self.data.get('active_projects', [])
            if p.get('type') == 'weapon_procurement'
        ]

    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel a procurement order.

        Partial refund based on progress.
        """
        projects = self.data.get('active_projects', [])

        for project in projects:
            if project.get('id') == order_id and project.get('type') == 'weapon_procurement':
                if project.get('status') != 'ordered':
                    return {'success': False, 'error': f'Order already {project.get("status")}'}

                # Calculate refund (50% minus delivered value)
                total_cost = project.get('total_cost_billions', 0)
                delivered_ratio = project.get('delivered', 0) / max(1, project.get('quantity', 1))
                refund = total_cost * 0.5 * (1 - delivered_ratio)

                # Apply refund
                budget = self.data.get('budget', {})
                allocation = budget.get('allocation', {})
                defense = allocation.get('defense', {})
                if 'breakdown' in defense:
                    defense['breakdown']['procurement'] = (
                        defense['breakdown'].get('procurement', 0) + refund
                    )

                # Damage relations with manufacturer
                source = project.get('source_country')
                if source:
                    relations = self.data.get('relations', {})
                    if source in relations:
                        relations[source]['score'] = max(-100,
                            relations[source].get('score', 0) - 5
                        )

                project['status'] = 'cancelled'
                self.data['active_projects'] = [
                    p for p in projects if p.get('id') != order_id
                ]

                return {
                    'success': True,
                    'refund': refund,
                    'relations_damage': -5,
                    'cancelled_order': project
                }

        return {'success': False, 'error': f'Order not found: {order_id}'}
