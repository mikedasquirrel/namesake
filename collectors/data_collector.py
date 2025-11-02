from core.models import db, Cryptocurrency, PriceHistory, NameAnalysis
from collectors.api_client import CoinGeckoClient
from analyzers.name_analyzer import NameAnalyzer
from analyzers.advanced_analyzer import AdvancedAnalyzer
from analyzers.esoteric_analyzer import EsotericAnalyzer
from datetime import datetime, date
import logging
import json

logger = logging.getLogger(__name__)


class DataCollector:
    """Orchestrates data collection and analysis"""
    
    def __init__(self):
        self.api_client = CoinGeckoClient()
        self.name_analyzer = NameAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.esoteric_analyzer = EsotericAnalyzer()
    
    def collect_all_data(self, limit=500):
        """
        Main data collection workflow
        
        Args:
            limit: Number of top cryptocurrencies to collect
            
        Returns:
            Dict with collection statistics
        """
        logger.info(f"Starting data collection for top {limit} cryptocurrencies...")
        
        stats = {
            'cryptocurrencies_added': 0,
            'cryptocurrencies_updated': 0,
            'price_histories_added': 0,
            'name_analyses_added': 0,
            'errors': []
        }
        
        # Fetch top cryptocurrencies
        cryptos = self.api_client.get_top_cryptocurrencies(limit)
        if not cryptos:
            logger.error("Failed to fetch cryptocurrencies from API")
            stats['errors'].append("Failed to fetch data from CoinGecko API")
            return stats
        
        logger.info(f"Fetched {len(cryptos)} cryptocurrencies from API")
        
        # Process each cryptocurrency
        for i, crypto_data in enumerate(cryptos, 1):
            logger.info(f"Processing {i}/{len(cryptos)}: {crypto_data['name']}")
            
            try:
                # Store or update cryptocurrency
                crypto = self._process_cryptocurrency(crypto_data)
                if crypto:
                    if i <= limit:  # Only count new ones
                        if db.session.query(Cryptocurrency).filter_by(id=crypto.id).first():
                            stats['cryptocurrencies_updated'] += 1
                        else:
                            stats['cryptocurrencies_added'] += 1
                    
                    # Fetch and store price history
                    history_added = self._process_price_history(crypto)
                    stats['price_histories_added'] += history_added
                    
                    db.session.commit()
                    
            except Exception as e:
                logger.error(f"Error processing {crypto_data.get('name', 'unknown')}: {e}")
                stats['errors'].append(f"{crypto_data.get('name', 'unknown')}: {str(e)}")
                db.session.rollback()
        
        # Perform name analysis on all cryptocurrencies
        logger.info("Performing name analysis...")
        analysis_stats = self._analyze_all_names()
        stats['name_analyses_added'] = analysis_stats['analyses_added']
        
        logger.info(f"Data collection complete: {stats}")
        return stats
    
    def _process_cryptocurrency(self, crypto_data):
        """Process and store a single cryptocurrency"""
        crypto_id = crypto_data['id']
        
        # Check if exists
        crypto = Cryptocurrency.query.filter_by(id=crypto_id).first()
        
        if not crypto:
            crypto = Cryptocurrency(id=crypto_id)
        
        # Update fields
        crypto.name = crypto_data['name']
        crypto.symbol = crypto_data['symbol'].upper()
        crypto.rank = crypto_data.get('market_cap_rank')
        crypto.market_cap = crypto_data.get('market_cap')
        crypto.current_price = crypto_data.get('current_price')
        crypto.total_volume = crypto_data.get('total_volume')
        crypto.circulating_supply = crypto_data.get('circulating_supply')
        crypto.max_supply = crypto_data.get('max_supply')
        crypto.ath = crypto_data.get('ath')
        
        # Parse ATH date
        ath_date = crypto_data.get('ath_date')
        if ath_date:
            try:
                crypto.ath_date = datetime.fromisoformat(ath_date.replace('Z', '+00:00'))
            except:
                crypto.ath_date = None
        
        crypto.last_updated = datetime.utcnow()
        
        db.session.add(crypto)
        return crypto
    
    def _process_price_history(self, crypto):
        """Fetch and store price history for a cryptocurrency"""
        logger.info(f"Fetching price history for {crypto.name}...")
        
        history_data = self.api_client.get_price_history(crypto.id, days=365)
        if not history_data:
            logger.warning(f"No price history available for {crypto.name}")
            return 0
        
        # Calculate performance metrics
        metrics = self.api_client.calculate_performance_metrics(history_data)
        
        # Delete old price history
        PriceHistory.query.filter_by(crypto_id=crypto.id).delete()
        
        # Store new price history
        count = 0
        for entry in history_data:
            price_hist = PriceHistory(
                crypto_id=crypto.id,
                date=entry['date'],
                price=entry['price'],
                market_cap=entry.get('market_cap'),
                volume=entry.get('volume'),
                price_30d_change=metrics.get('price_30d_change'),
                price_90d_change=metrics.get('price_90d_change'),
                price_1yr_change=metrics.get('price_1yr_change'),
                price_ath_change=metrics.get('price_ath_change')
            )
            db.session.add(price_hist)
            count += 1
        
        return count
    
    def _analyze_all_names(self):
        """Perform name analysis on all cryptocurrencies"""
        stats = {'analyses_added': 0}
        
        # Get all cryptocurrencies
        all_cryptos = Cryptocurrency.query.all()
        all_names = [c.name for c in all_cryptos]
        
        logger.info(f"Analyzing {len(all_cryptos)} cryptocurrency names...")
        
        for crypto in all_cryptos:
            try:
                # Check if analysis exists
                analysis = NameAnalysis.query.filter_by(crypto_id=crypto.id).first()
                if not analysis:
                    analysis = NameAnalysis(crypto_id=crypto.id)
                
                # Perform basic analysis
                results = self.name_analyzer.analyze_name(crypto.name, all_names)
                
                # Store basic results
                analysis.syllable_count = results['syllable_count']
                analysis.character_length = results['character_length']
                analysis.word_count = results['word_count']
                analysis.phonetic_score = results['phonetic_score']
                analysis.vowel_ratio = results['vowel_ratio']
                analysis.consonant_clusters = results['consonant_clusters']
                analysis.memorability_score = results['memorability_score']
                analysis.pronounceability_score = results['pronounceability_score']
                analysis.name_type = results['name_type']
                analysis.category_tags = json.dumps(results['category_tags'])
                analysis.uniqueness_score = results['uniqueness_score']
                analysis.avg_similarity_distance = results['avg_similarity_distance']
                analysis.closest_match = results['closest_match']
                analysis.closest_match_distance = results['closest_match_distance']
                analysis.has_numbers = results['has_numbers']
                analysis.has_special_chars = results['has_special_chars']
                analysis.capital_pattern = results['capital_pattern']
                analysis.is_real_word = results['is_real_word']
                analysis.semantic_category = results['semantic_category']
                
                # Perform advanced analysis
                advanced_results = self.advanced_analyzer.analyze(crypto.name, all_names)
                
                # Perform deep linguistic feature extraction
                try:
                    from analyzers.linguistic_feature_extractor import LinguisticFeatureExtractor
                    ling_extractor = LinguisticFeatureExtractor()
                    linguistic_features = ling_extractor.extract_all_features(crypto.name)
                    
                    # Merge linguistic features into advanced_metrics
                    advanced_results['linguistic_features'] = linguistic_features
                except Exception as e:
                    logger.warning(f"Could not extract linguistic features for {crypto.name}: {e}")
                
                analysis.advanced_metrics = json.dumps(advanced_results)
                
                # Perform esoteric analysis
                esoteric_results = self.esoteric_analyzer.analyze(crypto.name, crypto.ath_date)
                analysis.esoteric_metrics = json.dumps(esoteric_results)
                
                analysis.analyzed_date = datetime.utcnow()
                
                db.session.add(analysis)
                stats['analyses_added'] += 1
                
            except Exception as e:
                logger.error(f"Error analyzing {crypto.name}: {e}")
        
        # Calculate scarcity metrics (second pass)
        all_analyses = NameAnalysis.query.all()
        for analysis in all_analyses:
            scarcity = self.name_analyzer.calculate_scarcity_metrics(
                analysis.name_type, all_analyses
            )
            analysis.name_type_count = scarcity['name_type_count']
            analysis.name_type_percentile = scarcity['name_type_percentile']
        
        db.session.commit()
        logger.info(f"Name analysis complete: {stats}")
        
        return stats
    
    def update_price_data(self):
        """Update price data for existing cryptocurrencies"""
        logger.info("Updating price data for existing cryptocurrencies...")
        
        all_cryptos = Cryptocurrency.query.all()
        updated = 0
        
        for crypto in all_cryptos:
            try:
                # Fetch latest price data
                details = self.api_client.get_coin_details(crypto.id)
                if details:
                    crypto.current_price = details.get('market_data', {}).get('current_price', {}).get('usd')
                    crypto.market_cap = details.get('market_data', {}).get('market_cap', {}).get('usd')
                    crypto.last_updated = datetime.utcnow()
                    updated += 1
                    
            except Exception as e:
                logger.error(f"Error updating {crypto.name}: {e}")
        
        db.session.commit()
        logger.info(f"Updated {updated} cryptocurrencies")
        
        return {'updated': updated}
    
    def get_collection_status(self):
        """Get current status of data collection"""
        crypto_count = Cryptocurrency.query.count()
        analysis_count = NameAnalysis.query.count()
        
        latest_crypto = Cryptocurrency.query.order_by(
            Cryptocurrency.last_updated.desc()
        ).first()
        
        latest_analysis = NameAnalysis.query.order_by(
            NameAnalysis.analyzed_date.desc()
        ).first()
        
        return {
            'total_cryptocurrencies': crypto_count,
            'total_analyses': analysis_count,
            'last_crypto_update': latest_crypto.last_updated.isoformat() if latest_crypto else None,
            'last_analysis_update': latest_analysis.analyzed_date.isoformat() if latest_analysis else None,
            'api_status': 'connected' if self.api_client.ping() else 'disconnected'
        }

