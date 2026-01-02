"""
Tick Processor - Phase 1

Processes game ticks and coordinates updates across all game systems.
"""

from datetime import date
from typing import TYPE_CHECKING, Dict, List, Optional

from backend.engine.clock_service import clock_service, TickType

if TYPE_CHECKING:
    from backend.engine.economy_engine import EconomyEngine
    from backend.engine.demographics_engine import DemographicsEngine
    from backend.engine.sector_engine import SectorEngine
    from backend.engine.procurement_engine import ProcurementEngine
    from backend.engine.event_engine import EventEngine


class TickProcessor:
    """
    Coordinates tick updates across all game engines.

    Registers handlers with ClockService and delegates to appropriate engines.
    """

    def __init__(self, country_code: str, db_service):
        self.country_code = country_code
        self.db_service = db_service
        self._engines_initialized = False

        # Engine references (lazy loaded)
        self._economy_engine: Optional["EconomyEngine"] = None
        self._demographics_engine: Optional["DemographicsEngine"] = None
        self._sector_engine: Optional["SectorEngine"] = None
        self._procurement_engine: Optional["ProcurementEngine"] = None
        self._event_engine: Optional["EventEngine"] = None

        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register tick handlers with clock service."""
        clock_service.register_handler(TickType.DAILY, self.on_daily)
        clock_service.register_handler(TickType.WEEKLY, self.on_weekly)
        clock_service.register_handler(TickType.MONTHLY, self.on_monthly)
        clock_service.register_handler(TickType.QUARTERLY, self.on_quarterly)
        clock_service.register_handler(TickType.YEARLY, self.on_yearly)

    def _init_engines(self, data: dict) -> None:
        """Initialize engines with current country data."""
        from backend.engine.economy_engine import EconomyEngine
        from backend.engine.demographics_engine import DemographicsEngine
        from backend.engine.sector_engine import SectorEngine
        from backend.engine.procurement_engine import ProcurementEngine
        from backend.engine.event_engine import EventEngine

        self._economy_engine = EconomyEngine(data)
        self._demographics_engine = DemographicsEngine(data)
        self._sector_engine = SectorEngine(data)

        # Load catalogs for engines that need them
        weapons_catalog = self.db_service.load_weapons_catalog()
        events_catalog = self.db_service.load_events_catalog()

        self._procurement_engine = ProcurementEngine(data, weapons_catalog)
        self._event_engine = EventEngine(data, events_catalog)

        self._engines_initialized = True

    async def on_daily(self, game_date: date, day_count: int) -> None:
        """Daily updates - sync game date to data."""
        data = self.db_service.load_country(self.country_code)

        # Update meta with current date
        data['meta']['current_date'] = {
            'year': game_date.year,
            'month': game_date.month,
            'day': game_date.day
        }
        data['meta']['total_game_days_elapsed'] = day_count

        self.db_service.save_country(self.country_code, data)

    async def on_weekly(self, game_date: date, day_count: int) -> None:
        """Weekly updates - minor adjustments."""
        # Currently minimal - could add weekly events or minor stat adjustments
        pass

    async def on_monthly(self, game_date: date, day_count: int) -> None:
        """Monthly economic updates."""
        data = self.db_service.load_country(self.country_code)
        self._init_engines(data)

        # Process economic tick
        if self._economy_engine:
            changes = self._economy_engine.process_monthly_tick()
            data['meta']['last_economic_update'] = {
                'date': {'year': game_date.year, 'month': game_date.month, 'day': game_date.day},
                'changes': changes
            }

        # Check for events
        if self._event_engine:
            triggered_events = self._event_engine.check_events()
            if triggered_events:
                if 'active_events' not in data:
                    data['active_events'] = []
                data['active_events'].extend(triggered_events)

                # Apply event effects
                for event in triggered_events:
                    self._event_engine.apply_event_effects(event)

            # Process existing events (decrement duration)
            self._event_engine.process_active_events()

        self.db_service.save_country(self.country_code, data)

    async def on_quarterly(self, game_date: date, day_count: int) -> None:
        """Quarterly sector/project updates."""
        data = self.db_service.load_country(self.country_code)
        self._init_engines(data)

        # Process sector development projects
        if self._sector_engine:
            completed = self._sector_engine.process_quarterly_progress()
            if completed:
                if 'completed_projects' not in data:
                    data['completed_projects'] = []
                data['completed_projects'].extend(completed)

        self.db_service.save_country(self.country_code, data)

    async def on_yearly(self, game_date: date, day_count: int) -> None:
        """Yearly demographic/political updates."""
        data = self.db_service.load_country(self.country_code)
        self._init_engines(data)

        # Process demographics
        if self._demographics_engine:
            changes = self._demographics_engine.process_yearly_tick()
            data['meta']['last_demographic_update'] = {
                'date': {'year': game_date.year, 'month': game_date.month, 'day': game_date.day},
                'changes': changes
            }

        # Process weapon deliveries
        if self._procurement_engine:
            deliveries = self._procurement_engine.process_deliveries(game_date.year)
            if deliveries:
                if 'recent_deliveries' not in data:
                    data['recent_deliveries'] = []
                data['recent_deliveries'] = deliveries  # Keep only most recent

        self.db_service.save_country(self.country_code, data)

    def get_status(self) -> Dict:
        """Get tick processor status."""
        return {
            "country_code": self.country_code,
            "engines_initialized": self._engines_initialized,
            "clock_state": clock_service.get_state()
        }


# Store active processors by country
_processors: Dict[str, TickProcessor] = {}


def get_processor(country_code: str, db_service) -> TickProcessor:
    """Get or create a tick processor for a country."""
    if country_code not in _processors:
        _processors[country_code] = TickProcessor(country_code, db_service)
    return _processors[country_code]


def remove_processor(country_code: str) -> None:
    """Remove a tick processor."""
    if country_code in _processors:
        del _processors[country_code]
