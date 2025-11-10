"""
Competitive Context Collector
Collects entities within their competitive cohorts for relative feature analysis
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class CompetitiveContextCollector:
    """
    Collect entities with competitive cohort context
    Enables relative positioning and market saturation analysis
    """
    
    def __init__(self):
        self.cohort_definitions = self._init_cohort_definitions()
    
    def _init_cohort_definitions(self) -> Dict:
        """
        Define how to group entities into competitive cohorts per domain
        """
        return {
            'adult_film': {
                'cohort_window': 'month',  # Monthly competitive windows
                'grouping_key': 'upload_date',
                'sub_cohorts': ['genre', 'duration_category']  # Further segment by genre
            },
            'crypto': {
                'cohort_window': 'quarter',  # Quarterly launch cohorts
                'grouping_key': 'launch_date',
                'sub_cohorts': ['category', 'chain']  # DeFi/NFT/L1/L2
            },
            'sports': {
                'cohort_window': 'season',  # Same season = competitive cohort
                'grouping_key': 'draft_year',
                'sub_cohorts': ['position', 'team']  # Position groups
            },
            'hurricanes': {
                'cohort_window': 'year',  # Annual storm cohorts
                'grouping_key': 'year',
                'sub_cohorts': ['basin', 'category']  # Atlantic vs Pacific
            },
            'bands': {
                'cohort_window': 'year',  # Album release year
                'grouping_key': 'release_year',
                'sub_cohorts': ['genre', 'country']
            }
        }
    
    def collect_with_cohort(self, 
                           entity_id: str, 
                           domain: str, 
                           entities: List[Dict],
                           time_key: str = None) -> Dict:
        """
        Get entity with its competitive cohort
        
        Args:
            entity_id: The target entity
            domain: Domain name
            entities: All available entities
            time_key: Optional custom time grouping key
        
        Returns:
            {
                'entity': target entity data,
                'cohort': list of competitive entities,
                'cohort_stats': summary statistics,
                'relative_position': calculated relative metrics
            }
        """
        # Find target entity
        entity = next((e for e in entities if e.get('id') == entity_id), None)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")
        
        # Define cohort
        cohort_def = self.cohort_definitions.get(domain, {})
        grouping_key = time_key or cohort_def.get('grouping_key', 'date')
        
        # Get cohort entities
        cohort = self._get_cohort_entities(entity, entities, grouping_key, domain)
        
        # Calculate cohort statistics
        cohort_stats = self._calculate_cohort_stats(cohort)
        
        # Calculate relative position
        relative_position = self._calculate_relative_position(entity, cohort_stats)
        
        return {
            'entity': entity,
            'cohort': cohort,
            'cohort_stats': cohort_stats,
            'relative_position': relative_position,
            'cohort_size': len(cohort),
            'market_saturation': self._estimate_saturation(cohort, entity)
        }
    
    def _get_cohort_entities(self, 
                            entity: Dict, 
                            all_entities: List[Dict],
                            grouping_key: str,
                            domain: str) -> List[Dict]:
        """Get all entities in same competitive cohort"""
        
        entity_time = entity.get(grouping_key)
        
        if not entity_time:
            logger.warning(f"Entity missing {grouping_key}, using all as cohort")
            return all_entities
        
        # Get cohort window
        cohort_def = self.cohort_definitions.get(domain, {})
        window = cohort_def.get('cohort_window', 'year')
        
        # Filter to same window
        cohort = []
        for e in all_entities:
            e_time = e.get(grouping_key)
            if e_time and self._in_same_window(entity_time, e_time, window):
                cohort.append(e)
        
        return cohort
    
    def _in_same_window(self, time1: Any, time2: Any, window: str) -> bool:
        """Check if two times are in same competitive window"""
        
        if window == 'month':
            # Same year and month
            if isinstance(time1, datetime) and isinstance(time2, datetime):
                return time1.year == time2.year and time1.month == time2.month
            return time1 == time2
        
        elif window == 'quarter':
            # Same year and quarter
            if isinstance(time1, datetime) and isinstance(time2, datetime):
                q1 = (time1.year, (time1.month - 1) // 3)
                q2 = (time2.year, (time2.month - 1) // 3)
                return q1 == q2
            return time1 == time2
        
        elif window == 'year':
            # Same year
            if isinstance(time1, datetime) and isinstance(time2, datetime):
                return time1.year == time2.year
            return str(time1)[:4] == str(time2)[:4]
        
        elif window == 'season':
            # Sports season (year for most purposes)
            return self._in_same_window(time1, time2, 'year')
        
        return False
    
    def _calculate_cohort_stats(self, cohort: List[Dict]) -> Dict:
        """Calculate aggregate statistics for cohort"""
        
        if not cohort:
            return {}
        
        # Collect features from cohort
        import numpy as np
        
        stats = {
            'size': len(cohort),
            'mean_outcome': np.mean([e.get('outcome', 0) for e in cohort]),
            'std_outcome': np.std([e.get('outcome', 0) for e in cohort])
        }
        
        # Feature means (for relative calculation)
        feature_keys = ['harshness', 'syllables', 'length', 'memorability']
        for key in feature_keys:
            values = [e.get(key, 0) for e in cohort if key in e]
            if values:
                stats[f'mean_{key}'] = np.mean(values)
                stats[f'std_{key}'] = np.std(values)
        
        return stats
    
    def _calculate_relative_position(self, entity: Dict, cohort_stats: Dict) -> Dict:
        """Calculate entity's relative position vs cohort"""
        
        relative = {}
        
        feature_keys = ['harshness', 'syllables', 'length', 'memorability']
        for key in feature_keys:
            entity_value = entity.get(key, 0)
            cohort_mean = cohort_stats.get(f'mean_{key}', entity_value)
            cohort_std = cohort_stats.get(f'std_{key}', 1.0)
            
            # Relative difference from cohort
            relative[f'relative_{key}'] = entity_value - cohort_mean
            
            # Z-score (standardized position)
            if cohort_std > 0:
                relative[f'zscore_{key}'] = (entity_value - cohort_mean) / cohort_std
            else:
                relative[f'zscore_{key}'] = 0.0
        
        return relative
    
    def _estimate_saturation(self, cohort: List[Dict], entity: Dict) -> float:
        """
        Estimate market saturation (0-1)
        Higher = more crowded narrative space
        """
        if not cohort:
            return 0.5
        
        # Simple heuristic: cohort size relative to maximum
        # In production: would measure feature similarity clustering
        size = len(cohort)
        
        if size < 50:
            return 0.2  # Low saturation
        elif size < 200:
            return 0.5  # Medium
        elif size < 500:
            return 0.7  # High
        else:
            return 0.9  # Very saturated
    
    def batch_collect_with_cohorts(self, 
                                   entities: List[Dict],
                                   domain: str) -> List[Dict]:
        """
        Process all entities and add competitive context to each
        
        Returns:
            List of entities enhanced with cohort context and relative features
        """
        logger.info(f"Processing {len(entities)} entities with competitive context")
        
        # Group into cohorts
        cohort_def = self.cohort_definitions.get(domain, {})
        grouping_key = cohort_def.get('grouping_key', 'date')
        
        cohorts = defaultdict(list)
        for entity in entities:
            cohort_key = self._get_cohort_key(entity, grouping_key, domain)
            cohorts[cohort_key].append(entity)
        
        logger.info(f"Identified {len(cohorts)} cohorts")
        
        # Process each cohort
        enhanced_entities = []
        for cohort_key, cohort_entities in cohorts.items():
            cohort_stats = self._calculate_cohort_stats(cohort_entities)
            
            for entity in cohort_entities:
                # Add relative features
                relative_pos = self._calculate_relative_position(entity, cohort_stats)
                entity['competitive_context'] = {
                    'cohort_key': cohort_key,
                    'cohort_size': len(cohort_entities),
                    'relative_features': relative_pos,
                    'cohort_stats': cohort_stats,
                    'market_saturation': self._estimate_saturation(cohort_entities, entity)
                }
                enhanced_entities.append(entity)
        
        logger.info(f"Enhanced {len(enhanced_entities)} entities with competitive context")
        return enhanced_entities
    
    def _get_cohort_key(self, entity: Dict, grouping_key: str, domain: str) -> str:
        """Generate cohort key for entity"""
        value = entity.get(grouping_key)
        
        if isinstance(value, datetime):
            cohort_def = self.cohort_definitions.get(domain, {})
            window = cohort_def.get('cohort_window', 'year')
            
            if window == 'month':
                return f"{value.year}-{value.month:02d}"
            elif window == 'quarter':
                quarter = (value.month - 1) // 3 + 1
                return f"{value.year}-Q{quarter}"
            elif window == 'year':
                return str(value.year)
        
        return str(value) if value else 'unknown'

