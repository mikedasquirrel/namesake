"""
Multi-Sphere Pattern Analyzer
Discovers universal naming patterns across all 6 spheres
"""

import numpy as np
import pandas as pd
from core.models import db, Cryptocurrency, NameAnalysis, PriceHistory
from core.models import Domain, DomainAnalysis, Stock, StockAnalysis
from core.models import Film, FilmAnalysis, Book, BookAnalysis, Person, PersonAnalysis
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class MultiSphereAnalyzer:
    """Analyze patterns across all 6 spheres"""
    
    def __init__(self):
        self.spheres = ['crypto', 'domains', 'stocks', 'films', 'books', 'people']
    
    def get_all_sphere_data(self):
        """Get unified dataset across all spheres"""
        all_data = {
            'crypto': self._get_crypto_data(),
            'domains': self._get_domain_data(),
            'stocks': self._get_stock_data(),
            'films': self._get_film_data(),
            'books': self._get_book_data(),
            'people': self._get_people_data()
        }
        
        return all_data
    
    def _get_crypto_data(self):
        """Get crypto dataset"""
        latest_prices = db.session.query(
            PriceHistory.crypto_id,
            db.func.max(PriceHistory.date).label('max_date')
        ).group_by(PriceHistory.crypto_id).subquery()
        
        query = db.session.query(Cryptocurrency, NameAnalysis, PriceHistory)\
            .join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
            .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
            .join(latest_prices, db.and_(
                PriceHistory.crypto_id == latest_prices.c.crypto_id,
                PriceHistory.date == latest_prices.c.max_date
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
                    'performance': price.price_1yr_change
                })
        
        return pd.DataFrame(data)
    
    def _get_domain_data(self):
        """Get domain dataset"""
        query = db.session.query(Domain, DomainAnalysis)\
            .join(DomainAnalysis, Domain.id == DomainAnalysis.domain_id)
        
        data = []
        for domain, analysis in query.all():
            if domain.sale_price:
                data.append({
                    'name': domain.name,
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'performance': np.log10(domain.sale_price) * 20  # Log scale
                })
        
        return pd.DataFrame(data)
    
    def _get_stock_data(self):
        """Get stock dataset"""
        query = db.session.query(Stock, StockAnalysis)\
            .join(StockAnalysis, Stock.id == StockAnalysis.stock_id)
        
        data = []
        for stock, analysis in query.all():
            if stock.return_1yr is not None:
                data.append({
                    'name': stock.company_name,
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'performance': stock.return_1yr
                })
        
        return pd.DataFrame(data)
    
    def _get_film_data(self):
        """Get film dataset"""
        query = db.session.query(Film, FilmAnalysis)\
            .join(FilmAnalysis, Film.id == FilmAnalysis.film_id)
        
        data = []
        for film, analysis in query.all():
            if film.roi:
                data.append({
                    'name': film.title,
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'performance': film.roi
                })
        
        return pd.DataFrame(data)
    
    def _get_book_data(self):
        """Get book dataset"""
        query = db.session.query(Book, BookAnalysis)\
            .join(BookAnalysis, Book.id == BookAnalysis.book_id)
        
        data = []
        for book, analysis in query.all():
            if book.performance_score:
                data.append({
                    'name': book.title,
                    'syllables': analysis.syllable_count or 0,
                    'length': analysis.character_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'performance': book.performance_score
                })
        
        return pd.DataFrame(data)
    
    def _get_people_data(self):
        """Get people dataset"""
        query = db.session.query(Person, PersonAnalysis)\
            .join(PersonAnalysis, Person.id == PersonAnalysis.person_id)
        
        data = []
        for person, analysis in query.all():
            if person.net_worth:
                data.append({
                    'name': person.full_name,
                    'syllables': analysis.total_syllables or 0,
                    'length': analysis.total_length or 0,
                    'memorability': analysis.memorability_score or 0,
                    'uniqueness': analysis.uniqueness_score or 0,
                    'performance': np.log10(person.net_worth) * 10  # Log scale
                })
        
        return pd.DataFrame(data)
    
    def find_universal_patterns(self):
        """Find patterns that work across multiple spheres"""
        try:
            all_data = self.get_all_sphere_data()
            
            universal_patterns = []
            
            # Test each metric across all spheres
            metrics = ['syllables', 'length', 'memorability']
            
            for metric in metrics:
                pattern_result = self._test_metric_universality(metric, all_data)
                if pattern_result:
                    universal_patterns.append(pattern_result)
            
            return universal_patterns
        
        except Exception as e:
            logger.error(f"Universal pattern discovery error: {e}")
            return []
    
    def _test_metric_universality(self, metric, all_data):
        """Test if a metric correlates with performance across spheres"""
        correlations = {}
        
        for sphere, df in all_data.items():
            if len(df) < 5:
                continue
            
            try:
                corr, p_val = stats.pearsonr(df[metric], df['performance'])
                correlations[sphere] = {
                    'correlation': round(float(corr), 3),
                    'p_value': round(float(p_val), 4),
                    'sample_size': int(len(df)),
                    'significant': bool(p_val < 0.05)
                }
            except:
                continue
        
        # Count how many spheres show significant correlation
        significant_count = sum(1 for c in correlations.values() if c['significant'])
        
        # Calculate average correlation
        avg_corr = np.mean([c['correlation'] for c in correlations.values()])
        
        return {
            'metric': metric,
            'correlations': correlations,
            'significant_spheres': int(significant_count),
            'total_spheres': int(len(correlations)),
            'avg_correlation': round(float(avg_corr), 3),
            'is_universal': bool(significant_count >= 3),  # Universal if works in 3+ spheres
            'strength': 'STRONG' if significant_count >= 4 else ('MODERATE' if significant_count >= 2 else 'WEAK')
        }
    
    def calculate_correlation_matrix(self):
        """Calculate pairwise correlations between all spheres"""
        all_data = self.get_all_sphere_data()
        
        # Create matrix
        matrix = {}
        spheres_list = [s for s in self.spheres if s in all_data and len(all_data[s]) >= 5]
        
        for sphere1 in spheres_list:
            matrix[sphere1] = {}
            for sphere2 in spheres_list:
                if sphere1 == sphere2:
                    matrix[sphere1][sphere2] = 1.0
                else:
                    # Calculate correlation of patterns between spheres
                    corr = self._calculate_sphere_correlation(all_data[sphere1], all_data[sphere2])
                    matrix[sphere1][sphere2] = corr
        
        return matrix
    
    def _calculate_sphere_correlation(self, df1, df2):
        """Calculate correlation between two spheres"""
        try:
            # Compare how length affects performance in both spheres
            if len(df1) < 5 or len(df2) < 5:
                return 0
            
            # Group by length and get average performance
            df1_grouped = df1.groupby('length')['performance'].mean()
            df2_grouped = df2.groupby('length')['performance'].mean()
            
            # Find common lengths
            common_lengths = set(df1_grouped.index) & set(df2_grouped.index)
            
            if len(common_lengths) < 3:
                return 0
            
            vals1 = [df1_grouped[l] for l in common_lengths]
            vals2 = [df2_grouped[l] for l in common_lengths]
            
            corr, _ = stats.pearsonr(vals1, vals2)
            return round(corr, 3)
        except:
            return 0
    
    def get_sphere_statistics(self):
        """Get summary statistics for each sphere"""
        all_data = self.get_all_sphere_data()
        
        stats_summary = {}
        
        for sphere, df in all_data.items():
            if len(df) == 0:
                continue
            
            stats_summary[sphere] = {
                'count': len(df),
                'avg_syllables': round(df['syllables'].mean(), 2),
                'avg_length': round(df['length'].mean(), 2),
                'avg_memorability': round(df['memorability'].mean(), 2),
                'avg_performance': round(df['performance'].mean(), 2),
                'top_performer': df.nlargest(1, 'performance')['name'].iloc[0] if len(df) > 0 else None
            }
        
        return stats_summary

