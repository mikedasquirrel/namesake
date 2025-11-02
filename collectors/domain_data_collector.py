"""
Domain Data Collector
Populates database with historical domain sales and generates candidates
"""

from core.models import db, Domain, DomainAnalysis
from analyzers.domain_analyzer import DomainAnalyzer
from collectors.namebio_client import NameBioClient
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DomainDataCollector:
    """Collect and generate domain data"""
    
    def __init__(self):
        self.analyzer = DomainAnalyzer()
        self.namebio = NameBioClient()
    
    def collect_real_sales(self, limit=1000, min_price=1000):
        """
        Collect REAL domain sales from NameBio (NO DUMMY DATA)
        
        Args:
            limit: Number of sales to collect
            min_price: Minimum sale price filter
        
        Returns: Statistics on collection
        """
        try:
            logger.info(f"Collecting {limit} real domain sales (min price: ${min_price})")
            
            # Get real sales from NameBio
            real_sales = self.namebio.get_free_tier_data()  # Real verified sales
            
            if not real_sales:
                logger.warning("No sales data available from NameBio")
                return {'domains_added': 0, 'error': 'No data from NameBio'}
            
            logger.info(f"Retrieved {len(real_sales)} verified domain sales")
            
            # Get all domain names for uniqueness analysis
            all_names = [sale['name'] for sale in real_sales]
            
            added_count = 0
            
            for sale in real_sales:
                # Check if already exists
                existing = Domain.query.filter_by(full_domain=sale['domain']).first()
                if existing:
                    continue
                
                # Analyze the domain name
                analysis_results = self.analyzer.analyze_domain(sale['name'], sale['tld'], all_names)
                
                # Create domain record with REAL data
                domain = Domain(
                    name=sale['name'],
                    tld=sale['tld'],
                    full_domain=sale['domain'],
                    is_available=False,  # Sold domains are not available
                    sale_price=sale['price'],
                    sale_date=sale['date'],
                    keyword_score=analysis_results.get('keyword_score', 50),
                    brandability_score=analysis_results.get('brandability_score', 50),
                    tld_premium_multiplier=analysis_results.get('tld_premium_multiplier', 1.0)
                )
                
                db.session.add(domain)
                db.session.flush()
                
                # Create analysis record
                domain_analysis = DomainAnalysis(
                    domain_id=domain.id,
                    syllable_count=analysis_results.get('syllable_count'),
                    character_length=analysis_results.get('character_length'),
                    word_count=analysis_results.get('word_count'),
                    phonetic_score=analysis_results.get('phonetic_score'),
                    vowel_ratio=analysis_results.get('vowel_ratio'),
                    consonant_clusters=analysis_results.get('consonant_clusters'),
                    memorability_score=analysis_results.get('memorability_score'),
                    pronounceability_score=analysis_results.get('pronounceability_score'),
                    name_type=analysis_results.get('name_type'),
                    uniqueness_score=analysis_results.get('uniqueness_score'),
                    analyzed_date=datetime.utcnow()
                )
                
                db.session.add(domain_analysis)
                added_count += 1
            
            db.session.commit()
            
            logger.info(f"✅ Added {added_count} real domain sales to database")
            
            return {
                'domains_added': added_count,
                'total_in_db': Domain.query.count(),
                'source': 'NameBio/Public Records'
            }
        
        except Exception as e:
            logger.error(f"Real domain collection error: {e}")
            db.session.rollback()
            return {'domains_added': 0, 'error': str(e)}
    
    def bootstrap_with_known_sales(self):
        """DEPRECATED - Use collect_real_sales() instead"""
        logger.warning("bootstrap_with_known_sales() is deprecated - use collect_real_sales()")
        return self.collect_real_sales()
    
    def _old_bootstrap_method(self):
        """Old bootstrap method - kept for reference but not used"""
        try:
            # This was the old hardcoded method - replaced with real data collection
            known_sales = [
                {'name': 'voice', 'tld': '.com', 'price': 30000000, 'year': 2019},
                {'name': 'insurance', 'tld': '.com', 'price': 35600000, 'year': 2010},
                {'name': 'fb', 'tld': '.com', 'price': 8500000, 'year': 2010},
                {'name': 'tesla', 'tld': '.com', 'price': 11000000, 'year': 2018},
                {'name': 'zoom', 'tld': '.us', 'price': 2000000, 'year': 2018},
                {'name': 'z', 'tld': '.com', 'price': 6800000, 'year': 2014},
                
                # Tech domains
                {'name': 'block', 'tld': '.one', 'price': 70000, 'year': 2020},
                {'name': 'ai', 'tld': '.com', 'price': 5000000, 'year': 2021},
                {'name': 'crypto', 'tld': '.com', 'price': 1500000, 'year': 2018},
                {'name': 'nft', 'tld': '.com', 'price': 200000, 'year': 2021},
                {'name': 'meta', 'tld': '.com', 'price': 150000, 'year': 2021},
                {'name': 'web3', 'tld': '.com', 'price': 450000, 'year': 2022},
                
                # Medium value tech
                {'name': 'techflow', 'tld': '.io', 'price': 45000, 'year': 2020},
                {'name': 'datacore', 'tld': '.ai', 'price': 85000, 'year': 2023},
                {'name': 'cloudbase', 'tld': '.com', 'price': 120000, 'year': 2019},
                {'name': 'smartchain', 'tld': '.io', 'price': 35000, 'year': 2021},
                {'name': 'nexusai', 'tld': '.com', 'price': 95000, 'year': 2023},
                
                # Portmanteaus
                {'name': 'gigster', 'tld': '.com', 'price': 280000, 'year': 2015},
                {'name': 'cloudera', 'tld': '.com', 'price': 500000, 'year': 2013},
                {'name': 'databricks', 'tld': '.com', 'price': 250000, 'year': 2013},
                
                # Short/premium
                {'name': 'bit', 'tld': '.ly', 'price': 500000, 'year': 2011},
                {'name': 'we', 'tld': '.com', 'price': 8000000, 'year': 2015},
                {'name': 'go', 'tld': '.com', 'price': 750000, 'year': 2015},
                
                # Lower value examples
                {'name': 'techsolutions', 'tld': '.com', 'price': 8500, 'year': 2018},
                {'name': 'webservices', 'tld': '.net', 'price': 3200, 'year': 2017},
                {'name': 'digitalhub', 'tld': '.org', 'price': 2500, 'year': 2019}
            ]
            
            all_names = [s['name'] for s in known_sales]
            count = 0
            
            for sale in known_sales:
                # Check if exists
                full_domain = sale['name'] + sale['tld']
                existing = Domain.query.filter_by(full_domain=full_domain).first()
                
                if existing:
                    continue
                
                # Create domain record
                domain = Domain(
                    name=sale['name'],
                    tld=sale['tld'],
                    full_domain=full_domain,
                    is_available=False,
                    sale_price=sale['price'],
                    sale_date=datetime(sale['year'], 6, 15)  # Mid-year estimate
                )
                
                # Analyze name
                analysis_results = self.analyzer.analyze_domain(sale['name'], sale['tld'], all_names)
                
                domain.keyword_score = analysis_results.get('keyword_score', 50)
                domain.brandability_score = analysis_results.get('brandability_score', 50)
                domain.tld_premium_multiplier = analysis_results.get('tld_premium_multiplier', 1.0)
                
                # Estimate value (should be close to actual sale price)
                value_est = self.analyzer.estimate_value(sale['name'], sale['tld'], analysis_results)
                domain.estimated_value_low = value_est['estimated_value']['low']
                domain.estimated_value_high = value_est['estimated_value']['high']
                
                db.session.add(domain)
                db.session.flush()
                
                # Create domain analysis
                domain_analysis = DomainAnalysis(
                    domain_id=domain.id,
                    syllable_count=analysis_results.get('syllable_count'),
                    character_length=analysis_results.get('character_length'),
                    word_count=analysis_results.get('word_count'),
                    phonetic_score=analysis_results.get('phonetic_score'),
                    vowel_ratio=analysis_results.get('vowel_ratio'),
                    consonant_clusters=analysis_results.get('consonant_clusters'),
                    memorability_score=analysis_results.get('memorability_score'),
                    pronounceability_score=analysis_results.get('pronounceability_score'),
                    name_type=analysis_results.get('name_type'),
                    uniqueness_score=analysis_results.get('uniqueness_score'),
                    analyzed_date=datetime.utcnow()
                )
                
                db.session.add(domain_analysis)
                count += 1
            
            db.session.commit()
            
            logger.info(f"Bootstrapped {count} historical domain sales")
            
            return {'domains_added': count}
        
        except Exception as e:
            logger.error(f"Bootstrap error: {e}")
            db.session.rollback()
            return {'domains_added': 0, 'error': str(e)}
    
    def generate_available_opportunities(self, patterns, tlds=['.com', '.io', '.ai'], count_per_tld=20):
        """
        Generate available domain candidates based on discovered patterns
        
        Args:
            patterns: Patterns from pattern_discovery
            tlds: List of TLDs to check
            count_per_tld: Domains to generate per TLD
        
        Returns: List of generated opportunities
        """
        try:
            opportunities = []
            all_generated_names = []
            
            # Generate based on patterns
            for tld in tlds:
                generated = self.analyzer.generate_domain_candidates(patterns, tld, count_per_tld)
                
                for candidate in generated:
                    # Store in database
                    full_domain = candidate['name'] + tld
                    
                    existing = Domain.query.filter_by(full_domain=full_domain).first()
                    if existing:
                        continue
                    
                    domain = Domain(
                        name=candidate['name'],
                        tld=tld,
                        full_domain=full_domain,
                        is_available=True,  # Assume available for generated ones
                        estimated_value_low=candidate['estimated_value']['low'],
                        estimated_value_high=candidate['estimated_value']['high'],
                        keyword_score=candidate['analysis'].get('keyword_score', 50),
                        brandability_score=candidate['analysis'].get('brandability_score', 50),
                        tld_premium_multiplier=candidate['analysis'].get('tld_premium_multiplier', 1.0)
                    )
                    
                    db.session.add(domain)
                    db.session.flush()
                    
                    # Create analysis
                    domain_analysis = DomainAnalysis(
                        domain_id=domain.id,
                        syllable_count=candidate['analysis'].get('syllable_count'),
                        character_length=candidate['analysis'].get('character_length'),
                        memorability_score=candidate['analysis'].get('memorability_score'),
                        uniqueness_score=candidate['analysis'].get('uniqueness_score'),
                        phonetic_score=candidate['analysis'].get('phonetic_score'),
                        name_type=candidate['analysis'].get('name_type')
                    )
                    
                    db.session.add(domain_analysis)
                    
                    opportunities.append(candidate)
                    all_generated_names.append(candidate['name'])
            
            db.session.commit()
            
            logger.info(f"Generated {len(opportunities)} domain opportunities")
            
            return opportunities
        
        except Exception as e:
            logger.error(f"Opportunity generation error: {e}")
            db.session.rollback()
            return []

