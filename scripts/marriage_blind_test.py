"""
Marriage Prediction Blind Test Framework

Rigorous blind testing for marriage prediction study.
Ensures predictions are locked BEFORE seeing outcomes.

Scientific Rigor Protocol:
1. Generate predictions from names only
2. Lock predictions with timestamp
3. Later: Reveal outcomes
4. Calculate match scores
5. Statistical significance testing

This prevents cherry-picking and p-hacking.
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from scipy import stats

from analyzers.relationship_compatibility_analyzer import RelationshipCompatibilityAnalyzer
from core.marriage_models import MarriedCouple, PredictionLock
from core.models import db


class MarriageBlindTestFramework:
    """
    Blind testing framework for marriage predictions
    
    Protocol:
    1. Input: Names only (no outcomes)
    2. Generate: Compatibility predictions
    3. Lock: Save predictions with timestamp
    4. Later: Merge with actual outcomes
    5. Evaluate: Calculate prediction accuracy
    """
    
    def __init__(self, db_session=None):
        """
        Initialize blind test framework
        
        Args:
            db_session: Database session for storing predictions
        """
        self.analyzer = RelationshipCompatibilityAnalyzer(db_session)
        self.db = db_session
        self.predictions_locked = False
        self.locked_batch_id = None
        self.locked_predictions = {}
    
    def generate_blind_predictions(self, 
                                   couple_names: List[Tuple[str, str, int]],
                                   batch_id: str = None) -> Dict:
        """
        Generate predictions WITHOUT seeing outcomes
        
        Args:
            couple_names: List of (name1, name2, couple_id) tuples
            batch_id: Identifier for this prediction batch
            
        Returns:
            Dict with locked predictions
        """
        if self.predictions_locked:
            raise ValueError("Predictions already locked! Cannot regenerate.")
        
        if batch_id is None:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("=" * 80)
        print("BLIND PREDICTION GENERATION")
        print("=" * 80)
        print(f"\nBatch ID: {batch_id}")
        print(f"Number of couples: {len(couple_names)}")
        print("\nGenerating predictions from names only...")
        print("Outcomes will NOT be viewed until predictions are locked.\n")
        
        predictions = {}
        
        for name1, name2, couple_id in couple_names:
            print(f"Predicting: {name1} & {name2}...")
            
            # Generate prediction (blind to outcome)
            prediction = self.analyzer.predict_relationship_outcome(
                name1, name2
            )
            
            predictions[couple_id] = {
                'partner1_name': name1,
                'partner2_name': name2,
                'predicted_compatibility': prediction['predicted_compatibility'],
                'predicted_divorce_risk': prediction['predicted_divorce_risk'],
                'predicted_longevity_years': prediction['predicted_longevity_years'],
                'dominant_theory': prediction['dominant_theory'],
                'confidence': prediction['confidence'],
                'relationship_type': prediction['relationship_type'],
                'theory_scores': prediction['theory_scores']
            }
        
        # LOCK PREDICTIONS
        self.locked_predictions = predictions
        self.locked_batch_id = batch_id
        self.predictions_locked = True
        
        # Save to database (audit trail)
        if self.db:
            self._save_locked_predictions_to_db(batch_id)
        
        # Save to JSON file (backup audit trail)
        self._save_locked_predictions_to_file(batch_id)
        
        print(f"\n✓ {len(predictions)} predictions generated and LOCKED")
        print(f"✓ Batch ID: {batch_id}")
        print(f"✓ Timestamp: {datetime.now().isoformat()}")
        print("\nPredictions cannot be changed.")
        print("Ready to reveal outcomes for testing.\n")
        
        return {
            'batch_id': batch_id,
            'n_predictions': len(predictions),
            'locked_timestamp': datetime.now().isoformat(),
            'predictions': predictions
        }
    
    def reveal_and_test(self, actual_outcomes: Dict[int, Dict]) -> Dict:
        """
        Reveal actual outcomes and test predictions
        
        Args:
            actual_outcomes: Dict mapping couple_id → outcome data
                            {couple_id: {'is_divorced': bool, 
                                        'duration': float}}
            
        Returns:
            Dict with test results and statistics
        """
        if not self.predictions_locked:
            raise ValueError("Must lock predictions first!")
        
        print("=" * 80)
        print("OUTCOME REVELATION & TESTING")
        print("=" * 80)
        print(f"\nBatch ID: {self.locked_batch_id}")
        print(f"Testing {len(actual_outcomes)} couples\n")
        
        results = []
        
        for couple_id, prediction in self.locked_predictions.items():
            if couple_id not in actual_outcomes:
                print(f"Warning: No outcome for couple {couple_id}, skipping")
                continue
            
            outcome = actual_outcomes[couple_id]
            
            # Calculate match scores
            match = self._calculate_match_scores(prediction, outcome)
            
            result = {
                'couple_id': couple_id,
                'partner1_name': prediction['partner1_name'],
                'partner2_name': prediction['partner2_name'],
                'predicted_compatibility': prediction['predicted_compatibility'],
                'predicted_divorce_risk': prediction['predicted_divorce_risk'],
                'predicted_longevity': prediction['predicted_longevity_years'],
                'actual_is_divorced': outcome['is_divorced'],
                'actual_duration': outcome['duration'],
                'compatibility_match': match['compatibility_match'],
                'divorce_prediction_correct': match['divorce_correct'],
                'longevity_error': match['longevity_error'],
                'overall_accuracy': match['overall_accuracy']
            }
            
            results.append(result)
        
        # Aggregate statistics
        aggregate_stats = self._calculate_aggregate_statistics(results)
        
        # Statistical significance tests
        significance = self._test_statistical_significance(results)
        
        # Update database with outcomes
        if self.db:
            self._update_db_with_outcomes(results)
        
        # Save results
        self._save_test_results(results, aggregate_stats, significance)
        
        # Print summary
        self._print_test_summary(aggregate_stats, significance)
        
        return {
            'batch_id': self.locked_batch_id,
            'n_tested': len(results),
            'results': results,
            'aggregate_statistics': aggregate_stats,
            'statistical_significance': significance,
            'tested_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_match_scores(self, prediction: Dict, outcome: Dict) -> Dict:
        """
        Calculate match scores between prediction and outcome
        
        Args:
            prediction: Predicted values
            outcome: Actual outcomes
            
        Returns:
            Dict with match scores
        """
        # 1. Compatibility match
        # Higher compatibility should → longer marriage
        actual_duration = outcome['duration']
        predicted_compatibility = prediction['predicted_compatibility']
        
        # Normalize duration to 0-1 (assume max 50 years)
        normalized_duration = min(actual_duration / 50.0, 1.0)
        
        # Match score = how close they are
        compatibility_match = 1.0 - abs(predicted_compatibility - normalized_duration)
        
        # 2. Divorce prediction
        actual_divorced = outcome['is_divorced']
        predicted_risk = prediction['predicted_divorce_risk']
        
        # Correct if:
        # - Predicted high risk (>0.5) AND actually divorced
        # - Predicted low risk (<0.5) AND still married
        if actual_divorced:
            # Divorced: higher predicted risk = better
            divorce_correct = predicted_risk > 0.5
        else:
            # Still married: lower predicted risk = better
            divorce_correct = predicted_risk < 0.5
        
        # 3. Longevity error
        predicted_longevity = prediction['predicted_longevity_years']
        longevity_error = abs(predicted_longevity - actual_duration)
        
        # Normalize error (good prediction = error < 5 years)
        longevity_match = 1.0 - min(longevity_error / 20.0, 1.0)
        
        # 4. Overall accuracy (weighted average)
        overall = (
            compatibility_match * 0.4 +
            (1.0 if divorce_correct else 0.0) * 0.3 +
            longevity_match * 0.3
        )
        
        return {
            'compatibility_match': compatibility_match,
            'divorce_correct': divorce_correct,
            'longevity_error': longevity_error,
            'longevity_match': longevity_match,
            'overall_accuracy': overall
        }
    
    def _calculate_aggregate_statistics(self, results: List[Dict]) -> Dict:
        """
        Calculate aggregate statistics across all predictions
        
        Args:
            results: List of individual results
            
        Returns:
            Dict with aggregate stats
        """
        if not results:
            return {}
        
        # Extract arrays
        compatibility_matches = [r['compatibility_match'] for r in results]
        divorce_corrects = [r['divorce_prediction_correct'] for r in results]
        longevity_errors = [r['longevity_error'] for r in results]
        overall_accuracies = [r['overall_accuracy'] for r in results]
        
        # Calculate statistics
        stats_dict = {
            'n_couples': len(results),
            
            # Compatibility
            'mean_compatibility_match': np.mean(compatibility_matches),
            'median_compatibility_match': np.median(compatibility_matches),
            'std_compatibility_match': np.std(compatibility_matches),
            
            # Divorce prediction
            'divorce_prediction_accuracy': np.mean(divorce_corrects),
            'divorce_correct_count': sum(divorce_corrects),
            'divorce_incorrect_count': len(divorce_corrects) - sum(divorce_corrects),
            
            # Longevity
            'mean_longevity_error': np.mean(longevity_errors),
            'median_longevity_error': np.median(longevity_errors),
            'rmse_longevity': np.sqrt(np.mean([e**2 for e in longevity_errors])),
            
            # Overall
            'mean_overall_accuracy': np.mean(overall_accuracies),
            'median_overall_accuracy': np.median(overall_accuracies),
            'accuracy_above_70': sum(1 for a in overall_accuracies if a > 0.7),
            'accuracy_above_60': sum(1 for a in overall_accuracies if a > 0.6),
        }
        
        return stats_dict
    
    def _test_statistical_significance(self, results: List[Dict]) -> Dict:
        """
        Test statistical significance of predictions
        
        Tests:
        1. Is compatibility match > chance (0.5)?
        2. Is divorce prediction > chance (0.5)?
        3. Is longevity error < baseline error?
        
        Args:
            results: List of individual results
            
        Returns:
            Dict with significance tests
        """
        # Extract arrays
        compatibility_matches = [r['compatibility_match'] for r in results]
        divorce_corrects = [r['divorce_prediction_correct'] for r in results]
        overall_accuracies = [r['overall_accuracy'] for r in results]
        
        # Test 1: Compatibility match vs. chance (0.5)
        t_stat_compat, p_value_compat = stats.ttest_1samp(compatibility_matches, 0.5)
        
        # Test 2: Divorce accuracy vs. chance (0.5)
        divorce_rate = np.mean(divorce_corrects)
        # Binomial test
        n_correct = sum(divorce_corrects)
        n_total = len(divorce_corrects)
        p_value_divorce = stats.binom_test(n_correct, n_total, p=0.5, alternative='greater')
        
        # Test 3: Overall accuracy vs. chance (0.5)
        t_stat_overall, p_value_overall = stats.ttest_1samp(overall_accuracies, 0.5)
        
        # Effect sizes (Cohen's d)
        def cohens_d(sample, population_mean):
            return (np.mean(sample) - population_mean) / np.std(sample)
        
        d_compat = cohens_d(compatibility_matches, 0.5)
        d_overall = cohens_d(overall_accuracies, 0.5)
        
        return {
            'compatibility_test': {
                't_statistic': t_stat_compat,
                'p_value': p_value_compat,
                'cohens_d': d_compat,
                'significant': p_value_compat < 0.05,
                'interpretation': self._interpret_significance(p_value_compat, d_compat)
            },
            'divorce_test': {
                'accuracy': divorce_rate,
                'p_value': p_value_divorce,
                'significant': p_value_divorce < 0.05,
                'interpretation': self._interpret_divorce_accuracy(divorce_rate, p_value_divorce)
            },
            'overall_test': {
                't_statistic': t_stat_overall,
                'p_value': p_value_overall,
                'cohens_d': d_overall,
                'significant': p_value_overall < 0.05,
                'interpretation': self._interpret_significance(p_value_overall, d_overall)
            }
        }
    
    def _interpret_significance(self, p_value: float, effect_size: float) -> str:
        """Interpret significance test results"""
        if p_value < 0.001:
            sig_str = "highly significant (p < 0.001)"
        elif p_value < 0.01:
            sig_str = "very significant (p < 0.01)"
        elif p_value < 0.05:
            sig_str = "significant (p < 0.05)"
        else:
            sig_str = "not significant (p >= 0.05)"
        
        if abs(effect_size) < 0.2:
            effect_str = "small effect"
        elif abs(effect_size) < 0.5:
            effect_str = "medium effect"
        else:
            effect_str = "large effect"
        
        return f"{sig_str}, {effect_str} (d = {effect_size:.3f})"
    
    def _interpret_divorce_accuracy(self, accuracy: float, p_value: float) -> str:
        """Interpret divorce prediction accuracy"""
        if p_value < 0.05:
            return f"Significantly better than chance: {accuracy:.1%} accuracy (p = {p_value:.4f})"
        else:
            return f"Not significantly better than chance: {accuracy:.1%} accuracy (p = {p_value:.4f})"
    
    def _save_locked_predictions_to_db(self, batch_id: str):
        """Save locked predictions to database"""
        try:
            for couple_id, prediction in self.locked_predictions.items():
                lock = PredictionLock(
                    batch_id=batch_id,
                    locked_timestamp=datetime.utcnow(),
                    predictor_version="1.0.0",
                    couple_id=couple_id,
                    partner1_name=prediction['partner1_name'],
                    partner2_name=prediction['partner2_name'],
                    predicted_compatibility=prediction['predicted_compatibility'],
                    predicted_divorce_probability=prediction['predicted_divorce_risk'],
                    predicted_longevity_years=prediction['predicted_longevity_years'],
                    dominant_theory=prediction['dominant_theory']
                )
                self.db.add(lock)
            
            self.db.commit()
            print(f"✓ Predictions saved to database")
        
        except Exception as e:
            print(f"Warning: Could not save to database: {e}")
    
    def _save_locked_predictions_to_file(self, batch_id: str):
        """Save locked predictions to JSON file (audit trail)"""
        filepath = Path(f'analysis_outputs/marriage/predictions_{batch_id}.json')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            'batch_id': batch_id,
            'locked_timestamp': datetime.now().isoformat(),
            'predictor_version': '1.0.0',
            'n_predictions': len(self.locked_predictions),
            'predictions': self.locked_predictions
        }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"✓ Predictions saved to {filepath}")
    
    def _update_db_with_outcomes(self, results: List[Dict]):
        """Update database with revealed outcomes"""
        if not self.db:
            return
        
        try:
            for result in results:
                lock = self.db.query(PredictionLock).filter_by(
                    batch_id=self.locked_batch_id,
                    couple_id=result['couple_id']
                ).first()
                
                if lock:
                    lock.actual_is_divorced = result['actual_is_divorced']
                    lock.actual_marriage_duration = result['actual_duration']
                    lock.outcomes_revealed_timestamp = datetime.utcnow()
                    lock.compatibility_match_score = result['compatibility_match']
                    lock.divorce_prediction_correct = result['divorce_prediction_correct']
                    lock.longevity_prediction_error = result['longevity_error']
                    lock.overall_prediction_accuracy = result['overall_accuracy']
            
            self.db.commit()
        
        except Exception as e:
            print(f"Warning: Could not update database: {e}")
    
    def _save_test_results(self, results: List[Dict], aggregate: Dict, significance: Dict):
        """Save test results to file"""
        filepath = Path(f'analysis_outputs/marriage/test_results_{self.locked_batch_id}.json')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            'batch_id': self.locked_batch_id,
            'tested_timestamp': datetime.now().isoformat(),
            'n_tested': len(results),
            'results': results,
            'aggregate_statistics': aggregate,
            'statistical_significance': significance
        }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"\n✓ Results saved to {filepath}")
    
    def _print_test_summary(self, aggregate: Dict, significance: Dict):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 Sample Size: {aggregate['n_couples']} couples")
        
        print(f"\n🎯 Overall Accuracy:")
        print(f"  Mean: {aggregate['mean_overall_accuracy']:.3f} ({aggregate['mean_overall_accuracy']*100:.1f}%)")
        print(f"  Median: {aggregate['median_overall_accuracy']:.3f}")
        print(f"  Above 70%: {aggregate['accuracy_above_70']} couples")
        print(f"  Above 60%: {aggregate['accuracy_above_60']} couples")
        
        print(f"\n💑 Compatibility Match:")
        print(f"  Mean: {aggregate['mean_compatibility_match']:.3f}")
        print(f"  {significance['compatibility_test']['interpretation']}")
        
        print(f"\n💔 Divorce Prediction:")
        print(f"  Accuracy: {aggregate['divorce_prediction_accuracy']*100:.1f}%")
        print(f"  Correct: {aggregate['divorce_correct_count']}")
        print(f"  Incorrect: {aggregate['divorce_incorrect_count']}")
        print(f"  {significance['divorce_test']['interpretation']}")
        
        print(f"\n⏱️  Longevity Prediction:")
        print(f"  Mean Error: {aggregate['mean_longevity_error']:.2f} years")
        print(f"  RMSE: {aggregate['rmse_longevity']:.2f} years")
        
        print(f"\n📈 Statistical Significance:")
        if significance['overall_test']['significant']:
            print(f"  ✅ Predictions significantly better than chance")
            print(f"  p-value: {significance['overall_test']['p_value']:.4f}")
            print(f"  Effect size: {significance['overall_test']['cohens_d']:.3f}")
        else:
            print(f"  ❌ Predictions NOT significantly better than chance")
            print(f"  p-value: {significance['overall_test']['p_value']:.4f}")
        
        print("\n" + "=" * 80)


# Example usage
if __name__ == '__main__':
    framework = MarriageBlindTestFramework()
    
    # Sample couples (names only, no outcomes)
    test_couples = [
        ('Michael', 'Jennifer', 1),
        ('Christopher', 'Jessica', 2),
        ('Matthew', 'Ashley', 3),
        ('Joshua', 'Sarah', 4),
        ('Andrew', 'Amanda', 5),
    ]
    
    # Step 1: Generate blind predictions
    print("\n🔒 STEP 1: GENERATE BLIND PREDICTIONS\n")
    predictions = framework.generate_blind_predictions(test_couples)
    
    # Step 2: (Later) Reveal outcomes and test
    print("\n\n📊 STEP 2: REVEAL OUTCOMES & TEST\n")
    
    # Simulate actual outcomes
    actual_outcomes = {
        1: {'is_divorced': False, 'duration': 15.2},
        2: {'is_divorced': True, 'duration': 8.5},
        3: {'is_divorced': False, 'duration': 12.8},
        4: {'is_divorced': True, 'duration': 5.2},
        5: {'is_divorced': False, 'duration': 18.3},
    }
    
    results = framework.reveal_and_test(actual_outcomes)

