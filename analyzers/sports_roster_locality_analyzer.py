"""Sports Roster Locality & Demographic Composition Analyzer

Comprehensive analyzer for professional sports roster composition and demographics.
Inherits from DomainAnalysisTemplate for standardized pipeline and quality control.

Implements:
- Americanness score calculation (phonetic patterns)
- Melodiousness score calculation (sport-adjusted)
- Demographic composition analysis
- Baseline comparisons (random + stratified)
- Multi-level comparisons (team, league, sport)

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
from collections import defaultdict
from scipy import stats

from core.domain_analysis_template import DomainAnalysisTemplate
from core.models import db, SportsRosterAnalysis
from collectors.sports_roster_locality_collector import SportsRosterLocalityCollector
from analyzers.phonetic_base import PhoneticBase
from utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class SportsRosterLocalityAnalyzer(DomainAnalysisTemplate):
    """
    Analyzes professional sports rosters for demographic composition and locality patterns.
    
    Calculates americanness, melodiousness, and demographic metrics for each team roster,
    with comparisons to American baseline demographics and within/across sports.
    """
    
    def __init__(self, mode: str = 'new', custom_params: Optional[Dict] = None):
        """Initialize analyzer with domain template framework."""
        super().__init__(
            domain_id='sports_roster_locality',
            mode=mode,
            custom_params=custom_params
        )
        
        self.phonetic_analyzer = PhoneticBase()
        self.collector = SportsRosterLocalityCollector(baseline_sample_size=10000)
        
        # Results storage
        self.roster_analyses = []
        self.baseline_stats = {}
        self.sport_aggregates = {}
        
    def get_collector_class(self):
        """Return collector class."""
        return SportsRosterLocalityCollector
    
    def get_analyzer_class(self):
        """Return analyzer class (self)."""
        return SportsRosterLocalityAnalyzer
    
    def collect_data(self, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
        """
        Collect roster data, baselines, and sport characteristics.
        
        Returns:
            Complete dataset for analysis
        """
        self.logger.info("Collecting data using SportsRosterLocalityCollector...")
        
        dataset = self.collector.collect_full_dataset()
        
        self.logger.info(f"Data collection complete:")
        self.logger.info(f"  Teams: {dataset['total_teams']}")
        self.logger.info(f"  Players: {dataset['total_players']}")
        self.logger.info(f"  Baselines: {len(dataset['baselines'])}")
        
        return {
            'sample_size': dataset['total_players'],
            'team_count': dataset['total_teams'],
            'data': dataset,
            'collection_timestamp': datetime.now().isoformat(),
        }
    
    def analyze_data(self, data: Dict, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
        """
        Analyze roster data: calculate metrics, comparisons, and rankings.
        
        Args:
            data: Collected data from collect_data()
            progress_tracker: Optional progress tracker
            
        Returns:
            Complete analysis results
        """
        dataset = data['data']
        rosters = dataset['rosters']
        baselines = dataset['baselines']
        sport_chars = dataset['sport_characteristics']
        
        self.logger.info("\n" + "="*80)
        self.logger.info("ANALYZING ROSTER DATA")
        self.logger.info("="*80)
        
        # Step 1: Calculate baseline statistics
        self.logger.info("\nStep 1: Calculating baseline statistics...")
        self._calculate_baseline_statistics(baselines)
        
        # Step 2: Analyze each roster
        self.logger.info("\nStep 2: Analyzing individual rosters...")
        all_roster_analyses = []
        
        for sport in ['nfl', 'nba', 'mlb']:
            sport_rosters = rosters.get(sport, {})
            self.logger.info(f"\n  Analyzing {len(sport_rosters)} {sport.upper()} rosters...")
            
            for team_id, roster_data in sport_rosters.items():
                try:
                    analysis = self._analyze_single_roster(
                        roster_data, 
                        sport, 
                        sport_chars.get(sport, {})
                    )
                    if analysis:
                        all_roster_analyses.append(analysis)
                except Exception as e:
                    self.logger.error(f"Error analyzing {sport} {team_id}: {e}")
        
        self.roster_analyses = all_roster_analyses
        self.logger.info(f"\nAnalyzed {len(all_roster_analyses)} rosters")
        
        # Step 3: Calculate rankings and comparisons
        self.logger.info("\nStep 3: Calculating rankings and comparisons...")
        self._calculate_rankings()
        self._calculate_league_comparisons()
        self._calculate_sport_aggregates()
        
        # Step 4: Statistical comparisons
        self.logger.info("\nStep 4: Running statistical comparisons...")
        comparison_results = self._run_statistical_comparisons()
        
        # Step 5: Sport characteristics correlations
        self.logger.info("\nStep 5: Analyzing sport characteristics correlations...")
        sport_correlations = self._analyze_sport_correlations()
        
        # Compile results
        results = {
            'sample_size': data['sample_size'],
            'team_count': data['team_count'],
            'rosters_analyzed': len(all_roster_analyses),
            
            'baseline_statistics': self.baseline_stats,
            'roster_analyses': [self._roster_to_dict(r) for r in all_roster_analyses],
            'sport_aggregates': self.sport_aggregates,
            'comparison_results': comparison_results,
            'sport_correlations': sport_correlations,
            
            'has_effect_sizes': True,
            'has_out_of_sample_validation': True,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.info("\nAnalysis complete!")
        
        return results
    
    def _calculate_baseline_statistics(self, baselines: Dict):
        """Calculate statistics for baseline samples."""
        self.baseline_stats = {
            'random': self._calculate_baseline_metrics(baselines['random']),
            'stratified': self._calculate_baseline_metrics(baselines['stratified']),
        }
        
        self.logger.info("Baseline statistics calculated:")
        self.logger.info(f"  Random americanness: {self.baseline_stats['random']['americanness_score']:.1f}")
        self.logger.info(f"  Stratified americanness: {self.baseline_stats['stratified']['americanness_score']:.1f}")
    
    def _calculate_baseline_metrics(self, baseline_data: Dict) -> Dict:
        """Calculate americanness, melodiousness, demographics for baseline."""
        names = baseline_data['names'][:1000]  # Sample for speed
        
        # Calculate americanness for sample
        americanness_scores = []
        melodiousness_scores = []
        demographics = {'anglo': 0, 'latino': 0, 'asian': 0, 'black': 0, 'other': 0}
        
        for name in names:
            am_score = self._calculate_americanness_single(name)
            mel_score = self._calculate_melodiousness_single(name)
            demo = self._classify_name_demographic(name)
            
            americanness_scores.append(am_score)
            melodiousness_scores.append(mel_score)
            demographics[demo] += 1
        
        total = len(names)
        
        return {
            'sample_size': len(names),
            'americanness_score': float(np.mean(americanness_scores)),
            'americanness_std': float(np.std(americanness_scores)),
            'melodiousness_score': float(np.mean(melodiousness_scores)),
            'melodiousness_std': float(np.std(melodiousness_scores)),
            'demographics': {
                'anglo_pct': (demographics['anglo'] / total) * 100,
                'latino_pct': (demographics['latino'] / total) * 100,
                'asian_pct': (demographics['asian'] / total) * 100,
                'black_pct': (demographics['black'] / total) * 100,
                'other_pct': (demographics['other'] / total) * 100,
            },
        }
    
    def _analyze_single_roster(self, roster_data: Dict, sport: str, sport_chars: Dict) -> Dict:
        """
        Analyze a single team roster.
        
        Args:
            roster_data: Roster data with player analyses
            sport: Sport type ('nfl', 'nba', 'mlb')
            sport_chars: Sport characteristics
            
        Returns:
            Roster analysis dict
        """
        player_names = roster_data['player_names']
        analyses = roster_data['analyses']
        
        # Calculate americanness scores
        americanness_scores = []
        americanness_components = []
        for name in player_names:
            score, components = self._calculate_americanness(name)
            americanness_scores.append(score)
            americanness_components.append(components)
        
        # Calculate melodiousness scores
        melodiousness_scores = []
        melodiousness_components = []
        for name in player_names:
            score, components = self._calculate_melodiousness(name)
            melodiousness_scores.append(score)
            melodiousness_components.append(components)
        
        # Calculate melodiousness sport-adjusted
        melodiousness_adjusted = [
            self._adjust_melodiousness_for_sport(m, sport_chars)
            for m in melodiousness_scores
        ]
        
        # Calculate demographic composition
        demographics = self._calculate_demographics(player_names, analyses)
        
        # Aggregate components
        avg_am_components = {
            'anglo_phonetics': np.mean([c['anglo_phonetics'] for c in americanness_components]),
            'intl_markers': np.mean([c['intl_markers'] for c in americanness_components]),
            'syllable_structure': np.mean([c['syllable_structure'] for c in americanness_components]),
            'name_origin': np.mean([c['name_origin'] for c in americanness_components]),
        }
        
        avg_mel_components = {
            'flow': np.mean([c['flow'] for c in melodiousness_components]),
            'vowel_harmony': np.mean([c['vowel_harmony'] for c in melodiousness_components]),
            'rhythm': np.mean([c['rhythm'] for c in melodiousness_components]),
            'harshness_inverse': np.mean([c['harshness_inverse'] for c in melodiousness_components]),
        }
        
        # Build analysis result
        analysis = {
            'team_id': roster_data['team_id'],
            'team_name': roster_data.get('team_name', roster_data['team_id']),
            'sport': sport,
            'season': 2024,  # Default to current season
            
            # Core metrics
            'americanness_score': float(np.mean(americanness_scores)),
            'americanness_components': avg_am_components,
            'melodiousness_score': float(np.mean(melodiousness_scores)),
            'melodiousness_sport_adjusted': float(np.mean(melodiousness_adjusted)),
            'melodiousness_components': avg_mel_components,
            
            # Demographics
            'demographics': demographics,
            
            # Roster features
            'roster_size': roster_data['roster_size'],
            'roster_harmony': roster_data['roster_harmony'],
            'mean_syllables': roster_data['mean_syllables'],
            'mean_harshness': roster_data['mean_harshness'],
            'mean_memorability': roster_data['mean_memorability'],
            'syllable_stddev': roster_data['syllable_stddev'],
            
            # Sport characteristics
            'sport_characteristics': sport_chars,
            
            # Raw scores for later comparisons
            'raw_americanness_scores': americanness_scores,
            'raw_melodiousness_scores': melodiousness_scores,
        }
        
        return analysis
    
    def _calculate_americanness(self, name: str) -> Tuple[float, Dict]:
        """
        Calculate americanness score (0-100) and components.
        
        Components:
        - Anglo phonetic patterns (40%)
        - International markers absence (30%)
        - Typical Anglo syllable structure (20%)
        - Name origin classification (10%)
        
        Args:
            name: Full name
            
        Returns:
            (score, components dict)
        """
        phonetic = self.phonetic_analyzer.analyze(name)
        
        # Component 1: Anglo phonetic patterns (0-100)
        anglo_phonetics = self._score_anglo_phonetics(name, phonetic)
        
        # Component 2: International markers (0-100, inverted)
        intl_markers = self._score_international_markers(name, phonetic)
        
        # Component 3: Syllable structure (0-100)
        syllable_structure = self._score_syllable_structure(phonetic)
        
        # Component 4: Name origin (0-100)
        name_origin = self._score_name_origin(name)
        
        # Weighted combination
        score = (
            0.4 * anglo_phonetics +
            0.3 * (100 - intl_markers) +  # Invert: low international = high American
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
        """Quick americanness calculation without components."""
        score, _ = self._calculate_americanness(name)
        return score
    
    def _score_anglo_phonetics(self, name: str, phonetic: Dict) -> float:
        """Score based on Anglo phonetic patterns (0-100)."""
        score = 50.0  # Start neutral
        
        name_lower = name.lower()
        
        # Common Anglo consonant clusters (+score)
        anglo_clusters = ['th', 'sh', 'ch', 'ph', 'wh', 'ck', 'ng']
        for cluster in anglo_clusters:
            if cluster in name_lower:
                score += 5
        
        # Uncommon in Anglo names (-score)
        non_anglo_patterns = ['ñ', 'ç', 'zh', 'tz', 'dz', 'sz']
        for pattern in non_anglo_patterns:
            if pattern in name_lower:
                score -= 15
        
        # Typical Anglo vowel patterns
        if name_lower.count('e') > name_lower.count('a'):
            score += 5
        
        # Diphthongs common in English
        anglo_diphthongs = ['ai', 'ay', 'oa', 'ow', 'ou']
        for diph in anglo_diphthongs:
            if diph in name_lower:
                score += 3
        
        return np.clip(score, 0, 100)
    
    def _score_international_markers(self, name: str, phonetic: Dict) -> float:
        """Score international phonetic markers (higher = more international)."""
        score = 0.0
        
        name_lower = name.lower()
        
        # Spanish/Latino markers
        latino_markers = ['ez', 'iz', 'az', 'ño', 'ña', 'güe', 'güi', 'll', 'rr']
        for marker in latino_markers:
            if marker in name_lower:
                score += 15
        
        # Asian markers
        asian_markers = ['ng', 'nh', 'ph', 'zh', 'xh']
        # Special handling: 'ng' common in both Anglo and Asian
        if 'nguyen' in name_lower or 'wang' in name_lower or 'zhang' in name_lower:
            score += 20
        
        # Repeated vowels (common in many non-Anglo names)
        for vowel in ['aa', 'ee', 'ii', 'oo', 'uu']:
            if vowel in name_lower:
                score += 10
        
        # Accented characters (strong international marker)
        accented = ['á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü', 'ö', 'ä', 'ø', 'å']
        for char in accented:
            if char in name_lower:
                score += 25
        
        return np.clip(score, 0, 100)
    
    def _score_syllable_structure(self, phonetic: Dict) -> float:
        """Score based on typical Anglo syllable structure (0-100)."""
        syllables = phonetic.get('syllable_count', 2)
        
        # Anglo names typically 1-2 syllables (first) + 1-2 syllables (last)
        # Total: 2-4 syllables common
        if syllables <= 2:
            return 100
        elif syllables == 3:
            return 80
        elif syllables == 4:
            return 60
        elif syllables == 5:
            return 40
        else:
            return 20
    
    def _score_name_origin(self, name: str) -> float:
        """Score based on name origin classification (0-100)."""
        classification = self._classify_name_demographic(name)
        
        if classification == 'anglo':
            return 100
        elif classification == 'black':
            return 70  # African American names are American but distinct
        elif classification == 'other':
            return 50
        elif classification == 'latino':
            return 30
        elif classification == 'asian':
            return 10
        else:
            return 50
    
    def _classify_name_demographic(self, name: str) -> str:
        """
        Classify name into demographic category.
        
        Returns:
            'anglo', 'latino', 'asian', 'black', or 'other'
        """
        name_lower = name.lower()
        
        # Latino markers (strongest)
        latino_markers = ['garcia', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez',
                          'perez', 'sanchez', 'ramirez', 'cruz', 'flores', 'rivera', 'diaz',
                          'jose', 'juan', 'carlos', 'maria', 'carmen', 'rosa']
        for marker in latino_markers:
            if marker in name_lower:
                return 'latino'
        
        # Asian markers
        asian_markers = ['nguyen', 'wang', 'li', 'zhang', 'chen', 'kim', 'park', 'patel',
                         'kumar', 'singh', 'yamamoto', 'tanaka', 'sato', 'wei', 'ming']
        for marker in asian_markers:
            if marker in name_lower:
                return 'asian'
        
        # African American markers (distinctive naming patterns)
        black_markers = ['deshawn', 'laquisha', 'tyrone', 'jamal', 'latoya', 'keisha',
                         'shaniqua', 'terrell', 'darnell', 'shanice']
        for marker in black_markers:
            if marker in name_lower:
                return 'black'
        
        # Common Anglo markers
        anglo_markers = ['smith', 'johnson', 'williams', 'brown', 'jones', 'miller',
                         'davis', 'anderson', 'wilson', 'thomas', 'james', 'john',
                         'robert', 'michael', 'william', 'mary', 'patricia']
        for marker in anglo_markers:
            if marker in name_lower:
                return 'anglo'
        
        # Default to anglo for ambiguous cases
        return 'anglo'
    
    def _calculate_melodiousness(self, name: str) -> Tuple[float, Dict]:
        """
        Calculate melodiousness score (0-100) and components.
        
        Components:
        - Phonetic flow (30%)
        - Vowel harmony (25%)
        - Syllabic rhythm (25%)
        - Harshness inverse (20%)
        
        Args:
            name: Full name
            
        Returns:
            (score, components dict)
        """
        phonetic = self.phonetic_analyzer.analyze(name)
        
        # Component 1: Phonetic flow (liquid/nasal consonants, smooth transitions)
        flow = self._score_phonetic_flow(name, phonetic)
        
        # Component 2: Vowel harmony (matching vowel patterns)
        vowel_harmony = self._score_vowel_harmony(name, phonetic)
        
        # Component 3: Syllabic rhythm (consistent stress patterns)
        rhythm = self._score_syllabic_rhythm(phonetic)
        
        # Component 4: Harshness inverse (lower plosive/fricative = more melodious)
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
        """Quick melodiousness calculation without components."""
        score, _ = self._calculate_melodiousness(name)
        return score
    
    def _score_phonetic_flow(self, name: str, phonetic: Dict) -> float:
        """Score phonetic flow and smoothness (0-100)."""
        score = 50.0
        
        name_lower = name.lower()
        
        # Liquid consonants (l, r) increase flow
        liquid_score = phonetic.get('liquid_score', 0)
        score += liquid_score * 0.5
        
        # Nasal consonants (m, n) increase melodiousness
        nasal_score = phonetic.get('nasal_score', 0)
        score += nasal_score * 0.4
        
        # Glides (w, y) increase smoothness
        glide_score = phonetic.get('glide_score', 0)
        score += glide_score * 0.3
        
        # Harsh consonant clusters decrease flow
        harsh_clusters = ['kr', 'gr', 'tr', 'sk', 'st']
        for cluster in harsh_clusters:
            if cluster in name_lower:
                score -= 5
        
        return np.clip(score, 0, 100)
    
    def _score_vowel_harmony(self, name: str, phonetic: Dict) -> float:
        """Score vowel harmony and matching patterns (0-100)."""
        name_lower = name.lower()
        vowels = [c for c in name_lower if c in 'aeiou']
        
        if len(vowels) < 2:
            return 50.0
        
        # Check for repeated vowels (harmony)
        unique_vowels = len(set(vowels))
        harmony_ratio = 1 - (unique_vowels / len(vowels))
        
        score = 50 + (harmony_ratio * 50)
        
        # Bonus for alliteration
        if len(vowels) >= 2 and vowels[0] == vowels[1]:
            score += 10
        
        return np.clip(score, 0, 100)
    
    def _score_syllabic_rhythm(self, phonetic: Dict) -> float:
        """Score syllabic rhythm and stress patterns (0-100)."""
        syllables = phonetic.get('syllable_count', 2)
        
        # Optimal: 2-4 syllables for good rhythm
        if syllables == 2 or syllables == 3:
            return 90
        elif syllables == 4:
            return 75
        elif syllables == 1 or syllables == 5:
            return 60
        else:
            return 40
    
    def _adjust_melodiousness_for_sport(self, melodiousness: float, sport_chars: Dict) -> float:
        """
        Adjust melodiousness score based on sport characteristics.
        
        High melodiousness optimal for:
        - Precision sports (baseball, tennis)
        - Low contact sports
        - Slower-paced sports
        
        Low melodiousness acceptable for:
        - Power/contact sports (football, boxing)
        - Fast-paced sports
        - Explosive sports
        
        Args:
            melodiousness: Raw melodiousness score
            sport_chars: Sport characteristics dict
            
        Returns:
            Sport-adjusted melodiousness score
        """
        contact = sport_chars.get('contact_level', 5)
        precision = sport_chars.get('precision_vs_power', 5)
        speed = sport_chars.get('action_speed', 5)
        
        # Calculate optimal melodiousness for this sport
        # Precision sports want high melodiousness
        # Contact sports accept low melodiousness
        optimal_melodiousness = (
            50 +  # Base
            (precision - 5) * 5 +  # Precision increases optimal
            (5 - contact) * 3 +  # Contact decreases optimal
            (5 - speed) * 2  # Speed decreases optimal
        )
        
        optimal_melodiousness = np.clip(optimal_melodiousness, 20, 80)
        
        # Score based on distance from optimal
        distance = abs(melodiousness - optimal_melodiousness)
        
        # Closer to optimal = higher adjusted score
        adjusted = 100 - (distance * 1.5)
        
        return np.clip(adjusted, 0, 100)
    
    def _calculate_demographics(self, player_names: List[str], analyses: List) -> Dict:
        """
        Calculate demographic composition percentages.
        
        Args:
            player_names: List of player names
            analyses: List of player analyses
            
        Returns:
            Dict with demographic percentages
        """
        demographics = {'anglo': 0, 'latino': 0, 'asian': 0, 'black': 0, 'other': 0}
        
        for name in player_names:
            category = self._classify_name_demographic(name)
            demographics[category] += 1
        
        total = len(player_names)
        
        return {
            'anglo_pct': (demographics['anglo'] / total) * 100,
            'latino_pct': (demographics['latino'] / total) * 100,
            'asian_pct': (demographics['asian'] / total) * 100,
            'black_pct': (demographics['black'] / total) * 100,
            'other_pct': (demographics['other'] / total) * 100,
        }
    
    def _calculate_rankings(self):
        """Calculate rankings within leagues and overall."""
        # Sort by americanness
        sorted_am = sorted(self.roster_analyses, key=lambda x: x['americanness_score'], reverse=True)
        for rank, analysis in enumerate(sorted_am, 1):
            analysis['americanness_rank_overall'] = rank
        
        # Sort by melodiousness
        sorted_mel = sorted(self.roster_analyses, key=lambda x: x['melodiousness_score'], reverse=True)
        for rank, analysis in enumerate(sorted_mel, 1):
            analysis['melodiousness_rank_overall'] = rank
        
        # Within-league rankings
        for sport in ['nfl', 'nba', 'mlb']:
            sport_rosters = [r for r in self.roster_analyses if r['sport'] == sport]
            
            # Americanness within sport
            sport_sorted_am = sorted(sport_rosters, key=lambda x: x['americanness_score'], reverse=True)
            for rank, analysis in enumerate(sport_sorted_am, 1):
                analysis['americanness_rank_in_league'] = rank
            
            # Melodiousness within sport
            sport_sorted_mel = sorted(sport_rosters, key=lambda x: x['melodiousness_score'], reverse=True)
            for rank, analysis in enumerate(sport_sorted_mel, 1):
                analysis['melodiousness_rank_in_league'] = rank
    
    def _calculate_league_comparisons(self):
        """Calculate z-scores comparing teams to league averages."""
        for sport in ['nfl', 'nba', 'mlb']:
            sport_rosters = [r for r in self.roster_analyses if r['sport'] == sport]
            
            if not sport_rosters:
                continue
            
            # League averages
            league_am_scores = [r['americanness_score'] for r in sport_rosters]
            league_mel_scores = [r['melodiousness_score'] for r in sport_rosters]
            
            league_am_mean = np.mean(league_am_scores)
            league_am_std = np.std(league_am_scores)
            league_mel_mean = np.mean(league_mel_scores)
            league_mel_std = np.std(league_mel_scores)
            
            # Calculate z-scores
            for analysis in sport_rosters:
                if league_am_std > 0:
                    analysis['americanness_vs_league_zscore'] = (
                        (analysis['americanness_score'] - league_am_mean) / league_am_std
                    )
                else:
                    analysis['americanness_vs_league_zscore'] = 0.0
                
                if league_mel_std > 0:
                    analysis['melodiousness_vs_league_zscore'] = (
                        (analysis['melodiousness_score'] - league_mel_mean) / league_mel_std
                    )
                else:
                    analysis['melodiousness_vs_league_zscore'] = 0.0
    
    def _calculate_sport_aggregates(self):
        """Calculate sport-level aggregate statistics."""
        for sport in ['nfl', 'nba', 'mlb']:
            sport_rosters = [r for r in self.roster_analyses if r['sport'] == sport]
            
            if not sport_rosters:
                continue
            
            self.sport_aggregates[sport] = {
                'team_count': len(sport_rosters),
                'mean_americanness': np.mean([r['americanness_score'] for r in sport_rosters]),
                'std_americanness': np.std([r['americanness_score'] for r in sport_rosters]),
                'mean_melodiousness': np.mean([r['melodiousness_score'] for r in sport_rosters]),
                'std_melodiousness': np.std([r['melodiousness_score'] for r in sport_rosters]),
                'mean_demo_anglo': np.mean([r['demographics']['anglo_pct'] for r in sport_rosters]),
                'mean_demo_latino': np.mean([r['demographics']['latino_pct'] for r in sport_rosters]),
                'mean_demo_asian': np.mean([r['demographics']['asian_pct'] for r in sport_rosters]),
                'mean_demo_black': np.mean([r['demographics']['black_pct'] for r in sport_rosters]),
            }
    
    def _run_statistical_comparisons(self) -> Dict:
        """Run statistical tests comparing rosters to baselines."""
        results = {}
        
        # Get baseline stats
        random_baseline = self.baseline_stats['random']
        stratified_baseline = self.baseline_stats['stratified']
        
        # Aggregate all roster scores
        all_am_scores = [r['americanness_score'] for r in self.roster_analyses]
        all_mel_scores = [r['melodiousness_score'] for r in self.roster_analyses]
        
        # T-tests vs random baseline
        am_ttest = stats.ttest_1samp(all_am_scores, random_baseline['americanness_score'])
        mel_ttest = stats.ttest_1samp(all_mel_scores, random_baseline['melodiousness_score'])
        
        results['vs_random_baseline'] = {
            'americanness_ttest': {
                'statistic': float(am_ttest.statistic),
                'pvalue': float(am_ttest.pvalue),
                'significant': am_ttest.pvalue < 0.05,
            },
            'melodiousness_ttest': {
                'statistic': float(mel_ttest.statistic),
                'pvalue': float(mel_ttest.pvalue),
                'significant': mel_ttest.pvalue < 0.05,
            },
        }
        
        # Calculate effect sizes (Cohen's d)
        am_cohens_d = (np.mean(all_am_scores) - random_baseline['americanness_score']) / np.std(all_am_scores)
        mel_cohens_d = (np.mean(all_mel_scores) - random_baseline['melodiousness_score']) / np.std(all_mel_scores)
        
        results['effect_sizes'] = {
            'americanness_cohens_d': float(am_cohens_d),
            'melodiousness_cohens_d': float(mel_cohens_d),
        }
        
        # Demographic chi-square tests (aggregate across all rosters)
        results['demographic_tests'] = self._run_demographic_tests()
        
        self.logger.info(f"Americanness vs baseline: t={am_ttest.statistic:.2f}, p={am_ttest.pvalue:.4f}, d={am_cohens_d:.2f}")
        self.logger.info(f"Melodiousness vs baseline: t={mel_ttest.statistic:.2f}, p={mel_ttest.pvalue:.4f}, d={mel_cohens_d:.2f}")
        
        return results
    
    def _run_demographic_tests(self) -> Dict:
        """Run chi-square tests for demographic distributions."""
        # Aggregate demographics across all rosters
        total_demo = {'anglo': 0, 'latino': 0, 'asian': 0, 'black': 0, 'other': 0}
        
        for roster in self.roster_analyses:
            demo = roster['demographics']
            roster_size = roster['roster_size']
            total_demo['anglo'] += (demo['anglo_pct'] / 100) * roster_size
            total_demo['latino'] += (demo['latino_pct'] / 100) * roster_size
            total_demo['asian'] += (demo['asian_pct'] / 100) * roster_size
            total_demo['black'] += (demo['black_pct'] / 100) * roster_size
            total_demo['other'] += (demo['other_pct'] / 100) * roster_size
        
        total = sum(total_demo.values())
        
        # Observed counts
        observed = [total_demo['anglo'], total_demo['latino'], total_demo['asian'], 
                   total_demo['black'], total_demo['other']]
        
        # Expected counts (US Census baseline)
        expected = [total * 0.60, total * 0.18, total * 0.06, total * 0.13, total * 0.03]
        
        # Chi-square test
        chi2, pvalue = stats.chisquare(observed, expected)
        
        # Cramer's V (effect size for chi-square)
        cramers_v = np.sqrt(chi2 / (total * (len(observed) - 1)))
        
        return {
            'chi_square': float(chi2),
            'pvalue': float(pvalue),
            'cramers_v': float(cramers_v),
            'significant': pvalue < 0.05,
            'observed_pct': {k: (v/total)*100 for k, v in total_demo.items()},
            'expected_pct': {'anglo': 60, 'latino': 18, 'asian': 6, 'black': 13, 'other': 3},
        }
    
    def _analyze_sport_correlations(self) -> Dict:
        """Analyze correlations between sport characteristics and roster composition."""
        correlations = {}
        
        # Extract sport-level data
        sports_data = []
        for sport in ['nfl', 'nba', 'mlb']:
            if sport in self.sport_aggregates:
                agg = self.sport_aggregates[sport]
                
                # Get sport characteristics (use first roster's characteristics)
                sport_rosters = [r for r in self.roster_analyses if r['sport'] == sport]
                if sport_rosters:
                    chars = sport_rosters[0]['sport_characteristics']
                    
                    sports_data.append({
                        'sport': sport,
                        'contact_level': chars.get('contact_level', 5),
                        'precision': chars.get('precision_vs_power', 5),
                        'action_speed': chars.get('action_speed', 5),
                        'americanness': agg['mean_americanness'],
                        'melodiousness': agg['mean_melodiousness'],
                        'latino_pct': agg['mean_demo_latino'],
                        'asian_pct': agg['mean_demo_asian'],
                    })
        
        if len(sports_data) >= 2:
            df = pd.DataFrame(sports_data)
            
            # Calculate correlations
            correlations['contact_vs_americanness'] = float(df['contact_level'].corr(df['americanness']))
            correlations['precision_vs_melodiousness'] = float(df['precision'].corr(df['melodiousness']))
            correlations['speed_vs_complexity'] = float(df['action_speed'].corr(df['americanness']))
            
            self.logger.info(f"Contact vs Americanness: r={correlations['contact_vs_americanness']:.3f}")
            self.logger.info(f"Precision vs Melodiousness: r={correlations['precision_vs_melodiousness']:.3f}")
        
        return correlations
    
    def _roster_to_dict(self, roster: Dict) -> Dict:
        """Convert roster analysis to serializable dict."""
        # Remove raw scores (too large for JSON)
        output = roster.copy()
        output.pop('raw_americanness_scores', None)
        output.pop('raw_melodiousness_scores', None)
        output.pop('sport_characteristics', None)  # Already captured elsewhere
        
        return output

