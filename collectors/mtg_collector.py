"""Magic: The Gathering Card Collector

Collects MTG card data from Scryfall API with intelligent stratified sampling.
Focuses on cards where name matters most: mythics, legendaries, iconic spells.

Target: 3,000-4,000 cards (avoid data overload while capturing high-signal cards)
"""

import logging
import math
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests

from analyzers.name_analyzer import NameAnalyzer
from core.models import MTGCard, MTGCardAnalysis, db

logger = logging.getLogger(__name__)


class MTGCollector:
    """Collect Magic: The Gathering card data from Scryfall API."""
    
    def __init__(self):
        self.analyzer = NameAnalyzer()
        self.base_url = "https://api.scryfall.com"
        self.rate_limit_delay = 0.1  # 100ms between requests (Scryfall requirement)
    
    def collect_stratified_sample(self, target_total=3500):
        """Collect intelligently stratified sample of MTG cards.
        
        Strategy to avoid data overload while maximizing signal:
        - ALL mythic rares (highest value variance, name matters most)
        - ALL legendary creatures (iconic, collectible)
        - Sample of rares (focus on high-price or iconic sets)
        - Minimal commons/uncommons (low price variance, mechanical focus)
        
        Args:
            target_total: Target number of cards (default 3,500)
        
        Returns:
            Collection statistics
        """
        stats = {
            'target': target_total,
            'mythics_collected': 0,
            'legendaries_collected': 0,
            'rares_collected': 0,
            'uncommons_collected': 0,
            'commons_collected': 0,
            'total_added': 0,
            'total_updated': 0,
            'skipped_no_price': 0,
            'errors': 0
        }
        
        try:
            logger.info("Starting stratified MTG card collection...")
            logger.info(f"Target: {target_total} cards")
            
            # Phase 1: ALL mythic rares
            logger.info("\n[Phase 1/4] Collecting ALL mythic rare cards...")
            mythics = self._fetch_by_rarity('mythic', limit=None)
            stats['mythics_collected'] = len(mythics)
            mythic_stats = self._save_cards(mythics, 'mythic rares')
            stats['total_added'] += mythic_stats['added']
            stats['total_updated'] += mythic_stats['updated']
            stats['skipped_no_price'] += mythic_stats['skipped_no_price']
            
            # Phase 2: ALL legendary creatures
            logger.info("\n[Phase 2/4] Collecting ALL legendary creatures...")
            legendaries = self._fetch_legendary_creatures(limit=None)
            stats['legendaries_collected'] = len(legendaries)
            legendary_stats = self._save_cards(legendaries, 'legendary creatures')
            stats['total_added'] += legendary_stats['added']
            stats['total_updated'] += legendary_stats['updated']
            stats['skipped_no_price'] += legendary_stats['skipped_no_price']
            
            # Phase 3: Sample of rares (target ~1000-1500)
            current_total = stats['total_added'] + stats['total_updated']
            rares_target = min(1500, target_total - current_total)
            if rares_target > 0:
                logger.info(f"\n[Phase 3/4] Sampling {rares_target} rare cards...")
                rares = self._fetch_by_rarity('rare', limit=rares_target)
                stats['rares_collected'] = len(rares)
                rare_stats = self._save_cards(rares, 'rares')
                stats['total_added'] += rare_stats['added']
                stats['total_updated'] += rare_stats['updated']
                stats['skipped_no_price'] += rare_stats['skipped_no_price']
            
            # Phase 4: Small sample of uncommons (target ~300-500)
            current_total = stats['total_added'] + stats['total_updated']
            uncommons_target = min(400, max(0, target_total - current_total))
            if uncommons_target > 0:
                logger.info(f"\n[Phase 4/4] Sampling {uncommons_target} uncommon cards...")
                uncommons = self._fetch_by_rarity('uncommon', limit=uncommons_target)
                stats['uncommons_collected'] = len(uncommons)
                uncommon_stats = self._save_cards(uncommons, 'uncommons')
                stats['total_added'] += uncommon_stats['added']
                stats['total_updated'] += uncommon_stats['updated']
                stats['skipped_no_price'] += uncommon_stats['skipped_no_price']
            
            stats['total_in_db'] = MTGCard.query.count()
            
            logger.info(f"\n{'='*60}")
            logger.info("✅ MTG CARD COLLECTION COMPLETE")
            logger.info(f"{'='*60}")
            logger.info(f"Total in database: {stats['total_in_db']}")
            logger.info(f"  Mythics: {stats['mythics_collected']}")
            logger.info(f"  Legendaries: {stats['legendaries_collected']}")
            logger.info(f"  Rares: {stats['rares_collected']}")
            logger.info(f"  Uncommons: {stats['uncommons_collected']}")
            
            return stats
        
        except Exception as e:
            logger.error(f"MTG collection error: {e}")
            db.session.rollback()
            stats['error'] = str(e)
            return stats
    
    def _fetch_by_rarity(self, rarity: str, limit: Optional[int] = None) -> List[Dict]:
        """Fetch cards of specific rarity from Scryfall."""
        cards = []
        page = 1
        
        try:
            # Scryfall search query
            query = f'rarity:{rarity} game:paper'
            
            while True:
                url = f"{self.base_url}/cards/search"
                params = {'q': query, 'page': page, 'order': 'usd', 'dir': 'desc'}
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for card_data in data.get('data', []):
                    cards.append(self._parse_card(card_data))
                    
                    if limit and len(cards) >= limit:
                        return cards
                
                # Check if more pages
                if not data.get('has_more', False):
                    break
                
                page += 1
                time.sleep(self.rate_limit_delay)
                
                if page % 10 == 0:
                    logger.info(f"  Progress: {len(cards)} {rarity} cards collected...")
            
            return cards
        
        except Exception as e:
            logger.error(f"Error fetching {rarity} cards: {e}")
            return cards
    
    def _fetch_legendary_creatures(self, limit: Optional[int] = None) -> List[Dict]:
        """Fetch legendary creatures (high collectability, name-driven value)."""
        cards = []
        page = 1
        
        try:
            query = 't:legendary t:creature game:paper'
            
            while True:
                url = f"{self.base_url}/cards/search"
                params = {'q': query, 'page': page, 'order': 'usd', 'dir': 'desc'}
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for card_data in data.get('data', []):
                    cards.append(self._parse_card(card_data))
                    
                    if limit and len(cards) >= limit:
                        return cards
                
                if not data.get('has_more', False):
                    break
                
                page += 1
                time.sleep(self.rate_limit_delay)
                
                if page % 10 == 0:
                    logger.info(f"  Progress: {len(cards)} legendaries collected...")
            
            return cards
        
        except Exception as e:
            logger.error(f"Error fetching legendary creatures: {e}")
            return cards
    
    def _parse_card(self, card_data: Dict) -> Dict:
        """Parse Scryfall card JSON into our schema."""
        # Extract prices
        prices = card_data.get('prices', {})
        price_usd = self._parse_price(prices.get('usd'))
        price_usd_foil = self._parse_price(prices.get('usd_foil'))
        price_eur = self._parse_price(prices.get('eur'))
        
        # Parse card type
        type_line = card_data.get('type_line', '')
        is_creature = 'Creature' in type_line
        is_legendary = 'Legendary' in type_line
        is_instant_sorcery = 'Instant' in type_line or 'Sorcery' in type_line
        
        # Rarity tier
        rarity_map = {'common': 1, 'uncommon': 2, 'rare': 3, 'mythic': 4}
        rarity = card_data.get('rarity', 'common')
        
        # Color identity
        colors = card_data.get('color_identity', [])
        color_identity = ''.join(sorted(colors)) if colors else 'C'  # C = colorless
        
        # Release date
        released_at = card_data.get('released_at')
        release_date = datetime.fromisoformat(released_at).date() if released_at else None
        
        return {
            'id': card_data.get('id'),
            'name': card_data.get('name'),
            'set_code': card_data.get('set'),
            'set_name': card_data.get('set_name'),
            'rarity': rarity,
            'mana_cost': card_data.get('mana_cost'),
            'converted_mana_cost': card_data.get('cmc'),
            'card_type': type_line,
            'power': card_data.get('power'),
            'toughness': card_data.get('toughness'),
            'price_usd': price_usd,
            'price_usd_foil': price_usd_foil,
            'price_eur': price_eur,
            'edhrec_rank': card_data.get('edhrec_rank'),
            'artist': card_data.get('artist'),
            'flavor_text': card_data.get('flavor_text'),
            'oracle_text': card_data.get('oracle_text'),
            'release_date': release_date,
            'log_price_usd': math.log(price_usd) if price_usd and price_usd > 0 else None,
            'rarity_tier': rarity_map.get(rarity, 1),
            'is_legendary': is_legendary,
            'is_creature': is_creature,
            'is_instant_sorcery': is_instant_sorcery,
            'color_identity': color_identity
        }
    
    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """Parse price string to float."""
        if not price_str:
            return None
        try:
            return float(price_str)
        except (ValueError, TypeError):
            return None
    
    def _save_cards(self, cards: List[Dict], category_name: str) -> Dict:
        """Save cards to database with name analysis."""
        stats = {'added': 0, 'updated': 0, 'skipped_no_price': 0, 'errors': 0}
        
        # Get all card names for uniqueness analysis
        all_card_names = [c['name'] for c in cards if c.get('name')]
        
        for idx, card_data in enumerate(cards):
            try:
                # Skip cards with no price data (bulk commons, unreleased, etc.)
                if not card_data.get('price_usd') and not card_data.get('price_usd_foil'):
                    stats['skipped_no_price'] += 1
                    continue
                
                # Check if exists
                existing = MTGCard.query.get(card_data['id'])
                
                if existing:
                    # Update prices (they fluctuate)
                    existing.price_usd = card_data.get('price_usd')
                    existing.price_usd_foil = card_data.get('price_usd_foil')
                    existing.price_eur = card_data.get('price_eur')
                    existing.log_price_usd = card_data.get('log_price_usd')
                    existing.edhrec_rank = card_data.get('edhrec_rank')
                    card_record = existing
                    stats['updated'] += 1
                else:
                    # Create new
                    card_record = MTGCard(**{k: v for k, v in card_data.items() if k != 'id'})
                    card_record.id = card_data['id']
                    db.session.add(card_record)
                    stats['added'] += 1
                
                db.session.flush()
                
                # Analyze card name
                self._analyze_card_name(card_record, all_card_names, card_data.get('flavor_text'))
                
                # Batch commit every 50 cards
                if (stats['added'] + stats['updated']) % 50 == 0:
                    db.session.commit()
                    logger.info(f"  {category_name}: {stats['added'] + stats['updated']} processed...")
            
            except Exception as e:
                logger.error(f"Error saving card {card_data.get('name', 'unknown')}: {e}")
                stats['errors'] += 1
                db.session.rollback()
                continue
        
        db.session.commit()
        logger.info(f"✅ {category_name}: {stats['added']} added, {stats['updated']} updated")
        
        return stats
    
    def _analyze_card_name(self, card: MTGCard, all_names: List[str], flavor_text: Optional[str]):
        """Analyze card name with standard + MTG-specific metrics."""
        # Standard analysis
        standard_analysis = self.analyzer.analyze_name(card.name, all_names)
        
        # MTG-specific analysis
        fantasy_score = self._calculate_fantasy_score(card.name)
        power_connotation = self._calculate_power_connotation(card.name)
        mythic_resonance = self._calculate_mythic_resonance(card.name, card.is_legendary)
        flavor_sentiment = self._analyze_flavor_sentiment(flavor_text) if flavor_text else 0.0
        constructed_lang = self._calculate_constructed_language_score(card.name)
        
        # Check if analysis exists
        existing_analysis = MTGCardAnalysis.query.filter_by(card_id=card.id).first()
        
        if existing_analysis:
            # Update
            existing_analysis.syllable_count = standard_analysis.get('syllable_count')
            existing_analysis.character_length = standard_analysis.get('character_length')
            existing_analysis.word_count = standard_analysis.get('word_count')
            existing_analysis.phonetic_score = standard_analysis.get('phonetic_score')
            existing_analysis.vowel_ratio = standard_analysis.get('vowel_ratio')
            existing_analysis.memorability_score = standard_analysis.get('memorability_score')
            existing_analysis.pronounceability_score = standard_analysis.get('pronounceability_score')
            existing_analysis.uniqueness_score = standard_analysis.get('uniqueness_score')
            existing_analysis.name_type = standard_analysis.get('name_type')
            existing_analysis.fantasy_score = fantasy_score
            existing_analysis.power_connotation_score = power_connotation
            existing_analysis.mythic_resonance_score = mythic_resonance
            existing_analysis.flavor_text_sentiment = flavor_sentiment
            existing_analysis.constructed_language_score = constructed_lang
        else:
            # Create new
            analysis = MTGCardAnalysis(
                card_id=card.id,
                syllable_count=standard_analysis.get('syllable_count'),
                character_length=standard_analysis.get('character_length'),
                word_count=standard_analysis.get('word_count'),
                phonetic_score=standard_analysis.get('phonetic_score'),
                vowel_ratio=standard_analysis.get('vowel_ratio'),
                memorability_score=standard_analysis.get('memorability_score'),
                pronounceability_score=standard_analysis.get('pronounceability_score'),
                uniqueness_score=standard_analysis.get('uniqueness_score'),
                name_type=standard_analysis.get('name_type'),
                fantasy_score=fantasy_score,
                power_connotation_score=power_connotation,
                mythic_resonance_score=mythic_resonance,
                flavor_text_sentiment=flavor_sentiment,
                constructed_language_score=constructed_lang
            )
            db.session.add(analysis)
    
    def _calculate_fantasy_score(self, name: str) -> float:
        """Calculate how fantasy/medieval the name sounds (0-100).
        
        Indicators:
        - Apostrophes (e.g., Ur-Dragon, Ko'rish)
        - Fantasy suffixes (-ax, -or, -ath, -on, -el)
        - Multiple capitals (ElSpeth, JhoIra)
        - Archaic patterns (the, of the)
        """
        score = 50.0  # Baseline
        name_lower = name.lower()
        
        # Apostrophes and hyphens (constructed names)
        if "'" in name or '-' in name:
            score += 15
        
        # Fantasy suffixes
        fantasy_suffixes = ['ax', 'or', 'ath', 'on', 'el', 'ar', 'us', 'os', 'ix', 'ur', 'og']
        if any(name_lower.endswith(suffix) for suffix in fantasy_suffixes):
            score += 20
        
        # Multiple capital letters (CamelCase legendary names)
        capitals = sum(1 for c in name if c.isupper())
        if capitals > 1 and len(name) > 1:
            score += 10
        
        # Archaic articles
        if name_lower.startswith(('the ', 'of the', 'lord of', 'master of')):
            score += 15
        
        # Long multi-word names (epic feel)
        word_count = len(name.split())
        if word_count >= 3:
            score += 10
        
        # Uncommon letter combinations (fantasy constructed languages)
        rare_combos = ['zz', 'kh', 'zh', 'xh', 'qx', "'s", "k'"]
        if any(combo in name_lower for combo in rare_combos):
            score += 10
        
        return round(min(100, max(0, score)), 2)
    
    def _calculate_power_connotation(self, name: str) -> float:
        """Calculate aggressive vs. gentle power connotation (-100 to +100).
        
        Positive (aggressive): Death, Destroy, Dragon, Wrath, Annihilate
        Negative (gentle/peaceful): Healing, Peace, Mend, Serene, Gentle
        """
        name_lower = name.lower()
        
        aggressive_words = {
            'death', 'destroy', 'kill', 'dragon', 'wrath', 'annihilate', 'obliterate',
            'doom', 'rage', 'fury', 'slaughter', 'massacre', 'terminate', 'murder',
            'chaos', 'havoc', 'devastation', 'catastrophe', 'apocalypse', 'carnage',
            'butcher', 'slay', 'vanquish', 'crush', 'smash', 'demolish'
        }
        
        gentle_words = {
            'heal', 'peace', 'mend', 'serene', 'gentle', 'tranquil', 'calm', 'soothe',
            'nurture', 'harmony', 'blessing', 'grace', 'mercy', 'kindness', 'compassion',
            'life', 'growth', 'flourish', 'bloom', 'restore'
        }
        
        aggressive_count = sum(1 for word in aggressive_words if word in name_lower)
        gentle_count = sum(1 for word in gentle_words if word in name_lower)
        
        # Net score
        if aggressive_count == 0 and gentle_count == 0:
            return 0.0
        
        net_score = (aggressive_count - gentle_count) / max(aggressive_count + gentle_count, 1) * 100
        return round(net_score, 2)
    
    def _calculate_mythic_resonance(self, name: str, is_legendary: bool) -> float:
        """Calculate epic/legendary linguistic quality (0-100).
        
        Factors:
        - Title words (Lord, Master, King, Queen)
        - Epic scale (Ancient, Eternal, Infinite, Primordial)
        - Legendary status (boost if mechanically legendary)
        - Syllable length (longer = more epic)
        """
        score = 40.0  # Baseline
        name_lower = name.lower()
        
        # Title words
        titles = ['lord', 'master', 'king', 'queen', 'emperor', 'god', 'goddess', 
                  'champion', 'elder', 'ancient', 'primordial', 'eternal']
        if any(title in name_lower for title in titles):
            score += 25
        
        # Epic scale words
        epic_words = ['infinite', 'eternal', 'supreme', 'ultimate', 'primal', 'cosmic',
                      'void', 'abyss', 'immortal', 'omnipotent', 'divine']
        if any(word in name_lower for word in epic_words):
            score += 20
        
        # Mechanical legendary status
        if is_legendary:
            score += 15
        
        # Syllable length (more syllables = more epic)
        syllables = self.analyzer._count_syllables(name)
        if syllables >= 4:
            score += 10
        elif syllables >= 3:
            score += 5
        
        # Comma (indicates legendary title structure: "Name, Title")
        if ',' in name:
            score += 10
        
        return round(min(100, max(0, score)), 2)
    
    def _analyze_flavor_sentiment(self, flavor_text: str) -> float:
        """Analyze sentiment polarity of flavor text (-1.0 to +1.0)."""
        if not flavor_text:
            return 0.0
        
        flavor_lower = flavor_text.lower()
        
        positive_markers = ['triumph', 'victory', 'hope', 'light', 'glory', 'courage', 
                           'joy', 'peace', 'beauty', 'wonder', 'magnificent']
        negative_markers = ['doom', 'death', 'despair', 'darkness', 'fear', 'terror',
                           'horror', 'suffering', 'anguish', 'devastation', 'ruin']
        
        positive_count = sum(1 for word in positive_markers if word in flavor_lower)
        negative_count = sum(1 for word in negative_markers if word in flavor_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        polarity = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        return round(polarity, 2)
    
    def _calculate_constructed_language_score(self, name: str) -> float:
        """Calculate how much name sounds like constructed language (0-100).
        
        Indicators:
        - Apostrophes mid-word
        - Double consonants (Llanowar, Thraximundar)
        - X, Q, Z heavy usage
        - Vowel-final with hard consonant prefix
        """
        score = 0.0
        name_lower = name.lower()
        
        # Apostrophes (strong indicator)
        if "'" in name:
            score += 30
        
        # Rare letters
        rare_letters = ['x', 'q', 'z', 'k']
        rare_count = sum(name_lower.count(c) for c in rare_letters)
        score += min(rare_count * 10, 30)
        
        # Double consonants
        double_consonants = ['ll', 'rr', 'th', 'kk', 'zz']
        if any(combo in name_lower for combo in double_consonants):
            score += 20
        
        # Ends with vowel after hard consonants (Elvish pattern)
        if len(name_lower) > 2 and name_lower[-1] in 'aeiou' and name_lower[-2] in 'kzxq':
            score += 20
        
        return round(min(100, score), 2)



