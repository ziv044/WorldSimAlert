"""
World Sim Game Engine

This module contains all game engine components for the World Sim simulation.

Phases:
1. Clock & Tick System - Time progression
2. Constraint Engine - Action validation
3. Economy Engine - Economic simulation
4. Budget Engine - Government finances
5. Sector Engine - Economic sector development
6. Procurement Engine - Military purchases
7. Operations Engine - Military operations
8. Event Engine - Random events and crises
"""

from backend.engine.clock_service import (
    ClockService,
    TickType,
    clock_service
)

from backend.engine.tick_processor import (
    TickProcessor,
    get_processor,
    remove_processor
)

from backend.engine.constraint_engine import (
    ConstraintEngine,
    ConstraintType,
    ConstraintResult
)

from backend.engine.economy_engine import EconomyEngine

from backend.engine.demographics_engine import DemographicsEngine

from backend.engine.budget_engine import BudgetEngine

from backend.engine.sector_engine import SectorEngine

from backend.engine.procurement_engine import ProcurementEngine

from backend.engine.operations_engine import (
    OperationsEngine,
    OperationType,
    OperationResult
)

from backend.engine.event_engine import (
    EventEngine,
    EventCategory,
    EventSeverity
)


__all__ = [
    # Clock & Tick
    'ClockService',
    'TickType',
    'clock_service',
    'TickProcessor',
    'get_processor',
    'remove_processor',

    # Constraint Engine
    'ConstraintEngine',
    'ConstraintType',
    'ConstraintResult',

    # Economy
    'EconomyEngine',
    'DemographicsEngine',

    # Budget
    'BudgetEngine',

    # Sectors
    'SectorEngine',

    # Military
    'ProcurementEngine',
    'OperationsEngine',
    'OperationType',
    'OperationResult',

    # Events
    'EventEngine',
    'EventCategory',
    'EventSeverity',
]
