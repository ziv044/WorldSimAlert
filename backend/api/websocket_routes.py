"""
WebSocket endpoint for real-time game updates.
Provides push notifications for clock ticks, KPI changes, events, and unit movements.
"""
import asyncio
import json
from typing import Set, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


class MessageType(str, Enum):
    """Types of WebSocket messages."""
    CLOCK_TICK = "clock_tick"
    KPI_UPDATE = "kpi_update"
    EVENT_TRIGGER = "event_trigger"
    EVENT_RESOLVED = "event_resolved"
    OPERATION_UPDATE = "operation_update"
    OPERATION_COMPLETED = "operation_completed"
    UNIT_MOVED = "unit_moved"
    UNIT_STATUS = "unit_status"
    DELIVERY_ARRIVED = "delivery_arrived"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    SPEED_CHANGED = "speed_changed"
    # Border deployment events
    DEPLOYMENT_UPDATED = "deployment_updated"
    RESERVES_CALLED = "reserves_called"
    ALERT_LEVEL_CHANGED = "alert_level_changed"
    ERROR = "error"


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts.

    Supports:
    - Multiple concurrent connections
    - Country-specific subscriptions
    - Broadcast to all or specific countries
    """

    def __init__(self):
        # All active connections
        self.active_connections: Set[WebSocket] = set()

        # Country-specific connections: country_code -> set of websockets
        self.country_connections: Dict[str, Set[WebSocket]] = {}

        # Connection metadata: websocket -> {country_code, connected_at}
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, country_code: Optional[str] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()

        self.active_connections.add(websocket)
        self.connection_info[websocket] = {
            'country_code': country_code,
            'connected_at': datetime.utcnow()
        }

        if country_code:
            if country_code not in self.country_connections:
                self.country_connections[country_code] = set()
            self.country_connections[country_code].add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)

        info = self.connection_info.pop(websocket, {})
        country_code = info.get('country_code')

        if country_code and country_code in self.country_connections:
            self.country_connections[country_code].discard(websocket)
            if not self.country_connections[country_code]:
                del self.country_connections[country_code]

    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connections."""
        disconnected = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_to_country(self, country_code: str, message: Dict[str, Any]):
        """Broadcast a message to all connections subscribed to a country."""
        if country_code not in self.country_connections:
            return

        disconnected = []

        for websocket in self.country_connections[country_code]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self.disconnect(ws)

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.active_connections)

    def get_country_connection_count(self, country_code: str) -> int:
        """Get number of connections for a specific country."""
        return len(self.country_connections.get(country_code, set()))


# Singleton connection manager
manager = ConnectionManager()


# Router for WebSocket endpoints
router = APIRouter(tags=["WebSocket"])


@router.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates.

    Connect without country code to receive all updates.
    Send {"type": "subscribe", "country_code": "ISR"} to subscribe to country-specific updates.
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await manager.send_personal(websocket, {
            'type': 'connected',
            'message': 'WebSocket connected',
            'timestamp': datetime.utcnow().isoformat()
        })

        while True:
            # Receive messages from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal(websocket, {
                    'type': MessageType.ERROR.value,
                    'message': 'Invalid JSON'
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/api/ws/{country_code}")
async def websocket_country_endpoint(websocket: WebSocket, country_code: str):
    """
    WebSocket endpoint with automatic country subscription.

    All updates for the specified country will be pushed to this connection.
    """
    await manager.connect(websocket, country_code.upper())

    try:
        await manager.send_personal(websocket, {
            'type': 'connected',
            'message': f'WebSocket connected for {country_code.upper()}',
            'country_code': country_code.upper(),
            'timestamp': datetime.utcnow().isoformat()
        })

        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal(websocket, {
                    'type': MessageType.ERROR.value,
                    'message': 'Invalid JSON'
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming messages from clients."""
    msg_type = message.get('type')

    if msg_type == 'subscribe':
        # Subscribe to a country
        country_code = message.get('country_code', '').upper()
        if country_code:
            info = manager.connection_info.get(websocket, {})
            old_country = info.get('country_code')

            # Remove from old country
            if old_country and old_country in manager.country_connections:
                manager.country_connections[old_country].discard(websocket)

            # Add to new country
            if country_code not in manager.country_connections:
                manager.country_connections[country_code] = set()
            manager.country_connections[country_code].add(websocket)
            manager.connection_info[websocket]['country_code'] = country_code

            await manager.send_personal(websocket, {
                'type': 'subscribed',
                'country_code': country_code
            })

    elif msg_type == 'ping':
        # Respond to ping
        await manager.send_personal(websocket, {
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        })

    elif msg_type == 'get_status':
        # Return connection status
        await manager.send_personal(websocket, {
            'type': 'status',
            'total_connections': manager.get_connection_count(),
            'your_country': manager.connection_info.get(websocket, {}).get('country_code')
        })


# =============================================================================
# Broadcast Functions (called by game engine)
# =============================================================================

async def broadcast_clock_tick(date: str, time: str, speed: int, paused: bool):
    """Broadcast a clock tick to all connections."""
    await manager.broadcast({
        'type': MessageType.CLOCK_TICK.value,
        'data': {
            'date': date,
            'time': time,
            'speed': speed,
            'paused': paused
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_kpi_update(country_code: str, kpis: Dict[str, Any]):
    """Broadcast KPI updates to country subscribers."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.KPI_UPDATE.value,
        'country_code': country_code,
        'data': kpis,
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_event_trigger(
    country_code: str,
    event_id: str,
    event_name: str,
    severity: str,
    auto_pause: bool = False
):
    """Broadcast an event trigger to country subscribers."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.EVENT_TRIGGER.value,
        'country_code': country_code,
        'data': {
            'event_id': event_id,
            'event_name': event_name,
            'severity': severity,
            'auto_pause': auto_pause
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_operation_update(
    country_code: str,
    operation_id: str,
    status: str,
    progress: float,
    phase: str
):
    """Broadcast operation progress update."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.OPERATION_UPDATE.value,
        'country_code': country_code,
        'data': {
            'operation_id': operation_id,
            'status': status,
            'progress': progress,
            'phase': phase
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_operation_completed(
    country_code: str,
    operation_id: str,
    success: bool,
    result: Dict[str, Any]
):
    """Broadcast operation completion."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.OPERATION_COMPLETED.value,
        'country_code': country_code,
        'data': {
            'operation_id': operation_id,
            'success': success,
            'result': result
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_unit_moved(
    country_code: str,
    unit_id: str,
    location: Dict[str, float],
    status: str
):
    """Broadcast unit movement."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.UNIT_MOVED.value,
        'country_code': country_code,
        'data': {
            'unit_id': unit_id,
            'location': location,
            'status': status
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_unit_status(
    country_code: str,
    unit_id: str,
    status: str,
    health: float,
    fuel: float,
    ammo: float
):
    """Broadcast unit status change."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.UNIT_STATUS.value,
        'country_code': country_code,
        'data': {
            'unit_id': unit_id,
            'status': status,
            'health': health,
            'fuel': fuel,
            'ammo': ammo
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_delivery_arrived(
    country_code: str,
    weapon_type: str,
    quantity: int,
    order_id: str
):
    """Broadcast weapon delivery."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.DELIVERY_ARRIVED.value,
        'country_code': country_code,
        'data': {
            'weapon_type': weapon_type,
            'quantity': quantity,
            'order_id': order_id
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_game_state_change(paused: bool, speed: int):
    """Broadcast game pause/resume/speed change."""
    msg_type = MessageType.GAME_PAUSED if paused else MessageType.GAME_RESUMED

    await manager.broadcast({
        'type': msg_type.value,
        'data': {
            'paused': paused,
            'speed': speed
        },
        'timestamp': datetime.utcnow().isoformat()
    })


# =============================================================================
# Border Deployment Broadcast Functions
# =============================================================================

async def broadcast_deployment_updated(
    country_code: str,
    zone_id: str,
    zone_name: str,
    active_troops: int,
    reserve_troops: int,
    alert_level: str
):
    """Broadcast deployment zone update."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.DEPLOYMENT_UPDATED.value,
        'country_code': country_code,
        'data': {
            'zone_id': zone_id,
            'zone_name': zone_name,
            'active_troops': active_troops,
            'reserve_troops': reserve_troops,
            'total_troops': active_troops + reserve_troops,
            'alert_level': alert_level
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_reserves_called(
    country_code: str,
    count: int,
    total_called: int,
    zone_id: Optional[str] = None
):
    """Broadcast reserve callup."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.RESERVES_CALLED.value,
        'country_code': country_code,
        'data': {
            'called_up': count,
            'total_reserves_called': total_called,
            'deployed_to_zone': zone_id
        },
        'timestamp': datetime.utcnow().isoformat()
    })


async def broadcast_alert_level_changed(
    country_code: str,
    zone_id: str,
    zone_name: str,
    old_level: str,
    new_level: str
):
    """Broadcast alert level change."""
    await manager.broadcast_to_country(country_code, {
        'type': MessageType.ALERT_LEVEL_CHANGED.value,
        'country_code': country_code,
        'data': {
            'zone_id': zone_id,
            'zone_name': zone_name,
            'old_level': old_level,
            'new_level': new_level
        },
        'timestamp': datetime.utcnow().isoformat()
    })
