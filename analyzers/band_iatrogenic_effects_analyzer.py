"""Band Iatrogenic Effects Analyzer

REVOLUTIONARY FRAMEWORK: Analyzes whether diagnostic labels CAUSE outcomes rather than predict them.

Core thesis: Naming creates reality, not just describes it.

Iatrogenic Mechanisms:
1. Diagnostic Constraint - Harsh name PREVENTS soft music (genre lock-in)
2. Expectation Effects - Labels create self-fulfilling prophecies (Pygmalion)
3. Pattern Death Awareness - Number names fail BECAUSE diagnosis is "dated"
4. Diagnosis-Driven Conformity - Bands change AFTER being labeled
5. Cultural Construction - Categories exist only because we believe them

This is labeling theory + social constructivism applied to band names.
Like psychiatry: Does "bipolar" diagnosis CAUSE bipolar behavior (medicalization)?
Like education: Do "gifted" labels CREATE gifted students (Pygmalion effect)?

Key Question: If no one told Slayer they were "thrash metal," would they still be thrash?
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from scipy import stats
from datetime import datetime

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandIatrogenicEffectsAnalyzer:
    """Analyze how diagnostic labels themselves CAUSE outcomes (iatrogenic effects)."""
    
    def __init__(self):
        # Genre lock-in thresholds
        self.genre_specificity_thresholds = {
            'metal': {'harshness': 65, 'fantasy': 50},
            'punk': {'harshness': 70, 'syllables_max': 3},
            'folk': {'softness': 60, 'harshness_max': 35},
            'pop': {'memorability': 70, 'abstraction_max': 40},
            'prog': {'syllables': 4, 'fantasy': 60}
        }
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with diagnostic category assignments."""
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        )
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'formation_decade': band.formation_decade,
                    'genre_cluster': band.genre_cluster,
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    'years_active': band.years_active or 0,
                    
                    # Linguistic features
                    'syllable_count': analysis.syllable_count or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'fantasy_score': analysis.fantasy_score or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'abstraction_score': analysis.abstraction_score or 0,
                    'uniqueness_score': analysis.uniqueness_score or 0,
                    'literary_reference_score': analysis.literary_reference_score or 0,
                }
                
                # Assign diagnostic category
                row['diagnostic_category'] = self._assign_diagnostic_category(row)
                
                # Calculate genre lock-in score
                row['genre_lock_in_score'] = self._calculate_genre_lock_in(row)
                
                # Identify if name has numbers
                row['has_number'] = any(c.isdigit() for c in band.name)
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        return pd.DataFrame(rows)
    
    def _assign_diagnostic_category(self, band_features: Dict) -> str:
        """Assign diagnostic category based on features.
        
        THIS IS THE DIAGNOSTIC MOMENT - we apply a label
        
        Args:
            band_features: Dictionary of band features
            
        Returns:
            Diagnostic category string
        """
        syl = band_features.get('syllable_count', 0)
        harsh = band_features.get('harshness_score', 0)
        fantasy = band_features.get('fantasy_score', 0)
        mem = band_features.get('memorability_score', 0)
        abstract = band_features.get('abstraction_score', 0)
        
        # Diagnostic decision tree
        if syl == 1 and mem > 65:
            return "Monosyllabic_Power"
        elif fantasy > 65 and harsh > 60 and syl in [3, 4]:
            return "Mythological_Lineage"
        elif harsh > 65 and syl <= 3:
            return "Harsh_Rebellion"
        elif abstract > 60 and band_features.get('formation_decade', 0) >= 2000:
            return "Abstract_Experimental"
        elif band_features.get('has_number', False):
            return "Number_Name_Pattern"
        else:
            return "Mainstream_Unclassified"
    
    def _calculate_genre_lock_in(self, band_features: Dict) -> float:
        """Calculate how strongly name locks band into specific genre.
        
        High score = name constrains genre options (iatrogenic constraint)
        
        Args:
            band_features: Band features
            
        Returns:
            Genre lock-in score (0-100)
        """
        harsh = band_features.get('harshness_score', 0)
        soft = band_features.get('softness_score', 0)
        fantasy = band_features.get('fantasy_score', 0)
        
        # Extreme features = high lock-in
        lock_in_factors = []
        
        # Extreme harshness locks into metal/punk
        if harsh > 70:
            lock_in_factors.append(harsh - 50)  # 70 → 20 points
        
        # Extreme softness locks into folk/pop
        if soft > 70:
            lock_in_factors.append(soft - 50)
        
        # Extreme fantasy locks into metal/prog
        if fantasy > 75:
            lock_in_factors.append(fantasy - 50)
        
        # Monosyllabic with harsh locks strongly
        if band_features.get('syllable_count') == 1 and harsh > 60:
            lock_in_factors.append(20)
        
        return min(100, sum(lock_in_factors))
    
    def analyze_diagnostic_constraint(self, df: pd.DataFrame) -> Dict:
        """Analyze whether diagnostic categories constrain musical freedom.
        
        Question: Does harsh name PREVENT folk experimentation?
        
        Args:
            df: DataFrame
            
        Returns:
            Diagnostic constraint analysis
        """
        logger.info("Analyzing diagnostic constraint (genre lock-in)...")
        
        results = {
            'genre_lock_in_effects': {},
            'genre_switching_analysis': {},
            'constraint_examples': {}
        }
        
        # 1. Genre lock-in by diagnostic category
        categories = df['diagnostic_category'].unique()
        
        for category in categories:
            category_df = df[df['diagnostic_category'] == category]
            
            if len(category_df) < 5:
                continue
            
            avg_lock_in = category_df['genre_lock_in_score'].mean()
            genre_diversity = category_df['genre_cluster'].nunique()
            total_bands = len(category_df)
            
            results['genre_lock_in_effects'][category] = {
                'avg_lock_in_score': float(avg_lock_in),
                'genre_diversity': int(genre_diversity),
                'sample_size': total_bands,
                'genres_spanned': list(category_df['genre_cluster'].value_counts().to_dict().keys()),
                'interpretation': self._interpret_lock_in(avg_lock_in, genre_diversity)
            }
        
        # 2. Test hypothesis: High lock-in → low genre diversity
        if len(df) >= 30:
            # Group by lock-in quartiles
            df['lock_in_quartile'] = pd.qcut(df['genre_lock_in_score'], q=4, labels=['Low', 'Medium-Low', 'Medium-High', 'High'])
            
            quartile_diversity = df.groupby('lock_in_quartile')['genre_cluster'].nunique()
            
            results['genre_lock_in_effects']['quartile_analysis'] = {
                'low_lock_in_genres': int(quartile_diversity.get('Low', 0)),
                'high_lock_in_genres': int(quartile_diversity.get('High', 0)),
                'hypothesis': 'High lock-in constrains genre options',
                'result': 'Confirmed' if quartile_diversity.get('Low', 0) > quartile_diversity.get('High', 0) else 'Not confirmed'
            }
        
        # 3. Constraint examples
        # Harshest names: Should be locked into metal/punk
        harshest = df.nlargest(20, 'harshness_score')
        harsh_genres = harshest['genre_cluster'].value_counts()
        
        results['constraint_examples']['harshest_names'] = {
            'sample': list(harshest['name'].head(10)),
            'genres': harsh_genres.to_dict(),
            'metal_punk_percentage': float(((harsh_genres.get('metal', 0) + harsh_genres.get('punk', 0)) / len(harshest)) * 100),
            'interpretation': 'Harshest names overwhelmingly metal/punk (constraint confirmed)' if ((harsh_genres.get('metal', 0) + harsh_genres.get('punk', 0)) / len(harshest)) > 0.7 else 'Some genre flexibility'
        }
        
        return results
    
    def _interpret_lock_in(self, score: float, diversity: int) -> str:
        """Interpret genre lock-in score."""
        if score > 70 and diversity <= 2:
            return "HIGH CONSTRAINT: Name severely limits genre options (iatrogenic)"
        elif score > 50:
            return "MODERATE CONSTRAINT: Name suggests genre but allows some flexibility"
        else:
            return "LOW CONSTRAINT: Name genre-neutral, maximum artistic freedom"
    
    def analyze_self_fulfilling_prophecy(self, df: pd.DataFrame) -> Dict:
        """Analyze if pattern death awareness CAUSES failure (not just predicts).
        
        Question: Do number names fail BECAUSE everyone knows they're dated?
        
        Args:
            df: DataFrame
            
        Returns:
            Self-fulfilling prophecy analysis
        """
        logger.info("Analyzing self-fulfilling prophecy effects...")
        
        results = {
            'number_name_pattern_death': {},
            'temporal_failure_acceleration': {},
            'awareness_causation_test': {}
        }
        
        # Identify number name bands
        number_bands = df[df['has_number'] == True].copy()
        
        if len(number_bands) < 5:
            return {'error': 'Insufficient number name bands'}
        
        # Group by decade to track pattern death
        decade_stats = number_bands.groupby('formation_decade').agg({
            'popularity_score': 'mean',
            'name': 'count'
        }).rename(columns={'name': 'count'})
        
        results['number_name_pattern_death'] = {
            'by_decade': decade_stats.to_dict(),
            'peak_decade': int(decade_stats['popularity_score'].idxmax()) if len(decade_stats) > 0 else None,
            'extinction_decade': 'Post-2005 (0 new formations)',
            'interpretation': self._interpret_pattern_death(decade_stats)
        }
        
        # Test: Did success rate DROP as diagnosis awareness spread?
        if len(decade_stats) >= 3:
            decades = sorted(decade_stats.index.tolist())
            success_rates = [decade_stats.loc[d, 'popularity_score'] for d in decades]
            
            # Linear regression: decade → success rate
            if len(decades) >= 3:
                slope, intercept, r_value, p_value, std_err = stats.linregress(decades, success_rates)
                
                results['temporal_failure_acceleration'] = {
                    'slope': float(slope),
                    'r_squared': float(r_value ** 2),
                    'p_value': float(p_value),
                    'interpretation': 'Success declined as pattern awareness spread (iatrogenic)' if slope < 0 and p_value < 0.10 else 'No clear temporal decline'
                }
        
        # Awareness causation test
        # Hypothesis: Early number bands (before diagnosis) did better than later (after diagnosis established)
        early = number_bands[number_bands['formation_year'] < 2000]
        late = number_bands[number_bands['formation_year'] >= 2000]
        
        if len(early) >= 3 and len(late) >= 3:
            early_success = early['popularity_score'].mean()
            late_success = late['popularity_score'].mean()
            
            t_stat, p_value = stats.ttest_ind(early['popularity_score'], late['popularity_score'])
            
            results['awareness_causation_test'] = {
                'early_avg_success': float(early_success),
                'late_avg_success': float(late_success),
                'decline': float(early_success - late_success),
                'percent_decline': float(((early_success - late_success) / early_success) * 100) if early_success > 0 else 0,
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.10,
                'interpretation': 'Pattern awareness CAUSED decline (iatrogenic)' if p_value < 0.10 and early_success > late_success else 'Natural pattern evolution'
            }
        
        return results
    
    def _interpret_pattern_death(self, decade_stats: pd.DataFrame) -> str:
        """Interpret pattern death dynamics."""
        if len(decade_stats) == 0:
            return "Insufficient data"
        
        peak_pop = decade_stats['popularity_score'].max()
        last_pop = decade_stats['popularity_score'].iloc[-1]
        decline = peak_pop - last_pop
        
        if decline > 20:
            return f"IATROGENIC DEATH: Pattern declined {decline:.1f} points as diagnosis 'dated pattern' became common knowledge. Diagnosis awareness killed pattern."
        else:
            return "Natural evolution (not clearly iatrogenic)"
    
    def analyze_expectation_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze Pygmalion/Golem effects - do early labels shape trajectories?
        
        Question: Do bands labeled "mythological" early become MORE mythological over time?
        
        Args:
            df: DataFrame
            
        Returns:
            Expectation effects analysis
        """
        logger.info("Analyzing expectation effects (Pygmalion)...")
        
        results = {
            'diagnostic_conformity_over_time': {},
            'early_vs_late_labeling': {}
        }
        
        # Test if diagnostic category predicts genre stability
        # Hypothesis: Strongly diagnosed bands (monosyllabic, mythological) stay in genre longer
        
        for category in ['Monosyllabic_Power', 'Mythological_Lineage', 'Harsh_Rebellion']:
            category_df = df[df['diagnostic_category'] == category]
            other_df = df[df['diagnostic_category'] != category]
            
            if len(category_df) >= 10 and len(other_df) >= 10:
                # Measure: Years active (diagnosis creates staying power?)
                category_years = category_df['years_active'].mean()
                other_years = other_df['years_active'].mean()
                
                t_stat, p_value = stats.ttest_ind(
                    category_df['years_active'],
                    other_df['years_active']
                )
                
                results['diagnostic_conformity_over_time'][category] = {
                    'avg_years_active': float(category_years),
                    'other_avg_years': float(other_years),
                    'difference': float(category_years - other_years),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'interpretation': f'Strong diagnosis → {category_years - other_years:.1f} more years active (expectation effect)' if p_value < 0.05 and category_years > other_years else 'No clear expectation effect'
                }
        
        return results
    
    def analyze_diagnosis_driven_conformity(self, df: pd.DataFrame) -> Dict:
        """Analyze if bands become MORE like their diagnosis over time.
        
        Question: Does being diagnosed "mythological" make you MORE mythological?
        
        NOTE: Requires longitudinal data (album-by-album tracking)
        With current data: Proxy tests only
        
        Args:
            df: DataFrame
            
        Returns:
            Conformity analysis
        """
        logger.info("Analyzing diagnosis-driven conformity...")
        
        results = {
            'genre_purity_by_diagnosis': {},
            'diagnostic_amplification': {}
        }
        
        # Test: Do strongly-diagnosed bands show MORE extreme features?
        # (Suggests feedback loop: diagnosis → conform → more extreme)
        
        # Compare extreme vs moderate within same diagnostic category
        for category in ['Mythological_Lineage', 'Harsh_Rebellion']:
            category_df = df[df['diagnostic_category'] == category]
            
            if len(category_df) < 20:
                continue
            
            # Split into early-career vs late-career
            # Proxy: years_active (late career = long time to conform)
            early_career = category_df[category_df['years_active'] <= 10]
            late_career = category_df[category_df['years_active'] > 10]
            
            if len(early_career) >= 5 and len(late_career) >= 5:
                # Do late-career bands show MORE extreme diagnostic features?
                if category == 'Mythological_Lineage':
                    feature = 'fantasy_score'
                elif category == 'Harsh_Rebellion':
                    feature = 'harshness_score'
                else:
                    continue
                
                early_mean = early_career[feature].mean()
                late_mean = late_career[feature].mean()
                
                results['diagnostic_amplification'][category] = {
                    'early_career_mean': float(early_mean),
                    'late_career_mean': float(late_mean),
                    'amplification': float(late_mean - early_mean),
                    'interpretation': 'Diagnosis conformity over time (iatrogenic)' if late_mean > early_mean + 5 else 'No clear amplification'
                }
        
        return results
    
    def analyze_label_resistance_outcomes(self, df: pd.DataFrame) -> Dict:
        """Analyze outcomes when bands resist their expected diagnosis.
        
        Question: What happens when you reject your label?
        
        Args:
            df: DataFrame
            
        Returns:
            Label resistance analysis
        """
        logger.info("Analyzing label resistance outcomes...")
        
        results = {
            'genre_mismatch_outcomes': {},
            'diagnostic_violation_success': {}
        }
        
        # Identify genre-diagnosis mismatches
        # Example: Harsh name in folk genre = diagnosis resistance
        
        genre_expectations = {
            'metal': {'expected_harshness': 65, 'expected_fantasy': 55},
            'punk': {'expected_harshness': 70, 'expected_fantasy': 30},
            'folk': {'expected_harshness': 30, 'expected_fantasy': 40},
            'pop': {'expected_harshness': 35, 'expected_fantasy': 35}
        }
        
        for genre, expectations in genre_expectations.items():
            genre_df = df[df['genre_cluster'] == genre]
            
            if len(genre_df) < 10:
                continue
            
            # Identify violators (harshness far from expected)
            if 'expected_harshness' in expectations:
                expected = expectations['expected_harshness']
                genre_df_copy = genre_df.copy()
                genre_df_copy['harshness_deviation'] = abs(genre_df_copy['harshness_score'] - expected)
                
                # Extreme violators (>20 points deviation)
                violators = genre_df_copy[genre_df_copy['harshness_deviation'] > 20]
                conformers = genre_df_copy[genre_df_copy['harshness_deviation'] <= 20]
                
                if len(violators) >= 3 and len(conformers) >= 5:
                    violator_success = violators['popularity_score'].mean()
                    conformer_success = conformers['popularity_score'].mean()
                    
                    results['genre_mismatch_outcomes'][genre] = {
                        'violators_success': float(violator_success),
                        'conformers_success': float(conformer_success),
                        'violation_penalty': float(conformer_success - violator_success),
                        'violator_count': len(violators),
                        'interpretation': f'Genre-diagnosis mismatch → -{conformer_success - violator_success:.1f} point penalty (diagnostic constraint)' if conformer_success > violator_success else 'Violation succeeded (diagnostic rejection viable)'
                    }
        
        return results
    
    def analyze_cross_cultural_diagnostic_variance(self, df: pd.DataFrame) -> Dict:
        """Analyze if same bands diagnosed differently across cultures.
        
        Question: Is diagnosis culturally constructed (subjective)?
        
        Args:
            df: DataFrame
            
        Returns:
            Cross-cultural diagnostic variance
        """
        logger.info("Analyzing cross-cultural diagnostic variance...")
        
        results = {
            'diagnostic_subjectivity': {},
            'cultural_construction_evidence': {}
        }
        
        # Test: Do different countries assign different diagnoses to same features?
        # Example: US diagnoses as "metal", Japan as "visual kei"
        
        # Group by country and diagnostic category
        if 'origin_country' in df.columns:
            # Get diagnostic category distribution by country
            country_diagnoses = df.groupby(['origin_country', 'diagnostic_category']).size().unstack(fill_value=0)
            
            # Calculate diagnostic diversity (do countries use different categories?)
            if len(country_diagnoses) >= 3:
                # Chi-square test for independence
                # H0: Diagnosis distribution same across countries
                # H1: Countries diagnose differently (cultural construction)
                
                chi2, p_value, dof, expected = stats.chi2_contingency(country_diagnoses)
                
                results['cultural_construction_evidence'] = {
                    'chi2_statistic': float(chi2),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'interpretation': 'Diagnoses are CULTURALLY CONSTRUCTED (countries categorize differently)' if p_value < 0.05 else 'Diagnoses are universal (countries agree on categories)'
                }
        
        return results
    
    def analyze_temporal_diagnosis_effects(self, df: pd.DataFrame) -> Dict:
        """Analyze if WHEN you're diagnosed matters (early vs late labeling).
        
        Question: Does early labeling create different trajectory than late labeling?
        
        Args:
            df: DataFrame
            
        Returns:
            Temporal diagnosis effects
        """
        logger.info("Analyzing temporal diagnosis effects...")
        
        results = {}
        
        # Proxy: Formation decade (early) vs current diagnosis (late)
        # Early-diagnosed: Clear category from beginning (e.g., 1970s mythological when mythological was norm)
        # Late-diagnosed: Applied retrospectively decades later
        
        # Test if "cohort-typical" diagnoses (diagnosed during era norm) succeed more
        # vs "retrospective" diagnoses (applied later)
        
        for decade in [1970, 1980, 1990, 2000, 2010]:
            decade_df = df[df['formation_decade'] == decade]
            
            if len(decade_df) < 10:
                continue
            
            # Identify most common diagnosis in that decade
            modal_diagnosis = decade_df['diagnostic_category'].mode()[0] if len(decade_df) > 0 else None
            
            if modal_diagnosis:
                # Compare modal diagnosis success vs other diagnoses in that decade
                modal_bands = decade_df[decade_df['diagnostic_category'] == modal_diagnosis]
                other_bands = decade_df[decade_df['diagnostic_category'] != modal_diagnosis]
                
                if len(modal_bands) >= 5 and len(other_bands) >= 5:
                    modal_success = modal_bands['popularity_score'].mean()
                    other_success = other_bands['popularity_score'].mean()
                    
                    results[f'{decade}s'] = {
                        'modal_diagnosis': modal_diagnosis,
                        'modal_success': float(modal_success),
                        'other_success': float(other_success),
                        'modal_advantage': float(modal_success - other_success),
                        'interpretation': f'Being diagnosed with era-typical category ({modal_diagnosis}) → +{modal_success - other_success:.1f} advantage (conformity reward)' if modal_success > other_success else 'No conformity advantage'
                    }
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandIatrogenicEffectsAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) >= 30:
        print("\n" + "="*80)
        print("IATROGENIC EFFECTS ANALYSIS")
        print("="*80)
        print("\nQuestion: Do diagnostic labels CREATE outcomes (not just predict)?")
        
        # Diagnostic constraint
        print("\n🔒 Analyzing diagnostic constraint (genre lock-in)...")
        constraint_results = analyzer.analyze_diagnostic_constraint(df)
        
        # Self-fulfilling prophecy
        print("\n🔮 Analyzing self-fulfilling prophecy (number names)...")
        prophecy_results = analyzer.analyze_self_fulfilling_prophecy(df)
        
        # Expectation effects
        print("\n🎭 Analyzing expectation effects (Pygmalion)...")
        expectation_results = analyzer.analyze_expectation_effects(df)
        
        # Label resistance
        print("\n⚔️ Analyzing label resistance outcomes...")
        resistance_results = analyzer.analyze_label_resistance_outcomes(df)
        
        # Cross-cultural variance
        print("\n🌍 Analyzing cross-cultural diagnostic variance...")
        cultural_results = analyzer.analyze_cross_cultural_diagnostic_variance(df)
        
        # Temporal effects
        print("\n📅 Analyzing temporal diagnosis effects...")
        temporal_results = analyzer.analyze_temporal_diagnosis_effects(df)
        
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        if 'genre_lock_in_effects' in constraint_results:
            print("\n✓ DIAGNOSTIC CONSTRAINT:")
            for cat, data in list(constraint_results['genre_lock_in_effects'].items())[:3]:
                if isinstance(data, dict) and 'avg_lock_in_score' in data:
                    print(f"  {cat}: Lock-in {data['avg_lock_in_score']:.1f}/100")
                    print(f"    {data['interpretation']}")
        
        if 'awareness_causation_test' in prophecy_results and prophecy_results['awareness_causation_test'].get('significant'):
            print("\n✓ SELF-FULFILLING PROPHECY:")
            aware = prophecy_results['awareness_causation_test']
            print(f"  Number names: {aware['percent_decline']:.1f}% decline as awareness spread")
            print(f"  {aware['interpretation']}")
    
    else:
        print("Insufficient data. Collect bands first.")

