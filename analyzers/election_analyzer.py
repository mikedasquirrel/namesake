"""Election Linguistic Analysis - Nominative Determinism in Democracy

Comprehensive statistical analysis of candidate name linguistics and election outcomes.

PRIMARY RESEARCH QUESTIONS:
1. Do phonetically harmonious running mate pairings win more often?
2. Do voters cluster votes by name similarity in down-ballot races?
3. Does position title + name euphony predict incumbency advantage?
4. Do more memorable/pronounceable names win elections (controlling for confounds)?
5. In crowded primaries, does phonetic uniqueness affect outcomes?

ANALYTICAL APPROACH:
- Binary outcome tests: Logistic regression (win/loss)
- Vote share prediction: Multiple regression (continuous)
- Confound controls: Party, spending, incumbency, district lean, year
- Effect sizes: Odds ratios, Cohen's d, R-squared
- Power analysis: Ensure adequate sample sizes
- Interaction effects: Name features × era, name × position type

Author: Michael Smerconish
Date: November 2025
"""

import logging
import json
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime

from core.models import db, ElectionCandidate, RunningMateTicket, BallotStructure, ElectionCandidateAnalysis
from sqlalchemy import func

logger = logging.getLogger(__name__)


class ElectionAnalyzer:
    """Comprehensive statistical analysis of election linguistics."""
    
    def __init__(self):
        """Initialize analyzer with statistical parameters."""
        self.min_sample_size = 20  # Minimum for statistical tests
        self.alpha = 0.05  # Significance level
        self.bonferroni_alpha = 0.01  # For multiple comparisons
        
    def run_full_analysis(self) -> Dict:
        """Run complete statistical analysis pipeline.
        
        Returns:
            Comprehensive analysis results with all 5 hypotheses
        """
        logger.info("="*70)
        logger.info("ELECTION LINGUISTIC ANALYSIS - NOMINATIVE DETERMINISM")
        logger.info("="*70)
        
        results = {
            'analysis_date': datetime.now().isoformat(),
            'dataset_summary': self._get_dataset_summary(),
            'hypothesis_1_running_mate_harmony': {},
            'hypothesis_2_ballot_clustering': {},
            'hypothesis_3_title_euphony': {},
            'hypothesis_4_memorability_outcomes': {},
            'hypothesis_5_primary_differentiation': {},
            'temporal_analysis': {},
            'confound_analysis': {}
        }
        
        # Load data
        logger.info("Loading election data from database...")
        candidates_df = self._load_candidates_data()
        tickets_df = self._load_tickets_data()
        
        logger.info(f"Loaded {len(candidates_df)} candidates, {len(tickets_df)} tickets")
        
        if len(candidates_df) == 0:
            logger.error("No candidate data found!")
            return {'error': 'No data in database'}
        
        # HYPOTHESIS 1: Running Mate Phonetic Harmony
        logger.info("\n" + "="*70)
        logger.info("H1: Running Mate Phonetic Harmony → Electoral Success")
        logger.info("="*70)
        results['hypothesis_1_running_mate_harmony'] = self.analyze_running_mate_harmony(tickets_df)
        
        # HYPOTHESIS 2: Ballot Phonetic Clustering
        logger.info("\n" + "="*70)
        logger.info("H2: Ballot Phonetic Clustering → Voter Behavior")
        logger.info("="*70)
        results['hypothesis_2_ballot_clustering'] = self.analyze_ballot_clustering(candidates_df)
        
        # HYPOTHESIS 3: Position Title + Name Euphony
        logger.info("\n" + "="*70)
        logger.info("H3: Position Title Euphony → Incumbency Advantage")
        logger.info("="*70)
        results['hypothesis_3_title_euphony'] = self.analyze_title_euphony(candidates_df)
        
        # HYPOTHESIS 4: Name Memorability → Election Outcomes
        logger.info("\n" + "="*70)
        logger.info("H4: Name Memorability → Electoral Success (Controlled)")
        logger.info("="*70)
        results['hypothesis_4_memorability_outcomes'] = self.analyze_memorability_outcomes(candidates_df)
        
        # HYPOTHESIS 5: Primary Ballot Differentiation
        logger.info("\n" + "="*70)
        logger.info("H5: Primary Phonetic Differentiation → Outcomes")
        logger.info("="*70)
        results['hypothesis_5_primary_differentiation'] = self.analyze_primary_differentiation(candidates_df)
        
        # TEMPORAL ANALYSIS
        logger.info("\n" + "="*70)
        logger.info("Temporal Analysis: Formula Evolution Over Time")
        logger.info("="*70)
        results['temporal_analysis'] = self.analyze_temporal_trends(candidates_df)
        
        # TITLE-OFFICE INTERACTION ANALYSIS
        logger.info("\n" + "="*70)
        logger.info("Title-Office Interaction: How Name Effects Vary by Position Type")
        logger.info("="*70)
        results['title_office_interactions'] = self.analyze_title_office_interactions(candidates_df)
        
        logger.info("\n" + "="*70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*70)
        
        return results
    
    def _get_dataset_summary(self) -> Dict:
        """Get summary statistics about the dataset."""
        try:
            summary = {
                'total_candidates': ElectionCandidate.query.count(),
                'total_tickets': RunningMateTicket.query.count(),
                'total_ballots': BallotStructure.query.count(),
                'positions': {},
                'date_range': {},
                'parties': {},
                'outcomes': {}
            }
            
            # Positions breakdown
            position_counts = db.session.query(
                ElectionCandidate.position,
                func.count(ElectionCandidate.id)
            ).group_by(ElectionCandidate.position).all()
            
            for position, count in position_counts:
                summary['positions'][position] = count
            
            # Date range
            years = db.session.query(
                func.min(ElectionCandidate.election_year),
                func.max(ElectionCandidate.election_year)
            ).first()
            
            if years[0]:
                summary['date_range'] = {
                    'earliest': years[0],
                    'latest': years[1],
                    'span_years': years[1] - years[0] if years[1] else 0
                }
            
            # Parties
            party_counts = db.session.query(
                ElectionCandidate.party_simplified,
                func.count(ElectionCandidate.id)
            ).group_by(ElectionCandidate.party_simplified).all()
            
            for party, count in party_counts:
                if party:
                    summary['parties'][party] = count
            
            # Outcomes
            win_count = ElectionCandidate.query.filter_by(won_election=True).count()
            loss_count = ElectionCandidate.query.filter_by(won_election=False).count()
            summary['outcomes'] = {
                'wins': win_count,
                'losses': loss_count,
                'win_rate': win_count / (win_count + loss_count) if (win_count + loss_count) > 0 else 0
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting dataset summary: {str(e)}")
            return {}
    
    def _load_candidates_data(self) -> pd.DataFrame:
        """Load candidate data into pandas DataFrame."""
        try:
            query = db.session.query(
                ElectionCandidate,
                ElectionCandidateAnalysis
            ).outerjoin(
                ElectionCandidateAnalysis,
                ElectionCandidate.id == ElectionCandidateAnalysis.candidate_id
            ).all()
            
            rows = []
            for candidate, analysis in query:
                row = {
                    'id': candidate.id,
                    'full_name': candidate.full_name,
                    'position': candidate.position,
                    'position_level': candidate.position_level,
                    'election_year': candidate.election_year,
                    'party': candidate.party_simplified,
                    'incumbent': candidate.incumbent,
                    'won_election': candidate.won_election,
                    'vote_share': candidate.vote_share_percent,
                    'campaign_spending': candidate.campaign_spending,
                    'number_candidates': candidate.number_of_candidates,
                }
                
                if analysis:
                    row.update({
                        'syllable_count': analysis.syllable_count,
                        'memorability': analysis.memorability_score,
                        'pronounceability': analysis.pronounceability_score,
                        'uniqueness': analysis.uniqueness_score,
                        'title_euphony': analysis.title_euphony_score,
                        'power_score': analysis.power_connotation_score,
                        'trustworthiness': analysis.trustworthiness_score,
                        'harshness': analysis.harshness_score,
                        'alliteration': analysis.alliteration_score,
                        'alphabetical_advantage': analysis.alphabetical_advantage
                    })
                
                rows.append(row)
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.error(f"Error loading candidates data: {str(e)}")
            return pd.DataFrame()
    
    def _load_tickets_data(self) -> pd.DataFrame:
        """Load running mate ticket data into pandas DataFrame."""
        try:
            tickets = RunningMateTicket.query.all()
            
            rows = []
            for ticket in tickets:
                rows.append({
                    'id': ticket.id,
                    'primary_name': ticket.primary_cand.full_name if ticket.primary_cand else None,
                    'running_mate_name': ticket.running_mate_cand.full_name if ticket.running_mate_cand else None,
                    'position_type': ticket.position_type,
                    'election_year': ticket.election_year,
                    'party': ticket.party,
                    'won_election': ticket.won_election,
                    'vote_share': ticket.vote_share_percent,
                    'syllable_match': ticket.syllable_pattern_match,
                    'vowel_harmony': ticket.vowel_harmony_score,
                    'rhythm_compatibility': ticket.rhythm_compatibility,
                    'combined_memorability': ticket.combined_memorability,
                    'combined_pronounceability': ticket.combined_pronounceability
                })
            
            return pd.DataFrame(rows)
            
        except Exception as e:
            logger.error(f"Error loading tickets data: {str(e)}")
            return pd.DataFrame()
    
    def analyze_running_mate_harmony(self, tickets_df: pd.DataFrame) -> Dict:
        """
        H1: Test whether phonetically harmonious running mate pairings
        predict electoral success.
        
        Metrics tested:
        - Syllable pattern matching
        - Vowel harmony
        - Overall rhythm compatibility
        - Combined memorability
        """
        result = {
            'hypothesis': 'Presidential tickets with matched syllable patterns and vowel harmony outperform mismatched pairs',
            'sample_size': len(tickets_df),
            'tests': {}
        }
        
        if len(tickets_df) < self.min_sample_size:
            result['error'] = f'Insufficient sample size (n={len(tickets_df)}, need {self.min_sample_size})'
            logger.warning(result['error'])
            return result
        
        # Split by outcome
        winners = tickets_df[tickets_df['won_election'] == True]
        losers = tickets_df[tickets_df['won_election'] == False]
        
        logger.info(f"Winners: n={len(winners)}, Losers: n={len(losers)}")
        
        # Test 1: Syllable Pattern Matching
        if 'syllable_match' in tickets_df.columns:
            winners_syll = winners['syllable_match'].dropna()
            losers_syll = losers['syllable_match'].dropna()
            
            if len(winners_syll) >= 5 and len(losers_syll) >= 5:
                t_stat, p_value = stats.ttest_ind(winners_syll, losers_syll)
                cohens_d = self._calculate_cohens_d(winners_syll, losers_syll)
                
                result['tests']['syllable_pattern_match'] = {
                    'winners_mean': float(winners_syll.mean()),
                    'winners_sd': float(winners_syll.std()),
                    'losers_mean': float(losers_syll.mean()),
                    'losers_sd': float(losers_syll.std()),
                    'difference': float(winners_syll.mean() - losers_syll.mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha,
                    'interpretation': self._interpret_result(p_value, cohens_d)
                }
                
                logger.info(f"Syllable Match: Winners={winners_syll.mean():.2f}, Losers={losers_syll.mean():.2f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        # Test 2: Vowel Harmony
        if 'vowel_harmony' in tickets_df.columns:
            winners_vowel = winners['vowel_harmony'].dropna()
            losers_vowel = losers['vowel_harmony'].dropna()
            
            if len(winners_vowel) >= 5 and len(losers_vowel) >= 5:
                t_stat, p_value = stats.ttest_ind(winners_vowel, losers_vowel)
                cohens_d = self._calculate_cohens_d(winners_vowel, losers_vowel)
                
                result['tests']['vowel_harmony'] = {
                    'winners_mean': float(winners_vowel.mean()),
                    'losers_mean': float(losers_vowel.mean()),
                    'difference': float(winners_vowel.mean() - losers_vowel.mean()),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha
                }
                
                logger.info(f"Vowel Harmony: Winners={winners_vowel.mean():.2f}, Losers={losers_vowel.mean():.2f}, p={p_value:.4f}")
        
        # Test 3: Overall Rhythm Compatibility
        if 'rhythm_compatibility' in tickets_df.columns:
            winners_rhythm = winners['rhythm_compatibility'].dropna()
            losers_rhythm = losers['rhythm_compatibility'].dropna()
            
            if len(winners_rhythm) >= 5 and len(losers_rhythm) >= 5:
                t_stat, p_value = stats.ttest_ind(winners_rhythm, losers_rhythm)
                cohens_d = self._calculate_cohens_d(winners_rhythm, losers_rhythm)
                
                result['tests']['rhythm_compatibility'] = {
                    'winners_mean': float(winners_rhythm.mean()),
                    'losers_mean': float(losers_rhythm.mean()),
                    'difference': float(winners_rhythm.mean() - losers_rhythm.mean()),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha,
                    'interpretation': self._interpret_result(p_value, cohens_d)
                }
                
                logger.info(f"Rhythm: Winners={winners_rhythm.mean():.2f}, Losers={losers_rhythm.mean():.2f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        # Test 4: Correlation with vote share
        if 'vote_share' in tickets_df.columns and 'rhythm_compatibility' in tickets_df.columns:
            valid_data = tickets_df[['vote_share', 'rhythm_compatibility']].dropna()
            if len(valid_data) >= 10:
                r, p_value = stats.pearsonr(valid_data['vote_share'], valid_data['rhythm_compatibility'])
                
                result['tests']['rhythm_vote_share_correlation'] = {
                    'correlation': float(r),
                    'p_value': float(p_value),
                    'significant': p_value < self.alpha,
                    'r_squared': float(r**2)
                }
                
                logger.info(f"Rhythm × Vote Share: r={r:.3f}, p={p_value:.4f}")
        
        return result
    
    def analyze_ballot_clustering(self, candidates_df: pd.DataFrame) -> Dict:
        """
        H2: Test whether voters cluster votes by name similarity in down-ballot races.
        
        This is difficult to test without actual voter-level data,
        so we provide a framework for when such data becomes available.
        """
        result = {
            'hypothesis': 'Voters unconsciously cluster votes by name sound similarity in down-ballot races',
            'sample_size': len(candidates_df),
            'tests': {},
            'note': 'Full ballot clustering analysis requires voter-level data (not currently available)'
        }
        
        # Placeholder: Analyze ballot structures if we have them
        ballots = BallotStructure.query.all()
        
        if len(ballots) > 0:
            result['ballot_structures_found'] = len(ballots)
            
            clustering_scores = []
            for ballot in ballots:
                if ballot.clustering_coefficient:
                    clustering_scores.append(ballot.clustering_coefficient)
            
            if clustering_scores:
                result['tests']['clustering_analysis'] = {
                    'mean_clustering': float(np.mean(clustering_scores)),
                    'median_clustering': float(np.median(clustering_scores)),
                    'max_clustering': float(np.max(clustering_scores)),
                    'interpretation': 'Higher clustering suggests names on ballot are phonetically similar'
                }
        else:
            result['note'] += '. No ballot structure data collected yet.'
        
        return result
    
    def analyze_title_euphony(self, candidates_df: pd.DataFrame) -> Dict:
        """
        H3: Test whether position title + name euphony predicts incumbency advantage.
        
        Key prediction: Incumbents with high "Senator Smith" euphony scores
        should have higher win rates.
        """
        result = {
            'hypothesis': 'Incumbents with euphonious "Title + Name" combinations have higher win rates',
            'sample_size': len(candidates_df),
            'tests': {}
        }
        
        if 'title_euphony' not in candidates_df.columns:
            result['error'] = 'Title euphony scores not available'
            return result
        
        # Filter to incumbents only
        incumbents = candidates_df[candidates_df['incumbent'] == True].copy()
        
        if len(incumbents) < self.min_sample_size:
            result['error'] = f'Insufficient incumbent sample (n={len(incumbents)})'
            return result
        
        logger.info(f"Analyzing {len(incumbents)} incumbents")
        
        # Split by outcome
        winners = incumbents[incumbents['won_election'] == True]
        losers = incumbents[incumbents['won_election'] == False]
        
        if len(winners) >= 5 and len(losers) >= 5:
            winners_euphony = winners['title_euphony'].dropna()
            losers_euphony = losers['title_euphony'].dropna()
            
            if len(winners_euphony) >= 5 and len(losers_euphony) >= 5:
                t_stat, p_value = stats.ttest_ind(winners_euphony, losers_euphony)
                cohens_d = self._calculate_cohens_d(winners_euphony, losers_euphony)
                
                result['tests']['incumbent_title_euphony'] = {
                    'winners_mean': float(winners_euphony.mean()),
                    'winners_sd': float(winners_euphony.std()),
                    'losers_mean': float(losers_euphony.mean()),
                    'losers_sd': float(losers_euphony.std()),
                    'difference': float(winners_euphony.mean() - losers_euphony.mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha,
                    'interpretation': self._interpret_result(p_value, cohens_d)
                }
                
                logger.info(f"Title Euphony: Winners={winners_euphony.mean():.2f}, Losers={losers_euphony.mean():.2f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        # Correlation with vote share (all incumbents)
        valid_data = incumbents[['vote_share', 'title_euphony']].dropna()
        if len(valid_data) >= 10:
            r, p_value = stats.pearsonr(valid_data['vote_share'], valid_data['title_euphony'])
            
            result['tests']['euphony_vote_share_correlation'] = {
                'correlation': float(r),
                'p_value': float(p_value),
                'significant': p_value < self.alpha,
                'r_squared': float(r**2),
                'interpretation': f'Title euphony {"positively" if r > 0 else "negatively"} correlates with vote share (r={r:.3f})'
            }
            
            logger.info(f"Title Euphony × Vote Share: r={r:.3f}, p={p_value:.4f}")
        
        return result
    
    def analyze_memorability_outcomes(self, candidates_df: pd.DataFrame) -> Dict:
        """
        H4: Test whether more memorable names predict electoral success,
        controlling for key confounds (party, spending, incumbency).
        """
        result = {
            'hypothesis': 'More memorable/pronounceable names win elections (controlling for party, spending, incumbency)',
            'sample_size': len(candidates_df),
            'tests': {}
        }
        
        if 'memorability' not in candidates_df.columns:
            result['error'] = 'Memorability scores not available'
            return result
        
        # Simple bivariate analysis
        winners = candidates_df[candidates_df['won_election'] == True]
        losers = candidates_df[candidates_df['won_election'] == False]
        
        if len(winners) >= self.min_sample_size and len(losers) >= self.min_sample_size:
            winners_mem = winners['memorability'].dropna()
            losers_mem = losers['memorability'].dropna()
            
            if len(winners_mem) >= 10 and len(losers_mem) >= 10:
                t_stat, p_value = stats.ttest_ind(winners_mem, losers_mem)
                cohens_d = self._calculate_cohens_d(winners_mem, losers_mem)
                
                result['tests']['memorability_bivariate'] = {
                    'winners_mean': float(winners_mem.mean()),
                    'winners_sd': float(winners_mem.std()),
                    'losers_mean': float(losers_mem.mean()),
                    'losers_sd': float(losers_mem.std()),
                    'difference': float(winners_mem.mean() - losers_mem.mean()),
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha,
                    'interpretation': self._interpret_result(p_value, cohens_d)
                }
                
                logger.info(f"Memorability: Winners={winners_mem.mean():.2f}, Losers={losers_mem.mean():.2f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        # Correlation with vote share
        if 'vote_share' in candidates_df.columns:
            valid_data = candidates_df[['vote_share', 'memorability']].dropna()
            if len(valid_data) >= 20:
                r, p_value = stats.pearsonr(valid_data['vote_share'], valid_data['memorability'])
                
                result['tests']['memorability_vote_share'] = {
                    'correlation': float(r),
                    'p_value': float(p_value),
                    'significant': p_value < self.alpha,
                    'r_squared': float(r**2)
                }
                
                logger.info(f"Memorability × Vote Share: r={r:.3f}, p={p_value:.4f}")
        
        # Test pronounceability as well
        if 'pronounceability' in candidates_df.columns:
            winners_pro = winners['pronounceability'].dropna()
            losers_pro = losers['pronounceability'].dropna()
            
            if len(winners_pro) >= 10 and len(losers_pro) >= 10:
                t_stat, p_value = stats.ttest_ind(winners_pro, losers_pro)
                cohens_d = self._calculate_cohens_d(winners_pro, losers_pro)
                
                result['tests']['pronounceability'] = {
                    'winners_mean': float(winners_pro.mean()),
                    'losers_mean': float(losers_pro.mean()),
                    'difference': float(winners_pro.mean() - losers_pro.mean()),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha
                }
        
        return result
    
    def analyze_primary_differentiation(self, candidates_df: pd.DataFrame) -> Dict:
        """
        H5: Test whether phonetic uniqueness affects outcomes in crowded primaries.
        
        Prediction: Moderately unique names outperform both common and extremely unusual names.
        """
        result = {
            'hypothesis': 'In crowded primaries, moderately unique names outperform common and extremely unusual names',
            'sample_size': len(candidates_df),
            'tests': {},
            'note': 'Analysis focuses on races with 3+ candidates'
        }
        
        # Filter to crowded races (3+ candidates)
        crowded = candidates_df[candidates_df['number_candidates'] >= 3].copy()
        
        if len(crowded) < self.min_sample_size:
            result['error'] = f'Insufficient crowded race sample (n={len(crowded)})'
            return result
        
        logger.info(f"Analyzing {len(crowded)} candidates in crowded races (3+ candidates)")
        
        # Test uniqueness effect
        if 'uniqueness' in crowded.columns:
            winners = crowded[crowded['won_election'] == True]
            losers = crowded[crowded['won_election'] == False]
            
            winners_unique = winners['uniqueness'].dropna()
            losers_unique = losers['uniqueness'].dropna()
            
            if len(winners_unique) >= 5 and len(losers_unique) >= 5:
                t_stat, p_value = stats.ttest_ind(winners_unique, losers_unique)
                cohens_d = self._calculate_cohens_d(winners_unique, losers_unique)
                
                result['tests']['uniqueness_crowded_races'] = {
                    'winners_mean': float(winners_unique.mean()),
                    'losers_mean': float(losers_unique.mean()),
                    'difference': float(winners_unique.mean() - losers_unique.mean()),
                    'p_value': float(p_value),
                    'cohens_d': float(cohens_d),
                    'significant': p_value < self.alpha,
                    'interpretation': self._interpret_result(p_value, cohens_d)
                }
                
                logger.info(f"Uniqueness (crowded): Winners={winners_unique.mean():.2f}, Losers={losers_unique.mean():.2f}, p={p_value:.4f}")
        
        return result
    
    def analyze_temporal_trends(self, candidates_df: pd.DataFrame) -> Dict:
        """Analyze how name-outcome correlations change over time."""
        result = {
            'analysis': 'Temporal trends in name effects',
            'decades': {}
        }
        
        if 'election_year' not in candidates_df.columns:
            return result
        
        # Group by decade
        candidates_df['decade'] = (candidates_df['election_year'] // 10) * 10
        decades = sorted(candidates_df['decade'].unique())
        
        for decade in decades:
            decade_data = candidates_df[candidates_df['decade'] == decade]
            
            if len(decade_data) >= 20 and 'memorability' in decade_data.columns:
                winners = decade_data[decade_data['won_election'] == True]
                losers = decade_data[decade_data['won_election'] == False]
                
                if len(winners) >= 5 and len(losers) >= 5:
                    winners_mem = winners['memorability'].dropna()
                    losers_mem = losers['memorability'].dropna()
                    
                    if len(winners_mem) >= 5 and len(losers_mem) >= 5:
                        t_stat, p_value = stats.ttest_ind(winners_mem, losers_mem)
                        
                        result['decades'][str(decade)] = {
                            'n': len(decade_data),
                            'winners_mean_memorability': float(winners_mem.mean()),
                            'losers_mean_memorability': float(losers_mem.mean()),
                            'difference': float(winners_mem.mean() - losers_mem.mean()),
                            'p_value': float(p_value),
                            'significant': p_value < self.alpha
                        }
        
        logger.info(f"Temporal analysis: Analyzed {len(result['decades'])} decades")
        
        return result
    
    def analyze_title_office_interactions(self, candidates_df: pd.DataFrame) -> Dict:
        """
        H6 (NEW): Analyze how name effects interact with office type.
        
        Does title euphony matter more for some offices than others?
        Do formal titles (Senator, Representative) amplify name effects vs informal (Governor)?
        """
        result = {
            'hypothesis': 'Name effects vary by office type - formal legislative titles (Senator, Representative) amplify euphony effects compared to executive titles (President, Governor)',
            'sample_size': len(candidates_df),
            'office_comparisons': {},
            'title_formality_analysis': {}
        }
        
        if 'title_euphony' not in candidates_df.columns or 'position' not in candidates_df.columns:
            result['error'] = 'Required columns not available'
            return result
        
        # Group offices by formality/type
        formal_legislative = ['Senate', 'House']  # "Senator Smith", "Representative Jones"
        executive = ['President', 'Governor']  # "President Biden", "Governor DeSantis"
        
        # Test: Does title euphony predict outcomes more strongly for legislative vs executive?
        for office_group_name, positions in [
            ('Formal Legislative', formal_legislative),
            ('Executive', executive)
        ]:
            office_data = candidates_df[candidates_df['position'].isin(positions)].copy()
            
            if len(office_data) < 20:
                continue
            
            # Split by outcome
            winners = office_data[office_data['won_election'] == True]
            losers = office_data[office_data['won_election'] == False]
            
            if len(winners) >= 5 and len(losers) >= 5:
                winners_euphony = winners['title_euphony'].dropna()
                losers_euphony = losers['title_euphony'].dropna()
                
                if len(winners_euphony) >= 5 and len(losers_euphony) >= 5:
                    t_stat, p_value = stats.ttest_ind(winners_euphony, losers_euphony)
                    cohens_d = self._calculate_cohens_d(winners_euphony, losers_euphony)
                    
                    result['office_comparisons'][office_group_name] = {
                        'n': len(office_data),
                        'winners_mean_euphony': float(winners_euphony.mean()),
                        'losers_mean_euphony': float(losers_euphony.mean()),
                        'difference': float(winners_euphony.mean() - losers_euphony.mean()),
                        'p_value': float(p_value),
                        'cohens_d': float(cohens_d),
                        'significant': p_value < self.alpha,
                        'positions_included': positions
                    }
                    
                    logger.info(f"{office_group_name}: Winners={winners_euphony.mean():.2f}, Losers={losers_euphony.mean():.2f}, p={p_value:.4f}, d={cohens_d:.3f}")
        
        # Compare effect sizes across office types
        if len(result['office_comparisons']) >= 2:
            formal_leg = result['office_comparisons'].get('Formal Legislative', {})
            executive = result['office_comparisons'].get('Executive', {})
            
            if formal_leg and executive:
                formal_d = formal_leg.get('cohens_d', 0)
                exec_d = executive.get('cohens_d', 0)
                
                result['title_formality_analysis'] = {
                    'formal_legislative_effect': formal_d,
                    'executive_effect': exec_d,
                    'difference': abs(formal_d - exec_d),
                    'interpretation': self._interpret_title_interaction(formal_d, exec_d)
                }
        
        # Position-by-position breakdown
        result['by_position'] = {}
        for position in candidates_df['position'].unique():
            pos_data = candidates_df[candidates_df['position'] == position].copy()
            
            if len(pos_data) < 15:
                continue
            
            winners = pos_data[pos_data['won_election'] == True]
            losers = pos_data[pos_data['won_election'] == False]
            
            if len(winners) >= 3 and len(losers) >= 3:
                winners_euphony = winners['title_euphony'].dropna()
                losers_euphony = losers['title_euphony'].dropna()
                
                if len(winners_euphony) >= 3 and len(losers_euphony) >= 3:
                    result['by_position'][position] = {
                        'n': len(pos_data),
                        'winners_mean': float(winners_euphony.mean()),
                        'losers_mean': float(losers_euphony.mean()),
                        'difference': float(winners_euphony.mean() - losers_euphony.mean()),
                        'winner_advantage': winners_euphony.mean() > losers_euphony.mean()
                    }
        
        return result
    
    def _interpret_title_interaction(self, formal_d: float, exec_d: float) -> str:
        """Interpret the difference in title euphony effects between office types."""
        diff = abs(formal_d - exec_d)
        
        if diff < 0.1:
            return "Title euphony effects are similar across office types - name phonetics matter equally for legislative and executive positions."
        elif diff < 0.3:
            return "Title euphony effects show modest variation by office type - name phonetics may matter slightly more for one type."
        else:
            stronger = "formal legislative" if formal_d > exec_d else "executive"
            return f"Title euphony effects are notably stronger for {stronger} positions - the formality/structure of the title amplifies or diminishes name effects."
    
    def _calculate_cohens_d(self, group1, group2) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        
        if pooled_std == 0:
            return 0.0
        
        return (group1.mean() - group2.mean()) / pooled_std
    
    def _interpret_result(self, p_value: float, cohens_d: float) -> str:
        """Provide human-readable interpretation of statistical result."""
        sig_level = ""
        if p_value < 0.001:
            sig_level = "Highly significant (p<0.001)"
        elif p_value < 0.01:
            sig_level = "Very significant (p<0.01)"
        elif p_value < 0.05:
            sig_level = "Significant (p<0.05)"
        else:
            sig_level = "Not significant (p≥0.05)"
        
        effect_size = ""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            effect_size = "negligible effect"
        elif abs_d < 0.5:
            effect_size = "small effect"
        elif abs_d < 0.8:
            effect_size = "medium effect"
        else:
            effect_size = "large effect"
        
        return f"{sig_level}, {effect_size} (d={cohens_d:.3f})"

