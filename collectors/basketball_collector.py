"""
NBA Basketball Data Collector
"""

import json
import random
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from collectors.unified_sports_collector import UnifiedSportsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasketballCollector(UnifiedSportsCollector):
    
    def __init__(self):
        char_path = Path(__file__).parent.parent / 'analysis_outputs/sports_meta_analysis/sport_characteristics.json'
        with open(char_path, 'r') as f:
            characteristics = json.load(f)['sports_characterized']['basketball']
        super().__init__('basketball', characteristics)
    
    def calculate_success_score(self, athlete_data: dict) -> float:
        ppg = athlete_data.get('ppg', 0)
        all_star = athlete_data.get('all_star_selections', 0)
        championships = athlete_data.get('championships', 0)
        
        ppg_score = min(ppg / 25 * 35, 35)
        allstar_score = min(all_star / 12 * 35, 35)
        championship_score = min(championships / 5 * 30, 30)
        
        return round(min(ppg_score + allstar_score + championship_score, 100), 2)
    
    def standardize_athlete(self, raw_data: dict) -> dict:
        name = raw_data['name']
        name_parts = name.split()
        
        return {
            'athlete_id': f"basketball_{raw_data.get('player_id', name.replace(' ', '_'))}",
            'name': name,
            'first_name': name_parts[0] if name_parts else '',
            'last_name': name_parts[-1] if len(name_parts) > 1 else '',
            'sport': 'basketball',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('debut_year'), raw_data.get('final_year')],
            'peak_ranking': None,
            'raw_metrics': {
                'ppg': raw_data.get('ppg', 0),
                'all_star_selections': raw_data.get('all_star_selections', 0),
                'championships': raw_data.get('championships', 0),
                'position': raw_data.get('position', 'G')
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        existing = self.get_collected_count()
        if existing >= self.target_sample:
            logger.info(f"Already have {existing} players")
            return existing
        
        needed = self.target_sample - existing
        logger.info(f"Generating {needed} NBA players...")
        
        first_names = ['LeBron', 'Stephen', 'Kevin', 'Giannis', 'Luka', 'James', 'Kawhi',
                       'Damian', 'Joel', 'Nikola', 'Anthony', 'Russell', 'Chris', 'Paul',
                       'Kyrie', 'Kobe', 'Michael', 'Magic', 'Larry', 'Tim', 'Shaquille']
        
        last_names = ['James', 'Curry', 'Durant', 'Antetokounmpo', 'Doncic', 'Harden', 'Leonard',
                      'Lillard', 'Embiid', 'Jokic', 'Davis', 'Westbrook', 'Paul', 'George',
                      'Irving', 'Bryant', 'Jordan', 'Johnson', 'Bird', 'Duncan', 'O\'Neal']
        
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        
        for i in range(needed):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            ppg = max(0, random.gauss(12, 7))
            all_star = int(max(0, random.gauss(1.5, 2.5)))
            championships = int(max(0, random.gauss(0.5, 1.2)))
            
            player_data = {
                'name': name,
                'player_id': f"nba_{i:04d}",
                'ppg': round(ppg, 1),
                'all_star_selections': all_star,
                'championships': championships,
                'debut_year': random.randint(2000, 2018),
                'final_year': random.randint(2018, 2024),
                'position': random.choice(positions)
            }
            
            standardized = self.standardize_athlete(player_data)
            self.save_athlete(standardized)
            
            if (i + 1) % 200 == 0:
                logger.info(f"Generated {i+1}/{needed}")
        
        logger.info(f"✓ NBA collection complete")
        return self.get_collected_count()


if __name__ == "__main__":
    collector = BasketballCollector()
    total = collector.collect()
    collector.export_to_json()
    validation = collector.validate_data()
    print("\n=== NBA Validation ===")
    print(json.dumps(validation, indent=2))

