"""
Military service for managing border deployments and personnel.
Handles troop deployment, reserve callups, and threat assessment.
"""
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from backend.config import config
from backend.models.border_deployment import (
    BorderDeploymentZone,
    BorderDeploymentList,
    TroopTransfer,
    DeploymentAlertLevel
)
from backend.models.map import Coordinates
from backend.services.db_service import db_service
from backend.services.map_service import map_service


class MilitaryService:
    """Service for military deployment operations."""

    def __init__(self):
        self.db_path = config.DB_PATH
        self.map_path = self.db_path / "map"
        self._deployments_cache: Dict[str, BorderDeploymentList] = {}
        self._transfers_cache: Dict[str, List[TroopTransfer]] = {}

    def _ensure_map_dir(self):
        """Ensure map directory exists."""
        self.map_path.mkdir(parents=True, exist_ok=True)

    # ==================== Deployments ====================

    def load_deployments(self, country_code: str) -> BorderDeploymentList:
        """Load border deployment zones for a country."""
        if country_code in self._deployments_cache:
            return self._deployments_cache[country_code]

        file_path = self.map_path / f"deployments_{country_code.upper()}.json"
        if not file_path.exists():
            # Initialize from border data if no deployments exist
            return self.initialize_from_borders(country_code)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        zones = []
        for zone_data in data.get("zones", []):
            zone_data["center"] = Coordinates(**zone_data["center"])
            zone_data["alert_level"] = DeploymentAlertLevel(
                zone_data.get("alert_level", "peacetime")
            )
            if zone_data.get("last_incident"):
                zone_data["last_incident"] = datetime.fromisoformat(zone_data["last_incident"])
            zones.append(BorderDeploymentZone(**zone_data))

        deployment_list = BorderDeploymentList(
            country_code=country_code,
            zones=zones,
            total_active_deployed=data.get("total_active_deployed", 0),
            total_reserves_deployed=data.get("total_reserves_deployed", 0)
        )
        self._deployments_cache[country_code] = deployment_list
        return deployment_list

    def save_deployments(self, deployments: BorderDeploymentList) -> None:
        """Save border deployment zones."""
        self._ensure_map_dir()
        file_path = self.map_path / f"deployments_{deployments.country_code.upper()}.json"

        # Recalculate totals
        deployments.recalculate_totals()

        data = {
            "country_code": deployments.country_code,
            "zones": [zone.model_dump() for zone in deployments.zones],
            "total_active_deployed": deployments.total_active_deployed,
            "total_reserves_deployed": deployments.total_reserves_deployed
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self._deployments_cache[deployments.country_code] = deployments

    def initialize_from_borders(self, country_code: str) -> BorderDeploymentList:
        """Create default deployment zones from border data."""
        neighbor_data = map_service.get_neighbor_data(country_code)
        zones = []

        for neighbor in neighbor_data:
            neighbor_code = neighbor["country_code"]
            relation_status = neighbor.get("relation_status", "neutral")

            # Calculate threat level based on relation
            threat_level = self._calculate_threat_from_relation(relation_status)

            # Set alert level based on threat
            if threat_level >= 75:
                alert_level = DeploymentAlertLevel.HIGH_ALERT
            elif threat_level >= 50:
                alert_level = DeploymentAlertLevel.ELEVATED
            else:
                alert_level = DeploymentAlertLevel.PEACETIME

            # Estimate border center (midpoint between countries)
            borders = map_service.load_borders(country_code)
            neighbor_center = Coordinates(
                lat=neighbor["center"]["lat"],
                lng=neighbor["center"]["lng"]
            )

            if borders:
                # Calculate border midpoint
                center = Coordinates(
                    lat=(borders.center.lat + neighbor_center.lat) / 2,
                    lng=(borders.center.lng + neighbor_center.lng) / 2
                )
            else:
                center = neighbor_center

            zone = BorderDeploymentZone(
                id=f"bdz_{country_code}_{neighbor_code}",
                country_code=country_code,
                neighbor_code=neighbor_code,
                name=f"Border - {neighbor['name']}",
                center=center,
                border_length_km=50.0,  # Default estimate
                active_troops=1000,
                alert_level=alert_level,
                threat_level=threat_level,
                readiness_percent=75.0
            )
            zones.append(zone)

        deployment_list = BorderDeploymentList(
            country_code=country_code,
            zones=zones
        )
        deployment_list.recalculate_totals()

        # Save the initialized data
        self.save_deployments(deployment_list)
        return deployment_list

    def _calculate_threat_from_relation(self, relation_status: str) -> int:
        """Calculate threat level from relation status."""
        threat_map = {
            "hostile": 80,
            "conflict": 70,
            "tense": 50,
            "neutral": 30,
            "friendly": 15,
            "peace": 10,
            "ally": 5
        }
        return threat_map.get(relation_status.lower(), 30)

    # ==================== Troop Management ====================

    def deploy_troops(
        self,
        country_code: str,
        zone_id: str,
        active_troops: int = 0,
        reserve_troops: int = 0
    ) -> Dict[str, Any]:
        """Deploy troops to a border zone."""
        deployments = self.load_deployments(country_code)
        zone = deployments.get_by_id(zone_id)

        if not zone:
            return {"success": False, "error": f"Zone {zone_id} not found"}

        # Load country data to check available troops
        country_data = db_service.load_country(country_code)
        personnel = country_data.get("military", {}).get("personnel", {})

        available_active = personnel.get("active_duty", 0) - personnel.get("deployed_to_borders", 0)
        available_reserves = personnel.get("reserves_called", 0) - deployments.total_reserves_deployed

        # Validate active troops
        if active_troops > 0:
            if active_troops > available_active:
                return {
                    "success": False,
                    "error": f"Not enough active troops. Available: {available_active}"
                }
            if not zone.can_deploy(active_troops):
                return {
                    "success": False,
                    "error": f"Zone at capacity. Max: {zone.max_capacity}, Current: {zone.total_troops}"
                }

        # Validate reserve troops
        if reserve_troops > 0:
            if reserve_troops > available_reserves:
                return {
                    "success": False,
                    "error": f"Not enough called reserves. Available: {available_reserves}"
                }
            if not zone.can_deploy(active_troops + reserve_troops):
                return {
                    "success": False,
                    "error": f"Zone at capacity"
                }

        # Apply changes
        zone.active_troops += active_troops
        zone.reserve_troops += reserve_troops

        # Update country personnel tracking
        personnel["deployed_to_borders"] = personnel.get("deployed_to_borders", 0) + active_troops
        country_data["military"]["personnel"] = personnel
        db_service.save_country(country_code, country_data)

        # Save deployments
        self.save_deployments(deployments)

        return {
            "success": True,
            "zone_id": zone_id,
            "active_troops": zone.active_troops,
            "reserve_troops": zone.reserve_troops,
            "total_troops": zone.total_troops
        }

    def withdraw_troops(
        self,
        country_code: str,
        zone_id: str,
        active_troops: int = 0,
        reserve_troops: int = 0
    ) -> Dict[str, Any]:
        """Withdraw troops from a border zone."""
        deployments = self.load_deployments(country_code)
        zone = deployments.get_by_id(zone_id)

        if not zone:
            return {"success": False, "error": f"Zone {zone_id} not found"}

        # Validate
        if active_troops > zone.active_troops:
            return {"success": False, "error": "Cannot withdraw more active troops than deployed"}
        if reserve_troops > zone.reserve_troops:
            return {"success": False, "error": "Cannot withdraw more reserves than deployed"}

        # Apply changes
        zone.active_troops -= active_troops
        zone.reserve_troops -= reserve_troops

        # Update country personnel tracking
        country_data = db_service.load_country(country_code)
        personnel = country_data.get("military", {}).get("personnel", {})
        personnel["deployed_to_borders"] = max(0, personnel.get("deployed_to_borders", 0) - active_troops)
        country_data["military"]["personnel"] = personnel
        db_service.save_country(country_code, country_data)

        self.save_deployments(deployments)

        return {
            "success": True,
            "zone_id": zone_id,
            "active_troops": zone.active_troops,
            "reserve_troops": zone.reserve_troops
        }

    # ==================== Reserve Management ====================

    def callup_reserves(
        self,
        country_code: str,
        count: int,
        zone_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call up reserve personnel."""
        country_data = db_service.load_country(country_code)
        personnel = country_data.get("military", {}).get("personnel", {})

        total_reserves = personnel.get("reserves", 0)
        currently_called = personnel.get("reserves_called", 0)
        available = total_reserves - currently_called

        # Max 50% of reserves can be called at once
        max_callup = int(total_reserves * 0.5) - currently_called

        if count > available:
            return {
                "success": False,
                "error": f"Not enough reserves. Available: {available}"
            }

        if count > max_callup:
            return {
                "success": False,
                "error": f"Cannot call up more than 50% of reserves. Max additional: {max_callup}"
            }

        # Update called reserves
        personnel["reserves_called"] = currently_called + count
        country_data["military"]["personnel"] = personnel
        db_service.save_country(country_code, country_data)

        result = {
            "success": True,
            "called_up": count,
            "total_reserves_called": personnel["reserves_called"],
            "remaining_available": total_reserves - personnel["reserves_called"]
        }

        # If zone specified, deploy directly
        if zone_id:
            deploy_result = self.deploy_troops(
                country_code, zone_id,
                active_troops=0, reserve_troops=count
            )
            result["deployed_to_zone"] = zone_id
            result["deploy_result"] = deploy_result

        return result

    def stand_down_reserves(self, country_code: str, count: int) -> Dict[str, Any]:
        """Release reserve personnel back to civilian status."""
        deployments = self.load_deployments(country_code)
        country_data = db_service.load_country(country_code)
        personnel = country_data.get("military", {}).get("personnel", {})

        currently_called = personnel.get("reserves_called", 0)
        deployed_reserves = deployments.total_reserves_deployed

        # Can only stand down undeployed reserves
        available_to_stand_down = currently_called - deployed_reserves

        if count > available_to_stand_down:
            return {
                "success": False,
                "error": f"Cannot stand down deployed reserves. Available: {available_to_stand_down}"
            }

        personnel["reserves_called"] = currently_called - count
        country_data["military"]["personnel"] = personnel
        db_service.save_country(country_code, country_data)

        return {
            "success": True,
            "stood_down": count,
            "remaining_called": personnel["reserves_called"]
        }

    # ==================== Alert Level ====================

    def set_alert_level(
        self,
        country_code: str,
        zone_id: str,
        alert_level: str
    ) -> Dict[str, Any]:
        """Set alert level for a border zone."""
        deployments = self.load_deployments(country_code)
        zone = deployments.get_by_id(zone_id)

        if not zone:
            return {"success": False, "error": f"Zone {zone_id} not found"}

        try:
            new_level = DeploymentAlertLevel(alert_level)
        except ValueError:
            valid = [a.value for a in DeploymentAlertLevel]
            return {"success": False, "error": f"Invalid alert level. Valid: {valid}"}

        old_level = zone.alert_level
        zone.alert_level = new_level
        self.save_deployments(deployments)

        return {
            "success": True,
            "zone_id": zone_id,
            "old_level": old_level.value,
            "new_level": new_level.value
        }

    # ==================== Personnel Status ====================

    def get_personnel_status(self, country_code: str) -> Dict[str, Any]:
        """Get overall personnel deployment status."""
        country_data = db_service.load_country(country_code)
        personnel = country_data.get("military", {}).get("personnel", {})
        deployments = self.load_deployments(country_code)

        active_duty = personnel.get("active_duty", 0)
        reserves = personnel.get("reserves", 0)
        reserves_called = personnel.get("reserves_called", 0)
        deployed_to_borders = personnel.get("deployed_to_borders", 0)

        return {
            "active_duty": {
                "total": active_duty,
                "deployed_to_borders": deployed_to_borders,
                "available": active_duty - deployed_to_borders
            },
            "reserves": {
                "total": reserves,
                "called": reserves_called,
                "deployed": deployments.total_reserves_deployed,
                "available_to_call": reserves - reserves_called,
                "available_to_deploy": reserves_called - deployments.total_reserves_deployed
            },
            "border_summary": {
                "total_zones": len(deployments.zones),
                "total_active": deployments.total_active_deployed,
                "total_reserves": deployments.total_reserves_deployed,
                "high_threat_zones": len(deployments.get_high_threat(50))
            }
        }

    # ==================== Threat Assessment ====================

    def calculate_threat_levels(self, country_code: str) -> None:
        """Update threat levels for all zones based on relations."""
        deployments = self.load_deployments(country_code)
        neighbor_data = map_service.get_neighbor_data(country_code)

        # Create lookup for neighbor relations
        relation_map = {n["country_code"]: n.get("relation_status", "neutral")
                        for n in neighbor_data}

        for zone in deployments.zones:
            relation = relation_map.get(zone.neighbor_code, "neutral")
            zone.threat_level = self._calculate_threat_from_relation(relation)

        self.save_deployments(deployments)

    def clear_cache(self, country_code: Optional[str] = None) -> None:
        """Clear cached data."""
        if country_code:
            self._deployments_cache.pop(country_code, None)
            self._transfers_cache.pop(country_code, None)
        else:
            self._deployments_cache.clear()
            self._transfers_cache.clear()


# Singleton instance
military_service = MilitaryService()
