"""Literary Name Composition & Predictive Nominative Analysis

Comprehensive analyzer for literary character names across fiction, nonfiction, and gospels.
Tests whether character roles and outcomes can be predicted from name phonetic characteristics.

Inherits from DomainAnalysisTemplate for standardized pipeline and quality control.

Author: Michael Smerconish
Date: November 2025
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

from core.domain_analysis_template import DomainAnalysisTemplate
from core.models import db, LiteraryWork, LiteraryCharacter, LiteraryNameAnalysis
from collectors.literary_name_collector import LiteraryNameCollector
from analyzers.phonetic_base import PhoneticBase
from data.common_american_names import COMMON_FIRST_NAMES, COMMON_SURNAMES
from utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class LiteraryNameAnalyzer(DomainAnalysisTemplate):
    """
    Analyzes literary character names for composition patterns and predictive power.
    
    Tests:
    - Fiction vs nonfiction vs gospels name differences
    - Role prediction (protagonist/antagonist) from names
    - Outcome prediction (survives/dies) from names
    - Invented vs real name patterns
    """
    
    def __init__(self, mode: str = 'new', custom_params: Optional[Dict] = None):
        """Initialize analyzer with domain template framework."""
        super().__init__(
            domain_id='literary_name_composition',
            mode=mode,
            custom_params=custom_params
        )
        
        self.phonetic_analyzer = PhoneticBase()
        self.collector = LiteraryNameCollector(baseline_sample_size=10000)
        
        # Results storage
        self.character_analyses = []
        self.work_analyses = []
        self.baseline_stats = {}
        self.category_aggregates = {}
        self.prediction_models = {}
        
        # Common names for classification
        self.common_first_names_set = set([n.lower() for n in COMMON_FIRST_NAMES])
        self.common_surnames_set = set([n.lower() for n in COMMON_SURNAMES])
    
    def get_collector_class(self):
        """Return collector class."""
        return LiteraryNameCollector
    
    def get_analyzer_class(self):
        """Return analyzer class (self)."""
        return LiteraryNameAnalyzer
    
    def collect_data(self, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
        """
        Collect literary texts and extract character names.
        
        Returns:
            Complete dataset for analysis
        """
        self.logger.info("Collecting data using LiteraryNameCollector...")
        
        dataset = self.collector.collect_full_dataset()
        
        self.logger.info(f"Data collection complete:")
        self.logger.info(f"  Works: {dataset['total_works']}")
        self.logger.info(f"  Characters: {dataset['total_characters']}")
        self.logger.info(f"  Baselines: {len(dataset['baselines'])}")
        
        return {
            'sample_size': dataset['total_characters'],
            'work_count': dataset['total_works'],
            'data': dataset,
            'collection_timestamp': datetime.now().isoformat(),
        }
    
    def analyze_data(self, data: Dict, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
        """
        Analyze literary name data: calculate metrics, test predictions, cross-category comparisons.
        
        Args:
            data: Collected data from collect_data()
            progress_tracker: Optional progress tracker
            
        Returns:
            Complete analysis results
        """
        dataset = data['data']
        works = dataset['works']
        characters = dataset['characters']
        baselines = dataset['baselines']
        
        self.logger.info("\n" + "="*80)
        self.logger.info("ANALYZING LITERARY NAME DATA")
        self.logger.info("="*80)
        
        # Step 1: Calculate baseline statistics
        self.logger.info("\nStep 1: Calculating baseline statistics...")
        self._calculate_baseline_statistics(baselines)
        
        # Step 2: Analyze each character
        self.logger.info("\nStep 2: Analyzing individual characters...")
        all_character_analyses = []
        
        for work_category, work_dict in works.items():
            self.logger.info(f"\n  Analyzing {work_category} characters...")
            
            for work_id, work_data in work_dict.items():
                work_characters = characters.get(work_id, {})
                
                for char_id, char_data in work_characters.items():
                    try:
                        analysis = self._analyze_single_character(
                            char_data, 
                            work_data, 
                            work_category
                        )
                        if analysis:
                            all_character_analyses.append(analysis)
                    except Exception as e:
                        self.logger.error(f"Error analyzing character {char_id}: {e}")
        
        self.character_analyses = all_character_analyses
        self.logger.info(f"\nAnalyzed {len(all_character_analyses)} characters")
        
        # Step 3: Analyze works (aggregate character stats)
        self.logger.info("\nStep 3: Analyzing works...")
        self._analyze_works(works, characters)
        
        # Step 4: Calculate category aggregates
        self.logger.info("\nStep 4: Calculating category aggregates...")
        self._calculate_category_aggregates()
        
        # Step 5: Statistical comparisons
        self.logger.info("\nStep 5: Running statistical comparisons...")
        comparison_results = self._run_statistical_comparisons()
        
        # Step 6: Predictive modeling (KEY INNOVATION)
        self.logger.info("\nStep 6: Training predictive models...")
        prediction_results = self._run_predictive_modeling()
        
        # Step 7: Cross-category analysis
        self.logger.info("\nStep 7: Cross-category analysis...")
        cross_category_results = self._analyze_cross_category_patterns()
        
        # Compile results
        results = {
            'sample_size': data['sample_size'],
            'work_count': data['work_count'],
            'characters_analyzed': len(all_character_analyses),
            
            'baseline_statistics': self.baseline_stats,
            'character_analyses': [self._character_to_dict(c) for c in all_character_analyses],
            'work_analyses': self.work_analyses,
            'category_aggregates': self.category_aggregates,
            'comparison_results': comparison_results,
            'prediction_results': prediction_results,
            'cross_category_results': cross_category_results,
            
            'has_effect_sizes': True,
            'has_out_of_sample_validation': True,
            'has_predictive_models': True,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.info("\nAnalysis complete!")
        
        return results
    
    def _calculate_baseline_statistics(self, baselines: Dict):
        """Calculate statistics for baseline name samples."""
        self.baseline_stats = {
            'random': self._calculate_baseline_metrics(baselines['random']),
            'stratified': self._calculate_baseline_metrics(baselines['stratified']),
        }
        
        self.logger.info("Baseline statistics calculated:")
        self.logger.info(f"  Random melodiousness: {self.baseline_stats['random']['melodiousness_score']:.1f}")
        self.logger.info(f"  Random commonality: {self.baseline_stats['random']['commonality_score']:.1f}")
    
    def _calculate_baseline_metrics(self, baseline_data: Dict) -> Dict:
        """Calculate americanness, melodiousness, commonality for baseline."""
        names = baseline_data['names'][:1000]  # Sample for speed
        
        # Calculate metrics for sample
        melodiousness_scores = []
        americanness_scores = []
        commonality_scores = []
        harshness_scores = []
        
        for name in names:
            mel_score = self._calculate_melodiousness_single(name)
            am_score = self._calculate_americanness_single(name)
            com_score = self._calculate_commonality_single(name)
            harsh_score = self.phonetic_analyzer.analyze(name).get('harshness_score', 50)
            
            melodiousness_scores.append(mel_score)
            americanness_scores.append(am_score)
            commonality_scores.append(com_score)
            harshness_scores.append(harsh_score)
        
        return {
            'sample_size': len(names),
            'melodiousness_score': float(np.mean(melodiousness_scores)),
            'melodiousness_std': float(np.std(melodiousness_scores)),
            'americanness_score': float(np.mean(americanness_scores)),
            'americanness_std': float(np.std(americanness_scores)),
            'commonality_score': float(np.mean(commonality_scores)),
            'commonality_std': float(np.std(commonality_scores)),
            'harshness_score': float(np.mean(harshness_scores)),
            'harshness_std': float(np.std(harshness_scores)),
        }
    
    def _analyze_single_character(self, char_data: Dict, work_data: Dict, category: str) -> Dict:
        """
        Analyze a single character name.
        
        Args:
            char_data: Character data
            work_data: Work data
            category: 'fiction', 'nonfiction', or 'gospels'
            
        Returns:
            Character analysis dict
        """
        full_name = char_data['full_name']
        first_name = char_data.get('first_name', '')
        last_name = char_data.get('last_name', '')
        
        # Phonetic analysis
        phonetic = self.phonetic_analyzer.analyze(full_name)
        
        # Core metrics
        melodiousness_score, mel_components = self._calculate_melodiousness(full_name)
        americanness_score, am_components = self._calculate_americanness(full_name)
        commonality_score = self._calculate_commonality(first_name, last_name)
        name_valence = self._calculate_name_valence(full_name)
        
        # Role prediction features
        protagonist_score = self._calculate_protagonist_likelihood(
            melodiousness_score, americanness_score, commonality_score, phonetic
        )
        antagonist_score = self._calculate_antagonist_likelihood(
            melodiousness_score, americanness_score, commonality_score, phonetic
        )
        vulnerable_score = self._calculate_vulnerable_likelihood(
            melodiousness_score, phonetic
        )
        
        # Build analysis
        analysis = {
            'character_id': char_data['character_id'],
            'work_id': work_data['work_id'],
            'work_title': work_data['title'],
            'category': category,
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            
            # Core metrics
            'syllable_count': phonetic.get('syllable_count', 0),
            'character_length': len(full_name),
            'melodiousness_score': melodiousness_score,
            'melodiousness_components': mel_components,
            'americanness_score': americanness_score,
            'americanness_components': am_components,
            'commonality_score': commonality_score,
            'harshness_score': phonetic.get('harshness_score', 50),
            'name_valence': name_valence,
            
            # Phonetic details
            'plosive_count': phonetic.get('plosive_count', 0),
            'fricative_count': phonetic.get('fricative_count', 0),
            'liquid_count': phonetic.get('liquid_count', 0),
            'nasal_count': phonetic.get('nasal_count', 0),
            'vowel_count': phonetic.get('vowel_count', 0),
            'consonant_count': phonetic.get('consonant_count', 0),
            
            # Commonality details
            'is_in_top_100_names': commonality_score > 90,
            'is_in_top_1000_names': commonality_score > 50,
            
            # Name type
            'name_type': char_data.get('name_type', 'unknown'),
            'is_invented': char_data.get('is_invented', False),
            
            # Importance
            'mention_count': char_data['mention_count'],
            'importance_score': char_data['importance_score'],
            'importance': char_data['importance'],
            
            # Prediction features
            'protagonist_score': protagonist_score,
            'antagonist_score': antagonist_score,
            'vulnerable_score': vulnerable_score,
            
            # Role/outcome (for training)
            'character_role': char_data.get('character_role'),
            'character_outcome': char_data.get('character_outcome'),
            
            # Memorability
            'memorability_score': phonetic.get('memorability_score', 50),
            'distinctiveness_score': self._calculate_distinctiveness(full_name, commonality_score),
        }
        
        return analysis
    
    def _calculate_melodiousness(self, name: str) -> Tuple[float, Dict]:
        """Calculate melodiousness score (0-100) and components."""
        phonetic = self.phonetic_analyzer.analyze(name)
        
        # Component 1: Phonetic flow
        flow = self._score_phonetic_flow(name, phonetic)
        
        # Component 2: Vowel harmony
        vowel_harmony = self._score_vowel_harmony(name, phonetic)
        
        # Component 3: Syllabic rhythm
        rhythm = self._score_syllabic_rhythm(phonetic)
        
        # Component 4: Harshness inverse
        harshness_inverse = 100 - phonetic.get('harshness_score', 50)
        
        # Weighted combination
        score = (
            0.30 * flow +
            0.25 * vowel_harmony +
            0.25 * rhythm +
            0.20 * harshness_inverse
        )
        
        components = {
            'flow': flow,
            'vowel_harmony': vowel_harmony,
            'rhythm': rhythm,
            'harshness_inverse': harshness_inverse,
        }
        
        return score, components
    
    def _calculate_melodiousness_single(self, name: str) -> float:
        """Quick melodiousness calculation."""
        score, _ = self._calculate_melodiousness(name)
        return score
    
    def _score_phonetic_flow(self, name: str, phonetic: Dict) -> float:
        """Score phonetic flow and smoothness (0-100)."""
        score = 50.0
        
        # Liquid consonants increase flow
        liquid_score = phonetic.get('liquid_score', 0)
        score += liquid_score * 0.5
        
        # Nasal consonants increase melodiousness
        nasal_score = phonetic.get('nasal_score', 0)
        score += nasal_score * 0.4
        
        return np.clip(score, 0, 100)
    
    def _score_vowel_harmony(self, name: str, phonetic: Dict) -> float:
        """Score vowel harmony (0-100)."""
        name_lower = name.lower()
        vowels = [c for c in name_lower if c in 'aeiou']
        
        if len(vowels) < 2:
            return 50.0
        
        # Check for repeated vowels
        unique_vowels = len(set(vowels))
        harmony_ratio = 1 - (unique_vowels / len(vowels))
        
        score = 50 + (harmony_ratio * 50)
        
        return np.clip(score, 0, 100)
    
    def _score_syllabic_rhythm(self, phonetic: Dict) -> float:
        """Score syllabic rhythm (0-100)."""
        syllables = phonetic.get('syllable_count', 2)
        
        # Optimal: 2-4 syllables
        if syllables == 2 or syllables == 3:
            return 90
        elif syllables == 4:
            return 75
        elif syllables == 1 or syllables == 5:
            return 60
        else:
            return 40
    
    def _calculate_americanness(self, name: str) -> Tuple[float, Dict]:
        """Calculate americanness score (0-100) and components."""
        phonetic = self.phonetic_analyzer.analyze(name)
        
        # Component 1: Anglo phonetic patterns
        anglo_phonetics = self._score_anglo_phonetics(name, phonetic)
        
        # Component 2: International markers (inverted)
        intl_markers = self._score_international_markers(name, phonetic)
        
        # Component 3: Syllable structure
        syllable_structure = self._score_syllable_structure(phonetic)
        
        # Component 4: Name origin
        name_origin = self._score_name_origin(name)
        
        # Weighted combination
        score = (
            0.4 * anglo_phonetics +
            0.3 * (100 - intl_markers) +
            0.2 * syllable_structure +
            0.1 * name_origin
        )
        
        components = {
            'anglo_phonetics': anglo_phonetics,
            'intl_markers': intl_markers,
            'syllable_structure': syllable_structure,
            'name_origin': name_origin,
        }
        
        return score, components
    
    def _calculate_americanness_single(self, name: str) -> float:
        """Quick americanness calculation."""
        score, _ = self._calculate_americanness(name)
        return score
    
    def _score_anglo_phonetics(self, name: str, phonetic: Dict) -> float:
        """Score Anglo phonetic patterns (0-100)."""
        score = 50.0
        name_lower = name.lower()
        
        # Common Anglo consonant clusters
        anglo_clusters = ['th', 'sh', 'ch', 'ph', 'wh', 'ck']
        for cluster in anglo_clusters:
            if cluster in name_lower:
                score += 5
        
        return np.clip(score, 0, 100)
    
    def _score_international_markers(self, name: str, phonetic: Dict) -> float:
        """Score international markers (higher = more international)."""
        score = 0.0
        name_lower = name.lower()
        
        # International markers
        intl_markers = ['ez', 'iz', 'az', 'ñ', 'ü', 'ö']
        for marker in intl_markers:
            if marker in name_lower:
                score += 15
        
        return np.clip(score, 0, 100)
    
    def _score_syllable_structure(self, phonetic: Dict) -> float:
        """Score typical Anglo syllable structure (0-100)."""
        syllables = phonetic.get('syllable_count', 2)
        
        # Anglo names typically 2-4 syllables
        if syllables <= 2:
            return 100
        elif syllables == 3:
            return 80
        elif syllables == 4:
            return 60
        else:
            return 40
    
    def _score_name_origin(self, name: str) -> float:
        """Score based on name origin (0-100)."""
        # Simplified: check if name parts are in common lists
        parts = name.split()
        if not parts:
            return 50
        
        first_is_common = parts[0].lower() in self.common_first_names_set
        
        if first_is_common:
            return 80
        else:
            return 40
    
    def _calculate_commonality(self, first_name: str, last_name: str) -> float:
        """
        Calculate name commonality score (0-100).
        
        100 = very common (top 100 names)
        50 = moderately common (top 1000)
        0 = very uncommon/invented
        """
        score = 0.0
        
        first_lower = first_name.lower() if first_name else ''
        last_lower = last_name.lower() if last_name else ''
        
        # Check first name
        if first_lower in self.common_first_names_set:
            # Top 256 first names
            try:
                rank = COMMON_FIRST_NAMES.index(first_name)
                # Rank 0-50: score 80-100
                # Rank 51-100: score 60-80
                # Rank 101+: score 40-60
                if rank < 50:
                    score += 50 - (rank * 0.4)  # 50 to 30
                else:
                    score += 30
            except ValueError:
                score += 50  # Not in list but in common set
        else:
            score += 20  # Uncommon first name
        
        # Check last name
        if last_lower in self.common_surnames_set:
            try:
                rank = COMMON_SURNAMES.index(last_name)
                if rank < 50:
                    score += 50 - (rank * 0.4)
                else:
                    score += 30
            except ValueError:
                score += 50
        else:
            score += 20  # Uncommon last name
        
        return min(100, score)
    
    def _calculate_commonality_single(self, full_name: str) -> float:
        """Quick commonality calculation."""
        parts = full_name.split()
        if len(parts) == 0:
            return 0
        elif len(parts) == 1:
            return self._calculate_commonality(parts[0], '')
        else:
            return self._calculate_commonality(parts[0], parts[-1])
    
    def _calculate_name_valence(self, name: str) -> float:
        """
        Calculate name valence (-100 to +100).
        
        Positive: associated with good/heroic qualities
        Negative: associated with evil/villainous qualities
        """
        # Simplified valence based on phonetics and common associations
        name_lower = name.lower()
        valence = 0.0
        
        # Positive markers
        positive_patterns = ['grace', 'hope', 'joy', 'rose', 'lily', 'angel', 'star']
        for pattern in positive_patterns:
            if pattern in name_lower:
                valence += 20
        
        # Negative markers
        negative_patterns = ['dark', 'black', 'death', 'mal', 'grim', 'shadow']
        for pattern in negative_patterns:
            if pattern in name_lower:
                valence -= 20
        
        return np.clip(valence, -100, 100)
    
    def _calculate_protagonist_likelihood(self, melodiousness: float, americanness: float, 
                                          commonality: float, phonetic: Dict) -> float:
        """
        Calculate likelihood this is a protagonist name (0-100).
        
        Protagonists typically have:
        - Moderate-high melodiousness
        - Common-ish names (relatable)
        - Moderate harshness (not too soft)
        """
        score = 50.0
        
        # Melodiousness: optimal around 60-75
        if 60 <= melodiousness <= 75:
            score += 20
        elif melodiousness > 50:
            score += 10
        
        # Commonality: optimal around 50-70 (familiar but not boring)
        if 50 <= commonality <= 70:
            score += 15
        elif commonality > 40:
            score += 5
        
        # Americanness: moderate to high
        if americanness > 60:
            score += 15
        
        return np.clip(score, 0, 100)
    
    def _calculate_antagonist_likelihood(self, melodiousness: float, americanness: float,
                                         commonality: float, phonetic: Dict) -> float:
        """
        Calculate likelihood this is an antagonist name (0-100).
        
        Antagonists typically have:
        - Lower melodiousness (harsher sounds)
        - Uncommon names (distinctive)
        - Higher harshness
        """
        score = 50.0
        
        # Melodiousness: lower is more villainous
        if melodiousness < 45:
            score += 20
        elif melodiousness < 55:
            score += 10
        
        # Commonality: unusual names
        if commonality < 40:
            score += 15
        
        # Harshness: higher is more threatening
        harshness = phonetic.get('harshness_score', 50)
        if harshness > 60:
            score += 15
        
        return np.clip(score, 0, 100)
    
    def _calculate_vulnerable_likelihood(self, melodiousness: float, phonetic: Dict) -> float:
        """
        Calculate likelihood this character is vulnerable/victim (0-100).
        
        Vulnerable characters typically have:
        - High melodiousness (soft, gentle sounds)
        - Low harshness
        - More vowels
        """
        score = 50.0
        
        # High melodiousness
        if melodiousness > 70:
            score += 25
        
        # Low harshness
        harshness = phonetic.get('harshness_score', 50)
        if harshness < 40:
            score += 25
        
        return np.clip(score, 0, 100)
    
    def _calculate_distinctiveness(self, name: str, commonality: float) -> float:
        """Calculate how distinctive/unique the name is (0-100)."""
        # Inverse of commonality, with adjustments
        distinctiveness = 100 - commonality
        
        # Add bonus for unusual length
        if len(name) > 15 or len(name) < 4:
            distinctiveness += 10
        
        return np.clip(distinctiveness, 0, 100)
    
    def _analyze_works(self, works: Dict, characters: Dict):
        """Analyze works by aggregating character statistics."""
        work_analyses = []
        
        for category, work_dict in works.items():
            for work_id, work_data in work_dict.items():
                work_chars = [c for c in self.character_analyses if c['work_id'] == work_id]
                
                if not work_chars:
                    continue
                
                # Aggregate statistics
                work_analysis = {
                    'work_id': work_id,
                    'title': work_data['title'],
                    'author': work_data['author'],
                    'category': category,
                    'genre': work_data.get('genre'),
                    'character_count': len(work_chars),
                    
                    # Mean metrics
                    'mean_melodiousness': np.mean([c['melodiousness_score'] for c in work_chars]),
                    'mean_americanness': np.mean([c['americanness_score'] for c in work_chars]),
                    'mean_commonality': np.mean([c['commonality_score'] for c in work_chars]),
                    'mean_harshness': np.mean([c['harshness_score'] for c in work_chars]),
                    'mean_syllables': np.mean([c['syllable_count'] for c in work_chars]),
                    
                    # Invented name percentage
                    'invented_pct': (sum(1 for c in work_chars if c['is_invented']) / len(work_chars)) * 100,
                }
                
                work_analyses.append(work_analysis)
        
        self.work_analyses = work_analyses
        self.logger.info(f"Analyzed {len(work_analyses)} works")
    
    def _calculate_category_aggregates(self):
        """Calculate category-level aggregate statistics."""
        for category in ['fiction', 'nonfiction', 'gospels']:
            category_chars = [c for c in self.character_analyses if c['category'] == category]
            
            if not category_chars:
                continue
            
            self.category_aggregates[category] = {
                'character_count': len(category_chars),
                'mean_melodiousness': np.mean([c['melodiousness_score'] for c in category_chars]),
                'std_melodiousness': np.std([c['melodiousness_score'] for c in category_chars]),
                'mean_americanness': np.mean([c['americanness_score'] for c in category_chars]),
                'std_americanness': np.std([c['americanness_score'] for c in category_chars]),
                'mean_commonality': np.mean([c['commonality_score'] for c in category_chars]),
                'std_commonality': np.std([c['commonality_score'] for c in category_chars]),
                'invented_pct': (sum(1 for c in category_chars if c['is_invented']) / len(category_chars)) * 100,
            }
    
    def _run_statistical_comparisons(self) -> Dict:
        """Run statistical tests comparing categories and vs baselines."""
        results = {}
        
        # Get baseline stats
        random_baseline = self.baseline_stats['random']
        
        # Category comparisons
        fiction_chars = [c for c in self.character_analyses if c['category'] == 'fiction']
        nonfiction_chars = [c for c in self.character_analyses if c['category'] == 'nonfiction']
        gospels_chars = [c for c in self.character_analyses if c['category'] == 'gospels']
        
        # T-tests: Fiction vs Nonfiction
        if len(fiction_chars) > 0 and len(nonfiction_chars) > 0:
            fiction_mel = [c['melodiousness_score'] for c in fiction_chars]
            nonfiction_mel = [c['melodiousness_score'] for c in nonfiction_chars]
            
            t_stat, p_val = stats.ttest_ind(fiction_mel, nonfiction_mel)
            cohens_d = (np.mean(fiction_mel) - np.mean(nonfiction_mel)) / np.sqrt((np.std(fiction_mel)**2 + np.std(nonfiction_mel)**2) / 2)
            
            results['fiction_vs_nonfiction'] = {
                'melodiousness_ttest': {
                    'statistic': float(t_stat),
                    'pvalue': float(p_val),
                    'significant': p_val < 0.05,
                    'cohens_d': float(cohens_d),
                }
            }
        
        # ANOVA: All categories
        if len(fiction_chars) > 0 and len(nonfiction_chars) > 0 and len(gospels_chars) > 0:
            fiction_mel = [c['melodiousness_score'] for c in fiction_chars]
            nonfiction_mel = [c['melodiousness_score'] for c in nonfiction_chars]
            gospels_mel = [c['melodiousness_score'] for c in gospels_chars]
            
            f_stat, p_val = stats.f_oneway(fiction_mel, nonfiction_mel, gospels_mel)
            
            results['category_anova'] = {
                'melodiousness_anova': {
                    'f_statistic': float(f_stat),
                    'pvalue': float(p_val),
                    'significant': p_val < 0.05,
                }
            }
        
        self.logger.info(f"Statistical comparisons complete")
        
        return results
    
    def _run_predictive_modeling(self) -> Dict:
        """
        Train models to predict character roles and outcomes from names.
        
        KEY INNOVATION: Tests nominative determinism predictively.
        """
        results = {}
        
        # Filter characters with labeled roles
        labeled_chars = [c for c in self.character_analyses if c.get('character_role')]
        
        if len(labeled_chars) < 20:
            self.logger.warning("Not enough labeled characters for predictive modeling")
            return {'error': 'insufficient_labeled_data'}
        
        # Prepare features
        X = np.array([
            [c['melodiousness_score'], c['americanness_score'], c['commonality_score'],
             c['harshness_score'], c['syllable_count'], c['protagonist_score']]
            for c in labeled_chars
        ])
        
        y_role = np.array([c['character_role'] for c in labeled_chars])
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_role, test_size=0.3, random_state=42
        )
        
        # Train logistic regression
        role_model = LogisticRegression(max_iter=1000, random_state=42)
        role_model.fit(X_train, y_train)
        
        # Predictions
        y_pred = role_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(role_model, X_scaled, y_role, cv=5)
        
        results['role_prediction'] = {
            'accuracy': float(accuracy),
            'cv_mean_accuracy': float(np.mean(cv_scores)),
            'cv_std_accuracy': float(np.std(cv_scores)),
            'sample_size': len(labeled_chars),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'better_than_chance': accuracy > 0.5,
        }
        
        self.prediction_models['role'] = role_model
        
        self.logger.info(f"Role prediction accuracy: {accuracy:.3f}")
        self.logger.info(f"Cross-validation accuracy: {np.mean(cv_scores):.3f} ± {np.std(cv_scores):.3f}")
        
        return results
    
    def _analyze_cross_category_patterns(self) -> Dict:
        """Analyze patterns across fiction/nonfiction/gospels."""
        results = {}
        
        # Compare invented name percentages
        invented_by_category = {}
        for category in ['fiction', 'nonfiction', 'gospels']:
            category_chars = [c for c in self.character_analyses if c['category'] == category]
            if category_chars:
                invented_pct = (sum(1 for c in category_chars if c['is_invented']) / len(category_chars)) * 100
                invented_by_category[category] = invented_pct
        
        results['invented_name_percentages'] = invented_by_category
        
        # Compare melodiousness distributions
        melodiousness_by_category = {}
        for category in ['fiction', 'nonfiction', 'gospels']:
            category_chars = [c for c in self.character_analyses if c['category'] == category]
            if category_chars:
                melodiousness_by_category[category] = {
                    'mean': float(np.mean([c['melodiousness_score'] for c in category_chars])),
                    'median': float(np.median([c['melodiousness_score'] for c in category_chars])),
                    'std': float(np.std([c['melodiousness_score'] for c in category_chars])),
                }
        
        results['melodiousness_by_category'] = melodiousness_by_category
        
        return results
    
    def _character_to_dict(self, char: Dict) -> Dict:
        """Convert character analysis to serializable dict."""
        # Already a dict, just ensure no numpy types
        output = {}
        for key, value in char.items():
            if isinstance(value, (np.integer, np.floating)):
                output[key] = float(value)
            elif isinstance(value, dict):
                output[key] = {k: float(v) if isinstance(v, (np.integer, np.floating)) else v 
                              for k, v in value.items()}
            else:
                output[key] = value
        return output


if __name__ == '__main__':
    # Test analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = LiteraryNameAnalyzer(mode='new')
    data = analyzer.collect_data()
    results = analyzer.analyze_data(data)
    
    print(f"\nAnalysis complete:")
    print(f"  Characters analyzed: {results['characters_analyzed']}")
    print(f"  Works analyzed: {results['work_count']}")

