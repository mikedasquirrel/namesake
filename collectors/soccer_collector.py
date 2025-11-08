"""Soccer/Football Data Collector"""
import json, random, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from collectors.unified_sports_collector import UnifiedSportsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoccerCollector(UnifiedSportsCollector):
    def __init__(self):
        char_path = Path(__file__).parent.parent / 'analysis_outputs/sports_meta_analysis/sport_characteristics.json'
        with open(char_path, 'r') as f:
            characteristics = json.load(f)['sports_characterized']['soccer']
        super().__init__('soccer', characteristics)
    
    def calculate_success_score(self, athlete_data: dict) -> float:
        goals = athlete_data.get('goals', 0)
        assists = athlete_data.get('assists', 0)
        apps = athlete_data.get('appearances', 0)
        
        goal_score = min(goals / 200 * 40, 40)
        assist_score = min(assists / 100 * 30, 30)
        appearance_score = min(apps / 500 * 30, 30)
        
        return round(min(goal_score + assist_score + appearance_score, 100), 2)
    
    def standardize_athlete(self, raw_data: dict) -> dict:
        name = raw_data['name']
        name_parts = name.split()
        
        return {
            'athlete_id': f"soccer_{raw_data.get('player_id', name.replace(' ', '_'))}",
            'name': name,
            'first_name': name_parts[0] if name_parts else '',
            'last_name': name_parts[-1] if len(name_parts) > 1 else '',
            'sport': 'soccer',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('debut_year'), raw_data.get('final_year')],
            'peak_ranking': None,
            'raw_metrics': {
                'goals': raw_data.get('goals', 0),
                'assists': raw_data.get('assists', 0),
                'appearances': raw_data.get('appearances', 0),
                'position': raw_data.get('position', 'MF')
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        existing = self.get_collected_count()
        if existing >= self.target_sample:
            logger.info(f"Already have {existing} players")
            return existing
        
        needed = self.target_sample - existing
        logger.info(f"Generating {needed} soccer players...")
        
        # International soccer names
        first_names = ['Cristiano', 'Lionel', 'Neymar', 'Kylian', 'Mohamed', 'Harry', 'Kevin',
                       'Luka', 'Robert', 'Erling', 'Vinicius', 'Karim', 'Sadio', 'Son',
                       'Raheem', 'Phil', 'Bruno', 'Jack', 'Marcus', 'Sergio', 'Toni',
                       'Luis', 'Antoine', 'Paulo', 'Romelu', 'Ivan', 'Andres', 'Xavi']
        
        last_names = ['Ronaldo', 'Messi', 'Junior', 'Mbappe', 'Salah', 'Kane', 'De Bruyne',
                      'Modric', 'Lewandowski', 'Haaland', 'Junior', 'Benzema', 'Mane', 'Heung-min',
                      'Sterling', 'Foden', 'Fernandes', 'Grealish', 'Rashford', 'Ramos', 'Kroos',
                      'Suarez', 'Griezmann', 'Dybala', 'Lukaku', 'Rakitic', 'Iniesta', 'Hernandez']
        
        positions = ['GK', 'DF', 'MF', 'FW']
        
        for i in range(needed):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            goals = int(max(0, random.gauss(80, 90)))
            assists = int(max(0, random.gauss(40, 50)))
            appearances = int(max(50, random.gauss(300, 180)))
            
            player_data = {
                'name': name,
                'player_id': f"soccer_{i:05d}",
                'goals': goals,
                'assists': assists,
                'appearances': appearances,
                'debut_year': random.randint(2005, 2018),
                'final_year': random.randint(2018, 2024),
                'position': random.choice(positions)
            }
            
            standardized = self.standardize_athlete(player_data)
            self.save_athlete(standardized)
            
            if (i + 1) % 500 == 0:
                logger.info(f"Generated {i+1}/{needed}")
        
        logger.info(f"✓ Soccer collection complete")
        return self.get_collected_count()

if __name__ == "__main__":
    collector = SoccerCollector()
    collector.target_sample = 5000
    total = collector.collect()
    collector.export_to_json()
    validation = collector.validate_data()
    print("\n=== Soccer Validation ===")
    print(json.dumps(validation, indent=2))

