"""
Test Base Analyzer Classes
Tests for the common analyzer functionality
"""

import pytest
import numpy as np
from analyzers.base_analyzer import (
    BaseStatisticalAnalyzer,
    BaseLinguisticAnalyzer,
    BaseDomainAnalyzer,
    BaseBettingAnalyzer
)


class TestBaseStatisticalAnalyzer:
    """Test statistical analysis methods"""
    
    def test_calculate_correlation(self):
        """Test correlation calculation"""
        analyzer = BaseStatisticalAnalyzer()
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        result = analyzer.calculate_correlation(x, y)
        
        assert 'correlation' in result
        assert 'p_value' in result
        assert 'significant' in result
        assert result['correlation'] == pytest.approx(1.0, abs=0.01)
        assert result['significant'] == True
    
    def test_calculate_effect_size(self):
        """Test Cohen's d calculation"""
        analyzer = BaseStatisticalAnalyzer()
        group1 = np.array([10, 12, 14, 16, 18])
        group2 = np.array([5, 7, 9, 11, 13])
        
        result = analyzer.calculate_effect_size(group1, group2)
        
        assert 'cohens_d' in result
        assert 'effect_size_category' in result
        assert result['cohens_d'] > 0
        assert result['effect_size_category'] in ['negligible', 'small', 'medium', 'large']


class TestBaseLinguisticAnalyzer:
    """Test linguistic analysis methods"""
    
    def test_count_syllables_simple(self):
        """Test syllable counting"""
        analyzer = BaseLinguisticAnalyzer()
        
        assert analyzer.count_syllables('tank') == 1
        assert analyzer.count_syllables('thunder') == 2
        assert analyzer.count_syllables('destroyer') == 3
        assert analyzer.count_syllables('basketball') == 3
    
    def test_has_harsh_sounds(self):
        """Test harsh sound detection"""
        analyzer = BaseLinguisticAnalyzer()
        
        assert analyzer.has_harsh_sounds('Tank') == True
        assert analyzer.has_harsh_sounds('Grace') == True
        assert analyzer.has_harsh_sounds('Emily') == False
        assert analyzer.has_harsh_sounds('Luna') == False
    
    def test_calculate_memorability(self):
        """Test memorability calculation"""
        analyzer = BaseLinguisticAnalyzer()
        
        # Short names should be more memorable
        memo_short = analyzer.calculate_memorability('Bob')
        memo_long = analyzer.calculate_memorability('Bartholomew')
        
        assert 0 <= memo_short <= 1
        assert 0 <= memo_long <= 1
        assert memo_short > memo_long
    
    def test_extract_features(self):
        """Test complete feature extraction"""
        analyzer = BaseLinguisticAnalyzer()
        
        features = analyzer.extract_features('Tank')
        
        assert 'length' in features
        assert 'syllables' in features
        assert 'has_harsh_sounds' in features
        assert 'memorability' in features
        assert 'vowel_ratio' in features
        
        assert features['length'] == 4
        assert features['has_harsh_sounds'] == True


class TestBaseDomainAnalyzer:
    """Test domain analysis pipeline"""
    
    def test_analyze_domain(self, sample_names):
        """Test complete domain analysis"""
        analyzer = BaseDomainAnalyzer('test_domain')
        
        results = analyzer.analyze_domain(sample_names)
        
        assert 'domain' in results
        assert 'n_entities' in results
        assert 'features' in results
        assert 'outcomes' in results
        assert results['domain'] == 'test_domain'
        assert results['n_entities'] == len(sample_names)


class TestBaseBettingAnalyzer:
    """Test betting analysis methods"""
    
    def test_calculate_expected_value(self):
        """Test EV calculation"""
        analyzer = BaseBettingAnalyzer()
        
        # Positive odds (+200)
        ev_positive = analyzer.calculate_expected_value(0.5, 200, 100)
        assert isinstance(ev_positive, float)
        
        # Negative odds (-150)
        ev_negative = analyzer.calculate_expected_value(0.6, -150, 100)
        assert isinstance(ev_negative, float)
    
    def test_calculate_kelly_criterion(self):
        """Test Kelly Criterion calculation"""
        analyzer = BaseBettingAnalyzer()
        
        kelly = analyzer.calculate_kelly_criterion(0.6, -110)
        
        assert isinstance(kelly, float)
        assert kelly >= 0  # Should never be negative
        assert kelly <= 1  # Should never exceed 100% bankroll

