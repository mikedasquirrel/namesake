"""
Nominative Ensemble Generator
Generate interaction features between person names and label names

Purpose: Create nominative ensemble features (person × label interactions)
Theory: Harsh player + Harsh team = Amplification, etc.
Expected Impact: +5-9% ROI from ensemble nominative effects
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class NominativeEnsembleGenerator:
    """
    Generate ensemble interaction features between persons and labels
    
    Creates features like:
    - Player name × Team name alignment
    - Player name × Venue name synergy
    - Player name × Play type matching
    - Player name × Prop type harmony
    """
    
    def __init__(self):
        """Initialize ensemble generator"""
        pass
    
    def generate_ensemble_features(self, person_features: Dict, label_features: Dict,
                                  interaction_type: str = 'general') -> Dict:
        """
        Generate ensemble interaction features
        
        Args:
            person_features: Linguistic features of person name
            label_features: Linguistic features of label
            interaction_type: Type of interaction ('team', 'venue', 'play', etc.)
            
        Returns:
            Dictionary of ensemble features
        """
        ensemble = {}
        
        # === TYPE 1: ALIGNMENT EFFECTS ===
        ensemble.update(self._calculate_alignment_features(person_features, label_features))
        
        # === TYPE 2: CONTRAST EFFECTS ===
        ensemble.update(self._calculate_contrast_features(person_features, label_features))
        
        # === TYPE 3: SYNERGY EFFECTS ===
        ensemble.update(self._calculate_synergy_features(person_features, label_features))
        
        # === TYPE 4: DOMINANCE EFFECTS ===
        ensemble.update(self._calculate_dominance_features(person_features, label_features))
        
        # === TYPE 5: HARMONY EFFECTS ===
        ensemble.update(self._calculate_harmony_features(person_features, label_features))
        
        # === TYPE 6: INTERACTION-SPECIFIC FEATURES ===
        ensemble.update(self._calculate_interaction_specific_features(
            person_features, label_features, interaction_type
        ))
        
        # === METADATA ===
        ensemble['interaction_type'] = interaction_type
        ensemble['person_label'] = f"{person_features.get('name', 'Unknown')} × {label_features.get('label', 'Unknown')}"
        
        return ensemble
    
    def _calculate_alignment_features(self, person: Dict, label: Dict) -> Dict:
        """
        Calculate alignment/matching features
        Hypothesis: Similar phonetics → Amplification
        """
        features = {}
        
        # Harshness alignment
        person_harsh = person.get('harshness', 50)
        label_harsh = label.get('harshness', 50)
        harsh_diff = abs(person_harsh - label_harsh)
        features['harshness_alignment'] = 100 - harsh_diff  # 100 = perfect alignment
        features['both_harsh'] = 1 if person_harsh > 65 and label_harsh > 65 else 0
        features['both_soft'] = 1 if person_harsh < 45 and label_harsh < 45 else 0
        
        # Memorability alignment
        person_mem = person.get('memorability', 50)
        label_mem = label.get('memorability', 50)
        mem_diff = abs(person_mem - label_mem)
        features['memorability_alignment'] = 100 - mem_diff
        features['both_memorable'] = 1 if person_mem > 65 and label_mem > 65 else 0
        
        # Syllable alignment (brevity matching)
        person_syll = person.get('syllables', 2)
        label_syll = label.get('syllables', 2)
        syll_diff = abs(person_syll - label_syll)
        features['syllable_alignment'] = max(0, 5 - syll_diff) * 20  # 0-100 scale
        features['both_brief'] = 1 if person_syll <= 2 and label_syll <= 2 else 0
        
        # Phonetic type alignment (power, speed, soft)
        person_power = person.get('power_phoneme_ratio', 0.2)
        label_power = label.get('power_phoneme_ratio', 0.2)
        power_diff = abs(person_power - label_power)
        features['power_phoneme_alignment'] = 100 - (power_diff * 100)
        
        # Overall alignment score
        features['overall_alignment'] = np.mean([
            features['harshness_alignment'],
            features['memorability_alignment'],
            features['syllable_alignment'],
            features['power_phoneme_alignment']
        ])
        
        return features
    
    def _calculate_contrast_features(self, person: Dict, label: Dict) -> Dict:
        """
        Calculate contrast/mismatch features
        Hypothesis: High contrast → Standout effect or mismatch penalty
        """
        features = {}
        
        # Harshness contrast
        person_harsh = person.get('harshness', 50)
        label_harsh = label.get('harshness', 50)
        features['harshness_contrast'] = abs(person_harsh - label_harsh)
        features['extreme_harsh_contrast'] = 1 if features['harshness_contrast'] > 40 else 0
        
        # Memorability contrast
        person_mem = person.get('memorability', 50)
        label_mem = label.get('memorability', 50)
        features['memorability_contrast'] = abs(person_mem - label_mem)
        
        # Complexity contrast
        person_complex = person.get('consonant_clusters', 0) + person.get('length', 5) / 3
        label_complex = label.get('consonant_clusters', 0) + label.get('length', 5) / 3
        features['complexity_contrast'] = abs(person_complex - label_complex)
        
        # Standout effect (person much harsher/more memorable than label)
        features['person_dominates_harsh'] = 1 if (person_harsh - label_harsh) > 25 else 0
        features['person_dominates_memorable'] = 1 if (person_mem - label_mem) > 25 else 0
        features['label_dominates_harsh'] = 1 if (label_harsh - person_harsh) > 25 else 0
        
        return features
    
    def _calculate_synergy_features(self, person: Dict, label: Dict) -> Dict:
        """
        Calculate synergy/multiplicative features
        Hypothesis: Combined effects > sum of parts
        """
        features = {}
        
        person_harsh = person.get('harshness', 50)
        label_harsh = label.get('harshness', 50)
        person_mem = person.get('memorability', 50)
        label_mem = label.get('memorability', 50)
        person_syll = person.get('syllables', 2)
        label_syll = label.get('syllables', 2)
        
        # Multiplicative synergy (both high → amplification)
        features['harsh_synergy'] = (person_harsh / 100) * (label_harsh / 100) * 100
        features['memorable_synergy'] = (person_mem / 100) * (label_mem / 100) * 100
        
        # Brevity synergy (both short → speed/impact)
        features['brevity_synergy'] = (4 - min(person_syll, 4)) * (4 - min(label_syll, 4)) * 10
        
        # Combined power (sum of power phonemes)
        person_power = person.get('power_phoneme_count', 0)
        label_power = label.get('power_phoneme_count', 0)
        features['combined_power_phonemes'] = person_power + label_power
        
        # Combined speed phonemes
        person_speed = person.get('speed_phoneme_count', 0)
        label_speed = label.get('speed_phoneme_count', 0)
        features['combined_speed_phonemes'] = person_speed + label_speed
        
        # Phonetic resonance (similar phonetic profile)
        features['phonetic_resonance'] = 100 - features.get('power_phoneme_alignment', 50) if 'power_phoneme_alignment' in features else 50
        
        return features
    
    def _calculate_dominance_features(self, person: Dict, label: Dict) -> Dict:
        """
        Calculate dominance/superiority features
        Hypothesis: One name dominates → that entity's characteristics prevail
        """
        features = {}
        
        person_harsh = person.get('harshness', 50)
        label_harsh = label.get('harshness', 50)
        person_mem = person.get('memorability', 50)
        label_mem = label.get('memorability', 50)
        person_length = person.get('length', 5)
        label_length = label.get('length', 5)
        
        # Harshness dominance
        features['harshness_differential'] = person_harsh - label_harsh
        features['harshness_dominance_factor'] = abs(features['harshness_differential']) / 50
        features['person_harsher'] = 1 if features['harshness_differential'] > 15 else 0
        features['label_harsher'] = 1 if features['harshness_differential'] < -15 else 0
        
        # Memorability dominance
        features['memorability_differential'] = person_mem - label_mem
        features['person_more_memorable'] = 1 if features['memorability_differential'] > 15 else 0
        features['label_more_memorable'] = 1 if features['memorability_differential'] < -15 else 0
        
        # Length dominance (longer = more complex/important?)
        features['length_differential'] = person_length - label_length
        features['person_longer'] = 1 if features['length_differential'] > 3 else 0
        
        # Overall dominance score
        features['person_dominance_score'] = (
            features['person_harsher'] * 30 +
            features['person_more_memorable'] * 30 +
            features['person_longer'] * 20 +
            max(0, features['harshness_differential']) * 0.2
        )
        
        features['label_dominance_score'] = (
            features['label_harsher'] * 30 +
            features['label_more_memorable'] * 30 +
            max(0, -features['harshness_differential']) * 0.2
        )
        
        return features
    
    def _calculate_harmony_features(self, person: Dict, label: Dict) -> Dict:
        """
        Calculate harmony/compatibility features
        Hypothesis: Harmonious combinations → positive synergy
        """
        features = {}
        
        # Vowel harmony (both use similar vowels)
        person_front_vowels = person.get('front_vowel_count', 0)
        person_back_vowels = person.get('back_vowel_count', 0)
        label_front_vowels = label.get('front_vowel_count', 0)
        label_back_vowels = label.get('back_vowel_count', 0)
        
        person_vowel_balance = person_front_vowels / max(person_front_vowels + person_back_vowels, 1)
        label_vowel_balance = label_front_vowels / max(label_front_vowels + label_back_vowels, 1)
        features['vowel_harmony'] = 100 - abs(person_vowel_balance - label_vowel_balance) * 100
        
        # Consonant harmony (both use similar consonant types)
        person_plosives = person.get('plosive_count', 0)
        person_fricatives = person.get('fricative_count', 0)
        label_plosives = label.get('plosive_count', 0)
        label_fricatives = label.get('fricative_count', 0)
        
        person_cons_balance = person_plosives / max(person_plosives + person_fricatives, 1)
        label_cons_balance = label_plosives / max(label_plosives + label_fricatives, 1)
        features['consonant_harmony'] = 100 - abs(person_cons_balance - label_cons_balance) * 100
        
        # Rhythmic harmony (similar syllable patterns)
        person_syll = person.get('syllables', 2)
        label_syll = label.get('syllables', 2)
        features['rhythmic_harmony'] = 100 - abs(person_syll - label_syll) * 15
        
        # Sonority harmony (both melodic or both harsh)
        person_sonority = person.get('sonority_score', 50)
        label_sonority = label.get('sonority_score', 50)
        features['sonority_harmony'] = 100 - abs(person_sonority - label_sonority)
        
        # Overall harmony score
        features['overall_harmony'] = np.mean([
            features['vowel_harmony'],
            features['consonant_harmony'],
            features['rhythmic_harmony'],
            features['sonority_harmony']
        ])
        
        return features
    
    def _calculate_interaction_specific_features(self, person: Dict, label: Dict,
                                                interaction_type: str) -> Dict:
        """
        Calculate features specific to interaction type
        """
        features = {}
        
        if interaction_type == 'team':
            features.update(self._team_player_interaction(person, label))
        elif interaction_type == 'venue':
            features.update(self._venue_player_interaction(person, label))
        elif interaction_type == 'play':
            features.update(self._play_player_interaction(person, label))
        elif interaction_type == 'prop':
            features.update(self._prop_player_interaction(person, label))
        else:
            # Generic interaction features
            features['interaction_strength'] = features.get('overall_alignment', 50) if 'overall_alignment' in features else 50
        
        return features
    
    def _team_player_interaction(self, person: Dict, label: Dict) -> Dict:
        """Team-specific interaction features"""
        features = {}
        
        person_harsh = person.get('harshness', 50)
        team_aggression = label.get('team_aggression_score', 50)
        
        # Harsh player + aggressive team = amplification
        features['team_aggression_match'] = min(person_harsh, team_aggression) / 100
        features['team_amplification_factor'] = (person_harsh / 100) * (team_aggression / 100) * 100
        
        # Team tradition interaction
        team_tradition = label.get('team_tradition_score', 50)
        person_mem = person.get('memorability', 50)
        features['tradition_memorability_synergy'] = (team_tradition / 100) * (person_mem / 100) * 100
        
        # Home field advantage amplifier (if harsh team + harsh player)
        features['home_field_amplifier'] = 1.0 + (features['team_amplification_factor'] / 200)  # 1.0-1.5×
        
        return features
    
    def _venue_player_interaction(self, person: Dict, label: Dict) -> Dict:
        """Venue-specific interaction features"""
        features = {}
        
        person_harsh = person.get('harshness', 50)
        venue_intimidation = label.get('venue_intimidation', 50)
        venue_prestige = label.get('venue_prestige', 50)
        
        # Harsh player + intimidating venue = home dominance
        features['venue_intimidation_match'] = (person_harsh / 100) * (venue_intimidation / 100) * 100
        
        # Memorable player + prestigious venue = spotlight effect
        person_mem = person.get('memorability', 50)
        features['venue_spotlight_effect'] = (person_mem / 100) * (venue_prestige / 100) * 100
        
        # Venue amplification factor
        features['venue_amplifier'] = 1.0 + (venue_intimidation / 500)  # 1.0-1.2×
        
        return features
    
    def _play_player_interaction(self, person: Dict, label: Dict) -> Dict:
        """Play-specific interaction features"""
        features = {}
        
        person_harsh = person.get('harshness', 50)
        person_syll = person.get('syllables', 2)
        person_power = person.get('power_phoneme_ratio', 0.2)
        person_speed = person.get('speed_phoneme_ratio', 0.1)
        
        play_power = label.get('play_power_indicator', 0)
        play_speed = label.get('play_speed_indicator', 0)
        play_trick = label.get('play_trick_indicator', 0)
        play_complexity = label.get('play_complexity', 1)
        
        # Harsh player + power play = match
        features['power_play_match'] = (person_harsh / 100) * play_power * 100
        
        # Speed player + speed play = match
        features['speed_play_match'] = person_speed * play_speed * 100
        
        # Brief name + quick play = match
        features['quick_play_match'] = (4 - min(person_syll, 4)) * play_speed * 25
        
        # Memorable player + trick play = match
        person_mem = person.get('memorability', 50)
        features['trick_play_match'] = (person_mem / 100) * play_trick * 100
        
        # Play complexity alignment
        person_complexity = person.get('consonant_clusters', 0) + (person_syll - 1)
        features['play_complexity_alignment'] = 100 - abs(person_complexity - play_complexity) * 20
        
        # Overall play-player synergy
        features['play_player_synergy'] = np.mean([
            features['power_play_match'],
            features['speed_play_match'],
            features['quick_play_match'],
            features['trick_play_match']
        ])
        
        return features
    
    def _prop_player_interaction(self, person: Dict, label: Dict) -> Dict:
        """Prop-specific interaction features"""
        features = {}
        
        person_harsh = person.get('harshness', 50)
        person_mem = person.get('memorability', 50)
        
        prop_intensity = label.get('prop_action_intensity', 60)
        prop_precision = label.get('prop_precision_demand', 60)
        
        # Harsh player + intense prop (tackles, sacks) = match
        features['intensity_prop_match'] = (person_harsh / 100) * (prop_intensity / 100) * 100
        
        # Memorable player + precision prop = mismatch (or match?)
        features['precision_prop_interaction'] = (person_mem / 100) * (prop_precision / 100) * 100
        
        # Prop type amplifier (intense props amplified by harsh names)
        features['prop_amplifier'] = 1.0 + ((person_harsh / 100) * (prop_intensity / 100) * 0.3)  # 1.0-1.3×
        
        return features
    
    def generate_batch_ensemble_features(self, person_features: Dict,
                                        label_features_list: List[Dict],
                                        interaction_types: List[str]) -> List[Dict]:
        """
        Generate ensemble features for multiple labels
        
        Args:
            person_features: Single person's linguistic features
            label_features_list: List of label feature dicts
            interaction_types: List of interaction types (same length as labels)
            
        Returns:
            List of ensemble feature dictionaries
        """
        if len(label_features_list) != len(interaction_types):
            raise ValueError("label_features_list and interaction_types must have same length")
        
        return [
            self.generate_ensemble_features(person_features, label_features, interaction_type)
            for label_features, interaction_type in zip(label_features_list, interaction_types)
        ]


if __name__ == "__main__":
    # Test the ensemble generator
    from label_nominative_extractor import LabelNominativeExtractor
    
    print("="*80)
    print("NOMINATIVE ENSEMBLE GENERATOR - Test Run")
    print("="*80)
    
    # Mock person features (Nick Chubb - harsh RB name)
    person_features = {
        'name': 'Nick Chubb',
        'syllables': 2,
        'harshness': 72,
        'memorability': 68,
        'length': 9,
        'power_phoneme_count': 4,
        'speed_phoneme_count': 0,
        'power_phoneme_ratio': 0.44,
        'speed_phoneme_ratio': 0.0,
        'front_vowel_count': 1,
        'back_vowel_count': 1,
        'plosive_count': 3,
        'fricative_count': 0,
        'consonant_clusters': 2,
        'sonority_score': 65
    }
    
    # Extract label features
    label_extractor = LabelNominativeExtractor()
    
    # Test team interaction
    chiefs_features = label_extractor.extract_label_features("Kansas City Chiefs", "team")
    
    # Generate ensemble
    ensemble_gen = NominativeEnsembleGenerator()
    ensemble_features = ensemble_gen.generate_ensemble_features(
        person_features, chiefs_features, "team"
    )
    
    print(f"\nPerson: {person_features['name']}")
    print(f"Label: {chiefs_features['label']} ({chiefs_features['label_type']})")
    print(f"\n{'='*80}")
    print("ENSEMBLE FEATURES:")
    print(f"{'='*80}")
    
    print(f"\nAlignment Features:")
    print(f"  Harshness Alignment: {ensemble_features['harshness_alignment']:.1f}")
    print(f"  Overall Alignment: {ensemble_features['overall_alignment']:.1f}")
    print(f"  Both Harsh: {ensemble_features['both_harsh']}")
    
    print(f"\nSynergy Features:")
    print(f"  Harsh Synergy: {ensemble_features['harsh_synergy']:.1f}")
    print(f"  Combined Power Phonemes: {ensemble_features['combined_power_phonemes']}")
    
    print(f"\nDominance Features:")
    print(f"  Harshness Differential: {ensemble_features['harshness_differential']:.1f}")
    print(f"  Person Dominance Score: {ensemble_features['person_dominance_score']:.1f}")
    
    print(f"\nHarmony Features:")
    print(f"  Overall Harmony: {ensemble_features['overall_harmony']:.1f}")
    print(f"  Consonant Harmony: {ensemble_features['consonant_harmony']:.1f}")
    
    print(f"\nTeam-Specific Features:")
    print(f"  Team Amplification Factor: {ensemble_features['team_amplification_factor']:.1f}")
    print(f"  Home Field Amplifier: {ensemble_features['home_field_amplifier']:.3f}×")
    
    print(f"\n{'='*80}")
    print(f"Total Ensemble Features Generated: {len(ensemble_features)}")
    print(f"{'='*80}")
    
    # Test another interaction type
    print(f"\n\n{'='*80}")
    print("Testing Play Interaction...")
    print(f"{'='*80}")
    
    play_features = label_extractor.extract_label_features("Power I", "play")
    play_ensemble = ensemble_gen.generate_ensemble_features(
        person_features, play_features, "play"
    )
    
    print(f"\nPlay: {play_features['label']}")
    print(f"  Power Play Match: {play_ensemble['power_play_match']:.1f}")
    print(f"  Play-Player Synergy: {play_ensemble['play_player_synergy']:.1f}")
    
    print(f"\n{'='*80}")
    print("ENSEMBLE GENERATION COMPLETE")
    print("="*80)

