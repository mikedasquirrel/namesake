"""MTG Semantic Field Analyzer

Analyzes semantic domains and conceptual fields in MTG card names.

Maps names to conceptual domains:
- Destruction lexicon (annihilate, destroy, wrath)
- Creation lexicon (genesis, birth, growth)  
- Transformation lexicon (morph, shift, change)
- Control lexicon (counter, forbid, silence)
- Value lexicon (treasure, wealth, bounty)
- And others...

Uses semantic similarity to calculate distance from domain centroids.
"""

import logging
import re
from typing import Dict, List, Set, Tuple
import math

logger = logging.getLogger(__name__)


class MTGSemanticAnalyzer:
    """Analyzes semantic field membership and conceptual domains."""
    
    def __init__(self):
        # Semantic field lexicons
        self.semantic_fields = {
            'destruction': {
                'core': ['destroy', 'annihilate', 'obliterate', 'wrath', 'devastation'],
                'extended': ['ruin', 'shatter', 'break', 'demolish', 'ravage', 'crush',
                           'decimate', 'massacre', 'slaughter', 'eradicate'],
                'related': ['death', 'doom', 'end', 'terminus', 'apocalypse'],
                'color_affinity': ['R', 'B'],
            },
            'creation': {
                'core': ['create', 'birth', 'genesis', 'origin', 'beginning'],
                'extended': ['forge', 'craft', 'make', 'build', 'construct', 'spawn',
                           'generate', 'produce', 'manifest'],
                'related': ['growth', 'life', 'flourish', 'bloom', 'rise'],
                'color_affinity': ['G', 'W'],
            },
            'transformation': {
                'core': ['transform', 'change', 'shift', 'morph', 'mutate'],
                'extended': ['evolve', 'adapt', 'alter', 'convert', 'transmute',
                           'reshape', 'reform', 'metamorphosis'],
                'related': ['flux', 'transition', 'becoming', 'emergence'],
                'color_affinity': ['U', 'G'],
            },
            'control': {
                'core': ['counter', 'forbid', 'silence', 'bind', 'prevent'],
                'extended': ['stop', 'halt', 'block', 'restrain', 'contain', 'suppress',
                           'cancel', 'negate', 'nullify', 'void'],
                'related': ['law', 'order', 'authority', 'dominion', 'rule'],
                'color_affinity': ['U', 'W'],
            },
            'value': {
                'core': ['treasure', 'wealth', 'riches', 'bounty', 'prosperity'],
                'extended': ['gold', 'gem', 'jewel', 'hoard', 'fortune', 'abundance'],
                'related': ['precious', 'valuable', 'prize', 'reward'],
                'color_affinity': ['R', 'B'],
            },
            'sacrifice': {
                'core': ['sacrifice', 'offering', 'tribute', 'cost', 'price'],
                'extended': ['forfeit', 'give', 'surrender', 'relinquish', 'renounce'],
                'related': ['loss', 'debt', 'payment', 'blood'],
                'color_affinity': ['B'],
            },
            'protection': {
                'core': ['protect', 'shield', 'guard', 'defend', 'ward'],
                'extended': ['shelter', 'sanctuary', 'haven', 'refuge', 'safety',
                           'preservation', 'safeguard', 'fortify'],
                'related': ['immunity', 'indestructible', 'resilience', 'armor'],
                'color_affinity': ['W'],
            },
            'knowledge': {
                'core': ['knowledge', 'wisdom', 'insight', 'understanding', 'lore'],
                'extended': ['study', 'research', 'learn', 'discover', 'reveal',
                           'enlighten', 'teach', 'scry', 'vision'],
                'related': ['mind', 'intellect', 'thought', 'memory', 'archive'],
                'color_affinity': ['U'],
            },
            'power': {
                'core': ['power', 'might', 'strength', 'force', 'potency'],
                'extended': ['dominance', 'supremacy', 'mastery', 'authority', 'command'],
                'related': ['titan', 'colossus', 'juggernaut', 'behemoth'],
                'color_affinity': ['R', 'B', 'G'],
            },
            'life': {
                'core': ['life', 'living', 'vitality', 'vigor', 'essence'],
                'extended': ['heal', 'restore', 'renew', 'revive', 'resurrect',
                           'rejuvenate', 'mend', 'cure'],
                'related': ['soul', 'spirit', 'breath', 'pulse', 'heartbeat'],
                'color_affinity': ['W', 'G'],
            },
            'death': {
                'core': ['death', 'dead', 'dying', 'demise', 'mortality'],
                'extended': ['kill', 'slay', 'murder', 'execute', 'terminate',
                           'extinguish', 'perish', 'expire'],
                'related': ['corpse', 'grave', 'tomb', 'crypt', 'necro'],
                'color_affinity': ['B'],
            },
            'nature': {
                'core': ['nature', 'natural', 'wild', 'primal', 'savage'],
                'extended': ['forest', 'beast', 'growth', 'verdant', 'wilderness',
                           'fauna', 'flora', 'organic'],
                'related': ['earth', 'vine', 'root', 'leaf', 'branch'],
                'color_affinity': ['G'],
            },
            'artifice': {
                'core': ['artifact', 'machine', 'construct', 'device', 'mechanism'],
                'extended': ['forge', 'craft', 'engineer', 'invent', 'automaton',
                           'golem', 'assembly', 'workshop'],
                'related': ['metal', 'steel', 'bronze', 'copper', 'iron'],
                'color_affinity': ['U', 'R'],
            },
            'chaos': {
                'core': ['chaos', 'random', 'chance', 'luck', 'wild'],
                'extended': ['unpredictable', 'volatile', 'erratic', 'turbulent',
                           'mayhem', 'pandemonium', 'havoc'],
                'related': ['storm', 'frenzy', 'madness', 'confusion'],
                'color_affinity': ['R'],
            },
            'order': {
                'core': ['order', 'law', 'justice', 'balance', 'harmony'],
                'extended': ['regulate', 'organize', 'structure', 'discipline',
                           'hierarchy', 'system', 'code'],
                'related': ['peace', 'stability', 'equilibrium', 'symmetry'],
                'color_affinity': ['W', 'U'],
            },
        }
        
        # Compile all words for fast lookup
        self.all_semantic_words = set()
        self.word_to_fields = {}  # Map word to fields it appears in
        
        for field, data in self.semantic_fields.items():
            words = set(data['core'] + data['extended'] + data['related'])
            self.all_semantic_words.update(words)
            for word in words:
                if word not in self.word_to_fields:
                    self.word_to_fields[word] = []
                self.word_to_fields[word].append(field)
    
    def analyze_semantic_fields(self, name: str, oracle_text: str = None,
                               color_identity: str = None) -> Dict:
        """Comprehensive semantic field analysis.
        
        Args:
            name: Card name
            oracle_text: Card oracle text (for mechanic validation)
            color_identity: Color identity
            
        Returns:
            Dict with semantic field memberships and scores
        """
        name_lower = name.lower()
        oracle_lower = oracle_text.lower() if oracle_text else ''
        
        # Detect field memberships
        name_field_scores = self._calculate_field_scores(name_lower)
        oracle_field_scores = self._calculate_field_scores(oracle_lower) if oracle_text else {}
        
        # Combine name + oracle (name has more weight for nominative determinism)
        combined_scores = {}
        for field in self.semantic_fields.keys():
            name_score = name_field_scores.get(field, 0.0)
            oracle_score = oracle_field_scores.get(field, 0.0)
            # Weight name 70%, oracle 30%
            combined_scores[field] = (name_score * 0.7) + (oracle_score * 0.3)
        
        # Determine dominant fields
        dominant_fields = self._get_dominant_fields(combined_scores)
        
        # Semantic density (how many semantic domains present)
        semantic_density = sum(1 for score in combined_scores.values() if score > 30)
        
        # Semantic focus (concentration in one domain vs spread)
        semantic_focus = self._calculate_semantic_focus(combined_scores)
        
        # Color-semantic alignment (if color provided)
        color_alignment = {}
        if color_identity:
            color_alignment = self._analyze_color_semantic_alignment(
                combined_scores, color_identity
            )
        
        # Polar pairs (destruction vs creation, chaos vs order, etc.)
        polar_tension = self._analyze_polar_tension(combined_scores)
        
        # Semantic complexity (number of fields + diversity)
        semantic_complexity = self._calculate_semantic_complexity(
            combined_scores, semantic_density, semantic_focus
        )
        
        return {
            # Field scores (0-100) for name alone
            'name_semantic_scores': {k: round(v, 2) for k, v in name_field_scores.items()},
            
            # Combined name + oracle scores
            'combined_semantic_scores': {k: round(v, 2) for k, v in combined_scores.items()},
            
            # Dominant fields
            'primary_field': dominant_fields[0] if dominant_fields else 'neutral',
            'secondary_field': dominant_fields[1] if len(dominant_fields) > 1 else None,
            'dominant_fields': dominant_fields,
            
            # Metrics
            'semantic_density': semantic_density,
            'semantic_focus': round(semantic_focus, 2),
            'semantic_complexity': round(semantic_complexity, 2),
            
            # Color alignment
            'color_semantic_alignment': color_alignment,
            
            # Polar dynamics
            'polar_tension': polar_tension,
            
            # Specific features
            'has_destruction_semantics': combined_scores.get('destruction', 0) > 40,
            'has_creation_semantics': combined_scores.get('creation', 0) > 40,
            'is_semantically_rich': semantic_density >= 3,
            'is_semantically_focused': semantic_focus > 70,
        }
    
    def _calculate_field_scores(self, text: str) -> Dict[str, float]:
        """Calculate semantic field scores for given text."""
        scores = {}
        
        for field, data in self.semantic_fields.items():
            score = 0.0
            
            # Core words (highest weight)
            core_matches = sum(1 for word in data['core'] if word in text)
            score += core_matches * 40
            
            # Extended words (medium weight)
            extended_matches = sum(1 for word in data['extended'] if word in text)
            score += extended_matches * 25
            
            # Related words (lower weight)
            related_matches = sum(1 for word in data['related'] if word in text)
            score += related_matches * 15
            
            # Normalize to 0-100
            scores[field] = min(100, score)
        
        return scores
    
    def _get_dominant_fields(self, scores: Dict[str, float], threshold: float = 30.0) -> List[str]:
        """Get dominant semantic fields above threshold."""
        # Sort by score
        sorted_fields = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return fields above threshold
        return [field for field, score in sorted_fields if score > threshold]
    
    def _calculate_semantic_focus(self, scores: Dict[str, float]) -> float:
        """Calculate how focused (vs spread) the semantic profile is.
        
        High focus = concentrated in 1-2 domains
        Low focus = spread across many domains
        """
        if not scores:
            return 50.0
        
        # Calculate entropy-like measure
        total = sum(scores.values())
        if total == 0:
            return 0.0
        
        # Normalize scores
        probs = [s / total for s in scores.values() if s > 0]
        
        if not probs:
            return 0.0
        
        # Calculate concentration (inverse of entropy)
        # Perfect focus = 100, perfect spread = 0
        max_entropy = math.log(len(probs)) if len(probs) > 1 else 1
        entropy = -sum(p * math.log(p) for p in probs)
        
        focus = (1 - (entropy / max_entropy)) * 100 if max_entropy > 0 else 100
        
        return focus
    
    def _analyze_color_semantic_alignment(self, scores: Dict[str, float],
                                         color_identity: str) -> Dict:
        """Analyze alignment between semantic fields and color identity."""
        alignment_score = 0.0
        aligned_fields = []
        misaligned_fields = []
        
        for field, score in scores.items():
            if score < 20:  # Ignore weak signals
                continue
            
            field_data = self.semantic_fields[field]
            expected_colors = set(field_data['color_affinity'])
            actual_colors = set(color_identity)
            
            # Check alignment
            if expected_colors & actual_colors:  # Intersection
                alignment_score += score
                aligned_fields.append(field)
            else:
                misaligned_fields.append(field)
        
        # Normalize
        total_relevant_score = sum(s for s in scores.values() if s >= 20)
        alignment_percentage = (alignment_score / total_relevant_score * 100) if total_relevant_score > 0 else 0
        
        return {
            'alignment_percentage': round(alignment_percentage, 2),
            'aligned_fields': aligned_fields,
            'misaligned_fields': misaligned_fields,
            'is_aligned': alignment_percentage > 60,
        }
    
    def _analyze_polar_tension(self, scores: Dict[str, float]) -> Dict:
        """Analyze tension between opposing semantic poles."""
        polar_pairs = [
            ('destruction', 'creation'),
            ('chaos', 'order'),
            ('death', 'life'),
            ('power', 'knowledge'),
            ('sacrifice', 'protection'),
        ]
        
        tensions = {}
        max_tension = 0.0
        dominant_pole = None
        
        for pole_a, pole_b in polar_pairs:
            score_a = scores.get(pole_a, 0)
            score_b = scores.get(pole_b, 0)
            
            # Tension = both poles present
            # Directionality = which pole dominates
            if score_a > 20 or score_b > 20:
                tension_level = min(score_a, score_b)  # Tension from weaker pole
                direction = score_a - score_b  # Positive = pole_a dominant
                
                tensions[f'{pole_a}_vs_{pole_b}'] = {
                    'tension_level': round(tension_level, 2),
                    'direction': round(direction, 2),
                    'dominant_pole': pole_a if direction > 0 else pole_b,
                }
                
                if tension_level > max_tension:
                    max_tension = tension_level
                    dominant_pole = f'{pole_a}_vs_{pole_b}'
        
        return {
            'polar_tensions': tensions,
            'max_tension': round(max_tension, 2),
            'dominant_tension': dominant_pole,
            'has_polar_tension': max_tension > 30,
        }
    
    def _calculate_semantic_complexity(self, scores: Dict[str, float],
                                      density: int, focus: float) -> float:
        """Calculate overall semantic complexity.
        
        High complexity = many semantic domains (high density) but unfocused
        Low complexity = single focused domain or no strong domains
        """
        # Density component (0-100)
        density_score = min(density * 20, 100)
        
        # Unfocus component (inverse of focus)
        unfocus_score = 100 - focus
        
        # Combine: complexity increases with both density and unfocus
        complexity = (density_score * 0.6) + (unfocus_score * 0.4)
        
        return complexity

