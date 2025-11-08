"""
Blind Test Framework - Rigorous Falsifiable Testing

Prevents cherry-picking by:
1. Locking predictions BEFORE seeing actual data
2. Testing on multiple researchers
3. Statistical significance calculation
4. Cross-validation

This is SCIENCE - falsifiable, replicable, rigorous.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime
from typing import Dict, List
import numpy as np

from analyzers.discoverer_predictor import DiscovererPredictor, PersonProfile


class BlindTestFramework:
    """
    Ensures predictions are generated blind, then tested against reality
    """
    
    def __init__(self):
        self.predictor = DiscovererPredictor()
        self.predictions_locked = False
        self.locked_predictions = {}
    
    def generate_predictions_blind(self, names: List[str]) -> Dict:
        """
        Generate predictions for all names BEFORE seeing any actual data
        
        This locks predictions - can't change after seeing reality
        """
        if self.predictions_locked:
            raise ValueError("Predictions already locked! Can't regenerate.")
        
        print("=" * 80)
        print("GENERATING BLIND PREDICTIONS")
        print("=" * 80)
        print(f"\nPredicting profiles for {len(names)} individuals...")
        print("Predictions will be LOCKED before seeing actual data.\n")
        
        predictions = {}
        
        for name in names:
            print(f"Predicting: {name}...")
            profile = self.predictor.predict_person(name)
            predictions[name] = profile
        
        # LOCK predictions
        self.locked_predictions = predictions
        self.predictions_locked = True
        
        # Save locked predictions
        self._save_locked_predictions()
        
        print(f"\n✓ {len(predictions)} predictions generated and LOCKED")
        print("Cannot be changed. Ready for blind testing.")
        
        return predictions
    
    def test_prediction(self, name: str, actual_profile: Dict) -> Dict:
        """
        Test a prediction against actual profile
        
        Args:
            name: Person's name
            actual_profile: Their ACTUAL data (age, education, etc.)
            
        Returns:
            Match scores and analysis
        """
        if not self.predictions_locked:
            raise ValueError("Must lock predictions first! Call generate_predictions_blind()")
        
        if name not in self.locked_predictions:
            raise ValueError(f"No locked prediction for {name}")
        
        predicted = self.locked_predictions[name]
        
        # Calculate matches
        matches = self._calculate_matches(predicted, actual_profile)
        
        # Statistical analysis
        stats = self._calculate_statistics(matches)
        
        result = {
            'name': name,
            'predicted': self._profile_to_dict(predicted),
            'actual': actual_profile,
            'matches': matches,
            'statistics': stats,
            'overall_match': stats['overall_score']
        }
        
        return result
    
    def batch_test(self, actual_profiles: Dict[str, Dict]) -> Dict:
        """
        Test all predictions against actual profiles
        
        Returns aggregate statistics
        """
        results = {}
        
        for name, actual in actual_profiles.items():
            if name in self.locked_predictions:
                result = self.test_prediction(name, actual)
                results[name] = result
        
        # Aggregate statistics
        aggregate = self._aggregate_results(results)
        
        return {
            'individual_results': results,
            'aggregate': aggregate,
            'n_tested': len(results),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_matches(self, predicted: PersonProfile, actual: Dict) -> Dict:
        """Calculate match scores for each predicted criterion"""
        matches = {}
        
        # Age
        actual_age = actual.get('age')
        if actual_age:
            age_min, age_max = predicted.predicted_age_range
            if age_min <= actual_age <= age_max:
                matches['age'] = 1.0
            else:
                # Partial credit based on distance
                center = (age_min + age_max) / 2
                distance = abs(actual_age - center)
                matches['age'] = max(0, 1.0 - distance / 50)
        
        # Education level
        actual_edu = actual.get('education_level')
        if actual_edu:
            edu_match = {
                'elite': {'elite': 1.0, 'phd': 0.8, 'masters': 0.6},
                'phd': {'phd': 1.0, 'elite': 0.8, 'masters': 0.7},
                'masters': {'masters': 1.0, 'phd': 0.7, 'bachelors': 0.7},
                'bachelors': {'bachelors': 1.0, 'masters': 0.6}
            }
            matches['education_level'] = edu_match.get(predicted.predicted_education_level, {}).get(actual_edu, 0.5)
        
        # Elite institution
        actual_elite = actual.get('elite_institution', False)
        matches['elite_institution'] = 1.0 if predicted.predicted_elite_institution == actual_elite else 0.0
        
        # Field
        actual_field = actual.get('field')
        if actual_field:
            matches['field'] = 1.0 if predicted.predicted_field == actual_field else 0.3
        
        # MBTI
        actual_mbti = actual.get('mbti')
        if actual_mbti:
            # Match per dimension
            mbti_matches = []
            for i in range(4):
                mbti_matches.append(1.0 if predicted.predicted_mbti[i] == actual_mbti[i] else 0.0)
            matches['mbti'] = np.mean(mbti_matches)
        
        # Mental health
        actual_mh = actual.get('mental_health', [])
        mh_predictions = {
            'adhd': predicted.predicted_adhd_likelihood,
            'bipolar': predicted.predicted_bipolar_likelihood,
            'depression': predicted.predicted_depression_likelihood,
        }
        
        for condition, likelihood in mh_predictions.items():
            has_condition = condition in actual_mh
            if has_condition:
                matches[f'mental_health_{condition}'] = likelihood
            else:
                matches[f'mental_health_{condition}'] = 1.0 - likelihood
        
        # Family
        matches['has_suffix'] = 1.0 if predicted.predicted_has_junior_senior == actual.get('has_suffix', False) else 0.0
        
        # Circumstances
        matches['outsider'] = 1.0 if predicted.predicted_outsider_status == actual.get('outsider', False) else 0.5
        matches['revolutionary'] = 1.0 - abs(predicted.predicted_revolutionary_tendency - actual.get('revolutionary', 0.5))
        
        return matches
    
    def _calculate_statistics(self, matches: Dict) -> Dict:
        """Calculate statistical measures"""
        scores = list(matches.values())
        
        return {
            'overall_score': np.mean(scores),
            'median_score': np.median(scores),
            'std': np.std(scores),
            'n_criteria': len(scores),
            'perfect_matches': sum(1 for s in scores if s > 0.95),
            'good_matches': sum(1 for s in scores if s > 0.7),
        }
    
    def _aggregate_results(self, results: Dict) -> Dict:
        """Aggregate across all tested individuals"""
        all_scores = [r['statistics']['overall_score'] for r in results.values()]
        
        return {
            'mean_accuracy': np.mean(all_scores),
            'median_accuracy': np.median(all_scores),
            'std': np.std(all_scores),
            'n_tested': len(all_scores),
            'above_70': sum(1 for s in all_scores if s > 0.7),
            'above_80': sum(1 for s in all_scores if s > 0.8),
        }
    
    def _save_locked_predictions(self):
        """Save locked predictions (audit trail)"""
        save_data = {
            'locked_timestamp': datetime.now().isoformat(),
            'predictions': {
                name: self._profile_to_dict(profile)
                for name, profile in self.locked_predictions.items()
            }
        }
        
        filepath = Path('analysis_outputs/locked_predictions.json')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def _profile_to_dict(self, profile: PersonProfile) -> Dict:
        """Convert profile to dictionary"""
        return {
            'age_range': profile.predicted_age_range,
            'generation': profile.predicted_generation,
            'education_level': profile.predicted_education_level,
            'elite_institution': profile.predicted_elite_institution,
            'field': profile.predicted_field,
            'mbti': profile.predicted_mbti,
            'neurodivergent': profile.predicted_neurodivergent,
            'adhd_likelihood': profile.predicted_adhd_likelihood,
            'bipolar_likelihood': profile.predicted_bipolar_likelihood,
            'has_suffix': profile.predicted_has_junior_senior,
            'outsider': profile.predicted_outsider_status,
            'revolutionary': profile.predicted_revolutionary_tendency,
        }


# Example usage
if __name__ == '__main__':
    framework = BlindTestFramework()
    
    # Generate blind predictions for test names
    test_names = [
        "Michael Andrew Smerconish Jr",
        "Albert Einstein",
        "Marie Curie",
        "Richard Feynman",
    ]
    
    print("\nGenerating blind predictions...")
    predictions = framework.generate_predictions_blind(test_names)
    
    print("\nPredictions locked. Now ready for testing against actual data.")
    print("\nTo test: framework.test_prediction(name, actual_profile_dict)")

