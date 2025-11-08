"""
Unified Domain Model - EXTENDED with All Available Domains

Adds loaders for all 15+ domains in your database:
- Web Domains, Stocks, Films, Books, Hurricanes
- MTG Cards, Bands, NBA, NFL, Mental Health, Academics
- Plus existing: Crypto, Elections, Ships, Board Games, MLB

This is the FULL multi-domain nominative determinism research platform.
"""

from typing import Dict, List, Optional, Tuple
from core.unified_domain_model import (
    DomainLoader, UnifiedDomainEntity, DomainType, 
    CryptoLoader, ElectionLoader, ShipLoader, BoardGameLoader, MLBPlayerLoader,
    UnifiedDomainInterface
)
from core.models import (
    db, Domain, DomainAnalysis, Stock, StockAnalysis,
    Film, FilmAnalysis, Book, BookAnalysis,
    Hurricane, HurricaneAnalysis, MTGCard, MTGCardAnalysis,
    Band, BandAnalysis, NBAPlayer, NBAPlayerAnalysis,
    NFLPlayer, NFLPlayerAnalysis, MentalHealthTerm, MentalHealthAnalysis,
    Academic, AcademicAnalysis
)
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# Extend DomainType enum
class ExtendedDomainType(Enum):
    """All available research domains"""
    # Original 5
    CRYPTO = "crypto"
    ELECTION = "election"
    SHIP = "ship"
    BOARD_GAME = "board_game"
    MLB_PLAYER = "mlb_player"
    
    # New additions
    WEB_DOMAIN = "web_domain"
    STOCK = "stock"
    FILM = "film"
    BOOK = "book"
    HURRICANE = "hurricane"
    MTG_CARD = "mtg_card"
    BAND = "band"
    NBA_PLAYER = "nba_player"
    NFL_PLAYER = "nfl_player"
    MENTAL_HEALTH = "mental_health"
    ACADEMIC = "academic"


class WebDomainLoader(DomainLoader):
    """Loader for web domains (domain names)"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.WEB_DOMAIN)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Domain, DomainAnalysis).join(
            DomainAnalysis, Domain.id == DomainAnalysis.domain_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for domain, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'length', len(domain.domain_name)),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'brandability_score': getattr(analysis, 'brandability_score', 0.5),
                    'pronounceability_score': getattr(analysis, 'pronounceability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'word_count': getattr(analysis, 'word_count', 1),
                }
            
            # Outcome: Some metric of domain value/success
            outcome = getattr(domain, 'value_estimate', getattr(domain, 'traffic_rank', None))
            is_successful = outcome and outcome > 1000 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=domain.domain_name,
                domain=ExtendedDomainType.WEB_DOMAIN,
                entity_id=str(domain.id),
                outcome_metric=outcome,
                outcome_metric_name="domain_value",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'tld': getattr(domain, 'tld', None),
                    'registered_year': getattr(domain, 'registered_year', None),
                }
            )
            entities.append(entity)
        
        return entities


class StockLoader(DomainLoader):
    """Loader for stocks/companies"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.STOCK)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Stock, StockAnalysis).join(
            StockAnalysis, Stock.id == StockAnalysis.stock_id, isouter=True
        )
        
        if filters.get('min_market_cap'):
            query = query.filter(Stock.market_cap >= filters['min_market_cap'])
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for stock, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(stock.name)),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'innovation_score': getattr(analysis, 'innovation_score', 0.5),
                    'authority_score': getattr(analysis, 'authority_score', 50.0),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'word_count': getattr(analysis, 'word_count', 1),
                }
            
            # Outcome: Market cap or stock performance
            import math
            outcome = None
            if hasattr(stock, 'market_cap') and stock.market_cap and stock.market_cap > 0:
                outcome = math.log10(stock.market_cap)
            
            is_successful = stock.market_cap and stock.market_cap > 1e9 if hasattr(stock, 'market_cap') else False
            
            entity = UnifiedDomainEntity(
                name=stock.name,
                domain=ExtendedDomainType.STOCK,
                entity_id=str(stock.id),
                outcome_metric=outcome,
                outcome_metric_name="log_market_cap",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'symbol': getattr(stock, 'symbol', None),
                    'sector': getattr(stock, 'sector', None),
                }
            )
            entities.append(entity)
        
        return entities


class HurricaneLoader(DomainLoader):
    """Loader for hurricanes"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.HURRICANE)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Hurricane, HurricaneAnalysis).join(
            HurricaneAnalysis, Hurricane.id == HurricaneAnalysis.hurricane_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for hurricane, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(hurricane.name)),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'gender_association': getattr(analysis, 'gender_association', 'neutral'),
                }
            
            # Outcome: Hurricane intensity/damage
            outcome = getattr(hurricane, 'max_wind_speed', getattr(hurricane, 'damage_millions', None))
            is_successful = outcome and outcome > 100 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=hurricane.name,
                domain=ExtendedDomainType.HURRICANE,
                entity_id=str(hurricane.id),
                outcome_metric=outcome,
                outcome_metric_name="intensity",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'year': getattr(hurricane, 'year', None),
                    'category': getattr(hurricane, 'category', None),
                }
            )
            entities.append(entity)
        
        return entities


class MTGCardLoader(DomainLoader):
    """Loader for Magic: The Gathering cards"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.MTG_CARD)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(MTGCard, MTGCardAnalysis).join(
            MTGCardAnalysis, MTGCard.id == MTGCardAnalysis.card_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for card, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(card.name)),
                    'word_count': getattr(analysis, 'word_count', 1),
                    'fantasy_score': getattr(analysis, 'fantasy_score', 0.5),
                    'power_score': getattr(analysis, 'power_score', 0.5),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Card power/rarity/price
            outcome = getattr(card, 'edhrec_rank', getattr(card, 'price_usd', None))
            is_successful = outcome and outcome > 50 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=card.name,
                domain=ExtendedDomainType.MTG_CARD,
                entity_id=str(card.id),
                outcome_metric=outcome,
                outcome_metric_name="card_rank",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'color': getattr(card, 'colors', None),
                    'type': getattr(card, 'type_line', None),
                }
            )
            entities.append(entity)
        
        return entities


class BandLoader(DomainLoader):
    """Loader for music bands/artists"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.BAND)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis, Band.id == BandAnalysis.band_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for band, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(band.name)),
                    'word_count': getattr(analysis, 'word_count', 1),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'edginess_score': getattr(analysis, 'edginess_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Popularity/success
            outcome = getattr(band, 'listeners', getattr(band, 'albums_sold', None))
            is_successful = outcome and outcome > 100000 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=band.name,
                domain=ExtendedDomainType.BAND,
                entity_id=str(band.id),
                outcome_metric=outcome,
                outcome_metric_name="popularity",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'genre': getattr(band, 'genre', None),
                    'formed_year': getattr(band, 'formed_year', None),
                }
            )
            entities.append(entity)
        
        return entities


class NBAPlayerLoader(DomainLoader):
    """Loader for NBA players"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.NBA_PLAYER)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(NBAPlayer, NBAPlayerAnalysis).join(
            NBAPlayerAnalysis, NBAPlayer.id == NBAPlayerAnalysis.player_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for player, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(player.name)),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'power_connotation_score': getattr(analysis, 'power_connotation_score', 0.0),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Career stats (PPG, All-Star, etc.)
            outcome = getattr(player, 'career_ppg', getattr(player, 'all_star_count', None))
            is_successful = outcome and outcome > 15 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=player.name,
                domain=ExtendedDomainType.NBA_PLAYER,
                entity_id=str(player.id),
                outcome_metric=outcome,
                outcome_metric_name="career_ppg",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'position': getattr(player, 'position', None),
                    'debut_year': getattr(player, 'debut_year', None),
                }
            )
            entities.append(entity)
        
        return entities


class NFLPlayerLoader(DomainLoader):
    """Loader for NFL players"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.NFL_PLAYER)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(NFLPlayer, NFLPlayerAnalysis).join(
            NFLPlayerAnalysis, NFLPlayer.id == NFLPlayerAnalysis.player_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for player, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(player.name)),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'power_connotation_score': getattr(analysis, 'power_connotation_score', 0.0),
                    'aggression_score': getattr(analysis, 'aggression_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Career achievements
            outcome = getattr(player, 'pro_bowl_count', getattr(player, 'career_touchdowns', None))
            is_successful = outcome and outcome > 3 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=player.name,
                domain=ExtendedDomainType.NFL_PLAYER,
                entity_id=str(player.id),
                outcome_metric=outcome,
                outcome_metric_name="pro_bowls",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'position': getattr(player, 'position', None),
                    'draft_year': getattr(player, 'draft_year', None),
                }
            )
            entities.append(entity)
        
        return entities


class MentalHealthLoader(DomainLoader):
    """Loader for mental health terms (diagnoses/medications)"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.MENTAL_HEALTH)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(MentalHealthTerm, MentalHealthAnalysis).join(
            MentalHealthAnalysis, MentalHealthTerm.id == MentalHealthAnalysis.term_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for term, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(term.term)),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'clinical_formality': getattr(analysis, 'clinical_formality', 0.5),
                    'stigma_score': getattr(analysis, 'stigma_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Prevalence or stigma
            outcome = getattr(term, 'prevalence_rate', getattr(term, 'prescription_count', None))
            is_successful = outcome and outcome > 1 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=term.term,
                domain=ExtendedDomainType.MENTAL_HEALTH,
                entity_id=str(term.id),
                outcome_metric=outcome,
                outcome_metric_name="prevalence",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'category': getattr(term, 'category', None),
                    'term_type': getattr(term, 'term_type', None),
                }
            )
            entities.append(entity)
        
        return entities


class AcademicLoader(DomainLoader):
    """Loader for academics/researchers"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.ACADEMIC)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Academic, AcademicAnalysis).join(
            AcademicAnalysis, Academic.id == AcademicAnalysis.academic_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for academic, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(academic.name)),
                    'authority_score': getattr(analysis, 'authority_score', 50.0),
                    'prestige_score': getattr(analysis, 'prestige_score', 50.0),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: h-index or citations
            outcome = getattr(academic, 'h_index', getattr(academic, 'total_citations', None))
            is_successful = outcome and outcome > 50 if outcome else False
            
            entity = UnifiedDomainEntity(
                name=academic.name,
                domain=ExtendedDomainType.ACADEMIC,
                entity_id=str(academic.id),
                outcome_metric=outcome,
                outcome_metric_name="h_index",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'field': getattr(academic, 'field', None),
                    'nobel_prize': getattr(academic, 'nobel_prize', False),
                }
            )
            entities.append(entity)
        
        return entities


class FilmLoader(DomainLoader):
    """Loader for films/movies"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.FILM)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Film, FilmAnalysis).join(
            FilmAnalysis, Film.id == FilmAnalysis.film_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for film, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(film.title)),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'word_count': getattr(analysis, 'word_count', 2),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Box office or rating
            outcome = getattr(film, 'box_office_millions', getattr(film, 'imdb_rating', None))
            is_successful = outcome and outcome > 100 if hasattr(film, 'box_office_millions') else outcome and outcome > 7.0
            
            entity = UnifiedDomainEntity(
                name=film.title,
                domain=ExtendedDomainType.FILM,
                entity_id=str(film.id),
                outcome_metric=outcome,
                outcome_metric_name="box_office",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'year': getattr(film, 'release_year', None),
                    'genre': getattr(film, 'genre', None),
                }
            )
            entities.append(entity)
        
        return entities


class BookLoader(DomainLoader):
    """Loader for books"""
    
    def __init__(self):
        super().__init__(ExtendedDomainType.BOOK)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        filters = filters or {}
        
        query = db.session.query(Book, BookAnalysis).join(
            BookAnalysis, Book.id == BookAnalysis.book_id, isouter=True
        )
        
        if limit:
            query = query.limit(limit)
        
        entities = []
        for book, analysis in query.all():
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(book.title)),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'word_count': getattr(analysis, 'word_count', 2),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                }
            
            # Outcome: Sales or rating
            outcome = getattr(book, 'copies_sold', getattr(book, 'goodreads_rating', None))
            is_successful = outcome and outcome > 100000 if hasattr(book, 'copies_sold') else outcome and outcome > 4.0
            
            entity = UnifiedDomainEntity(
                name=book.title,
                domain=ExtendedDomainType.BOOK,
                entity_id=str(book.id),
                outcome_metric=outcome,
                outcome_metric_name="sales",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'author': getattr(book, 'author', None),
                    'year': getattr(book, 'publication_year', None),
                }
            )
            entities.append(entity)
        
        return entities


class ExtendedDomainInterface(UnifiedDomainInterface):
    """Extended interface with all 15+ domains"""
    
    def __init__(self):
        # Original loaders
        self.loaders = {
            ExtendedDomainType.CRYPTO: CryptoLoader(),
            ExtendedDomainType.ELECTION: ElectionLoader(),
            ExtendedDomainType.SHIP: ShipLoader(),
            ExtendedDomainType.BOARD_GAME: BoardGameLoader(),
            ExtendedDomainType.MLB_PLAYER: MLBPlayerLoader(),
            
            # New loaders
            ExtendedDomainType.WEB_DOMAIN: WebDomainLoader(),
            ExtendedDomainType.STOCK: StockLoader(),
            ExtendedDomainType.HURRICANE: HurricaneLoader(),
            ExtendedDomainType.MTG_CARD: MTGCardLoader(),
            ExtendedDomainType.BAND: BandLoader(),
            ExtendedDomainType.NBA_PLAYER: NBAPlayerLoader(),
            ExtendedDomainType.NFL_PLAYER: NFLPlayerLoader(),
            ExtendedDomainType.MENTAL_HEALTH: MentalHealthLoader(),
            ExtendedDomainType.ACADEMIC: AcademicLoader(),
            ExtendedDomainType.FILM: FilmLoader(),
            ExtendedDomainType.BOOK: BookLoader(),
        }
    
    def get_domain_info(self) -> Dict:
        """Get information about all available domains"""
        from app import app
        
        info = {}
        
        with app.app_context():
            for domain_type in ExtendedDomainType:
                try:
                    entities = self.load_domain(domain_type, limit=1)
                    stats = self.get_statistics(domain_type)
                    
                    info[domain_type.value] = {
                        'name': domain_type.value,
                        'available': True,
                        'count': stats.get('count', 0),
                        'with_analysis': stats.get('with_analysis', 0),
                        'with_outcome': stats.get('with_outcome', 0),
                        'outcome_metric': entities[0].outcome_metric_name if entities else 'unknown'
                    }
                except Exception as e:
                    info[domain_type.value] = {
                        'name': domain_type.value,
                        'available': False,
                        'error': str(e)
                    }
        
        return info

