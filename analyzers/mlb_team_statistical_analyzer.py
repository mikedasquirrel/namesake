"""MLB Team Statistical Analyzer

Comprehensive 3-layer analysis: Team Name + City + Roster Amalgamation

Analyses:
1. Team name analysis (name types, memorability)
2. City analysis (prestige hierarchy)
3. Roster amalgamation (player name composites)
4. Composite score prediction (3-layer → wins)
5. Matchup prediction (linguistic differential → winner)
6. Historical evolution (relocations, name changes)
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, accuracy_score, mean_squared_error
from scipy import stats

from core.models import db, MLBTeam, MLBTeamAnalysis, MLBMatchup

logger = logging.getLogger(__name__)


class MLBTeamStatisticalAnalyzer:
    """Comprehensive statistical analysis for MLB teams with 3-layer framework."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.composite_model = None
        self.matchup_model = None
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all teams with complete 3-layer analysis.
        
        Returns:
            DataFrame with team, city, roster, and composite data
        """
        query = db.session.query(MLBTeam, MLBTeamAnalysis).join(
            MLBTeamAnalysis,
            MLBTeam.id == MLBTeamAnalysis.team_id
        )
        
        rows = []
        for team, analysis in query.all():
            try:
                row = {
                    # Team metadata
                    'team_id': team.id,
                    'team_name': team.name,
                    'full_name': team.full_name,
                    'city': team.city,
                    'league': team.league,
                    'division': team.division,
                    
                    # Performance (outcomes)
                    'wins': team.wins_season or 0,
                    'losses': team.losses_season or 0,
                    'win_percentage': team.win_percentage or 0,
                    'world_series_titles': team.world_series_titles or 0,
                    'playoff_appearances': team.playoff_appearances or 0,
                    
                    # Layer 1: Team name
                    'team_name_syllables': analysis.team_name_syllables or 0,
                    'team_name_memorability': analysis.team_name_memorability or 50,
                    'team_name_power_score': analysis.team_name_power_score or 50,
                    'team_name_prestige': analysis.team_name_prestige or 70,
                    'team_name_type': analysis.team_name_type or 'Other',
                    
                    # Layer 2: City
                    'city_syllables': analysis.city_syllables or 0,
                    'city_prestige_score': analysis.city_prestige_score or 60,
                    'city_memorability': analysis.city_memorability or 50,
                    'city_market_tier': analysis.city_market_tier or 'Mid',
                    
                    # Layer 3: Roster
                    'roster_size': analysis.roster_size or 0,
                    'roster_mean_syllables': analysis.roster_mean_syllables or 3.0,
                    'roster_mean_harshness': analysis.roster_mean_harshness or 50,
                    'roster_mean_memorability': analysis.roster_mean_memorability or 50,
                    'roster_harmony_score': analysis.roster_harmony_score or 75,
                    'roster_international_percentage': analysis.roster_international_percentage or 35,
                    'roster_syllable_stddev': analysis.roster_syllable_stddev or 0.5,
                    
                    # Composite
                    'composite_linguistic_score': analysis.composite_linguistic_score or 60,
                    'composite_memorability': analysis.composite_memorability or 50,
                    'composite_prestige': analysis.composite_prestige or 60,
                    'composite_harmony': analysis.composite_harmony or 75,
                }
                
                rows.append(row)
            except Exception as e:
                logger.warning(f"Error loading team {team.full_name}: {e}")
                continue
        
        df = pd.DataFrame(rows)
        logger.info(f"Loaded {len(df)} MLB teams for analysis")
        return df
    
    def run_full_analysis(self) -> Dict:
        """Execute all 6 analysis modules.
        
        Returns:
            Dict with comprehensive results
        """
        logger.info("=== MLB TEAM STATISTICAL ANALYSIS ===")
        
        df = self.get_comprehensive_dataset()
        
        if len(df) < 10:
            logger.error("Insufficient data for analysis (need 10+ teams)")
            return {'error': 'Insufficient data', 'sample_size': len(df)}
        
        results = {}
        
        # Analysis 1: Team Name Analysis
        logger.info("\n1. Team name analysis...")
        results['team_names'] = self.analyze_team_names(df)
        
        # Analysis 2: City Analysis
        logger.info("\n2. City prestige analysis...")
        results['cities'] = self.analyze_cities(df)
        
        # Analysis 3: Roster Amalgamation
        logger.info("\n3. Roster amalgamation analysis...")
        results['rosters'] = self.analyze_rosters(df)
        
        # Analysis 4: Composite Score Prediction
        logger.info("\n4. Composite score prediction...")
        results['composite_prediction'] = self.predict_from_composite(df)
        
        # Analysis 5: Layer Importance
        logger.info("\n5. Layer importance analysis...")
        results['layer_importance'] = self.analyze_layer_importance(df)
        
        # Analysis 6: Team Rankings
        logger.info("\n6. Team rankings...")
        results['rankings'] = self.rank_teams(df)
        
        results['sample_size'] = len(df)
        results['timestamp'] = datetime.now().isoformat()
        
        logger.info("\n=== ANALYSIS COMPLETE ===")
        return results
    
    def analyze_team_names(self, df: pd.DataFrame) -> Dict:
        """Analyze team name characteristics and correlations.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with team name analysis
        """
        # By type
        by_type = {}
        for name_type in df['team_name_type'].unique():
            type_df = df[df['team_name_type'] == name_type]
            if len(type_df) >= 2:
                by_type[name_type] = {
                    'count': len(type_df),
                    'mean_win_pct': float(type_df['win_percentage'].mean()),
                    'mean_memorability': float(type_df['team_name_memorability'].mean()),
                    'ws_titles': int(type_df['world_series_titles'].sum())
                }
        
        # Correlation with success
        if len(df) >= 15 and df['win_percentage'].std() > 0:
            r_mem, p_mem = stats.pearsonr(df['team_name_memorability'], df['win_percentage'])
            r_power, p_power = stats.pearsonr(df['team_name_power_score'], df['win_percentage'])
            
            correlations = {
                'memorability_win_pct': {'r': float(r_mem), 'p': float(p_mem)},
                'power_win_pct': {'r': float(r_power), 'p': float(p_power)}
            }
        else:
            correlations = {}
        
        return {
            'by_type': by_type,
            'correlations': correlations,
            'mean_syllables': float(df['team_name_syllables'].mean())
        }
    
    def analyze_cities(self, df: pd.DataFrame) -> Dict:
        """Analyze city prestige hierarchy and impact on success.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with city analysis
        """
        # Test city prestige hypothesis
        if len(df) >= 15 and df['win_percentage'].std() > 0:
            r, p_value = stats.pearsonr(df['city_prestige_score'], df['win_percentage'])
            
            # Compare tiers
            major_markets = df[df['city_market_tier'] == 'Major']
            small_markets = df[df['city_market_tier'] == 'Small']
            
            if len(major_markets) >= 3 and len(small_markets) >= 3:
                t_stat, p_tier = stats.ttest_ind(major_markets['win_percentage'], 
                                                 small_markets['win_percentage'])
                tier_difference = major_markets['win_percentage'].mean() - small_markets['win_percentage'].mean()
            else:
                p_tier = 1.0
                tier_difference = 0.0
        else:
            r, p_value = 0, 1.0
            p_tier = 1.0
            tier_difference = 0.0
        
        return {
            'city_prestige_correlation': {'r': float(r), 'p': float(p_value)},
            'market_tier_effect': {
                'major_vs_small_difference': float(tier_difference),
                'p_value': float(p_tier)
            },
            'top_prestige_cities': df.nlargest(5, 'city_prestige_score')[['city', 'city_prestige_score']].to_dict('records')
        }
    
    def analyze_rosters(self, df: pd.DataFrame) -> Dict:
        """Analyze roster amalgamation effects.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with roster analysis
        """
        results = {}
        
        # Roster harmony hypothesis
        if len(df) >= 15 and df['win_percentage'].std() > 0:
            r_harmony, p_harmony = stats.pearsonr(df['roster_harmony_score'], df['win_percentage'])
            r_intl, p_intl = stats.pearsonr(df['roster_international_percentage'], df['win_percentage'])
            
            results['harmony_correlation'] = {'r': float(r_harmony), 'p': float(p_harmony)}
            results['international_correlation'] = {'r': float(r_intl), 'p': float(p_intl)}
        
        # Summary statistics
        results['mean_roster_harmony'] = float(df['roster_harmony_score'].mean())
        results['mean_international_pct'] = float(df['roster_international_percentage'].mean())
        results['top_harmony_teams'] = df.nlargest(5, 'roster_harmony_score')[['full_name', 'roster_harmony_score']].to_dict('records')
        
        return results
    
    def predict_from_composite(self, df: pd.DataFrame) -> Dict:
        """Predict win percentage from composite linguistic score.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with prediction results
        """
        if len(df) < 15:
            return {'error': 'Insufficient data'}
        
        # Simple correlation
        r, p_value = stats.pearsonr(df['composite_linguistic_score'], df['win_percentage'])
        
        # Multiple regression (team + city + roster components)
        feature_cols = [
            'team_name_memorability', 'team_name_prestige',
            'city_prestige_score',
            'roster_mean_memorability', 'roster_harmony_score'
        ]
        
        X = df[feature_cols].fillna(50)
        y = df['win_percentage']
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        
        # Feature importance
        importances = dict(zip(feature_cols, model.feature_importances_))
        
        self.composite_model = model
        
        return {
            'composite_correlation': {'r': float(r), 'p': float(p_value)},
            'model_r2': float(r2),
            'feature_importance': {k: float(v) for k, v in sorted(importances.items(), key=lambda x: x[1], reverse=True)},
            'n_test': len(X_test)
        }
    
    def analyze_layer_importance(self, df: pd.DataFrame) -> Dict:
        """Determine which layer (team/city/roster) matters most.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with layer importance analysis
        """
        if len(df) < 15:
            return {'error': 'Insufficient data'}
        
        results = {}
        
        # Correlate each layer with win percentage
        layers = {
            'team_name': 'team_name_memorability',
            'city': 'city_prestige_score',
            'roster': 'roster_mean_memorability',
            'composite': 'composite_linguistic_score'
        }
        
        for layer_name, feature in layers.items():
            if df[feature].std() > 0:
                r, p = stats.pearsonr(df[feature], df['win_percentage'])
                results[f'{layer_name}_correlation'] = {
                    'r': float(r),
                    'p': float(p),
                    'r_squared': float(r**2)
                }
        
        return results
    
    def rank_teams(self, df: pd.DataFrame) -> Dict:
        """Rank teams by various metrics.
        
        Args:
            df: Complete dataset
        
        Returns:
            Dict with team rankings
        """
        rankings = {}
        
        # By composite score
        rankings['by_composite'] = df.nlargest(10, 'composite_linguistic_score')[
            ['full_name', 'composite_linguistic_score', 'win_percentage']
        ].to_dict('records')
        
        # By city prestige
        rankings['by_city_prestige'] = df.nlargest(10, 'city_prestige_score')[
            ['full_name', 'city_prestige_score', 'win_percentage']
        ].to_dict('records')
        
        # By roster harmony
        rankings['by_roster_harmony'] = df.nlargest(10, 'roster_harmony_score')[
            ['full_name', 'roster_harmony_score', 'win_percentage']
        ].to_dict('records')
        
        # Most international rosters
        rankings['most_international'] = df.nlargest(10, 'roster_international_percentage')[
            ['full_name', 'roster_international_percentage', 'win_percentage']
        ].to_dict('records')
        
        return rankings
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report.
        
        Returns:
            Dict with complete analysis
        """
        df = self.get_comprehensive_dataset()
        
        if len(df) < 5:
            return {'error': 'Insufficient data', 'sample_size': len(df)}
        
        report = {
            'sample_size': len(df),
            'full_analysis': self.run_full_analysis(),
            'generated_at': datetime.now().isoformat()
        }
        
        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = MLBTeamStatisticalAnalyzer()
    report = analyzer.generate_summary_report()
    print(f"Analysis complete: {report.get('sample_size', 0)} teams")


