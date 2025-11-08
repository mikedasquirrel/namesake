"""
Sport-Specific Analyzer
Analyzes each sport independently to find which linguistic features predict success
"""

import json
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from typing import Dict, List, Tuple, Any
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.name_analyzer import NameAnalyzer
from utils.phonetic_analysis import PhoneticAnalyzer
from utils.visual_name_transformer import VisualNameTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SportSpecificAnalyzer:
    """
    Analyze one sport to determine which name features predict success
    """
    
    def __init__(self, sport_name: str, sport_characteristics: Dict[str, Any]):
        self.sport = sport_name
        self.characteristics = sport_characteristics
        self.athletes_df = None
        self.linguistic_features_df = None
        self.results = {}
        
    def load_athlete_data(self, db_path: str = None):
        """Load athlete data from database"""
        if db_path is None:
            db_path = f"analysis_outputs/sports_meta_analysis/{self.sport}_athletes.db"
        
        try:
            conn = sqlite3.connect(db_path)
            self.athletes_df = pd.read_sql_query("SELECT * FROM athletes", conn)
            conn.close()
            logger.info(f"Loaded {len(self.athletes_df)} athletes for {self.sport}")
            return True
        except Exception as e:
            logger.error(f"Could not load data for {self.sport}: {e}")
            return False
    
    def extract_linguistic_features(self):
        """
        Extract all linguistic features from athlete names
        Uses all 6 transformation formulas
        """
        logger.info(f"Extracting linguistic features for {len(self.athletes_df)} athletes...")
        
        name_analyzer = NameAnalyzer()
        phonetic_analyzer = PhoneticAnalyzer()
        transformer = VisualNameTransformer()
        
        features_list = []
        
        for idx, row in self.athletes_df.iterrows():
            name = row['full_name']
            
            try:
                # Phonetic features
                phonetic = phonetic_analyzer.analyze(name)
                
                # Visual features from all 6 formulas
                visual_features = {}
                for formula_type in ['phonetic', 'semantic', 'structural', 
                                    'frequency', 'numerological', 'hybrid']:
                    result = transformer.transform(name, formula_type=formula_type)
                    visual_features[f'{formula_type}_complexity'] = result['properties'].get('complexity', 0)
                    visual_features[f'{formula_type}_symmetry'] = result['properties'].get('symmetry', 0)
                    visual_features[f'{formula_type}_hue'] = result['properties'].get('hue', 0)
                
                # Basic name properties
                name_parts = name.split()
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[-1] if len(name_parts) > 1 else ''
                
                features = {
                    'athlete_id': row['athlete_id'],
                    'name': name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'success_score': row['success_score'],
                    
                    # Basic features
                    'total_syllables': phonetic.get('total_syllables', 0),
                    'syllables_first': phonetic.get('syllables_first_name', 0),
                    'syllables_last': phonetic.get('syllables_last_name', 0),
                    'character_length': len(name.replace(' ', '')),
                    'word_count': len(name_parts),
                    
                    # Phonetic features
                    'harshness_score': phonetic.get('harshness_score', 0),
                    'softness_score': phonetic.get('softness_score', 0),
                    'memorability_score': phonetic.get('memorability_score', 0),
                    'pronounceability': phonetic.get('pronounceability', 0),
                    'vowel_ratio': phonetic.get('vowel_ratio', 0),
                    'consonant_clusters': phonetic.get('consonant_clusters', 0),
                    'alliteration': 1 if len(name_parts) > 1 and name_parts[0][0].lower() == name_parts[-1][0].lower() else 0,
                    
                    # Visual features from formulas
                    **visual_features
                }
                
                features_list.append(features)
                
                if (idx + 1) % 100 == 0:
                    logger.info(f"Processed {idx + 1}/{len(self.athletes_df)} athletes")
                    
            except Exception as e:
                logger.warning(f"Could not analyze {name}: {e}")
                continue
        
        self.linguistic_features_df = pd.DataFrame(features_list)
        logger.info(f"Extracted {len(self.linguistic_features_df.columns)} features")
        
        return self.linguistic_features_df
    
    def calculate_correlations(self) -> Dict[str, float]:
        """
        Calculate correlations between linguistic features and success
        """
        logger.info("Calculating correlations...")
        
        if self.linguistic_features_df is None:
            logger.error("No linguistic features extracted yet")
            return {}
        
        # Get all numeric feature columns (exclude IDs and names)
        feature_cols = [col for col in self.linguistic_features_df.columns 
                       if col not in ['athlete_id', 'name', 'first_name', 'last_name', 'success_score']
                       and self.linguistic_features_df[col].dtype in [np.float64, np.int64]]
        
        correlations = {}
        
        for feature in feature_cols:
            try:
                # Remove any NaN values
                valid_data = self.linguistic_features_df[[feature, 'success_score']].dropna()
                
                if len(valid_data) > 10:  # Need minimum sample
                    r, p = stats.pearsonr(valid_data[feature], valid_data['success_score'])
                    correlations[feature] = {
                        'r': round(r, 4),
                        'p': round(p, 6),
                        'n': len(valid_data),
                        'significant': p < 0.05
                    }
            except Exception as e:
                logger.warning(f"Could not calculate correlation for {feature}: {e}")
        
        # Sort by absolute correlation strength
        self.results['correlations'] = dict(sorted(
            correlations.items(),
            key=lambda x: abs(x[1]['r']),
            reverse=True
        ))
        
        logger.info(f"Calculated {len(correlations)} correlations")
        return self.results['correlations']
    
    def identify_top_features(self, n: int = 10) -> List[Tuple[str, Dict]]:
        """Return top N most predictive features"""
        if 'correlations' not in self.results:
            self.calculate_correlations()
        
        top_features = list(self.results['correlations'].items())[:n]
        
        logger.info(f"Top {n} predictive features for {self.sport}:")
        for feature, stats_dict in top_features:
            logger.info(f"  {feature}: r={stats_dict['r']:.3f}, p={stats_dict['p']:.4f}")
        
        return top_features
    
    def build_prediction_model(self) -> Dict[str, Any]:
        """
        Build Random Forest model to predict success from name features
        """
        logger.info("Building prediction model...")
        
        if self.linguistic_features_df is None:
            logger.error("No features to build model with")
            return {}
        
        # Prepare data
        feature_cols = [col for col in self.linguistic_features_df.columns 
                       if col not in ['athlete_id', 'name', 'first_name', 'last_name', 'success_score']
                       and self.linguistic_features_df[col].dtype in [np.float64, np.int64]]
        
        X = self.linguistic_features_df[feature_cols].fillna(0)
        y = self.linguistic_features_df['success_score'].fillna(0)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        model.fit(X, y)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        # Feature importance
        feature_importance = dict(zip(feature_cols, model.feature_importances_))
        top_features = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10])
        
        model_results = {
            'r2_score': model.score(X, y),
            'cv_scores': {
                'mean': cv_scores.mean(),
                'std': cv_scores.std(),
                'scores': cv_scores.tolist()
            },
            'top_10_features': {k: round(v, 4) for k, v in top_features.items()},
            'n_features': len(feature_cols),
            'n_samples': len(X)
        }
        
        self.results['prediction_model'] = model_results
        
        logger.info(f"Model R² score: {model_results['r2_score']:.3f}")
        logger.info(f"CV R² score: {model_results['cv_scores']['mean']:.3f} ± {model_results['cv_scores']['std']:.3f}")
        
        return model_results
    
    def test_hypotheses(self) -> Dict[str, Any]:
        """
        Test sport-specific hypotheses based on characteristics
        """
        logger.info("Testing sport-specific hypotheses...")
        
        hypotheses = {}
        
        # Hypothesis: Contact level predicts harshness importance
        if 'harshness_score' in self.results.get('correlations', {}):
            harshness_corr = self.results['correlations']['harshness_score']['r']
            contact_level = self.characteristics.get('contact_level', 0)
            
            hypotheses['contact_harshness'] = {
                'contact_level': contact_level,
                'harshness_effect': harshness_corr,
                'hypothesis': 'Higher contact → stronger harshness effect',
                'prediction': 'strong' if contact_level > 7 else 'moderate' if contact_level > 4 else 'weak',
                'observed': 'strong' if abs(harshness_corr) > 0.25 else 'moderate' if abs(harshness_corr) > 0.15 else 'weak'
            }
        
        # Hypothesis: Team size predicts brevity importance
        team_size = self.characteristics.get('team_structure', {}).get('team_size', 1)
        if 'total_syllables' in self.results.get('correlations', {}):
            syllable_corr = self.results['correlations']['total_syllables']['r']
            
            hypotheses['team_brevity'] = {
                'team_size': team_size,
                'syllable_effect': syllable_corr,
                'hypothesis': 'Larger teams → stronger short name advantage',
                'prediction': 'strong' if team_size > 9 else 'moderate' if team_size > 5 else 'weak',
                'observed': 'strong' if syllable_corr < -0.20 else 'moderate' if syllable_corr < -0.10 else 'weak'
            }
        
        # Hypothesis: Precision predicts memorability over harshness
        precision_score = self.characteristics.get('precision_vs_power', 5)
        if 'memorability_score' in self.results.get('correlations', {}):
            memo_corr = self.results['correlations']['memorability_score']['r']
            harsh_corr = self.results['correlations'].get('harshness_score', {}).get('r', 0)
            
            hypotheses['precision_memorability'] = {
                'precision_score': precision_score,
                'memorability_effect': memo_corr,
                'harshness_effect': harsh_corr,
                'memorability_dominance': memo_corr > harsh_corr,
                'hypothesis': 'High precision sports prioritize memorability',
                'prediction': memo_corr > harsh_corr if precision_score > 6 else harsh_corr > memo_corr
            }
        
        self.results['hypotheses'] = hypotheses
        return hypotheses
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate comprehensive analysis report"""
        if output_file is None:
            output_file = f"analysis_outputs/sports_meta_analysis/{self.sport}_analysis.json"
        
        report = {
            'sport': self.sport,
            'sport_characteristics': self.characteristics,
            'sample_size': len(self.athletes_df) if self.athletes_df is not None else 0,
            'analysis_date': pd.Timestamp.now().isoformat(),
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to: {output_file}")
        return output_file
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run all analysis steps"""
        logger.info(f"\n{'='*60}")
        logger.info(f"ANALYZING: {self.sport.upper()}")
        logger.info(f"{'='*60}\n")
        
        # Steps
        if not self.load_athlete_data():
            logger.error(f"Could not load data for {self.sport}")
            return {}
        
        self.extract_linguistic_features()
        self.calculate_correlations()
        self.identify_top_features()
        self.build_prediction_model()
        self.test_hypotheses()
        
        report_file = self.generate_report()
        
        logger.info(f"\n✓ {self.sport} analysis complete")
        logger.info(f"  Report: {report_file}\n")
        
        return self.results


def analyze_all_sports():
    """Analyze all available sports"""
    # Load sport characteristics
    with open('analysis_outputs/sports_meta_analysis/sport_characteristics.json', 'r') as f:
        characteristics_data = json.load(f)
    
    sports_characterized = characteristics_data['sports_characterized']
    
    all_results = {}
    
    for sport_name, characteristics in sports_characterized.items():
        try:
            analyzer = SportSpecificAnalyzer(sport_name, characteristics)
            results = analyzer.run_complete_analysis()
            all_results[sport_name] = results
        except Exception as e:
            logger.error(f"Error analyzing {sport_name}: {e}")
            all_results[sport_name] = {'error': str(e)}
    
    # Save combined results
    with open('analysis_outputs/sports_meta_analysis/all_sports_analysis.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info("\n" + "="*80)
    logger.info("ALL SPORTS ANALYSIS COMPLETE")
    logger.info("="*80)
    
    return all_results


if __name__ == "__main__":
    analyze_all_sports()

