"""
Database service for JSON file operations.
Handles all read/write operations for country data and game state.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from backend.config import config


class DBService:
    """Service for database operations using JSON files."""

    def __init__(self):
        self.db_path = config.DB_PATH

    def load_country(self, country_code: str) -> Dict[str, Any]:
        """Load country state from JSON file."""
        file_path = self.db_path / "countries" / f"{country_code.upper()}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Country {country_code} not found")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_country(self, country_code: str, data: Dict[str, Any]) -> None:
        """Save country state to JSON file."""
        file_path = self.db_path / "countries" / f"{country_code.upper()}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_countries(self) -> list[str]:
        """List all available country codes."""
        countries_dir = self.db_path / "countries"
        if not countries_dir.exists():
            return []

        return [f.stem for f in countries_dir.glob("*.json")]

    def load_game_state(self) -> Dict[str, Any]:
        """Load global game state."""
        file_path = self.db_path / "game_state.json"
        if not file_path.exists():
            return {
                "current_date": {"year": 2024, "month": 1, "day": 1},
                "paused": True,
                "speed": 1,
                "selected_country": "ISR",
                "tick_count": 0
            }

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Normalize date format
            if isinstance(data.get("current_date"), str):
                parts = data["current_date"].split("-")
                data["current_date"] = {
                    "year": int(parts[0]),
                    "month": int(parts[1]),
                    "day": int(parts[2])
                }
            return data

    def save_game_state(self, data: Dict[str, Any]) -> None:
        """Save global game state."""
        file_path = self.db_path / "game_state.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_catalog(self, catalog_name: str) -> Dict[str, Any]:
        """Load a catalog file (weapons, events, constraints)."""
        file_path = self.db_path / "catalog" / f"{catalog_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Catalog {catalog_name} not found")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_relations_matrix(self) -> Dict[str, Any]:
        """Load the relations matrix."""
        file_path = self.db_path / "relations" / "relations_matrix.json"
        if not file_path.exists():
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_weapons_catalog(self) -> Dict[str, Any]:
        """Load the weapons catalog."""
        try:
            return self.load_catalog("weapons_catalog")
        except FileNotFoundError:
            return {}

    def load_events_catalog(self) -> Dict[str, Any]:
        """Load the events catalog."""
        try:
            return self.load_catalog("events_catalog")
        except FileNotFoundError:
            return {}

    def load_constraints(self) -> Dict[str, Any]:
        """Load the constraints definitions."""
        try:
            return self.load_catalog("constraints")
        except FileNotFoundError:
            return {}


# Singleton instance
db_service = DBService()
