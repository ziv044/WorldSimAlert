"""
Sector Engine - Phase 5

Allows player to invest in economic sectors and manage development projects.
"""

from typing import Dict, List, Optional
from backend.engine.constraint_engine import ConstraintEngine


class SectorEngine:
    """
    Manages sector development and investment.

    Player actions:
    - Invest in sectors to increase level
    - Start infrastructure projects
    - Track project progress
    """

    # Sector definitions with requirements
    SECTOR_REQUIREMENTS = {
        'technology': {
            'workforce': {'software_engineers': 5000, 'scientists': 1000},
            'infrastructure': {'digital.internet_penetration': 70},
            'cost_per_level': 0.5  # Billions per level
        },
        'finance': {
            'workforce': {'financial_analysts': 2000},
            'infrastructure': {'digital.internet_penetration': 80},
            'cost_per_level': 0.3
        },
        'manufacturing': {
            'workforce': {'technicians': 10000, 'civil_engineers': 2000},
            'infrastructure': {'industrial.manufacturing_capacity': 60},
            'cost_per_level': 0.8
        },
        'agriculture': {
            'workforce': {},  # No specialized workforce needed
            'infrastructure': {'water.agricultural_capacity': 50},
            'cost_per_level': 0.2
        },
        'tourism': {
            'workforce': {},
            'infrastructure': {'transport.airports': 3},
            'cost_per_level': 0.3
        },
        'healthcare_sector': {
            'workforce': {'medical_staff': 5000},
            'infrastructure': {'healthcare.hospitals': 50},
            'cost_per_level': 0.6
        },
        'construction': {
            'workforce': {'civil_engineers': 3000, 'technicians': 5000},
            'infrastructure': {},
            'cost_per_level': 0.4
        },
        'defense_industry': {
            'workforce': {'aerospace_engineers': 2000, 'scientists': 1000},
            'infrastructure': {'industrial.manufacturing_capacity': 70},
            'cost_per_level': 1.0
        },
        'energy': {
            'workforce': {'civil_engineers': 2000},
            'infrastructure': {},
            'cost_per_level': 0.7
        },
        'retail': {
            'workforce': {},
            'infrastructure': {'transport.quality_index': 50},
            'cost_per_level': 0.2
        }
    }

    # Infrastructure project types
    INFRASTRUCTURE_PROJECTS = {
        'power_plant': {
            'cost': 5.0,
            'duration_quarters': 12,
            'effects': {'energy.total_capacity_gw': 2.0, 'energy.renewable_percent': 5}
        },
        'highway': {
            'cost': 2.0,
            'duration_quarters': 8,
            'effects': {'transport.highway_km': 100, 'transport.quality_index': 5}
        },
        'port': {
            'cost': 4.0,
            'duration_quarters': 16,
            'effects': {'transport.ports': 1}
        },
        'airport': {
            'cost': 3.0,
            'duration_quarters': 12,
            'effects': {'transport.airports': 1}
        },
        'university': {
            'cost': 1.0,
            'duration_quarters': 8,
            'effects': {'education.universities': 1}
        },
        'hospital': {
            'cost': 0.5,
            'duration_quarters': 4,
            'effects': {'healthcare.hospitals': 1, 'healthcare.beds_per_1000': 0.2}
        },
        'military_factory': {
            'cost': 3.0,
            'duration_quarters': 12,
            'effects': {'industrial.military_production_capability': True}
        },
        'research_center': {
            'cost': 2.0,
            'duration_quarters': 8,
            'effects': {'education.research_centers': 1}
        },
        'data_center': {
            'cost': 1.5,
            'duration_quarters': 6,
            'effects': {'digital.data_center_capacity': 10}
        },
        'desalination_plant': {
            'cost': 1.0,
            'duration_quarters': 6,
            'effects': {'water.desalination_capacity': 100}  # Million cubic meters
        }
    }

    def __init__(self, country_data: dict):
        self.data = country_data
        self.constraint_engine = ConstraintEngine(country_data)

    def invest_in_sector(
        self,
        sector_name: str,
        investment_billions: float,
        target_improvement: int = 5
    ) -> Dict:
        """
        Start a sector improvement project.

        Args:
            sector_name: Name of sector to invest in
            investment_billions: Amount to invest
            target_improvement: Level points to gain (default 5)

        Returns:
            Dict with success status and project details
        """
        sectors = self.data.get('sectors', {})

        if sector_name not in sectors:
            return {'success': False, 'error': f'Unknown sector: {sector_name}'}

        sector = sectors[sector_name]
        current_level = sector.get('level', 50)

        if current_level >= 100:
            return {'success': False, 'error': f'{sector_name} already at maximum level'}

        # Get sector requirements
        requirements = self.SECTOR_REQUIREMENTS.get(sector_name, {})

        # Build constraints
        constraints = {
            'budget': {
                'amount_billions': investment_billions,
                'budget_category': 'development'
            }
        }

        if requirements.get('workforce'):
            constraints['workforce'] = requirements['workforce']

        if requirements.get('infrastructure'):
            constraints['infrastructure'] = requirements['infrastructure']

        # Check constraints
        can_invest, results = self.constraint_engine.check_all(constraints)

        if not can_invest:
            failed = [r for r in results if not r.satisfied]
            return {
                'success': False,
                'error': 'Constraints not met',
                'failed_constraints': [r.to_dict() for r in failed]
            }

        # Calculate project duration
        cost_per_level = requirements.get('cost_per_level', 0.5)
        efficiency = investment_billions / (cost_per_level * target_improvement)
        base_quarters = 4
        time_quarters = max(2, int(base_quarters / max(0.5, efficiency)))

        # Adjust improvement based on investment efficiency
        actual_improvement = min(
            target_improvement,
            int(investment_billions / cost_per_level),
            100 - current_level  # Can't go above 100
        )

        # Create project
        current_date = self.data.get('meta', {}).get('current_date', {})
        project = {
            'id': f"sector_{sector_name}_{current_date.get('year', 2024)}_{current_date.get('month', 1)}",
            'type': 'sector_development',
            'sector': sector_name,
            'investment': investment_billions,
            'target_improvement': actual_improvement,
            'start_date': current_date.copy(),
            'duration_quarters': time_quarters,
            'quarters_remaining': time_quarters,
            'status': 'in_progress'
        }

        # Add to active projects
        if 'active_projects' not in self.data:
            self.data['active_projects'] = []
        self.data['active_projects'].append(project)

        # Deduct from development budget
        self._deduct_budget(investment_billions)

        # Mark investment in sector
        sector['recent_investment'] = sector.get('recent_investment', 0) + investment_billions

        return {
            'success': True,
            'project': project,
            'expected_completion': f"{time_quarters} quarters",
            'expected_new_level': current_level + actual_improvement
        }

    def start_infrastructure_project(
        self,
        project_type: str,
        custom_name: Optional[str] = None
    ) -> Dict:
        """
        Start an infrastructure construction project.

        Args:
            project_type: Type from INFRASTRUCTURE_PROJECTS
            custom_name: Optional custom name for the project
        """
        if project_type not in self.INFRASTRUCTURE_PROJECTS:
            return {
                'success': False,
                'error': f'Unknown project type: {project_type}',
                'available_types': list(self.INFRASTRUCTURE_PROJECTS.keys())
            }

        project_def = self.INFRASTRUCTURE_PROJECTS[project_type]
        cost = project_def['cost']

        # Check budget
        budget_result = self.constraint_engine.check_budget(cost, 'infrastructure')
        if not budget_result.satisfied:
            return {
                'success': False,
                'error': budget_result.message
            }

        # Create project
        current_date = self.data.get('meta', {}).get('current_date', {})
        project = {
            'id': f"infra_{project_type}_{current_date.get('year', 2024)}_{current_date.get('month', 1)}",
            'type': 'infrastructure',
            'subtype': project_type,
            'name': custom_name or project_type.replace('_', ' ').title(),
            'cost': cost,
            'effects': project_def['effects'],
            'start_date': current_date.copy(),
            'duration_quarters': project_def['duration_quarters'],
            'quarters_remaining': project_def['duration_quarters'],
            'status': 'in_progress'
        }

        # Add to active projects
        if 'active_projects' not in self.data:
            self.data['active_projects'] = []
        self.data['active_projects'].append(project)

        # Deduct budget
        self._deduct_budget(cost)

        return {
            'success': True,
            'project': project
        }

    def process_quarterly_progress(self) -> List[Dict]:
        """
        Process quarterly progress on all active projects.

        Returns:
            List of completed projects
        """
        completed = []
        projects = self.data.get('active_projects', [])

        for project in projects:
            if project.get('status') != 'in_progress':
                continue

            project['quarters_remaining'] -= 1

            if project['quarters_remaining'] <= 0:
                # Complete the project
                if project['type'] == 'sector_development':
                    self._complete_sector_project(project)
                elif project['type'] == 'infrastructure':
                    self._complete_infrastructure_project(project)

                project['status'] = 'completed'
                completed.append(project)

        # Remove completed projects from active list
        self.data['active_projects'] = [
            p for p in projects if p.get('status') != 'completed'
        ]

        return completed

    def _complete_sector_project(self, project: Dict) -> None:
        """Apply effects of completed sector development."""
        sector_name = project['sector']
        improvement = project['target_improvement']

        sectors = self.data.get('sectors', {})
        if sector_name in sectors:
            sector = sectors[sector_name]
            sector['level'] = min(100, sector.get('level', 50) + improvement)

            # Increase GDP contribution proportionally
            gdp_contribution = sector.get('gdp_contribution_billions', 10)
            sector['gdp_contribution_billions'] = gdp_contribution * (1 + improvement * 0.02)

            # Increase employment
            employment = sector.get('employment', 100000)
            sector['employment'] = int(employment * (1 + improvement * 0.01))

    def _complete_infrastructure_project(self, project: Dict) -> None:
        """Apply effects of completed infrastructure project."""
        effects = project.get('effects', {})
        infrastructure = self.data.get('infrastructure', {})

        for path, value in effects.items():
            self._apply_nested_value(infrastructure, path, value)

    def _apply_nested_value(self, data: dict, path: str, value) -> None:
        """Apply a value to a nested dictionary path."""
        keys = path.split('.')
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        final_key = keys[-1]
        if isinstance(value, bool):
            current[final_key] = value
        elif final_key in current:
            current[final_key] = current[final_key] + value
        else:
            current[final_key] = value

    def _deduct_budget(self, amount: float) -> None:
        """Deduct amount from development budget."""
        budget = self.data.get('budget', {})
        allocation = budget.get('allocation', {})

        # Try infrastructure budget first
        if 'infrastructure' in allocation:
            infra = allocation['infrastructure']
            if infra.get('amount', 0) >= amount:
                infra['amount'] -= amount
                return

        # Fallback to general expenditure increase
        budget['total_expenditure_billions'] = (
            budget.get('total_expenditure_billions', 100) + amount
        )

    def get_sector_summary(self, sector_name: Optional[str] = None) -> Dict:
        """Get summary of sector(s)."""
        sectors = self.data.get('sectors', {})

        if sector_name:
            if sector_name not in sectors:
                return {'error': f'Unknown sector: {sector_name}'}
            sector = sectors[sector_name]
            return {
                'name': sector_name,
                'level': sector.get('level', 50),
                'gdp_contribution': sector.get('gdp_contribution_billions', 0),
                'employment': sector.get('employment', 0),
                'growth_rate': sector.get('growth_rate', 0),
                'requirements': self.SECTOR_REQUIREMENTS.get(sector_name, {})
            }

        return {
            name: {
                'level': s.get('level', 50),
                'gdp_contribution': s.get('gdp_contribution_billions', 0),
                'employment': s.get('employment', 0)
            }
            for name, s in sectors.items()
        }

    def get_active_projects(self) -> List[Dict]:
        """Get list of active projects."""
        projects = []
        for p in self.data.get('active_projects', []):
            duration = max(1, p.get('duration_quarters', 1))
            remaining = p.get('quarters_remaining', 0)
            progress = int((1 - remaining / duration) * 100)

            projects.append({
                'id': p.get('id'),
                'project_type': p.get('subtype') or p.get('type'),
                'type': p.get('type'),
                'name': p.get('name') or p.get('sector'),
                'quarters_remaining': remaining,
                'total_duration': duration,
                'progress': progress,
                'progress_percent': progress,
                'eta': f"{remaining} quarters",
                'status': p.get('status')
            })
        return projects

    def cancel_project(self, project_id: str) -> Dict:
        """
        Cancel an active project.

        No refund is given.
        """
        projects = self.data.get('active_projects', [])

        for i, project in enumerate(projects):
            if project.get('id') == project_id:
                if project.get('status') == 'in_progress':
                    project['status'] = 'cancelled'
                    self.data['active_projects'] = [
                        p for p in projects if p.get('id') != project_id
                    ]
                    return {
                        'success': True,
                        'cancelled_project': project,
                        'note': 'No refund for cancelled projects'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Project already {project.get("status")}'
                    }

        return {'success': False, 'error': f'Project not found: {project_id}'}
