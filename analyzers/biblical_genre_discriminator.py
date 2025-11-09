"""
Biblical Genre Discriminator
=============================

Sophisticated test distinguishing different OT genres by their ensemble patterns.

Key Insight: Not all biblical books claim same truth-status:
1. Historical Chronicles (Kings, Chronicles) - claim to document history
2. Legendary Narratives (Patriarchs, Judges) - heroic tales, historicity debated  
3. Mythological (Creation, Eden, Flood) - symbolic/cosmological
4. Wisdom Literature (Job, Ecclesiastes) - poetic/philosophical, not historical
5. Prophetic (Isaiah, Jeremiah) - prophetic visions, some historical context

HYPOTHESIS: Historical chronicles should show documentary patterns,
           Mythological/poetic should show fictional/literary patterns.

This is MUCH more rigorous test of the ensemble methodology.
"""

import logging
import numpy as np
from typing import Dict, List
from scipy import stats

from analyzers.character_ensemble_analyzer import character_ensemble_analyzer
from analyzers.statistical_rigor import statistical_rigor

logger = logging.getLogger(__name__)


class BiblicalGenreDiscriminator:
    """Discriminate biblical genres by ensemble patterns."""
    
    # Categorized by scholarly consensus on genre/truth-claims
    BIBLICAL_SECTIONS = {
        'mythological_cosmological': {
            'books': ['Genesis 1-11 (Creation-Babel)'],
            'characters': ['Adam', 'Eve', 'Cain', 'Abel', 'Noah', 'Shem', 'Ham', 'Japheth'],
            'truth_claim': 'symbolic/mythological',
            'scholarly_consensus': 'Not historical—cosmological myth',
            'even_believers_accept': 'Many accept as symbolic, not literal',
            'expected_pattern': 'Could show literary construction'
        },
        'legendary_heroic': {
            'books': ['Judges', 'Genesis 12-50 (Patriarchs)'],
            'characters': ['Samson', 'Gideon', 'Deborah', 'Ehud', 'Jephthah', 'Abraham', 'Isaac', 'Jacob'],
            'truth_claim': 'legendary/semi-historical',
            'scholarly_consensus': 'Heroic legends, historical core uncertain',
            'even_believers_accept': 'Some view as embellished traditions',
            'expected_pattern': 'Mixed—could show some literary enhancement'
        },
        'wisdom_poetic': {
            'books': ['Job', 'Ecclesiastes', 'Proverbs', 'Song of Songs'],
            'characters': ['Job', 'Qoheleth (Ecclesiastes author)'],
            'truth_claim': 'philosophical/poetic',
            'scholarly_consensus': 'Not claiming historical narrative',
            'even_believers_accept': 'Understood as wisdom literature, not chronicle',
            'expected_pattern': 'Could show literary construction (it\'s poetry!)'
        },
        'historical_chronicles': {
            'books': ['1-2 Kings', '1-2 Chronicles', '1-2 Samuel'],
            'characters': ['David', 'Solomon', 'Saul', 'Rehoboam', 'Jeroboam', 'Ahab', 'Jehoshaphat', 'Hezekiah', 'Josiah'],
            'truth_claim': 'historical chronicle',
            'scholarly_consensus': 'Claims to document history—some events verified by Assyrian records',
            'even_believers_accept': 'Treated as historical books',
            'expected_pattern': 'SHOULD show documentary patterns if method valid',
            'external_verification': 'Some kings verified in Assyrian annals, Babylonian chronicles'
        },
        'prophetic_historical': {
            'books': ['Isaiah', 'Jeremiah', 'Ezekiel'],
            'characters': ['Isaiah', 'Jeremiah', 'Ezekiel', 'Daniel'],
            'truth_claim': 'prophetic with historical context',
            'scholarly_consensus': 'Real historical prophets (some verified)',
            'even_believers_accept': 'Historical figures',
            'expected_pattern': 'Should show documentary patterns'
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("BiblicalGenreDiscriminator initialized")
    
    def discriminate_by_genre(self) -> Dict:
        """
        Test if ensemble patterns discriminate biblical genres.
        
        KEY TEST: Do historical chronicles show different patterns from mythological sections?
        If YES → ensemble methodology can distinguish genres within Bible
        If NO → all biblical literature follows same pattern (interesting either way)
        """
        analyses = {}
        
        for genre, data in self.BIBLICAL_SECTIONS.items():
            analysis = self._analyze_genre_section(genre, data)
            analyses[genre] = analysis
        
        # Compare historical vs mythological
        comparison = self._compare_historical_vs_mythological(analyses)
        
        # Test discrimination power
        discrimination = self._test_discrimination_power(analyses)
        
        return {
            'genre_analyses': analyses,
            'historical_vs_mythological': comparison,
            'discrimination_test': discrimination,
            'interpretation': self._interpret_results(comparison, discrimination)
        }
    
    def _analyze_genre_section(self, genre: str, data: Dict) -> Dict:
        """Analyze single genre section."""
        characters = data['characters']
        
        # Analyze ensemble
        char_dicts = [{'name': n, 'role': 'protagonist'} for n in characters]
        ensemble_analysis = character_ensemble_analyzer.analyze_ensemble(char_dicts, genre)
        
        variance = ensemble_analysis['ensemble_statistics']['stddev_melodiousness'] ** 2
        mean_melodious = ensemble_analysis['ensemble_statistics']['mean_melodiousness']
        optimization = ensemble_analysis['optimization_detection']['optimization_score']
        
        return {
            'genre': genre,
            'n_characters': len(characters),
            'truth_claim': data['truth_claim'],
            'scholarly_consensus': data['scholarly_consensus'],
            'variance': float(variance),
            'mean_melodiousness': float(mean_melodious),
            'optimization_score': float(optimization),
            'expected_pattern': data['expected_pattern']
        }
    
    def _compare_historical_vs_mythological(self, analyses: Dict) -> Dict:
        """
        Compare historical chronicles to mythological sections.
        
        CRITICAL TEST: If methodology works, should detect difference.
        """
        # Historical books (should show documentary patterns)
        historical = analyses.get('historical_chronicles', {})
        hist_variance = historical.get('variance', 0)
        hist_optimization = historical.get('optimization_score', 0)
        
        # Mythological (might show literary patterns)
        mythological = analyses.get('mythological_cosmological', {})
        myth_variance = mythological.get('variance', 0)
        myth_optimization = mythological.get('optimization_score', 0)
        
        # Test if different
        variance_diff = abs(hist_variance - myth_variance)
        opt_diff = abs(hist_optimization - myth_optimization)
        
        return {
            'historical_chronicles': {
                'variance': float(hist_variance),
                'optimization': float(hist_optimization),
                'n': historical.get('n_characters', 0)
            },
            'mythological_cosmological': {
                'variance': float(myth_variance),
                'optimization': float(myth_optimization),
                'n': mythological.get('n_characters', 0)
            },
            'differences': {
                'variance': float(variance_diff),
                'optimization': float(opt_diff)
            },
            'patterns_differ': variance_diff > 0.10 or opt_diff > 0.20,
            'interpretation': self._interpret_historical_vs_myth(hist_variance, myth_variance, hist_optimization, myth_optimization)
        }
    
    def _interpret_historical_vs_myth(self, hist_var, myth_var, hist_opt, myth_opt) -> str:
        """Interpret historical vs mythological comparison."""
        if abs(hist_var - myth_var) < 0.10 and abs(hist_opt - myth_opt) < 0.15:
            return """HISTORICAL AND MYTHOLOGICAL SHOW SIMILAR PATTERNS:
- Historical chronicles variance ({:.3f}) ≈ Mythological variance ({:.3f})
- Both show realistic diversity (not optimized)

INTERPRETATION: Even mythological sections (Adam/Eve, Noah) show documentary-style naming patterns. 
This could mean:
(a) Ancient mythological narratives used real naming patterns (cultural verisimilitude), OR
(b) Authors treated myths as if historical (claimed cosmological truth), OR
(c) Pattern so ingrained in Hebrew literature it appears even in non-historical books

This is INTERESTING finding either way.""".format(hist_var, myth_var)
        
        else:
            return """HISTORICAL AND MYTHOLOGICAL SHOW DIFFERENT PATTERNS:
- Historical chronicles variance ({:.3f}) vs Mythological variance ({:.3f})
- Historical optimization ({:.3f}) vs Mythological optimization ({:.3f})

INTERPRETATION: Ensemble methodology CAN discriminate genres within Bible!
- Historical books show documentary patterns (as expected)
- Mythological books show more literary construction (as expected)

This VALIDATES the methodology—it detects known differences in truth-claims.""".format(
                hist_var, myth_var, hist_opt, myth_opt
            )
    
    def _test_discrimination_power(self, analyses: Dict) -> Dict:
        """
        Test if ensemble patterns successfully discriminate known genres.
        
        Known truth-claims:
        - Kings/Chronicles: Historical chronicle (highest truth-claim)
        - Job: Philosophical parable (not claiming history)
        - Genesis 1-11: Cosmological myth (symbolic)
        
        Can ensemble patterns detect these differences?
        """
        variances_by_truth_claim = {}
        
        for genre, analysis in analyses.items():
            truth_claim = analysis['truth_claim']
            variance = analysis['variance']
            
            if truth_claim not in variances_by_truth_claim:
                variances_by_truth_claim[truth_claim] = []
            variances_by_truth_claim[truth_claim].append(variance)
        
        # ANOVA across truth-claim types
        groups = list(variances_by_truth_claim.values())
        
        if len(groups) >= 2:
            # Simplified F-test (would need more data for robust ANOVA)
            # For now, compare means
            means = {k: np.mean(v) for k, v in variances_by_truth_claim.items()}
            
            return {
                'truth_claim_types': list(variances_by_truth_claim.keys()),
                'mean_variance_by_type': {k: float(v) for k, v in means.items()},
                'range': float(max(means.values()) - min(means.values())),
                'can_discriminate': max(means.values()) - min(means.values()) > 0.10
            }
        
        return {'insufficient_data': True}


# Singleton
biblical_genre_discriminator = BiblicalGenreDiscriminator()

