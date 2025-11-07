"""Immigration Surname Semantic Classifier

Classifies surnames by their SEMANTIC MEANING in original language, not geographic pattern.

PRIMARY RESEARCH QUESTION:
Do toponymic surnames (place-meaning names like Galilei, Romano, Berliner) show different
US immigration rates and settlement patterns than occupational (Smith, Baker), descriptive 
(Brown, Long), or patronymic (Johnson, O'Brien) surnames?

SEMANTIC CATEGORIES:
1. **Toponymic** - Place/geographic meaning
   - Examples: Galilei (from Galilee), Romano (from Rome), Berliner (from Berlin), 
     London, Paris, Veneziano (Venetian), Napolitano (from Naples)
   
2. **Occupational** - Job/trade meaning
   - Examples: Smith, Baker, Shoemaker, Fischer (fisher), Mueller (miller), 
     Schneider (tailor), Ferrari (blacksmith)

3. **Descriptive** - Physical/character traits
   - Examples: Brown, Long, Short, Klein (small), Gross (big), Rossi (red-haired),
     Bianchi (white), Nero (black)

4. **Patronymic** - Father's name
   - Examples: Johnson (John's son), O'Brien (descendant of Brian), 
     Ivanov (son of Ivan), Martinez (son of Martin)

5. **Religious** - Religious meaning
   - Examples: Christian, Bishop, Pope, Santo, Chiesa (church), Temple

6. **Nature/Animal** - Natural elements
   - Examples: Wolf, Fox, Rivers, Stone, Berg (mountain)

Author: Michael Smerconish
Date: November 2025
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class ImmigrationSurnameClassifier:
    """Etymology-based classifier for surname semantic meaning analysis."""
    
    # Version for tracking classification changes
    VERSION = "2.0"
    
    # Comprehensive etymology database by semantic category
    
    TOPONYMIC_SURNAMES = {
        # Italian toponymic (place-based)
        'Romano': {'meaning': 'from Rome', 'place': 'Rome', 'place_country': 'Italy', 'place_type': 'city', 'importance': 95},
        'Veneziano': {'meaning': 'from Venice', 'place': 'Venice', 'place_country': 'Italy', 'place_type': 'city', 'importance': 90},
        'Napolitano': {'meaning': 'from Naples', 'place': 'Naples', 'place_country': 'Italy', 'place_type': 'city', 'importance': 85},
        'Fiorentino': {'meaning': 'from Florence', 'place': 'Florence', 'place_country': 'Italy', 'place_type': 'city', 'importance': 90},
        'Milanese': {'meaning': 'from Milan', 'place': 'Milan', 'place_country': 'Italy', 'place_type': 'city', 'importance': 85},
        'Genovese': {'meaning': 'from Genoa', 'place': 'Genoa', 'place_country': 'Italy', 'place_type': 'city', 'importance': 80},
        'Siciliano': {'meaning': 'from Sicily', 'place': 'Sicily', 'place_country': 'Italy', 'place_type': 'region', 'importance': 85},
        'Calabrese': {'meaning': 'from Calabria', 'place': 'Calabria', 'place_country': 'Italy', 'place_type': 'region', 'importance': 75},
        'Toscano': {'meaning': 'from Tuscany', 'place': 'Tuscany', 'place_country': 'Italy', 'place_type': 'region', 'importance': 85},
        'Galilei': {'meaning': 'from Galilee', 'place': 'Galilee', 'place_country': 'Israel', 'place_type': 'region', 'importance': 90},
        
        # German toponymic
        'Berliner': {'meaning': 'from Berlin', 'place': 'Berlin', 'place_country': 'Germany', 'place_type': 'city', 'importance': 95},
        'Hamburger': {'meaning': 'from Hamburg', 'place': 'Hamburg', 'place_country': 'Germany', 'place_type': 'city', 'importance': 80},
        'Frankfurter': {'meaning': 'from Frankfurt', 'place': 'Frankfurt', 'place_country': 'Germany', 'place_type': 'city', 'importance': 85},
        'Wiener': {'meaning': 'from Vienna', 'place': 'Vienna', 'place_country': 'Austria', 'place_type': 'city', 'importance': 90},
        'Breslauer': {'meaning': 'from Breslau', 'place': 'Breslau/Wrocław', 'place_country': 'Poland', 'place_type': 'city', 'importance': 75},
        
        # English toponymic
        'London': {'meaning': 'from London', 'place': 'London', 'place_country': 'England', 'place_type': 'city', 'importance': 100},
        'York': {'meaning': 'from York', 'place': 'York', 'place_country': 'England', 'place_type': 'city', 'importance': 85},
        'Lancaster': {'meaning': 'from Lancaster', 'place': 'Lancaster', 'place_country': 'England', 'place_type': 'city', 'importance': 75},
        'Bristol': {'meaning': 'from Bristol', 'place': 'Bristol', 'place_country': 'England', 'place_type': 'city', 'importance': 75},
        
        # French toponymic
        'Paris': {'meaning': 'from Paris', 'place': 'Paris', 'place_country': 'France', 'place_type': 'city', 'importance': 100},
        'Lyon': {'meaning': 'from Lyon', 'place': 'Lyon', 'place_country': 'France', 'place_type': 'city', 'importance': 80},
        'Marseille': {'meaning': 'from Marseille', 'place': 'Marseille', 'place_country': 'France', 'place_type': 'city', 'importance': 80},
        'Normandy': {'meaning': 'from Normandy', 'place': 'Normandy', 'place_country': 'France', 'place_type': 'region', 'importance': 85},
        
        # Spanish toponymic
        'Toledo': {'meaning': 'from Toledo', 'place': 'Toledo', 'place_country': 'Spain', 'place_type': 'city', 'importance': 85},
        'Cordoba': {'meaning': 'from Córdoba', 'place': 'Córdoba', 'place_country': 'Spain', 'place_type': 'city', 'importance': 80},
        'Sevilla': {'meaning': 'from Seville', 'place': 'Seville', 'place_country': 'Spain', 'place_type': 'city', 'importance': 85},
        'Valencia': {'meaning': 'from Valencia', 'place': 'Valencia', 'place_country': 'Spain', 'place_type': 'city', 'importance': 80},
        
        # Polish toponymic
        'Warszawski': {'meaning': 'from Warsaw', 'place': 'Warsaw', 'place_country': 'Poland', 'place_type': 'city', 'importance': 95},
        'Krakowski': {'meaning': 'from Kraków', 'place': 'Kraków', 'place_country': 'Poland', 'place_type': 'city', 'importance': 85},
    }
    
    OCCUPATIONAL_SURNAMES = {
        # English occupational
        'Smith': {'meaning': 'metalworker, blacksmith', 'occupation': 'metalworking'},
        'Baker': {'meaning': 'bread maker', 'occupation': 'baking'},
        'Miller': {'meaning': 'grain miller', 'occupation': 'milling'},
        'Taylor': {'meaning': 'tailor, clothes maker', 'occupation': 'tailoring'},
        'Cook': {'meaning': 'cook, chef', 'occupation': 'cooking'},
        'Carpenter': {'meaning': 'woodworker', 'occupation': 'carpentry'},
        'Mason': {'meaning': 'stone worker', 'occupation': 'masonry'},
        'Shoemaker': {'meaning': 'cobbler, shoe maker', 'occupation': 'shoemaking'},
        'Fisher': {'meaning': 'fisherman', 'occupation': 'fishing'},
        'Cooper': {'meaning': 'barrel maker', 'occupation': 'cooperage'},
        
        # German occupational
        'Mueller': {'meaning': 'miller (German)', 'occupation': 'milling'},
        'Schmidt': {'meaning': 'smith (German)', 'occupation': 'metalworking'},
        'Schneider': {'meaning': 'tailor (German)', 'occupation': 'tailoring'},
        'Fischer': {'meaning': 'fisher (German)', 'occupation': 'fishing'},
        'Weber': {'meaning': 'weaver (German)', 'occupation': 'weaving'},
        'Wagner': {'meaning': 'wagon maker (German)', 'occupation': 'wagon making'},
        'Becker': {'meaning': 'baker (German)', 'occupation': 'baking'},
        'Zimmermann': {'meaning': 'carpenter (German)', 'occupation': 'carpentry'},
        
        # Italian occupational
        'Ferrari': {'meaning': 'blacksmith (Italian)', 'occupation': 'metalworking'},
        'Fabbri': {'meaning': 'smith (Italian)', 'occupation': 'metalworking'},
        'Barbieri': {'meaning': 'barber (Italian)', 'occupation': 'barbering'},
        'Sartori': {'meaning': 'tailor (Italian)', 'occupation': 'tailoring'},
        'Molinari': {'meaning': 'miller (Italian)', 'occupation': 'milling'},
        'Pesci': {'meaning': 'fisherman (Italian)', 'occupation': 'fishing'},
        
        # French occupational
        'Lefevre': {'meaning': 'smith (French)', 'occupation': 'metalworking'},
        'Boucher': {'meaning': 'butcher (French)', 'occupation': 'butchering'},
        'Boulanger': {'meaning': 'baker (French)', 'occupation': 'baking'},
        'Charpentier': {'meaning': 'carpenter (French)', 'occupation': 'carpentry'},
        'Mercier': {'meaning': 'merchant (French)', 'occupation': 'trade'},
        
        # Spanish occupational
        'Herrero': {'meaning': 'blacksmith (Spanish)', 'occupation': 'metalworking'},
        'Molina': {'meaning': 'mill worker (Spanish)', 'occupation': 'milling'},
        'Guerrero': {'meaning': 'warrior (Spanish)', 'occupation': 'military'},
    }
    
    DESCRIPTIVE_SURNAMES = {
        # Color/appearance
        'Brown': {'meaning': 'brown-haired/dark-complexioned', 'trait': 'appearance'},
        'White': {'meaning': 'fair-haired/light-complexioned', 'trait': 'appearance'},
        'Black': {'meaning': 'dark-haired/dark-complexioned', 'trait': 'appearance'},
        'Gray': {'meaning': 'gray-haired', 'trait': 'appearance'},
        'Rossi': {'meaning': 'red-haired (Italian)', 'trait': 'appearance'},
        'Bianchi': {'meaning': 'white/fair (Italian)', 'trait': 'appearance'},
        'Nero': {'meaning': 'black/dark (Italian)', 'trait': 'appearance'},
        'Russo': {'meaning': 'red-haired (Italian)', 'trait': 'appearance'},
        
        # Size/stature
        'Long': {'meaning': 'tall', 'trait': 'stature'},
        'Short': {'meaning': 'short', 'trait': 'stature'},
        'Little': {'meaning': 'small', 'trait': 'stature'},
        'Gross': {'meaning': 'large/big (German)', 'trait': 'stature'},
        'Klein': {'meaning': 'small (German)', 'trait': 'stature'},
        'Grande': {'meaning': 'large (Italian)', 'trait': 'stature'},
        'Piccolo': {'meaning': 'small (Italian)', 'trait': 'stature'},
        'Petit': {'meaning': 'small (French)', 'trait': 'stature'},
        'Legrand': {'meaning': 'the large (French)', 'trait': 'stature'},
        
        # Other traits
        'Young': {'meaning': 'young', 'trait': 'age'},
        'Old': {'meaning': 'old', 'trait': 'age'},
        'Strong': {'meaning': 'strong', 'trait': 'character'},
        'Wise': {'meaning': 'wise', 'trait': 'character'},
    }
    
    PATRONYMIC_SURNAMES = {
        # English patronymic
        'Johnson': {'meaning': "son of John", 'father_name': 'John'},
        'Williams': {'meaning': "son of William", 'father_name': 'William'},
        'Jackson': {'meaning': "son of Jack", 'father_name': 'Jack'},
        'Anderson': {'meaning': "son of Andrew", 'father_name': 'Andrew'},
        'Thompson': {'meaning': "son of Thomas", 'father_name': 'Thomas'},
        'Peterson': {'meaning': "son of Peter", 'father_name': 'Peter'},
        
        # Spanish patronymic
        'Martinez': {'meaning': "son of Martin", 'father_name': 'Martin'},
        'Rodriguez': {'meaning': "son of Rodrigo", 'father_name': 'Rodrigo'},
        'Hernandez': {'meaning': "son of Hernando", 'father_name': 'Hernando'},
        'Lopez': {'meaning': "son of Lope", 'father_name': 'Lope'},
        'Gonzalez': {'meaning': "son of Gonzalo", 'father_name': 'Gonzalo'},
        
        # Russian patronymic
        'Ivanov': {'meaning': "son of Ivan", 'father_name': 'Ivan'},
        'Petrov': {'meaning': "son of Peter", 'father_name': 'Peter'},
        'Sidorov': {'meaning': "son of Sidor", 'father_name': 'Sidor'},
        'Sokolov': {'meaning': "son of Sokol", 'father_name': 'Sokol'},
        
        # Irish patronymic
        "O'Brien": {'meaning': "descendant of Brian", 'father_name': 'Brian'},
        "O'Connor": {'meaning': "descendant of Connor", 'father_name': 'Connor'},
        "O'Sullivan": {'meaning': "descendant of Sullivan", 'father_name': 'Sullivan'},
        'McCarthy': {'meaning': "son of Cárthach", 'father_name': 'Cárthach'},
        'Murphy': {'meaning': "descendant of Murchadh", 'father_name': 'Murchadh'},
    }
    
    RELIGIOUS_SURNAMES = {
        'Christian': {'meaning': 'follower of Christ', 'religious_reference': 'Christianity'},
        'Bishop': {'meaning': 'bishop (church official)', 'religious_reference': 'Christianity'},
        'Pope': {'meaning': 'pope', 'religious_reference': 'Christianity'},
        'Priest': {'meaning': 'priest', 'religious_reference': 'Christianity'},
        'Church': {'meaning': 'church', 'religious_reference': 'Christianity'},
        'Temple': {'meaning': 'temple', 'religious_reference': 'general'},
        'Santo': {'meaning': 'saint (Italian/Spanish)', 'religious_reference': 'Christianity'},
        'Chiesa': {'meaning': 'church (Italian)', 'religious_reference': 'Christianity'},
        'Cohen': {'meaning': 'priest (Jewish)', 'religious_reference': 'Judaism'},
        'Levy': {'meaning': 'Levite (Jewish)', 'religious_reference': 'Judaism'},
    }
    
    def __init__(self):
        """Initialize classifier with etymology databases."""
        logger.info(f"Initializing Immigration Surname Semantic Classifier v{self.VERSION}")
        self.classified_cache = {}
        
    def classify_surname(self, surname: str, additional_context: Optional[Dict] = None) -> Dict:
        """Classify a surname by its SEMANTIC MEANING in original language.
        
        Args:
            surname: The surname to classify
            additional_context: Optional context (known origin, etc.)
            
        Returns:
            Classification results including semantic category and meaning
        """
        if not surname or not isinstance(surname, str):
            return self._error_result("Invalid surname")
        
        surname = surname.strip().title()
        
        # Check cache
        if surname in self.classified_cache:
            return self.classified_cache[surname]
        
        logger.info(f"Classifying surname: {surname}")
        
        results = {
            'surname': surname,
            'semantic_category': None,
            'is_toponymic': False,
            'meaning_in_original': None,
            'confidence_score': 0.0,
            'classification_method': 'etymology_database',
            'classifier_version': self.VERSION,
            'etymology_features': {},
            'place_info': None
        }
        
        # Check each semantic category
        
        # 1. Check TOPONYMIC (highest priority for this research)
        if surname in self.TOPONYMIC_SURNAMES:
            info = self.TOPONYMIC_SURNAMES[surname]
            results.update({
                'semantic_category': 'toponymic',
                'is_toponymic': True,
                'meaning_in_original': info['meaning'],
                'confidence_score': 95.0,
                'place_info': {
                    'place_name': info['place'],
                    'place_country': info['place_country'],
                    'place_type': info['place_type'],
                    'place_importance': info['importance']
                },
                'etymology_features': {
                    'category': 'toponymic',
                    'evidence': f"Known place-based surname meaning '{info['meaning']}'",
                    'place_reference': info['place']
                }
            })
            self.classified_cache[surname] = results
            return results
        
        # 2. Check OCCUPATIONAL
        if surname in self.OCCUPATIONAL_SURNAMES:
            info = self.OCCUPATIONAL_SURNAMES[surname]
            results.update({
                'semantic_category': 'occupational',
                'is_toponymic': False,
                'meaning_in_original': info['meaning'],
                'confidence_score': 95.0,
                'etymology_features': {
                    'category': 'occupational',
                    'occupation': info['occupation'],
                    'evidence': f"Known occupational surname meaning '{info['meaning']}'"
                }
            })
            self.classified_cache[surname] = results
            return results
        
        # 3. Check DESCRIPTIVE
        if surname in self.DESCRIPTIVE_SURNAMES:
            info = self.DESCRIPTIVE_SURNAMES[surname]
            results.update({
                'semantic_category': 'descriptive',
                'is_toponymic': False,
                'meaning_in_original': info['meaning'],
                'confidence_score': 95.0,
                'etymology_features': {
                    'category': 'descriptive',
                    'trait_type': info['trait'],
                    'evidence': f"Known descriptive surname meaning '{info['meaning']}'"
                }
            })
            self.classified_cache[surname] = results
            return results
        
        # 4. Check PATRONYMIC
        if surname in self.PATRONYMIC_SURNAMES:
            info = self.PATRONYMIC_SURNAMES[surname]
            results.update({
                'semantic_category': 'patronymic',
                'is_toponymic': False,
                'meaning_in_original': info['meaning'],
                'confidence_score': 95.0,
                'etymology_features': {
                    'category': 'patronymic',
                    'father_name': info['father_name'],
                    'evidence': f"Known patronymic surname meaning '{info['meaning']}'"
                }
            })
            self.classified_cache[surname] = results
            return results
        
        # 5. Check RELIGIOUS
        if surname in self.RELIGIOUS_SURNAMES:
            info = self.RELIGIOUS_SURNAMES[surname]
            results.update({
                'semantic_category': 'religious',
                'is_toponymic': False,
                'meaning_in_original': info['meaning'],
                'confidence_score': 95.0,
                'etymology_features': {
                    'category': 'religious',
                    'religious_reference': info['religious_reference'],
                    'evidence': f"Known religious surname meaning '{info['meaning']}'"
                }
            })
            self.classified_cache[surname] = results
            return results
        
        # 6. Pattern-based classification (fallback)
        pattern_result = self._classify_by_pattern(surname)
        if pattern_result:
            results.update(pattern_result)
            self.classified_cache[surname] = results
            return results
        
        # 7. Unknown - default to descriptive with low confidence
        results.update({
            'semantic_category': 'unknown',
            'is_toponymic': False,
            'meaning_in_original': 'Unknown etymology',
            'confidence_score': 20.0,
            'etymology_features': {
                'category': 'unknown',
                'evidence': 'Not in etymology database, pattern matching failed'
            }
        })
        
        self.classified_cache[surname] = results
        return results
    
    def _classify_by_pattern(self, surname: str) -> Optional[Dict]:
        """Classify by linguistic patterns when not in database.
        
        Args:
            surname: The surname
            
        Returns:
            Classification dict or None
        """
        surname_lower = surname.lower()
        
        # Patronymic patterns
        if surname.endswith('son'):
            return {
                'semantic_category': 'patronymic',
                'is_toponymic': False,
                'meaning_in_original': f"son of {surname[:-3]}",
                'confidence_score': 70.0,
                'etymology_features': {
                    'category': 'patronymic',
                    'pattern': '-son suffix',
                    'evidence': 'English/Scandinavian patronymic pattern'
                }
            }
        
        if surname.endswith('ez') or surname.endswith('az') or surname.endswith('iz'):
            return {
                'semantic_category': 'patronymic',
                'is_toponymic': False,
                'meaning_in_original': f"son of {surname[:-2]}",
                'confidence_score': 70.0,
                'etymology_features': {
                    'category': 'patronymic',
                    'pattern': '-ez/-az/-iz suffix',
                    'evidence': 'Spanish patronymic pattern'
                }
            }
        
        if surname.endswith('ov') or surname.endswith('ev'):
            return {
                'semantic_category': 'patronymic',
                'is_toponymic': False,
                'meaning_in_original': f"son of {surname[:-2]}",
                'confidence_score': 70.0,
                'etymology_features': {
                    'category': 'patronymic',
                    'pattern': '-ov/-ev suffix',
                    'evidence': 'Russian patronymic pattern'
                }
            }
        
        if surname.startswith("O'") or surname.startswith('Mc') or surname.startswith('Mac'):
            return {
                'semantic_category': 'patronymic',
                'is_toponymic': False,
                'meaning_in_original': f"descendant of {surname[2:] if surname.startswith(\"O'\") else surname[2:]}",
                'confidence_score': 75.0,
                'etymology_features': {
                    'category': 'patronymic',
                    'pattern': "O'/Mc/Mac prefix",
                    'evidence': 'Irish/Scottish patronymic pattern'
                }
            }
        
        # Toponymic patterns (city/region suffixes)
        if surname_lower.endswith('ano') or surname_lower.endswith('ese'):
            # Italian place-based pattern
            return {
                'semantic_category': 'toponymic',
                'is_toponymic': True,
                'meaning_in_original': f"from {surname[:-3] if surname_lower.endswith('ano') else surname[:-3]}",
                'confidence_score': 60.0,
                'etymology_features': {
                    'category': 'toponymic',
                    'pattern': '-ano/-ese suffix',
                    'evidence': 'Italian toponymic pattern (likely place-based)'
                }
            }
        
        if surname_lower.endswith('er') and surname_lower != 'baker' and surname_lower != 'fisher':
            # German toponymic pattern (Berliner, Frankfurter)
            # But need to exclude occupational -er endings
            if len(surname) > 6:  # Avoid short names
                return {
                    'semantic_category': 'toponymic',
                    'is_toponymic': True,
                    'meaning_in_original': f"from {surname[:-2]}",
                    'confidence_score': 50.0,
                    'etymology_features': {
                        'category': 'toponymic',
                        'pattern': '-er suffix (German)',
                        'evidence': 'Possible German toponymic pattern'
                    }
                }
        
        return None
    
    def _error_result(self, message: str) -> Dict:
        """Return error result."""
        return {
            'error': message,
            'classifier_version': self.VERSION
        }
    
    def batch_classify(self, surnames: List[str]) -> List[Dict]:
        """Classify multiple surnames efficiently."""
        results = []
        total = len(surnames)
        
        for i, surname in enumerate(surnames):
            if (i + 1) % 100 == 0:
                logger.info(f"Classified {i + 1}/{total} surnames...")
            
            result = self.classify_surname(surname)
            results.append(result)
        
        logger.info(f"Batch classification complete: {total} surnames")
        return results
    
    def get_classification_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from classification results."""
        if not results:
            return {'error': 'No results to summarize'}
        
        toponymic = [r for r in results if r.get('is_toponymic', False)]
        
        # Count by category
        category_counts = Counter(r.get('semantic_category') for r in results if r.get('semantic_category'))
        
        summary = {
            'total_surnames': len(results),
            'toponymic_count': len(toponymic),
            'toponymic_percentage': round(len(toponymic) / len(results) * 100, 2),
            'category_distribution': dict(category_counts),
            'mean_confidence': round(sum(r.get('confidence_score', 0) for r in results) / len(results), 2)
        }
        
        return summary
