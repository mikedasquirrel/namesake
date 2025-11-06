"""MTG Intertextual Reference Analyzer

Analyzes mythological, literary, and historical references in MTG card names.

Quantifies cultural sophistication by detecting:
- Mythological references (Greek, Norse, Egyptian, Japanese, etc.)
- Literary allusions (Shakespeare, epic poetry, folklore)
- Historical figures and events
- Biblical/religious terminology
- Reference obscurity (common vs esoteric)
"""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class MTGIntertextualAnalyzer:
    """Analyzes intertextual references and cultural depth in card names."""
    
    def __init__(self):
        # Mythological reference database
        self.mythological_references = {
            'greek': {
                'deities': ['zeus', 'hera', 'athena', 'apollo', 'artemis', 'poseidon',
                          'hades', 'demeter', 'dionysus', 'aphrodite', 'ares', 'hermes'],
                'heroes': ['hercules', 'heracles', 'perseus', 'theseus', 'achilles',
                         'odysseus', 'jason', 'orpheus'],
                'creatures': ['hydra', 'chimera', 'sphinx', 'minotaur', 'medusa',
                           'cerberus', 'pegasus', 'phoenix', 'griffin'],
                'concepts': ['olympus', 'tartarus', 'elysium', 'styx', 'muse',
                           'titan', 'olympian', 'oracle'],
                'obscurity': 'low',  # Well-known
            },
            'norse': {
                'deities': ['odin', 'thor', 'loki', 'freya', 'frigg', 'heimdall',
                          'tyr', 'balder', 'hel'],
                'heroes': ['sigurd', 'beowulf', 'ragnar'],
                'creatures': ['fenrir', 'jormungandr', 'sleipnir', 'valkyrie', 'draugr'],
                'concepts': ['valhalla', 'ragnarok', 'yggdrasil', 'asgard', 'midgard',
                           'bifrost', 'rune', 'heim'],
                'obscurity': 'medium',
            },
            'egyptian': {
                'deities': ['ra', 'osiris', 'isis', 'anubis', 'horus', 'set', 'thoth',
                          'bastet', 'sekhmet', 'ptah'],
                'concepts': ['pharaoh', 'pyramid', 'sphinx', 'scarab', 'ankh',
                           'obelisk', 'necropolis'],
                'obscurity': 'medium',
            },
            'japanese': {
                'deities': ['amaterasu', 'susanoo', 'tsukuyomi', 'inari', 'izanagi',
                          'izanami'],
                'creatures': ['kitsune', 'tanuki', 'tengu', 'kappa', 'oni', 'dragon',
                            'kirin', 'phoenix'],
                'concepts': ['kami', 'yokai', 'shogun', 'samurai', 'ronin', 'daimyo',
                           'shrine', 'temple'],
                'obscurity': 'medium',
            },
            'celtic': {
                'deities': ['dagda', 'morrigan', 'lugh', 'brigid', 'cernunnos'],
                'heroes': ['cu chulainn', 'finn'],
                'creatures': ['banshee', 'kelpie', 'selkie'],
                'concepts': ['druid', 'bard', 'tuatha', 'sidhe', 'avalon'],
                'obscurity': 'high',
            },
            'mesopotamian': {
                'deities': ['marduk', 'ishtar', 'enlil', 'enki', 'tiamat'],
                'creatures': ['lamassu', 'pazuzu'],
                'concepts': ['ziggurat', 'babylon'],
                'obscurity': 'high',
            },
            'hindu': {
                'deities': ['brahma', 'vishnu', 'shiva', 'krishna', 'kali', 'ganesh'],
                'creatures': ['garuda', 'naga'],
                'concepts': ['avatar', 'asura', 'deva', 'rakshasa', 'maya'],
                'obscurity': 'medium',
            },
        }
        
        # Literary references
        self.literary_references = {
            'shakespeare': {
                'characters': ['hamlet', 'ophelia', 'macbeth', 'othello', 'prospero',
                             'ariel', 'puck', 'titania', 'oberon'],
                'plays': ['tempest', 'midsummer'],
                'quotes': ['sound', 'fury', 'dagger'],
                'obscurity': 'low',
            },
            'epic_poetry': {
                'works': ['odyssey', 'iliad', 'aeneid', 'beowulf', 'gilgamesh',
                        'paradise', 'inferno'],
                'characters': ['dante', 'virgil', 'achilles', 'hector'],
                'obscurity': 'medium',
            },
            'arthurian': {
                'characters': ['arthur', 'merlin', 'lancelot', 'guinevere', 'mordred',
                             'galahad', 'percival'],
                'concepts': ['excalibur', 'grail', 'camelot', 'avalon', 'round table'],
                'obscurity': 'low',
            },
            'folklore': {
                'creatures': ['troll', 'goblin', 'fairy', 'elf', 'dwarf', 'giant',
                            'witch', 'wizard'],
                'concepts': ['enchantment', 'curse', 'blessing', 'spell'],
                'obscurity': 'low',
            },
        }
        
        # Historical references
        self.historical_references = {
            'ancient_rome': {
                'figures': ['caesar', 'augustus', 'nero', 'cicero', 'brutus'],
                'concepts': ['senate', 'legion', 'consul', 'emperor', 'gladiator'],
                'obscurity': 'medium',
            },
            'medieval': {
                'titles': ['knight', 'lord', 'baron', 'duke', 'count', 'king', 'queen'],
                'concepts': ['crusade', 'castle', 'siege', 'tournament'],
                'obscurity': 'low',
            },
        }
        
        # Biblical/religious references
        self.biblical_references = {
            'figures': ['angel', 'demon', 'seraph', 'cherub', 'archangel', 'gabriel',
                       'michael', 'lucifer', 'solomon', 'samson'],
            'concepts': ['apocalypse', 'revelation', 'genesis', 'exodus', 'deluge',
                        'covenant', 'testament', 'prophet'],
            'obscurity': 'low',
        }
        
        # Compile all references for quick lookup
        self._compile_reference_index()
    
    def _compile_reference_index(self):
        """Compile searchable index of all references."""
        self.reference_index = {}
        
        # Mythological
        for culture, data in self.mythological_references.items():
            for category, terms in data.items():
                if category == 'obscurity':
                    continue
                for term in terms:
                    self.reference_index[term] = {
                        'type': 'mythological',
                        'culture': culture,
                        'category': category,
                        'obscurity': data['obscurity'],
                    }
        
        # Literary
        for source, data in self.literary_references.items():
            for category, terms in data.items():
                if category == 'obscurity':
                    continue
                for term in terms:
                    self.reference_index[term] = {
                        'type': 'literary',
                        'source': source,
                        'category': category,
                        'obscurity': data['obscurity'],
                    }
        
        # Historical
        for period, data in self.historical_references.items():
            for category, terms in data.items():
                if category == 'obscurity':
                    continue
                for term in terms:
                    self.reference_index[term] = {
                        'type': 'historical',
                        'period': period,
                        'category': category,
                        'obscurity': data.get('obscurity', 'medium'),
                    }
        
        # Biblical
        for term in self.biblical_references['figures'] + self.biblical_references['concepts']:
            self.reference_index[term] = {
                'type': 'biblical',
                'category': 'religious',
                'obscurity': self.biblical_references['obscurity'],
            }
    
    def analyze_intertextual_references(self, name: str, flavor_text: str = None) -> Dict:
        """Comprehensive intertextual reference analysis.
        
        Args:
            name: Card name
            flavor_text: Flavor text (for additional context)
            
        Returns:
            Dict with reference detection and sophistication metrics
        """
        name_lower = name.lower()
        flavor_lower = flavor_text.lower() if flavor_text else ''
        
        # Detect references in name
        name_references = self._detect_references(name_lower)
        
        # Detect references in flavor text
        flavor_references = self._detect_references(flavor_lower) if flavor_text else []
        
        # Combined analysis
        all_references = name_references + flavor_references
        
        # Reference categories
        mythological = [r for r in all_references if r['type'] == 'mythological']
        literary = [r for r in all_references if r['type'] == 'literary']
        historical = [r for r in all_references if r['type'] == 'historical']
        biblical = [r for r in all_references if r['type'] == 'biblical']
        
        # Cultural breadth (how many different cultures/sources)
        cultures = set()
        for ref in all_references:
            if ref['type'] == 'mythological':
                cultures.add(ref['culture'])
            elif ref['type'] == 'literary':
                cultures.add(ref['source'])
            elif ref['type'] == 'historical':
                cultures.add(ref['period'])
            elif ref['type'] == 'biblical':
                cultures.add('biblical')
        
        cultural_breadth = len(cultures)
        
        # Reference obscurity score (higher = more esoteric)
        obscurity_scores = {'low': 20, 'medium': 50, 'high': 80}
        avg_obscurity = 0.0
        if all_references:
            obscurity_sum = sum(obscurity_scores[r['obscurity']] for r in all_references)
            avg_obscurity = obscurity_sum / len(all_references)
        
        # Calculate overall sophistication
        sophistication = self._calculate_sophistication(
            name_references, all_references, cultural_breadth, avg_obscurity
        )
        
        return {
            # References found in name
            'name_references': name_references,
            'name_reference_count': len(name_references),
            
            # All references (name + flavor)
            'total_references': all_references,
            'total_reference_count': len(all_references),
            
            # By category
            'mythological_references': mythological,
            'literary_references': literary,
            'historical_references': historical,
            'biblical_references': biblical,
            
            # Metrics
            'cultural_breadth': cultural_breadth,
            'avg_obscurity_score': round(avg_obscurity, 2),
            'intertextual_sophistication': round(sophistication, 2),
            
            # Classifications
            'has_mythological': len(mythological) > 0,
            'has_literary': len(literary) > 0,
            'has_historical': len(historical) > 0,
            'has_biblical': len(biblical) > 0,
            'is_culturally_rich': cultural_breadth >= 2,
            'is_obscure': avg_obscurity > 60,
            
            # Dominant reference type
            'dominant_reference_type': self._get_dominant_type(all_references),
        }
    
    def _detect_references(self, text: str) -> List[Dict]:
        """Detect all references in given text."""
        references = []
        
        for term, data in self.reference_index.items():
            if term in text:
                references.append({
                    'term': term,
                    **data
                })
        
        return references
    
    def _calculate_sophistication(self, name_refs: List, all_refs: List,
                                  breadth: int, obscurity: float) -> float:
        """Calculate overall intertextual sophistication."""
        score = 0.0
        
        # Name references (weighted higher than flavor)
        score += min(len(name_refs) * 30, 60)
        
        # Cultural breadth
        score += min(breadth * 15, 45)
        
        # Obscurity bonus (esoteric references = more sophisticated)
        score += (obscurity / 100) * 30
        
        # Multiple reference types
        types = set(r['type'] for r in all_refs)
        if len(types) > 1:
            score += 20
        
        return min(100, score)
    
    def _get_dominant_type(self, references: List[Dict]) -> str:
        """Get dominant reference type."""
        if not references:
            return 'none'
        
        type_counts = {}
        for ref in references:
            ref_type = ref['type']
            type_counts[ref_type] = type_counts.get(ref_type, 0) + 1
        
        return max(type_counts, key=type_counts.get)

