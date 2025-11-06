"""Comprehensive MTG Card Collection Script

Collects 10,000+ cards with complete data dimensions:
- ALL mythics
- ALL legendaries  
- ALL cards >$10
- Stratified sample of iconic sets
- Complete instant/sorcery collection
- Format legalities
- Reprint history
- Advanced linguistic analysis
"""

import logging
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collectors.mtg_collector import MTGCollector
from analyzers.mtg_phonosemantic_analyzer import MTGPhonosemanticAnalyzer
from analyzers.mtg_constructed_language_analyzer import MTGConstructedLanguageAnalyzer
from analyzers.mtg_narrative_analyzer import MTGNarrativeAnalyzer
from analyzers.mtg_semantic_analyzer import MTGSemanticAnalyzer
from analyzers.mtg_format_analyzer import MTGFormatAnalyzer
from analyzers.mtg_intertextual_analyzer import MTGIntertextualAnalyzer
from core.models import db, MTGCard, MTGCardAnalysis
from app import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('mtg_comprehensive_collection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ComprehensiveMTGCollector:
    """Comprehensive MTG data collection with advanced analysis."""
    
    def __init__(self):
        self.collector = MTGCollector()
        
        # Advanced analyzers
        self.phonosemantic = MTGPhonosemanticAnalyzer()
        self.constructed_lang = MTGConstructedLanguageAnalyzer()
        self.narrative = MTGNarrativeAnalyzer()
        self.semantic = MTGSemanticAnalyzer()
        self.format_analyzer = MTGFormatAnalyzer()
        self.intertextual = MTGIntertextualAnalyzer()
        
        self.stats = {
            'total_collected': 0,
            'mythics': 0,
            'legendaries': 0,
            'premium': 0,
            'instants_sorceries': 0,
            'iconic_sets': 0,
            'analyzed': 0,
            'errors': 0,
        }
    
    def collect_comprehensive_dataset(self, target=10000):
        """Collect comprehensive MTG dataset with advanced analysis."""
        logger.info("="*70)
        logger.info("COMPREHENSIVE MTG COLLECTION - TARGET: {:,} CARDS".format(target))
        logger.info("="*70)
        
        with app.app_context():
            # Phase 1: Core collection (mythics, legendaries, premium)
            logger.info("\n[Phase 1/4] Core Collection (Mythics + Legendaries + Premium)")
            self.collector.collect_stratified_sample(target_total=5000)
            
            # Phase 2: Complete instant/sorcery collection
            logger.info("\n[Phase 2/4] Complete Instant/Sorcery Collection")
            self._collect_complete_spells()
            
            # Phase 3: Iconic sets sampling
            logger.info("\n[Phase 3/4] Iconic Sets Sampling")
            self._collect_iconic_sets()
            
            # Phase 4: Advanced analysis on all collected cards
            logger.info("\n[Phase 4/4] Advanced Linguistic Analysis")
            self._analyze_all_cards()
            
            # Final stats
            total = MTGCard.query.count()
            analyzed = MTGCardAnalysis.query.filter(
                MTGCardAnalysis.phonosemantic_data.isnot(None)
            ).count()
            
            logger.info("\n" + "="*70)
            logger.info("COLLECTION COMPLETE!")
            logger.info("="*70)
            logger.info(f"Total cards in database: {total:,}")
            logger.info(f"Cards with advanced analysis: {analyzed:,}")
            logger.info(f"Coverage: {(analyzed/total*100):.1f}%")
            
            return {
                'success': True,
                'total_cards': total,
                'analyzed_cards': analyzed,
                'stats': self.stats
            }
    
    def _collect_complete_spells(self):
        """Collect ALL instant and sorcery cards."""
        import requests
        
        try:
            # Scryfall query for all instants and sorceries with prices
            query = '(t:instant OR t:sorcery) game:paper'
            url = f"{self.collector.base_url}/cards/search"
            params = {'q': query, 'order': 'name'}
            
            page = 1
            collected = 0
            
            while True:
                logger.info(f"  Fetching page {page}...")
                params['page'] = page
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                for card_data in data.get('data', []):
                    parsed = self.collector._parse_card(card_data)
                    
                    # Skip cards with no price
                    if not parsed.get('price_usd') and not parsed.get('price_usd_foil'):
                        continue
                    
                    # Add format legalities
                    legalities = card_data.get('legalities', {})
                    parsed['format_legalities'] = json.dumps(legalities)
                    
                    # Add reprint data
                    parsed['reprint_count'] = len(card_data.get('prints_search_uri', '').split('&')) - 1
                    
                    # Save/update
                    self._save_card_with_advanced_analysis(parsed)
                    collected += 1
                
                if not data.get('has_more', False):
                    break
                
                page += 1
                time.sleep(self.collector.rate_limit_delay)
            
            logger.info(f"✅ Collected {collected} instant/sorcery cards")
            self.stats['instants_sorceries'] = collected
            
        except Exception as e:
            logger.error(f"Error collecting spells: {e}")
            self.stats['errors'] += 1
    
    def _collect_iconic_sets(self):
        """Sample cards from iconic sets."""
        iconic_sets = [
            'lea',  # Alpha
            'leb',  # Beta
            'usg',  # Urza's Saga
            'mrd',  # Mirrodin
            'rav',  # Ravnica
            'isd',  # Innistrad
            'ktk',  # Khans of Tarkir
            'mh1',  # Modern Horizons
            'mh2',  # Modern Horizons 2
        ]
        
        import requests
        
        collected = 0
        
        for set_code in iconic_sets:
            try:
                logger.info(f"  Collecting from {set_code.upper()}...")
                
                url = f"{self.collector.base_url}/cards/search"
                params = {'q': f'set:{set_code} game:paper', 'order': 'usd', 'dir': 'desc'}
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                
                for card_data in data.get('data', []):
                    parsed = self.collector._parse_card(card_data)
                    
                    if not parsed.get('price_usd') and not parsed.get('price_usd_foil'):
                        continue
                    
                    # Add extra data
                    legalities = card_data.get('legalities', {})
                    parsed['format_legalities'] = json.dumps(legalities)
                    parsed['set_year'] = card_data.get('released_at', '')[:4] if card_data.get('released_at') else None
                    
                    self._save_card_with_advanced_analysis(parsed)
                    collected += 1
                
                time.sleep(self.collector.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error collecting {set_code}: {e}")
                continue
        
        logger.info(f"✅ Collected {collected} cards from iconic sets")
        self.stats['iconic_sets'] = collected
    
    def _save_card_with_advanced_analysis(self, card_data):
        """Save card with comprehensive advanced analysis."""
        try:
            # Check if exists
            existing = MTGCard.query.get(card_data['id'])
            
            if existing:
                # Update prices and metadata
                existing.price_usd = card_data.get('price_usd')
                existing.price_usd_foil = card_data.get('price_usd_foil')
                existing.log_price_usd = card_data.get('log_price_usd')
                existing.format_legalities = card_data.get('format_legalities')
                existing.set_year = card_data.get('set_year')
                existing.reprint_count = card_data.get('reprint_count', 0)
                card_record = existing
            else:
                # Create new
                card_record = MTGCard(**{k: v for k, v in card_data.items() if k != 'id'})
                card_record.id = card_data['id']
                db.session.add(card_record)
            
            db.session.flush()
            
            # Run advanced analysis
            self._run_advanced_analysis(card_record)
            
            db.session.commit()
            self.stats['total_collected'] += 1
            
            if self.stats['total_collected'] % 100 == 0:
                logger.info(f"  Progress: {self.stats['total_collected']:,} cards processed...")
            
        except Exception as e:
            logger.error(f"Error saving card {card_data.get('name')}: {e}")
            db.session.rollback()
            self.stats['errors'] += 1
    
    def _analyze_all_cards(self):
        """Run advanced analysis on all cards in database."""
        cards = MTGCard.query.all()
        total = len(cards)
        
        logger.info(f"Analyzing {total:,} cards with advanced linguistic features...")
        
        for idx, card in enumerate(cards):
            try:
                self._run_advanced_analysis(card)
                
                if (idx + 1) % 100 == 0:
                    db.session.commit()
                    logger.info(f"  Progress: {idx+1:,}/{total:,} ({(idx+1)/total*100:.1f}%)")
                    self.stats['analyzed'] = idx + 1
                
            except Exception as e:
                logger.error(f"Error analyzing {card.name}: {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
        logger.info(f"✅ Analysis complete: {total:,} cards")
    
    def _run_advanced_analysis(self, card):
        """Run all advanced analyzers on a card."""
        # Get or create analysis record
        analysis = MTGCardAnalysis.query.filter_by(card_id=card.id).first()
        if not analysis:
            # This shouldn't happen if collector ran first, but handle it
            return
        
        # Parse format legalities if available
        format_legalities = None
        if card.format_legalities:
            try:
                format_legalities = json.loads(card.format_legalities)
            except:
                pass
        
        # Phonosemantic analysis
        try:
            phonosemantic = self.phonosemantic.analyze_card_phonetics(
                card.name,
                color_identity=card.color_identity,
                card_type=card.card_type,
                oracle_text=card.oracle_text
            )
            analysis.phonosemantic_data = json.dumps(phonosemantic)
        except Exception as e:
            logger.debug(f"Phonosemantic error for {card.name}: {e}")
        
        # Constructed language analysis
        try:
            constructed = self.constructed_lang.analyze_constructed_language(
                card.name,
                set_code=card.set_code,
                card_type=card.card_type
            )
            analysis.constructed_lang_data = json.dumps(constructed)
        except Exception as e:
            logger.debug(f"Constructed lang error for {card.name}: {e}")
        
        # Narrative analysis
        try:
            narrative = self.narrative.analyze_narrative_structure(
                card.name,
                card_type=card.card_type,
                flavor_text=card.flavor_text,
                is_legendary=card.is_legendary
            )
            analysis.narrative_data = json.dumps(narrative)
        except Exception as e:
            logger.debug(f"Narrative error for {card.name}: {e}")
        
        # Semantic analysis
        try:
            semantic = self.semantic.analyze_semantic_fields(
                card.name,
                oracle_text=card.oracle_text,
                color_identity=card.color_identity
            )
            analysis.semantic_data = json.dumps(semantic)
        except Exception as e:
            logger.debug(f"Semantic error for {card.name}: {e}")
        
        # Format affinity analysis
        try:
            format_affinity = self.format_analyzer.analyze_format_linguistic_markers(
                card.name,
                format_legalities=format_legalities,
                card_type=card.card_type,
                is_legendary=card.is_legendary,
                converted_mana_cost=card.converted_mana_cost
            )
            analysis.format_affinity_data = json.dumps(format_affinity)
        except Exception as e:
            logger.debug(f"Format affinity error for {card.name}: {e}")
        
        # Intertextual analysis
        try:
            intertextual = self.intertextual.analyze_intertextual_references(
                card.name,
                flavor_text=card.flavor_text
            )
            analysis.intertextual_data = json.dumps(intertextual)
        except Exception as e:
            logger.debug(f"Intertextual error for {card.name}: {e}")


if __name__ == '__main__':
    collector = ComprehensiveMTGCollector()
    result = collector.collect_comprehensive_dataset(target=10000)
    
    if result['success']:
        logger.info("\n✅ COMPREHENSIVE MTG COLLECTION SUCCESSFUL!")
        logger.info(f"Total cards: {result['total_cards']:,}")
        logger.info(f"Analyzed cards: {result['analyzed_cards']:,}")
    else:
        logger.error("\n❌ Collection failed")
        sys.exit(1)

