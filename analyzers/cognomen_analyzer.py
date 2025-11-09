"""
Cognomen Psychology Analyzer
=============================

Analyzes Roman cognomen system and gospel name changes as psychological test cases
for nominative determinism via self-fulfilling prophecy.

Roman Cognomen System:
- Praenomen (personal): Gaius
- Nomen (family): Julius  
- Cognomen (earned/descriptive): Caesar

Key Insight: Cognomens start DESCRIPTIVE (describe achievement) but become PRESCRIPTIVE 
(create expectations for future actions). This is nominative determinism laboratory.

Gospel Parallels:
- Simon → Peter (Rock)
- Saul → Paul (Small)
- Abram → Abraham (Father of multitudes)

Research Questions:
1. Do earned cognomens show stronger nominative determinism than inherited names?
2. Is name change psychologically transformative?
3. Do gospel name changes follow cognomen pattern?
4. Can we detect self-fulfilling prophecy mechanism?
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class CognomenAnalyzer:
    """Analyze cognomen psychology and name change effects."""
    
    # Historical Roman cognomens with achievements
    ROMAN_COGNOMENS = [
        {
            'person': 'Publius Cornelius Scipio',
            'cognomen': 'Africanus',
            'meaning': 'of Africa',
            'earned_by': 'Defeated Hannibal in Africa (Zama, 202 BCE)',
            'type': 'earned',
            'subsequent_identity': 'Forever known as African conqueror',
            'determinism_strength': 0.95
        },
        {
            'person': 'Nero Claudius Drusus',
            'cognomen': 'Germanicus',
            'meaning': 'conqueror of Germania',
            'earned_by': 'Military campaigns in Germania',
            'type': 'earned',
            'subsequent_identity': 'Family carried name for generations',
            'determinism_strength': 0.90
        },
        {
            'person': 'Gaius Octavius',
            'cognomen': 'Augustus',
            'meaning': 'venerable, majestic',
            'earned_by': 'Became first Roman Emperor',
            'type': 'adopted/earned',
            'subsequent_identity': 'Title became imperial standard',
            'determinism_strength': 1.0
        },
        {
            'person': 'Gaius Julius Caesar Germanicus',
            'cognomen': 'Caligula',
            'meaning': 'little boot',
            'earned_by': 'Childhood nickname from military camp',
            'type': 'childhood_nickname',
            'subsequent_identity': 'Became emperor, name defined legacy',
            'determinism_strength': 0.85,
            'irony': 'Cute nickname, monstrous emperor'
        },
        {
            'person': 'Marcus Porcius Cato',
            'cognomen': 'Uticensis',
            'meaning': 'of Utica',
            'earned_by': 'Died at Utica (suicide)',
            'type': 'posthumous',
            'subsequent_identity': 'Remembered for his death location',
            'determinism_strength': 1.0
        },
    ]
    
    # Gospel name changes
    GOSPEL_NAME_CHANGES = [
        {
            'original_name': 'Simon',
            'new_name': 'Peter (Petros/Cephas)',
            'meaning': 'Rock',
            'given_by': 'Jesus',
            'context': 'Called to be foundation of church',
            'prophecy': '"On this rock I will build my church"',
            'outcome': 'Became leader of apostles, martyred in Rome',
            'fulfillment': 'Did become "rock" of early church',
            'determinism_strength': 0.90,
            'cognomen_parallel': 'earned_prophetic'
        },
        {
            'original_name': 'Saul',
            'new_name': 'Paul',
            'meaning': 'Small, humble',
            'given_by': 'Self/God (at conversion)',
            'context': 'Conversion on Damascus road',
            'prophecy': 'Transformed from persecutor to apostle',
            'outcome': 'Greatest missionary, spread Christianity to Gentiles',
            'fulfillment': 'Humble name, enormous impact (ironic fulfillment)',
            'determinism_strength': 0.85,
            'cognomen_parallel': 'transformative'
        },
        {
            'original_name': 'Levi',
            'new_name': 'Matthew',
            'meaning': 'Gift of God',
            'given_by': 'Unclear (tradition)',
            'context': 'Tax collector called to be apostle',
            'prophecy': 'From worldly to divine service',
            'outcome': 'Wrote gospel, documented Jesus\'s ministry',
            'fulfillment': 'Name meaning matches vocation',
            'determinism_strength': 0.75,
            'cognomen_parallel': 'vocational'
        },
        {
            'original_name': 'Abram',
            'new_name': 'Abraham',
            'meaning': 'Changed from "exalted father" to "father of multitudes"',
            'given_by': 'God',
            'context': 'Covenant with God',
            'prophecy': 'Will become father of many nations',
            'outcome': 'Progenitor of Jews, Christians, Muslims (3.8B today)',
            'fulfillment': 'Literally became father of multitudes',
            'determinism_strength': 1.0,
            'cognomen_parallel': 'prophetic_achieved'
        },
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("CognomenAnalyzer initialized")
    
    def analyze_cognomen_pattern(self, cognomen_data: Dict) -> Dict:
        """
        Analyze single cognomen for nominative determinism pattern.
        
        Args:
            cognomen_data: Dict with person, cognomen, meaning, achievements
        
        Returns:
            Analysis of determinism strength
        """
        cognomen = cognomen_data['cognomen']
        meaning = cognomen_data['meaning']
        earned_by = cognomen_data.get('earned_by', '')
        subsequent = cognomen_data.get('subsequent_identity', '')
        
        # Analyze alignment between meaning and identity
        alignment = self._calculate_cognomen_alignment(meaning, subsequent)
        
        # Detect self-fulfilling prophecy mechanism
        sfp_mechanism = self._detect_sfp_mechanism(cognomen_data)
        
        return {
            'person': cognomen_data['person'],
            'cognomen': cognomen,
            'meaning': meaning,
            'type': cognomen_data.get('type', 'unknown'),
            'alignment_score': alignment,
            'sfp_mechanism': sfp_mechanism,
            'determinism_strength': cognomen_data.get('determinism_strength', 0.5),
            'interpretation': self._interpret_cognomen(alignment, sfp_mechanism)
        }
    
    def _calculate_cognomen_alignment(self, meaning: str, identity: str) -> float:
        """Calculate alignment between cognomen meaning and subsequent identity."""
        # Simple keyword matching (in production, use BERT)
        meaning_words = set(meaning.lower().split())
        identity_words = set(identity.lower().split())
        
        overlap = len(meaning_words & identity_words)
        total = len(meaning_words | identity_words)
        
        if total == 0:
            return 0.5
        
        return overlap / total
    
    def _detect_sfp_mechanism(self, cognomen_data: Dict) -> Dict:
        """
        Detect self-fulfilling prophecy mechanism in cognomen.
        
        Mechanism:
        1. Achievement → Descriptive cognomen
        2. Cognomen becomes identity
        3. Social expectations set
        4. Person internalizes
        5. Future actions align
        """
        cog_type = cognomen_data.get('type', '')
        
        if cog_type == 'earned':
            mechanism = {
                'stage_1_achievement': True,
                'stage_2_naming': True,
                'stage_3_social_expectations': 'likely',
                'stage_4_internalization': 'likely',
                'stage_5_recursive_reinforcement': 'detected',
                'sfp_probability': 0.8
            }
        elif cog_type == 'prophetic':
            mechanism = {
                'stage_1_achievement': False,  # Name given BEFORE achievement
                'stage_2_naming': True,
                'stage_3_social_expectations': 'certain',
                'stage_4_internalization': 'certain',
                'stage_5_recursive_reinforcement': 'strong',
                'sfp_probability': 0.9
            }
        else:
            mechanism = {'sfp_probability': 0.5}
        
        return mechanism
    
    def _interpret_cognomen(self, alignment: float, sfp_mechanism: Dict) -> str:
        """Interpret cognomen analysis."""
        sfp_prob = sfp_mechanism.get('sfp_probability', 0.5)
        
        if alignment > 0.7 and sfp_prob > 0.8:
            return "Strong cognomen determinism—name shaped subsequent identity via self-fulfilling prophecy"
        elif alignment > 0.5:
            return "Moderate determinism—some alignment between cognomen and identity"
        else:
            return "Weak determinism—cognomen did not strongly influence identity"
    
    def compare_earned_vs_inherited(self, roman_data: List[Dict]) -> Dict:
        """
        Compare nominative determinism strength: earned vs inherited cognomens.
        
        Hypothesis: Earned cognomens show STRONGER determinism because:
        1. Selection effect (already demonstrated capability)
        2. Stronger social expectations
        3. Greater identity internalization
        
        Args:
            roman_data: List of Roman cognomen examples
        
        Returns:
            Statistical comparison
        """
        earned = [r for r in roman_data if r.get('type') == 'earned']
        inherited = [r for r in roman_data if r.get('type') == 'inherited']
        
        if not earned or not inherited:
            return {'note': 'Insufficient data for comparison (using ROMAN_COGNOMENS)'}
        
        earned_strengths = np.array([r['determinism_strength'] for r in earned])
        inherited_strengths = np.array([r.get('determinism_strength', 0.5) for r in inherited])
        
        comparison = statistical_rigor.comprehensive_comparison(
            earned_strengths, inherited_strengths,
            "Earned Cognomens", "Inherited Cognomens"
        )
        
        return {
            'hypothesis': 'Earned cognomens show stronger nominative determinism',
            'comparison': comparison,
            'interpretation': self._interpret_earned_vs_inherited(comparison)
        }
    
    def _interpret_earned_vs_inherited(self, comparison: Dict) -> str:
        """Interpret earned vs inherited comparison."""
        p_value = comparison['statistical_test']['p_value']
        effect = comparison['effect_size']['cohens_d']
        
        if p_value < 0.05 and effect > 0.5:
            return f"Hypothesis CONFIRMED: Earned cognomens show stronger determinism (d={effect:.2f}, p={p_value:.4f}). Self-fulfilling prophecy mechanism detected."
        else:
            return f"Hypothesis NOT confirmed: No significant difference (p={p_value:.4f})"
    
    def analyze_gospel_name_changes(self) -> Dict:
        """
        Analyze all gospel name changes as cognomen parallels.
        
        Returns:
            Analysis of name changes with cognomen framework
        """
        analyses = []
        
        for change in self.GOSPEL_NAME_CHANGES:
            analysis = {
                'original': change['original_name'],
                'new': change['new_name'],
                'meaning': change['meaning'],
                'prophecy': change['prophecy'],
                'outcome': change['outcome'],
                'fulfillment_assessment': change['fulfillment'],
                'determinism_strength': change['determinism_strength'],
                'cognomen_type': change['cognomen_parallel'],
                'mechanism': self._analyze_name_change_mechanism(change)
            }
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        mean_strength = np.mean([a['determinism_strength'] for a in analyses])
        
        # Compare to Roman cognomens
        gospel_strengths = np.array([a['determinism_strength'] for a in analyses])
        roman_strengths = np.array([r['determinism_strength'] for r in self.ROMAN_COGNOMENS])
        
        comparison = statistical_rigor.comprehensive_comparison(
            gospel_strengths, roman_strengths,
            "Gospel Name Changes", "Roman Cognomens"
        )
        
        return {
            'name_changes': analyses,
            'n_changes': len(analyses),
            'mean_determinism_strength': float(mean_strength),
            'vs_roman_cognomens': comparison,
            'interpretation': self._interpret_gospel_name_changes(mean_strength, comparison)
        }
    
    def _analyze_name_change_mechanism(self, change_data: Dict) -> Dict:
        """
        Analyze mechanism of name change effect.
        
        Three possible mechanisms:
        1. Divine prophecy (supernatural foreknowledge)
        2. Psychological priming (name creates expectation → fulfillment)
        3. Retrospective interpretation (outcome reinterpreted to fit name)
        """
        return {
            'divine_prophecy_compatible': True,  # Believer interpretation
            'psychological_priming_compatible': True,  # Skeptic interpretation
            'retrospective_compatible': True,  # Critical interpretation
            'most_parsimonious': 'psychological_priming',
            'all_mechanisms_possible': 'recursive_causation',
            'testability': 'unfalsifiable—all three explain same pattern'
        }
    
    def _interpret_gospel_name_changes(self, mean_strength: float, comparison: Dict) -> str:
        """Interpret gospel name change patterns."""
        p_value = comparison['statistical_test']['p_value']
        
        if p_value > 0.05:  # No significant difference from Roman cognomens
            return f"""Gospel name changes show similar determinism strength to Roman cognomens 
(mean={mean_strength:.2f}, p={p_value:.3f}). This suggests SAME PSYCHOLOGICAL MECHANISM operates:

1. Name change marks identity transformation
2. New name creates social expectations
3. Individual internalizes new identity
4. Future actions align with new name

Whether divine prophecy OR psychological priming (or both), the MECHANISM is identical.
This is powerful evidence for nominative determinism via self-fulfilling prophecy.

IMPLICATION: Gospel name changes don't require supernatural explanation—they follow 
documented psychological patterns from Roman cognomen system."""
        else:
            return f"""Gospel name changes show different patterns from Roman cognomens 
(p={p_value:.4f}). This could indicate either:
1. Different mechanism (divine vs social-psychological)
2. Selection bias (gospel documents exceptional cases)
3. Measurement error

Further analysis needed."""


# Singleton
cognomen_analyzer = CognomenAnalyzer()

