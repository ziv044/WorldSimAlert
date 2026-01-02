"""
Clock & Tick System - Phase 1

Manages game time progression and triggers tick handlers at appropriate intervals.
"""

from datetime import date, timedelta
from typing import Callable, Dict, List, Optional
import asyncio


class TickType:
    """Tick type constants for different update frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ClockService:
    """
    Manages game clock and tick system.

    Tick intervals:
    - Daily: 1 game day = 1 real second at 1x speed
    - Weekly: Every 7 game days
    - Monthly: First of each month
    - Quarterly: Jan, Apr, Jul, Oct
    - Yearly: January 1st
    """

    def __init__(self, start_date: Optional[date] = None):
        self.current_date: date = start_date or date(2024, 1, 1)
        self.day_count: int = 0
        self.paused: bool = True
        self.speed: float = 1.0
        self._running: bool = False
        self._task: Optional[asyncio.Task] = None

        self.tick_handlers: Dict[str, List[Callable]] = {
            TickType.DAILY: [],
            TickType.WEEKLY: [],
            TickType.MONTHLY: [],
            TickType.QUARTERLY: [],
            TickType.YEARLY: [],
        }

    def register_handler(self, tick_type: str, handler: Callable) -> None:
        """
        Register a function to be called on specific tick type.

        Args:
            tick_type: One of TickType constants
            handler: Async function(game_date: date, day_count: int)
        """
        if tick_type in self.tick_handlers:
            self.tick_handlers[tick_type].append(handler)

    def unregister_handler(self, tick_type: str, handler: Callable) -> None:
        """Remove a registered handler."""
        if tick_type in self.tick_handlers and handler in self.tick_handlers[tick_type]:
            self.tick_handlers[tick_type].remove(handler)

    async def advance_day(self) -> Dict[str, bool]:
        """
        Advance game by one day and trigger appropriate ticks.

        Returns:
            Dict indicating which tick types were triggered
        """
        if self.paused:
            return {}

        self.day_count += 1
        self.current_date += timedelta(days=1)

        triggered = {
            TickType.DAILY: True,
            TickType.WEEKLY: False,
            TickType.MONTHLY: False,
            TickType.QUARTERLY: False,
            TickType.YEARLY: False,
        }

        # Always trigger daily
        await self._trigger_handlers(TickType.DAILY)

        # Check for weekly (every 7 days)
        if self.day_count % 7 == 0:
            triggered[TickType.WEEKLY] = True
            await self._trigger_handlers(TickType.WEEKLY)

        # Check for monthly (first of month)
        if self.current_date.day == 1:
            triggered[TickType.MONTHLY] = True
            await self._trigger_handlers(TickType.MONTHLY)

            # Check for quarterly (Jan, Apr, Jul, Oct)
            if self.current_date.month in [1, 4, 7, 10]:
                triggered[TickType.QUARTERLY] = True
                await self._trigger_handlers(TickType.QUARTERLY)

            # Check for yearly (January)
            if self.current_date.month == 1:
                triggered[TickType.YEARLY] = True
                await self._trigger_handlers(TickType.YEARLY)

        return triggered

    async def _trigger_handlers(self, tick_type: str) -> None:
        """Trigger all handlers for a tick type."""
        for handler in self.tick_handlers[tick_type]:
            try:
                await handler(self.current_date, self.day_count)
            except Exception as e:
                print(f"Error in {tick_type} handler: {e}")

    async def run(self) -> None:
        """Main game loop - runs continuously."""
        self._running = True
        while self._running:
            if not self.paused:
                await self.advance_day()
            await asyncio.sleep(1.0 / self.speed)

    def start(self) -> asyncio.Task:
        """Start the clock in the background."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run())
        return self._task

    def stop(self) -> None:
        """Stop the clock loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    def pause(self) -> None:
        """Pause the game clock."""
        self.paused = True

    def resume(self) -> None:
        """Resume the game clock."""
        self.paused = False

    def set_speed(self, speed: float) -> None:
        """
        Set game speed multiplier.

        Args:
            speed: Multiplier (1.0 = normal, 2.0 = 2x, etc.)
        """
        self.speed = max(0.1, min(100.0, speed))

    def set_date(self, new_date: date) -> None:
        """Set the current game date (for save/load)."""
        self.current_date = new_date

    def get_state(self) -> Dict:
        """Get current clock state."""
        return {
            "current_date": {
                "year": self.current_date.year,
                "month": self.current_date.month,
                "day": self.current_date.day
            },
            "day_count": self.day_count,
            "paused": self.paused,
            "speed": self.speed
        }


# Global clock instance
clock_service = ClockService()
