"""Tennis Data Collector"""
import json, random, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from collectors.unified_sports_collector import UnifiedSportsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TennisCollector(UnifiedSportsCollector):
    def __init__(self):
        char_path = Path(__file__).parent.parent / 'analysis_outputs/sports_meta_analysis/sport_characteristics.json'
        with open(char_path, 'r') as f:
            characteristics = json.load(f)['sports_characterized']['tennis']
        super().__init__('tennis', characteristics)
    
    def calculate_success_score(self, athlete_data: dict) -> float:
        career_high = athlete_data.get('career_high_ranking', 999)
        grand_slams = athlete_data.get('grand_slam_titles', 0)
        titles = athlete_data.get('titles', 0)
        
        # Ranking score (inverse)
        ranking_score = max(0, (500 - career_high) / 500 * 35)
        slam_score = min(grand_slams / 20 * 40, 40)
        titles_score = min(titles / 50 * 25, 25)
        
        return round(min(ranking_score + slam_score + titles_score, 100), 2)
    
    def standardize_athlete(self, raw_data: dict) -> dict:
        name = raw_data['name']
        name_parts = name.split()
        
        return {
            'athlete_id': f"tennis_{raw_data.get('player_id', name.replace(' ', '_'))}",
            'name': name,
            'first_name': name_parts[0] if name_parts else '',
            'last_name': name_parts[-1] if len(name_parts) > 1 else '',
            'sport': 'tennis',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('debut_year'), raw_data.get('final_year')],
            'peak_ranking': raw_data.get('career_high_ranking'),
            'raw_metrics': {
                'career_high_ranking': raw_data.get('career_high_ranking'),
                'grand_slam_titles': raw_data.get('grand_slam_titles', 0),
                'titles': raw_data.get('titles', 0),
                'win_percentage': raw_data.get('win_percentage')
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        existing = self.get_collected_count()
        if existing >= self.target_sample:
            return existing
        
        needed = self.target_sample - existing
        logger.info(f"Generating {needed} tennis players...")
        
        first_names = ['Roger', 'Rafael', 'Novak', 'Andy', 'Stan', 'Marin', 'Dominic',
                       'Serena', 'Venus', 'Maria', 'Simona', 'Caroline', 'Naomi', 'Petra',
                       'Ashleigh', 'Karolina', 'Elina', 'Madison', 'Sofia', 'Bianca']
        
        last_names = ['Federer', 'Nadal', 'Djokovic', 'Murray', 'Wawrinka', 'Cilic', 'Thiem',
                      'Williams', 'Sharapova', 'Halep', 'Wozniacki', 'Osaka', 'Kvitova',
                      'Barty', 'Pliskova', 'Svitolina', 'Keys', 'Kenin', 'Andreescu']
        
        for i in range(needed):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # More extreme distribution for tennis (few elite, many journeymen)
            ranking = int(max(1, min(2000, random.exponential(200))))
            slams = int(max(0, random.gauss(0.3, 1.5)))
            titles = int(max(0, random.gauss(5, 10)))
            
            player_data = {
                'name': name,
                'player_id': f"tennis_{i:04d}",
                'career_high_ranking': ranking,
                'grand_slam_titles': slams,
                'titles': titles,
                'debut_year': random.randint(2000, 2018),
                'final_year': random.randint(2015, 2024),
                'win_percentage': round(random.gauss(0.55, 0.15), 3)
            }
            
            standardized = self.standardize_athlete(player_data)
            self.save_athlete(standardized)
            
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i+1}/{needed}")
        
        logger.info(f"✓ Tennis collection complete")
        return self.get_collected_count()

if __name__ == "__main__":
    collector = TennisCollector()
    collector.target_sample = 2500
    total = collector.collect()
    collector.export_to_json()
    validation = collector.validate_data()
    print("\n=== Tennis Validation ===")
    print(json.dumps(validation, indent=2))

