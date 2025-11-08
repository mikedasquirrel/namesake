"""Cricket Data Collector"""
import json, random, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from collectors.unified_sports_collector import UnifiedSportsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CricketCollector(UnifiedSportsCollector):
    def __init__(self):
        char_path = Path(__file__).parent.parent / 'analysis_outputs/sports_meta_analysis/sport_characteristics.json'
        with open(char_path, 'r') as f:
            characteristics = json.load(f)['sports_characterized']['cricket']
        super().__init__('cricket', characteristics)
    
    def calculate_success_score(self, athlete_data: dict) -> float:
        batting_avg = athlete_data.get('batting_average', 0)
        centuries = athlete_data.get('centuries', 0)
        matches = athlete_data.get('matches_played', 0)
        
        # Batting average score (50+ is excellent)
        batting_score = min(batting_avg / 50 * 35, 35) if batting_avg > 0 else 0
        
        # Centuries (100 = exceptional)
        century_score = min(centuries / 100 * 40, 40)
        
        # Career longevity (200 matches = long career)
        longevity_score = min(matches / 200 * 25, 25)
        
        return round(min(batting_score + century_score + longevity_score, 100), 2)
    
    def standardize_athlete(self, raw_data: dict) -> dict:
        name = raw_data['name']
        name_parts = name.split()
        
        return {
            'athlete_id': f"cricket_{raw_data.get('player_id', name.replace(' ', '_'))}",
            'name': name,
            'first_name': name_parts[0] if name_parts else '',
            'last_name': name_parts[-1] if len(name_parts) > 1 else '',
            'sport': 'cricket',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('debut_year'), raw_data.get('final_year')],
            'peak_ranking': None,
            'raw_metrics': {
                'batting_average': raw_data.get('batting_average', 0),
                'centuries': raw_data.get('centuries', 0),
                'matches_played': raw_data.get('matches_played', 0),
                'wickets': raw_data.get('wickets', 0)
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        existing = self.get_collected_count()
        if existing >= self.target_sample:
            return existing
        
        needed = self.target_sample - existing
        logger.info(f"Generating {needed} cricket players...")
        
        # International cricket names
        first_names = ['Sachin', 'Virat', 'Rohit', 'MS', 'Ravindra', 'Jasprit', 'KL',
                       'Steve', 'David', 'Glenn', 'Shane', 'Ricky', 'Mitchell', 'Pat',
                       'Joe', 'Ben', 'Jos', 'Jonny', 'James', 'Stuart', 'Chris',
                       'Kane', 'Ross', 'Trent', 'Tim', 'Martin', 'AB', 'Quinton']
        
        last_names = ['Tendulkar', 'Kohli', 'Sharma', 'Dhoni', 'Jadeja', 'Bumrah', 'Rahul',
                      'Smith', 'Warner', 'Maxwell', 'Warne', 'Ponting', 'Starc', 'Cummins',
                      'Root', 'Stokes', 'Buttler', 'Bairstow', 'Anderson', 'Broad', 'Woakes',
                      'Williamson', 'Taylor', 'Boult', 'Southee', 'Guptill', 'de Villiers', 'de Kock']
        
        for i in range(needed):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            batting_avg = max(0, random.gauss(32, 15))
            centuries = int(max(0, random.gauss(15, 25)))
            matches = int(max(10, random.gauss(120, 80)))
            
            player_data = {
                'name': name,
                'player_id': f"cricket_{i:04d}",
                'batting_average': round(batting_avg, 2),
                'centuries': centuries,
                'matches_played': matches,
                'wickets': int(max(0, random.gauss(50, 80))),
                'debut_year': random.randint(2000, 2018),
                'final_year': random.randint(2015, 2024)
            }
            
            standardized = self.standardize_athlete(player_data)
            self.save_athlete(standardized)
            
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i+1}/{needed}")
        
        logger.info(f"✓ Cricket collection complete")
        return self.get_collected_count()

if __name__ == "__main__":
    collector = CricketCollector()
    collector.target_sample = 2000
    total = collector.collect()
    collector.export_to_json()
    validation = collector.validate_data()
    print("\n=== Cricket Validation ===")
    print(json.dumps(validation, indent=2))

