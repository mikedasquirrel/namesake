"""Sports Roster Locality & Demographic Composition Collector

Aggregates existing NFL/NBA/MLB player data by team and generates baseline American name samples.
Part of the Domain Analysis Template System for roster composition analysis.

Author: Michael Smerconish
Date: November 2025
"""

import logging
import json
import random
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

from core.models import db, NFLPlayer, NBAPlayer, MLBPlayer
from core.models import NFLPlayerAnalysis, NBAPlayerAnalysis, MLBPlayerAnalysis
from data.common_american_names import COMMON_FIRST_NAMES, COMMON_SURNAMES, generate_population_names
from analyzers.phonetic_base import PhoneticBase

logger = logging.getLogger(__name__)


class SportsRosterLocalityCollector:
    """
    Collects and aggregates professional sports roster data for locality analysis.
    
    Aggregates:
    - NFL player data (by team)
    - NBA player data (by team)
    - MLB player data (by team)
    - American baseline name samples (random + stratified)
    - Sport characteristics (contact level, speed, precision)
    """
    
    def __init__(self, baseline_sample_size: int = 10000):
        """
        Initialize collector.
        
        Args:
            baseline_sample_size: Number of baseline American names to generate
        """
        self.baseline_sample_size = baseline_sample_size
        self.phonetic_analyzer = PhoneticBase()
        
        # Sport characteristics file
        self.sport_chars_file = Path("analysis_outputs/sports_meta_analysis/sport_characteristics.json")
        
        logger.info("SportsRosterLocalityCollector initialized")
        logger.info(f"Baseline sample size: {baseline_sample_size:,}")
    
    def collect_all_rosters(self) -> Dict:
        """
        Collect all professional sports roster data.
        
        Returns:
            Dictionary with roster data by sport and team
        """
        logger.info("="*80)
        logger.info("COLLECTING ROSTER DATA")
        logger.info("="*80)
        
        results = {
            'rosters': {},
            'sport_counts': {},
            'total_players': 0,
            'total_teams': 0,
        }
        
        # Collect NFL rosters
        logger.info("\nCollecting NFL rosters...")
        nfl_rosters = self._collect_nfl_rosters()
        results['rosters']['nfl'] = nfl_rosters
        results['sport_counts']['nfl'] = {
            'teams': len(nfl_rosters),
            'players': sum(r['roster_size'] for r in nfl_rosters.values())
        }
        logger.info(f"  NFL: {len(nfl_rosters)} teams, {results['sport_counts']['nfl']['players']} players")
        
        # Collect NBA rosters
        logger.info("\nCollecting NBA rosters...")
        nba_rosters = self._collect_nba_rosters()
        results['rosters']['nba'] = nba_rosters
        results['sport_counts']['nba'] = {
            'teams': len(nba_rosters),
            'players': sum(r['roster_size'] for r in nba_rosters.values())
        }
        logger.info(f"  NBA: {len(nba_rosters)} teams, {results['sport_counts']['nba']['players']} players")
        
        # Collect MLB rosters
        logger.info("\nCollecting MLB rosters...")
        mlb_rosters = self._collect_mlb_rosters()
        results['rosters']['mlb'] = mlb_rosters
        results['sport_counts']['mlb'] = {
            'teams': len(mlb_rosters),
            'players': sum(r['roster_size'] for r in mlb_rosters.values())
        }
        logger.info(f"  MLB: {len(mlb_rosters)} teams, {results['sport_counts']['mlb']['players']} players")
        
        # Calculate totals
        results['total_teams'] = sum(s['teams'] for s in results['sport_counts'].values())
        results['total_players'] = sum(s['players'] for s in results['sport_counts'].values())
        
        logger.info(f"\nTotal: {results['total_teams']} teams, {results['total_players']} players")
        
        return results
    
    def _collect_nfl_rosters(self) -> Dict:
        """Collect NFL rosters grouped by team."""
        rosters = {}
        
        # Get all NFL players with analyses
        query = db.session.query(NFLPlayer, NFLPlayerAnalysis).join(
            NFLPlayerAnalysis,
            NFLPlayer.id == NFLPlayerAnalysis.player_id
        ).filter(
            NFLPlayer.team.isnot(None)
        )
        
        players_by_team = defaultdict(list)
        for player, analysis in query.all():
            if player.team:
                players_by_team[player.team].append({
                    'player': player,
                    'analysis': analysis
                })
        
        # Aggregate by team
        for team_id, players in players_by_team.items():
            if len(players) < 10:  # Skip teams with too few players
                continue
            
            roster_data = self._aggregate_roster_data(players, 'nfl', team_id)
            rosters[team_id] = roster_data
        
        return rosters
    
    def _collect_nba_rosters(self) -> Dict:
        """Collect NBA rosters grouped by team."""
        rosters = {}
        
        # Get all NBA players with analyses
        query = db.session.query(NBAPlayer, NBAPlayerAnalysis).join(
            NBAPlayerAnalysis,
            NBAPlayer.id == NBAPlayerAnalysis.player_id
        ).filter(
            NBAPlayer.team.isnot(None)
        )
        
        players_by_team = defaultdict(list)
        for player, analysis in query.all():
            if player.team:
                players_by_team[player.team].append({
                    'player': player,
                    'analysis': analysis
                })
        
        # Aggregate by team
        for team_id, players in players_by_team.items():
            if len(players) < 8:  # Skip teams with too few players
                continue
            
            roster_data = self._aggregate_roster_data(players, 'nba', team_id)
            rosters[team_id] = roster_data
        
        return rosters
    
    def _collect_mlb_rosters(self) -> Dict:
        """Collect MLB rosters grouped by team."""
        rosters = {}
        
        # Get all MLB players with analyses
        query = db.session.query(MLBPlayer, MLBPlayerAnalysis).join(
            MLBPlayerAnalysis,
            MLBPlayer.id == MLBPlayerAnalysis.player_id
        ).filter(
            MLBPlayer.team_id.isnot(None)
        )
        
        players_by_team = defaultdict(list)
        for player, analysis in query.all():
            if player.team_id:
                players_by_team[player.team_id].append({
                    'player': player,
                    'analysis': analysis
                })
        
        # Aggregate by team
        for team_id, players in players_by_team.items():
            if len(players) < 10:  # Skip teams with too few players
                continue
            
            roster_data = self._aggregate_roster_data(players, 'mlb', team_id)
            rosters[team_id] = roster_data
        
        return rosters
    
    def _aggregate_roster_data(self, players: List[Dict], sport: str, team_id: str) -> Dict:
        """
        Aggregate player-level data into team-level roster features.
        
        Args:
            players: List of player dicts with 'player' and 'analysis' keys
            sport: 'nfl', 'nba', or 'mlb'
            team_id: Team identifier
            
        Returns:
            Dict with aggregated roster features
        """
        analyses = [p['analysis'] for p in players if p['analysis']]
        
        if not analyses:
            return None
        
        # Extract player names for full name analysis
        player_names = [p['player'].name for p in players if p['player'].name]
        
        # Basic roster aggregates
        syllables = [a.syllable_count for a in analyses if a.syllable_count]
        harshness = [a.harshness_score for a in analyses if a.harshness_score]
        memorability = [a.memorability_score for a in analyses if a.memorability_score]
        
        roster_data = {
            'team_id': team_id,
            'sport': sport,
            'roster_size': len(analyses),
            'player_names': player_names,
            
            # Aggregate phonetic features
            'mean_syllables': float(np.mean(syllables)) if syllables else 3.0,
            'syllable_stddev': float(np.std(syllables)) if len(syllables) > 1 else 0.5,
            'mean_harshness': float(np.mean(harshness)) if harshness else 50.0,
            'mean_memorability': float(np.mean(memorability)) if memorability else 50.0,
            
            # Roster harmony (inverse of syllable stddev)
            'roster_harmony': 100 - (float(np.std(syllables)) * 15) if len(syllables) > 1 else 75.0,
            
            # Store analyses for demographic classification
            'analyses': analyses,
        }
        
        # Get team name for proper identification
        player_obj = players[0]['player']
        if hasattr(player_obj, 'team_name') and player_obj.team_name:
            roster_data['team_name'] = player_obj.team_name
        else:
            roster_data['team_name'] = team_id
        
        return roster_data
    
    def generate_baseline_samples(self) -> Dict:
        """
        Generate baseline American name samples.
        
        Returns:
            Dict with random and stratified baseline samples
        """
        logger.info("\n" + "="*80)
        logger.info("GENERATING BASELINE SAMPLES")
        logger.info("="*80)
        
        # Generate random sample
        logger.info(f"\nGenerating {self.baseline_sample_size:,} random American names...")
        random_names = generate_population_names(self.baseline_sample_size)
        
        # Analyze random baseline
        random_baseline = self._analyze_name_sample(random_names, "Random Baseline")
        
        # Generate stratified sample matching US demographics
        logger.info(f"\nGenerating {self.baseline_sample_size:,} stratified American names...")
        stratified_names = self._generate_stratified_baseline()
        
        # Analyze stratified baseline
        stratified_baseline = self._analyze_name_sample(stratified_names, "Stratified Baseline")
        
        return {
            'random': random_baseline,
            'stratified': stratified_baseline,
        }
    
    def _generate_stratified_baseline(self) -> List[str]:
        """
        Generate stratified baseline matching US demographic breakdown.
        
        Target demographics (approximations):
        - 60% Anglo (traditional Anglo-American names)
        - 18% Latino (Spanish/Latin American origin)
        - 6% Asian (East/South/Southeast Asian)
        - 13% Black (African American naming patterns)
        - 3% Other
        """
        n = self.baseline_sample_size
        
        stratified_names = []
        
        # Anglo names (60%)
        n_anglo = int(n * 0.60)
        anglo_first = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
                       'Mary', 'Patricia', 'Jennifer', 'Linda', 'Barbara', 'Elizabeth', 'Susan', 'Jessica']
        anglo_last = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Wilson',
                      'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson']
        
        for _ in range(n_anglo):
            first = random.choice(anglo_first)
            last = random.choice(anglo_last)
            stratified_names.append(f"{first} {last}")
        
        # Latino names (18%)
        n_latino = int(n * 0.18)
        latino_first = ['Jose', 'Juan', 'Carlos', 'Luis', 'Miguel', 'Jorge', 'Pedro', 'Antonio',
                        'Maria', 'Carmen', 'Rosa', 'Ana', 'Isabel', 'Teresa', 'Lucia', 'Elena']
        latino_last = ['Garcia', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Perez',
                       'Sanchez', 'Ramirez', 'Torres', 'Flores', 'Rivera', 'Gomez', 'Diaz', 'Cruz', 'Reyes']
        
        for _ in range(n_latino):
            first = random.choice(latino_first)
            last = random.choice(latino_last)
            stratified_names.append(f"{first} {last}")
        
        # Asian names (6%)
        n_asian = int(n * 0.06)
        asian_first = ['Wei', 'Ming', 'Jun', 'Yuki', 'Haruto', 'Raj', 'Amit', 'Vikram',
                       'Mei', 'Lin', 'Sakura', 'Yuna', 'Priya', 'Ananya', 'Kavya', 'Riya']
        asian_last = ['Wang', 'Li', 'Zhang', 'Chen', 'Liu', 'Nguyen', 'Kim', 'Park',
                      'Patel', 'Kumar', 'Singh', 'Sharma', 'Tanaka', 'Sato', 'Suzuki', 'Yamamoto']
        
        for _ in range(n_asian):
            first = random.choice(asian_first)
            last = random.choice(asian_last)
            stratified_names.append(f"{first} {last}")
        
        # Black/African American names (13%)
        n_black = int(n * 0.13)
        black_first = ['Tyrone', 'DeShawn', 'Marcus', 'Jamal', 'Terrell', 'Andre', 'Xavier', 'Isaiah',
                       'Latoya', 'Keisha', 'Shaniqua', 'Tamika', 'Aaliyah', 'Jasmine', 'Destiny', 'Imani']
        black_last = ['Washington', 'Jefferson', 'Jackson', 'Robinson', 'Harris', 'Wright', 'Coleman',
                      'Walker', 'Bryant', 'Henderson', 'Barnes', 'Patterson', 'Butler', 'Foster', 'Bell', 'Perry']
        
        for _ in range(n_black):
            first = random.choice(black_first)
            last = random.choice(black_last)
            stratified_names.append(f"{first} {last}")
        
        # Other (3%) - Mixed/varied
        n_other = n - (n_anglo + n_latino + n_asian + n_black)
        for _ in range(n_other):
            first = random.choice(COMMON_FIRST_NAMES)
            last = random.choice(COMMON_SURNAMES)
            stratified_names.append(f"{first} {last}")
        
        # Shuffle to mix demographics
        random.shuffle(stratified_names)
        
        return stratified_names
    
    def _analyze_name_sample(self, names: List[str], label: str) -> Dict:
        """
        Analyze a sample of names using phonetic analyzer.
        
        Args:
            names: List of full names
            label: Label for logging
            
        Returns:
            Dict with aggregated phonetic features
        """
        logger.info(f"Analyzing {len(names):,} {label} names...")
        
        syllables = []
        harshness = []
        memorability = []
        
        for name in names[:1000]:  # Sample first 1000 for speed
            analysis = self.phonetic_analyzer.analyze(name)
            if analysis:
                syllables.append(analysis.get('syllable_count', 3))
                harshness.append(analysis.get('harshness_score', 50))
                memorability.append(analysis.get('memorability_score', 50))
        
        baseline_data = {
            'sample_size': len(names),
            'analyzed_sample': len(syllables),
            'names': names,  # Store for later analysis
            
            # Aggregates
            'mean_syllables': float(np.mean(syllables)) if syllables else 3.0,
            'syllable_stddev': float(np.std(syllables)) if syllables else 0.5,
            'mean_harshness': float(np.mean(harshness)) if harshness else 50.0,
            'mean_memorability': float(np.mean(memorability)) if memorability else 50.0,
        }
        
        logger.info(f"  Mean syllables: {baseline_data['mean_syllables']:.2f}")
        logger.info(f"  Mean harshness: {baseline_data['mean_harshness']:.1f}")
        logger.info(f"  Mean memorability: {baseline_data['mean_memorability']:.1f}")
        
        return baseline_data
    
    def load_sport_characteristics(self) -> Dict:
        """
        Load sport characteristics from JSON file.
        
        Returns:
            Dict with sport characteristics (contact level, speed, precision, etc.)
        """
        logger.info("\n" + "="*80)
        logger.info("LOADING SPORT CHARACTERISTICS")
        logger.info("="*80)
        
        if not self.sport_chars_file.exists():
            logger.warning(f"Sport characteristics file not found: {self.sport_chars_file}")
            logger.warning("Using default characteristics")
            return self._get_default_sport_characteristics()
        
        try:
            with open(self.sport_chars_file, 'r') as f:
                data = json.load(f)
            
            # Extract relevant sport characteristics
            characteristics = {}
            for sport_key in ['football', 'basketball', 'baseball']:
                if sport_key in data.get('sports_characterized', {}):
                    sport_data = data['sports_characterized'][sport_key]
                    
                    # Map to our sport keys
                    our_key = {'football': 'nfl', 'basketball': 'nba', 'baseball': 'mlb'}[sport_key]
                    
                    characteristics[our_key] = {
                        'contact_level': sport_data.get('contact_level', 5),
                        'action_speed': sport_data.get('action_speed', 5),
                        'precision_vs_power': sport_data.get('precision_vs_power', 5),
                        'endurance_vs_explosive': sport_data.get('endurance_vs_explosive', 5),
                        'team_size': sport_data.get('team_structure', {}).get('team_size', 11),
                        'announcer_repetition': sport_data.get('announcer_repetition', 7),
                    }
                    
                    logger.info(f"\n{our_key.upper()}:")
                    logger.info(f"  Contact level: {characteristics[our_key]['contact_level']}/10")
                    logger.info(f"  Action speed: {characteristics[our_key]['action_speed']}/10")
                    logger.info(f"  Precision: {characteristics[our_key]['precision_vs_power']}/10")
                    logger.info(f"  Team size: {characteristics[our_key]['team_size']}")
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Error loading sport characteristics: {e}")
            return self._get_default_sport_characteristics()
    
    def _get_default_sport_characteristics(self) -> Dict:
        """Return default sport characteristics if file not found."""
        return {
            'nfl': {
                'contact_level': 9,
                'action_speed': 5,
                'precision_vs_power': 3,
                'endurance_vs_explosive': 1,
                'team_size': 11,
                'announcer_repetition': 8,
            },
            'nba': {
                'contact_level': 6,
                'action_speed': 9,
                'precision_vs_power': 6,
                'endurance_vs_explosive': 6,
                'team_size': 5,
                'announcer_repetition': 9,
            },
            'mlb': {
                'contact_level': 2,
                'action_speed': 3,
                'precision_vs_power': 7,
                'endurance_vs_explosive': 2,
                'team_size': 9,
                'announcer_repetition': 8,
            },
        }
    
    def collect_full_dataset(self) -> Dict:
        """
        Collect complete dataset: rosters, baselines, and sport characteristics.
        
        Returns:
            Complete dataset for analysis
        """
        logger.info("\n" + "="*80)
        logger.info("COLLECTING FULL DATASET")
        logger.info("="*80)
        
        # Collect rosters
        roster_data = self.collect_all_rosters()
        
        # Generate baselines
        baseline_data = self.generate_baseline_samples()
        
        # Load sport characteristics
        sport_chars = self.load_sport_characteristics()
        
        # Combine
        full_dataset = {
            'rosters': roster_data['rosters'],
            'sport_counts': roster_data['sport_counts'],
            'total_teams': roster_data['total_teams'],
            'total_players': roster_data['total_players'],
            'baselines': baseline_data,
            'sport_characteristics': sport_chars,
            'collection_complete': True,
        }
        
        logger.info("\n" + "="*80)
        logger.info("COLLECTION COMPLETE")
        logger.info("="*80)
        logger.info(f"Teams: {full_dataset['total_teams']}")
        logger.info(f"Players: {full_dataset['total_players']}")
        logger.info(f"Baseline samples: {len(baseline_data['random']['names']):,}")
        logger.info("="*80)
        
        return full_dataset

