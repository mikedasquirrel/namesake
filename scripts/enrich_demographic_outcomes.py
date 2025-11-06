"""Demographic Outcomes Enrichment Script

Disaggregates county-level hurricane outcomes to demographic subgroups.
Takes aggregate county data (deaths, displacement, FEMA applications) and
estimates demographic-specific impacts based on population proportions and
known disparities.

Methodology:
1. Start with county-level aggregate outcomes
2. Retrieve census demographic breakdowns for county
3. Proportionally allocate outcomes to demographic groups
4. Apply adjustment factors based on vulnerability literature
5. Create HurricaneDemographicImpact records for each group

Usage:
    python scripts/enrich_demographic_outcomes.py --hurricane AL092005
    python scripts/enrich_demographic_outcomes.py --all
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from core.models import (
    Hurricane, HurricaneDemographicImpact, GeographicDemographics,
    HurricaneGeography, db
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemographicEnricher:
    """Enrich county-level outcomes with demographic breakdowns."""
    
    def __init__(self):
        # Vulnerability adjustment factors (from literature)
        # Values > 1.0 indicate higher vulnerability, < 1.0 lower
        
        # Race/ethnicity adjustments (based on evacuation/impact studies)
        self.race_vulnerability = {
            'white': 0.9,
            'black': 1.3,
            'hispanic_latino': 1.2,
            'asian': 1.0,
            'native': 1.4,
            'pacific': 1.1,
            'other': 1.1,
            'multiracial': 1.0
        }
        
        # Income vulnerability (lower income = higher vulnerability)
        self.income_vulnerability = {
            'quintile_1': 1.5,  # Lowest income
            'quintile_2': 1.3,
            'quintile_3': 1.0,
            'quintile_4': 0.8,
            'quintile_5': 0.6   # Highest income
        }
        
        # Age vulnerability (very young and elderly more vulnerable)
        self.age_vulnerability = {
            'under_18': 1.2,
            '18_34': 0.9,
            '35_49': 0.8,
            '50_64': 1.0,
            '65_74': 1.3,
            '75_plus': 1.6
        }
    
    def enrich_hurricane(self, hurricane_id: str) -> Dict:
        """
        Enrich all counties for a hurricane with demographic breakdowns.
        
        Args:
            hurricane_id: Hurricane ID
        
        Returns:
            Results dict
        """
        results = {
            'hurricane_id': hurricane_id,
            'counties_processed': 0,
            'demographic_records_created': 0,
            'success': False
        }
        
        try:
            with app.app_context():
                hurricane = Hurricane.query.get(hurricane_id)
                if not hurricane:
                    logger.error(f"Hurricane {hurricane_id} not found")
                    results['error'] = 'Hurricane not found'
                    return results
                
                logger.info(f"Enriching demographics for {hurricane.name} ({hurricane.year})")
                
                # Get all county-level aggregate records
                aggregate_records = HurricaneDemographicImpact.query.filter_by(
                    hurricane_id=hurricane_id,
                    geographic_level='county',
                    demographic_category='total',
                    demographic_value='all'
                ).all()
                
                if not aggregate_records:
                    logger.warning(f"No aggregate county data found for {hurricane_id}")
                    results['success'] = True
                    return results
                
                logger.info(f"Found {len(aggregate_records)} counties to disaggregate")
                
                for aggregate in aggregate_records:
                    county_results = self._disaggregate_county(hurricane_id, aggregate)
                    results['counties_processed'] += 1
                    results['demographic_records_created'] += county_results.get('records_created', 0)
                
                db.session.commit()
                
                results['success'] = True
                logger.info(f"✅ Created {results['demographic_records_created']} demographic impact records")
                
        except Exception as e:
            logger.error(f"Error enriching demographics: {e}", exc_info=True)
            db.session.rollback()
            results['error'] = str(e)
        
        return results
    
    def _disaggregate_county(self, hurricane_id: str, aggregate: HurricaneDemographicImpact) -> Dict:
        """
        Disaggregate county-level aggregate data into demographic subgroups.
        
        Args:
            hurricane_id: Hurricane ID
            aggregate: Aggregate HurricaneDemographicImpact record
        
        Returns:
            Results dict
        """
        results = {'records_created': 0}
        
        geographic_code = aggregate.geographic_code
        
        # Get demographics for this county
        demographics = GeographicDemographics.query.filter_by(
            geographic_code=geographic_code,
            geographic_level='county'
        ).order_by(GeographicDemographics.year.desc()).first()
        
        if not demographics:
            logger.warning(f"No demographics found for county {geographic_code}")
            return results
        
        # Disaggregate by race
        race_records = self._disaggregate_by_race(
            hurricane_id, aggregate, demographics
        )
        results['records_created'] += race_records
        
        # Disaggregate by income quintile (if available)
        income_records = self._disaggregate_by_income(
            hurricane_id, aggregate, demographics
        )
        results['records_created'] += income_records
        
        # Disaggregate by age group
        age_records = self._disaggregate_by_age(
            hurricane_id, aggregate, demographics
        )
        results['records_created'] += age_records
        
        return results
    
    def _disaggregate_by_race(self, hurricane_id: str, aggregate: HurricaneDemographicImpact,
                              demographics: GeographicDemographics) -> int:
        """Disaggregate by race/ethnicity."""
        if not demographics.race_breakdown:
            return 0
        
        race_data = json.loads(demographics.race_breakdown)
        total_pop = demographics.total_population or 0
        
        if total_pop == 0:
            return 0
        
        records_created = 0
        
        # Total outcomes to distribute
        total_deaths = aggregate.deaths or 0
        total_displaced = aggregate.displaced_persons or 0
        total_fema = aggregate.fema_applications or 0
        total_damage = aggregate.damage_estimate_usd or 0.0
        
        for race_category, pop_count in race_data.items():
            if pop_count is None or pop_count == 0:
                continue
            
            # Population proportion
            proportion = pop_count / total_pop
            
            # Vulnerability adjustment
            vulnerability = self.race_vulnerability.get(race_category, 1.0)
            
            # Adjusted proportion (proportional to population × vulnerability)
            # Calculate total vulnerability-weighted population for normalization
            total_vuln_weighted = sum(
                (race_data.get(cat, 0) or 0) * self.race_vulnerability.get(cat, 1.0)
                for cat in self.race_vulnerability.keys()
            )
            
            if total_vuln_weighted == 0:
                continue
            
            adjusted_proportion = (pop_count * vulnerability) / total_vuln_weighted
            
            # Allocate outcomes
            deaths = int(total_deaths * adjusted_proportion) if total_deaths else None
            displaced = int(total_displaced * adjusted_proportion) if total_displaced else None
            fema_apps = int(total_fema * adjusted_proportion) if total_fema else None
            damage = total_damage * adjusted_proportion if total_damage else None
            
            # Create record
            self._create_demographic_impact_record(
                hurricane_id=hurricane_id,
                geographic_code=aggregate.geographic_code,
                demographic_category='race',
                demographic_value=race_category,
                population_at_risk=pop_count,
                deaths=deaths,
                displaced=displaced,
                fema_applications=fema_apps,
                damage=damage,
                data_source=f"DISAGGREGATED_FROM_{aggregate.data_source}",
                confidence='low'  # Disaggregated data is estimated
            )
            
            records_created += 1
        
        return records_created
    
    def _disaggregate_by_income(self, hurricane_id: str, aggregate: HurricaneDemographicImpact,
                                 demographics: GeographicDemographics) -> int:
        """Disaggregate by income quintile."""
        if not demographics.income_breakdown:
            return 0
        
        income_data = json.loads(demographics.income_breakdown)
        
        if not income_data:
            # If no quintile data, estimate based on median income and poverty rate
            # This is a simplified estimation
            return 0
        
        total_pop = demographics.total_population or 0
        if total_pop == 0:
            return 0
        
        records_created = 0
        
        total_deaths = aggregate.deaths or 0
        total_displaced = aggregate.displaced_persons or 0
        total_fema = aggregate.fema_applications or 0
        total_damage = aggregate.damage_estimate_usd or 0.0
        
        for quintile, pop_count in income_data.items():
            if pop_count is None or pop_count == 0:
                continue
            
            vulnerability = self.income_vulnerability.get(quintile, 1.0)
            
            # Vulnerability-weighted allocation
            total_vuln_weighted = sum(
                (income_data.get(q, 0) or 0) * self.income_vulnerability.get(q, 1.0)
                for q in self.income_vulnerability.keys()
            )
            
            if total_vuln_weighted == 0:
                continue
            
            adjusted_proportion = (pop_count * vulnerability) / total_vuln_weighted
            
            self._create_demographic_impact_record(
                hurricane_id=hurricane_id,
                geographic_code=aggregate.geographic_code,
                demographic_category='income_quintile',
                demographic_value=quintile,
                population_at_risk=pop_count,
                deaths=int(total_deaths * adjusted_proportion) if total_deaths else None,
                displaced=int(total_displaced * adjusted_proportion) if total_displaced else None,
                fema_applications=int(total_fema * adjusted_proportion) if total_fema else None,
                damage=total_damage * adjusted_proportion if total_damage else None,
                data_source=f"DISAGGREGATED_FROM_{aggregate.data_source}",
                confidence='low'
            )
            
            records_created += 1
        
        return records_created
    
    def _disaggregate_by_age(self, hurricane_id: str, aggregate: HurricaneDemographicImpact,
                             demographics: GeographicDemographics) -> int:
        """Disaggregate by age group."""
        if not demographics.age_breakdown:
            return 0
        
        age_data = json.loads(demographics.age_breakdown)
        
        if not age_data:
            return 0
        
        total_pop = demographics.total_population or 0
        if total_pop == 0:
            return 0
        
        records_created = 0
        
        total_deaths = aggregate.deaths or 0
        total_displaced = aggregate.displaced_persons or 0
        total_fema = aggregate.fema_applications or 0
        total_damage = aggregate.damage_estimate_usd or 0.0
        
        for age_group, pop_count in age_data.items():
            if pop_count is None or pop_count == 0:
                continue
            
            vulnerability = self.age_vulnerability.get(age_group, 1.0)
            
            total_vuln_weighted = sum(
                (age_data.get(ag, 0) or 0) * self.age_vulnerability.get(ag, 1.0)
                for ag in self.age_vulnerability.keys()
            )
            
            if total_vuln_weighted == 0:
                continue
            
            adjusted_proportion = (pop_count * vulnerability) / total_vuln_weighted
            
            self._create_demographic_impact_record(
                hurricane_id=hurricane_id,
                geographic_code=aggregate.geographic_code,
                demographic_category='age_group',
                demographic_value=age_group,
                population_at_risk=pop_count,
                deaths=int(total_deaths * adjusted_proportion) if total_deaths else None,
                displaced=int(total_displaced * adjusted_proportion) if total_displaced else None,
                fema_applications=int(total_fema * adjusted_proportion) if total_fema else None,
                damage=total_damage * adjusted_proportion if total_damage else None,
                data_source=f"DISAGGREGATED_FROM_{aggregate.data_source}",
                confidence='low'
            )
            
            records_created += 1
        
        return records_created
    
    def _create_demographic_impact_record(self, hurricane_id: str, geographic_code: str,
                                          demographic_category: str, demographic_value: str,
                                          population_at_risk: int, deaths: Optional[int],
                                          displaced: Optional[int], fema_applications: Optional[int],
                                          damage: Optional[float], data_source: str,
                                          confidence: str):
        """Create or update a demographic impact record."""
        # Check if record already exists
        existing = HurricaneDemographicImpact.query.filter_by(
            hurricane_id=hurricane_id,
            geographic_code=geographic_code,
            geographic_level='county',
            demographic_category=demographic_category,
            demographic_value=demographic_value
        ).first()
        
        # Calculate rates
        death_rate = (deaths / population_at_risk * 1000) if population_at_risk and deaths else None
        displacement_rate = (displaced / population_at_risk) if population_at_risk and displaced else None
        fema_rate = (fema_applications / population_at_risk) if population_at_risk and fema_applications else None
        
        if existing:
            # Update existing
            existing.population_at_risk = population_at_risk
            existing.deaths = deaths
            existing.displaced_persons = displaced
            existing.fema_applications = fema_applications
            existing.damage_estimate_usd = damage
            existing.death_rate_per_1000 = death_rate
            existing.displacement_rate = displacement_rate
            existing.fema_application_rate = fema_rate
            existing.data_source = data_source
            existing.confidence_level = confidence
        else:
            # Create new
            impact = HurricaneDemographicImpact(
                hurricane_id=hurricane_id,
                geographic_code=geographic_code,
                geographic_level='county',
                demographic_category=demographic_category,
                demographic_value=demographic_value,
                population_at_risk=population_at_risk,
                deaths=deaths,
                displaced_persons=displaced,
                fema_applications=fema_applications,
                damage_estimate_usd=damage,
                death_rate_per_1000=death_rate,
                displacement_rate=displacement_rate,
                fema_application_rate=fema_rate,
                data_source=data_source,
                confidence_level=confidence
            )
            db.session.add(impact)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Disaggregate county outcomes to demographic subgroups'
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--hurricane', type=str, help='Hurricane ID')
    mode_group.add_argument('--all', action='store_true', help='Enrich all hurricanes')
    
    args = parser.parse_args()
    
    enricher = DemographicEnricher()
    
    if args.hurricane:
        results = enricher.enrich_hurricane(args.hurricane)
        print(f"\n✅ Enrichment complete: {results.get('demographic_records_created', 0)} records created")
    
    elif args.all:
        with app.app_context():
            hurricanes = db.session.query(Hurricane.id).join(
                HurricaneDemographicImpact
            ).distinct().all()
            
            total_records = 0
            for (hurricane_id,) in hurricanes:
                logger.info(f"\nEnriching {hurricane_id}")
                results = enricher.enrich_hurricane(hurricane_id)
                total_records += results.get('demographic_records_created', 0)
            
            print(f"\n✅ All enrichment complete: {total_records} total demographic records created")


if __name__ == '__main__':
    main()

