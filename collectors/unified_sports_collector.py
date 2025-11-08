"""
Unified Sports Collector Framework
Standardized data collection across all sports for meta-analysis
"""

import json
import time
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import sqlite3
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedSportsCollector:
    """
    Base class for collecting athlete data across sports
    Standardizes schema and provides common functionality
    """
    
    def __init__(self, sport_name: str, sport_characteristics: Dict[str, Any]):
        self.sport = sport_name
        self.characteristics = sport_characteristics
        self.target_sample = 2000
        self.athletes = []
        
        # Database setup
        self.db_path = f"analysis_outputs/sports_meta_analysis/{sport_name}_athletes.db"
        self._init_database()
        
        # Rate limiting
        self.request_delay = 1.5  # seconds between requests
        
    def _init_database(self):
        """Initialize SQLite database with standardized schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS athletes (
                athlete_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                sport TEXT NOT NULL,
                success_score REAL,
                career_start_year INTEGER,
                career_end_year INTEGER,
                peak_ranking INTEGER,
                raw_metrics TEXT,
                achievements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_metadata (
                collection_date TIMESTAMP,
                athletes_collected INTEGER,
                data_source TEXT,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
        
    def standardize_athlete(self, raw_data: Dict) -> Dict:
        """
        Convert sport-specific data to standardized schema
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement standardize_athlete()")
    
    def calculate_success_score(self, athlete_data: Dict) -> float:
        """
        Calculate normalized success score (0-100)
        Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement calculate_success_score()")
    
    def save_athlete(self, athlete: Dict):
        """Save standardized athlete to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO athletes 
            (athlete_id, full_name, first_name, last_name, sport, success_score,
             career_start_year, career_end_year, peak_ranking, raw_metrics, achievements)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            athlete['athlete_id'],
            athlete['name'],
            athlete.get('first_name', ''),
            athlete.get('last_name', ''),
            athlete['sport'],
            athlete['success_score'],
            athlete.get('career_years', [None, None])[0],
            athlete.get('career_years', [None, None])[1] if len(athlete.get('career_years', [])) > 1 else None,
            athlete.get('peak_ranking'),
            json.dumps(athlete.get('raw_metrics', {})),
            json.dumps(athlete.get('achievements', []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_collected_count(self) -> int:
        """Return number of athletes already collected"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM athletes")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def export_to_json(self) -> str:
        """Export collected data to JSON file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM athletes")
        
        columns = [description[0] for description in cursor.description]
        athletes = []
        
        for row in cursor.fetchall():
            athlete = dict(zip(columns, row))
            # Parse JSON fields
            athlete['raw_metrics'] = json.loads(athlete['raw_metrics'])
            athlete['achievements'] = json.loads(athlete['achievements'])
            athletes.append(athlete)
        
        conn.close()
        
        output_file = f"analysis_outputs/sports_meta_analysis/{self.sport}_athletes.json"
        with open(output_file, 'w') as f:
            json.dump(athletes, f, indent=2)
        
        logger.info(f"Exported {len(athletes)} athletes to {output_file}")
        return output_file
    
    def safe_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with rate limiting and retries"""
        for attempt in range(max_retries):
            try:
                time.sleep(self.request_delay)
                response = requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5 * (attempt + 1))  # Exponential backoff
        return None
    
    def collect(self):
        """Main collection method - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement collect()")
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate collected data quality"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM athletes")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM athletes WHERE success_score IS NOT NULL")
        with_score = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT full_name) FROM athletes")
        unique_names = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(success_score) FROM athletes WHERE success_score IS NOT NULL")
        avg_score = cursor.fetchone()[0]
        
        conn.close()
        
        validation = {
            'total_athletes': total_count,
            'athletes_with_score': with_score,
            'unique_names': unique_names,
            'average_success_score': round(avg_score, 2) if avg_score else None,
            'data_completeness': round((with_score / total_count * 100), 2) if total_count > 0 else 0,
            'potential_duplicates': total_count - unique_names
        }
        
        logger.info(f"Validation results: {validation}")
        return validation


class SoccerCollector(UnifiedSportsCollector):
    """Collect soccer/football player data"""
    
    def __init__(self):
        characteristics = json.load(open('analysis_outputs/sports_meta_analysis/sport_characteristics.json'))['sports_characterized']['soccer']
        super().__init__('soccer', characteristics)
        self.base_url = "https://fbref.com"
    
    def calculate_success_score(self, athlete_data: Dict) -> float:
        """
        Calculate success score from goals, assists, appearances, market_value
        Normalized to 0-100 scale
        """
        goals = athlete_data.get('goals', 0)
        assists = athlete_data.get('assists', 0)
        appearances = athlete_data.get('appearances', 0)
        
        # Simple scoring: weighted combination
        # Top players: 200+ goals OR 100+ assists OR 500+ appearances = 100
        goal_score = min(goals / 200 * 40, 40)  # Max 40 points
        assist_score = min(assists / 100 * 30, 30)  # Max 30 points
        appearance_score = min(appearances / 500 * 30, 30)  # Max 30 points
        
        total = goal_score + assist_score + appearance_score
        return round(min(total, 100), 2)
    
    def standardize_athlete(self, raw_data: Dict) -> Dict:
        """Convert FBref data to standard schema"""
        return {
            'athlete_id': f"soccer_{raw_data.get('player_id', raw_data['name'].replace(' ', '_'))}",
            'name': raw_data['name'],
            'first_name': raw_data['name'].split()[0] if raw_data['name'] else '',
            'last_name': raw_data['name'].split()[-1] if raw_data['name'] and len(raw_data['name'].split()) > 1 else '',
            'sport': 'soccer',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('career_start'), raw_data.get('career_end')],
            'peak_ranking': raw_data.get('peak_ranking'),
            'raw_metrics': {
                'goals': raw_data.get('goals', 0),
                'assists': raw_data.get('assists', 0),
                'appearances': raw_data.get('appearances', 0),
                'market_value': raw_data.get('market_value'),
                'position': raw_data.get('position')
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        """Collect soccer player data from FBref"""
        logger.info(f"Starting soccer data collection (target: {self.target_sample})")
        
        # For now, return placeholder - actual scraping would go here
        logger.info("Soccer collector ready for implementation")
        # Actual implementation would scrape FBref or use API
        pass


class TennisCollector(UnifiedSportsCollector):
    """Collect tennis player data"""
    
    def __init__(self):
        characteristics = json.load(open('analysis_outputs/sports_meta_analysis/sport_characteristics.json'))['sports_characterized']['tennis']
        super().__init__('tennis', characteristics)
    
    def calculate_success_score(self, athlete_data: Dict) -> float:
        """
        Score based on career high ranking, grand slams, prize money
        """
        career_high = athlete_data.get('career_high_ranking', 999)
        grand_slams = athlete_data.get('grand_slam_titles', 0)
        
        # Ranking score (inverse - lower ranking is better)
        ranking_score = max(0, (500 - career_high) / 500 * 40)
        
        # Grand slam score
        slam_score = min(grand_slams / 20 * 60, 60)  # 20 slams = max score
        
        total = ranking_score + slam_score
        return round(min(total, 100), 2)
    
    def standardize_athlete(self, raw_data: Dict) -> Dict:
        return {
            'athlete_id': f"tennis_{raw_data.get('player_id', raw_data['name'].replace(' ', '_'))}",
            'name': raw_data['name'],
            'first_name': raw_data['name'].split()[0] if raw_data['name'] else '',
            'last_name': raw_data['name'].split()[-1] if raw_data['name'] and len(raw_data['name'].split()) > 1 else '',
            'sport': 'tennis',
            'success_score': self.calculate_success_score(raw_data),
            'career_years': [raw_data.get('career_start'), raw_data.get('career_end')],
            'peak_ranking': raw_data.get('career_high_ranking'),
            'raw_metrics': {
                'career_high_ranking': raw_data.get('career_high_ranking'),
                'grand_slam_titles': raw_data.get('grand_slam_titles', 0),
                'atp_wta_titles': raw_data.get('titles', 0),
                'prize_money': raw_data.get('prize_money'),
                'win_percentage': raw_data.get('win_percentage')
            },
            'achievements': raw_data.get('achievements', [])
        }
    
    def collect(self):
        logger.info(f"Starting tennis data collection (target: {self.target_sample})")
        logger.info("Tennis collector ready for implementation")
        pass


# Factory function to create appropriate collector
def get_collector(sport_name: str) -> UnifiedSportsCollector:
    """Return appropriate collector for sport"""
    collectors = {
        'soccer': SoccerCollector,
        'tennis': TennisCollector,
        # Add others as implemented
    }
    
    if sport_name not in collectors:
        raise ValueError(f"No collector implemented for sport: {sport_name}")
    
    return collectors[sport_name]()


if __name__ == "__main__":
    # Test the framework
    print("Testing Unified Sports Collector Framework")
    
    # Test soccer collector
    soccer = SoccerCollector()
    print(f"Soccer collector initialized: {soccer.sport}")
    print(f"Target sample: {soccer.target_sample}")
    print(f"Database: {soccer.db_path}")
    
    # Test tennis collector  
    tennis = TennisCollector()
    print(f"Tennis collector initialized: {tennis.sport}")
    
    print("\nFramework ready for data collection!")

