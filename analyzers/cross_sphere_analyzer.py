"""
Cross-Sphere Pattern Analyzer
Discovers universal naming patterns across cryptocurrencies and domains
"""

import numpy as np
import pandas as pd
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory, Domain, DomainAnalysis, CrossSpherePattern, Ship, ShipAnalysis
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class CrossSphereAnalyzer:
    """Analyze patterns across different asset spheres"""
    
    def find_universal_patterns(self):
        """Discover patterns that work across crypto, domains, and ships"""
        try:
            crypto_df = self._get_crypto_dataset()
            domain_df = self._get_domain_dataset()
            ships_df = self._get_ships_dataset()
            
            logger.info(f"Cross-sphere datasets: Crypto={len(crypto_df)}, Domains={len(domain_df)}, Ships={len(ships_df)}")
            
            if len(crypto_df) < 20 or len(domain_df) < 10:
                return {'universal_patterns': [], 'message': 'Insufficient data'}
            
            universal_patterns = []
            
            # Test syllable pattern transfer (all domains)
            syllable_pattern = self._test_syllable_universality_all(crypto_df, domain_df, ships_df)
            if syllable_pattern:
                universal_patterns.append(syllable_pattern)
            
            # Test memorability transfer (all domains)
            memorability_pattern = self._test_memorability_universality_all(crypto_df, domain_df, ships_df)
            if memorability_pattern:
                universal_patterns.append(memorability_pattern)
            
            # Test geographic names pattern (ships, hurricanes)
            if len(ships_df) >= 5:
                geographic_pattern = self._test_geographic_names_pattern(ships_df)
                if geographic_pattern:
                    universal_patterns.append(geographic_pattern)
            
            # Test authority/power phonetics (ships, academics, bands)
            if len(ships_df) >= 5:
                authority_pattern = self._test_authority_phonetics_pattern(ships_df)
                if authority_pattern:
                    universal_patterns.append(authority_pattern)
            
            # Legacy two-domain tests
            syllable_pattern_2d = self._test_syllable_universality(crypto_df, domain_df)
            memorability_pattern_2d = self._test_memorability_universality(crypto_df, domain_df)
            length_pattern = self._test_length_universality(crypto_df, domain_df)
            type_pattern = self._test_type_universality(crypto_df, domain_df)
            
            for p in [syllable_pattern_2d, memorability_pattern_2d, length_pattern, type_pattern]:
                if p and p not in universal_patterns:
                    universal_patterns.append(p)
            
            # Save to database
            for pattern in universal_patterns:
                self._save_cross_sphere_pattern(pattern)
            
            return {
                'universal_patterns': universal_patterns,
                'crypto_sample_size': len(crypto_df),
                'domain_sample_size': len(domain_df),
                'ships_sample_size': len(ships_df)
            }
        
        except Exception as e:
            logger.error(f"Universal pattern discovery error: {e}")
            return {'universal_patterns': [], 'error': str(e)}
    
    def _get_crypto_dataset(self):
        """Get cryptocurrency dataset"""
        latest_prices_subq = db.session.query(
            PriceHistory.crypto_id,
            db.func.max(PriceHistory.date).label('max_date')
        ).group_by(PriceHistory.crypto_id).subquery()
        
        query = db.session.query(
            Cryptocurrency,
            NameAnalysis,
            PriceHistory
        ).join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
         .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
         .join(latest_prices_subq, db.and_(
             PriceHistory.crypto_id == latest_prices_subq.c.crypto_id,
             PriceHistory.date == latest_prices_subq.c.max_date
         ))
        
        data = []
        for crypto, analysis, price in query.all():
            if price.price_1yr_change is not None:
                data.append({
                    'name': crypto.name,
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'name_type': analysis.name_type or 'other',
                    'performance': price.price_1yr_change  # Use 1yr return as "value"
                })
        
        return pd.DataFrame(data)
    
    def _get_domain_dataset(self):
        """Get domain dataset"""
        query = db.session.query(Domain, DomainAnalysis)\
            .join(DomainAnalysis, Domain.id == DomainAnalysis.domain_id)
        
        data = []
        for domain, analysis in query.all():
            if domain.sale_price:  # Only historical sales with known prices
                data.append({
                    'name': domain.name,
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'name_type': analysis.name_type or 'other',
                    'performance': np.log10(domain.sale_price) * 20  # Normalize: log scale of price
                })
        
        return pd.DataFrame(data)
    
    def _get_ships_dataset(self):
        """Get ships dataset for cross-domain comparison"""
        try:
            query = db.session.query(Ship, ShipAnalysis)\
                .join(ShipAnalysis, Ship.id == ShipAnalysis.ship_id)
            
            data = []
            for ship, analysis in query.all():
                if ship.historical_significance_score:
                    data.append({
                        'name': ship.name,
                        'syllables': analysis.syllable_count or 0,
                        'length': analysis.character_length or 0,
                        'memorability': analysis.memorability_score or 0,
                        'uniqueness': analysis.uniqueness_score or 0,
                        'name_type': analysis.name_category or 'other',
                        'performance': ship.historical_significance_score,
                        'name_category': ship.name_category,
                        'is_geographic': analysis.is_geographic_name,
                        'is_saint': analysis.is_saint_name,
                        'authority_score': analysis.authority_score or 0,
                        'harshness_score': analysis.harshness_score or 0,
                        'power_connotation': analysis.power_connotation_score or 0
                    })
            
            return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"Could not load ships dataset: {e}")
            return pd.DataFrame()
    
    def _test_syllable_universality_all(self, crypto_df, domain_df, ships_df):
        """Test syllable patterns across all three domains"""
        if len(ships_df) < 5:
            return None
        
        # Test 2-3 syllable pattern in each domain
        results = {}
        
        for name, df in [('crypto', crypto_df), ('domains', domain_df), ('ships', ships_df)]:
            if len(df) < 5:
                continue
            
            optimal = df[df['syllables'].isin([2, 3])]['performance']
            other = df[~df['syllables'].isin([2, 3])]['performance']
            
            if len(optimal) >= 3 and len(other) >= 3:
                t_stat, p_val = stats.ttest_ind(optimal, other)
                effect = (optimal.mean() - other.mean()) / optimal.std() if optimal.std() > 0 else 0
                
                results[name] = {
                    'mean_optimal': float(optimal.mean()),
                    'mean_other': float(other.mean()),
                    'p_value': float(p_val),
                    'effect_size': float(effect),
                    'significant': p_val < 0.1
                }
        
        # Check if pattern holds across domains
        significant_count = sum(1 for r in results.values() if r['significant'])
        
        if significant_count >= 2:
            return {
                'pattern_name': '2-3 Syllables Optimal (Multi-Domain)',
                'description': f'2-3 syllable names optimal across {significant_count} domains',
                'domains': results,
                'universal_strength': (significant_count / 3) * 100,
                'is_universal': True
            }
        
        return None
    
    def _test_memorability_universality_all(self, crypto_df, domain_df, ships_df):
        """Test memorability correlation across all domains"""
        if len(ships_df) < 5:
            return None
        
        results = {}
        
        for name, df in [('crypto', crypto_df), ('domains', domain_df), ('ships', ships_df)]:
            if len(df) < 10:
                continue
            
            clean_df = df[(df['memorability'] > 0) & (df['performance'].notna())]
            
            if len(clean_df) >= 5:
                corr, p_val = stats.pearsonr(clean_df['memorability'], clean_df['performance'])
                
                results[name] = {
                    'correlation': float(corr),
                    'p_value': float(p_val),
                    'sample_size': len(clean_df),
                    'significant': p_val < 0.1
                }
        
        significant_count = sum(1 for r in results.values() if r['significant'] and r['correlation'] > 0)
        
        if significant_count >= 2:
            return {
                'pattern_name': 'Memorability → Performance (Multi-Domain)',
                'description': f'Memorable names correlate with success across {significant_count} domains',
                'domains': results,
                'universal_strength': (significant_count / 3) * 100,
                'is_universal': True
            }
        
        return None
    
    def _test_geographic_names_pattern(self, ships_df):
        """Test if geographic names show advantage (ships-specific but cross-domain comparable)"""
        if 'is_geographic' not in ships_df.columns or 'is_saint' not in ships_df.columns:
            return None
        
        geographic = ships_df[ships_df['is_geographic'] == True]['performance']
        saint = ships_df[ships_df['is_saint'] == True]['performance']
        
        if len(geographic) < 3 or len(saint) < 3:
            return None
        
        t_stat, p_val = stats.ttest_ind(geographic, saint, equal_var=False)
        effect = (geographic.mean() - saint.mean()) / geographic.std() if geographic.std() > 0 else 0
        
        return {
            'pattern_name': 'Geographic Names Advantage (Ships)',
            'description': 'Geographic place names correlate with greater historical achievement than saint names',
            'domains': {
                'ships': {
                    'geographic_mean': float(geographic.mean()),
                    'saint_mean': float(saint.mean()),
                    'p_value': float(p_val),
                    'effect_size': float(effect),
                    'significant': p_val < 0.05
                }
            },
            'universal_strength': 100 if p_val < 0.05 else 50,
            'is_universal': p_val < 0.05,
            'cross_domain_note': 'Can be compared to hurricane geographic names, band place names, etc.'
        }
    
    def _test_authority_phonetics_pattern(self, ships_df):
        """Test if authority/harshness phonetics correlate with outcomes"""
        if 'authority_score' not in ships_df.columns:
            return None
        
        clean_df = ships_df[(ships_df['authority_score'] > 0) & (ships_df['performance'].notna())]
        
        if len(clean_df) < 10:
            return None
        
        corr, p_val = stats.pearsonr(clean_df['authority_score'], clean_df['performance'])
        
        if p_val < 0.1:
            return {
                'pattern_name': 'Authority/Power Phonetics (Ships)',
                'description': 'Authoritative-sounding names correlate with achievement',
                'domains': {
                    'ships': {
                        'correlation': float(corr),
                        'p_value': float(p_val),
                        'sample_size': len(clean_df),
                        'significant': p_val < 0.05
                    }
                },
                'universal_strength': abs(corr) * 100,
                'is_universal': p_val < 0.05,
                'cross_domain_note': 'Compare to: hurricane harshness → casualties, academic authority → h-index, band power → genre success'
            }
        
        return None
    
    def _test_syllable_universality(self, crypto_df, domain_df):
        """Test if syllable patterns transfer"""
        # Test 2-3 syllable pattern
        crypto_23 = crypto_df[crypto_df['syllables'].isin([2, 3])]['performance']
        crypto_other = crypto_df[~crypto_df['syllables'].isin([2, 3])]['performance']
        
        domain_23 = domain_df[domain_df['syllables'].isin([2, 3])]['performance']
        domain_other = domain_df[~domain_df['syllables'].isin([2, 3])]['performance']
        
        if len(crypto_23) < 10 or len(domain_23) < 5:
            return None
        
        # T-tests for each sphere
        crypto_tstat, crypto_pval = stats.ttest_ind(crypto_23, crypto_other)
        domain_tstat, domain_pval = stats.ttest_ind(domain_23, domain_other)
        
        # Effect sizes
        crypto_effect = (crypto_23.mean() - crypto_other.mean()) / crypto_23.std()
        domain_effect = (domain_23.mean() - domain_other.mean()) / domain_23.std()
        
        # Cross-sphere correlation
        try:
            cross_corr = np.corrcoef([crypto_effect, domain_effect])[0, 1] if not np.isnan(crypto_effect) and not np.isnan(domain_effect) else 0
        except:
            cross_corr = 0
        
        # Calculate universal strength
        both_significant = crypto_pval < 0.05 and domain_pval < 0.1
        universal_strength = abs(cross_corr) * 100 if both_significant else 0
        
        return {
            'pattern_name': '2-3 Syllable Names',
            'description': 'Names with 2-3 syllables outperform across both spheres',
            'crypto': {
                'correlation': round(crypto_effect, 3),
                'p_value': round(crypto_pval, 4),
                'sample_size': len(crypto_23),
                'effect_size': round(crypto_effect, 2),
                'avg_performance': round(crypto_23.mean(), 2)
            },
            'domains': {
                'correlation': round(domain_effect, 3),
                'p_value': round(domain_pval, 4),
                'sample_size': len(domain_23),
                'effect_size': round(domain_effect, 2),
                'avg_performance': round(domain_23.mean(), 2)
            },
            'universal_strength': round(universal_strength, 1),
            'is_universal': both_significant,
            'cross_correlation': round(cross_corr, 3)
        }
    
    def _test_memorability_universality(self, crypto_df, domain_df):
        """Test if memorability correlates with value in both spheres"""
        # Correlation between memorability and performance
        crypto_corr, crypto_pval = stats.pearsonr(crypto_df['memorability'], crypto_df['performance'])
        domain_corr, domain_pval = stats.pearsonr(domain_df['memorability'], domain_df['performance'])
        
        # Both positive and significant?
        both_significant = crypto_pval < 0.05 and domain_pval < 0.1
        both_positive = crypto_corr > 0 and domain_corr > 0
        
        # Cross-sphere correlation (similarity of correlations)
        cross_corr = (crypto_corr + domain_corr) / 2  # Average of correlations
        universal_strength = abs(cross_corr) * 100 if (both_significant and both_positive) else 0
        
        return {
            'pattern_name': 'Memorability Premium',
            'description': 'High memorability scores correlate with higher value',
            'crypto': {
                'correlation': round(crypto_corr, 3),
                'p_value': round(crypto_pval, 4),
                'sample_size': len(crypto_df),
                'effect_size': round(crypto_corr, 2)
            },
            'domains': {
                'correlation': round(domain_corr, 3),
                'p_value': round(domain_pval, 4),
                'sample_size': len(domain_df),
                'effect_size': round(domain_corr, 2)
            },
            'universal_strength': round(universal_strength, 1),
            'is_universal': both_significant and both_positive,
            'cross_correlation': round(cross_corr, 3)
        }
    
    def _test_length_universality(self, crypto_df, domain_df):
        """Test length preferences across spheres"""
        # Note: Crypto prefers 5-8, domains prefer 4-6
        crypto_optimal = crypto_df[crypto_df['length'].between(5, 8)]['performance']
        crypto_other = crypto_df[~crypto_df['length'].between(5, 8)]['performance']
        
        domain_optimal = domain_df[domain_df['length'].between(4, 6)]['performance']
        domain_other = domain_df[~domain_df['length'].between(4, 6)]['performance']
        
        if len(crypto_optimal) < 10 or len(domain_optimal) < 5:
            return None
        
        crypto_tstat, crypto_pval = stats.ttest_ind(crypto_optimal, crypto_other)
        domain_tstat, domain_pval = stats.ttest_ind(domain_optimal, domain_other)
        
        crypto_effect = (crypto_optimal.mean() - crypto_other.mean()) / crypto_optimal.std()
        domain_effect = (domain_optimal.mean() - domain_other.mean()) / domain_optimal.std()
        
        # This might be sphere-specific (different optimal lengths)
        both_significant = crypto_pval < 0.05 and domain_pval < 0.1
        
        return {
            'pattern_name': 'Optimal Length (Sphere-Specific)',
            'description': 'Crypto prefers 5-8 chars, domains prefer 4-6 chars',
            'crypto': {
                'correlation': round(crypto_effect, 3),
                'p_value': round(crypto_pval, 4),
                'sample_size': len(crypto_optimal),
                'effect_size': round(crypto_effect, 2),
                'optimal_range': '5-8 characters'
            },
            'domains': {
                'correlation': round(domain_effect, 3),
                'p_value': round(domain_pval, 4),
                'sample_size': len(domain_optimal),
                'effect_size': round(domain_effect, 2),
                'optimal_range': '4-6 characters'
            },
            'universal_strength': 60 if both_significant else 30,
            'is_universal': False,  # Sphere-specific
            'note': 'Pattern exists in both spheres but with different parameters'
        }
    
    def _test_type_universality(self, crypto_df, domain_df):
        """Test if tech-oriented names command premium in both"""
        crypto_tech = crypto_df[crypto_df['name_type'] == 'tech']['performance']
        crypto_nontech = crypto_df[crypto_df['name_type'] != 'tech']['performance']
        
        domain_tech = domain_df[domain_df['name_type'] == 'tech']['performance']
        domain_nontech = domain_df[domain_df['name_type'] != 'tech']['performance']
        
        if len(crypto_tech) < 10 or len(domain_tech) < 5:
            return None
        
        crypto_tstat, crypto_pval = stats.ttest_ind(crypto_tech, crypto_nontech)
        domain_tstat, domain_pval = stats.ttest_ind(domain_tech, domain_nontech)
        
        crypto_effect = (crypto_tech.mean() - crypto_nontech.mean()) / crypto_tech.std()
        domain_effect = (domain_tech.mean() - domain_nontech.mean()) / domain_tech.std()
        
        both_significant = crypto_pval < 0.05 and domain_pval < 0.1
        try:
            cross_corr = np.corrcoef([crypto_effect, domain_effect])[0, 1] if not np.isnan(crypto_effect) and not np.isnan(domain_effect) else 0
        except:
            cross_corr = 0
        
        return {
            'pattern_name': 'Tech-Oriented Premium',
            'description': 'Technology-oriented names command premium value',
            'crypto': {
                'correlation': round(crypto_effect, 3),
                'p_value': round(crypto_pval, 4),
                'sample_size': len(crypto_tech),
                'effect_size': round(crypto_effect, 2)
            },
            'domains': {
                'correlation': round(domain_effect, 3),
                'p_value': round(domain_pval, 4),
                'sample_size': len(domain_tech),
                'effect_size': round(domain_effect, 2)
            },
            'universal_strength': abs(cross_corr) * 100 if both_significant else 0,
            'is_universal': both_significant,
            'cross_correlation': round(cross_corr, 3)
        }
    
    def _save_cross_sphere_pattern(self, pattern_data):
        """Save discovered cross-sphere pattern to database"""
        try:
            # Check if exists
            existing = CrossSpherePattern.query.filter_by(pattern_name=pattern_data['pattern_name']).first()
            
            if existing:
                # Update existing
                pattern = existing
            else:
                pattern = CrossSpherePattern()
            
            pattern.pattern_name = pattern_data['pattern_name']
            pattern.pattern_description = pattern_data['description']
            
            # Crypto data
            pattern.crypto_correlation = pattern_data['crypto']['correlation']
            pattern.crypto_p_value = pattern_data['crypto']['p_value']
            pattern.crypto_sample_size = pattern_data['crypto']['sample_size']
            pattern.crypto_effect_size = pattern_data['crypto']['effect_size']
            
            # Domain data
            pattern.domain_correlation = pattern_data['domains']['correlation']
            pattern.domain_p_value = pattern_data['domains']['p_value']
            pattern.domain_sample_size = pattern_data['domains']['sample_size']
            pattern.domain_effect_size = pattern_data['domains']['effect_size']
            
            # Universal metrics
            pattern.universal_strength = pattern_data['universal_strength']
            pattern.is_universal = pattern_data['is_universal']
            pattern.transferability_score = abs(pattern_data.get('cross_correlation', 0)) * 100
            
            if not existing:
                db.session.add(pattern)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving pattern: {e}")
            db.session.rollback()
    
    def get_sphere_specific_patterns(self):
        """Get patterns that are strong in one sphere but not the other"""
        try:
            crypto_df = self._get_crypto_dataset()
            domain_df = self._get_domain_dataset()
            
            sphere_specific = {
                'crypto_only': [],
                'domain_only': []
            }
            
            # Crypto-specific: Animal names pattern
            crypto_animal = crypto_df[crypto_df['name_type'] == 'animal']['performance']
            domain_animal = domain_df[domain_df['name_type'] == 'animal']['performance'] if 'animal' in domain_df['name_type'].values else pd.Series([])
            
            if len(crypto_animal) >= 5:
                crypto_avg = crypto_animal.mean()
                market_avg = crypto_df['performance'].mean()
                
                if abs(crypto_avg - market_avg) > 20:  # Significant difference
                    sphere_specific['crypto_only'].append({
                        'pattern': 'Animal Names',
                        'description': 'Animal-themed names show distinct behavior in crypto vs domains',
                        'crypto_effect': round(crypto_avg - market_avg, 2),
                        'reason': 'Crypto market sensitive to novelty/meme value; domains less so'
                    })
            
            # Domain-specific: Ultra-short (2-3 chars) premium
            domain_ultra_short = domain_df[domain_df['length'] <= 3]['performance']
            crypto_ultra_short = crypto_df[crypto_df['length'] <= 3]['performance']
            
            if len(domain_ultra_short) >= 5:
                domain_avg = domain_ultra_short.mean()
                domain_market_avg = domain_df['performance'].mean()
                
                if (domain_avg - domain_market_avg) > 20:  # Significant premium in domains
                    sphere_specific['domain_only'].append({
                        'pattern': 'Ultra-Short Names (2-3 chars)',
                        'description': 'Massive premium in domains, less so in crypto',
                        'domain_effect': round(domain_avg - domain_market_avg, 2),
                        'reason': 'Domain scarcity creates premium; crypto needs meaning/context'
                    })
            
            return sphere_specific
        
        except Exception as e:
            logger.error(f"Sphere-specific pattern error: {e}")
            return {'crypto_only': [], 'domain_only': []}
    
    def calculate_pattern_transferability(self, pattern_type, from_sphere='crypto', to_sphere='domains'):
        """
        Calculate probability that a pattern from one sphere works in another
        
        Returns: Transfer probability (0-100%)
        """
        try:
            # Get all cross-sphere patterns
            patterns = CrossSpherePattern.query.all()
            
            if not patterns:
                return 50  # Default 50% if no data
            
            # Calculate historical transfer success rate
            universal_count = sum(1 for p in patterns if p.is_universal)
            total_count = len(patterns)
            
            transfer_rate = (universal_count / total_count * 100) if total_count > 0 else 50
            
            return round(transfer_rate, 1)
        
        except Exception as e:
            logger.error(f"Transferability calculation error: {e}")
            return 50
    
    def get_cross_sphere_correlations(self):
        """Get correlation coefficients between spheres for each metric"""
        try:
            crypto_df = self._get_crypto_dataset()
            domain_df = self._get_domain_dataset()
            
            correlations = []
            
            metrics = ['syllables', 'length', 'memorability', 'uniqueness']
            
            for metric in metrics:
                # Group by metric value and calculate average performance
                crypto_grouped = crypto_df.groupby(metric)['performance'].mean()
                domain_grouped = domain_df.groupby(metric)['performance'].mean()
                
                # Find common values
                common_values = set(crypto_grouped.index) & set(domain_grouped.index)
                
                if len(common_values) >= 3:
                    crypto_vals = [crypto_grouped[v] for v in common_values]
                    domain_vals = [domain_grouped[v] for v in common_values]
                    
                    corr, p_val = stats.pearsonr(crypto_vals, domain_vals)
                    
                    correlations.append({
                        'metric': metric,
                        'cross_sphere_correlation': round(corr, 3),
                        'p_value': round(p_val, 4),
                        'interpretation': self._interpret_correlation(corr),
                        'common_datapoints': len(common_values)
                    })
            
            return correlations
        
        except Exception as e:
            logger.error(f"Cross-sphere correlation error: {e}")
            return []
    
    def _interpret_correlation(self, corr):
        """Interpret correlation strength"""
        abs_corr = abs(corr)
        if abs_corr > 0.7:
            return 'Strong cross-sphere correlation - Universal pattern'
        elif abs_corr > 0.5:
            return 'Moderate cross-sphere correlation'
        elif abs_corr > 0.3:
            return 'Weak cross-sphere correlation'
        else:
            return 'No significant cross-sphere correlation - Sphere-specific'

