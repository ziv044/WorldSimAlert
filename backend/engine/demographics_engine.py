"""
Demographics Engine - Phase 3

Processes yearly demographic changes: population, age distribution, workforce, education.
"""

from typing import Dict, List


class DemographicsEngine:
    """
    Manages demographic simulation.

    Yearly tick updates:
    - Population growth (births, deaths, migration)
    - Age distribution shifts
    - Working age population
    - Graduate production
    - Expertise pool updates
    """

    def __init__(self, country_data: dict):
        self.data = country_data

    def process_yearly_tick(self) -> Dict:
        """
        Process annual demographic changes.

        Returns:
            Dict of all changes made
        """
        changes = {}

        # 1. Population changes
        pop_changes = self._calculate_population_change()
        changes['population'] = pop_changes

        # 2. Age distribution shift
        age_changes = self._update_age_distribution()
        changes['age_distribution'] = age_changes

        # 3. Update working age population
        labor_changes = self._update_labor_force()
        changes['labor_force'] = labor_changes

        # 4. Process graduates
        grad_changes = self._process_graduates()
        changes['graduates'] = grad_changes

        # 5. Update expertise pools
        pool_changes = self._update_expertise_pools()
        changes['expertise_pools'] = pool_changes

        # 6. Update median age
        self._update_median_age()

        return changes

    def _calculate_population_change(self) -> Dict:
        """
        Calculate population change from births, deaths, and migration.
        """
        demo = self.data.get('demographics', {})
        population = demo.get('total_population', 10_000_000)

        # Birth and death rates per 1000
        birth_rate = demo.get('birth_rate_per_1000', 12)
        death_rate = demo.get('death_rate_per_1000', 6)
        migration_rate = demo.get('net_migration_per_1000', 2)

        births = int(population * birth_rate / 1000)
        deaths = int(population * death_rate / 1000)
        migration = int(population * migration_rate / 1000)

        net_change = births - deaths + migration
        new_population = population + net_change

        # Apply changes
        demo['total_population'] = new_population

        return {
            'births': births,
            'deaths': deaths,
            'migration': migration,
            'net_change': net_change,
            'new_population': new_population,
            'growth_rate': (net_change / population) * 100
        }

    def _update_age_distribution(self) -> Dict:
        """
        Update age cohort distribution.

        Shifts population through age brackets over time.
        """
        demo = self.data.get('demographics', {})
        age_dist = demo.get('age_distribution', {})
        population = demo.get('total_population', 10_000_000)

        # Calculate new distribution based on births, deaths, aging
        birth_rate = demo.get('birth_rate_per_1000', 12)
        new_children = int(population * birth_rate / 1000)

        old_0_14 = age_dist.get('0_14', 0.20)
        old_15_24 = age_dist.get('15_24', 0.15)
        old_25_54 = age_dist.get('25_54', 0.40)
        old_55_64 = age_dist.get('55_64', 0.12)
        old_65_plus = age_dist.get('65_plus', 0.13)

        # Simplified aging model: each year ~1/10 of each cohort moves up
        # (very simplified - real demographics are more complex)
        aging_rate = 0.067  # ~1/15 per year

        # Shift populations
        new_0_14 = old_0_14 * (1 - aging_rate) + (new_children / population)
        new_15_24 = old_15_24 * (1 - aging_rate) + (old_0_14 * aging_rate * 0.7)
        new_25_54 = old_25_54 * (1 - aging_rate * 0.5) + (old_15_24 * aging_rate)
        new_55_64 = old_55_64 * (1 - aging_rate) + (old_25_54 * aging_rate * 0.3)
        new_65_plus = old_65_plus * 0.97 + (old_55_64 * aging_rate)  # 3% mortality

        # Normalize to sum to 1
        total = new_0_14 + new_15_24 + new_25_54 + new_55_64 + new_65_plus
        if total > 0:
            age_dist['0_14'] = new_0_14 / total
            age_dist['15_24'] = new_15_24 / total
            age_dist['25_54'] = new_25_54 / total
            age_dist['55_64'] = new_55_64 / total
            age_dist['65_plus'] = new_65_plus / total

        return {
            'new_distribution': age_dist.copy()
        }

    def _update_labor_force(self) -> Dict:
        """
        Update working age population and labor force.
        """
        demo = self.data.get('demographics', {})
        age_dist = demo.get('age_distribution', {})
        population = demo.get('total_population', 10_000_000)

        # Working age is roughly 15-64
        working_age_percent = (
            age_dist.get('15_24', 0.15) +
            age_dist.get('25_54', 0.40) +
            age_dist.get('55_64', 0.12)
        )
        working_age = int(population * working_age_percent)

        # Labor force participation
        participation = demo.get('labor_force_participation', 0.65)
        active_labor = int(working_age * participation)

        # Apply
        demo['working_age_population'] = working_age
        demo['active_labor_force'] = active_labor

        return {
            'working_age_population': working_age,
            'working_age_percent': working_age_percent * 100,
            'active_labor_force': active_labor,
            'participation_rate': participation * 100
        }

    def _process_graduates(self) -> Dict:
        """
        Process annual graduate production into workforce.
        """
        workforce = self.data.get('workforce', {})
        annual_grads = workforce.get('annual_graduates', {})
        by_education = workforce.get('by_education', {})

        changes = {}

        for level, count in annual_grads.items():
            if level in by_education:
                old_count = by_education[level].get('count', 0)
                by_education[level]['count'] = old_count + count
                changes[level] = {
                    'added': count,
                    'new_total': old_count + count
                }

        return changes

    def _update_expertise_pools(self) -> Dict:
        """
        Update expertise pools based on education and attrition.
        """
        workforce = self.data.get('workforce', {})
        pools = workforce.get('expertise_pools', {})
        annual_grads = workforce.get('annual_graduates', {})

        changes = {}

        # Map education levels to expertise pools (simplified)
        education_to_pool = {
            'bachelors': ['software_engineers', 'civil_engineers', 'scientists'],
            'masters': ['software_engineers', 'aerospace_engineers', 'scientists'],
            'phd': ['scientists', 'aerospace_engineers'],
            'vocational': ['technicians', 'medical_staff'],
        }

        for edu_level, pools_affected in education_to_pool.items():
            grads = annual_grads.get(edu_level, 0)
            grad_per_pool = grads // max(1, len(pools_affected))

            for pool_name in pools_affected:
                if pool_name in pools:
                    pool = pools[pool_name]

                    # Add graduates
                    old_available = pool.get('available', 0)
                    new_available = old_available + grad_per_pool

                    # Apply attrition (retirement, emigration) - about 3% per year
                    attrition = int(old_available * 0.03)
                    new_available = max(0, new_available - attrition)

                    pool['available'] = new_available

                    if pool_name not in changes:
                        changes[pool_name] = {'added': 0, 'attrition': 0}
                    changes[pool_name]['added'] += grad_per_pool
                    changes[pool_name]['attrition'] += attrition

        return changes

    def _update_median_age(self) -> None:
        """
        Update median age based on birth/death rates.
        """
        demo = self.data.get('demographics', {})
        birth_rate = demo.get('birth_rate_per_1000', 12)
        death_rate = demo.get('death_rate_per_1000', 6)

        median_age = demo.get('median_age', 35)

        # If births > deaths, population is getting younger, else older
        if birth_rate > death_rate * 1.5:
            median_age = max(20, median_age - 0.1)
        elif birth_rate < death_rate:
            median_age = min(55, median_age + 0.2)
        else:
            # Slight aging trend in developed countries
            median_age = min(55, median_age + 0.1)

        demo['median_age'] = round(median_age, 1)

    def set_migration_policy(self, policy: str) -> Dict:
        """
        Set immigration policy and adjust migration rate.

        Args:
            policy: 'open', 'moderate', 'closed'

        Returns:
            Dict with new rates and effects
        """
        demo = self.data.get('demographics', {})
        indices = self.data.get('indices', {})

        policy_effects = {
            'open': {
                'migration_rate': 5,
                'workforce_growth': 0.02,
                'stability_change': -3,
                'diversity_change': 5
            },
            'moderate': {
                'migration_rate': 2,
                'workforce_growth': 0.01,
                'stability_change': 0,
                'diversity_change': 2
            },
            'closed': {
                'migration_rate': -1,
                'workforce_growth': -0.005,
                'stability_change': 2,
                'diversity_change': -1
            }
        }

        if policy not in policy_effects:
            return {'error': f'Unknown policy: {policy}'}

        effects = policy_effects[policy]

        # Apply effects
        demo['net_migration_per_1000'] = effects['migration_rate']
        demo['immigration_policy'] = policy

        indices['stability'] = max(0, min(100,
            indices.get('stability', 70) + effects['stability_change']
        ))

        return {
            'policy': policy,
            'effects': effects
        }

    def get_demographic_summary(self) -> Dict:
        """Get summary of current demographic state."""
        demo = self.data.get('demographics', {})
        workforce = self.data.get('workforce', {})

        return {
            'population': demo.get('total_population', 0),
            'median_age': demo.get('median_age', 0),
            'birth_rate': demo.get('birth_rate_per_1000', 0),
            'death_rate': demo.get('death_rate_per_1000', 0),
            'migration_rate': demo.get('net_migration_per_1000', 0),
            'working_age_population': demo.get('working_age_population', 0),
            'labor_force_participation': demo.get('labor_force_participation', 0),
            'unemployment_rate': workforce.get('unemployment_rate', 0),
            'age_distribution': demo.get('age_distribution', {})
        }

    def get_workforce_summary(self) -> Dict:
        """Get summary of workforce state."""
        workforce = self.data.get('workforce', {})

        pools = workforce.get('expertise_pools', {})
        pool_summary = {}
        for name, pool in pools.items():
            pool_summary[name] = {
                'available': pool.get('available', 0),
                'employed': pool.get('employed', 0),
                'free': pool.get('available', 0) - pool.get('employed', 0),
                'quality_index': pool.get('quality_index', 50)
            }

        return {
            'total_workforce': workforce.get('total_workforce', 0),
            'unemployment_rate': workforce.get('unemployment_rate', 0),
            'by_education': workforce.get('by_education', {}),
            'expertise_pools': pool_summary,
            'annual_graduates': workforce.get('annual_graduates', {})
        }
