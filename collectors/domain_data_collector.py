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
    
    def collect_real_sales(self, limit=500, min_price=10000, tlds=None, earliest_year=2005):
        """Collect verified historical domain sales with quality gating."""
        stats = {
            'requested_limit': limit,
            'min_price': min_price,
            'earliest_year': earliest_year,
            'domains_added': 0,
            'skipped_existing': 0,
            'skipped_low_price': 0,
            'skipped_invalid': 0,
            'skipped_tld': 0,
            'skipped_analysis': 0
        }
        try:
            raw_sales = self.namebio.get_free_tier_data()
            if not raw_sales:
                logger.warning("No sales data available from NameBio sources")
                stats['message'] = 'No data from NameBio'
                return stats
            normalized_tlds = {t.lower().lstrip('.') for t in tlds} if tlds else None
            existing_full_domains = {
                (full_domain or '').lower()
                for (full_domain,) in db.session.query(Domain.full_domain).all()
                if full_domain
            }
            all_domain_names = [name for (name,) in db.session.query(Domain.name).all() if name]
            seen_this_run = set()
            for sale in raw_sales:
                if stats['domains_added'] >= limit:
                    break
                normalized = self._normalize_sale(sale)
                if not normalized:
                    stats['skipped_invalid'] += 1
                    continue
                if normalized_tlds and normalized['tld'].lstrip('.') not in normalized_tlds:
                    stats['skipped_tld'] += 1
                    continue
                if normalized['price'] < min_price:
                    stats['skipped_low_price'] += 1
                    continue
                if normalized['sale_date'] and normalized['sale_date'].year < earliest_year:
                    stats['skipped_invalid'] += 1
                    continue
                domain_key = normalized['full_domain'].lower()
                if domain_key in existing_full_domains or domain_key in seen_this_run:
                    stats['skipped_existing'] += 1
                    continue
                analysis_results = self.analyzer.analyze_domain(
                    normalized['name'],
                    normalized['tld'],
                    all_domain_names or None
                )
                if not analysis_results:
                    stats['skipped_analysis'] += 1
                    continue
                valuation = self.analyzer.estimate_value(
                    normalized['name'],
                    normalized['tld'],
                    analysis_results
                ) or {}
                domain = Domain(
                    name=normalized['name'],
                    tld=normalized['tld'],
                    full_domain=normalized['full_domain'],
                    is_available=False,
                    sale_price=normalized['price'],
                    sale_date=normalized['sale_date'],
                    keyword_score=analysis_results.get('keyword_score'),
                    brandability_score=analysis_results.get('brandability_score'),
                    tld_premium_multiplier=analysis_results.get('tld_premium_multiplier'),
                    days_on_market=None
                )
                estimated = valuation.get('estimated_value', {})
                domain.estimated_value_low = estimated.get('low')
                domain.estimated_value_high = estimated.get('high')
                db.session.add(domain)
                db.session.flush()
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
                stats['domains_added'] += 1
                seen_this_run.add(domain_key)
                all_domain_names.append(normalized['name'])
            db.session.commit()
            stats['total_in_db'] = Domain.query.count()
            logger.info("Added %s domain sales (limit=%s)", stats['domains_added'], limit)
            return stats
        except Exception as e:
            logger.error(f"Real domain collection error: {e}")
            db.session.rollback()
            stats['error'] = str(e)
            return stats
    
    def _normalize_sale(self, sale):
        domain_str = sale.get('domain') or sale.get('name')
        if not domain_str:
            return None
        name, tld = self._split_domain(domain_str)
        if not name or not tld:
            return None
        price = sale.get('price')
        try:
            price_val = float(price)
        except (TypeError, ValueError):
            return None
        sale_date = sale.get('date')
        if isinstance(sale_date, str):
            try:
                sale_date = datetime.fromisoformat(sale_date)
            except ValueError:
                return None
        elif sale_date and not isinstance(sale_date, datetime):
            return None
        return {
            'name': name,
            'tld': tld,
            'full_domain': f"{name}{tld}",
            'price': price_val,
            'sale_date': sale_date,
            'source': sale.get('source')
        }
    
    def _split_domain(self, full_domain):
        cleaned = (full_domain or '').strip().lower()
        if '.' not in cleaned:
            return cleaned, ''
        parts = cleaned.rsplit('.', 1)
        name = parts[0]
        tld = f".{parts[1]}"
        return name, tld
    
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

