"""
Event Engine - Phase 8

Generates and manages events based on KPI thresholds.
"""

import random
from typing import Dict, List, Optional
from enum import Enum


class EventCategory(Enum):
    """Categories of events."""
    ECONOMIC = "economic"
    MILITARY = "military"
    POLITICAL = "political"
    SOCIAL = "social"
    NATURAL = "natural"
    DIPLOMATIC = "diplomatic"


class EventSeverity(Enum):
    """Severity levels for events."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class EventEngine:
    """
    Manages event generation and processing.

    Events are triggered based on:
    - KPI thresholds (debt too high, unemployment too high, etc.)
    - Random chance with modifiers
    - Player actions
    - External factors
    """

    # Default event definitions (can be overridden by catalog)
    DEFAULT_EVENTS = {
        'economic_crisis': {
            'name': 'Economic Crisis',
            'category': EventCategory.ECONOMIC.value,
            'severity': EventSeverity.MAJOR.value,
            'base_probability_annual': 0.05,
            'triggers': {
                'debt_to_gdp > 90': {'add': 0.15},
                'deficit_to_gdp > 8': {'add': 0.10},
                'inflation > 15': {'add': 0.10}
            },
            'prevention': {
                'foreign_reserves > 12': {'subtract': 0.05},
                'credit_rating == AAA': {'subtract': 0.05}
            },
            'effects': {
                'economy.gdp_growth_rate': -2.0,
                'indices.happiness': -10,
                'indices.stability': -15
            },
            'duration_months': 12,
            'responses': ['austerity', 'stimulus', 'bailout', 'do_nothing']
        },
        'recession': {
            'name': 'Recession',
            'category': EventCategory.ECONOMIC.value,
            'severity': EventSeverity.MODERATE.value,
            'base_probability_annual': 0.08,
            'triggers': {
                'gdp_growth < 0': {'add': 0.20},
                'unemployment > 10': {'add': 0.10}
            },
            'effects': {
                'economy.gdp_growth_rate': -1.5,
                'workforce.unemployment_rate': 2.0,
                'indices.happiness': -5
            },
            'duration_months': 6
        },
        'military_tension': {
            'name': 'Military Tension',
            'category': EventCategory.MILITARY.value,
            'severity': EventSeverity.MODERATE.value,
            'base_probability_annual': 0.10,
            'triggers': {
                'military_readiness < 60': {'add': 0.10},
                'hostile_neighbors > 2': {'add': 0.15}
            },
            'prevention': {
                'military_readiness > 90': {'subtract': 0.08},
                'strong_alliances > 2': {'subtract': 0.05}
            },
            'effects': {
                'indices.stability': -10,
                'budget.defense_pressure': 5
            },
            'duration_months': 3,
            'responses': ['mobilize', 'preemptive_strike', 'defensive_posture', 'negotiate']
        },
        'civil_unrest': {
            'name': 'Civil Unrest',
            'category': EventCategory.SOCIAL.value,
            'severity': EventSeverity.MODERATE.value,
            'base_probability_annual': 0.06,
            'triggers': {
                'happiness < 40': {'add': 0.15},
                'unemployment > 15': {'add': 0.15},
                'inequality > 70': {'add': 0.10}
            },
            'prevention': {
                'happiness > 70': {'subtract': 0.04},
                'public_trust > 60': {'subtract': 0.03}
            },
            'effects': {
                'indices.stability': -15,
                'indices.happiness': -5,
                'economy.gdp_growth_rate': -0.5
            },
            'duration_months': 2,
            'responses': ['concessions', 'crackdown', 'dialogue', 'ignore']
        },
        'natural_disaster': {
            'name': 'Natural Disaster',
            'category': EventCategory.NATURAL.value,
            'severity': EventSeverity.MAJOR.value,
            'base_probability_annual': 0.03,
            'effects': {
                'infrastructure.damage': 10,
                'economy.gdp_billions_usd': -5,
                'demographics.casualties': 100,
                'indices.happiness': -8
            },
            'duration_months': 1
        },
        'diplomatic_incident': {
            'name': 'Diplomatic Incident',
            'category': EventCategory.DIPLOMATIC.value,
            'severity': EventSeverity.MINOR.value,
            'base_probability_annual': 0.12,
            'effects': {
                'relations.random_country': -10,
                'indices.international_standing': -5
            },
            'duration_months': 1
        },
        'tech_breakthrough': {
            'name': 'Technology Breakthrough',
            'category': EventCategory.ECONOMIC.value,
            'severity': EventSeverity.MINOR.value,
            'base_probability_annual': 0.04,
            'triggers': {
                'sector_technology > 80': {'add': 0.10},
                'research_spending > 3': {'add': 0.05}
            },
            'effects': {
                'sectors.technology.level': 3,
                'economy.gdp_growth_potential': 0.2,
                'indices.innovation': 5
            },
            'duration_months': 0  # Instant effect
        },
        'trade_deal_opportunity': {
            'name': 'Trade Deal Opportunity',
            'category': EventCategory.DIPLOMATIC.value,
            'severity': EventSeverity.MINOR.value,
            'base_probability_annual': 0.15,
            'triggers': {
                'good_relations > 3': {'add': 0.10}
            },
            'effects': {
                'economy.trade_potential': 2
            },
            'duration_months': 0,
            'requires_response': True
        }
    }

    def __init__(self, country_data: dict, event_catalog: Optional[dict] = None):
        self.data = country_data
        self.catalog = event_catalog or self.DEFAULT_EVENTS

    def check_events(self) -> List[Dict]:
        """
        Check for event triggers and return triggered events.

        Called during monthly tick.
        """
        triggered = []

        for event_id, event_def in self.catalog.items():
            probability = self._calculate_probability(event_def)

            if random.random() < probability:
                event_instance = self._create_event_instance(event_id, event_def)
                triggered.append(event_instance)

        return triggered

    def _calculate_probability(self, event_def: dict) -> float:
        """Calculate event probability based on current KPIs."""
        # Base annual probability converted to monthly
        base = event_def.get('base_probability_annual', 0.05) / 12

        # Add trigger modifiers
        for condition, modifier in event_def.get('triggers', {}).items():
            if self._evaluate_condition(condition):
                base += modifier.get('add', 0) / 12

        # Subtract prevention modifiers
        for condition, modifier in event_def.get('prevention', {}).items():
            if self._evaluate_condition(condition):
                base -= modifier.get('subtract', 0) / 12

        # Clamp to valid probability
        return max(0, min(1, base))

    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a condition string.

        Examples:
        - 'debt_to_gdp > 80'
        - 'happiness < 40'
        - 'credit_rating == AAA'
        """
        # Parse condition
        parts = condition.split()
        if len(parts) != 3:
            return False

        path, operator, value = parts

        # Get current value
        current = self._get_value(path)
        if current is None:
            return False

        # Handle string comparisons
        if value.replace('.', '').replace('-', '').isdigit():
            target = float(value)
        else:
            target = value
            current = str(current)

        # Evaluate
        if operator == '>':
            return current > target
        elif operator == '<':
            return current < target
        elif operator == '>=':
            return current >= target
        elif operator == '<=':
            return current <= target
        elif operator == '==':
            return current == target
        elif operator == '!=':
            return current != target

        return False

    def _get_value(self, path: str) -> Optional[float]:
        """Get value from data using path notation."""
        # Handle special computed values
        special_values = {
            'debt_to_gdp': lambda: self.data.get('economy', {}).get('debt', {}).get('debt_to_gdp_percent', 0),
            'deficit_to_gdp': lambda: self.data.get('budget', {}).get('deficit_to_gdp_percent', 0),
            'gdp_growth': lambda: self.data.get('economy', {}).get('gdp_growth_rate', 0),
            'inflation': lambda: self.data.get('economy', {}).get('inflation_rate', 0),
            'unemployment': lambda: self.data.get('workforce', {}).get('unemployment_rate', 0),
            'happiness': lambda: self.data.get('indices', {}).get('happiness', 50),
            'stability': lambda: self.data.get('indices', {}).get('stability', 50),
            'public_trust': lambda: self.data.get('indices', {}).get('public_trust', 50),
            'military_readiness': lambda: self.data.get('military', {}).get('readiness', {}).get('overall', 50),
            'foreign_reserves': lambda: self.data.get('economy', {}).get('reserves', {}).get('months_of_imports_covered', 6),
            'credit_rating': lambda: self.data.get('economy', {}).get('debt', {}).get('credit_rating', 'A'),
            'sector_technology': lambda: self.data.get('sectors', {}).get('technology', {}).get('level', 50),
            'hostile_neighbors': lambda: self._count_hostile_relations(),
            'good_relations': lambda: self._count_good_relations(),
            'strong_alliances': lambda: self._count_alliances(),
        }

        if path in special_values:
            return special_values[path]()

        # Try dot notation
        keys = path.replace('_', '.').split('.')
        current = self.data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        if isinstance(current, (int, float)):
            return float(current)
        return current

    def _count_hostile_relations(self) -> int:
        """Count countries with negative relations."""
        relations = self.data.get('relations', {})
        return sum(1 for r in relations.values() if r.get('score', 0) < -20)

    def _count_good_relations(self) -> int:
        """Count countries with positive relations."""
        relations = self.data.get('relations', {})
        return sum(1 for r in relations.values() if r.get('score', 0) > 50)

    def _count_alliances(self) -> int:
        """Count formal alliances."""
        relations = self.data.get('relations', {})
        count = 0
        for r in relations.values():
            treaties = r.get('treaties', [])
            if any('alliance' in t.lower() or 'defense' in t.lower() for t in treaties):
                count += 1
        return count

    def _create_event_instance(self, event_id: str, event_def: dict) -> Dict:
        """Create an active event instance."""
        current_date = self.data.get('meta', {}).get('current_date', {})

        return {
            'id': f"{event_id}_{current_date.get('year', 2024)}_{current_date.get('month', 1)}",
            'event_type': event_id,
            'name': event_def.get('name', event_id),
            'category': event_def.get('category', 'unknown'),
            'severity': event_def.get('severity', 'minor'),
            'effects': event_def.get('effects', {}),
            'duration_months': event_def.get('duration_months', 1),
            'months_remaining': event_def.get('duration_months', 1),
            'triggered_date': current_date.copy(),
            'responses': event_def.get('responses', []),
            'requires_response': event_def.get('requires_response', False),
            'response_given': None,
            'status': 'active'
        }

    def apply_event_effects(self, event: dict) -> None:
        """Apply event effects to country data."""
        for path, change in event.get('effects', {}).items():
            self._apply_change(path, change)

    def _apply_change(self, path: str, change: float) -> None:
        """Apply a change to a data path."""
        keys = path.split('.')
        current = self.data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        final_key = keys[-1]
        if final_key in current:
            if isinstance(current[final_key], (int, float)):
                current[final_key] += change
            else:
                current[final_key] = change
        else:
            current[final_key] = change

    def respond_to_event(self, event_id: str, response: str) -> Dict:
        """
        Apply player response to an event.

        Args:
            event_id: ID of the active event
            response: Response choice from event's responses list
        """
        active_events = self.data.get('active_events', [])

        for event in active_events:
            if event.get('id') == event_id:
                available_responses = event.get('responses', [])

                if response not in available_responses:
                    return {
                        'success': False,
                        'error': f'Invalid response: {response}',
                        'available': available_responses
                    }

                # Apply response effects
                effects = self._get_response_effects(event.get('event_type'), response)
                for path, change in effects.items():
                    self._apply_change(path, change)

                event['response_given'] = response
                event['status'] = 'responded'

                return {
                    'success': True,
                    'event': event.get('name'),
                    'response': response,
                    'effects_applied': effects
                }

        return {'success': False, 'error': f'Event not found: {event_id}'}

    def _get_response_effects(self, event_type: str, response: str) -> Dict:
        """Get effects for a specific response to an event."""
        response_effects = {
            'economic_crisis': {
                'austerity': {
                    'budget.total_expenditure_billions': -10,
                    'indices.happiness': -15,
                    'economy.debt.debt_to_gdp_percent': -5
                },
                'stimulus': {
                    'budget.deficit_billions': 20,
                    'economy.gdp_growth_rate': 1.0,
                    'indices.happiness': 5
                },
                'bailout': {
                    'economy.debt.total_billions': 30,
                    'indices.sovereignty': -10,
                    'economy.gdp_growth_rate': 0.5
                },
                'do_nothing': {
                    'indices.stability': -10,
                    'economy.gdp_growth_rate': -1.0
                }
            },
            'military_tension': {
                'mobilize': {
                    'military.readiness.overall': 20,
                    'economy.gdp_growth_rate': -0.5,
                    'indices.stability': 5
                },
                'preemptive_strike': {
                    'indices.international_standing': -20,
                    'indices.stability': -10
                },
                'defensive_posture': {
                    'military.readiness.overall': 10,
                    'indices.stability': 5
                },
                'negotiate': {
                    'indices.stability': 3,
                    'military.readiness.overall': -5
                }
            },
            'civil_unrest': {
                'concessions': {
                    'indices.happiness': 10,
                    'budget.total_expenditure_billions': 5,
                    'indices.precedent': 5
                },
                'crackdown': {
                    'indices.stability': 10,
                    'indices.happiness': -15,
                    'indices.international_standing': -10
                },
                'dialogue': {
                    'indices.happiness': 5,
                    'indices.public_trust': 5
                },
                'ignore': {
                    'indices.stability': -15
                }
            }
        }

        return response_effects.get(event_type, {}).get(response, {})

    def process_active_events(self) -> List[Dict]:
        """
        Process all active events (decrement duration, expire old events).

        Returns list of expired events.
        """
        expired = []
        active_events = self.data.get('active_events', [])

        for event in active_events:
            if event.get('status') != 'active':
                continue

            event['months_remaining'] = event.get('months_remaining', 1) - 1

            if event['months_remaining'] <= 0:
                event['status'] = 'expired'
                expired.append(event)

        # Remove expired events
        self.data['active_events'] = [
            e for e in active_events if e.get('status') == 'active'
        ]

        return expired

    def get_active_events(self) -> List[Dict]:
        """Get list of currently active events."""
        return [
            {
                'id': e.get('id'),
                'name': e.get('name'),
                'category': e.get('category'),
                'severity': e.get('severity'),
                'months_remaining': e.get('months_remaining'),
                'requires_response': e.get('requires_response') and not e.get('response_given'),
                'responses': e.get('responses', [])
            }
            for e in self.data.get('active_events', [])
            if e.get('status') == 'active'
        ]

    def get_event_history(self, limit: int = 10) -> List[Dict]:
        """Get recent event history."""
        history = self.data.get('event_history', [])
        return history[-limit:] if history else []

    def force_event(self, event_id: str) -> Dict:
        """
        Force trigger a specific event (for testing/scenarios).

        Args:
            event_id: Event type ID from catalog
        """
        if event_id not in self.catalog:
            return {
                'success': False,
                'error': f'Unknown event: {event_id}',
                'available': list(self.catalog.keys())
            }

        event_def = self.catalog[event_id]
        event_instance = self._create_event_instance(event_id, event_def)

        if 'active_events' not in self.data:
            self.data['active_events'] = []
        self.data['active_events'].append(event_instance)

        # Apply immediate effects
        self.apply_event_effects(event_instance)

        return {
            'success': True,
            'event': event_instance
        }
