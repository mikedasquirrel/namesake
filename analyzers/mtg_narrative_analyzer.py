"""MTG Narrative Structure Analyzer

Analyzes narrative and storytelling patterns encoded in MTG card names.

MTG names often encode narrative arcs:
- Hero's journey progression (Student → Apprentice → Master → Elder)
- Temporal markers (Ancient, Eternal, Young, New)
- Transformation vocabulary (Ascended, Corrupted, Reborn)
- Agency and voice (active vs passive constructions)
- Epic vs mundane framing
"""

import logging
import re
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class MTGNarrativeAnalyzer:
    """Analyzes narrative and storytelling structures in MTG card names."""
    
    def __init__(self):
        # Hero's journey stages
        self.heros_journey_stages = {
            'novice': {
                'markers': ['student', 'apprentice', 'novice', 'initiate', 'acolyte', 'neophyte'],
                'stage': 1,
                'narrative_weight': 20,
            },
            'developing': {
                'markers': ['adept', 'disciple', 'practitioner', 'journeyman', 'seeker'],
                'stage': 2,
                'narrative_weight': 40,
            },
            'proficient': {
                'markers': ['master', 'expert', 'champion', 'veteran', 'savant'],
                'stage': 3,
                'narrative_weight': 60,
            },
            'legendary': {
                'markers': ['elder', 'grand master', 'archmaster', 'supreme', 'legendary'],
                'stage': 4,
                'narrative_weight': 80,
            },
            'transcendent': {
                'markers': ['ancient', 'eternal', 'immortal', 'god', 'primordial'],
                'stage': 5,
                'narrative_weight': 100,
            },
        }
        
        # Temporal progression markers
        self.temporal_markers = {
            'primordial': ['primordial', 'first', 'genesis', 'dawn', 'origin'],
            'ancient': ['ancient', 'elder', 'old', 'forgotten', 'lost'],
            'eternal': ['eternal', 'everlasting', 'undying', 'immortal', 'timeless'],
            'present': ['current', 'now', 'living', 'present'],
            'new': ['new', 'young', 'rising', 'emerging', 'nascent'],
            'future': ['prophesied', 'foretold', 'destined', 'fated'],
        }
        
        # Transformation vocabulary
        self.transformation_types = {
            'ascension': {
                'markers': ['ascended', 'risen', 'elevated', 'transcended', 'awakened'],
                'direction': 'upward',
                'valence': 'positive',
            },
            'corruption': {
                'markers': ['corrupted', 'fallen', 'twisted', 'tainted', 'defiled', 'plagued'],
                'direction': 'downward',
                'valence': 'negative',
            },
            'rebirth': {
                'markers': ['reborn', 'renewed', 'revived', 'resurrected', 'restored'],
                'direction': 'cyclical',
                'valence': 'positive',
            },
            'evolution': {
                'markers': ['evolved', 'transformed', 'changed', 'shifted', 'mutated'],
                'direction': 'horizontal',
                'valence': 'neutral',
            },
            'destruction': {
                'markers': ['shattered', 'broken', 'destroyed', 'ruined', 'unmade'],
                'direction': 'downward',
                'valence': 'negative',
            },
        }
        
        # Agency markers (active vs passive voice)
        self.agency_markers = {
            'high_agency': {
                'verbs': ['commands', 'conquers', 'destroys', 'creates', 'rules', 'wields'],
                'roles': ['master', 'lord', 'king', 'queen', 'commander', 'sovereign'],
            },
            'medium_agency': {
                'verbs': ['seeks', 'guards', 'watches', 'defends', 'protects'],
                'roles': ['guardian', 'protector', 'keeper', 'warden'],
            },
            'low_agency': {
                'roles': ['servant', 'slave', 'minion', 'thrall', 'puppet'],
                'passive_markers': ['bound', 'enslaved', 'controlled', 'captured'],
            },
        }
        
        # Title complexity (simple vs epic multi-clause titles)
        self.title_complexity_markers = {
            'simple_descriptor': 1,  # e.g., "Forest Bear"
            'single_title': 2,  # e.g., "Lord of Atlantis"
            'double_title': 3,  # e.g., "Ob Nixilis, the Fallen"
            'epic_clause': 4,  # e.g., "Gisela, Blade of Goldnight"
            'legendary_epithet': 5,  # e.g., "Nicol Bolas, God-Pharaoh"
        }
        
        # Narrative framing
        self.narrative_frames = {
            'epic': ['legendary', 'epic', 'saga', 'chronicle', 'tale'],
            'mythic': ['god', 'titan', 'primordial', 'elder', 'ancient'],
            'intimate': ['young', 'small', 'humble', 'simple'],
            'tragic': ['fallen', 'doomed', 'cursed', 'damned', 'forsaken'],
            'heroic': ['champion', 'savior', 'hero', 'liberator', 'defender'],
            'villainous': ['tyrant', 'villain', 'oppressor', 'destroyer', 'conqueror'],
        }
        
        # Relational/social markers
        self.relational_markers = {
            'familial': ['father', 'mother', 'brother', 'sister', 'child', 'kin'],
            'hierarchical': ['lord', 'master', 'servant', 'king', 'queen', 'subject'],
            'communal': ['council', 'guild', 'assembly', 'congregation', 'tribe'],
            'solitary': ['lone', 'solo', 'hermit', 'outcast', 'exile'],
        }
    
    def analyze_narrative_structure(self, name: str, card_type: str = None,
                                    flavor_text: str = None, is_legendary: bool = False) -> Dict:
        """Comprehensive narrative structure analysis.
        
        Args:
            name: Card name
            card_type: Card type line
            flavor_text: Flavor text (for context)
            is_legendary: Whether card is legendary
            
        Returns:
            Dict with narrative metrics and classifications
        """
        name_lower = name.lower()
        
        # Hero's journey stage detection
        journey_stage = self._detect_journey_stage(name_lower)
        
        # Temporal positioning
        temporal_position = self._detect_temporal_position(name_lower)
        
        # Transformation type
        transformation = self._detect_transformation(name_lower)
        
        # Agency level
        agency = self._analyze_agency(name, name_lower)
        
        # Title complexity
        title_complexity = self._analyze_title_complexity(name, is_legendary)
        
        # Narrative frame
        narrative_frame = self._detect_narrative_frame(name_lower)
        
        # Relational positioning
        relational_context = self._detect_relational_context(name_lower)
        
        # Narrative arc progression (for legendary creatures)
        arc_progression = None
        if is_legendary and ',' in name:
            arc_progression = self._analyze_arc_progression(name)
        
        # Overall narrative complexity score
        narrative_complexity = self._calculate_narrative_complexity(
            journey_stage, temporal_position, transformation,
            agency, title_complexity, narrative_frame
        )
        
        return {
            # Hero's journey
            'journey_stage': journey_stage['stage_name'],
            'journey_level': journey_stage['stage_number'],
            'narrative_weight': journey_stage['narrative_weight'],
            
            # Temporal positioning
            'temporal_position': temporal_position['primary'],
            'temporal_markers_found': temporal_position['markers'],
            'temporal_depth': temporal_position['depth'],
            
            # Transformation
            'transformation_type': transformation['type'],
            'transformation_direction': transformation['direction'],
            'transformation_valence': transformation['valence'],
            'is_transformed': transformation['is_transformed'],
            
            # Agency
            'agency_level': agency['level'],
            'agency_score': agency['score'],
            'voice_type': agency['voice'],
            
            # Title structure
            'title_complexity': title_complexity['level'],
            'title_components': title_complexity['components'],
            'has_epithet': title_complexity['has_epithet'],
            'has_comma_structure': ',' in name,
            
            # Narrative frame
            'narrative_frame': narrative_frame['primary'],
            'frame_markers': narrative_frame['markers'],
            
            # Relational context
            'relational_context': relational_context['primary'],
            'relational_markers': relational_context['markers'],
            
            # Arc progression (for legendary creatures)
            'arc_progression': arc_progression,
            
            # Summary metrics
            'overall_narrative_complexity': round(narrative_complexity, 2),
            'is_epic_framing': narrative_complexity > 70,
            'is_intimate_framing': narrative_complexity < 30,
            
            # Specific features
            'has_title_prefix': self._has_title_prefix(name_lower),
            'has_power_suffix': self._has_power_suffix(name_lower),
            'multiclause_structure': name.count(',') > 0,
        }
    
    def _detect_journey_stage(self, name_lower: str) -> Dict:
        """Detect hero's journey stage from name."""
        for stage_name, stage_data in self.heros_journey_stages.items():
            for marker in stage_data['markers']:
                if marker in name_lower:
                    return {
                        'stage_name': stage_name,
                        'stage_number': stage_data['stage'],
                        'narrative_weight': stage_data['narrative_weight'],
                        'marker_found': marker,
                    }
        
        # Default: no clear stage
        return {
            'stage_name': 'undefined',
            'stage_number': 0,
            'narrative_weight': 50,
            'marker_found': None,
        }
    
    def _detect_temporal_position(self, name_lower: str) -> Dict:
        """Detect temporal positioning in name."""
        found_markers = []
        positions = []
        
        for position, markers in self.temporal_markers.items():
            for marker in markers:
                if marker in name_lower:
                    found_markers.append(marker)
                    positions.append(position)
        
        # Temporal depth (how many temporal markers)
        depth = len(found_markers)
        
        # Primary position (if multiple, take first/most significant)
        primary = positions[0] if positions else 'present'
        
        return {
            'primary': primary,
            'markers': found_markers,
            'depth': depth,
            'is_temporally_marked': depth > 0,
        }
    
    def _detect_transformation(self, name_lower: str) -> Dict:
        """Detect transformation vocabulary."""
        for trans_type, trans_data in self.transformation_types.items():
            for marker in trans_data['markers']:
                if marker in name_lower:
                    return {
                        'type': trans_type,
                        'direction': trans_data['direction'],
                        'valence': trans_data['valence'],
                        'is_transformed': True,
                        'marker_found': marker,
                    }
        
        return {
            'type': 'none',
            'direction': 'static',
            'valence': 'neutral',
            'is_transformed': False,
            'marker_found': None,
        }
    
    def _analyze_agency(self, name: str, name_lower: str) -> Dict:
        """Analyze agency level in name."""
        # Check high agency
        high_count = 0
        for verb in self.agency_markers['high_agency']['verbs']:
            if verb in name_lower:
                high_count += 2
        for role in self.agency_markers['high_agency']['roles']:
            if role in name_lower:
                high_count += 1
        
        # Check medium agency
        medium_count = 0
        for verb in self.agency_markers['medium_agency']['verbs']:
            if verb in name_lower:
                medium_count += 2
        for role in self.agency_markers['medium_agency']['roles']:
            if role in name_lower:
                medium_count += 1
        
        # Check low agency
        low_count = 0
        for role in self.agency_markers['low_agency']['roles']:
            if role in name_lower:
                low_count += 1
        for passive in self.agency_markers['low_agency']['passive_markers']:
            if passive in name_lower:
                low_count += 2
        
        # Determine level
        if high_count > max(medium_count, low_count):
            level = 'high'
            score = 80
            voice = 'active'
        elif medium_count > max(high_count, low_count):
            level = 'medium'
            score = 50
            voice = 'active'
        elif low_count > 0:
            level = 'low'
            score = 20
            voice = 'passive'
        else:
            level = 'neutral'
            score = 50
            voice = 'neutral'
        
        return {
            'level': level,
            'score': score,
            'voice': voice,
        }
    
    def _analyze_title_complexity(self, name: str, is_legendary: bool) -> Dict:
        """Analyze title complexity."""
        components = len(name.split())
        
        # Check for comma (legendary epithet structure)
        has_comma = ',' in name
        has_epithet = has_comma
        
        # Determine complexity level
        if has_comma and components > 4:
            level = 5  # Legendary epithet
        elif has_comma:
            level = 4  # Epic clause
        elif components > 3:
            level = 3  # Double title
        elif components == 2 or components == 3:
            level = 2  # Single title
        else:
            level = 1  # Simple descriptor
        
        # Count title prefixes (Lord, Master, etc.)
        title_count = sum(1 for word in name.split() if word.lower() in [
            'lord', 'lady', 'master', 'king', 'queen', 'elder', 'ancient'
        ])
        
        return {
            'level': level,
            'components': components,
            'has_epithet': has_epithet,
            'title_prefix_count': title_count,
        }
    
    def _detect_narrative_frame(self, name_lower: str) -> Dict:
        """Detect overall narrative framing."""
        found_markers = []
        frames = []
        
        for frame, markers in self.narrative_frames.items():
            for marker in markers:
                if marker in name_lower:
                    found_markers.append(marker)
                    frames.append(frame)
        
        primary = frames[0] if frames else 'neutral'
        
        return {
            'primary': primary,
            'markers': found_markers,
            'is_framed': len(frames) > 0,
        }
    
    def _detect_relational_context(self, name_lower: str) -> Dict:
        """Detect relational/social positioning."""
        found_markers = []
        contexts = []
        
        for context, markers in self.relational_markers.items():
            for marker in markers:
                if marker in name_lower:
                    found_markers.append(marker)
                    contexts.append(context)
        
        primary = contexts[0] if contexts else 'individual'
        
        return {
            'primary': primary,
            'markers': found_markers,
            'is_relational': len(contexts) > 0,
        }
    
    def _analyze_arc_progression(self, name: str) -> Dict:
        """Analyze arc progression in legendary comma-structure names."""
        # Split by comma
        parts = [p.strip() for p in name.split(',')]
        
        if len(parts) < 2:
            return None
        
        main_name = parts[0]
        epithet = parts[1]
        
        # Check if epithet shows transformation
        epithet_lower = epithet.lower()
        
        transformation = None
        for trans_type, trans_data in self.transformation_types.items():
            if any(marker in epithet_lower for marker in trans_data['markers']):
                transformation = trans_type
                break
        
        # Check if epithet shows journey stage
        journey_stage = None
        for stage_name, stage_data in self.heros_journey_stages.items():
            if any(marker in epithet_lower for marker in stage_data['markers']):
                journey_stage = stage_name
                break
        
        return {
            'main_name': main_name,
            'epithet': epithet,
            'transformation_in_epithet': transformation,
            'journey_stage_in_epithet': journey_stage,
            'epithet_length': len(epithet.split()),
        }
    
    def _calculate_narrative_complexity(self, journey_stage: Dict, temporal_position: Dict,
                                       transformation: Dict, agency: Dict,
                                       title_complexity: Dict, narrative_frame: Dict) -> float:
        """Calculate overall narrative complexity score."""
        score = 0.0
        
        # Journey stage weight
        score += journey_stage['narrative_weight'] * 0.25
        
        # Temporal depth
        score += min(temporal_position['depth'] * 20, 30)
        
        # Transformation presence
        if transformation['is_transformed']:
            score += 20
        
        # Agency score
        score += agency['score'] * 0.15
        
        # Title complexity
        score += title_complexity['level'] * 5
        
        # Frame presence
        if narrative_frame['is_framed']:
            score += 15
        
        return min(100, score)
    
    def _has_title_prefix(self, name_lower: str) -> bool:
        """Check if name has formal title prefix."""
        titles = ['lord', 'lady', 'master', 'king', 'queen', 'elder', 'ancient',
                  'grand', 'high', 'arch', 'supreme', 'royal']
        return any(name_lower.startswith(title) for title in titles)
    
    def _has_power_suffix(self, name_lower: str) -> bool:
        """Check if name has power/dominance suffix."""
        suffixes = ['the great', 'the mighty', 'the powerful', 'the terrible',
                   'the destroyer', 'the conqueror', 'the eternal']
        return any(suffix in name_lower for suffix in suffixes)

