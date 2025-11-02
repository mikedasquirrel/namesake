import re
from core.models import Cryptocurrency, NameAnalysis, PriceHistory, db
from sqlalchemy import and_, or_
import json


class QueryParser:
    """Parse plain English queries into database filters"""
    
    def __init__(self):
        # Keyword mappings
        self.performance_keywords = {
            '30d': 'price_30d_change',
            '30-day': 'price_30d_change',
            '90d': 'price_90d_change',
            '90-day': 'price_90d_change',
            '1yr': 'price_1yr_change',
            '1-year': 'price_1yr_change',
            'year': 'price_1yr_change',
            'ath': 'price_ath_change',
            'all-time': 'price_ath_change'
        }
        
        self.name_type_keywords = {
            'animal': 'animal',
            'tech': 'tech',
            'technology': 'tech',
            'mythological': 'mythological',
            'myth': 'mythological',
            'financial': 'financial',
            'finance': 'financial',
            'astronomical': 'astronomical',
            'astronomy': 'astronomical',
            'elemental': 'elemental',
            'invented': 'invented',
            'acronym': 'acronym'
        }
        
        self.comparison_keywords = {
            'high': 'high',
            'low': 'low',
            'positive': 'positive',
            'negative': 'negative',
            'above': 'above',
            'below': 'below',
            'greater': 'above',
            'less': 'below',
            'top': 'top',
            'bottom': 'bottom',
            'best': 'top',
            'worst': 'bottom'
        }
    
    def parse(self, query_text):
        """
        Parse a natural language query into database filters
        
        Args:
            query_text: Plain English query
            
        Returns:
            Dict with parsed filters and parameters
        """
        query_lower = query_text.lower()
        
        filters = {
            'name_type': None,
            'syllable_count': None,
            'length_range': None,
            'performance_metric': None,
            'performance_threshold': None,
            'performance_comparison': None,
            'has_numbers': None,
            'uniqueness': None,
            'memorability': None,
            'limit': 100,
            'sort_by': None,
            'sort_order': 'desc'
        }
        
        # Extract name type
        for keyword, name_type in self.name_type_keywords.items():
            if keyword in query_lower:
                filters['name_type'] = name_type
                break
        
        # Extract syllable count
        syllable_match = re.search(r'(\d+)[\s-]syllable', query_lower)
        if syllable_match:
            filters['syllable_count'] = int(syllable_match.group(1))
        
        # Extract length keywords
        if 'short name' in query_lower or 'short' in query_lower:
            filters['length_range'] = (1, 6)
        elif 'long name' in query_lower or 'long' in query_lower:
            filters['length_range'] = (10, 100)
        elif 'medium' in query_lower:
            filters['length_range'] = (6, 10)
        
        # Extract performance metric
        for keyword, metric in self.performance_keywords.items():
            if keyword in query_lower:
                filters['performance_metric'] = metric
                break
        
        # Extract performance threshold
        percent_match = re.search(r'(\d+)%', query_lower)
        if percent_match:
            threshold = int(percent_match.group(1))
            
            # Determine comparison
            if any(word in query_lower for word in ['above', 'over', 'greater', 'more than', '>']):
                filters['performance_comparison'] = 'above'
                filters['performance_threshold'] = threshold
            elif any(word in query_lower for word in ['below', 'under', 'less', 'fewer than', '<']):
                filters['performance_comparison'] = 'below'
                filters['performance_threshold'] = threshold
        
        # Detect positive/negative performance
        if 'positive' in query_lower or 'gain' in query_lower or 'growth' in query_lower:
            filters['performance_comparison'] = 'above'
            filters['performance_threshold'] = 0
        elif 'negative' in query_lower or 'loss' in query_lower or 'decline' in query_lower:
            filters['performance_comparison'] = 'below'
            filters['performance_threshold'] = 0
        
        # Extract has_numbers
        if 'no numbers' in query_lower or 'without numbers' in query_lower:
            filters['has_numbers'] = False
        elif 'with numbers' in query_lower or 'has numbers' in query_lower:
            filters['has_numbers'] = True
        
        # Extract uniqueness
        if 'unique' in query_lower or 'rare' in query_lower:
            filters['uniqueness'] = 'high'
        elif 'common' in query_lower or 'similar' in query_lower:
            filters['uniqueness'] = 'low'
        
        # Extract memorability
        if 'memorable' in query_lower or 'catchy' in query_lower:
            filters['memorability'] = 'high'
        
        # Extract limit
        limit_match = re.search(r'(?:top|show|find|get)\s+(\d+)', query_lower)
        if limit_match:
            filters['limit'] = int(limit_match.group(1))
        
        # Extract sort
        if 'highest' in query_lower or 'best performing' in query_lower or 'top' in query_lower:
            filters['sort_order'] = 'desc'
        elif 'lowest' in query_lower or 'worst performing' in query_lower or 'bottom' in query_lower:
            filters['sort_order'] = 'asc'
        
        return filters
    
    def execute_query(self, filters):
        """
        Execute a parsed query against the database
        
        Args:
            filters: Parsed filter dictionary
            
        Returns:
            List of matching cryptocurrencies with analysis
        """
        # Build query
        query = db.session.query(Cryptocurrency, NameAnalysis, PriceHistory)\
            .join(NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id)\
            .join(PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id)\
            .group_by(Cryptocurrency.id)\
            .having(PriceHistory.date == db.session.query(db.func.max(PriceHistory.date))
                    .filter(PriceHistory.crypto_id == Cryptocurrency.id).correlate(Cryptocurrency))
        
        # Apply filters
        if filters.get('name_type'):
            query = query.filter(NameAnalysis.name_type == filters['name_type'])
        
        if filters.get('syllable_count'):
            query = query.filter(NameAnalysis.syllable_count == filters['syllable_count'])
        
        if filters.get('length_range'):
            min_len, max_len = filters['length_range']
            query = query.filter(
                and_(
                    NameAnalysis.character_length >= min_len,
                    NameAnalysis.character_length <= max_len
                )
            )
        
        if filters.get('has_numbers') is not None:
            query = query.filter(NameAnalysis.has_numbers == filters['has_numbers'])
        
        if filters.get('uniqueness') == 'high':
            query = query.filter(NameAnalysis.uniqueness_score >= 70)
        elif filters.get('uniqueness') == 'low':
            query = query.filter(NameAnalysis.uniqueness_score < 40)
        
        if filters.get('memorability') == 'high':
            query = query.filter(NameAnalysis.memorability_score >= 70)
        
        # Performance filters
        if filters.get('performance_metric') and filters.get('performance_threshold') is not None:
            metric_column = getattr(PriceHistory, filters['performance_metric'])
            
            if filters.get('performance_comparison') == 'above':
                query = query.filter(metric_column >= filters['performance_threshold'])
            elif filters.get('performance_comparison') == 'below':
                query = query.filter(metric_column <= filters['performance_threshold'])
        
        # Sorting
        if filters.get('performance_metric'):
            metric_column = getattr(PriceHistory, filters['performance_metric'])
            if filters.get('sort_order') == 'desc':
                query = query.order_by(metric_column.desc())
            else:
                query = query.order_by(metric_column.asc())
        else:
            # Default sort by market cap
            query = query.order_by(Cryptocurrency.market_cap.desc())
        
        # Apply limit
        query = query.limit(filters.get('limit', 100))
        
        # Execute and format results
        results = []
        for crypto, analysis, price_hist in query.all():
            results.append({
                'cryptocurrency': crypto.to_dict(),
                'name_analysis': analysis.to_dict(),
                'performance': {
                    'price_30d_change': price_hist.price_30d_change,
                    'price_90d_change': price_hist.price_90d_change,
                    'price_1yr_change': price_hist.price_1yr_change,
                    'price_ath_change': price_hist.price_ath_change
                }
            })
        
        return results
    
    def get_preset_queries(self):
        """Get list of preset queries for common use cases"""
        return [
            {
                'name': 'Top Animal Names',
                'query': 'Show top 20 animal names with positive 1-year growth',
                'description': 'Animal-themed cryptocurrencies with positive annual returns'
            },
            {
                'name': 'Short & Memorable Winners',
                'query': 'Find short memorable names with above 50% 1-year returns',
                'description': 'Catchy, short names that performed well'
            },
            {
                'name': 'Unique Tech Names',
                'query': 'Show unique technology names with high 90-day returns',
                'description': 'Distinctive tech-focused cryptocurrencies'
            },
            {
                'name': '3-Syllable Champions',
                'query': 'Find 3-syllable names with positive all-time returns',
                'description': 'Medium-complexity names that succeeded'
            },
            {
                'name': 'No Numbers, High Performance',
                'query': 'Show names without numbers with above 100% 1-year growth',
                'description': 'Pure letter names with strong returns'
            },
            {
                'name': 'Rare Name Types',
                'query': 'Find rare unique names with positive 90-day performance',
                'description': 'Uncommon name categories that gained value'
            },
            {
                'name': 'Best Mythological Names',
                'query': 'Show mythological names with high 1-year returns',
                'description': 'Myth-inspired cryptocurrencies that performed well'
            },
            {
                'name': 'Top Performing Short Names',
                'query': 'Find top 10 short names with highest 1-year growth',
                'description': 'Brief names with exceptional returns'
            }
        ]
    
    def natural_language_query(self, query_text):
        """
        Complete natural language query workflow
        
        Args:
            query_text: Plain English query
            
        Returns:
            Dict with parsed filters and results
        """
        filters = self.parse(query_text)
        results = self.execute_query(filters)
        
        return {
            'query': query_text,
            'filters': filters,
            'result_count': len(results),
            'results': results
        }

