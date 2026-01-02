"""
World Sim - Main Application

FastAPI application with game engine integration.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from backend.config import config
from backend.services.db_service import db_service
from backend.services.save_service import save_service

# Engine imports
from backend.engine.clock_service import clock_service, TickType
from backend.engine.tick_processor import get_processor
from backend.engine.budget_engine import BudgetEngine
from backend.engine.sector_engine import SectorEngine
from backend.engine.procurement_engine import ProcurementEngine
from backend.engine.operations_engine import OperationsEngine, OperationType
from backend.engine.event_engine import EventEngine
from backend.engine.economy_engine import EconomyEngine
from backend.engine.demographics_engine import DemographicsEngine
from backend.engine.constraint_engine import ConstraintEngine


# =============================================================================
# Pydantic Models for Request Bodies
# =============================================================================

class BudgetAdjustment(BaseModel):
    category: str
    new_percent: float
    funding_source: str = "rebalance"


class TaxAdjustment(BaseModel):
    new_rate: float


class DebtAction(BaseModel):
    amount_billions: float


class SectorInvestment(BaseModel):
    sector_name: str
    investment_billions: float
    target_improvement: int = 5


class InfrastructureProject(BaseModel):
    project_type: str
    custom_name: Optional[str] = None


class WeaponPurchase(BaseModel):
    weapon_id: str
    quantity: int


class WeaponSale(BaseModel):
    weapon_model: str
    quantity: int
    buyer_country: str


class OperationPlan(BaseModel):
    operation_type: str
    target_country: str
    target_description: str
    assets_committed: Optional[dict] = None


class EventResponse(BaseModel):
    event_id: str
    response: str


class SaveGame(BaseModel):
    slot_name: Optional[str] = None
    description: Optional[str] = None


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("Starting World Sim server...")

    # Initialize tick processor for default country
    state = db_service.load_game_state()
    country_code = state.get("selected_country", "ISR")
    get_processor(country_code, db_service)

    # Start clock service
    clock_service.start()
    print(f"Game clock started for {country_code}")

    yield

    # Shutdown
    print("Shutting down World Sim server...")
    clock_service.stop()


app = FastAPI(
    title="World Sim - Country Simulation Game",
    description="A single-player country simulation combining city-builder economics, grand strategy depth, and military realism",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend assets (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# =============================================================================
# Root and Health Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Serve the frontend index.html."""
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "clock": clock_service.get_state()
    }


# =============================================================================
# Country API Endpoints
# =============================================================================

@app.get("/api/countries")
async def list_countries():
    """List all available countries."""
    countries = db_service.list_countries()
    return {"countries": countries}


@app.get("/api/country/{country_code}")
async def get_country(country_code: str):
    """Get full country state."""
    try:
        data = db_service.load_country(country_code.upper())
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/country/{country_code}/economy")
async def get_economy(country_code: str):
    """Get economy and budget data with summary."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = EconomyEngine(data)
        return {
            "economy": data.get("economy", {}),
            "budget": data.get("budget", {}),
            "summary": engine.get_economic_summary()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/country/{country_code}/military")
async def get_military(country_code: str):
    """Get military data with summary."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = OperationsEngine(data)
        return {
            "military": data.get("military", {}),
            "inventory": data.get("military_inventory", {}),
            "summary": engine.get_military_summary()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/country/{country_code}/demographics")
async def get_demographics(country_code: str):
    """Get demographics and workforce data with summary."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = DemographicsEngine(data)
        return {
            "demographics": data.get("demographics", {}),
            "workforce": data.get("workforce", {}),
            "summary": engine.get_demographic_summary(),
            "workforce_summary": engine.get_workforce_summary()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/country/{country_code}/infrastructure")
async def get_infrastructure(country_code: str):
    """Get infrastructure data."""
    try:
        data = db_service.load_country(country_code.upper())
        return {
            "infrastructure": data.get("infrastructure", {})
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/country/{country_code}/relations")
async def get_relations(country_code: str):
    """Get diplomatic relations data."""
    try:
        data = db_service.load_country(country_code.upper())
        return {
            "relations": data.get("relations", {})
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/country/{country_code}/sectors")
async def get_sectors(country_code: str):
    """Get sector data with summary."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = SectorEngine(data)
        return {
            "sectors": data.get("sectors", {}),
            "summary": engine.get_sector_summary(),
            "active_projects": engine.get_active_projects()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Game Clock API Endpoints
# =============================================================================

@app.get("/api/game/state")
async def get_game_state():
    """Get current game state including clock."""
    state = db_service.load_game_state()
    state["clock"] = clock_service.get_state()
    return state


@app.post("/api/game/clock")
async def update_clock(
    action: str = Query(..., description="Action: pause, resume, or set_speed"),
    speed: float = Query(1.0, description="Game speed multiplier (1, 2, 5, 10)")
):
    """Control game clock: pause, resume, set_speed."""
    if action == "pause":
        clock_service.pause()
    elif action == "resume":
        clock_service.resume()
    elif action == "set_speed":
        if speed not in [1, 2, 5, 10]:
            raise HTTPException(status_code=400, detail="Speed must be 1, 2, 5, or 10")
        clock_service.set_speed(speed)
    else:
        raise HTTPException(status_code=400, detail="Action must be: pause, resume, or set_speed")

    # Sync with game state file
    state = db_service.load_game_state()
    state["paused"] = clock_service.paused
    state["speed"] = clock_service.speed
    db_service.save_game_state(state)

    return clock_service.get_state()


@app.post("/api/game/pause")
async def pause_game():
    """Pause the game clock."""
    clock_service.pause()
    state = db_service.load_game_state()
    state["paused"] = True
    db_service.save_game_state(state)
    return clock_service.get_state()


@app.post("/api/game/resume")
async def resume_game():
    """Resume the game clock."""
    clock_service.resume()
    state = db_service.load_game_state()
    state["paused"] = False
    db_service.save_game_state(state)
    return clock_service.get_state()


@app.post("/api/game/speed")
async def set_speed(speed: int = Query(..., description="Game speed (1, 2, 5, or 10)")):
    """Set game speed multiplier."""
    if speed not in [1, 2, 5, 10]:
        raise HTTPException(status_code=400, detail="Speed must be 1, 2, 5, or 10")

    clock_service.set_speed(speed)
    state = db_service.load_game_state()
    state["speed"] = speed
    db_service.save_game_state(state)
    return clock_service.get_state()


@app.get("/api/game/stream")
async def stream_updates():
    """SSE endpoint for real-time game updates."""
    import json

    async def event_generator():
        last_day = clock_service.day_count
        while True:
            if clock_service.day_count > last_day:
                last_day = clock_service.day_count
                state = db_service.load_game_state()
                country_code = state.get("selected_country", "ISR")
                try:
                    data = db_service.load_country(country_code)
                    update = {
                        "clock": clock_service.get_state(),
                        "meta": data.get("meta", {}),
                        "indices": data.get("indices", {})
                    }
                    yield f"data: {json.dumps(update)}\n\n"
                except Exception:
                    pass
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# =============================================================================
# Budget API Endpoints
# =============================================================================

@app.get("/api/budget/{country_code}")
async def get_budget(country_code: str):
    """Get budget summary."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = BudgetEngine(data)
        return engine.get_budget_summary()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/budget/{country_code}/adjust")
async def adjust_budget(country_code: str, adjustment: BudgetAdjustment):
    """Adjust budget allocation."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = BudgetEngine(data)

        result = engine.adjust_allocation(
            adjustment.category,
            adjustment.new_percent,
            adjustment.funding_source
        )

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/budget/{country_code}/tax")
async def set_tax_rate(country_code: str, adjustment: TaxAdjustment):
    """Set tax rate."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = BudgetEngine(data)

        result = engine.set_tax_rate(adjustment.new_rate)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/budget/{country_code}/debt/take")
async def take_debt(country_code: str, action: DebtAction):
    """Take on debt."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = BudgetEngine(data)

        result = engine.take_debt(action.amount_billions)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/budget/{country_code}/debt/repay")
async def repay_debt(country_code: str, action: DebtAction):
    """Repay debt."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = BudgetEngine(data)

        result = engine.repay_debt(action.amount_billions)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Sector Development API Endpoints
# =============================================================================

@app.post("/api/sectors/{country_code}/invest")
async def invest_in_sector(country_code: str, investment: SectorInvestment):
    """Invest in a sector."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = SectorEngine(data)

        result = engine.invest_in_sector(
            investment.sector_name,
            investment.investment_billions,
            investment.target_improvement
        )

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/sectors/{country_code}/infrastructure")
async def start_infrastructure(country_code: str, project: InfrastructureProject):
    """Start an infrastructure project."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = SectorEngine(data)

        result = engine.start_infrastructure_project(
            project.project_type,
            project.custom_name
        )

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.get("/api/sectors/{country_code}/projects")
async def get_projects(country_code: str):
    """Get active projects."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = SectorEngine(data)
        return {"projects": engine.get_active_projects()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.delete("/api/sectors/{country_code}/projects/{project_id}")
async def cancel_project(country_code: str, project_id: str):
    """Cancel a project."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = SectorEngine(data)

        result = engine.cancel_project(project_id)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Military Procurement API Endpoints
# =============================================================================

@app.get("/api/procurement/catalog")
async def get_weapons_catalog(category: Optional[str] = None):
    """Get weapons catalog."""
    catalog = db_service.load_weapons_catalog()
    if category:
        catalog = {k: v for k, v in catalog.items() if v.get('category') == category}
    return {"catalog": catalog}


@app.get("/api/procurement/{country_code}/orders")
async def get_procurement_orders(country_code: str):
    """Get active procurement orders."""
    try:
        data = db_service.load_country(country_code.upper())
        catalog = db_service.load_weapons_catalog()
        engine = ProcurementEngine(data, catalog)
        return {"orders": engine.get_active_orders()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/procurement/{country_code}/check")
async def check_purchase_eligibility(country_code: str, purchase: WeaponPurchase):
    """Check if a weapon purchase is possible."""
    try:
        data = db_service.load_country(country_code.upper())
        catalog = db_service.load_weapons_catalog()
        engine = ProcurementEngine(data, catalog)

        return engine.check_purchase_eligibility(
            purchase.weapon_id,
            purchase.quantity
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/procurement/{country_code}/purchase")
async def purchase_weapon(country_code: str, purchase: WeaponPurchase):
    """Purchase weapons."""
    try:
        data = db_service.load_country(country_code.upper())
        catalog = db_service.load_weapons_catalog()
        engine = ProcurementEngine(data, catalog)

        result = engine.request_purchase(
            purchase.weapon_id,
            purchase.quantity
        )

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/procurement/{country_code}/sell")
async def sell_weapon(country_code: str, sale: WeaponSale):
    """Sell weapons from inventory."""
    try:
        data = db_service.load_country(country_code.upper())
        catalog = db_service.load_weapons_catalog()
        engine = ProcurementEngine(data, catalog)

        result = engine.sell_weapons(
            sale.weapon_model,
            sale.quantity,
            sale.buyer_country
        )

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.delete("/api/procurement/{country_code}/orders/{order_id}")
async def cancel_order(country_code: str, order_id: str):
    """Cancel a procurement order."""
    try:
        data = db_service.load_country(country_code.upper())
        catalog = db_service.load_weapons_catalog()
        engine = ProcurementEngine(data, catalog)

        result = engine.cancel_order(order_id)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Military Operations API Endpoints
# =============================================================================

@app.get("/api/operations/types")
async def get_operation_types():
    """Get available operation types."""
    return {
        "types": [op.value for op in OperationType],
        "details": OperationsEngine.OPERATIONS
    }


@app.post("/api/operations/{country_code}/plan")
async def plan_operation(country_code: str, plan: OperationPlan):
    """Plan an operation (without executing)."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = OperationsEngine(data)

        return engine.plan_operation(
            plan.operation_type,
            plan.target_country,
            plan.target_description,
            plan.assets_committed
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/operations/{country_code}/execute")
async def execute_operation(country_code: str, plan: OperationPlan):
    """Execute a military operation."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = OperationsEngine(data)

        result = engine.execute_operation(
            plan.operation_type,
            plan.target_country,
            plan.target_description,
            plan.assets_committed
        )

        db_service.save_country(country_code.upper(), data)

        return result.to_dict()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/operations/{country_code}/readiness")
async def set_readiness(country_code: str, level: str = Query(..., description="low, normal, high, or maximum")):
    """Set military readiness level."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = OperationsEngine(data)

        result = engine.set_readiness_level(level)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Events API Endpoints
# =============================================================================

@app.get("/api/events/{country_code}")
async def get_events(country_code: str):
    """Get active events."""
    try:
        data = db_service.load_country(country_code.upper())
        events_catalog = db_service.load_events_catalog()
        engine = EventEngine(data, events_catalog)

        return {
            "active_events": engine.get_active_events(),
            "history": engine.get_event_history()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/events/{country_code}/respond")
async def respond_to_event(country_code: str, response: EventResponse):
    """Respond to an active event."""
    try:
        data = db_service.load_country(country_code.upper())
        events_catalog = db_service.load_events_catalog()
        engine = EventEngine(data, events_catalog)

        result = engine.respond_to_event(response.event_id, response.response)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


@app.post("/api/events/{country_code}/trigger")
async def trigger_event(country_code: str, event_id: str = Query(...)):
    """Force trigger an event (for testing)."""
    try:
        data = db_service.load_country(country_code.upper())
        events_catalog = db_service.load_events_catalog()
        engine = EventEngine(data, events_catalog)

        result = engine.force_event(event_id)

        if result.get('success'):
            db_service.save_country(country_code.upper(), data)

        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Save/Load API Endpoints
# =============================================================================

@app.get("/api/saves")
async def list_saves():
    """List all save slots."""
    return {"saves": save_service.list_saves()}


@app.get("/api/saves/{slot_name}")
async def get_save_details(slot_name: str):
    """Get details of a specific save."""
    return save_service.get_save_details(slot_name)


@app.post("/api/saves/{country_code}")
async def save_game(country_code: str, save: SaveGame):
    """Save the game."""
    return save_service.save_game(
        country_code.upper(),
        save.slot_name,
        save.description
    )


@app.post("/api/saves/load/{slot_name}")
async def load_game(slot_name: str):
    """Load a saved game."""
    result = save_service.load_game(slot_name)

    if result.get('success'):
        # Reinitialize tick processor for loaded country
        country_code = result.get('meta', {}).get('country_code', 'ISR')
        get_processor(country_code, db_service)

    return result


@app.delete("/api/saves/{slot_name}")
async def delete_save(slot_name: str):
    """Delete a save slot."""
    return save_service.delete_save(slot_name)


@app.post("/api/saves/{country_code}/quick")
async def quick_save(country_code: str):
    """Quick save."""
    return save_service.quick_save(country_code.upper())


@app.post("/api/saves/quickload")
async def quick_load():
    """Quick load."""
    return save_service.quick_load()


# =============================================================================
# Constraint Checking API
# =============================================================================

@app.post("/api/constraints/{country_code}/check")
async def check_constraints(country_code: str, constraints: dict):
    """Check if constraints are satisfied."""
    try:
        data = db_service.load_country(country_code.upper())
        engine = ConstraintEngine(data)

        satisfied, results = engine.check_all(constraints)

        return {
            "satisfied": satisfied,
            "results": [r.to_dict() for r in results]
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
