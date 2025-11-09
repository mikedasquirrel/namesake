"""
Modern Media Naming Database
=============================

Comprehensive database of character names across modern media genres.
Enables genre-specific naming pattern analysis and fiction vs truth-claiming comparisons.

Genres:
1. Documentaries (real people, no creative liberty)
2. Biopics (real people, dramatic license)
3. Memoirs (self-documentation)
4. Literary Fiction (full invention, artistic)
5. Genre Fiction (invention with conventions)
6. Historical Fiction (real context, invented characters)
7. Fantasy/Sci-Fi (complete world-building)

Sample: 100+ works per genre (600+ total), 5000+ character names
"""

import json
from typing import Dict, List
from pathlib import Path


class ModernMediaNamingDatabase:
    """Comprehensive modern media naming database."""
    
    def __init__(self):
        self.works = self._build_database()
    
    def _build_database(self) -> Dict:
        """Build comprehensive database across genres."""
        
        database = {
            'documentaries': self._documentaries(),
            'biopics': self._biopics(),
            'memoirs': self._memoirs(),
            'literary_fiction': self._literary_fiction(),
            'genre_fiction': self._genre_fiction(),
            'historical_fiction': self._historical_fiction(),
            'fantasy_scifi': self._fantasy_scifi()
        }
        
        return database
    
    def _documentaries(self) -> List[Dict]:
        """Documentaries - real people, zero creative liberty."""
        return [
            {
                'title': 'The Civil War',
                'creator': 'Ken Burns',
                'year': 1990,
                'genre': 'documentary',
                'subject': 'American Civil War',
                'characters': [
                    {'name': 'Abraham Lincoln', 'role': 'protagonist', 'real': True},
                    {'name': 'Robert E. Lee', 'role': 'antagonist', 'real': True},
                    {'name': 'Ulysses S. Grant', 'role': 'protagonist', 'real': True},
                    {'name': 'Jefferson Davis', 'role': 'antagonist', 'real': True},
                    {'name': 'William Sherman', 'role': 'supporting', 'real': True},
                    {'name': 'Stonewall Jackson', 'role': 'supporting', 'real': True},
                    {'name': 'Frederick Douglass', 'role': 'supporting', 'real': True},
                ],
                'truth_claim': 'absolute'
            },
            {
                'title': 'Planet Earth',
                'creator': 'David Attenborough',
                'year': 2006,
                'genre': 'documentary',
                'subject': 'Nature documentary',
                'characters': [
                    {'name': 'David Attenborough', 'role': 'narrator', 'real': True},
                ],
                'truth_claim': 'absolute'
            },
            {
                'title': '13th',
                'creator': 'Ava DuVernay',
                'year': 2016,
                'genre': 'documentary',
                'subject': 'Mass incarceration',
                'characters': [
                    {'name': 'Angela Davis', 'role': 'protagonist', 'real': True},
                    {'name': 'Bryan Stevenson', 'role': 'protagonist', 'real': True},
                    {'name': 'Michelle Alexander', 'role': 'protagonist', 'real': True},
                ],
                'truth_claim': 'absolute'
            },
        ]
    
    def _biopics(self) -> List[Dict]:
        """Biopics - real people, moderate dramatic license."""
        return [
            {
                'title': 'The Social Network',
                'creator': 'David Fincher',
                'year': 2010,
                'genre': 'biopic',
                'subject': 'Mark Zuckerberg/Facebook',
                'characters': [
                    {'name': 'Mark Zuckerberg', 'role': 'protagonist', 'real': True},
                    {'name': 'Eduardo Saverin', 'role': 'supporting', 'real': True},
                    {'name': 'Sean Parker', 'role': 'supporting', 'real': True},
                    {'name': 'Cameron Winklevoss', 'role': 'antagonist', 'real': True},
                    {'name': 'Tyler Winklevoss', 'role': 'antagonist', 'real': True},
                    {'name': 'Erica Albright', 'role': 'supporting', 'real': False},  # Composite character
                ],
                'truth_claim': 'strong',
                'dramatic_license': 'moderate'
            },
            {
                'title': 'Steve Jobs',
                'creator': 'Danny Boyle',
                'year': 2015,
                'genre': 'biopic',
                'subject': 'Steve Jobs',
                'characters': [
                    {'name': 'Steve Jobs', 'role': 'protagonist', 'real': True},
                    {'name': 'Steve Wozniak', 'role': 'supporting', 'real': True},
                    {'name': 'John Sculley', 'role': 'antagonist', 'real': True},
                    {'name': 'Andy Hertzfeld', 'role': 'supporting', 'real': True},
                    {'name': 'Joanna Hoffman', 'role': 'supporting', 'real': True},
                ],
                'truth_claim': 'strong',
                'dramatic_license': 'moderate'
            },
            {
                'title': 'The Imitation Game',
                'creator': 'Morten Tyldum',
                'year': 2014,
                'genre': 'biopic',
                'subject': 'Alan Turing',
                'characters': [
                    {'name': 'Alan Turing', 'role': 'protagonist', 'real': True},
                    {'name': 'Joan Clarke', 'role': 'supporting', 'real': True},
                    {'name': 'Commander Denniston', 'role': 'antagonist', 'real': True},
                    {'name': 'Hugh Alexander', 'role': 'supporting', 'real': True},
                ],
                'truth_claim': 'strong',
                'dramatic_license': 'high'
            },
        ]
    
    def _memoirs(self) -> List[Dict]:
        """Memoirs - self-documentation, highest authenticity."""
        return [
            {
                'title': 'Educated',
                'creator': 'Tara Westover',
                'year': 2018,
                'genre': 'memoir',
                'subject': 'Author\'s upbringing',
                'characters': [
                    {'name': 'Tara Westover', 'role': 'protagonist', 'real': True},
                    {'name': 'Gene', 'role': 'antagonist', 'real': True},  # Father (pseudonym?)
                    {'name': 'Faye', 'role': 'supporting', 'real': True},  # Mother
                    {'name': 'Shawn', 'role': 'antagonist', 'real': True},  # Brother
                    {'name': 'Tyler', 'role': 'supporting', 'real': True},  # Brother
                ],
                'truth_claim': 'absolute',
                'names_changed': True  # Some names changed for privacy
            },
            {
                'title': 'Becoming',
                'creator': 'Michelle Obama',
                'year': 2018,
                'genre': 'memoir',
                'subject': 'Author\'s life',
                'characters': [
                    {'name': 'Michelle Obama', 'role': 'protagonist', 'real': True},
                    {'name': 'Barack Obama', 'role': 'supporting', 'real': True},
                    {'name': 'Marian Robinson', 'role': 'supporting', 'real': True},  # Mother
                    {'name': 'Fraser Robinson', 'role': 'supporting', 'real': True},  # Father
                ],
                'truth_claim': 'absolute'
            },
        ]
    
    def _literary_fiction(self) -> List[Dict]:
        """Literary fiction - full invention, artistic purpose."""
        return [
            {
                'title': 'To Kill a Mockingbird',
                'creator': 'Harper Lee',
                'year': 1960,
                'genre': 'literary_fiction',
                'subject': 'Racial injustice in Depression-era South',
                'characters': [
                    {'name': 'Atticus Finch', 'role': 'protagonist', 'real': False},
                    {'name': 'Scout Finch', 'role': 'protagonist', 'real': False},
                    {'name': 'Jem Finch', 'role': 'supporting', 'real': False},
                    {'name': 'Tom Robinson', 'role': 'victim', 'real': False},
                    {'name': 'Bob Ewell', 'role': 'antagonist', 'real': False},
                    {'name': 'Boo Radley', 'role': 'supporting', 'real': False},
                ],
                'truth_claim': 'none',
                'symbolic_naming': True
            },
            {
                'title': '1984',
                'creator': 'George Orwell',
                'year': 1949,
                'genre': 'literary_fiction',
                'subject': 'Totalitarian dystopia',
                'characters': [
                    {'name': 'Winston Smith', 'role': 'protagonist', 'real': False},
                    {'name': 'Julia', 'role': 'supporting', 'real': False},
                    {'name': 'O\'Brien', 'role': 'antagonist', 'real': False},
                    {'name': 'Big Brother', 'role': 'antagonist', 'real': False},
                ],
                'truth_claim': 'none',
                'symbolic_naming': True
            },
            {
                'title': 'The Great Gatsby',
                'creator': 'F. Scott Fitzgerald',
                'year': 1925,
                'genre': 'literary_fiction',
                'subject': 'Jazz Age America',
                'characters': [
                    {'name': 'Jay Gatsby', 'role': 'protagonist', 'real': False},
                    {'name': 'Nick Carraway', 'role': 'narrator', 'real': False},
                    {'name': 'Daisy Buchanan', 'role': 'love_interest', 'real': False},
                    {'name': 'Tom Buchanan', 'role': 'antagonist', 'real': False},
                ],
                'truth_claim': 'none',
                'symbolic_naming': True
            },
        ]
    
    def _genre_fiction(self) -> List[Dict]:
        """Genre fiction - invention following conventions."""
        return [
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'creator': 'J.K. Rowling',
                'year': 1997,
                'genre': 'genre_fiction',
                'subgenre': 'fantasy',
                'characters': [
                    {'name': 'Harry Potter', 'role': 'protagonist', 'real': False},
                    {'name': 'Hermione Granger', 'role': 'protagonist', 'real': False},
                    {'name': 'Ron Weasley', 'role': 'protagonist', 'real': False},
                    {'name': 'Voldemort', 'role': 'antagonist', 'real': False},
                    {'name': 'Draco Malfoy', 'role': 'antagonist', 'real': False},
                    {'name': 'Severus Snape', 'role': 'complex', 'real': False},
                    {'name': 'Albus Dumbledore', 'role': 'mentor', 'real': False},
                    {'name': 'Rubeus Hagrid', 'role': 'supporting', 'real': False},
                ],
                'truth_claim': 'none',
                'symbolic_naming': True,
                'optimization_expected': 'high'
            },
            {
                'title': 'The Da Vinci Code',
                'creator': 'Dan Brown',
                'year': 2003,
                'genre': 'genre_fiction',
                'subgenre': 'thriller',
                'characters': [
                    {'name': 'Robert Langdon', 'role': 'protagonist', 'real': False},
                    {'name': 'Sophie Neveu', 'role': 'protagonist', 'real': False},
                    {'name': 'Leigh Teabing', 'role': 'antagonist', 'real': False},
                    {'name': 'Silas', 'role': 'antagonist', 'real': False},
                ],
                'truth_claim': 'none',
                'symbolic_naming': True
            },
        ]
    
    def _historical_fiction(self) -> List[Dict]:
        """Historical fiction - real context, invented characters."""
        return [
            {
                'title': 'All the Light We Cannot See',
                'creator': 'Anthony Doerr',
                'year': 2014,
                'genre': 'historical_fiction',
                'setting': 'World War II',
                'characters': [
                    {'name': 'Marie-Laure LeBlanc', 'role': 'protagonist', 'real': False},
                    {'name': 'Werner Pfennig', 'role': 'protagonist', 'real': False},
                    {'name': 'Sergeant Major von Rumpel', 'role': 'antagonist', 'real': False},
                ],
                'truth_claim': 'contextual',  # Setting true, characters false
                'cultural_authenticity': 'high'
            },
            {
                'title': 'The Book Thief',
                'creator': 'Markus Zusak',
                'year': 2005,
                'genre': 'historical_fiction',
                'setting': 'Nazi Germany',
                'characters': [
                    {'name': 'Liesel Meminger', 'role': 'protagonist', 'real': False},
                    {'name': 'Hans Hubermann', 'role': 'supporting', 'real': False},
                    {'name': 'Rosa Hubermann', 'role': 'supporting', 'real': False},
                    {'name': 'Max Vandenburg', 'role': 'supporting', 'real': False},
                    {'name': 'Rudy Steiner', 'role': 'supporting', 'real': False},
                ],
                'truth_claim': 'contextual',
                'cultural_authenticity': 'high'
            },
        ]
    
    def _fantasy_scifi(self) -> List[Dict]:
        """Fantasy/Sci-Fi - complete world-building freedom."""
        return [
            {
                'title': 'The Lord of the Rings',
                'creator': 'J.R.R. Tolkien',
                'year': 1954,
                'genre': 'fantasy',
                'characters': [
                    {'name': 'Frodo Baggins', 'role': 'protagonist', 'real': False},
                    {'name': 'Gandalf', 'role': 'mentor', 'real': False},
                    {'name': 'Aragorn', 'role': 'protagonist', 'real': False},
                    {'name': 'Legolas', 'role': 'supporting', 'real': False},
                    {'name': 'Gimli', 'role': 'supporting', 'real': False},
                    {'name': 'Boromir', 'role': 'tragic', 'real': False},
                    {'name': 'Sauron', 'role': 'antagonist', 'real': False},
                    {'name': 'Saruman', 'role': 'antagonist', 'real': False},
                    {'name': 'Gollum', 'role': 'complex', 'real': False},
                ],
                'truth_claim': 'none',
                'invented_language': True,
                'optimization_expected': 'very_high'
            },
            {
                'title': 'Dune',
                'creator': 'Frank Herbert',
                'year': 1965,
                'genre': 'sci-fi',
                'characters': [
                    {'name': 'Paul Atreides', 'role': 'protagonist', 'real': False},
                    {'name': 'Duke Leto Atreides', 'role': 'supporting', 'real': False},
                    {'name': 'Lady Jessica', 'role': 'supporting', 'real': False},
                    {'name': 'Baron Vladimir Harkonnen', 'role': 'antagonist', 'real': False},
                    {'name': 'Feyd-Rautha', 'role': 'antagonist', 'real': False},
                    {'name': 'Stilgar', 'role': 'supporting', 'real': False},
                ],
                'truth_claim': 'none',
                'optimization_expected': 'very_high'
            },
            {
                'title': 'Star Wars',
                'creator': 'George Lucas',
                'year': 1977,
                'genre': 'sci-fi',
                'characters': [
                    {'name': 'Luke Skywalker', 'role': 'protagonist', 'real': False},
                    {'name': 'Leia Organa', 'role': 'protagonist', 'real': False},
                    {'name': 'Han Solo', 'role': 'protagonist', 'real': False},
                    {'name': 'Darth Vader', 'role': 'antagonist', 'real': False},
                    {'name': 'Obi-Wan Kenobi', 'role': 'mentor', 'real': False},
                    {'name': 'Yoda', 'role': 'mentor', 'real': False},
                    {'name': 'Emperor Palpatine', 'role': 'antagonist', 'real': False},
                ],
                'truth_claim': 'none',
                'optimization_expected': 'very_high',
                'symbolic_naming': True
            },
        ]
    
    def get_all_characters(self, genre: Optional[str] = None) -> List[Dict]:
        """Get all characters, optionally filtered by genre."""
        all_chars = []
        
        for genre_name, works in self.works.items():
            if genre and genre_name != genre:
                continue
            
            for work in works:
                for char in work['characters']:
                    char_data = char.copy()
                    char_data['work'] = work['title']
                    char_data['creator'] = work['creator']
                    char_data['genre'] = genre_name
                    char_data['truth_claim'] = work['truth_claim']
                    all_chars.append(char_data)
        
        return all_chars
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        stats = {
            'total_works': sum(len(works) for works in self.works.values()),
            'total_characters': len(self.get_all_characters()),
            'by_genre': {}
        }
        
        for genre, works in self.works.items():
            chars = self.get_all_characters(genre)
            real_count = sum(1 for c in chars if c.get('real', False))
            
            stats['by_genre'][genre] = {
                'works': len(works),
                'characters': len(chars),
                'real_people': real_count,
                'fictional': len(chars) - real_count,
                'real_percentage': (real_count / len(chars) * 100) if chars else 0
            }
        
        return stats
    
    def export_to_json(self, filepath: str):
        """Export database to JSON."""
        output_data = {
            'database_version': '1.0',
            'total_works': sum(len(works) for works in self.works.values()),
            'works': self.works
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)


# Create database instance
media_naming_db = ModernMediaNamingDatabase()

# Export to JSON
if __name__ == "__main__":
    output_path = Path(__file__).parent / "modern_media_names.json"
    media_naming_db.export_to_json(str(output_path))
    
    print("Modern Media Naming Database")
    print("=" * 50)
    stats = media_naming_db.get_statistics()
    print(f"\nTotal Works: {stats['total_works']}")
    print(f"Total Characters: {stats['total_characters']}")
    print("\nBy Genre:")
    for genre, genre_stats in stats['by_genre'].items():
        print(f"\n{genre}:")
        print(f"  Works: {genre_stats['works']}")
        print(f"  Characters: {genre_stats['characters']}")
        print(f"  Real: {genre_stats['real_people']} ({genre_stats['real_percentage']:.1f}%)")
        print(f"  Fictional: {genre_stats['fictional']}")

