"""
Tests for WebSocket endpoints and connection manager.
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from backend.api.websocket_routes import (
    ConnectionManager,
    MessageType,
    broadcast_clock_tick,
    broadcast_kpi_update,
    broadcast_event_trigger,
    broadcast_operation_update,
    broadcast_unit_moved
)


class TestConnectionManager:
    """Tests for ConnectionManager."""

    @pytest.fixture
    def manager(self):
        """Create a fresh connection manager."""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        ws.accept = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_adds_to_active_connections(self, manager, mock_websocket):
        """Test that connect adds websocket to active connections."""
        await manager.connect(mock_websocket)

        assert mock_websocket in manager.active_connections
        assert mock_websocket in manager.connection_info

    @pytest.mark.asyncio
    async def test_connect_with_country_code(self, manager, mock_websocket):
        """Test connecting with a country code."""
        await manager.connect(mock_websocket, "ISR")

        assert mock_websocket in manager.active_connections
        assert "ISR" in manager.country_connections
        assert mock_websocket in manager.country_connections["ISR"]
        assert manager.connection_info[mock_websocket]['country_code'] == "ISR"

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self, manager, mock_websocket):
        """Test that disconnect removes websocket."""
        await manager.connect(mock_websocket)
        manager.disconnect(mock_websocket)

        assert mock_websocket not in manager.active_connections
        assert mock_websocket not in manager.connection_info

    @pytest.mark.asyncio
    async def test_disconnect_removes_from_country(self, manager, mock_websocket):
        """Test that disconnect removes from country connections."""
        await manager.connect(mock_websocket, "ISR")
        manager.disconnect(mock_websocket)

        assert "ISR" not in manager.country_connections

    @pytest.mark.asyncio
    async def test_send_personal(self, manager, mock_websocket):
        """Test sending a personal message."""
        await manager.connect(mock_websocket)

        message = {'type': 'test', 'data': 'hello'}
        await manager.send_personal(mock_websocket, message)

        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, manager):
        """Test broadcasting to all connections."""
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2.send_json = AsyncMock()

        await manager.connect(ws1)
        await manager.connect(ws2)

        message = {'type': 'test', 'data': 'broadcast'}
        await manager.broadcast(message)

        ws1.send_json.assert_called_with(message)
        ws2.send_json.assert_called_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_country(self, manager):
        """Test broadcasting to a specific country."""
        ws_isr = AsyncMock()
        ws_usa = AsyncMock()
        ws_isr.send_json = AsyncMock()
        ws_usa.send_json = AsyncMock()

        await manager.connect(ws_isr, "ISR")
        await manager.connect(ws_usa, "USA")

        message = {'type': 'test', 'data': 'country_specific'}
        await manager.broadcast_to_country("ISR", message)

        ws_isr.send_json.assert_called_with(message)
        ws_usa.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_handles_disconnection(self, manager):
        """Test that broadcast handles failed connections."""
        ws_good = AsyncMock()
        ws_bad = AsyncMock()
        ws_good.send_json = AsyncMock()
        ws_bad.send_json = AsyncMock(side_effect=Exception("Connection closed"))

        await manager.connect(ws_good)
        await manager.connect(ws_bad)

        message = {'type': 'test'}
        await manager.broadcast(message)

        # Bad connection should be removed
        assert ws_bad not in manager.active_connections
        assert ws_good in manager.active_connections

    def test_get_connection_count(self, manager):
        """Test getting connection count."""
        assert manager.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_get_connection_count_after_connect(self, manager, mock_websocket):
        """Test connection count after connecting."""
        await manager.connect(mock_websocket)
        assert manager.get_connection_count() == 1

    @pytest.mark.asyncio
    async def test_get_country_connection_count(self, manager, mock_websocket):
        """Test getting country-specific connection count."""
        await manager.connect(mock_websocket, "ISR")
        assert manager.get_country_connection_count("ISR") == 1
        assert manager.get_country_connection_count("USA") == 0


class TestBroadcastFunctions:
    """Tests for broadcast helper functions."""

    @pytest.fixture
    def mock_manager(self, monkeypatch):
        """Mock the connection manager."""
        from backend.api import websocket_routes

        mock = AsyncMock()
        mock.broadcast = AsyncMock()
        mock.broadcast_to_country = AsyncMock()
        monkeypatch.setattr(websocket_routes, 'manager', mock)
        return mock

    @pytest.mark.asyncio
    async def test_broadcast_clock_tick(self, mock_manager):
        """Test clock tick broadcast."""
        await broadcast_clock_tick("2024-03-15", "14:32", 2, False)

        mock_manager.broadcast.assert_called_once()
        call_args = mock_manager.broadcast.call_args[0][0]
        assert call_args['type'] == MessageType.CLOCK_TICK.value
        assert call_args['data']['date'] == "2024-03-15"
        assert call_args['data']['speed'] == 2

    @pytest.mark.asyncio
    async def test_broadcast_kpi_update(self, mock_manager):
        """Test KPI update broadcast."""
        kpis = {'gdp': 520.5, 'treasury': 45.2}
        await broadcast_kpi_update("ISR", kpis)

        mock_manager.broadcast_to_country.assert_called_once()
        call_args = mock_manager.broadcast_to_country.call_args
        assert call_args[0][0] == "ISR"
        assert call_args[0][1]['type'] == MessageType.KPI_UPDATE.value
        assert call_args[0][1]['data'] == kpis

    @pytest.mark.asyncio
    async def test_broadcast_event_trigger(self, mock_manager):
        """Test event trigger broadcast."""
        await broadcast_event_trigger(
            "ISR",
            "evt_001",
            "Border Tension",
            "critical",
            auto_pause=True
        )

        mock_manager.broadcast_to_country.assert_called_once()
        call_args = mock_manager.broadcast_to_country.call_args[0][1]
        assert call_args['type'] == MessageType.EVENT_TRIGGER.value
        assert call_args['data']['event_id'] == "evt_001"
        assert call_args['data']['auto_pause'] is True

    @pytest.mark.asyncio
    async def test_broadcast_operation_update(self, mock_manager):
        """Test operation update broadcast."""
        await broadcast_operation_update(
            "ISR",
            "op_001",
            "active",
            45.0,
            "engagement"
        )

        mock_manager.broadcast_to_country.assert_called_once()
        call_args = mock_manager.broadcast_to_country.call_args[0][1]
        assert call_args['type'] == MessageType.OPERATION_UPDATE.value
        assert call_args['data']['progress'] == 45.0

    @pytest.mark.asyncio
    async def test_broadcast_unit_moved(self, mock_manager):
        """Test unit movement broadcast."""
        await broadcast_unit_moved(
            "ISR",
            "unit_001",
            {'lat': 32.0, 'lng': 34.8},
            "deployed"
        )

        mock_manager.broadcast_to_country.assert_called_once()
        call_args = mock_manager.broadcast_to_country.call_args[0][1]
        assert call_args['type'] == MessageType.UNIT_MOVED.value
        assert call_args['data']['unit_id'] == "unit_001"


class TestWebSocketEndpoint:
    """Integration tests for WebSocket endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_websocket_connect(self, client):
        """Test WebSocket connection."""
        with client.websocket_connect("/api/ws") as websocket:
            # Should receive welcome message
            data = websocket.receive_json()
            assert data['type'] == 'connected'

    def test_websocket_connect_with_country(self, client):
        """Test WebSocket connection with country code."""
        with client.websocket_connect("/api/ws/ISR") as websocket:
            data = websocket.receive_json()
            assert data['type'] == 'connected'
            assert data['country_code'] == 'ISR'

    def test_websocket_ping_pong(self, client):
        """Test ping/pong functionality."""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive welcome
            websocket.receive_json()

            # Send ping
            websocket.send_json({'type': 'ping'})

            # Should receive pong
            data = websocket.receive_json()
            assert data['type'] == 'pong'
            assert 'timestamp' in data

    def test_websocket_subscribe(self, client):
        """Test subscribing to a country."""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive welcome
            websocket.receive_json()

            # Subscribe
            websocket.send_json({'type': 'subscribe', 'country_code': 'ISR'})

            # Should receive confirmation
            data = websocket.receive_json()
            assert data['type'] == 'subscribed'
            assert data['country_code'] == 'ISR'

    def test_websocket_get_status(self, client):
        """Test getting connection status."""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive welcome
            websocket.receive_json()

            # Get status
            websocket.send_json({'type': 'get_status'})

            data = websocket.receive_json()
            assert data['type'] == 'status'
            assert 'total_connections' in data

    def test_websocket_invalid_json(self, client):
        """Test handling invalid JSON."""
        with client.websocket_connect("/api/ws") as websocket:
            # Receive welcome
            websocket.receive_json()

            # Send invalid JSON
            websocket.send_text("not json")

            # Should receive error
            data = websocket.receive_json()
            assert data['type'] == 'error'
