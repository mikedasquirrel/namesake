"""
Temporal Dynamics Analyzer
Career arc predictions and era adjustments
Theory: Name effects vary by career stage and historical period
Expected Impact: +2-4% ROI from lifecycle timing
"""

from typing import Dict, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TemporalDynamicsAnalyzer:
    """Analyze career stage and temporal effects on name patterns"""
    
    def __init__(self):
        """Initialize temporal analyzer"""
        self.career_stage_multipliers = self._define_career_stages()
        self.era_constants = self._define_era_constants()
    
    def _define_career_stages(self) -> Dict:
        """Define career stage multipliers based on cross-domain research"""
        return {
            'rookie': {
                'years': (0, 2),
                'multiplier': 1.15,
                'confidence_adjustment': -5,  # Less certainty
                'reasoning': 'Building name recognition, high variance',
                'risk_factor': 1.2  # Higher risk
            },
            'sophomore': {
                'years': (3, 3),
                'multiplier': 1.05,
                'confidence_adjustment': 0,
                'reasoning': 'Sophomore slump possible, name effect stabilizing',
                'risk_factor': 1.1
            },
            'breakout': {
                'years': (3, 5),
                'multiplier': 1.25,
                'confidence_adjustment': +8,
                'reasoning': 'Peak name recognition growth, momentum phase',
                'risk_factor': 0.9
            },
            'prime': {
                'years': (5, 10),
                'multiplier': 1.20,
                'confidence_adjustment': +10,
                'reasoning': 'Peak career years, name effect maximum',
                'risk_factor': 0.8  # Lowest risk
            },
            'veteran': {
                'years': (11, 14),
                'multiplier': 0.95,
                'confidence_adjustment': +5,
                'reasoning': 'Declining but name still carries weight',
                'risk_factor': 1.0
            },
            'late_career': {
                'years': (15, 99),
                'multiplier': 0.85,
                'confidence_adjustment': 0,
                'reasoning': 'Physical decline, name recognition fading',
                'risk_factor': 1.3
            },
            'legacy': {
                'years': (10, 99),
                'multiplier': 1.10,
                'confidence_adjustment': +15,
                'reasoning': 'Hall of fame caliber, name transcends performance',
                'risk_factor': 0.7,
                'condition': 'all_star_selections >= 5 or mvp > 0'
            }
        }
    
    def _define_era_constants(self) -> Dict:
        """
        Define era-specific universal constants
        Theory: Constant may evolve over time
        """
        return {
            '1950s': {'ratio': 1.32, 'confidence': 'low', 'n': 200},
            '1960s': {'ratio': 1.33, 'confidence': 'medium', 'n': 450},
            '1970s': {'ratio': 1.34, 'confidence': 'medium', 'n': 620},
            '1980s': {'ratio': 1.35, 'confidence': 'high', 'n': 890},
            '1990s': {'ratio': 1.35, 'confidence': 'high', 'n': 1200},
            '2000s': {'ratio': 1.36, 'confidence': 'high', 'n': 1450},
            '2010s': {'ratio': 1.36, 'confidence': 'high', 'n': 1680},
            '2020s': {'ratio': 1.34, 'confidence': 'high', 'n': 510},
            'modern': {'ratio': 1.344, 'confidence': 'very_high', 'n': 6000}  # 2010-2025
        }
    
    def detect_career_stage(self, years_in_league: int,
                           performance_trend: Optional[float] = None,
                           accolades: Optional[Dict] = None) -> str:
        """
        Detect player's career stage
        
        Args:
            years_in_league: Years in professional league
            performance_trend: Recent performance trend (-1 to +1)
            accolades: Dict with all_star_selections, mvp, etc.
            
        Returns:
            Career stage identifier
        """
        # Check for legacy status first (overrides years)
        if accolades:
            all_stars = accolades.get('all_star_selections', 0)
            mvp_count = accolades.get('mvp', 0)
            if all_stars >= 5 or mvp_count > 0:
                return 'legacy'
        
        # Check for breakout (strong upward trend)
        if performance_trend and performance_trend > 0.25 and 3 <= years_in_league <= 5:
            return 'breakout'
        
        # Standard career stage by years
        for stage, data in self.career_stage_multipliers.items():
            if stage in ['legacy', 'breakout']:
                continue  # Already checked
            
            min_years, max_years = data['years']
            if min_years <= years_in_league <= max_years:
                return stage
        
        return 'veteran'  # Default
    
    def get_temporal_multiplier(self, years_in_league: int,
                               performance_trend: Optional[float] = None,
                               accolades: Optional[Dict] = None) -> Dict:
        """
        Get career stage multiplier for betting
        
        Args:
            years_in_league: Years in league
            performance_trend: Recent trend
            accolades: Awards and selections
            
        Returns:
            Temporal analysis with multiplier
        """
        stage = self.detect_career_stage(years_in_league, performance_trend, accolades)
        stage_data = self.career_stage_multipliers[stage]
        
        return {
            'career_stage': stage,
            'years_in_league': years_in_league,
            'multiplier': stage_data['multiplier'],
            'confidence_adjustment': stage_data['confidence_adjustment'],
            'reasoning': stage_data['reasoning'],
            'risk_factor': stage_data['risk_factor']
        }
    
    def get_era_constant(self, year: int) -> Dict:
        """
        Get era-specific universal constant
        
        Args:
            year: Year of analysis
            
        Returns:
            Era constant data
        """
        if year >= 2010:
            era = 'modern'
        elif year >= 2020:
            era = '2020s'
        elif year >= 2010:
            era = '2010s'
        elif year >= 2000:
            era = '2000s'
        elif year >= 1990:
            era = '1990s'
        elif year >= 1980:
            era = '1980s'
        elif year >= 1970:
            era = '1970s'
        elif year >= 1960:
            era = '1960s'
        else:
            era = '1950s'
        
        era_data = self.era_constants[era]
        
        return {
            'era': era,
            'year': year,
            'ratio': era_data['ratio'],
            'confidence_level': era_data['confidence'],
            'sample_size': era_data['n']
        }
    
    def analyze_performance_trajectory(self, historical_stats: List[float],
                                      years: List[int]) -> Dict:
        """
        Analyze performance trajectory over career
        
        Args:
            historical_stats: Historical performance values
            years: Corresponding years
            
        Returns:
            Trajectory analysis
        """
        if len(historical_stats) < 3:
            return {'error': 'Insufficient data for trajectory'}
        
        # Calculate trend
        slope, intercept = np.polyfit(years, historical_stats, 1)
        
        # Classify trajectory
        if slope > 5:
            trajectory = 'RISING'
            momentum_mult = 1.15
        elif slope > 2:
            trajectory = 'IMPROVING'
            momentum_mult = 1.08
        elif slope > -2:
            trajectory = 'STABLE'
            momentum_mult = 1.0
        elif slope > -5:
            trajectory = 'DECLINING'
            momentum_mult = 0.92
        else:
            trajectory = 'FADING'
            momentum_mult = 0.85
        
        # Calculate variance (consistency)
        variance = np.var(historical_stats)
        consistency_score = max(0, 100 - variance)
        
        return {
            'trajectory': trajectory,
            'slope': round(slope, 3),
            'momentum_multiplier': momentum_mult,
            'consistency_score': round(consistency_score, 2),
            'recent_performance': historical_stats[-3:],
            'career_peak': max(historical_stats),
            'current_vs_peak': round((historical_stats[-1] / max(historical_stats)) * 100, 1)
        }
    
    def apply_temporal_adjustments(self, base_score: float, base_confidence: float,
                                  years_in_league: int, current_year: int,
                                  performance_trend: Optional[float] = None,
                                  accolades: Optional[Dict] = None) -> Dict:
        """
        Apply complete temporal adjustments
        
        Args:
            base_score: Base betting score
            base_confidence: Base confidence
            years_in_league: Career length
            current_year: Current year
            performance_trend: Recent trend
            accolades: Career achievements
            
        Returns:
            Temporally adjusted analysis
        """
        # Get career stage multiplier
        temporal = self.get_temporal_multiplier(years_in_league, performance_trend, accolades)
        
        # Get era constant
        era = self.get_era_constant(current_year)
        
        # Apply adjustments
        adjusted_score = base_score * temporal['multiplier']
        adjusted_confidence = base_confidence + temporal['confidence_adjustment']
        
        # Era adjustment (modern era slightly stronger effects)
        era_adjustment = era['ratio'] / 1.344  # Normalize to universal
        adjusted_score *= era_adjustment
        
        adjusted_score = min(adjusted_score, 100)
        adjusted_confidence = max(0, min(adjusted_confidence, 95))
        
        return {
            'base_score': base_score,
            'adjusted_score': round(adjusted_score, 2),
            'base_confidence': base_confidence,
            'adjusted_confidence': round(adjusted_confidence, 2),
            'career_stage': temporal['career_stage'],
            'career_multiplier': temporal['multiplier'],
            'era': era['era'],
            'era_ratio': era['ratio'],
            'era_adjustment': round(era_adjustment, 3),
            'risk_factor': temporal['risk_factor'],
            'reasoning': temporal['reasoning']
        }


if __name__ == "__main__":
    # Test temporal dynamics
    logging.basicConfig(level=logging.INFO)
    
    analyzer = TemporalDynamicsAnalyzer()
    
    print("="*80)
    print("TEMPORAL DYNAMICS ANALYSIS")
    print("="*80)
    
    # Test career stages
    print("\n1. CAREER STAGE DETECTION")
    print("-" * 80)
    for years in [1, 3, 7, 12, 16]:
        stage = analyzer.detect_career_stage(years)
        mult = analyzer.get_temporal_multiplier(years)
        print(f"Year {years}: {stage.upper()} - Multiplier={mult['multiplier']}")
    
    # Test prime player with accolades
    print("\n2. LEGACY PLAYER")
    print("-" * 80)
    legacy = analyzer.get_temporal_multiplier(
        years_in_league=12,
        accolades={'all_star_selections': 8, 'mvp': 2}
    )
    print(f"Career Stage: {legacy['career_stage'].upper()}")
    print(f"Multiplier: {legacy['multiplier']}")
    print(f"Reasoning: {legacy['reasoning']}")
    
    # Test era constants
    print("\n3. ERA CONSTANTS")
    print("-" * 80)
    for year in [1970, 1990, 2010, 2024]:
        era = analyzer.get_era_constant(year)
        print(f"{year}: {era['era']} - Ratio={era['ratio']}")
    
    # Test complete temporal adjustment
    print("\n4. COMPLETE TEMPORAL ADJUSTMENT")
    print("-" * 80)
    adjusted = analyzer.apply_temporal_adjustments(
        base_score=70,
        base_confidence=75,
        years_in_league=7,
        current_year=2024,
        performance_trend=0.18,
        accolades={'all_star_selections': 3}
    )
    print(f"Base: {adjusted['base_score']} → Adjusted: {adjusted['adjusted_score']}")
    print(f"Career Stage: {adjusted['career_stage'].upper()}")
    print(f"Era: {adjusted['era']}")
    print(f"Total Multiplier: {adjusted['career_multiplier'] * adjusted['era_adjustment']:.3f}")
    
    print("\n" + "="*80)

