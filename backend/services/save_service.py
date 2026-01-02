"""
Save/Load Service - Phase 9

Manages game state persistence with save slots.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SaveService:
    """
    Manages save game functionality.

    Features:
    - Multiple save slots
    - Automatic backups
    - Save metadata (date, country, game date)
    - Quick save/load
    """

    def __init__(self, saves_dir: Optional[Path] = None, db_dir: Optional[Path] = None):
        self.saves_dir = saves_dir or Path("db/saves")
        self.db_dir = db_dir or Path("db")
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval_days = 30  # Game days
        self.max_auto_saves = 5

    def save_game(
        self,
        country_code: str,
        slot_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Save current game state to a slot.

        Args:
            country_code: Country being played
            slot_name: Name for the save slot (auto-generated if None)
            description: Optional description for the save

        Returns:
            Dict with save metadata
        """
        if not slot_name:
            slot_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize slot name
        slot_name = "".join(c for c in slot_name if c.isalnum() or c in '-_')

        save_dir = self.saves_dir / slot_name
        save_dir.mkdir(exist_ok=True)

        try:
            # Copy country file
            src_country = self.db_dir / "countries" / f"{country_code}.json"
            dst_country = save_dir / f"{country_code}.json"

            if src_country.exists():
                shutil.copy(src_country, dst_country)
            else:
                return {'success': False, 'error': f'Country file not found: {country_code}'}

            # Copy game state
            src_state = self.db_dir / "game_state.json"
            if src_state.exists():
                shutil.copy(src_state, save_dir / "game_state.json")

            # Get game date from country data
            game_date = self._get_game_date(country_code)

            # Create metadata
            meta = {
                'slot_name': slot_name,
                'country_code': country_code,
                'save_time': datetime.now().isoformat(),
                'game_date': game_date,
                'description': description or f"Save on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'version': '1.0'
            }

            with open(save_dir / "meta.json", "w") as f:
                json.dump(meta, f, indent=2)

            return {
                'success': True,
                'slot_name': slot_name,
                'meta': meta
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def load_game(self, slot_name: str) -> Dict:
        """
        Load a saved game.

        Args:
            slot_name: Name of the save slot to load

        Returns:
            Dict with load status and metadata
        """
        save_dir = self.saves_dir / slot_name

        if not save_dir.exists():
            return {'success': False, 'error': f'Save not found: {slot_name}'}

        try:
            # Load metadata
            meta_file = save_dir / "meta.json"
            if not meta_file.exists():
                return {'success': False, 'error': 'Save metadata missing'}

            with open(meta_file) as f:
                meta = json.load(f)

            country_code = meta.get('country_code')
            if not country_code:
                return {'success': False, 'error': 'Country code missing from save'}

            # Backup current state before loading
            self._create_backup(country_code)

            # Restore country file
            src_country = save_dir / f"{country_code}.json"
            dst_country = self.db_dir / "countries" / f"{country_code}.json"

            if src_country.exists():
                shutil.copy(src_country, dst_country)
            else:
                return {'success': False, 'error': f'Country save file missing: {country_code}'}

            # Restore game state
            src_state = save_dir / "game_state.json"
            if src_state.exists():
                shutil.copy(src_state, self.db_dir / "game_state.json")

            return {
                'success': True,
                'slot_name': slot_name,
                'meta': meta
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _create_backup(self, country_code: str) -> None:
        """Create a backup before loading."""
        backup_dir = self.saves_dir / "_backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{country_code}_{timestamp}"

        self.save_game(country_code, backup_name, "Automatic backup before load")

        # Clean old backups (keep last 3)
        backups = sorted(backup_dir.glob("backup_*"))
        while len(backups) > 3:
            oldest = backups.pop(0)
            if oldest.is_dir():
                shutil.rmtree(oldest)

    def delete_save(self, slot_name: str) -> Dict:
        """
        Delete a save slot.

        Args:
            slot_name: Name of the save slot to delete
        """
        save_dir = self.saves_dir / slot_name

        if not save_dir.exists():
            return {'success': False, 'error': f'Save not found: {slot_name}'}

        try:
            shutil.rmtree(save_dir)
            return {'success': True, 'deleted': slot_name}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_saves(self) -> List[Dict]:
        """
        List all save slots.

        Returns:
            List of save metadata dicts, sorted by save time
        """
        saves = []

        for save_dir in self.saves_dir.iterdir():
            if not save_dir.is_dir():
                continue
            if save_dir.name.startswith('_'):  # Skip special dirs like _backups
                continue

            meta_file = save_dir / "meta.json"
            if meta_file.exists():
                try:
                    with open(meta_file) as f:
                        meta = json.load(f)
                        meta['slot_name'] = save_dir.name
                        saves.append(meta)
                except Exception:
                    # Include partial info for corrupted saves
                    saves.append({
                        'slot_name': save_dir.name,
                        'error': 'Metadata corrupted'
                    })

        # Sort by save time, newest first
        saves.sort(key=lambda x: x.get('save_time', ''), reverse=True)
        return saves

    def quick_save(self, country_code: str) -> Dict:
        """
        Quick save to a special slot (overwrites previous quick save).
        """
        return self.save_game(country_code, "quicksave", "Quick Save")

    def quick_load(self) -> Dict:
        """
        Load the quick save slot.
        """
        return self.load_game("quicksave")

    def auto_save(self, country_code: str, game_day: int) -> Optional[Dict]:
        """
        Auto-save if interval has passed.

        Called during game tick.
        """
        if not self.auto_save_enabled:
            return None

        if game_day % self.auto_save_interval_days != 0:
            return None

        # Rotate auto-saves
        auto_saves = [
            s for s in self.list_saves()
            if s.get('slot_name', '').startswith('autosave_')
        ]

        # Remove oldest if too many
        while len(auto_saves) >= self.max_auto_saves:
            oldest = auto_saves.pop()
            self.delete_save(oldest['slot_name'])

        # Create new auto-save
        slot_name = f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return self.save_game(country_code, slot_name, f"Auto-save (Day {game_day})")

    def export_save(self, slot_name: str, export_path: Path) -> Dict:
        """
        Export a save to a portable format.

        Args:
            slot_name: Save slot to export
            export_path: Destination path for the export
        """
        save_dir = self.saves_dir / slot_name

        if not save_dir.exists():
            return {'success': False, 'error': f'Save not found: {slot_name}'}

        try:
            # Create a zip archive
            archive_name = export_path / f"{slot_name}_export"
            shutil.make_archive(str(archive_name), 'zip', save_dir)

            return {
                'success': True,
                'exported_to': f"{archive_name}.zip"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def import_save(self, import_path: Path, slot_name: Optional[str] = None) -> Dict:
        """
        Import a save from an exported archive.

        Args:
            import_path: Path to the .zip archive
            slot_name: Name for the imported save (uses archive name if None)
        """
        if not import_path.exists():
            return {'success': False, 'error': f'File not found: {import_path}'}

        if not slot_name:
            slot_name = import_path.stem.replace('_export', '')

        save_dir = self.saves_dir / slot_name

        try:
            # Extract archive
            shutil.unpack_archive(import_path, save_dir)

            return {
                'success': True,
                'imported_as': slot_name
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_game_date(self, country_code: str) -> Dict:
        """Get the current game date from country data."""
        country_file = self.db_dir / "countries" / f"{country_code}.json"

        try:
            with open(country_file) as f:
                data = json.load(f)
                return data.get('meta', {}).get('current_date', {
                    'year': 2024, 'month': 1, 'day': 1
                })
        except Exception:
            return {'year': 2024, 'month': 1, 'day': 1}

    def get_save_details(self, slot_name: str) -> Dict:
        """
        Get detailed information about a save.

        Includes preview of game state.
        """
        save_dir = self.saves_dir / slot_name

        if not save_dir.exists():
            return {'success': False, 'error': f'Save not found: {slot_name}'}

        try:
            # Load metadata
            with open(save_dir / "meta.json") as f:
                meta = json.load(f)

            country_code = meta.get('country_code')

            # Load country data preview
            country_file = save_dir / f"{country_code}.json"
            if country_file.exists():
                with open(country_file) as f:
                    country_data = json.load(f)

                preview = {
                    'country_name': country_data.get('meta', {}).get('full_name'),
                    'game_date': country_data.get('meta', {}).get('current_date'),
                    'gdp': country_data.get('economy', {}).get('gdp_billions_usd'),
                    'population': country_data.get('demographics', {}).get('total_population'),
                    'happiness': country_data.get('indices', {}).get('happiness'),
                    'stability': country_data.get('indices', {}).get('stability')
                }
            else:
                preview = None

            return {
                'success': True,
                'meta': meta,
                'preview': preview
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global save service instance
save_service = SaveService()
