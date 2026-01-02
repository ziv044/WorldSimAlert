# Backend Gaps for Functional Game

What's missing from the backend to make the UX specification work.

---

## Status Summary

| Feature | Backend | Endpoints | Status |
|---------|---------|-----------|--------|
| Budget Allocation | ✓ | ✓ | **READY** |
| Sector Investment | ✓ | ✓ | **READY** |
| Infrastructure Projects | ✓ | ✓ | **READY** |
| Military Procurement | ✓ | ✓ | **READY** |
| Event System + Responses | ✓ | ✓ | **READY** |
| Game Clock + Speed | ✓ | ✓ | **READY** |
| Military Operations | Partial | Partial | **NEEDS LOCATIONS** |
| Real-Time Streaming | Partial | Partial | **NEEDS WEBSOCKET** |
| Map Display | ✗ | ✗ | **MISSING** |
| City Data | ✗ | ✗ | **MISSING** |
| Military Bases | ✗ | ✗ | **MISSING** |
| Unit Positioning | ✗ | ✗ | **MISSING** |
| Unit Orders | ✗ | ✗ | **MISSING** |
| Geographic Engine | ✗ | ✗ | **MISSING** |

---

## CRITICAL MISSING: Map & Geographic System

The center of the UI (interactive map) has **zero backend support**.

### Missing Data Models

```python
# models/map.py - Geographic coordinate system
class Coordinates(BaseModel):
    lat: float
    lng: float

class MapRegion(BaseModel):
    id: str
    name: str
    country_code: str
    polygon: List[Coordinates]  # GeoJSON-style boundary
    terrain_type: str  # urban, desert, mountain, water

# models/cities.py - City definitions
class City(BaseModel):
    id: str
    name: str
    country_code: str
    location: Coordinates
    population: int
    is_capital: bool
    infrastructure_level: int
    garrison_units: List[str]  # unit IDs stationed here

# models/bases.py - Military installations
class MilitaryBase(BaseModel):
    id: str
    name: str
    location: Coordinates
    base_type: str  # air_base, naval_base, army_base, command
    capacity: int
    stationed_units: List[str]
    operational: bool

# models/units.py - Individual unit tracking
class MilitaryUnit(BaseModel):
    id: str
    unit_type: str  # F-35, Merkava, Sa'ar_Corvette
    quantity: int
    location: Coordinates
    status: str  # idle, deployed, in_combat, returning
    health: float  # 0-100%
    assigned_operation: Optional[str]
    home_base: str
```

### Missing API Endpoints

```
GET  /api/map/data                    - Full map with cities, bases, borders
GET  /api/map/cities                  - All cities with locations
GET  /api/map/bases                   - All military bases
GET  /api/map/units                   - All unit positions
GET  /api/map/borders                 - Country borders as GeoJSON
GET  /api/map/overlay/{type}          - Heat maps (economic/military/diplomatic)

POST /api/units/{unit_id}/deploy      - Deploy unit to location
POST /api/units/{unit_id}/move        - Move unit to destination
POST /api/units/{unit_id}/return      - Return unit to base
GET  /api/units/{unit_id}/status      - Get unit status and location
```

### Missing Engine

```python
# engine/geographic_engine.py
class GeographicEngine:
    def calculate_distance(self, from: Coordinates, to: Coordinates) -> float
    def get_units_in_radius(self, center: Coordinates, radius_km: float) -> List[MilitaryUnit]
    def get_travel_time(self, unit: MilitaryUnit, destination: Coordinates) -> timedelta
    def check_line_of_sight(self, from: Coordinates, to: Coordinates) -> bool
    def get_terrain_at(self, location: Coordinates) -> str
```

---

## MISSING: Location-Based Operations

Operations exist but can't target locations.

### Current State
```python
# Can do this:
execute_operation(country_code="ISR", operation_type="air_strike", target="enemy")

# Cannot do this:
execute_operation(country_code="ISR", operation_type="air_strike",
                  target_location=Coordinates(lat=33.8, lng=35.5),
                  units=["unit_001", "unit_002"])
```

### Needs Added

```python
# engine/operations_engine.py additions
def execute_operation(
    self,
    country_code: str,
    operation_type: str,
    target_location: Coordinates,      # NEW
    unit_ids: List[str],               # NEW - specific units
    duration_days: Optional[int] = None # NEW - for patrols/blockades
) -> OperationResult

def get_active_operations(self, country_code: str) -> List[ActiveOperation]
def cancel_operation(self, operation_id: str) -> bool
def get_operation_progress(self, operation_id: str) -> OperationStatus
```

### New Model

```python
# models/active_operation.py
class ActiveOperation(BaseModel):
    id: str
    operation_type: str
    country_code: str
    target_location: Coordinates
    assigned_units: List[str]
    started_at: datetime
    duration_days: int
    progress_percent: float
    status: str  # active, completed, failed, cancelled
    casualties: Dict[str, int]
```

---

## MISSING: Real-Time WebSocket

SSE exists but is too slow and coarse.

### Current Limitation
- Updates only when game **day** changes
- Only sends clock + indices
- No operation progress streaming
- No event push notifications

### Needs Added

```python
# WebSocket endpoint
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Push updates for:
        # - Clock ticks (every game hour)
        # - KPI changes
        # - Event triggers (with auto-pause)
        # - Operation progress
        # - Unit movements
        # - Procurement deliveries
```

### Message Types Needed

```json
{"type": "clock_tick", "data": {"date": "2024-03-15", "time": "14:32"}}
{"type": "kpi_update", "data": {"gdp": 520.5, "treasury": 45.2}}
{"type": "event_trigger", "data": {"id": "evt_001", "severity": "critical", "auto_pause": true}}
{"type": "operation_progress", "data": {"id": "op_001", "progress": 45, "status": "active"}}
{"type": "unit_moved", "data": {"unit_id": "u_001", "location": {"lat": 32.1, "lng": 34.8}}}
{"type": "delivery_arrived", "data": {"weapon": "F-35", "quantity": 5}}
```

---

## MISSING: Seed Data

### Cities (Israel example)
```json
// db/map/cities_ISR.json
[
  {"id": "tlv", "name": "Tel Aviv", "lat": 32.0853, "lng": 34.7818, "population": 460000, "is_capital": false},
  {"id": "jrs", "name": "Jerusalem", "lat": 31.7683, "lng": 35.2137, "population": 936000, "is_capital": true},
  {"id": "hfa", "name": "Haifa", "lat": 32.7940, "lng": 34.9896, "population": 285000, "is_capital": false},
  {"id": "ber", "name": "Be'er Sheva", "lat": 31.2530, "lng": 34.7915, "population": 209000, "is_capital": false}
]
```

### Military Bases
```json
// db/map/bases_ISR.json
[
  {"id": "ramat_david", "name": "Ramat David AFB", "type": "air_base", "lat": 32.6651, "lng": 35.1796},
  {"id": "nevatim", "name": "Nevatim AFB", "type": "air_base", "lat": 31.2083, "lng": 35.0122},
  {"id": "haifa_naval", "name": "Haifa Naval Base", "type": "naval_base", "lat": 32.8191, "lng": 34.9983},
  {"id": "tze'elim", "name": "Tze'elim Training Base", "type": "army_base", "lat": 31.1500, "lng": 34.5833}
]
```

### Unit Assignments
```json
// db/map/units_ISR.json
[
  {"id": "u_f35_1", "type": "F-35I", "quantity": 25, "base": "nevatim", "status": "idle"},
  {"id": "u_f35_2", "type": "F-35I", "quantity": 25, "base": "ramat_david", "status": "idle"},
  {"id": "u_merkava_1", "type": "Merkava_Mk4", "quantity": 120, "base": "tze'elim", "status": "idle"},
  {"id": "u_saar_1", "type": "Saar_6", "quantity": 4, "base": "haifa_naval", "status": "idle"}
]
```

---

## Implementation Order

### Phase 1: Map Foundation (Blocks Everything)
1. Create `models/map.py`, `models/cities.py`, `models/bases.py`, `models/units.py`
2. Create seed data files for Israel
3. Create `GET /api/map/*` endpoints
4. Create `services/map_service.py` for data loading

### Phase 2: Unit Management
1. Create `engine/unit_engine.py`
2. Add unit deployment/movement endpoints
3. Track unit positions in game state
4. Update units on tick

### Phase 3: Location-Based Operations
1. Extend `operations_engine.py` with location targeting
2. Add `ActiveOperation` model
3. Track ongoing operations
4. Calculate operation effects by location

### Phase 4: Real-Time Updates
1. Add WebSocket endpoint
2. Broadcast clock ticks at hour granularity
3. Push event notifications with auto-pause
4. Stream operation progress
5. Stream unit movements

---

## Files to Create

```
backend/
├── models/
│   ├── map.py              # NEW - Coordinates, MapRegion
│   ├── cities.py           # NEW - City model
│   ├── bases.py            # NEW - MilitaryBase model
│   ├── units.py            # NEW - MilitaryUnit model
│   └── active_operation.py # NEW - ActiveOperation model
├── engine/
│   ├── geographic_engine.py # NEW - Distance, travel time, terrain
│   └── unit_engine.py       # NEW - Unit deployment, movement
├── services/
│   └── map_service.py       # NEW - Load map data from JSON
db/
├── map/
│   ├── cities_ISR.json      # NEW - Israel cities
│   ├── bases_ISR.json       # NEW - Israel bases
│   ├── units_ISR.json       # NEW - Israel unit assignments
│   └── borders.geojson      # NEW - Country borders
```

---

## Endpoints to Add

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/map/data` | Full map state |
| GET | `/api/map/cities` | All cities |
| GET | `/api/map/bases` | All military bases |
| GET | `/api/map/units` | All unit positions |
| GET | `/api/map/borders` | GeoJSON borders |
| GET | `/api/map/overlay/{type}` | Heat map data |
| POST | `/api/units/{id}/deploy` | Deploy to location |
| POST | `/api/units/{id}/move` | Move unit |
| POST | `/api/units/{id}/return` | Return to base |
| GET | `/api/operations/active` | Active operations |
| DELETE | `/api/operations/{id}` | Cancel operation |
| WS | `/api/ws` | Real-time updates |

---

## What Works Today (No Changes Needed)

These features are **complete and ready**:
- Budget allocation with sliders
- Tax rate adjustment
- Sector investment
- Infrastructure project building
- Military procurement queue (Red Alert style)
- Weapons catalog browsing
- Event generation and responses
- Game clock with pause/speed
- Save/load system
- All economic KPI calculations
