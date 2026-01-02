"""
Active operation tracking model.
Tracks ongoing military operations with progress and results.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

from .map import Coordinates


class OperationType(str, Enum):
    AIR_STRIKE = "air_strike"
    AIR_INTERCEPT = "air_intercept"
    AIR_PATROL = "air_patrol"
    GROUND_ASSAULT = "ground_assault"
    GROUND_DEFENSE = "ground_defense"
    GROUND_PATROL = "ground_patrol"
    NAVAL_PATROL = "naval_patrol"
    NAVAL_BLOCKADE = "naval_blockade"
    NAVAL_STRIKE = "naval_strike"
    CYBER_ATTACK = "cyber_attack"
    SPECIAL_OPS = "special_ops"
    RECONNAISSANCE = "reconnaissance"
    ARTILLERY_BARRAGE = "artillery_barrage"
    MISSILE_STRIKE = "missile_strike"


class OperationStatus(str, Enum):
    PLANNING = "planning"
    DEPLOYING = "deploying"  # Units moving to position
    ACTIVE = "active"  # Operation in progress
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ABORTED = "aborted"  # Cancelled mid-operation


class OperationResult(BaseModel):
    """Results of a completed operation."""
    success: bool
    objectives_achieved: int = 0
    objectives_total: int = 1
    enemy_casualties: int = 0
    enemy_equipment_destroyed: Dict[str, int] = {}
    friendly_casualties: int = 0
    friendly_equipment_lost: Dict[str, int] = {}
    munitions_expended: Dict[str, int] = {}
    cost_millions: float = 0
    intelligence_gained: Optional[str] = None
    territory_gained_km2: float = 0
    diplomatic_impact: Dict[str, int] = {}  # country_code -> relation change


class ActiveOperation(BaseModel):
    """An ongoing military operation."""
    id: str
    name: str
    country_code: str
    operation_type: OperationType
    status: OperationStatus = OperationStatus.PLANNING

    # Timing
    created_at: datetime
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_hours: int = 1  # Expected duration

    # Location
    origin_location: Coordinates  # Where units deploy from
    target_location: Coordinates
    target_name: Optional[str] = None  # e.g., city name, base name
    target_country_code: Optional[str] = None

    # Units
    assigned_unit_ids: List[str] = []
    unit_types_involved: Dict[str, int] = {}  # unit_type -> count

    # Progress
    progress_percent: float = Field(default=0, ge=0, le=100)
    phase: str = "preparation"  # preparation, deployment, engagement, extraction
    phases_completed: List[str] = []

    # Requirements
    required_assets: Dict[str, int] = {}  # asset_type -> count required
    munitions_allocated: Dict[str, int] = {}

    # Success factors
    success_probability: float = Field(default=0.75, ge=0, le=1)
    loss_probability: float = Field(default=0.05, ge=0, le=1)

    # Costs
    political_cost: int = Field(default=0, ge=0, le=100)
    estimated_cost_millions: float = 0

    # Results (populated on completion)
    result: Optional[OperationResult] = None

    # Visibility
    is_covert: bool = False
    detection_risk: float = Field(default=0.1, ge=0, le=1)
    detected: bool = False

    def is_active(self) -> bool:
        """Check if operation is still ongoing."""
        return self.status in [
            OperationStatus.PLANNING,
            OperationStatus.DEPLOYING,
            OperationStatus.ACTIVE
        ]

    def can_cancel(self) -> bool:
        """Check if operation can be cancelled."""
        return self.status in [
            OperationStatus.PLANNING,
            OperationStatus.DEPLOYING
        ]


class OperationsList(BaseModel):
    """Collection of operations for a country."""
    country_code: str
    operations: List[ActiveOperation] = []

    def get_by_id(self, op_id: str) -> Optional[ActiveOperation]:
        """Get operation by ID."""
        for op in self.operations:
            if op.id == op_id:
                return op
        return None

    def get_active(self) -> List[ActiveOperation]:
        """Get all active operations."""
        return [op for op in self.operations if op.is_active()]

    def get_by_type(self, op_type: OperationType) -> List[ActiveOperation]:
        """Get operations by type."""
        return [op for op in self.operations if op.operation_type == op_type]

    def get_by_status(self, status: OperationStatus) -> List[ActiveOperation]:
        """Get operations by status."""
        return [op for op in self.operations if op.status == status]

    def get_completed(self) -> List[ActiveOperation]:
        """Get completed operations (success or failure)."""
        return [
            op for op in self.operations
            if op.status in [OperationStatus.COMPLETED, OperationStatus.FAILED]
        ]

    def get_targeting_location(self, location: Coordinates, radius_km: float) -> List[ActiveOperation]:
        """Get operations targeting near a location."""
        return [
            op for op in self.operations
            if op.is_active() and location.distance_to(op.target_location) <= radius_km
        ]
