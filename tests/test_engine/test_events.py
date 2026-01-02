# tests/test_engine/test_events.py
import pytest
from unittest.mock import patch
from copy import deepcopy
from backend.engine.event_engine import EventEngine, EventCategory, EventSeverity


class TestProbabilityCalculation:
    """Test event probability calculations"""

    def test_base_probability(self, sample_country_data, sample_events_catalog):
        """Should use base probability with no triggers"""
        engine = EventEngine(sample_country_data, sample_events_catalog)

        # Get recession probability (debt and growth are fine in fixture)
        prob = engine._calculate_probability(sample_events_catalog['recession'])

        # Should be near base (0.05/12 = ~0.004)
        assert 0.001 < prob < 0.01

    def test_trigger_increases_probability(self, sample_country_data, sample_events_catalog):
        """Triggers should increase probability"""
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 90

        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])

        # Should be higher than base
        assert prob > 0.01

    def test_prevention_decreases_probability(self, sample_country_data, sample_events_catalog):
        """Prevention factors should decrease probability"""
        sample_country_data['economy']['reserves']['months_of_imports_covered'] = 15
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 30

        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])

        # Should be very low
        assert prob < 0.005

    def test_probability_clamped(self, sample_country_data, sample_events_catalog):
        """Probability should be clamped between 0 and 1"""
        # Set extreme values
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 200
        sample_country_data['economy']['inflation_rate'] = 50
        sample_country_data['economy']['gdp_growth_rate'] = -10

        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])

        assert 0 <= prob <= 1

    def test_probability_minimum_zero(self, sample_country_data, sample_events_catalog):
        """Probability should not go below zero"""
        # Set conditions that would give negative probability
        sample_country_data['economy']['reserves']['months_of_imports_covered'] = 100
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 10

        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])

        assert prob >= 0


class TestConditionEvaluation:
    """Test condition string evaluation"""

    def test_evaluate_greater_than(self, sample_country_data):
        """Should evaluate > conditions"""
        engine = EventEngine(sample_country_data)

        assert engine._evaluate_condition("happiness > 50") is True
        assert engine._evaluate_condition("happiness > 80") is False

    def test_evaluate_less_than(self, sample_country_data):
        """Should evaluate < conditions"""
        engine = EventEngine(sample_country_data)

        assert engine._evaluate_condition("happiness < 80") is True
        assert engine._evaluate_condition("happiness < 50") is False

    def test_evaluate_equality(self, sample_country_data):
        """Should evaluate == conditions"""
        engine = EventEngine(sample_country_data)

        assert engine._evaluate_condition("credit_rating == A") is True
        assert engine._evaluate_condition("credit_rating == AAA") is False

    def test_evaluate_invalid_condition(self, sample_country_data):
        """Should return False for invalid conditions"""
        engine = EventEngine(sample_country_data)

        assert engine._evaluate_condition("invalid") is False
        assert engine._evaluate_condition("too many parts here") is False


class TestEventEffects:
    """Test event effect application"""

    def test_apply_effects(self, sample_country_data, sample_events_catalog):
        """Effects should be applied to country data"""
        engine = EventEngine(sample_country_data, sample_events_catalog)

        event = {
            'effects': {
                'economy.gdp_growth_rate': -3.0,
                'indices.happiness': -10
            }
        }

        old_happiness = sample_country_data['indices']['happiness']
        engine.apply_event_effects(event)

        assert sample_country_data['indices']['happiness'] == old_happiness - 10

    def test_apply_nested_effects(self, sample_country_data, sample_events_catalog):
        """Should apply effects to nested paths"""
        engine = EventEngine(sample_country_data, sample_events_catalog)

        event = {
            'effects': {
                'economy.gdp_growth_rate': -2.0
            }
        }

        old_growth = sample_country_data['economy']['gdp_growth_rate']
        engine.apply_event_effects(event)

        assert sample_country_data['economy']['gdp_growth_rate'] == old_growth - 2.0

    def test_apply_creates_missing_keys(self, sample_country_data, sample_events_catalog):
        """Should create missing keys when applying effects"""
        engine = EventEngine(sample_country_data, sample_events_catalog)

        event = {
            'effects': {
                'indices.new_index': 50
            }
        }

        engine.apply_event_effects(event)

        assert sample_country_data['indices']['new_index'] == 50


class TestEventChecking:
    """Test event trigger checking"""

    def test_check_events_returns_list(self, sample_country_data, sample_events_catalog):
        """check_events should return a list"""
        engine = EventEngine(sample_country_data, sample_events_catalog)

        with patch('random.random', return_value=0.001):  # Force trigger
            events = engine.check_events()

        assert isinstance(events, list)

    def test_event_instance_structure(self, sample_country_data, sample_events_catalog):
        """Triggered events should have correct structure"""
        engine = EventEngine(sample_country_data, sample_events_catalog)

        with patch('random.random', return_value=0.0001):  # Force trigger
            events = engine.check_events()

        if events:
            event = events[0]
            assert 'id' in event
            assert 'event_type' in event
            assert 'name' in event
            assert 'effects' in event
            assert 'duration_months' in event


class TestEventResponses:
    """Test event response handling"""

    def test_respond_to_event(self, sample_country_data):
        """Should process event response"""
        # Add an active event
        sample_country_data['active_events'] = [{
            'id': 'test_event_2024_1',
            'event_type': 'civil_unrest',
            'name': 'Civil Unrest',
            'status': 'active',
            'responses': ['concessions', 'crackdown', 'dialogue', 'ignore']
        }]

        engine = EventEngine(sample_country_data)
        result = engine.respond_to_event('test_event_2024_1', 'dialogue')

        assert result['success'] is True
        assert result['response'] == 'dialogue'

    def test_invalid_response(self, sample_country_data):
        """Should reject invalid response"""
        sample_country_data['active_events'] = [{
            'id': 'test_event_2024_1',
            'event_type': 'civil_unrest',
            'status': 'active',
            'responses': ['concessions', 'crackdown']
        }]

        engine = EventEngine(sample_country_data)
        result = engine.respond_to_event('test_event_2024_1', 'invalid_response')

        assert result['success'] is False
        assert 'Invalid response' in result['error']

    def test_response_to_nonexistent_event(self, sample_country_data):
        """Should fail for nonexistent event"""
        sample_country_data['active_events'] = []

        engine = EventEngine(sample_country_data)
        result = engine.respond_to_event('nonexistent_event', 'any')

        assert result['success'] is False
        assert 'not found' in result['error']


class TestActiveEventProcessing:
    """Test active event management"""

    def test_process_active_events(self, sample_country_data):
        """Should decrement duration of active events"""
        sample_country_data['active_events'] = [{
            'id': 'test_event_2024_1',
            'status': 'active',
            'months_remaining': 3
        }]

        engine = EventEngine(sample_country_data)
        expired = engine.process_active_events()

        assert sample_country_data['active_events'][0]['months_remaining'] == 2
        assert len(expired) == 0

    def test_event_expires(self, sample_country_data):
        """Events should expire when duration reaches 0"""
        sample_country_data['active_events'] = [{
            'id': 'test_event_2024_1',
            'status': 'active',
            'months_remaining': 1
        }]

        engine = EventEngine(sample_country_data)
        expired = engine.process_active_events()

        assert len(expired) == 1
        assert expired[0]['id'] == 'test_event_2024_1'

    def test_get_active_events(self, sample_country_data):
        """Should return list of active events"""
        sample_country_data['active_events'] = [
            {'id': 'event1', 'name': 'Event 1', 'status': 'active', 'months_remaining': 3},
            {'id': 'event2', 'name': 'Event 2', 'status': 'active', 'months_remaining': 1}
        ]

        engine = EventEngine(sample_country_data)
        active = engine.get_active_events()

        assert len(active) == 2


class TestForceEvent:
    """Test forced event triggering"""

    def test_force_event(self, sample_country_data):
        """Should force trigger a specific event"""
        engine = EventEngine(sample_country_data)
        result = engine.force_event('recession')

        assert result['success'] is True
        assert result['event']['event_type'] == 'recession'
        assert len(sample_country_data['active_events']) == 1

    def test_force_unknown_event(self, sample_country_data):
        """Should fail for unknown event type"""
        engine = EventEngine(sample_country_data)
        result = engine.force_event('nonexistent_event')

        assert result['success'] is False
        assert 'Unknown event' in result['error']

    def test_force_event_applies_effects(self, sample_country_data):
        """Forced event should apply effects immediately"""
        old_happiness = sample_country_data['indices']['happiness']

        engine = EventEngine(sample_country_data)
        engine.force_event('civil_unrest')

        # Civil unrest has happiness -5 effect
        assert sample_country_data['indices']['happiness'] != old_happiness


class TestEventHistory:
    """Test event history tracking"""

    def test_get_event_history(self, sample_country_data):
        """Should return event history"""
        sample_country_data['event_history'] = [
            {'id': 'event1', 'name': 'Past Event 1'},
            {'id': 'event2', 'name': 'Past Event 2'}
        ]

        engine = EventEngine(sample_country_data)
        history = engine.get_event_history()

        assert len(history) == 2

    def test_get_event_history_with_limit(self, sample_country_data):
        """Should respect history limit"""
        sample_country_data['event_history'] = [
            {'id': f'event{i}'} for i in range(20)
        ]

        engine = EventEngine(sample_country_data)
        history = engine.get_event_history(limit=5)

        assert len(history) == 5

    def test_empty_event_history(self, sample_country_data):
        """Should handle empty history"""
        engine = EventEngine(sample_country_data)
        history = engine.get_event_history()

        assert history == []


class TestSpecialValueGetters:
    """Test special computed value accessors"""

    def test_get_debt_to_gdp(self, sample_country_data):
        """Should get debt to GDP ratio"""
        engine = EventEngine(sample_country_data)
        value = engine._get_value('debt_to_gdp')

        assert value == 50  # From fixture

    def test_get_unemployment(self, sample_country_data):
        """Should get unemployment rate"""
        engine = EventEngine(sample_country_data)
        value = engine._get_value('unemployment')

        assert value == 5.1  # From fixture

    def test_get_happiness(self, sample_country_data):
        """Should get happiness index"""
        engine = EventEngine(sample_country_data)
        value = engine._get_value('happiness')

        assert value == 65  # From fixture

    def test_get_nonexistent_value(self, sample_country_data):
        """Should return None for nonexistent paths"""
        engine = EventEngine(sample_country_data)
        value = engine._get_value('nonexistent.path.here')

        assert value is None


class TestRelationsCount:
    """Test relations counting helpers"""

    def test_count_hostile_relations(self, sample_country_data):
        """Should count hostile countries"""
        sample_country_data['relations']['ENM'] = {'score': -50}

        engine = EventEngine(sample_country_data)
        count = engine._count_hostile_relations()

        assert count == 1

    def test_count_good_relations(self, sample_country_data):
        """Should count friendly countries"""
        engine = EventEngine(sample_country_data)
        count = engine._count_good_relations()

        # USA has score 80 in fixture
        assert count == 1

    def test_count_alliances(self, sample_country_data):
        """Should count formal alliances"""
        sample_country_data['relations']['USA']['treaties'] = ['Mutual Defense Treaty']

        engine = EventEngine(sample_country_data)
        count = engine._count_alliances()

        assert count == 1
