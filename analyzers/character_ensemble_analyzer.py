"""
Character Ensemble Analyzer
============================

Analyzes character groups (ensembles) using same methodology as sports team roster analysis.
Tests whether character groups show phonetic coherence, optimization, and role-based patterns.

Methodology Parallel to Sports Teams:
- Individual names → Roster statistics (mean, stddev, harmony)
- Protagonist ensemble vs Antagonist ensemble (like home vs away teams)
- Composite scores (weighted combination of factors)
- Within-group coherence vs between-group contrast

Key Research Questions:
1. Do protagonist ensembles show phonetic coherence? (optimization marker)
2. Are hero/villain groups phonetically contrasted? (narrative design)
3. Do gospels show realistic diversity or fictional optimization?
4. Can we distinguish fiction from truth-claiming via ensemble patterns?
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from collections import Counter, defaultdict

from analyzers.acoustic_analyzer import acoustic_analyzer
from analyzers.phonetic_universals_analyzer import phonetic_universals_analyzer
from analyzers.statistical_rigor import statistical_rigor

logger = logging.getLogger(__name__)


class CharacterEnsembleAnalyzer:
    """
    Analyze character ensembles like sports team rosters.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("CharacterEnsembleAnalyzer initialized")
    
    def analyze_ensemble(self, character_names: List[Dict], 
                        ensemble_name: str = "Ensemble") -> Dict:
        """
        Analyze a group of characters as an ensemble.
        
        Args:
            character_names: List of dicts with 'name', 'role', optional acoustic data
            ensemble_name: Name of the ensemble (e.g., "Apostles", "Fellowship")
        
        Returns:
            Comprehensive ensemble analysis
        """
        if not character_names:
            return {'error': 'No characters provided'}
        
        self.logger.info(f"Analyzing ensemble: {ensemble_name} ({len(character_names)} characters)")
        
        # Analyze each character
        analyzed_characters = []
        for char in character_names:
            name = char.get('name', '')
            if name:
                try:
                    acoustic = acoustic_analyzer.analyze(name)
                    universals = phonetic_universals_analyzer.analyze(name)
                    
                    analyzed_characters.append({
                        'name': name,
                        'role': char.get('role', 'unknown'),
                        'melodiousness': acoustic['overall']['melodiousness'],
                        'harshness': acoustic['harshness']['overall_score'],
                        'phonetic_complexity': acoustic['overall']['phonetic_complexity'],
                        'bouba_kiki': universals['bouba_kiki']['score'],
                        'emotional_valence': universals['emotional_valence']['universal'],
                        'pronounceability': acoustic['pronounceability']['universal']
                    })
                except Exception as e:
                    self.logger.error(f"Error analyzing {name}: {e}")
        
        if not analyzed_characters:
            return {'error': 'No valid character analyses'}
        
        # Calculate ensemble-level statistics
        ensemble_stats = self._calculate_ensemble_statistics(analyzed_characters)
        
        # Role-based analysis
        role_analysis = self._analyze_by_role(analyzed_characters)
        
        # Phonetic coherence (like team harmony)
        coherence = self._calculate_phonetic_coherence(analyzed_characters)
        
        # Composite scores (like team composite_linguistic_score)
        composite = self._calculate_composite_scores(ensemble_stats)
        
        # Optimization detection
        optimization = self._detect_optimization(analyzed_characters, role_analysis)
        
        return {
            'ensemble_name': ensemble_name,
            'size': len(analyzed_characters),
            'characters': analyzed_characters,
            'ensemble_statistics': ensemble_stats,
            'role_analysis': role_analysis,
            'phonetic_coherence': coherence,
            'composite_scores': composite,
            'optimization_detection': optimization,
            'interpretation': self._interpret_ensemble(ensemble_stats, coherence, optimization)
        }
    
    def _calculate_ensemble_statistics(self, characters: List[Dict]) -> Dict:
        """
        Calculate ensemble-level statistics (parallel to roster statistics).
        """
        melodiousness_values = [c['melodiousness'] for c in characters]
        harshness_values = [c['harshness'] for c in characters]
        complexity_values = [c['phonetic_complexity'] for c in characters]
        bouba_kiki_values = [c['bouba_kiki'] for c in characters]
        valence_values = [c['emotional_valence'] for c in characters]
        pronounce_values = [c['pronounceability'] for c in characters]
        
        return {
            # Mean scores (like roster_mean_X)
            'mean_melodiousness': float(np.mean(melodiousness_values)),
            'mean_harshness': float(np.mean(harshness_values)),
            'mean_complexity': float(np.mean(complexity_values)),
            'mean_bouba_kiki': float(np.mean(bouba_kiki_values)),
            'mean_valence': float(np.mean(valence_values)),
            'mean_pronounceability': float(np.mean(pronounce_values)),
            
            # Diversity measures (like roster_syllable_stddev)
            'stddev_melodiousness': float(np.std(melodiousness_values)),
            'stddev_harshness': float(np.std(harshness_values)),
            'stddev_complexity': float(np.std(complexity_values)),
            
            # Harmony score (inverse of variance - like roster_harmony_score)
            'harmony_score': float(1 - np.var(melodiousness_values)),
            'phonetic_diversity': float(np.std(melodiousness_values) + np.std(harshness_values)),
            
            # Extremes (like roster_max/min)
            'most_melodious': float(max(melodiousness_values)),
            'least_melodious': float(min(melodiousness_values)),
            'harshest_character': float(max(harshness_values)),
            'softest_character': float(min(harshness_values)),
            
            # Range metrics
            'melodiousness_range': float(max(melodiousness_values) - min(melodiousness_values)),
            'harshness_range': float(max(harshness_values) - min(harshness_values)),
        }
    
    def _analyze_by_role(self, characters: List[Dict]) -> Dict:
        """
        Analyze ensemble split by character roles.
        Tests if roles show distinct naming patterns (optimization marker).
        """
        by_role = defaultdict(list)
        for char in characters:
            role = char['role']
            by_role[role].append(char)
        
        role_stats = {}
        for role, chars in by_role.items():
            if chars:
                melodious_vals = [c['melodiousness'] for c in chars]
                harsh_vals = [c['harshness'] for c in chars]
                
                role_stats[role] = {
                    'count': len(chars),
                    'mean_melodiousness': float(np.mean(melodious_vals)),
                    'mean_harshness': float(np.mean(harsh_vals)),
                    'stddev_melodiousness': float(np.std(melodious_vals)),
                    'names': [c['name'] for c in chars]
                }
        
        # Calculate between-role variance (high = optimization)
        if len(role_stats) >= 2:
            role_melodious_means = [rs['mean_melodiousness'] for rs in role_stats.values()]
            between_role_variance = float(np.var(role_melodious_means))
            
            # Within-role variance (average)
            within_role_variances = [rs['stddev_melodiousness']**2 for rs in role_stats.values()]
            within_role_variance = float(np.mean(within_role_variances))
            
            # F-ratio: between/within (high = strong role differentiation)
            f_ratio = between_role_variance / within_role_variance if within_role_variance > 0 else 0
        else:
            between_role_variance = 0
            within_role_variance = 0
            f_ratio = 0
        
        return {
            'roles': role_stats,
            'n_roles': len(role_stats),
            'between_role_variance': float(between_role_variance),
            'within_role_variance': float(within_role_variance),
            'f_ratio': float(f_ratio),
            'role_differentiation': 'High' if f_ratio > 2 else 'Medium' if f_ratio > 1 else 'Low'
        }
    
    def _calculate_phonetic_coherence(self, characters: List[Dict]) -> Dict:
        """
        Calculate phonetic coherence of ensemble (like roster_harmony_score).
        
        Coherence = Low variance in phonetic features
        High coherence suggests optimization; Low coherence suggests realism
        """
        melodious_vals = [c['melodiousness'] for c in characters]
        harsh_vals = [c['harshness'] for c in characters]
        
        # Coefficient of variation (stddev / mean)
        melodious_cv = np.std(melodious_vals) / np.mean(melodious_vals) if np.mean(melodious_vals) > 0 else 0
        harsh_cv = np.std(harsh_vals) / np.mean(harsh_vals) if np.mean(harsh_vals) > 0 else 0
        
        # Coherence = 1 - average CV (low CV = high coherence)
        coherence = 1 - (melodious_cv + harsh_cv) / 2
        
        # Pairwise compatibility (how well names "sound together")
        compatibility_scores = []
        for i, char1 in enumerate(characters):
            for char2 in characters[i+1:]:
                # Compatibility = similarity in phonetic profile
                similarity = 1 - abs(char1['melodiousness'] - char2['melodiousness'])
                compatibility_scores.append(similarity)
        
        mean_compatibility = float(np.mean(compatibility_scores)) if compatibility_scores else 0.5
        
        return {
            'coherence_score': float(max(coherence, 0)),
            'melodiousness_cv': float(melodious_cv),
            'harshness_cv': float(harsh_cv),
            'mean_pairwise_compatibility': mean_compatibility,
            'coherence_level': 'High' if coherence > 0.7 else 'Medium' if coherence > 0.5 else 'Low',
            'interpretation': self._interpret_coherence(coherence)
        }
    
    def _interpret_coherence(self, coherence: float) -> str:
        """Interpret coherence score."""
        if coherence > 0.7:
            return "High phonetic coherence suggests optimized ensemble (fiction marker)"
        elif coherence > 0.5:
            return "Medium coherence—balanced between optimization and diversity"
        else:
            return "Low coherence suggests realistic name diversity (truth-claim marker)"
    
    def _calculate_composite_scores(self, ensemble_stats: Dict) -> Dict:
        """
        Calculate composite scores (parallel to team composite_linguistic_score).
        
        Weighting: Melodiousness 40%, Harshness 30%, Pronounceability 30%
        """
        melodious = ensemble_stats['mean_melodiousness']
        harsh = ensemble_stats['mean_harshness']
        pronounce = ensemble_stats['mean_pronounceability']
        harmony = ensemble_stats['harmony_score']
        
        # Composite linguistic score
        composite_linguistic = (
            melodious * 0.40 +
            (1 - harsh) * 0.30 +  # Invert harshness (lower = better)
            pronounce * 0.30
        )
        
        # Composite appeal (melodious + harmony)
        composite_appeal = (melodious + harmony) / 2
        
        # Composite power (harshness + complexity)
        composite_power = (harsh + ensemble_stats['mean_complexity']) / 2
        
        return {
            'composite_linguistic_score': float(composite_linguistic),
            'composite_appeal': float(composite_appeal),
            'composite_power': float(composite_power),
            'composite_harmony': float(harmony),
            'interpretation': self._interpret_composite(composite_linguistic, composite_appeal, composite_power)
        }
    
    def _interpret_composite(self, linguistic: float, appeal: float, power: float) -> str:
        """Interpret composite scores."""
        if linguistic > 0.7 and appeal > 0.7:
            return "Highly optimized ensemble—melodious and harmonious (fiction marker)"
        elif power > 0.7:
            return "Powerful/harsh ensemble—potentially antagonist group"
        else:
            return "Balanced ensemble—realistic name diversity"
    
    def _detect_optimization(self, characters: List[Dict], role_analysis: Dict) -> Dict:
        """
        Detect if ensemble shows signs of narrative optimization.
        
        Optimization markers:
        1. High role differentiation (heroes melodious, villains harsh)
        2. High coherence within roles
        3. Low variance overall (all names "good quality")
        4. Suspicious perfection (too good to be random)
        """
        optimization_score = 0.0
        markers = []
        
        # Marker 1: Role differentiation
        if role_analysis.get('f_ratio', 0) > 2:
            optimization_score += 0.35
            markers.append("Strong role differentiation (F={:.2f})".format(role_analysis['f_ratio']))
        
        # Marker 2: High overall quality
        mean_melodious = np.mean([c['melodiousness'] for c in characters])
        if mean_melodious > 0.7:
            optimization_score += 0.25
            markers.append(f"Suspiciously high mean melodiousness ({mean_melodious:.2f})")
        
        # Marker 3: Low variance (homogeneity)
        melodious_std = np.std([c['melodiousness'] for c in characters])
        if melodious_std < 0.15:
            optimization_score += 0.20
            markers.append(f"Low variance—over-optimization ({melodious_std:.3f})")
        
        # Marker 4: No "bad" names (floor effect)
        min_melodious = min([c['melodiousness'] for c in characters])
        if min_melodious > 0.5:
            optimization_score += 0.20
            markers.append(f"No poorly melodious names (min={min_melodious:.2f})")
        
        return {
            'optimization_score': float(optimization_score),
            'optimization_level': 'High' if optimization_score > 0.7 else 'Medium' if optimization_score > 0.4 else 'Low',
            'markers_detected': markers,
            'interpretation': self._interpret_optimization(optimization_score),
            'implication': 'Fictional invention likely' if optimization_score > 0.7 else 'Truth-claiming likely' if optimization_score < 0.3 else 'Ambiguous'
        }
    
    def _interpret_optimization(self, score: float) -> str:
        """Interpret optimization score."""
        if score > 0.7:
            return "Strong optimization detected—names appear selected for narrative effect (FICTION MARKER)"
        elif score > 0.4:
            return "Moderate optimization—some selection bias present"
        else:
            return "Low optimization—realistic name diversity (TRUTH-CLAIM MARKER)"
    
    def _interpret_ensemble(self, stats: Dict, coherence: Dict, optimization: Dict) -> str:
        """Generate comprehensive interpretation."""
        lines = []
        
        lines.append(f"Ensemble shows {coherence['coherence_level'].lower()} phonetic coherence (score: {coherence['coherence_score']:.2f})")
        lines.append(f"Mean melodiousness: {stats['mean_melodiousness']:.2f} (diversity: σ={stats['stddev_melodiousness']:.3f})")
        lines.append(f"Optimization level: {optimization['optimization_level']} ({optimization['optimization_score']:.2f})")
        lines.append(f"Implication: {optimization['implication']}")
        
        return ". ".join(lines)
    
    def compare_ensembles(self, ensemble1: List[Dict], ensemble2: List[Dict],
                         name1: str = "Protagonists", name2: str = "Antagonists") -> Dict:
        """
        Compare two ensembles (e.g., heroes vs villains, apostles vs pharisees).
        
        Tests if groups are phonetically contrasted (narrative design).
        
        Args:
            ensemble1, ensemble2: Lists of character dicts
            name1, name2: Ensemble labels
        
        Returns:
            Statistical comparison with implications
        """
        # Analyze both ensembles
        analysis1 = self.analyze_ensemble(ensemble1, name1)
        analysis2 = self.analyze_ensemble(ensemble2, name2)
        
        if 'error' in analysis1 or 'error' in analysis2:
            return {'error': 'Invalid ensembles'}
        
        # Extract melodiousness arrays
        melodious1 = np.array([c['melodiousness'] for c in analysis1['characters']])
        melodious2 = np.array([c['melodiousness'] for c in analysis2['characters']])
        
        # Statistical comparison using rigorous methods
        comparison = statistical_rigor.comprehensive_comparison(
            melodious1, melodious2, name1, name2
        )
        
        # Calculate phonetic distance between ensembles
        mean1 = analysis1['ensemble_statistics']['mean_melodiousness']
        mean2 = analysis2['ensemble_statistics']['mean_melodiousness']
        
        phonetic_distance = abs(mean1 - mean2)
        
        # Contrast ratio (how different are the groups?)
        contrast_ratio = phonetic_distance / ((mean1 + mean2) / 2) if (mean1 + mean2) > 0 else 0
        
        return {
            'ensemble1': {
                'name': name1,
                'analysis': analysis1
            },
            'ensemble2': {
                'name': name2,
                'analysis': analysis2
            },
            'statistical_comparison': comparison,
            'phonetic_distance': float(phonetic_distance),
            'contrast_ratio': float(contrast_ratio),
            'contrast_interpretation': self._interpret_contrast(phonetic_distance, contrast_ratio, comparison),
            'optimization_assessment': self._assess_ensemble_optimization(analysis1, analysis2, contrast_ratio)
        }
    
    def _interpret_contrast(self, distance: float, ratio: float, comparison: Dict) -> str:
        """Interpret phonetic contrast between ensembles."""
        p_value = comparison['statistical_test']['p_value']
        effect_size = comparison['effect_size']['cohens_d']
        
        if p_value < 0.05 and abs(effect_size) > 0.5:
            strength = "significant"
            if distance > 0.3:
                interpretation = f"Strong phonetic contrast (distance={distance:.2f}, d={effect_size:.2f}) suggests deliberate differentiation (OPTIMIZATION MARKER)"
            else:
                interpretation = f"Moderate contrast suggests some differentiation"
        else:
            interpretation = f"No significant contrast (p={p_value:.3f})—groups phonetically similar (REALISM MARKER)"
        
        return interpretation
    
    def _assess_ensemble_optimization(self, analysis1: Dict, analysis2: Dict, 
                                     contrast_ratio: float) -> str:
        """
        Assess if ensemble comparison suggests fictional optimization or realistic diversity.
        """
        opt1 = analysis1['optimization_detection']['optimization_score']
        opt2 = analysis2['optimization_detection']['optimization_score']
        
        avg_optimization = (opt1 + opt2) / 2
        
        if avg_optimization > 0.6 and contrast_ratio > 0.3:
            return """HIGH OPTIMIZATION: Both ensembles internally optimized AND strongly contrasted.
Suggests: Fictional narrative with deliberate hero/villain phonetic differentiation.
Implication: Author consciously crafting opposing groups."""
        
        elif avg_optimization < 0.3 and contrast_ratio < 0.2:
            return """LOW OPTIMIZATION: Both ensembles show realistic diversity AND minimal contrast.
Suggests: Documentary realism—groups not phonetically designed for opposition.
Implication: Truth-claiming or historically constrained narrative."""
        
        else:
            return """MODERATE OPTIMIZATION: Mixed signals.
Suggests: Some selection bias but realistic constraints present.
Implication: Interpreted history or historical fiction with dramatic license."""
    
    def gospel_ensemble_analysis(self, gospel_name: str) -> Dict:
        """
        Analyze gospel character ensembles: Apostles vs Pharisees/Opponents.
        
        Args:
            gospel_name: Which gospel (matthew, mark, luke, john)
        
        Returns:
            Ensemble analysis for gospel groups
        """
        # Known gospel character groups
        apostles = [
            {'name': 'Peter', 'role': 'protagonist'},
            {'name': 'John', 'role': 'protagonist'},
            {'name': 'James', 'role': 'protagonist'},
            {'name': 'Andrew', 'role': 'protagonist'},
            {'name': 'Philip', 'role': 'protagonist'},
            {'name': 'Thomas', 'role': 'protagonist'},
            {'name': 'Matthew', 'role': 'protagonist'},
            {'name': 'Bartholomew', 'role': 'protagonist'},
            {'name': 'James son of Alphaeus', 'role': 'protagonist'},
            {'name': 'Thaddaeus', 'role': 'protagonist'},
            {'name': 'Simon', 'role': 'protagonist'},
            {'name': 'Judas', 'role': 'antagonist'},  # Traitor
        ]
        
        opponents = [
            {'name': 'Caiaphas', 'role': 'antagonist'},
            {'name': 'Annas', 'role': 'antagonist'},
            {'name': 'Pilate', 'role': 'antagonist'},
            {'name': 'Herod', 'role': 'antagonist'},
            {'name': 'Barabbas', 'role': 'antagonist'},
        ]
        
        women_followers = [
            {'name': 'Mary Magdalene', 'role': 'supporting'},
            {'name': 'Mary mother of Jesus', 'role': 'supporting'},
            {'name': 'Martha', 'role': 'supporting'},
            {'name': 'Mary of Bethany', 'role': 'supporting'},
        ]
        
        # Analyze each group
        apostle_analysis = self.analyze_ensemble(apostles, "Apostles")
        opponent_analysis = self.analyze_ensemble(opponents, "Opponents")
        women_analysis = self.analyze_ensemble(women_followers, "Women Followers")
        
        # Compare apostles vs opponents
        comparison = self.compare_ensembles(apostles, opponents, "Apostles", "Opponents")
        
        return {
            'gospel': gospel_name,
            'apostle_ensemble': apostle_analysis,
            'opponent_ensemble': opponent_analysis,
            'women_ensemble': women_analysis,
            'apostles_vs_opponents': comparison,
            'overall_assessment': self._assess_gospel_ensembles(apostle_analysis, opponent_analysis, comparison),
            'name_repetition': self._calculate_gospel_name_repetition(apostles + opponents + women_followers)
        }
    
    def _assess_gospel_ensembles(self, apostle_analysis: Dict, opponent_analysis: Dict,
                                comparison: Dict) -> str:
        """Overall assessment of gospel ensemble patterns."""
        
        apostle_opt = apostle_analysis['optimization_detection']['optimization_score']
        opponent_opt = opponent_analysis['optimization_detection']['optimization_score']
        contrast = comparison['phonetic_distance']
        
        if apostle_opt < 0.3 and opponent_opt < 0.3 and contrast < 0.2:
            return """Gospel ensembles show LOW OPTIMIZATION and LOW CONTRAST.
Both apostles and opponents have realistic name diversity without strong phonetic differentiation.
This supports TRUTH-CLAIMING DOCUMENTARY interpretation—real people had diverse names not optimized for narrative roles.

Evidence strength: STRONG for historical authenticity."""
        
        elif apostle_opt > 0.6 or opponent_opt > 0.6:
            return """Gospel ensembles show OPTIMIZATION in at least one group.
This suggests some selection bias or narrative shaping.
However, doesn't prove fiction—could be selective emphasis within historical framework.

Evidence strength: MODERATE for literary construction within truth-claiming."""
        
        else:
            return """Gospel ensembles show MIXED PATTERNS.
Some optimization present but realistic diversity maintained.
Consistent with 'interpreted history' model—real people, selective emphasis.

Evidence strength: Supports scholarly consensus of theological biography."""
    
    def _calculate_gospel_name_repetition(self, all_characters: List[Dict]) -> Dict:
        """
        Calculate name repetition in gospel (CRITICAL MARKER).
        
        High repetition = realism (multiple Johns, Marys)
        Low repetition = optimization (each character distinct)
        """
        names = [c['name'] for c in all_characters]
        name_counts = Counter(names)
        
        repeated_names = [name for name, count in name_counts.items() if count > 1]
        repetition_rate = len(repeated_names) / len(set(names)) if names else 0
        
        # Check for "Mary" specifically (multiple Marys = historically realistic)
        mary_count = sum(1 for name in names if 'Mary' in name)
        
        return {
            'total_characters': len(all_characters),
            'unique_names': len(set(names)),
            'repeated_names': repeated_names,
            'repetition_rate': float(repetition_rate),
            'mary_count': mary_count,
            'interpretation': self._interpret_repetition(repetition_rate, mary_count)
        }
    
    def _interpret_repetition(self, rate: float, mary_count: int) -> str:
        """Interpret name repetition rate."""
        if rate > 0.25:  # >25% of unique names appear multiple times
            return f"HIGH name repetition ({rate:.1%})—historically realistic. Multiple Marys ({mary_count}) especially authentic. TRUTH-CLAIM MARKER."
        elif rate > 0.15:
            return f"MODERATE repetition ({rate:.1%})—balanced between realism and clarity."
        else:
            return f"LOW repetition ({rate:.1%})—each character distinct. Narrative optimization for clarity. FICTION MARKER."


# Singleton
character_ensemble_analyzer = CharacterEnsembleAnalyzer()

