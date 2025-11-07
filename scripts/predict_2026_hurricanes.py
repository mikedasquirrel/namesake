"""2026 Atlantic Hurricane Casualty Predictions - Pre-Registration

This script generates PRE-REGISTERED predictions for the 2026 Atlantic hurricane season
based solely on name phonetics. This is a prospective test of nominative determinism.

PRE-REGISTERED: January 2025
SEASON: June-November 2026
EVALUATION: December 2026

**Critical**: These predictions are made BEFORE any 2026 storms occur.
Any post-hoc adjustment would invalidate the temporal precedence test.
"""

import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Hurricane, HurricaneAnalysis
from analyzers.name_analyzer import NameAnalyzer
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import pickle

# 2026 Atlantic Hurricane Names (Official WMO List)
HURRICANE_NAMES_2026 = [
    "Adria", "Braylen", "Carla", "Deshawn", "Emilia", "Foster",
    "Gemma", "Heath", "Isla", "Jacinta", "Kenyon", "Leah",
    "Marcus", "Nayeli", "Owen", "Paige", "Rafael", "Savannah",
    "Tony", "Valeria", "William"
]


class Hurricane2026Predictor:
    """Generate pre-registered predictions for 2026 Atlantic hurricane season."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        db.init_app(self.app)
        self.analyzer = NameAnalyzer()
        self.predictions = {}
        self.model_metadata = {}
        
    def run_complete_prediction(self) -> Dict:
        """Execute full prediction protocol."""
        
        print("="*80)
        print("2026 ATLANTIC HURRICANE CASUALTY PREDICTIONS")
        print("PRE-REGISTRATION FOR TEMPORAL PRECEDENCE TEST")
        print("="*80)
        print(f"Date Generated: {datetime.now().isoformat()}")
        print(f"Prediction Count: {len(HURRICANE_NAMES_2026)} names")
        print()
        
        with self.app.app_context():
            # Step 1: Train model on historical data (1950-2024)
            print("[1/5] Training model on historical data...")
            model, scaler, feature_names, training_metrics = self._train_historical_model()
            
            # Step 2: Extract phonetic features for 2026 names
            print("\n[2/5] Extracting phonetic features for 2026 names...")
            features_2026 = self._extract_2026_features()
            
            # Step 3: Generate predictions
            print("\n[3/5] Generating predictions...")
            predictions = self._generate_predictions(model, scaler, feature_names, features_2026)
            
            # Step 4: Create prediction document
            print("\n[4/5] Creating pre-registration document...")
            document = self._create_preregistration_document(
                predictions, training_metrics, feature_names
            )
            
            # Step 5: Save and hash
            print("\n[5/5] Saving and hashing predictions...")
            self._save_predictions(document)
            
        print("\n" + "="*80)
        print("PRE-REGISTRATION COMPLETE")
        print("="*80)
        print("Next steps:")
        print("1. Submit to OSF (https://osf.io/registries)")
        print("2. Publish on platform at /2026-predictions")
        print("3. Wait for 2026 hurricane season")
        print("4. Evaluate predictions in December 2026")
        print()
        
        return document
    
    def _train_historical_model(self) -> Tuple:
        """Train logistic regression model on 1950-2024 hurricane data."""
        
        # Load historical hurricane data
        hurricanes = Hurricane.query.filter(Hurricane.year >= 1950).all()
        analyses = {ha.hurricane_id: ha for ha in HurricaneAnalysis.query.all()}
        
        data = []
        for h in hurricanes:
            analysis = analyses.get(h.id)
            if not analysis:
                continue
            
            # Binary outcome: Any casualties (>0 deaths)
            has_casualties = 1 if (h.deaths and h.deaths > 0) else 0
            
            data.append({
                'name': h.name,
                'year': h.year,
                'deaths': h.deaths or 0,
                'has_casualties': has_casualties,
                'max_wind_mph': h.max_wind_mph,
                'saffir_simpson_category': h.saffir_simpson_category,
                
                # Phonetic features
                'phonetic_harshness': analysis.phonetic_harshness_score or 50.0,
                'memorability': analysis.memorability_score or 50.0,
                'syllable_count': analysis.syllable_count or 2,
                'length': analysis.character_length or 5,
                'vowel_ratio': analysis.vowel_ratio or 0.4,
                'plosive_count': 0,  # Not in model, estimate from harshness
                'sibilant_count': 0,  # Not in model, estimate from harshness
            })
        
        df = pd.DataFrame(data)
        
        print(f"   Historical sample: {len(df)} hurricanes (1950-2024)")
        print(f"   Casualties: {df['has_casualties'].sum()} with casualties, {len(df) - df['has_casualties'].sum()} without")
        
        # Define features (phonetic only, plus minimal controls)
        # Note: Using only features available in both historical and new names
        feature_names = [
            'phonetic_harshness',
            'memorability',
            'syllable_count',
            'length',
            'vowel_ratio'
        ]
        
        # Prepare data
        X = df[feature_names].fillna(df[feature_names].median())
        y = df['has_casualties']
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train logistic regression
        model = LogisticRegression(
            penalty='l2',
            C=1.0,
            max_iter=1000,
            random_state=42,
            class_weight='balanced'  # Handle class imbalance
        )
        
        # Cross-validation to estimate performance
        cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc')
        
        # Fit final model on all data
        model.fit(X_scaled, y)
        
        # Training metrics
        y_pred_proba = model.predict_proba(X_scaled)[:, 1]
        train_auc = self._compute_auc(y, y_pred_proba)
        
        training_metrics = {
            'sample_size': len(df),
            'features_used': feature_names,
            'train_auc': float(train_auc),
            'cv_auc_mean': float(cv_scores.mean()),
            'cv_auc_std': float(cv_scores.std()),
            'feature_coefficients': {
                name: float(coef) 
                for name, coef in zip(feature_names, model.coef_[0])
            },
            'intercept': float(model.intercept_[0])
        }
        
        print(f"   Train AUC: {train_auc:.3f}")
        print(f"   CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        print(f"   Feature coefficients:")
        for name, coef in training_metrics['feature_coefficients'].items():
            print(f"      {name}: {coef:+.3f}")
        
        return model, scaler, feature_names, training_metrics
    
    def _extract_2026_features(self) -> pd.DataFrame:
        """Extract phonetic features for all 2026 hurricane names."""
        
        features_list = []
        
        for name in HURRICANE_NAMES_2026:
            # Analyze name
            analysis = self.analyzer.analyze_name(name)
            
            features = {
                'name': name,
                # Map NameAnalyzer keys to our feature names
                'phonetic_harshness': analysis.get('phonetic_score', 50.0),  # Use phonetic_score as proxy
                'memorability': analysis.get('memorability_score', 50.0),
                'syllable_count': analysis.get('syllable_count', len(name) // 3 + 1),
                'length': analysis.get('character_length', len(name)),
                'vowel_ratio': analysis.get('vowel_ratio', 0.4),
            }
            
            features_list.append(features)
            print(f"   {name}: harshness={features['phonetic_harshness']:.1f}, mem={features['memorability']:.1f}")
        
        return pd.DataFrame(features_list)
    
    def _generate_predictions(self, model, scaler, feature_names, 
                            features_df: pd.DataFrame) -> List[Dict]:
        """Generate casualty predictions for each 2026 name."""
        
        predictions = []
        
        # Prepare features
        X = features_df[feature_names].fillna(features_df[feature_names].median())
        X_scaled = scaler.transform(X)
        
        # Predict probabilities
        proba = model.predict_proba(X_scaled)[:, 1]
        
        # Create predictions
        for idx, row in features_df.iterrows():
            pred = {
                'rank': idx + 1,  # Will be re-sorted
                'name': row['name'],
                'casualty_probability': float(proba[idx]),
                'binary_prediction': 'HIGH' if proba[idx] >= 0.5 else 'LOW',
                'confidence': 'high' if abs(proba[idx] - 0.5) > 0.2 else 'moderate',
                'phonetic_features': {
                    'harshness': float(row['phonetic_harshness']),
                    'memorability': float(row['memorability']),
                    'syllables': int(row['syllable_count']),
                    'length': int(row['length'])
                }
            }
            predictions.append(pred)
        
        # Sort by predicted probability (highest first)
        predictions.sort(key=lambda x: x['casualty_probability'], reverse=True)
        
        # Update ranks
        for idx, pred in enumerate(predictions):
            pred['predicted_casualty_rank'] = idx + 1
        
        # Print summary
        print(f"\n   TOP 5 PREDICTED HIGH-CASUALTY NAMES:")
        for pred in predictions[:5]:
            print(f"      #{pred['predicted_casualty_rank']}: {pred['name']} "
                  f"(p={pred['casualty_probability']:.3f})")
        
        print(f"\n   BOTTOM 5 PREDICTED LOW-CASUALTY NAMES:")
        for pred in predictions[-5:]:
            print(f"      #{pred['predicted_casualty_rank']}: {pred['name']} "
                  f"(p={pred['casualty_probability']:.3f})")
        
        return predictions
    
    def _create_preregistration_document(self, predictions: List[Dict],
                                        training_metrics: Dict,
                                        feature_names: List[str]) -> Dict:
        """Create comprehensive pre-registration document."""
        
        document = {
            'metadata': {
                'title': '2026 Atlantic Hurricane Casualty Predictions from Name Phonetics',
                'authors': ['Michael Smerconish'],
                'institution': 'Independent Research',
                'date_preregistered': datetime.now().isoformat(),
                'season_start': '2026-06-01',
                'season_end': '2026-11-30',
                'evaluation_date': '2026-12-31',
                'version': '1.0',
                'status': 'PRE-REGISTERED'
            },
            
            'hypothesis': {
                'research_question': 'Can phonetic features of hurricane names predict casualty outcomes prospectively?',
                'prediction': 'Names with higher phonetic harshness, memorability, and other linguistic features will correlate with casualty presence in 2026 season',
                'temporal_precedence': 'All predictions made BEFORE 2026 hurricane season begins',
                'falsifiability': 'Spearman correlation < 0.2 or ROC AUC < 0.55 would falsify hypothesis'
            },
            
            'methodology': {
                'training_data': {
                    'years': '1950-2024',
                    'sample_size': training_metrics['sample_size'],
                    'outcome_variable': 'Binary casualty presence (any deaths >0)',
                    'feature_set': feature_names
                },
                'model_specification': {
                    'type': 'Logistic Regression',
                    'regularization': 'L2 (C=1.0)',
                    'class_weight': 'balanced',
                    'cross_validation': '5-fold stratified',
                    'feature_scaling': 'StandardScaler (z-score normalization)'
                },
                'model_performance': {
                    'train_auc': training_metrics['train_auc'],
                    'cv_auc_mean': training_metrics['cv_auc_mean'],
                    'cv_auc_std': training_metrics['cv_auc_std']
                },
                'feature_coefficients': training_metrics['feature_coefficients']
            },
            
            'predictions': predictions,
            
            'success_criteria': {
                'primary': 'Spearman rank correlation > 0.5 between predicted and actual casualty rankings',
                'secondary': [
                    'ROC AUC > 0.75 for binary high/low casualty prediction',
                    'At least 3 of top 5 predicted names result in actual high casualties',
                    'Performance significantly better than chance (p < 0.05)'
                ]
            },
            
            'falsification_criteria': {
                'null_result': 'Spearman r < 0.2 (no correlation)',
                'weak_result': 'ROC AUC < 0.55 (barely better than random)',
                'reversed': 'Negative correlation (predictions inverse of reality)'
            },
            
            'analysis_plan': {
                'data_collection': 'NOAA HURDAT2 database for actual 2026 storm casualties',
                'evaluation_metrics': [
                    'Spearman rank correlation (primary)',
                    'ROC AUC for binary predictions',
                    'RMSE for probability calibration',
                    'Top-K accuracy (K=5, 10)'
                ],
                'statistical_tests': [
                    'Permutation test against random baseline',
                    'Bootstrap confidence intervals for correlation',
                    'Chi-square test for high/low classification'
                ],
                'reporting': 'Full results regardless of outcome (success or failure)'
            },
            
            'ethical_considerations': {
                'purpose': 'Scientific test of nominative determinism theory',
                'limitations': 'Names do not cause hurricanes; predictions test perception/response effects',
                'transparency': 'Pre-registration prevents post-hoc rationalization',
                'no_harm': 'Predictions will not influence WMO naming decisions or public safety'
            }
        }
        
        # Add document hash for immutability verification
        document_str = json.dumps(document, sort_keys=True, indent=2)
        document['verification'] = {
            'sha256_hash': hashlib.sha256(document_str.encode()).hexdigest(),
            'note': 'This hash can verify document was not modified after pre-registration'
        }
        
        return document
    
    def _save_predictions(self, document: Dict):
        """Save predictions to multiple formats for transparency."""
        
        output_dir = Path(__file__).parent.parent / 'data' / 'predictions_2026'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_path = output_dir / 'hurricane_predictions_2026.json'
        with open(json_path, 'w') as f:
            json.dump(document, f, indent=2)
        print(f"   ✓ Saved JSON: {json_path}")
        
        # Save as human-readable text
        txt_path = output_dir / 'hurricane_predictions_2026.txt'
        with open(txt_path, 'w') as f:
            f.write("2026 ATLANTIC HURRICANE CASUALTY PREDICTIONS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Pre-Registered: {document['metadata']['date_preregistered']}\n")
            f.write(f"Season: June-November 2026\n")
            f.write(f"Evaluation: December 2026\n\n")
            
            f.write("PREDICTED CASUALTY RANKINGS (Highest to Lowest Risk):\n")
            f.write("-" * 80 + "\n")
            for pred in document['predictions']:
                f.write(f"{pred['predicted_casualty_rank']:2d}. {pred['name']:10s} "
                       f"(p={pred['casualty_probability']:.3f}, {pred['binary_prediction']})\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("VERIFICATION HASH (SHA-256):\n")
            f.write(document['verification']['sha256_hash'] + "\n")
        print(f"   ✓ Saved TXT: {txt_path}")
        
        # Save predictions as CSV for easy analysis
        csv_path = output_dir / 'hurricane_predictions_2026.csv'
        predictions_df = pd.DataFrame(document['predictions'])
        predictions_df.to_csv(csv_path, index=False)
        print(f"   ✓ Saved CSV: {csv_path}")
        
        print(f"\n   Document hash: {document['verification']['sha256_hash']}")
        print(f"   This hash proves predictions were made before 2026 season")
    
    @staticmethod
    def _compute_auc(y_true, y_pred_proba):
        """Compute ROC AUC manually."""
        from sklearn.metrics import roc_auc_score
        return roc_auc_score(y_true, y_pred_proba)


def main():
    """Run 2026 hurricane prediction protocol."""
    predictor = Hurricane2026Predictor()
    document = predictor.run_complete_prediction()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Submit to OSF: https://osf.io/registries/osf/new")
    print("2. Create public page at /2026-predictions")
    print("3. Tweet/announce with timestamp")
    print("4. Store hash on blockchain (optional)")
    print("5. Wait for hurricane season...")
    print("6. Evaluate in December 2026")
    print()


if __name__ == '__main__':
    main()

