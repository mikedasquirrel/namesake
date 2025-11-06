"""Demographic Impact Analyzer

Calculates demographic-specific impact rates for hurricanes including:
- Deaths per capita by demographic group
- Displacement rates by demographic
- FEMA application rates by demographic
- Identifies disproportionate impacts across race, income, and age categories

Compares outcomes within same storm across different demographic groups.
"""

import logging
from typing import Dict, List, Optional, Tuple
import json
from collections import defaultdict

import numpy as np
from scipy import stats

from core.models import (
    Hurricane, HurricaneDemographicImpact, HurricaneGeography,
    GeographicDemographics, HurricaneAnalysis, db
)

logger = logging.getLogger(__name__)


class DemographicImpactAnalyzer:
    """Analyze demographic-specific hurricane impacts."""
    
    def __init__(self):
        self.demographic_categories = {
            'race': ['white', 'black', 'asian', 'hispanic_latino', 'native', 'pacific', 'other', 'multiracial'],
            'income_quintile': ['quintile_1', 'quintile_2', 'quintile_3', 'quintile_4', 'quintile_5'],
            'age_group': ['under_18', '18_34', '35_49', '50_64', '65_74', '75_plus']
        }
    
    def analyze_hurricane(self, hurricane_id: str) -> Dict:
        """
        Analyze demographic impacts for a single hurricane.
        
        Args:
            hurricane_id: Hurricane ID
        
        Returns:
            Analysis results dict
        """
        hurricane = Hurricane.query.get(hurricane_id)
        if not hurricane:
            logger.error(f"Hurricane {hurricane_id} not found")
            return {'success': False, 'error': 'Hurricane not found'}
        
        results = {
            'hurricane_id': hurricane_id,
            'hurricane_name': hurricane.name,
            'year': hurricane.year,
            'demographic_analysis': {},
            'disparity_metrics': {},
            'success': False
        }
        
        try:
            # Get all county-level impacts for this hurricane
            county_impacts = HurricaneDemographicImpact.query.filter_by(
                hurricane_id=hurricane_id,
                geographic_level='county'
            ).all()
            
            if not county_impacts:
                logger.warning(f"No demographic impact data for {hurricane.name} ({hurricane.year})")
                results['success'] = True
                return results
            
            # Analyze by each demographic category
            for category in ['race', 'income_quintile', 'age_group']:
                category_analysis = self._analyze_demographic_category(
                    hurricane_id,
                    county_impacts,
                    category
                )
                results['demographic_analysis'][category] = category_analysis
            
            # Calculate disparity metrics
            results['disparity_metrics'] = self._calculate_disparity_metrics(
                results['demographic_analysis']
            )
            
            results['success'] = True
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing demographics for {hurricane_id}: {e}")
            results['error'] = str(e)
            return results
    
    def _analyze_demographic_category(self, hurricane_id: str, 
                                       county_impacts: List, 
                                       category: str) -> Dict:
        """
        Analyze impacts within a specific demographic category.
        
        Args:
            hurricane_id: Hurricane ID
            county_impacts: List of HurricaneDemographicImpact records
            category: 'race', 'income_quintile', or 'age_group'
        
        Returns:
            Category analysis dict
        """
        analysis = {
            'category': category,
            'groups': {},
            'total_population_at_risk': 0,
            'total_deaths': 0,
            'total_displaced': 0,
            'total_fema_applications': 0
        }
        
        # Aggregate data by demographic value within category
        for impact in county_impacts:
            if impact.demographic_category != category:
                continue
            
            demographic_value = impact.demographic_value
            
            if demographic_value not in analysis['groups']:
                analysis['groups'][demographic_value] = {
                    'population_at_risk': 0,
                    'deaths': 0,
                    'injuries': 0,
                    'displaced': 0,
                    'fema_applications': 0,
                    'damage_usd': 0.0,
                    'counties_affected': 0
                }
            
            group = analysis['groups'][demographic_value]
            
            # Aggregate metrics
            group['population_at_risk'] += impact.population_at_risk or 0
            group['deaths'] += impact.deaths or 0
            group['injuries'] += impact.injuries or 0
            group['displaced'] += impact.displaced_persons or 0
            group['fema_applications'] += impact.fema_applications or 0
            group['damage_usd'] += impact.damage_estimate_usd or 0.0
            group['counties_affected'] += 1
            
            # Update totals
            analysis['total_population_at_risk'] += impact.population_at_risk or 0
            analysis['total_deaths'] += impact.deaths or 0
            analysis['total_displaced'] += impact.displaced_persons or 0
            analysis['total_fema_applications'] += impact.fema_applications or 0
        
        # Calculate rates for each group
        for group_name, group_data in analysis['groups'].items():
            pop = group_data['population_at_risk']
            if pop > 0:
                group_data['death_rate_per_1000'] = (group_data['deaths'] / pop) * 1000
                group_data['displacement_rate'] = group_data['displaced'] / pop
                group_data['fema_application_rate'] = group_data['fema_applications'] / pop
                group_data['damage_per_capita'] = group_data['damage_usd'] / pop
            else:
                group_data['death_rate_per_1000'] = None
                group_data['displacement_rate'] = None
                group_data['fema_application_rate'] = None
                group_data['damage_per_capita'] = None
        
        return analysis
    
    def _calculate_disparity_metrics(self, demographic_analysis: Dict) -> Dict:
        """
        Calculate disparity metrics across demographic groups.
        
        Metrics include:
        - Relative risk ratios
        - Disparity indices
        - Statistical significance tests
        
        Args:
            demographic_analysis: Dict of category analyses
        
        Returns:
            Disparity metrics dict
        """
        disparities = {}
        
        for category, analysis in demographic_analysis.items():
            if not analysis or 'groups' not in analysis:
                continue
            
            groups = analysis['groups']
            
            if len(groups) < 2:
                continue
            
            # Calculate rate disparities
            death_rates = {}
            displacement_rates = {}
            fema_rates = {}
            
            for group_name, group_data in groups.items():
                if group_data.get('death_rate_per_1000') is not None:
                    death_rates[group_name] = group_data['death_rate_per_1000']
                if group_data.get('displacement_rate') is not None:
                    displacement_rates[group_name] = group_data['displacement_rate']
                if group_data.get('fema_application_rate') is not None:
                    fema_rates[group_name] = group_data['fema_application_rate']
            
            disparities[category] = {
                'death_rate_disparity': self._calculate_rate_disparity(death_rates),
                'displacement_rate_disparity': self._calculate_rate_disparity(displacement_rates),
                'fema_rate_disparity': self._calculate_rate_disparity(fema_rates)
            }
        
        return disparities
    
    def _calculate_rate_disparity(self, rates: Dict[str, float]) -> Dict:
        """
        Calculate disparity metrics for a set of rates.
        
        Args:
            rates: Dict mapping group names to rates
        
        Returns:
            Disparity metrics dict
        """
        if not rates or len(rates) < 2:
            return {
                'has_data': False,
                'min_rate': None,
                'max_rate': None,
                'range': None,
                'relative_disparity': None,
                'highest_group': None,
                'lowest_group': None
            }
        
        values = list(rates.values())
        min_rate = min(values)
        max_rate = max(values)
        
        # Find which groups have min/max
        highest_group = [k for k, v in rates.items() if v == max_rate][0]
        lowest_group = [k for k, v in rates.items() if v == min_rate][0]
        
        # Relative disparity (ratio of highest to lowest)
        relative_disparity = max_rate / min_rate if min_rate > 0 else None
        
        return {
            'has_data': True,
            'min_rate': min_rate,
            'max_rate': max_rate,
            'range': max_rate - min_rate,
            'relative_disparity': relative_disparity,
            'highest_group': highest_group,
            'lowest_group': lowest_group,
            'group_rates': rates
        }
    
    def compare_across_hurricanes(self, hurricane_ids: List[str]) -> Dict:
        """
        Compare demographic impacts across multiple hurricanes.
        
        Args:
            hurricane_ids: List of hurricane IDs
        
        Returns:
            Comparison results
        """
        comparison = {
            'hurricanes_analyzed': len(hurricane_ids),
            'demographic_patterns': {},
            'consistent_disparities': {},
            'success': False
        }
        
        try:
            # Analyze each hurricane
            hurricane_analyses = []
            for hurricane_id in hurricane_ids:
                analysis = self.analyze_hurricane(hurricane_id)
                if analysis.get('success'):
                    hurricane_analyses.append(analysis)
            
            if not hurricane_analyses:
                logger.warning("No successful hurricane analyses")
                comparison['success'] = True
                return comparison
            
            # Identify consistent patterns
            comparison['consistent_disparities'] = self._identify_consistent_patterns(
                hurricane_analyses
            )
            
            comparison['success'] = True
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing hurricanes: {e}")
            comparison['error'] = str(e)
            return comparison
    
    def _identify_consistent_patterns(self, hurricane_analyses: List[Dict]) -> Dict:
        """
        Identify demographic disparities that appear consistently across hurricanes.
        
        Args:
            hurricane_analyses: List of hurricane analysis results
        
        Returns:
            Consistent patterns dict
        """
        patterns = {
            'race_patterns': [],
            'income_patterns': [],
            'age_patterns': []
        }
        
        # For each category, track which group consistently has highest/lowest impacts
        category_map = {
            'race': 'race_patterns',
            'income_quintile': 'income_patterns',
            'age_group': 'age_patterns'
        }
        
        for category, pattern_key in category_map.items():
            # Track highest/lowest groups across hurricanes
            highest_death_groups = []
            highest_displacement_groups = []
            
            for analysis in hurricane_analyses:
                disparity = analysis.get('disparity_metrics', {}).get(category, {})
                
                death_disp = disparity.get('death_rate_disparity', {})
                if death_disp.get('has_data'):
                    highest_death_groups.append(death_disp.get('highest_group'))
                
                displacement_disp = disparity.get('displacement_rate_disparity', {})
                if displacement_disp.get('has_data'):
                    highest_displacement_groups.append(displacement_disp.get('highest_group'))
            
            # Count occurrences
            if highest_death_groups:
                from collections import Counter
                most_common_death = Counter(highest_death_groups).most_common(1)[0]
                patterns[pattern_key].append({
                    'metric': 'death_rate',
                    'highest_impact_group': most_common_death[0],
                    'frequency': most_common_death[1],
                    'total_hurricanes': len(highest_death_groups),
                    'consistency_pct': (most_common_death[1] / len(highest_death_groups)) * 100
                })
            
            if highest_displacement_groups:
                from collections import Counter
                most_common_displacement = Counter(highest_displacement_groups).most_common(1)[0]
                patterns[pattern_key].append({
                    'metric': 'displacement_rate',
                    'highest_impact_group': most_common_displacement[0],
                    'frequency': most_common_displacement[1],
                    'total_hurricanes': len(highest_displacement_groups),
                    'consistency_pct': (most_common_displacement[1] / len(highest_displacement_groups)) * 100
                })
        
        return patterns
    
    def calculate_impact_scores(self, hurricane_id: str) -> Dict:
        """
        Calculate composite impact scores for each demographic group.
        
        Combines multiple metrics (deaths, displacement, damage) into
        overall impact scores for comparison.
        
        Args:
            hurricane_id: Hurricane ID
        
        Returns:
            Impact scores dict
        """
        analysis = self.analyze_hurricane(hurricane_id)
        
        if not analysis.get('success'):
            return analysis
        
        scores = {}
        
        for category, cat_analysis in analysis.get('demographic_analysis', {}).items():
            scores[category] = {}
            
            for group_name, group_data in cat_analysis.get('groups', {}).items():
                # Composite score based on normalized rates
                death_rate = group_data.get('death_rate_per_1000', 0) or 0
                disp_rate = group_data.get('displacement_rate', 0) or 0
                fema_rate = group_data.get('fema_application_rate', 0) or 0
                
                # Weighted composite (deaths weighted most heavily)
                composite_score = (
                    death_rate * 100 +      # Weight deaths heavily
                    disp_rate * 50 +        # Displacement medium weight
                    fema_rate * 25          # FEMA apps lighter weight
                )
                
                scores[category][group_name] = {
                    'composite_impact_score': composite_score,
                    'death_rate_per_1000': death_rate,
                    'displacement_rate': disp_rate,
                    'fema_application_rate': fema_rate
                }
        
        return {
            'hurricane_id': hurricane_id,
            'impact_scores': scores,
            'success': True
        }

