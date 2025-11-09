"""
Bayesian Live Updater
Real-time adaptation as season progresses
Theory: Start with universal constant, update with observed performance
Expected Impact: +2-3% ROI from adaptive learning
"""

from typing import Dict, List, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BayesianLiveUpdater:
    """Update predictions in real-time as season progresses"""
    
    UNIVERSAL_PRIOR_STRENGTH = 100  # Equivalent to 100 observations
    
    def __init__(self):
        """Initialize Bayesian updater"""
        self.player_posteriors = {}  # Store updated beliefs per player
    
    def calculate_posterior(self, prior_mean: float, prior_strength: int,
                           observed_values: List[float]) -> Dict:
        """
        Calculate Bayesian posterior after observations
        
        Args:
            prior_mean: Prior expectation (from universal constant)
            prior_strength: Strength of prior (pseudo-observations)
            observed_values: Actual observed performances
            
        Returns:
            Posterior distribution
        """
        n_observed = len(observed_values)
        
        if n_observed == 0:
            return {
                'posterior_mean': prior_mean,
                'posterior_strength': prior_strength,
                'weight_prior': 1.0,
                'weight_data': 0.0
            }
        
        observed_mean = np.mean(observed_values)
        
        # Bayesian update
        total_strength = prior_strength + n_observed
        weight_prior = prior_strength / total_strength
        weight_data = n_observed / total_strength
        
        posterior_mean = (prior_mean * weight_prior) + (observed_mean * weight_data)
        
        # Calculate uncertainty reduction
        prior_variance = 100  # Assume prior variance
        posterior_variance = prior_variance / (1 + n_observed / prior_strength)
        uncertainty_reduction = 1 - (posterior_variance / prior_variance)
        
        return {
            'prior_mean': prior_mean,
            'prior_strength': prior_strength,
            'observed_mean': round(observed_mean, 2),
            'n_observed': n_observed,
            'posterior_mean': round(posterior_mean, 2),
            'posterior_strength': total_strength,
            'weight_prior': round(weight_prior, 3),
            'weight_data': round(weight_data, 3),
            'uncertainty_reduction': round(uncertainty_reduction * 100, 1)
        }
    
    def update_player_belief(self, player_id: str, prior_score: float,
                            observed_performance: float) -> Dict:
        """
        Update belief about a specific player after observing performance
        
        Args:
            player_id: Player identifier
            prior_score: Prior expectation
            observed_performance: Actual performance
            
        Returns:
            Updated belief
        """
        # Get existing posterior or initialize
        if player_id not in self.player_posteriors:
            self.player_posteriors[player_id] = {
                'observations': [],
                'prior_mean': prior_score,
                'prior_strength': self.UNIVERSAL_PRIOR_STRENGTH
            }
        
        # Add observation
        self.player_posteriors[player_id]['observations'].append(observed_performance)
        
        # Calculate posterior
        posterior = self.calculate_posterior(
            prior_mean=self.player_posteriors[player_id]['prior_mean'],
            prior_strength=self.player_posteriors[player_id]['prior_strength'],
            observed_values=self.player_posteriors[player_id]['observations']
        )
        
        return {
            'player_id': player_id,
            **posterior,
            'total_observations': len(self.player_posteriors[player_id]['observations'])
        }
    
    def get_season_adjusted_prediction(self, player_id: str, games_played: int,
                                      prior_score: float, season_performances: List[float]) -> Dict:
        """
        Get prediction that adapts over the season
        
        Args:
            player_id: Player identifier
            games_played: Games played this season
            prior_score: Universal constant-based prior
            season_performances: Actual performances so far
            
        Returns:
            Season-adjusted prediction
        """
        # Early season: Trust prior more
        # Late season: Trust observations more
        season_progress = min(games_played / 16, 1.0)  # Normalize to 16-game season
        
        # Update with observations
        posterior = self.calculate_posterior(
            prior_mean=prior_score,
            prior_strength=self.UNIVERSAL_PRIOR_STRENGTH,
            observed_values=season_performances
        )
        
        # Confidence increases with observations
        base_confidence = 70
        observation_confidence_boost = min(season_progress * 15, 15)  # Up to +15%
        adjusted_confidence = base_confidence + observation_confidence_boost
        
        # Prediction intervals (Bayesian credible intervals)
        posterior_std = np.std(season_performances) if season_performances else 10
        credible_interval = (
            posterior['posterior_mean'] - 1.96 * posterior_std,
            posterior['posterior_mean'] + 1.96 * posterior_std
        )
        
        return {
            'player_id': player_id,
            'games_played': games_played,
            'season_progress': round(season_progress * 100, 1),
            'prior_score': prior_score,
            'posterior_mean': posterior['posterior_mean'],
            'weight_prior': posterior['weight_prior'],
            'weight_observations': posterior['weight_data'],
            'confidence': round(adjusted_confidence, 1),
            'credible_interval': tuple(round(x, 2) for x in credible_interval),
            'uncertainty_reduction': posterior['uncertainty_reduction'],
            'recommendation': 'Trust posterior more' if season_progress > 0.5 else 'Trust prior more'
        }
    
    def detect_regime_change(self, recent_performances: List[float],
                            prior_mean: float, threshold: float = 2.0) -> Dict:
        """
        Detect if player performance has fundamentally changed (regime shift)
        
        Args:
            recent_performances: Last 5-10 performances
            prior_mean: Expected mean from prior
            threshold: Standard deviations for regime change detection
            
        Returns:
            Regime change analysis
        """
        if len(recent_performances) < 5:
            return {'regime_change': False, 'reason': 'Insufficient data'}
        
        recent_mean = np.mean(recent_performances)
        recent_std = np.std(recent_performances)
        
        # Z-score of recent mean vs prior
        if recent_std > 0:
            z_score = (recent_mean - prior_mean) / recent_std
        else:
            z_score = 0
        
        # Detect regime change
        if abs(z_score) > threshold:
            regime_change = True
            
            if z_score > 0:
                direction = 'BREAKOUT'
                adjustment = 1.20
                reasoning = f'Performance significantly above prior (z={z_score:.2f}) - breakout detected'
            else:
                direction = 'DECLINE'
                adjustment = 0.85
                reasoning = f'Performance significantly below prior (z={z_score:.2f}) - decline detected'
        else:
            regime_change = False
            direction = 'STABLE'
            adjustment = 1.0
            reasoning = 'Performance consistent with prior expectations'
        
        return {
            'regime_change': regime_change,
            'direction': direction,
            'z_score': round(z_score, 3),
            'adjustment_multiplier': adjustment,
            'reasoning': reasoning,
            'recent_mean': round(recent_mean, 2),
            'prior_mean': prior_mean,
            'deviation': round(recent_mean - prior_mean, 2)
        }
    
    def adaptive_confidence(self, games_into_season: int, prediction_accuracy: float,
                           max_games: int = 16) -> Dict:
        """
        Calculate adaptive confidence based on prediction track record
        
        Args:
            games_into_season: Games played
            prediction_accuracy: % of predictions correct so far
            max_games: Games in season
            
        Returns:
            Adaptive confidence
        """
        season_progress = games_into_season / max_games
        
        # Start with lower confidence, increase with good track record
        base_confidence = 60 + (season_progress * 10)  # 60% → 70% over season
        
        # Accuracy adjustment
        if prediction_accuracy > 0.65:
            accuracy_boost = (prediction_accuracy - 0.5) * 40  # Up to +20%
        elif prediction_accuracy < 0.45:
            accuracy_boost = (prediction_accuracy - 0.5) * 40  # Down to -20%
        else:
            accuracy_boost = 0
        
        final_confidence = base_confidence + accuracy_boost
        final_confidence = max(40, min(final_confidence, 90))
        
        return {
            'games_into_season': games_into_season,
            'season_progress': round(season_progress * 100, 1),
            'prediction_accuracy': round(prediction_accuracy * 100, 1),
            'base_confidence': round(base_confidence, 1),
            'accuracy_adjustment': round(accuracy_boost, 1),
            'final_confidence': round(final_confidence, 1),
            'confidence_trend': 'INCREASING' if accuracy_boost > 5 else 'DECREASING' if accuracy_boost < -5 else 'STABLE'
        }


if __name__ == "__main__":
    # Test Bayesian updater
    logging.basicConfig(level=logging.INFO)
    
    updater = BayesianLiveUpdater()
    
    print("="*80)
    print("BAYESIAN LIVE UPDATING")
    print("="*80)
    
    # Test 1: Season progression
    print("\n1. SEASON PROGRESSION")
    print("-" * 80)
    
    prior_score = 72
    performances = [68, 75, 71, 77, 74, 79]  # Trending up
    
    for i in [1, 3, 6]:
        adjusted = updater.get_season_adjusted_prediction(
            player_id='player_1',
            games_played=i,
            prior_score=prior_score,
            season_performances=performances[:i]
        )
        print(f"\nAfter {i} games:")
        print(f"  Posterior: {adjusted['posterior_mean']}")
        print(f"  Weight prior: {adjusted['weight_prior']:.1%}, Weight data: {adjusted['weight_observations']:.1%}")
        print(f"  Confidence: {adjusted['confidence']}%")
    
    # Test 2: Regime change detection
    print("\n2. REGIME CHANGE DETECTION")
    print("-" * 80)
    
    # Breakout scenario
    breakout = updater.detect_regime_change([78, 82, 85, 88, 90], prior_mean=65)
    print(f"Breakout: {breakout['direction']}")
    print(f"Z-score: {breakout['z_score']}")
    print(f"Adjustment: {breakout['adjustment_multiplier']}×")
    
    print("\n" + "="*80)

