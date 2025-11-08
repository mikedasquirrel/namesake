"""
Deep Recursive Tracker

Tracks deep recursive patterns WITHOUT forcing them:
- Selection force names (if available in data)
- Warning label text effects (if applicable)
- Gravity reversal as domains accumulate
- Emergent shape formation
- Semi-artificial selection indicators

Makes these analyses POSSIBLE without requiring them.
Data speaks for itself.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RecursiveContext:
    """Optional recursive context for any entity"""
    
    # Selection force (if applicable)
    selection_mechanism_name: Optional[str] = None
    selection_formality: Optional[float] = None
    selection_gravity_type: Optional[str] = None
    
    # Warning/label text (if applicable)
    label_text: Optional[str] = None
    contains_power_words: Optional[List[str]] = None  # "addictive", "dangerous", etc.
    
    # Hierarchical position
    parent_category_name: Optional[str] = None
    subcategory_name: Optional[str] = None
    
    # Temporal
    era_name: Optional[str] = None  # "Modern Era", "Golden Age", etc.
    
    # Alternative namings (what else could this be called?)
    alternative_names: Optional[List[str]] = None


@dataclass
class DomainAccumulationState:
    """Tracks state as domains accumulate"""
    n_domains: int
    current_correlation_strength: float
    correlation_trend: str  # 'increasing', 'plateauing', 'decreasing', 'reversing'
    
    # Gravity state
    gravity_phase: str  # 'normal', 'peak', 'declining', 'anti'
    suspected_threshold: Optional[int] = None  # Domain count where reversal suspected
    
    # Shape emergence
    visible_dimensionality: int
    shape_clarity: float  # 0-1, how clear is emergent shape?
    suspected_shape: Optional[str] = None


class DeepRecursiveTracker:
    """
    Tracks deep recursive patterns as they naturally emerge
    
    Philosophy: Don't impose patterns, but make them detectable if present
    """
    
    def __init__(self):
        self.history_file = Path('analysis_outputs/recursive_history.json')
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load historical tracking data"""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return {
            'domain_accumulation': [],
            'correlation_by_domain_count': [],
            'dimensionality_by_domain_count': [],
            'selection_forces': {},
            'power_words': {},
        }
    
    def track_analysis_run(self, n_domains: int, overall_correlation: float,
                          dimensionality: int, meta_results: Dict):
        """
        Track this analysis run for longitudinal patterns
        
        This builds the data to detect:
        - Gravity reversal (correlation vs domain count)
        - Shape emergence (dimensionality collapse)
        - Threshold effects
        """
        # Record this run
        self.history['domain_accumulation'].append({
            'n_domains': n_domains,
            'correlation': overall_correlation,
            'dimensionality': dimensionality,
            'timestamp': meta_results.get('timestamp', 'unknown')
        })
        
        # Check for gravity reversal
        gravity_state = self._detect_gravity_state()
        
        # Check for shape emergence
        shape_state = self._detect_shape_emergence()
        
        # Save
        self._save_history()
        
        return {
            'gravity_state': gravity_state,
            'shape_state': shape_state
        }
    
    def _detect_gravity_state(self) -> Dict:
        """Detect if gravity is normal, reversing, or anti"""
        
        if len(self.history['correlation_by_domain_count']) < 3:
            return {'phase': 'insufficient_data'}
        
        # Get recent correlations
        recent = self.history['correlation_by_domain_count'][-5:]
        
        # Calculate trend
        if len(recent) >= 3:
            correlations = [r['correlation'] for r in recent]
            
            # Linear fit
            x = np.arange(len(correlations))
            slope, intercept = np.polyfit(x, correlations, 1)
            
            if slope > 0.01:
                phase = 'normal'  # Increasing
                trend = 'increasing'
            elif slope < -0.01:
                phase = 'declining'  # Decreasing - possible reversal
                trend = 'decreasing'
            else:
                phase = 'plateau'
                trend = 'plateauing'
            
            return {
                'phase': phase,
                'trend': trend,
                'slope': float(slope),
                'recent_correlations': correlations,
                'interpretation': self._interpret_gravity_phase(phase, slope)
            }
        
        return {'phase': 'unknown'}
    
    def _interpret_gravity_phase(self, phase: str, slope: float) -> str:
        """Interpret gravity phase"""
        if phase == 'declining' and slope < -0.02:
            return "⚠️  GRAVITY REVERSAL SUSPECTED: Correlations declining as domains added. " \
                   "May be approaching threshold where nominative forces flip direction."
        elif phase == 'plateau':
            return "Reached gravity equilibrium. Adding domains doesn't strengthen pattern."
        elif phase == 'normal':
            return "Normal gravity. Patterns strengthen with more domains."
        else:
            return "Unknown gravity state."
    
    def _detect_shape_emergence(self) -> Dict:
        """Detect if geometric shape is emerging as domains accumulate"""
        
        dim_history = self.history['dimensionality_by_domain_count']
        
        if len(dim_history) < 3:
            return {'emerging': False, 'reason': 'insufficient_data'}
        
        # Track dimensionality over time
        recent_dims = [d['dimensionality'] for d in dim_history[-5:]]
        
        # Is dimensionality collapsing? (sign of shape emergence)
        if len(recent_dims) >= 3:
            if recent_dims[-1] < recent_dims[0]:
                # Dimensionality is DECREASING
                clarity = (recent_dims[0] - recent_dims[-1]) / recent_dims[0]
                
                if clarity > 0.3:  # 30%+ collapse
                    return {
                        'emerging': True,
                        'clarity': clarity,
                        'current_dimensionality': recent_dims[-1],
                        'interpretation': f"🔥 SHAPE EMERGENCE DETECTED: " \
                                        f"Dimensionality collapsing from {recent_dims[0]} to {recent_dims[-1]}. " \
                                        f"Universal form becoming visible."
                    }
        
        return {'emerging': False, 'dimensionality_stable': True}
    
    def track_selection_force(self, domain: str, mechanism_name: str, 
                             mechanism_properties: Dict):
        """Track selection force for a domain (optional)"""
        
        if domain not in self.history['selection_forces']:
            self.history['selection_forces'][domain] = []
        
        self.history['selection_forces'][domain].append({
            'mechanism': mechanism_name,
            'properties': mechanism_properties,
            'tracked_date': 'now'
        })
        
        self._save_history()
    
    def track_power_word(self, word: str, context: str, observed_effect: float):
        """Track powerful words (like 'addictive') if found in data"""
        
        if word not in self.history['power_words']:
            self.history['power_words'][word] = []
        
        self.history['power_words'][word].append({
            'context': context,
            'observed_effect': observed_effect,
        })
        
        self._save_history()
    
    def _save_history(self):
        """Save tracking history"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def generate_recursive_report(self) -> str:
        """Generate report on deep recursive patterns"""
        lines = []
        lines.append("=" * 80)
        lines.append("DEEP RECURSIVE PATTERN TRACKING")
        lines.append("=" * 80)
        lines.append("")
        
        # Domain accumulation analysis
        n_runs = len(self.history['domain_accumulation'])
        lines.append(f"Analysis Runs Tracked: {n_runs}")
        
        if n_runs >= 3:
            gravity_state = self._detect_gravity_state()
            lines.append(f"\nGravity State: {gravity_state.get('phase', 'unknown')}")
            lines.append(f"Trend: {gravity_state.get('trend', 'unknown')}")
            
            if gravity_state.get('interpretation'):
                lines.append(f"\n{gravity_state['interpretation']}")
            
            shape_state = self._detect_shape_emergence()
            if shape_state.get('emerging'):
                lines.append(f"\n🔥 SHAPE EMERGENCE:")
                lines.append(f"  Clarity: {shape_state['clarity']*100:.1f}%")
                lines.append(f"  {shape_state['interpretation']}")
        
        # Selection forces tracked
        if self.history['selection_forces']:
            lines.append(f"\nSelection Forces Tracked: {len(self.history['selection_forces'])}")
            for domain, forces in self.history['selection_forces'].items():
                lines.append(f"  {domain}: {len(forces)} mechanisms")
        
        # Power words tracked
        if self.history['power_words']:
            lines.append(f"\nPower Words Tracked: {len(self.history['power_words'])}")
            for word, observations in self.history['power_words'].items():
                lines.append(f"  '{word}': {len(observations)} observations")
        
        if n_runs < 3:
            lines.append("\nInsufficient data for deep recursive analysis.")
            lines.append("Continue running analyses to build longitudinal data.")
        
        return "\n".join(lines)


# Global instance
deep_tracker = DeepRecursiveTracker()

