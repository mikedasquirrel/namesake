"""
Base Analyzer Classes
Provides common functionality for all analyzer modules to reduce code duplication

Usage:
    class MyDomainAnalyzer(BaseStatisticalAnalyzer):
        def analyze(self, data):
            # Domain-specific logic
            pass
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    Base class for all analyzers
    Provides common initialization and utility methods
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results = {}
    
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by subclasses
        
        Args:
            data: Input data to analyze
            
        Returns:
            Dictionary of analysis results
        """
        pass
    
    def validate_data(self, data: Any) -> bool:
        """Validate input data - override in subclasses if needed"""
        return data is not None
    
    def log_analysis(self, message: str):
        """Log analysis progress"""
        self.logger.info(message)


class BaseStatisticalAnalyzer(BaseAnalyzer):
    """
    Base class for statistical analysis
    Provides common statistical methods
    """
    
    def __init__(self, min_sample_size: int = 30, alpha: float = 0.05):
        super().__init__()
        self.min_sample_size = min_sample_size
        self.alpha = alpha
    
    def calculate_correlation(self, x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Calculate correlation with significance test"""
        if len(x) < self.min_sample_size:
            self.logger.warning(f"Sample size {len(x)} below minimum {self.min_sample_size}")
        
        r, p = stats.pearsonr(x, y)
        
        return {
            'correlation': float(r),
            'p_value': float(p),
            'significant': p < self.alpha,
            'n': len(x)
        }
    
    def calculate_regression(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Simple linear regression"""
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        model = LinearRegression()
        model.fit(X, y)
        predictions = model.predict(X)
        
        return {
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'r_squared': float(r2_score(y, predictions)),
            'n': len(y)
        }
    
    def calculate_effect_size(self, group1: np.ndarray, group2: np.ndarray) -> Dict[str, float]:
        """Calculate Cohen's d effect size"""
        mean_diff = np.mean(group1) - np.mean(group2)
        pooled_std = np.sqrt((np.std(group1)**2 + np.std(group2)**2) / 2)
        
        cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
        
        return {
            'cohens_d': float(cohens_d),
            'mean_group1': float(np.mean(group1)),
            'mean_group2': float(np.mean(group2)),
            'effect_size_category': self._categorize_effect_size(cohens_d)
        }
    
    def _categorize_effect_size(self, d: float) -> str:
        """Categorize Cohen's d"""
        abs_d = abs(d)
        if abs_d < 0.2:
            return 'negligible'
        elif abs_d < 0.5:
            return 'small'
        elif abs_d < 0.8:
            return 'medium'
        else:
            return 'large'


class BaseLinguisticAnalyzer(BaseAnalyzer):
    """
    Base class for linguistic feature extraction
    Provides common linguistic analysis methods
    """
    
    def __init__(self):
        super().__init__()
        self._init_linguistic_tools()
    
    def _init_linguistic_tools(self):
        """Initialize linguistic analysis tools"""
        try:
            import pyphen
            self.hyphenator = pyphen.Pyphen(lang='en')
        except ImportError:
            self.logger.warning("pyphen not available, syllable counting will be approximate")
            self.hyphenator = None
    
    def extract_features(self, name: str) -> Dict[str, Any]:
        """Extract common linguistic features from a name"""
        return {
            'length': len(name),
            'syllables': self.count_syllables(name),
            'has_harsh_sounds': self.has_harsh_sounds(name),
            'memorability': self.calculate_memorability(name),
            'vowel_ratio': self.calculate_vowel_ratio(name)
        }
    
    def count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        if self.hyphenator:
            return len(self.hyphenator.inserted(word).split('-'))
        else:
            # Simple fallback
            return self._count_syllables_simple(word)
    
    def _count_syllables_simple(self, word: str) -> int:
        """Simple syllable counting fallback"""
        vowels = 'aeiouy'
        word = word.lower()
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        return max(1, count)
    
    def has_harsh_sounds(self, word: str) -> bool:
        """Check if word contains harsh consonants"""
        harsh_consonants = set('kgptbdxz')
        return any(c in word.lower() for c in harsh_consonants)
    
    def calculate_memorability(self, word: str) -> float:
        """Calculate memorability score (0-1)"""
        # Simple heuristic: shorter + fewer syllables = more memorable
        length_score = max(0, 1 - (len(word) - 3) / 10)
        syllable_score = max(0, 1 - (self.count_syllables(word) - 1) / 5)
        
        return (length_score + syllable_score) / 2
    
    def calculate_vowel_ratio(self, word: str) -> float:
        """Calculate ratio of vowels to total letters"""
        vowels = 'aeiou'
        word_lower = word.lower()
        vowel_count = sum(1 for c in word_lower if c in vowels)
        return vowel_count / len(word) if word else 0


class BaseDomainAnalyzer(BaseStatisticalAnalyzer, BaseLinguisticAnalyzer):
    """
    Combined base class for domain analysis
    Provides both statistical and linguistic capabilities
    
    Use this for most domain-specific analyzers
    """
    
    def __init__(self, domain_name: str):
        BaseStatisticalAnalyzer.__init__(self)
        BaseLinguisticAnalyzer.__init__(self)
        self.domain_name = domain_name
    
    def analyze_domain(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Standard domain analysis pipeline
        
        Args:
            entities: List of entity dictionaries with 'name' and 'outcome' fields
            
        Returns:
            Complete analysis results
        """
        if not self.validate_data(entities):
            raise ValueError("Invalid data provided")
        
        # Extract features
        self.log_analysis(f"Analyzing {len(entities)} entities in {self.domain_name}")
        
        features = []
        outcomes = []
        
        for entity in entities:
            name = entity.get('name', '')
            outcome = entity.get('outcome', 0)
            
            if name and outcome is not None:
                features.append(self.extract_features(name))
                outcomes.append(outcome)
        
        # Statistical analysis
        results = {
            'domain': self.domain_name,
            'n_entities': len(entities),
            'n_analyzed': len(features),
            'features': features,
            'outcomes': outcomes
        }
        
        if len(features) >= self.min_sample_size:
            # Calculate correlations for key features
            syllables = np.array([f['syllables'] for f in features])
            harsh = np.array([f['has_harsh_sounds'] for f in features])
            outcomes_arr = np.array(outcomes)
            
            results['syllable_correlation'] = self.calculate_correlation(syllables, outcomes_arr)
            results['harsh_sounds_effect'] = self.calculate_effect_size(
                outcomes_arr[harsh == 1],
                outcomes_arr[harsh == 0]
            )
        
        return results


class BaseBettingAnalyzer(BaseAnalyzer):
    """
    Base class for betting/prediction analyzers
    """
    
    def __init__(self):
        super().__init__()
        self.min_confidence = 0.5
    
    def calculate_expected_value(self, win_prob: float, odds: int, stake: float = 100) -> float:
        """Calculate expected value of a bet"""
        if odds > 0:
            payout = stake * (odds / 100)
        else:
            payout = stake * (100 / abs(odds))
        
        ev = (win_prob * payout) - ((1 - win_prob) * stake)
        return ev
    
    def calculate_kelly_criterion(self, win_prob: float, odds: int) -> float:
        """Calculate optimal bet size using Kelly Criterion"""
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
        
        kelly = (win_prob * decimal_odds - 1) / (decimal_odds - 1)
        return max(0, kelly)  # Never bet negative

