"""
Historical Season Analyzer
Analyze betting performance across past seasons
Track portfolio performance season-by-season, sport-by-sport
"""

from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class HistoricalSeasonAnalyzer:
    """Analyze historical betting performance by season"""
    
    def __init__(self):
        """Initialize historical analyzer"""
        self.season_definitions = self._define_seasons()
    
    def _define_seasons(self) -> Dict:
        """Define season boundaries for each sport"""
        return {
            'football': {
                'regular_season': (9, 1, 1, 7),  # Sept-Dec/Jan
                'playoffs': (1, 8, 2, 15),       # Jan-Feb
                'offseason': (2, 16, 8, 31)      # Feb-Aug
            },
            'basketball': {
                'regular_season': (10, 15, 4, 15),  # Oct-Apr
                'playoffs': (4, 16, 6, 30),         # Apr-Jun
                'offseason': (7, 1, 10, 14)         # Jul-Oct
            },
            'baseball': {
                'regular_season': (3, 20, 9, 30),  # Mar-Sep
                'playoffs': (10, 1, 11, 15),       # Oct-Nov
                'offseason': (11, 16, 3, 19)       # Nov-Mar
            }
        }
    
    def categorize_bets_by_season(self, bets: List[Dict], sport: str) -> Dict:
        """
        Categorize bets by season and phase
        
        Args:
            bets: List of bet records with timestamps
            sport: Sport type
            
        Returns:
            Bets organized by season
        """
        seasons = defaultdict(lambda: defaultdict(list))
        
        for bet in bets:
            game_date = bet.get('game_date')
            if not game_date:
                continue
            
            if isinstance(game_date, str):
                game_date = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
            
            # Determine season year and phase
            season_year, phase = self._determine_season_phase(game_date, sport)
            
            seasons[season_year][phase].append(bet)
        
        return dict(seasons)
    
    def _determine_season_phase(self, date: datetime, sport: str) -> Tuple[int, str]:
        """Determine which season and phase a date belongs to"""
        month = date.month
        day = date.day
        year = date.year
        
        # Determine season year (e.g., 2024-2025 NFL season = "2024")
        if sport == 'football':
            season_year = year if month >= 9 else year - 1
        elif sport == 'basketball':
            season_year = year if month >= 10 else year - 1
        elif sport == 'baseball':
            season_year = year
        else:
            season_year = year
        
        # Determine phase
        season_def = self.season_definitions.get(sport, {})
        
        for phase, (start_m, start_d, end_m, end_d) in season_def.items():
            if self._date_in_range(month, day, start_m, start_d, end_m, end_d):
                return season_year, phase
        
        return season_year, 'unknown'
    
    def _date_in_range(self, month: int, day: int, 
                       start_m: int, start_d: int, 
                       end_m: int, end_d: int) -> bool:
        """Check if date falls in range"""
        if start_m <= end_m:
            # Same year range
            if month < start_m or month > end_m:
                return False
            if month == start_m and day < start_d:
                return False
            if month == end_m and day > end_d:
                return False
            return True
        else:
            # Wraps around year (e.g., Dec-Jan)
            if month >= start_m or month <= end_m:
                if month == start_m and day < start_d:
                    return False
                if month == end_m and day > end_d:
                    return False
                return True
            return False
    
    def analyze_season_performance(self, season_bets: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze performance for a season broken down by phase
        
        Args:
            season_bets: Dict mapping phase to list of bets
            
        Returns:
            Season performance analysis
        """
        results = {}
        
        for phase, bets in season_bets.items():
            if not bets:
                continue
            
            settled_bets = [b for b in bets if b.get('bet_status') in ['won', 'lost', 'push']]
            
            if not settled_bets:
                continue
            
            wins = sum(1 for b in settled_bets if b.get('bet_status') == 'won')
            losses = sum(1 for b in settled_bets if b.get('bet_status') == 'lost')
            pushes = sum(1 for b in settled_bets if b.get('bet_status') == 'push')
            
            total_staked = sum(b.get('stake', 0) for b in settled_bets)
            total_profit = sum(b.get('profit', 0) for b in settled_bets)
            
            win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
            roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
            
            results[phase] = {
                'total_bets': len(settled_bets),
                'wins': wins,
                'losses': losses,
                'pushes': pushes,
                'win_rate': round(win_rate * 100, 2),
                'total_staked': round(total_staked, 2),
                'total_profit': round(total_profit, 2),
                'roi': round(roi, 2)
            }
        
        # Overall season
        all_bets = [b for phase_bets in season_bets.values() for b in phase_bets]
        settled_all = [b for b in all_bets if b.get('bet_status') in ['won', 'lost', 'push']]
        
        if settled_all:
            wins_all = sum(1 for b in settled_all if b.get('bet_status') == 'won')
            losses_all = sum(1 for b in settled_all if b.get('bet_status') == 'lost')
            staked_all = sum(b.get('stake', 0) for b in settled_all)
            profit_all = sum(b.get('profit', 0) for b in settled_all)
            
            results['season_total'] = {
                'total_bets': len(settled_all),
                'wins': wins_all,
                'losses': losses_all,
                'win_rate': round(wins_all / (wins_all + losses_all) * 100, 2) if (wins_all + losses_all) > 0 else 0,
                'total_staked': round(staked_all, 2),
                'total_profit': round(profit_all, 2),
                'roi': round(profit_all / staked_all * 100, 2) if staked_all > 0 else 0
            }
        
        return results
    
    def compare_seasons(self, all_seasons: Dict[int, Dict]) -> Dict:
        """
        Compare performance across multiple seasons
        
        Args:
            all_seasons: Dict mapping season_year to season performance
            
        Returns:
            Cross-season comparison
        """
        season_summaries = []
        
        for year, season_data in sorted(all_seasons.items()):
            if 'season_total' in season_data:
                total = season_data['season_total']
                season_summaries.append({
                    'season': year,
                    'bets': total['total_bets'],
                    'win_rate': total['win_rate'],
                    'roi': total['roi'],
                    'profit': total['total_profit']
                })
        
        if not season_summaries:
            return {'error': 'No season data available'}
        
        # Calculate trends
        rois = [s['roi'] for s in season_summaries]
        win_rates = [s['win_rate'] for s in season_summaries]
        
        return {
            'seasons_analyzed': len(season_summaries),
            'season_breakdown': season_summaries,
            'aggregate': {
                'mean_roi': round(np.mean(rois), 2),
                'std_roi': round(np.std(rois), 2),
                'mean_win_rate': round(np.mean(win_rates), 2),
                'best_season': max(season_summaries, key=lambda x: x['roi']),
                'worst_season': min(season_summaries, key=lambda x: x['roi']),
                'consistency': 'HIGH' if np.std(rois) < 5 else 'MODERATE' if np.std(rois) < 10 else 'VARIABLE'
            },
            'trend': {
                'roi_trend': 'IMPROVING' if rois[-1] > rois[0] else 'DECLINING' if rois[-1] < rois[0] else 'STABLE',
                'latest_season': season_summaries[-1]
            }
        }
    
    def analyze_portfolio_history(self, bets_by_sport: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze complete portfolio performance across all sports and seasons
        
        Args:
            bets_by_sport: Dict mapping sport to list of all bets
            
        Returns:
            Complete portfolio historical analysis
        """
        portfolio_analysis = {
            'by_sport': {},
            'by_season': defaultdict(lambda: {'bets': [], 'by_sport': {}}),
            'aggregate': {}
        }
        
        # Analyze each sport
        for sport, bets in bets_by_sport.items():
            # Categorize by season
            season_bets = self.categorize_bets_by_season(bets, sport)
            
            # Analyze each season
            sport_seasons = {}
            for year, phases in season_bets.items():
                season_perf = self.analyze_season_performance(phases)
                sport_seasons[year] = season_perf
                
                # Add to portfolio view
                portfolio_analysis['by_season'][year]['bets'].extend(bets)
                portfolio_analysis['by_season'][year]['by_sport'][sport] = season_perf.get('season_total', {})
            
            # Compare across seasons for this sport
            sport_comparison = self.compare_seasons(sport_seasons)
            
            portfolio_analysis['by_sport'][sport] = {
                'seasons': sport_seasons,
                'comparison': sport_comparison
            }
        
        # Calculate aggregate portfolio metrics
        all_bets = [b for sport_bets in bets_by_sport.values() for b in sport_bets]
        settled = [b for b in all_bets if b.get('bet_status') in ['won', 'lost', 'push']]
        
        if settled:
            total_staked = sum(b.get('stake', 0) for b in settled)
            total_profit = sum(b.get('profit', 0) for b in settled)
            wins = sum(1 for b in settled if b.get('bet_status') == 'won')
            losses = sum(1 for b in settled if b.get('bet_status') == 'lost')
            
            portfolio_analysis['aggregate'] = {
                'total_bets': len(settled),
                'total_sports': len(bets_by_sport),
                'total_staked': round(total_staked, 2),
                'total_profit': round(total_profit, 2),
                'overall_roi': round(total_profit / total_staked * 100, 2) if total_staked > 0 else 0,
                'overall_win_rate': round(wins / (wins + losses) * 100, 2) if (wins + losses) > 0 else 0,
                'by_sport_contribution': self._calculate_sport_contributions(bets_by_sport)
            }
        
        return portfolio_analysis
    
    def _calculate_sport_contributions(self, bets_by_sport: Dict) -> Dict:
        """Calculate each sport's contribution to portfolio"""
        contributions = {}
        
        for sport, bets in bets_by_sport.items():
            settled = [b for b in bets if b.get('bet_status') in ['won', 'lost', 'push']]
            if settled:
                profit = sum(b.get('profit', 0) for b in settled)
                staked = sum(b.get('stake', 0) for b in settled)
                
                contributions[sport] = {
                    'profit': round(profit, 2),
                    'staked': round(staked, 2),
                    'roi': round(profit / staked * 100, 2) if staked > 0 else 0,
                    'bet_count': len(settled)
                }
        
        return contributions


if __name__ == "__main__":
    print("Historical Season Analyzer ready for season-by-season tracking")

