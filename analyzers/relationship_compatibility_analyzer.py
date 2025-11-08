"""
Relationship Compatibility Analyzer

Core analysis engine for marriage prediction study.
Calculates compatibility scores, relative success metrics, and tests theories.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, date
import logging

from utils.relationship_formulas import RelationshipFormulaEngine, RelationshipEncoding
from analyzers.name_analyzer import NameAnalyzer
from core.marriage_models import (
    MarriedCouple, MarriageAnalysis, ChildName, 
    DivorceBaseline, CelebrityMarriage, PredictionLock
)

logger = logging.getLogger(__name__)


@dataclass
class RelativeSuccessMetrics:
    """Relative success calculation results"""
    actual_duration: float
    expected_duration: float
    relative_success_score: float
    exceeds_expectations: bool
    percentile_rank: float  # 0-100 (relative to cohort)
    

@dataclass
class TheoryComparisonResult:
    """Results from testing multiple compatibility theories"""
    similarity_score: float
    complementarity_score: float
    golden_ratio_score: float
    resonance_score: float
    winning_theory: str
    confidence: float


class RelationshipCompatibilityAnalyzer:
    """
    Main analyzer for marriage prediction study
    
    Responsibilities:
    1. Calculate name interaction metrics
    2. Compute relative success scores
    3. Test compatibility theories
    4. Analyze children's names
    5. Generate predictions (for blind testing)
    """
    
    def __init__(self, db_session=None):
        """
        Initialize analyzer
        
        Args:
            db_session: SQLAlchemy database session (optional)
        """
        self.relationship_engine = RelationshipFormulaEngine()
        self.name_analyzer = NameAnalyzer()
        self.db = db_session
        
        # Baseline data (loaded from database or defaults)
        self.divorce_baselines = self._load_divorce_baselines()
        
        # Constants to test for
        self.decay_constant = 0.993
        self.growth_constant = 1.008
    
    def analyze_couple(self, couple: MarriedCouple, 
                      include_children: bool = True) -> MarriageAnalysis:
        """
        Complete analysis of a married couple
        
        Args:
            couple: MarriedCouple database object
            include_children: Whether to analyze children's names
            
        Returns:
            MarriageAnalysis with all metrics calculated
        """
        logger.info(f"Analyzing couple: {couple.partner1_full_name} & {couple.partner2_full_name}")
        
        # Step 1: Individual name analysis
        features1 = self.name_analyzer.analyze_name(couple.partner1_first)
        features2 = self.name_analyzer.analyze_name(couple.partner2_first)
        
        # Step 2: Relationship interaction analysis
        relationship = self.relationship_engine.analyze_relationship(
            couple.partner1_first,
            couple.partner2_first,
            include_phonetic=True
        )
        
        # Step 3: Test all compatibility theories
        theory_results = self._test_compatibility_theories(relationship)
        
        # Step 4: Calculate relative success (if outcome known)
        relative_success = None
        if couple.marriage_duration_years is not None:
            relative_success = self._calculate_relative_success(couple)
        
        # Step 5: Create analysis record
        analysis = MarriageAnalysis(
            couple_id=couple.id,
            
            # Partner 1 features
            p1_syllable_count=features1.get('syllable_count'),
            p1_character_length=features1.get('character_length'),
            p1_harshness_score=features1.get('harshness_score', 0),
            p1_smoothness_score=100 - features1.get('harshness_score', 50),
            p1_memorability_score=features1.get('memorability_score'),
            p1_pronounceability=features1.get('pronounceability_score'),
            p1_vowel_ratio=features1.get('vowel_ratio'),
            p1_name_type=features1.get('name_type'),
            p1_cultural_origin=features1.get('semantic_category'),
            p1_uniqueness_score=features1.get('uniqueness_score', 50),
            
            # Partner 2 features
            p2_syllable_count=features2.get('syllable_count'),
            p2_character_length=features2.get('character_length'),
            p2_harshness_score=features2.get('harshness_score', 0),
            p2_smoothness_score=100 - features2.get('harshness_score', 50),
            p2_memorability_score=features2.get('memorability_score'),
            p2_pronounceability=features2.get('pronounceability_score'),
            p2_vowel_ratio=features2.get('vowel_ratio'),
            p2_name_type=features2.get('name_type'),
            p2_cultural_origin=features2.get('semantic_category'),
            p2_uniqueness_score=features2.get('uniqueness_score', 50),
            
            # Pairwise interaction features
            compatibility_score=relationship.compatibility_score,
            distance_score=relationship.distance_score,
            resonance_score=relationship.resonance_score,
            balance_score=relationship.balance_score,
            golden_ratio_proximity=relationship.golden_ratio_proximity,
            syllable_ratio=relationship.syllable_ratio,
            syllable_ratio_to_phi=relationship.syllable_ratio_to_phi,
            color_harmony=relationship.color_harmony,
            complexity_balance=relationship.complexity_balance,
            symmetry_match=relationship.symmetry_match,
            
            # Phonetic interactions
            phonetic_distance=relationship.phonetic_distance,
            vowel_harmony=relationship.vowel_harmony,
            consonant_compatibility=relationship.consonant_compatibility,
            stress_alignment=relationship.stress_alignment,
            
            # Cultural/social
            cultural_origin_match=relationship.cultural_origin_match,
            social_class_alignment=relationship.social_class_alignment,
            
            # Relationship classification
            relationship_type=relationship.relationship_type,
            
            # Theory scores
            similarity_theory_score=theory_results.similarity_score,
            complementarity_theory_score=theory_results.complementarity_score,
            golden_ratio_theory_score=theory_results.golden_ratio_score,
            resonance_theory_score=theory_results.resonance_score,
            
            # Relative success (if calculable)
            relative_success_score=relative_success.relative_success_score if relative_success else None,
            exceeds_expectations=relative_success.exceeds_expectations if relative_success else None,
            expected_divorce_rate=relative_success.expected_duration if relative_success else None,
            
            # Metadata
            analyzed_date=datetime.utcnow(),
            analyzer_version="1.0.0",
            formula_id="hybrid"
        )
        
        # Step 6: Analyze children's names (if requested and available)
        if include_children and couple.has_children:
            self._analyze_children_names(couple, analysis)
        
        return analysis
    
    def _test_compatibility_theories(self, relationship: RelationshipEncoding) -> TheoryComparisonResult:
        """
        Test all four compatibility theories
        
        Theories:
        1. Similarity: Similar names → compatible (low distance)
        2. Complementarity: Opposite names → balance (high color harmony)
        3. Golden Ratio: φ relationship → harmony (low syllable_ratio_to_phi)
        4. Resonance: Harmonic ratios → success (high resonance_score)
        
        Returns:
            TheoryComparisonResult with all scores
        """
        # Theory 1: Similarity (inverse of distance)
        similarity_score = 1.0 - relationship.distance_score
        
        # Theory 2: Complementarity (color harmony + balance)
        complementarity_score = (relationship.color_harmony + relationship.balance_score) / 2.0
        
        # Theory 3: Golden Ratio (proximity to φ)
        # Convert distance from φ to proximity score
        golden_ratio_score = 1.0 - min(relationship.syllable_ratio_to_phi, 1.0)
        
        # Theory 4: Resonance (harmonic frequency ratios)
        resonance_score = relationship.resonance_score
        
        # Determine winning theory (highest score)
        scores = {
            'similarity': similarity_score,
            'complementarity': complementarity_score,
            'golden_ratio': golden_ratio_score,
            'resonance': resonance_score
        }
        
        winning_theory = max(scores, key=scores.get)
        confidence = scores[winning_theory]
        
        return TheoryComparisonResult(
            similarity_score=similarity_score,
            complementarity_score=complementarity_score,
            golden_ratio_score=golden_ratio_score,
            resonance_score=resonance_score,
            winning_theory=winning_theory,
            confidence=confidence
        )
    
    def _calculate_relative_success(self, couple: MarriedCouple) -> RelativeSuccessMetrics:
        """
        Calculate relative success score
        
        Formula:
            Relative_Success = Actual_Duration / Expected_Duration
        
        Where Expected_Duration is based on:
        - Age at marriage
        - Marriage year (cohort effects)
        - Geographic region
        - Urban/rural
        
        Args:
            couple: MarriedCouple with outcome data
            
        Returns:
            RelativeSuccessMetrics
        """
        actual_duration = couple.marriage_duration_years
        
        # Get expected duration from baseline
        baseline = self._get_baseline_for_couple(couple)
        expected_duration = baseline['expected_duration']
        
        # Calculate relative success
        if expected_duration > 0:
            relative_success = actual_duration / expected_duration
        else:
            relative_success = 1.0  # Neutral if no baseline
        
        # Exceeds expectations if relative > 1.0
        exceeds = relative_success > 1.0
        
        # Percentile rank (compared to cohort)
        percentile = self._calculate_percentile(couple, actual_duration)
        
        return RelativeSuccessMetrics(
            actual_duration=actual_duration,
            expected_duration=expected_duration,
            relative_success_score=relative_success,
            exceeds_expectations=exceeds,
            percentile_rank=percentile
        )
    
    def _get_baseline_for_couple(self, couple: MarriedCouple) -> Dict:
        """
        Get baseline expectations for a specific couple
        
        Args:
            couple: MarriedCouple
            
        Returns:
            Dict with expected_duration, expected_divorce_rate, etc.
        """
        # Age bracket
        avg_age = (couple.partner1_age_at_marriage + couple.partner2_age_at_marriage) / 2.0
        if avg_age < 25:
            age_bracket = '18-24'
        elif avg_age < 30:
            age_bracket = '25-29'
        elif avg_age < 35:
            age_bracket = '30-34'
        elif avg_age < 40:
            age_bracket = '35-39'
        else:
            age_bracket = '40+'
        
        # Era
        era = couple.cohort_era or '2000s'
        
        # Region
        region = couple.geographic_region or 'USA'
        
        # Lookup baseline
        key = (era, age_bracket, region)
        
        if key in self.divorce_baselines:
            return self.divorce_baselines[key]
        
        # Fallback to general baseline
        return {
            'expected_duration': 12.0,  # General average
            'expected_divorce_rate': 0.42,
            'sample_size': 1000
        }
    
    def _load_divorce_baselines(self) -> Dict:
        """
        Load divorce baseline data from database or use defaults
        
        Returns:
            Dict mapping (era, age_bracket, region) → baseline stats
        """
        baselines = {}
        
        # If database available, load from DivorceBaseline table
        if self.db:
            try:
                from core.marriage_models import DivorceBaseline
                baseline_records = self.db.query(DivorceBaseline).all()
                
                for record in baseline_records:
                    # Determine era from year range
                    year_mid = (record.marriage_year_start + record.marriage_year_end) / 2
                    if year_mid < 1990:
                        era = '1980s'
                    elif year_mid < 2000:
                        era = '1990s'
                    elif year_mid < 2010:
                        era = '2000s'
                    elif year_mid < 2020:
                        era = '2010s'
                    else:
                        era = '2020s'
                    
                    key = (era, record.age_bracket, record.geographic_region)
                    baselines[key] = {
                        'expected_duration': record.median_marriage_duration,
                        'expected_divorce_rate': record.divorce_rate,
                        'sample_size': record.sample_size
                    }
            except Exception as e:
                logger.warning(f"Could not load baselines from database: {e}")
        
        # Fallback: Default baselines (approximate U.S. statistics)
        if not baselines:
            baselines = self._get_default_baselines()
        
        return baselines
    
    def _get_default_baselines(self) -> Dict:
        """
        Default baseline statistics (approximate U.S. averages)
        
        Based on CDC and Census data
        """
        baselines = {}
        
        # Template: (era, age_bracket, region) → stats
        eras = ['1980s', '1990s', '2000s', '2010s', '2020s']
        age_brackets = ['18-24', '25-29', '30-34', '35-39', '40+']
        regions = ['USA', 'Northeast', 'South', 'Midwest', 'West']
        
        # Age effect (younger → higher divorce rate, shorter duration)
        age_divorce_rates = {
            '18-24': 0.55,
            '25-29': 0.45,
            '30-34': 0.38,
            '35-39': 0.32,
            '40+': 0.28
        }
        
        age_durations = {
            '18-24': 8.0,
            '25-29': 10.5,
            '30-34': 13.0,
            '35-39': 15.0,
            '40+': 17.0
        }
        
        # Era effect (divorce rates changed over time)
        era_modifiers = {
            '1980s': 1.05,  # Peak divorce era
            '1990s': 1.00,
            '2000s': 0.95,
            '2010s': 0.90,  # Declining divorce rates
            '2020s': 0.88
        }
        
        # Regional effect (small)
        region_modifiers = {
            'USA': 1.00,
            'Northeast': 0.95,
            'South': 1.05,  # Bible Belt effect
            'Midwest': 0.98,
            'West': 1.02
        }
        
        # Generate all combinations
        for era in eras:
            for age in age_brackets:
                for region in regions:
                    base_rate = age_divorce_rates[age]
                    base_duration = age_durations[age]
                    
                    # Apply modifiers
                    adjusted_rate = base_rate * era_modifiers[era] * region_modifiers[region]
                    adjusted_duration = base_duration / era_modifiers[era] * region_modifiers[region]
                    
                    key = (era, age, region)
                    baselines[key] = {
                        'expected_duration': adjusted_duration,
                        'expected_divorce_rate': min(adjusted_rate, 0.70),  # Cap at 70%
                        'sample_size': 500  # Assumed
                    }
        
        return baselines
    
    def _calculate_percentile(self, couple: MarriedCouple, actual_duration: float) -> float:
        """
        Calculate percentile rank of this couple within their cohort
        
        Args:
            couple: MarriedCouple
            actual_duration: Actual marriage duration
            
        Returns:
            Percentile (0-100)
        """
        # Query similar couples from database
        if not self.db:
            return 50.0  # Default to median
        
        try:
            # Get all couples in same cohort
            similar_couples = self.db.query(MarriedCouple).filter(
                MarriedCouple.cohort_era == couple.cohort_era,
                MarriedCouple.marriage_duration_years.isnot(None)
            ).all()
            
            if len(similar_couples) < 10:
                return 50.0  # Not enough data
            
            # Calculate percentile
            durations = [c.marriage_duration_years for c in similar_couples]
            percentile = (sum(1 for d in durations if d < actual_duration) / len(durations)) * 100
            
            return percentile
            
        except Exception as e:
            logger.warning(f"Could not calculate percentile: {e}")
            return 50.0
    
    def _analyze_children_names(self, couple: MarriedCouple, analysis: MarriageAnalysis):
        """
        Analyze children's names relative to parents
        
        Tests:
        1. Blending: Is child name style between parents?
        2. Dominance: Does one parent's style dominate?
        3. Innovation: Is child name more creative/unique than parents?
        
        Args:
            couple: MarriedCouple with children
            analysis: MarriageAnalysis to augment
        """
        if not couple.children or len(couple.children) == 0:
            return
        
        # Get parent name features
        p1_features = self.name_analyzer.analyze_name(couple.partner1_first)
        p2_features = self.name_analyzer.analyze_name(couple.partner2_first)
        
        for child in couple.children:
            # Analyze child name
            child_features = self.name_analyzer.analyze_name(child.first_name)
            
            # Calculate similarity to each parent
            sim_to_p1 = self._calculate_name_similarity(child_features, p1_features)
            sim_to_p2 = self._calculate_name_similarity(child_features, p2_features)
            
            # Blending score (is it between parents?)
            expected_blend = (
                (p1_features.get('memorability_score', 50) + p2_features.get('memorability_score', 50)) / 2.0
            )
            actual_child = child_features.get('memorability_score', 50)
            blending_score = 1.0 - abs(actual_child - expected_blend) / 50.0  # Normalize to 0-1
            
            # Dominance (which parent's style wins?)
            if sim_to_p1 > sim_to_p2 + 0.2:
                dominant_parent = 'partner1'
            elif sim_to_p2 > sim_to_p1 + 0.2:
                dominant_parent = 'partner2'
            else:
                dominant_parent = 'balanced'
            
            # Innovation score (how unique is child name?)
            innovation_score = child_features.get('uniqueness_score', 50) / 100.0
            
            # Update child record
            child.similarity_to_parent1 = sim_to_p1
            child.similarity_to_parent2 = sim_to_p2
            child.blending_score = blending_score
            child.dominant_parent = dominant_parent
            child.innovation_score = innovation_score
    
    def _calculate_name_similarity(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate similarity between two name feature sets
        
        Args:
            features1: Name features dict
            features2: Name features dict
            
        Returns:
            Similarity score (0-1, higher = more similar)
        """
        # Compare key features
        syl_diff = abs(features1.get('syllable_count', 2) - features2.get('syllable_count', 2))
        len_diff = abs(features1.get('character_length', 5) - features2.get('character_length', 5))
        mem_diff = abs(features1.get('memorability_score', 50) - features2.get('memorability_score', 50))
        
        # Normalize and invert (difference → similarity)
        syl_sim = 1.0 - min(syl_diff / 5.0, 1.0)
        len_sim = 1.0 - min(len_diff / 10.0, 1.0)
        mem_sim = 1.0 - min(mem_diff / 100.0, 1.0)
        
        # Average
        similarity = (syl_sim + len_sim + mem_sim) / 3.0
        
        return similarity
    
    def predict_relationship_outcome(self, 
                                    partner1_name: str,
                                    partner2_name: str,
                                    age1: int = None,
                                    age2: int = None,
                                    marriage_year: int = None) -> Dict:
        """
        Predict relationship outcome from names (BLIND PREDICTION)
        
        This method generates predictions WITHOUT seeing actual outcome.
        For use in blind testing framework.
        
        Args:
            partner1_name: First partner's name
            partner2_name: Second partner's name
            age1: Partner 1 age at marriage (optional)
            age2: Partner 2 age at marriage (optional)
            marriage_year: Year of marriage (optional)
            
        Returns:
            Dict with predictions
        """
        # Analyze relationship
        relationship = self.relationship_engine.analyze_relationship(
            partner1_name,
            partner2_name,
            include_phonetic=True
        )
        
        # Test theories
        theories = self._test_compatibility_theories(relationship)
        
        # Predict compatibility (0-1)
        predicted_compatibility = relationship.compatibility_score
        
        # Predict divorce risk (inverse of compatibility, adjusted)
        base_risk = 0.42  # General divorce rate
        name_adjustment = (0.5 - predicted_compatibility) * 0.4  # Max ±20% adjustment
        predicted_divorce_risk = max(0.0, min(1.0, base_risk + name_adjustment))
        
        # Predict longevity (adjusted by age and era if provided)
        base_longevity = 12.0  # General average
        
        if age1 and age2:
            # Adjust for age
            avg_age = (age1 + age2) / 2.0
            if avg_age < 25:
                base_longevity = 8.0
            elif avg_age < 30:
                base_longevity = 10.5
            elif avg_age < 35:
                base_longevity = 13.0
            else:
                base_longevity = 15.0
        
        # Name adjustment (±30%)
        name_boost = (predicted_compatibility - 0.5) * 0.6
        predicted_longevity = base_longevity * (1.0 + name_boost)
        
        # Confidence (based on theory agreement)
        theory_scores = [
            theories.similarity_score,
            theories.complementarity_score,
            theories.golden_ratio_score,
            theories.resonance_score
        ]
        theory_std = np.std(theory_scores)
        confidence = 1.0 - min(theory_std, 1.0)  # Low std = high confidence
        
        return {
            'predicted_compatibility': predicted_compatibility,
            'predicted_divorce_risk': predicted_divorce_risk,
            'predicted_longevity_years': predicted_longevity,
            'dominant_theory': theories.winning_theory,
            'confidence': confidence,
            'relationship_type': relationship.relationship_type,
            'theory_scores': {
                'similarity': theories.similarity_score,
                'complementarity': theories.complementarity_score,
                'golden_ratio': theories.golden_ratio_score,
                'resonance': theories.resonance_score
            }
        }
    
    def batch_analyze_couples(self, couples: List[MarriedCouple]) -> pd.DataFrame:
        """
        Analyze multiple couples and return results as DataFrame
        
        Args:
            couples: List of MarriedCouple objects
            
        Returns:
            DataFrame with all analysis results
        """
        results = []
        
        for couple in couples:
            try:
                analysis = self.analyze_couple(couple)
                
                result = {
                    'couple_id': couple.id,
                    'partner1': couple.partner1_first,
                    'partner2': couple.partner2_first,
                    'compatibility_score': analysis.compatibility_score,
                    'golden_ratio_proximity': analysis.golden_ratio_proximity,
                    'phonetic_distance': analysis.phonetic_distance,
                    'vowel_harmony': analysis.vowel_harmony,
                    'relationship_type': analysis.relationship_type,
                    'is_divorced': couple.is_divorced,
                    'marriage_duration': couple.marriage_duration_years,
                    'relative_success': analysis.relative_success_score,
                    'exceeds_expectations': analysis.exceeds_expectations,
                    'similarity_theory': analysis.similarity_theory_score,
                    'complementarity_theory': analysis.complementarity_theory_score,
                    'golden_ratio_theory': analysis.golden_ratio_theory_score,
                    'resonance_theory': analysis.resonance_theory_score,
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error analyzing couple {couple.id}: {e}")
                continue
        
        return pd.DataFrame(results)

