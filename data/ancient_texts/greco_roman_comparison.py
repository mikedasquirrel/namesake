"""
Ancient Greco-Roman Text Comparison Dataset
============================================

Critical for validating ensemble methodology with texts of KNOWN truth-status.

Ancient Historians (KNOWN DOCUMENTARY):
- Josephus, Thucydides, Herodotus, Polybius, Livy, Tacitus, etc.
- Truth-status: Documentary (some events archaeologically verified)
- Expected pattern: High variance, low optimization

Ancient Literary/Epic (KNOWN FICTION):
- Homer, Virgil, Ovid, Greek tragedies, etc.
- Truth-status: Epic/mythological poetry
- Expected pattern: Low variance, high optimization

This provides GROUND TRUTH for calibration.
If methodology works, should discriminate these known cases.
"""

import json
from typing import Dict, List
from pathlib import Path


class GrecoRomanComparisonDatabase:
    """Ancient texts with known truth-status for methodology validation."""
    
    def __init__(self):
        self.texts = self._build_database()
    
    def _build_database(self) -> Dict:
        """Build complete ancient text database."""
        
        return {
            'ancient_historians': self._ancient_historians(),
            'ancient_literary': self._ancient_literary(),
            'ancient_biography': self._ancient_biography()
        }
    
    def _ancient_historians(self) -> List[Dict]:
        """
        Ancient historical texts with documentary claims.
        Many events independently verified by archaeology/other sources.
        """
        return [
            {
                'title': 'Jewish Antiquities',
                'author': 'Josephus',
                'year': 94,
                'language': 'Greek',
                'genre': 'history',
                'truth_claim': 'documentary',
                'external_verification': 'High - many events confirmed by archaeology',
                'characters': [
                    {'name': 'Herod', 'role': 'antagonist', 'real': True},
                    {'name': 'Pontius Pilate', 'role': 'antagonist', 'real': True},
                    {'name': 'Caiaphas', 'role': 'antagonist', 'real': True},
                    {'name': 'John the Baptist', 'role': 'protagonist', 'real': True},
                    {'name': 'Vespasian', 'role': 'protagonist', 'real': True},
                    {'name': 'Titus', 'role': 'protagonist', 'real': True},
                ],
                'notes': 'Jewish historian, contemporary source for 1st century'
            },
            {
                'title': 'The Peloponnesian War',
                'author': 'Thucydides',
                'year': -400,
                'language': 'Greek',
                'genre': 'history',
                'truth_claim': 'documentary',
                'external_verification': 'High - Father of historical method',
                'characters': [
                    {'name': 'Pericles', 'role': 'protagonist', 'real': True},
                    {'name': 'Alcibiades', 'role': 'complex', 'real': True},
                    {'name': 'Nicias', 'role': 'protagonist', 'real': True},
                    {'name': 'Cleon', 'role': 'antagonist', 'real': True},
                    {'name': 'Brasidas', 'role': 'antagonist', 'real': True},
                    {'name': 'Lysander', 'role': 'antagonist', 'real': True},
                ],
                'notes': 'Eyewitness account of war, rigorous methodology'
            },
            {
                'title': 'Histories',
                'author': 'Herodotus',
                'year': -430,
                'language': 'Greek',
                'genre': 'history',
                'truth_claim': 'documentary',
                'external_verification': 'Medium - some legendary material mixed in',
                'characters': [
                    {'name': 'Croesus', 'role': 'protagonist', 'real': True},
                    {'name': 'Cyrus', 'role': 'protagonist', 'real': True},
                    {'name': 'Darius', 'role': 'protagonist', 'real': True},
                    {'name': 'Xerxes', 'role': 'antagonist', 'real': True},
                    {'name': 'Leonidas', 'role': 'protagonist', 'real': True},
                    {'name': 'Themistocles', 'role': 'protagonist', 'real': True},
                ],
                'notes': 'Father of history, travels and investigations'
            },
            {
                'title': 'Histories',
                'author': 'Polybius',
                'year': -140,
                'language': 'Greek',
                'genre': 'history',
                'truth_claim': 'documentary',
                'external_verification': 'High - pragmatic historian',
                'characters': [
                    {'name': 'Scipio Africanus', 'role': 'protagonist', 'real': True},
                    {'name': 'Hannibal', 'role': 'antagonist', 'real': True},
                    {'name': 'Philip V', 'role': 'antagonist', 'real': True},
                    {'name': 'Fabius', 'role': 'protagonist', 'real': True},
                ],
                'notes': 'Rigorous historical method, personal experience'
            },
            {
                'title': 'Ab Urbe Condita (History of Rome)',
                'author': 'Livy',
                'year': 27,
                'language': 'Latin',
                'genre': 'history',
                'truth_claim': 'documentary',
                'external_verification': 'High for later books, legendary for early Rome',
                'characters': [
                    {'name': 'Romulus', 'role': 'protagonist', 'real': False},  # Legendary founder
                    {'name': 'Cincinnatus', 'role': 'protagonist', 'real': True},
                    {'name': 'Scipio', 'role': 'protagonist', 'real': True},
                    {'name': 'Cato', 'role': 'protagonist', 'real': True},
                    {'name': 'Caesar', 'role': 'protagonist', 'real': True},
                ],
                'notes': 'Mix of legend (early) and history (late)'
            },
            {
                'title': 'Annals',
                'author': 'Tacitus',
                'year': 116,
                'language': 'Latin',
                'genre': 'history',
                'truth_claim': 'documentary',
                'external_verification': 'High - careful source analysis',
                'characters': [
                    {'name': 'Tiberius', 'role': 'antagonist', 'real': True},
                    {'name': 'Nero', 'role': 'antagonist', 'real': True},
                    {'name': 'Sejanus', 'role': 'antagonist', 'real': True},
                    {'name': 'Agrippina', 'role': 'complex', 'real': True},
                ],
                'notes': 'Critical historian, documented Neronian persecution of Christians'
            },
            {
                'title': 'Parallel Lives',
                'author': 'Plutarch',
                'year': 100,
                'language': 'Greek',
                'genre': 'biography',
                'truth_claim': 'biographical',
                'external_verification': 'High - comparative biography',
                'characters': [
                    {'name': 'Alexander', 'role': 'protagonist', 'real': True},
                    {'name': 'Caesar', 'role': 'protagonist', 'real': True},
                    {'name': 'Demosthenes', 'role': 'protagonist', 'real': True},
                    {'name': 'Cicero', 'role': 'protagonist', 'real': True},
                    {'name': 'Pericles', 'role': 'protagonist', 'real': True},
                ],
                'notes': 'Comparative biography, moralistic purpose'
            },
        ]
    
    def _ancient_literary(self) -> List[Dict]:
        """
        Ancient literary/epic texts (KNOWN fiction/poetry).
        Not claiming historical truth.
        """
        return [
            {
                'title': 'The Iliad',
                'author': 'Homer',
                'year': -750,
                'language': 'Greek',
                'genre': 'epic_poetry',
                'truth_claim': 'mythological',
                'external_verification': 'None - Trojan War historicity disputed',
                'characters': [
                    {'name': 'Achilles', 'role': 'protagonist', 'real': False},
                    {'name': 'Hector', 'role': 'antagonist', 'real': False},
                    {'name': 'Agamemnon', 'role': 'complex', 'real': False},
                    {'name': 'Odysseus', 'role': 'protagonist', 'real': False},
                    {'name': 'Priam', 'role': 'supporting', 'real': False},
                    {'name': 'Paris', 'role': 'antagonist', 'real': False},
                    {'name': 'Ajax', 'role': 'protagonist', 'real': False},
                    {'name': 'Patroclus', 'role': 'supporting', 'real': False},
                ],
                'notes': 'Epic poetry, may have historical kernel but highly mythologized'
            },
            {
                'title': 'The Odyssey',
                'author': 'Homer',
                'year': -750,
                'language': 'Greek',
                'genre': 'epic_poetry',
                'truth_claim': 'mythological',
                'external_verification': 'None',
                'characters': [
                    {'name': 'Odysseus', 'role': 'protagonist', 'real': False},
                    {'name': 'Penelope', 'role': 'protagonist', 'real': False},
                    {'name': 'Telemachus', 'role': 'supporting', 'real': False},
                    {'name': 'Circe', 'role': 'complex', 'real': False},
                    {'name': 'Polyphemus', 'role': 'antagonist', 'real': False},
                    {'name': 'Calypso', 'role': 'supporting', 'real': False},
                ],
                'notes': 'Epic journey, fantastical elements, mythological'
            },
            {
                'title': 'The Aeneid',
                'author': 'Virgil',
                'year': -19,
                'language': 'Latin',
                'genre': 'epic_poetry',
                'truth_claim': 'literary_mythological',
                'external_verification': 'None - founding myth',
                'characters': [
                    {'name': 'Aeneas', 'role': 'protagonist', 'real': False},
                    {'name': 'Dido', 'role': 'tragic', 'real': False},
                    {'name': 'Turnus', 'role': 'antagonist', 'real': False},
                    {'name': 'Anchises', 'role': 'supporting', 'real': False},
                ],
                'notes': 'Literary epic, Roman founding myth, Augustan propaganda'
            },
            {
                'title': 'Metamorphoses',
                'author': 'Ovid',
                'year': 8,
                'language': 'Latin',
                'genre': 'mythological_poetry',
                'truth_claim': 'mythological',
                'external_verification': 'None - collection of myths',
                'characters': [
                    {'name': 'Apollo', 'role': 'deity', 'real': False},
                    {'name': 'Daphne', 'role': 'tragic', 'real': False},
                    {'name': 'Narcissus', 'role': 'tragic', 'real': False},
                    {'name': 'Echo', 'role': 'tragic', 'real': False},
                    {'name': 'Perseus', 'role': 'protagonist', 'real': False},
                    {'name': 'Orpheus', 'role': 'protagonist', 'real': False},
                ],
                'notes': 'Mythological poetry, explicitly fictional/symbolic'
            },
            {
                'title': 'Oedipus Rex',
                'author': 'Sophocles',
                'year': -429,
                'language': 'Greek',
                'genre': 'tragedy',
                'truth_claim': 'mythological_drama',
                'external_verification': 'None - mythological',
                'characters': [
                    {'name': 'Oedipus', 'role': 'tragic_protagonist', 'real': False},
                    {'name': 'Jocasta', 'role': 'tragic', 'real': False},
                    {'name': 'Creon', 'role': 'antagonist', 'real': False},
                    {'name': 'Tiresias', 'role': 'prophet', 'real': False},
                ],
                'notes': 'Greek tragedy, mythological subject matter'
            },
            {
                'title': 'Medea',
                'author': 'Euripides',
                'year': -431,
                'language': 'Greek',
                'genre': 'tragedy',
                'truth_claim': 'mythological_drama',
                'external_verification': 'None',
                'characters': [
                    {'name': 'Medea', 'role': 'tragic_protagonist', 'real': False},
                    {'name': 'Jason', 'role': 'antagonist', 'real': False},
                    {'name': 'Creon', 'role': 'antagonist', 'real': False},
                ],
                'notes': 'Tragedy based on myth'
            },
            {
                'title': 'The Golden Ass',
                'author': 'Apuleius',
                'year': 170,
                'language': 'Latin',
                'genre': 'novel',
                'truth_claim': 'fictional',
                'external_verification': 'None - Roman novel',
                'characters': [
                    {'name': 'Lucius', 'role': 'protagonist', 'real': False},
                    {'name': 'Photis', 'role': 'supporting', 'real': False},
                    {'name': 'Pamphile', 'role': 'antagonist', 'real': False},
                ],
                'notes': 'Roman novel, picaresque fiction'
            },
        ]
    
    def _ancient_biography(self) -> List[Dict]:
        """Ancient biographical texts (mixed truth-claims)."""
        return [
            {
                'title': 'Life of Caesar',
                'author': 'Plutarch',
                'year': 100,
                'language': 'Greek',
                'genre': 'biography',
                'truth_claim': 'biographical_moralistic',
                'external_verification': 'High - Caesar well documented',
                'characters': [
                    {'name': 'Julius Caesar', 'role': 'protagonist', 'real': True},
                    {'name': 'Pompey', 'role': 'antagonist', 'real': True},
                    {'name': 'Brutus', 'role': 'complex', 'real': True},
                    {'name': 'Cato', 'role': 'antagonist', 'real': True},
                    {'name': 'Cleopatra', 'role': 'supporting', 'real': True},
                ],
                'notes': 'Biography with moral purpose, generally accurate'
            },
            {
                'title': 'Life of Apollonius of Tyana',
                'author': 'Philostratus',
                'year': 220,
                'language': 'Greek',
                'genre': 'hagiography',
                'truth_claim': 'biographical_legendary',
                'external_verification': 'Low - possibly fictional sage',
                'characters': [
                    {'name': 'Apollonius', 'role': 'protagonist', 'real': 'disputed'},
                    {'name': 'Damis', 'role': 'companion', 'real': 'disputed'},
                ],
                'notes': 'Legendary biography, possibly fictional, claimed as rival to Jesus'
            },
        ]
    
    def get_all_characters(self, category: str = None) -> List[Dict]:
        """Get all characters, optionally filtered by category."""
        all_chars = []
        
        for category_name, texts in self.texts.items():
            if category and category_name != category:
                continue
            
            for text in texts:
                for char in text['characters']:
                    char_data = char.copy()
                    char_data['work'] = text['title']
                    char_data['author'] = text['author']
                    char_data['year'] = text['year']
                    char_data['genre'] = text['genre']
                    char_data['truth_claim'] = text['truth_claim']
                    char_data['external_verification'] = text['external_verification']
                    all_chars.append(char_data)
        
        return all_chars
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        stats = {
            'total_texts': sum(len(texts) for texts in self.texts.values()),
            'total_characters': len(self.get_all_characters()),
            'by_category': {}
        }
        
        for category, texts in self.texts.items():
            chars = self.get_all_characters(category)
            real_count = sum(1 for c in chars if c.get('real') == True)
            
            stats['by_category'][category] = {
                'texts': len(texts),
                'characters': len(chars),
                'real_people': real_count,
                'fictional': len(chars) - real_count
            }
        
        return stats
    
    def export_to_json(self, filepath: str):
        """Export database to JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.texts, f, indent=2, ensure_ascii=False)


# Singleton
greco_roman_db = GrecoRomanComparisonDatabase()

if __name__ == "__main__":
    output_path = Path(__file__).parent / "greco_roman_comparison.json"
    greco_roman_db.export_to_json(str(output_path))
    
    stats = greco_roman_db.get_statistics()
    print("Ancient Greco-Roman Comparison Database")
    print("=" * 50)
    print(f"Total Texts: {stats['total_texts']}")
    print(f"Total Characters: {stats['total_characters']}")
    print("\nBy Category:")
    for cat, cat_stats in stats['by_category'].items():
        print(f"\n{cat}:")
        print(f"  Texts: {cat_stats['texts']}")
        print(f"  Characters: {cat_stats['characters']}")
        print(f"  Real: {cat_stats['real_people']}")

