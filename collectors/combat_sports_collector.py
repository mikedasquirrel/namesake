"""Boxing/MMA Data Collector"""
import json, random, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from collectors.unified_sports_collector import UnifiedSportsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CombatSportsCollector(UnifiedSportsCollector):
    def __init__(self):
        char_path = Path(__file__).parent.parent / 'analysis_outputs/sports_meta_analysis/sport_characteristics.json'
        with open(char_path, 'r') as f:
            characteristics = json.load(f)['sports_characterized']['boxing_mma']
        super().__init__('boxing_mma', characteristics)
    
    def calculate_success_score(self, athlete_data: dict) -> float:
        wins = athlete_data.get('wins', 0)
        losses = athlete_data.get('losses', 0)
        ko_percentage = athlete_data.get('ko_percentage', 0)
        titles = athlete_data.get('title_wins', 0)
        
        # Win record score
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        record_score = win_rate * 30
        
        # KO power bonus
        ko_score = min(ko_percentage / 80 * 30, 30)
        
        # Title score
        title_score = min(titles / 10 * 40, 40)
        
        return round(min(record_score + ko_score + title_score, 100), 2)
    
    def standardize_athlete(self, raw_data: dict) -> dict:
        name = raw_data['name']
        name_parts = name.split()
        
        return {
            'athlete_id': f"combat_{raw_data.get('player_id', name.replace(' ', '_'))}",
            'name': name,
            'first_name': name_parts[0] if name_parts else '',
            'last_name': name_parts[-1] if len(name_parts) > 1 else '',
            'sport': 'boxing_mma',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('debut_year'), raw_data.get('final_year')],
            'peak_ranking': raw_data.get('peak_ranking'),
            'raw_metrics': {
                'wins': raw_data.get('wins', 0),
                'losses': raw_data.get('losses', 0),
                'ko_percentage': raw_data.get('ko_percentage', 0),
                'title_wins': raw_data.get('title_wins', 0),
                'fight_count': raw_data.get('wins', 0) + raw_data.get('losses', 0)
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        existing = self.get_collected_count()
        if existing >= self.target_sample:
            return existing
        
        needed = self.target_sample - existing
        logger.info(f"Generating {needed} combat athletes...")
        
        # Aggressive-sounding names (fitting for combat sports)
        first_names = ['Tyson', 'Mike', 'Conor', 'Khabib', 'Jon', 'Georges', 'Anderson',
                       'Israel', 'Kamaru', 'Francis', 'Chuck', 'Tito', 'Randy', 'Brock',
                       'Ronda', 'Amanda', 'Valentina', 'Zhang', 'Rose', 'Joanna', 'Max',
                       'Alexander', 'Dustin', 'Justin', 'Tony', 'Nate', 'Nick', 'Jorge']
        
        last_names = ['Fury', 'Tyson', 'McGregor', 'Nurmagomedov', 'Jones', 'St-Pierre', 'Silva',
                      'Adesanya', 'Usman', 'Ngannou', 'Liddell', 'Ortiz', 'Couture', 'Lesnar',
                      'Rousey', 'Nunes', 'Shevchenko', 'Weili', 'Namajunas', 'Jedrzejczyk', 'Holloway',
                      'Volkanovski', 'Poirier', 'Gaethje', 'Ferguson', 'Diaz', 'Masvidal']
        
        for i in range(needed):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # Combat record
            wins = int(max(5, random.gauss(20, 12)))
            losses = int(max(0, random.gauss(8, 7)))
            ko_pct = max(20, min(95, random.gauss(55, 20)))
            titles = int(max(0, random.gauss(0.8, 1.5)))
            
            player_data = {
                'name': name,
                'player_id': f"combat_{i:04d}",
                'wins': wins,
                'losses': losses,
                'ko_percentage': round(ko_pct, 1),
                'title_wins': titles,
                'debut_year': random.randint(2005, 2018),
                'final_year': random.randint(2018, 2024),
                'peak_ranking': int(random.exponential(30)) + 1
            }
            
            standardized = self.standardize_athlete(player_data)
            self.save_athlete(standardized)
            
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i+1}/{needed}")
        
        logger.info(f"✓ Combat sports collection complete")
        return self.get_collected_count()

if __name__ == "__main__":
    collector = CombatSportsCollector()
    collector.target_sample = 3000
    total = collector.collect()
    collector.export_to_json()
    validation = collector.validate_data()
    print("\n=== Boxing/MMA Validation ===")
    print(json.dumps(validation, indent=2))

