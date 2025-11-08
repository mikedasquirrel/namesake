"""
Domain Formula Optimizer - Data-Driven Formula Discovery

This module discovers optimal formulas for each domain by letting the data speak.
Rather than imposing predetermined weights, we extract all possible features and
let statistical methods reveal which matter and how much.

Philosophy: The magical constants (0.993, 1.008) should emerge from the data,
not be imposed upon it. The formula should be discovered, not designed.

Author: Michael Andrew Smerconish Jr.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import (
    SelectKBest, mutual_info_regression, f_regression, RFE
)
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from analyzers.universal_statistical_suite import UniversalStatisticalSuite
from analyzers.phonetic_base import get_analyzer as get_phonetic_analyzer
from analyzers.phonetic_composites import get_composite_analyzer

logger = logging.getLogger(__name__)


@dataclass
class FormulaDiscovery:
    """Results from formula discovery process"""
    domain: str
    best_model_type: str
    feature_importances: Dict[str, float]
    feature_weights: Dict[str, float]
    performance_metrics: Dict[str, float]
    cross_validation_scores: Dict[str, float]
    formula_expression: str
    interpretations: Dict[str, str]
    magical_constants: List[Dict[str, Any]]  # Where 0.993/1.008 appear
    

@dataclass
class FeatureSet:
    """Complete feature extraction for a name"""
    name: str
    # Phonetic features (from existing analyzers)
    phonetic_complexity: float
    phonetic_symmetry: float
    phonetic_power: float
    phonetic_momentum: float
    phonetic_entropy: float
    phonetic_consonance: float
    
    # Structural features
    length: int
    syllable_count: int
    vowel_ratio: float
    consonant_clusters: int
    
    # Composite features
    complexity: float
    symmetry: float
    angular_vs_curved: float
    hue: float
    saturation: float
    brightness: float
    fractal_dimension: float
    pattern_density: float
    glow_intensity: float
    
    # Semantic features (if available)
    semantic_power: Optional[float] = None
    semantic_valence: Optional[float] = None
    
    # Meta features
    has_numbers: bool = False
    has_special_chars: bool = False
    is_alliterative: bool = False
    is_monosyllabic: bool = False


class DomainFormulaOptimizer:
    """
    Discover optimal formulas from data rather than imposing them.
    
    Process:
    1. Extract ALL possible features (50-100+)
    2. Test which features correlate with outcomes
    3. Compare multiple model types
    4. Select best model via cross-validation
    5. Extract feature importances/weights
    6. Look for magical constants in the weights
    """
    
    def __init__(self, domain_name: str):
        self.domain = domain_name
        self.stat_suite = UniversalStatisticalSuite()
        self.phonetic_analyzer = get_phonetic_analyzer()
        self.composite_analyzer = get_composite_analyzer()
        self.scaler = StandardScaler()
        
    def extract_all_features(self, name: str, context: Optional[Dict] = None) -> Dict[str, float]:
        """
        Extract every possible feature from a name.
        
        Returns: Dictionary with 50-100+ features
        """
        features = {}
        
        # Basic properties
        features['length'] = len(name)
        features['word_count'] = len(name.split())
        
        # Phonetic base features
        try:
            phonetic = self.phonetic_analyzer.analyze(name)
            for key, value in phonetic.items():
                if isinstance(value, (int, float)):
                    features[f'phonetic_{key}'] = value
        except Exception as e:
            logger.warning(f"Phonetic analysis failed for {name}: {e}")
        
        # Composite features
        try:
            composite = self.composite_analyzer.analyze(name)
            for key, value in composite.items():
                if isinstance(value, (int, float)):
                    features[f'composite_{key}'] = value
        except Exception as e:
            logger.warning(f"Composite analysis failed for {name}: {e}")
        
        # Syllable features
        syllables = self._count_syllables(name)
        features['syllable_count'] = syllables
        features['syllables_per_char'] = syllables / max(len(name), 1)
        features['is_monosyllabic'] = 1.0 if syllables == 1 else 0.0
        features['is_disyllabic'] = 1.0 if syllables == 2 else 0.0
        
        # Vowel/consonant features
        vowels = sum(1 for c in name.lower() if c in 'aeiou')
        consonants = sum(1 for c in name.lower() if c.isalpha() and c not in 'aeiou')
        features['vowel_count'] = vowels
        features['consonant_count'] = consonants
        features['vowel_ratio'] = vowels / max(len(name), 1)
        features['consonant_ratio'] = consonants / max(len(name), 1)
        features['vowel_consonant_ratio'] = vowels / max(consonants, 1)
        
        # Consonant clusters
        features['consonant_clusters'] = self._count_consonant_clusters(name)
        
        # Character type features
        features['has_numbers'] = 1.0 if any(c.isdigit() for c in name) else 0.0
        features['has_special_chars'] = 1.0 if any(not c.isalnum() and not c.isspace() for c in name) else 0.0
        features['has_uppercase'] = 1.0 if any(c.isupper() for c in name) else 0.0
        features['all_uppercase'] = 1.0 if name.isupper() else 0.0
        features['all_lowercase'] = 1.0 if name.islower() else 0.0
        
        # Alliteration
        features['is_alliterative'] = self._is_alliterative(name)
        
        # Repetition features
        features['repeated_chars'] = self._count_repeated_chars(name)
        features['max_repeated_char'] = self._max_consecutive_char(name)
        
        # Letter frequency features (first/last letter effects)
        if len(name) > 0:
            features['first_letter_numeric'] = ord(name[0].upper()) - ord('A') if name[0].isalpha() else 0
            features['last_letter_numeric'] = ord(name[-1].upper()) - ord('A') if name[-1].isalpha() else 0
        
        # Phonetic patterns
        features['starts_with_vowel'] = 1.0 if name and name[0].lower() in 'aeiou' else 0.0
        features['ends_with_vowel'] = 1.0 if name and name[-1].lower() in 'aeiou' else 0.0
        
        # Uniqueness (estimated)
        features['character_diversity'] = len(set(name.lower())) / max(len(name), 1)
        
        # Interaction features (quadratic terms for key features)
        if 'syllable_count' in features and 'length' in features:
            features['syllables_x_length'] = features['syllable_count'] * features['length']
        
        # Add domain-specific context if provided
        if context:
            for key, value in context.items():
                if isinstance(value, (int, float)):
                    features[f'context_{key}'] = value
        
        return features
    
    def extract_features_bulk(self, names: List[str], 
                             contexts: Optional[List[Dict]] = None) -> pd.DataFrame:
        """Extract features for multiple names"""
        if contexts is None:
            contexts = [None] * len(names)
        
        feature_dicts = []
        for name, context in zip(names, contexts):
            try:
                features = self.extract_all_features(name, context)
                features['name'] = name
                feature_dicts.append(features)
            except Exception as e:
                logger.warning(f"Feature extraction failed for {name}: {e}")
                continue
        
        return pd.DataFrame(feature_dicts)
    
    def discover_formula(self, names: List[str], outcomes: List[float],
                        contexts: Optional[List[Dict]] = None,
                        test_size: float = 0.2) -> FormulaDiscovery:
        """
        Main discovery process: find the optimal formula for this domain.
        
        Args:
            names: List of entity names
            outcomes: List of outcome values (success metric)
            contexts: Optional domain-specific context per entity
            test_size: Proportion for test set
            
        Returns:
            FormulaDiscovery with complete results
        """
        logger.info(f"🔍 Discovering formula for {self.domain} domain...")
        logger.info(f"   Sample size: {len(names)}, Outcomes range: [{min(outcomes):.2f}, {max(outcomes):.2f}]")
        
        # 1. Extract features
        logger.info("   Extracting features...")
        df = self.extract_features_bulk(names, contexts)
        df['outcome'] = outcomes[:len(df)]  # Match length
        
        # Remove NaN values
        df = df.dropna()
        
        if len(df) < 10:
            raise ValueError(f"Insufficient data after cleaning: {len(df)} samples")
        
        # Separate features and outcome
        feature_cols = [col for col in df.columns if col not in ['name', 'outcome']]
        X = df[feature_cols].values
        y = df['outcome'].values
        
        logger.info(f"   Features extracted: {len(feature_cols)}")
        
        # 2. Univariate feature selection
        logger.info("   Running univariate feature selection...")
        significant_features = self._univariate_selection(X, y, feature_cols)
        logger.info(f"   Significant features: {len(significant_features)}")
        
        # 3. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # 4. Compare models
        logger.info("   Comparing models...")
        model_results = self._compare_models(X_train, y_train, X_test, y_test)
        
        # 5. Select best model
        best_model_name = max(model_results.items(), 
                            key=lambda x: x[1]['cv_score'])[0]
        best_model = model_results[best_model_name]['model']
        
        logger.info(f"   Best model: {best_model_name} (CV R² = {model_results[best_model_name]['cv_score']:.4f})")
        
        # 6. Extract feature importances
        feature_importances = self._extract_feature_importances(
            best_model, feature_cols
        )
        
        # 7. Look for magical constants
        magical_constants = self._find_magical_constants(
            feature_importances, model_results[best_model_name]
        )
        
        # 8. Build formula expression
        formula_expr = self._build_formula_expression(
            best_model_name, feature_importances, feature_cols
        )
        
        # 9. Performance metrics
        y_pred_train = best_model.predict(X_train)
        y_pred_test = best_model.predict(X_test)
        
        performance = {
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test)
        }
        
        # 10. Interpretations
        interpretations = self._generate_interpretations(
            feature_importances, performance, significant_features
        )
        
        return FormulaDiscovery(
            domain=self.domain,
            best_model_type=best_model_name,
            feature_importances=feature_importances,
            feature_weights=feature_importances,  # Same for now
            performance_metrics=performance,
            cross_validation_scores=model_results[best_model_name],
            formula_expression=formula_expr,
            interpretations=interpretations,
            magical_constants=magical_constants
        )
    
    def _univariate_selection(self, X: np.ndarray, y: np.ndarray, 
                             feature_names: List[str]) -> List[str]:
        """
        Test each feature individually against outcome.
        Return features with p < 0.10.
        """
        significant = []
        
        for i, feature_name in enumerate(feature_names):
            x = X[:, i]
            
            # Skip if no variance
            if np.std(x) == 0:
                continue
            
            # Correlation test
            r, p = stats.pearsonr(x, y)
            
            if p < 0.10:  # Liberal threshold for initial selection
                significant.append({
                    'name': feature_name,
                    'r': r,
                    'p': p
                })
        
        return significant
    
    def _compare_models(self, X_train: np.ndarray, y_train: np.ndarray,
                       X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Compare multiple model types with cross-validation.
        """
        models = {
            'Linear': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1),
            'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        }
        
        results = {}
        
        for name, model in models.items():
            try:
                # Fit
                model.fit(X_train, y_train)
                
                # Cross-validation on training set
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, 
                                           scoring='r2')
                
                # Test set performance
                y_pred = model.predict(X_test)
                test_r2 = r2_score(y_test, y_pred)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                
                results[name] = {
                    'model': model,
                    'cv_score': np.mean(cv_scores),
                    'cv_std': np.std(cv_scores),
                    'test_r2': test_r2,
                    'test_rmse': test_rmse
                }
            except Exception as e:
                logger.warning(f"Model {name} failed: {e}")
                continue
        
        return results
    
    def _extract_feature_importances(self, model, feature_names: List[str]) -> Dict[str, float]:
        """
        Extract feature importances/coefficients from model.
        """
        importances = {}
        
        if hasattr(model, 'feature_importances_'):
            # Tree-based models
            for name, importance in zip(feature_names, model.feature_importances_):
                importances[name] = float(importance)
        elif hasattr(model, 'coef_'):
            # Linear models
            for name, coef in zip(feature_names, model.coef_):
                importances[name] = float(abs(coef))
        
        # Sort by importance
        importances = dict(sorted(importances.items(), 
                                 key=lambda x: abs(x[1]), 
                                 reverse=True))
        
        return importances
    
    def _find_magical_constants(self, feature_importances: Dict[str, float],
                                model_results: Dict) -> List[Dict[str, Any]]:
        """
        Look for the magical constants (0.993, 1.008) or other universal patterns.
        
        These might appear as:
        - Ratios between feature weights
        - Coefficients near these values
        - Equilibrium points in the formula
        """
        constants_found = []
        
        # Known magical constants to look for
        magical_values = [0.993, 0.9871, 0.9885, 0.9956, 0.9995, 0.9919, 0.9924,
                         1.008, 1.0136, 1.0120, 1.0045, 1.0005, 1.0086, 1.0079]
        
        # Check feature weights
        for name, weight in feature_importances.items():
            for magic in magical_values:
                if abs(weight - magic) < 0.01:  # Within 1%
                    constants_found.append({
                        'type': 'feature_weight',
                        'feature': name,
                        'value': weight,
                        'magical_constant': magic,
                        'difference': abs(weight - magic)
                    })
        
        # Check ratios between top features
        top_features = list(feature_importances.items())[:10]
        for i in range(len(top_features)):
            for j in range(i+1, len(top_features)):
                name1, weight1 = top_features[i]
                name2, weight2 = top_features[j]
                
                if weight2 != 0:
                    ratio = weight1 / weight2
                    
                    for magic in magical_values:
                        if abs(ratio - magic) < 0.01:
                            constants_found.append({
                                'type': 'feature_ratio',
                                'numerator': name1,
                                'denominator': name2,
                                'ratio': ratio,
                                'magical_constant': magic,
                                'difference': abs(ratio - magic)
                            })
        
        # Check R² and adjusted R² (might be near equilibrium)
        if 'test_r2' in model_results:
            r2 = model_results['test_r2']
            for magic in magical_values:
                if abs(r2 - magic) < 0.01:
                    constants_found.append({
                        'type': 'model_r2',
                        'value': r2,
                        'magical_constant': magic,
                        'difference': abs(r2 - magic)
                    })
        
        return constants_found
    
    def _build_formula_expression(self, model_type: str, 
                                  feature_importances: Dict[str, float],
                                  feature_names: List[str]) -> str:
        """
        Build human-readable formula expression.
        """
        # Get top 10 features
        top_features = list(feature_importances.items())[:10]
        
        expr = f"Outcome = f("
        for i, (name, weight) in enumerate(top_features):
            if i > 0:
                expr += " + "
            expr += f"{weight:.4f}×{name}"
        expr += ")"
        
        expr += f"\n\nModel: {model_type}"
        expr += f"\nTop predictors: {', '.join([f[0] for f in top_features[:5]])}"
        
        return expr
    
    def _generate_interpretations(self, feature_importances: Dict[str, float],
                                  performance: Dict[str, float],
                                  significant_features: List[Dict]) -> Dict[str, str]:
        """
        Generate human-readable interpretations.
        """
        interp = {}
        
        # Overall performance
        test_r2 = performance['test_r2']
        if test_r2 < 0.10:
            interp['overall'] = "Weak predictive power - names explain <10% of variance"
        elif test_r2 < 0.30:
            interp['overall'] = "Moderate predictive power - names explain some variance"
        elif test_r2 < 0.50:
            interp['overall'] = "Good predictive power - names are meaningful predictors"
        else:
            interp['overall'] = "Strong predictive power - names substantially predict outcomes"
        
        # Top feature
        if feature_importances:
            top_feature = list(feature_importances.keys())[0]
            interp['top_feature'] = f"{top_feature} is the strongest predictor"
        
        # Feature count
        interp['n_significant'] = f"{len(significant_features)} features show univariate significance"
        
        return interp
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count"""
        word = word.lower()
        count = 0
        vowels = 'aeiou'
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            count -= 1
        
        # Ensure at least 1
        if count == 0:
            count = 1
        
        return count
    
    def _count_consonant_clusters(self, text: str) -> int:
        """Count consonant clusters (2+ consecutive consonants)"""
        text = text.lower()
        clusters = 0
        consonant_run = 0
        
        for char in text:
            if char.isalpha() and char not in 'aeiou':
                consonant_run += 1
            else:
                if consonant_run >= 2:
                    clusters += 1
                consonant_run = 0
        
        if consonant_run >= 2:
            clusters += 1
        
        return clusters
    
    def _is_alliterative(self, text: str) -> float:
        """Check if alliterative (repeated initial sounds)"""
        words = text.split()
        if len(words) < 2:
            return 0.0
        
        initials = [w[0].lower() for w in words if w]
        if len(set(initials)) < len(initials):
            return 1.0
        return 0.0
    
    def _count_repeated_chars(self, text: str) -> int:
        """Count how many characters appear more than once"""
        from collections import Counter
        counts = Counter(text.lower())
        return sum(1 for c, count in counts.items() if count > 1 and c.isalpha())
    
    def _max_consecutive_char(self, text: str) -> int:
        """Maximum consecutive repetition of any character"""
        if not text:
            return 0
        
        max_run = 1
        current_run = 1
        
        for i in range(1, len(text)):
            if text[i].lower() == text[i-1].lower():
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        
        return max_run


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def discover_domain_formula(domain_name: str, names: List[str], 
                           outcomes: List[float],
                           contexts: Optional[List[Dict]] = None) -> FormulaDiscovery:
    """
    One-line function to discover optimal formula for a domain.
    
    Usage:
        discovery = discover_domain_formula('NBA', player_names, ppg_values)
        print(discovery.formula_expression)
        print(f"R² = {discovery.performance_metrics['test_r2']:.3f}")
    """
    optimizer = DomainFormulaOptimizer(domain_name)
    return optimizer.discover_formula(names, outcomes, contexts)

