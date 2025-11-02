"""
Domain Name Analyzer
Analyzes web domain names using same methodology as cryptocurrency analysis
"""

from analyzers.name_analyzer import NameAnalyzer
import logging

logger = logging.getLogger(__name__)


class DomainAnalyzer:
    """Analyze domain names for value prediction"""
    
    def __init__(self):
        self.name_analyzer = NameAnalyzer()
        
        # TLD premium multipliers based on market data
        self.tld_multipliers = {
            '.com': 10.0,   # Standard, highest value
            '.io': 7.5,     # Tech affinity
            '.ai': 12.0,    # AI boom premium
            '.co': 3.5,     # Secondary choice
            '.net': 2.5,    # Legacy
            '.org': 1.5,    # Non-profit association
            '.app': 5.0,    # App/tech
            '.dev': 5.5,    # Developer-focused
            '.tech': 4.0,   # Tech generic
            '.xyz': 1.0,    # Base value
            '.blog': 1.2,
            '.store': 2.0,
            '.online': 0.8
        }
        
        # Commercial keywords add value
        self.commercial_keywords = {
            'data': 8, 'cloud': 9, 'tech': 7, 'digital': 6, 'crypto': 8,
            'ai': 10, 'web': 5, 'net': 4, 'app': 7, 'soft': 5,
            'ware': 4, 'sys': 5, 'smart': 6, 'auto': 5, 'bot': 6
        }
    
    def analyze_domain(self, domain_name, tld, all_domain_names=None):
        """
        Analyze a domain name
        
        Args:
            domain_name: Domain without extension (e.g., 'google')
            tld: Top-level domain (e.g., '.com')
            all_domain_names: List of all domains for uniqueness calculation
        
        Returns: dict with analysis results
        """
        try:
            # Use existing name analysis infrastructure
            if all_domain_names is None:
                all_domain_names = [domain_name]
            
            base_analysis = self.name_analyzer.analyze_name(domain_name, all_domain_names)
            
            # Add domain-specific metrics
            tld_score = self._calculate_tld_score(tld)
            keyword_score = self._calculate_keyword_score(domain_name)
            brandability_score = self._calculate_brandability(domain_name, base_analysis)
            
            return {
                **base_analysis,
                'tld': tld,
                'tld_premium_multiplier': tld_score,
                'keyword_score': keyword_score,
                'brandability_score': brandability_score
            }
        
        except Exception as e:
            logger.error(f"Domain analysis error: {e}")
            return None
    
    def _calculate_tld_score(self, tld):
        """Calculate TLD premium multiplier"""
        return self.tld_multipliers.get(tld.lower(), 1.0)
    
    def _calculate_keyword_score(self, domain_name):
        """Calculate commercial keyword value"""
        score = 50  # Base score
        
        domain_lower = domain_name.lower()
        
        # Check for commercial keywords
        for keyword, value in self.commercial_keywords.items():
            if keyword in domain_lower:
                score += value
        
        return min(100, score)
    
    def _calculate_brandability(self, domain_name, base_analysis):
        """Calculate how good the domain is as a brand"""
        score = 0
        
        # Memorability is key for brands
        score += base_analysis.get('memorability_score', 50) * 0.4
        
        # Uniqueness matters
        score += base_analysis.get('uniqueness_score', 50) * 0.3
        
        # Short is better for brands (but not too short)
        length = base_analysis.get('character_length', 7)
        if 4 <= length <= 8:
            score += 100 * 0.2
        elif 3 <= length <= 10:
            score += 70 * 0.2
        else:
            score += 40 * 0.2
        
        # Pronounceability
        score += base_analysis.get('pronounceability_score', 50) * 0.1
        
        return min(100, score)
    
    def estimate_value(self, domain_name, tld, analysis_data=None):
        """
        Estimate domain value based on name analysis
        
        Returns: dict with estimated value range
        """
        try:
            if not analysis_data:
                analysis_data = self.analyze_domain(domain_name, tld)
            
            # Base value calculation
            base_value = 500  # Minimum domain value
            
            # Memorability factor
            memorability = analysis_data.get('memorability_score', 50)
            base_value += (memorability - 50) * 100
            
            # Uniqueness factor
            uniqueness = analysis_data.get('uniqueness_score', 50)
            base_value += (uniqueness - 50) * 80
            
            # Brandability factor
            brandability = analysis_data.get('brandability_score', 50)
            base_value += (brandability - 50) * 120
            
            # Keyword factor
            keyword_score = analysis_data.get('keyword_score', 50)
            base_value += (keyword_score - 50) * 150
            
            # Length premium (shorter is better for domains)
            length = analysis_data.get('character_length', 7)
            if length <= 4:
                base_value *= 5  # Ultra-short premium
            elif length <= 6:
                base_value *= 2.5  # Short premium
            elif length <= 8:
                base_value *= 1.5  # Medium premium
            
            # TLD multiplier
            tld_multiplier = analysis_data.get('tld_premium_multiplier', 1.0)
            base_value *= tld_multiplier
            
            # Add variance for range
            low_estimate = base_value * 0.7
            high_estimate = base_value * 1.8
            
            return {
                'estimated_value': {
                    'low': round(low_estimate, 0),
                    'mid': round(base_value, 0),
                    'high': round(high_estimate, 0)
                },
                'factors': {
                    'memorability_contribution': round((memorability - 50) * 100, 0),
                    'brandability_contribution': round((brandability - 50) * 120, 0),
                    'keyword_contribution': round((keyword_score - 50) * 150, 0),
                    'tld_multiplier': round(tld_multiplier, 1)
                }
            }
        
        except Exception as e:
            logger.error(f"Value estimation error: {e}")
            return None
    
    def generate_domain_candidates(self, patterns, tld='.com', count=100):
        """
        Generate domain candidates based on successful patterns
        
        Args:
            patterns: List of patterns from pattern_discovery
            tld: Target TLD
            count: Number of candidates to generate
        
        Returns: list of generated domain names
        """
        candidates = []
        
        # Use crypto naming patterns to generate domains
        # This is a simple implementation - could be much more sophisticated
        
        prefixes = ['tech', 'data', 'cloud', 'smart', 'auto', 'digital', 'cyber', 'neo', 'next', 'core']
        suffixes = ['hub', 'flow', 'link', 'space', 'zone', 'base', 'sync', 'net', 'wave', 'spark']
        
        for prefix in prefixes:
            for suffix in suffixes:
                if len(candidates) >= count:
                    break
                
                domain_name = prefix + suffix
                full_domain = domain_name + tld
                
                # Analyze
                analysis = self.analyze_domain(domain_name, tld)
                value_estimate = self.estimate_value(domain_name, tld, analysis)
                
                candidates.append({
                    'name': domain_name,
                    'tld': tld,
                    'full_domain': full_domain,
                    'analysis': analysis,
                    'estimated_value': value_estimate['estimated_value'],
                    'score': (analysis.get('memorability_score', 50) + analysis.get('brandability_score', 50)) / 2
                })
        
        # Sort by estimated value
        candidates.sort(key=lambda x: x['estimated_value']['mid'], reverse=True)
        
        return candidates[:count]

