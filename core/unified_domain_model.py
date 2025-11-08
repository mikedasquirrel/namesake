"""
Unified Domain Model - Cross-Domain Abstraction Layer

Provides standardized interface to access entities across all research domains:
- Cryptocurrency
- Elections
- Ships
- Board Games
- MLB Players
- (Extensible to future domains)

Enables formula testing across domains without domain-specific code.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from sqlalchemy import func, and_, or_

from core.models import (
    db, Cryptocurrency, NameAnalysis, PriceHistory,
    ElectionCandidate, ElectionCandidateAnalysis,
    Ship, ShipAnalysis,
    BoardGame, BoardGameAnalysis,
    MLBPlayer, MLBPlayerAnalysis
)

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """Supported research domains"""
    CRYPTO = "crypto"
    ELECTION = "election"
    SHIP = "ship"
    BOARD_GAME = "board_game"
    MLB_PLAYER = "mlb_player"


@dataclass
class UnifiedDomainEntity:
    """
    Standardized representation of any entity across domains
    """
    # Core identification
    name: str
    domain: DomainType
    entity_id: str  # Domain-specific ID
    
    # Outcome metric (the thing we're trying to predict)
    outcome_metric: Optional[float] = None
    outcome_metric_name: str = ""
    outcome_rank: Optional[int] = None  # Percentile or ranking
    
    # Success classification
    is_successful: Optional[bool] = None  # Binary success indicator
    success_threshold: Optional[float] = None
    
    # Linguistic features (extracted from name analysis)
    linguistic_features: Dict[str, Any] = field(default_factory=dict)
    
    # Visual encoding (from formula transformation)
    visual_encoding: Optional[Dict[str, Any]] = None
    formula_id: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis results
    prediction_accuracy: Optional[float] = None
    correlation_strength: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'domain': self.domain.value,
            'entity_id': self.entity_id,
            'outcome_metric': self.outcome_metric,
            'outcome_metric_name': self.outcome_metric_name,
            'outcome_rank': self.outcome_rank,
            'is_successful': self.is_successful,
            'linguistic_features': self.linguistic_features,
            'visual_encoding': self.visual_encoding,
            'formula_id': self.formula_id,
            'metadata': self.metadata,
        }


class DomainLoader:
    """Base class for domain-specific data loaders"""
    
    def __init__(self, domain_type: DomainType):
        self.domain_type = domain_type
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """Load entities from this domain"""
        raise NotImplementedError
    
    def get_linguistic_features(self, entity_id: str) -> Dict[str, Any]:
        """Get linguistic features for an entity"""
        raise NotImplementedError
    
    def get_outcome_metric(self, entity_id: str) -> Tuple[Optional[float], str]:
        """Get outcome metric and its name"""
        raise NotImplementedError


class CryptoLoader(DomainLoader):
    """Loader for cryptocurrency domain"""
    
    def __init__(self):
        super().__init__(DomainType.CRYPTO)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """Load cryptocurrency entities"""
        filters = filters or {}
        
        # Build query
        query = db.session.query(Cryptocurrency, NameAnalysis, PriceHistory).join(
            NameAnalysis, Cryptocurrency.id == NameAnalysis.crypto_id, isouter=True
        ).join(
            PriceHistory, Cryptocurrency.id == PriceHistory.crypto_id, isouter=True
        )
        
        # Apply filters
        if filters.get('min_market_cap'):
            query = query.filter(Cryptocurrency.market_cap >= filters['min_market_cap'])
        
        if filters.get('has_analysis'):
            query = query.filter(NameAnalysis.id.isnot(None))
        
        # Limit
        if limit:
            query = query.limit(limit)
        
        entities = []
        for crypto, analysis, price in query.all():
            # Extract linguistic features (with safe defaults)
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(crypto.name)),
                    'phonetic_score': getattr(analysis, 'phonetic_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'smoothness_score': getattr(analysis, 'smoothness_score', 0.5),
                    'plosive_ratio': getattr(analysis, 'plosive_ratio', 0.2),
                    'power_connotation_score': getattr(analysis, 'power_connotation_score', 0.0),
                    'phonetic_complexity': getattr(analysis, 'phonetic_complexity', 0.5),
                    'name_type': getattr(analysis, 'name_type', 'unknown'),
                    'semantic_category': getattr(analysis, 'semantic_category', 'neutral'),
                    'uniqueness_score': getattr(analysis, 'uniqueness_score', 50),
                    'word_count': getattr(analysis, 'word_count', 1),
                }
            
            # Outcome metric: market cap (log scale)
            outcome = None
            if crypto.market_cap and crypto.market_cap > 0:
                import math
                outcome = math.log10(crypto.market_cap)
            
            # Success: Market cap > $10M
            is_successful = crypto.market_cap and crypto.market_cap > 10000000
            
            entity = UnifiedDomainEntity(
                name=crypto.name,
                domain=DomainType.CRYPTO,
                entity_id=crypto.id,
                outcome_metric=outcome,
                outcome_metric_name="log_market_cap",
                outcome_rank=None,
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'symbol': crypto.symbol,
                    'market_cap': crypto.market_cap,
                    'price': crypto.current_price,
                }
            )
            entities.append(entity)
        
        return entities
    
    def get_linguistic_features(self, entity_id: str) -> Dict[str, Any]:
        """Get linguistic features for a crypto"""
        analysis = NameAnalysis.query.filter_by(crypto_id=entity_id).first()
        if not analysis:
            return {}
        
        return {
            'syllable_count': analysis.syllable_count,
            'character_length': analysis.character_length,
            'phonetic_score': analysis.phonetic_score,
            'vowel_ratio': analysis.vowel_ratio,
            'memorability_score': analysis.memorability_score,
            'name_type': analysis.name_type,
            'semantic_category': analysis.semantic_category,
        }
    
    def get_outcome_metric(self, entity_id: str) -> Tuple[Optional[float], str]:
        """Get market cap for a crypto"""
        crypto = Cryptocurrency.query.get(entity_id)
        if not crypto or not crypto.market_cap or crypto.market_cap <= 0:
            return None, "log_market_cap"
        
        import math
        return math.log10(crypto.market_cap), "log_market_cap"


class ElectionLoader(DomainLoader):
    """Loader for election domain"""
    
    def __init__(self):
        super().__init__(DomainType.ELECTION)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """Load election candidate entities"""
        filters = filters or {}
        
        # Build query
        query = db.session.query(ElectionCandidate, ElectionCandidateAnalysis).join(
            ElectionCandidateAnalysis,
            ElectionCandidate.id == ElectionCandidateAnalysis.candidate_id,
            isouter=True
        )
        
        # Apply filters
        if filters.get('position'):
            query = query.filter(ElectionCandidate.position == filters['position'])
        
        if filters.get('year'):
            query = query.filter(ElectionCandidate.election_year == filters['year'])
        
        # Limit
        if limit:
            query = query.limit(limit)
        
        entities = []
        for candidate, analysis in query.all():
            # Extract linguistic features (safe)
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(candidate.full_name)),
                    'word_count': getattr(analysis, 'word_count', 2),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'smoothness_score': getattr(analysis, 'smoothness_score', 0.5),
                    'power_connotation_score': getattr(analysis, 'power_connotation_score', 0.0),
                    'authority_score': getattr(analysis, 'authority_score', 50.0),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'plosive_ratio': getattr(analysis, 'plosive_ratio', 0.2),
                    'phonetic_complexity': getattr(analysis, 'phonetic_complexity', 0.5),
                }
            
            # Outcome metric: won election (1.0 or 0.0)
            outcome = 1.0 if candidate.won_election else 0.0
            
            entity = UnifiedDomainEntity(
                name=candidate.full_name,
                domain=DomainType.ELECTION,
                entity_id=str(candidate.id),
                outcome_metric=outcome,
                outcome_metric_name="won_election",
                is_successful=candidate.won_election,
                linguistic_features=ling_features,
                metadata={
                    'position': getattr(candidate, 'position', 'Unknown'),
                    'year': getattr(candidate, 'election_year', None),
                    'party': getattr(candidate, 'party_simplified', 'Unknown'),
                    'vote_share': getattr(candidate, 'vote_share_percentage', None),
                }
            )
            entities.append(entity)
        
        return entities


class ShipLoader(DomainLoader):
    """Loader for naval ships domain"""
    
    def __init__(self):
        super().__init__(DomainType.SHIP)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """Load ship entities"""
        filters = filters or {}
        
        # Build query
        query = db.session.query(Ship, ShipAnalysis).join(
            ShipAnalysis, Ship.id == ShipAnalysis.ship_id, isouter=True
        )
        
        # Apply filters
        if filters.get('nation'):
            query = query.filter(Ship.nation == filters['nation'])
        
        if filters.get('has_events'):
            query = query.filter(Ship.major_events_count > 0)
        
        # Limit
        if limit:
            query = query.limit(limit)
        
        entities = []
        for ship, analysis in query.all():
            # Extract linguistic features (safe)
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(ship.name)),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'smoothness_score': getattr(analysis, 'softness_score', 0.5),
                    'authority_score': getattr(analysis, 'authority_score', 50.0),
                    'power_connotation_score': getattr(analysis, 'power_connotation_score', 0.0),
                    'prestige_score': getattr(analysis, 'prestige_score', 50.0),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'plosive_ratio': getattr(analysis, 'plosive_ratio', 0.2),
                    'name_type': getattr(analysis, 'name_type', 'unknown'),
                }
            
            # Outcome metric: historical significance score
            outcome = getattr(ship, 'historical_significance_score', 0.0)
            
            # Success: Significant historical impact (score > 50)
            is_successful = outcome and outcome > 50
            
            entity = UnifiedDomainEntity(
                name=ship.name,
                domain=DomainType.SHIP,
                entity_id=str(ship.id),
                outcome_metric=outcome,
                outcome_metric_name="significance_score",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'nation': getattr(ship, 'nation', 'Unknown'),
                    'ship_class': getattr(ship, 'ship_class', 'Unknown'),
                    'launch_year': getattr(ship, 'launch_year', None),
                    'major_events': getattr(ship, 'major_events_count', 0),
                }
            )
            entities.append(entity)
        
        return entities


class BoardGameLoader(DomainLoader):
    """Loader for board games domain"""
    
    def __init__(self):
        super().__init__(DomainType.BOARD_GAME)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """Load board game entities"""
        filters = filters or {}
        
        # Build query
        query = db.session.query(BoardGame, BoardGameAnalysis).join(
            BoardGameAnalysis, BoardGame.id == BoardGameAnalysis.game_id, isouter=True
        )
        
        # Apply filters
        if filters.get('min_rating'):
            query = query.filter(BoardGame.average_rating >= filters['min_rating'])
        
        # Limit
        if limit:
            query = query.limit(limit)
        
        entities = []
        for game, analysis in query.all():
            # Extract linguistic features (safe)
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(game.name)),
                    'word_count': getattr(analysis, 'word_count', 2),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'smoothness_score': getattr(analysis, 'smoothness_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'plosive_ratio': getattr(analysis, 'plosive_ratio', 0.2),
                    'phonetic_complexity': getattr(analysis, 'phonetic_complexity', 0.5),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'name_type': getattr(analysis, 'name_type', 'unknown'),
                }
            
            # Outcome metric: average rating
            outcome = game.average_rating if game.average_rating else None
            
            # Success: Rating >= 7.5 (high-quality games)
            is_successful = game.average_rating and game.average_rating >= 7.5
            
            entity = UnifiedDomainEntity(
                name=game.name,
                domain=DomainType.BOARD_GAME,
                entity_id=str(game.id),
                outcome_metric=outcome,
                outcome_metric_name="average_rating",
                outcome_rank=game.bgg_rank,
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'year_published': getattr(game, 'year_published', None),
                    'complexity': getattr(game, 'complexity_average', None),
                    'min_players': getattr(game, 'min_players', None),
                    'max_players': getattr(game, 'max_players', None),
                }
            )
            entities.append(entity)
        
        return entities


class MLBPlayerLoader(DomainLoader):
    """Loader for MLB players domain"""
    
    def __init__(self):
        super().__init__(DomainType.MLB_PLAYER)
    
    def load_entities(self, limit: Optional[int] = None, 
                     filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """Load MLB player entities"""
        filters = filters or {}
        
        # Build query
        query = db.session.query(MLBPlayer, MLBPlayerAnalysis).join(
            MLBPlayerAnalysis, MLBPlayer.id == MLBPlayerAnalysis.player_id, isouter=True
        )
        
        # Apply filters
        if filters.get('position'):
            query = query.filter(MLBPlayer.primary_position == filters['position'])
        
        if filters.get('min_games'):
            query = query.filter(MLBPlayer.games_played >= filters['min_games'])
        
        # Limit
        if limit:
            query = query.limit(limit)
        
        entities = []
        for player, analysis in query.all():
            # Extract linguistic features (safe)
            ling_features = {}
            if analysis:
                ling_features = {
                    'syllable_count': getattr(analysis, 'syllable_count', 2),
                    'character_length': getattr(analysis, 'character_length', len(player.full_name)),
                    'harshness_score': getattr(analysis, 'harshness_score', 0.5),
                    'smoothness_score': getattr(analysis, 'smoothness_score', 0.5),
                    'power_connotation_score': getattr(analysis, 'power_connotation_score', 0.0),
                    'memorability_score': getattr(analysis, 'memorability_score', 0.5),
                    'vowel_ratio': getattr(analysis, 'vowel_ratio', 0.4),
                    'plosive_ratio': getattr(analysis, 'plosive_ratio', 0.2),
                    'phonetic_complexity': getattr(analysis, 'phonetic_complexity', 0.5),
                }
            
            # Outcome metric: Use batting average or default metric
            outcome = getattr(player, 'war', getattr(player, 'batting_average', None))
            
            # Success: Above average performance
            is_successful = outcome and outcome > 0 if outcome is not None else False
            
            entity = UnifiedDomainEntity(
                name=player.full_name,
                domain=DomainType.MLB_PLAYER,
                entity_id=player.id,
                outcome_metric=outcome,
                outcome_metric_name="performance_metric",
                is_successful=is_successful,
                linguistic_features=ling_features,
                metadata={
                    'position': getattr(player, 'primary_position', 'Unknown'),
                    'debut_year': getattr(player, 'debut_year', None),
                    'games_played': getattr(player, 'games_played', None),
                }
            )
            entities.append(entity)
        
        return entities


class UnifiedDomainInterface:
    """
    Main interface for cross-domain entity access
    """
    
    def __init__(self):
        self.loaders = {
            DomainType.CRYPTO: CryptoLoader(),
            DomainType.ELECTION: ElectionLoader(),
            DomainType.SHIP: ShipLoader(),
            DomainType.BOARD_GAME: BoardGameLoader(),
            DomainType.MLB_PLAYER: MLBPlayerLoader(),
        }
    
    def load_domain(self, domain: DomainType, limit: Optional[int] = None,
                   filters: Optional[Dict] = None) -> List[UnifiedDomainEntity]:
        """
        Load entities from specified domain
        
        Args:
            domain: Which domain to load
            limit: Maximum number of entities
            filters: Domain-specific filters
            
        Returns:
            List of UnifiedDomainEntity objects
        """
        loader = self.loaders.get(domain)
        if not loader:
            raise ValueError(f"Unknown domain: {domain}")
        
        return loader.load_entities(limit=limit, filters=filters)
    
    def load_all_domains(self, limit_per_domain: Optional[int] = None) -> Dict[DomainType, List[UnifiedDomainEntity]]:
        """
        Load entities from all domains
        
        Returns:
            Dictionary mapping domain to entity lists
        """
        results = {}
        for domain in DomainType:
            try:
                results[domain] = self.load_domain(domain, limit=limit_per_domain)
                logger.info(f"Loaded {len(results[domain])} entities from {domain.value}")
            except Exception as e:
                logger.error(f"Error loading {domain.value}: {e}")
                results[domain] = []
        
        return results
    
    def get_entity_by_name(self, name: str, domain: DomainType) -> Optional[UnifiedDomainEntity]:
        """Find entity by name in specific domain"""
        entities = self.load_domain(domain)
        for entity in entities:
            if entity.name.lower() == name.lower():
                return entity
        return None
    
    def get_statistics(self, domain: DomainType) -> Dict[str, Any]:
        """Get statistics about a domain"""
        entities = self.load_domain(domain)
        
        if not entities:
            return {'count': 0}
        
        # Calculate statistics
        outcomes = [e.outcome_metric for e in entities if e.outcome_metric is not None]
        successful = [e for e in entities if e.is_successful]
        
        stats = {
            'count': len(entities),
            'with_analysis': len([e for e in entities if e.linguistic_features]),
            'with_outcome': len(outcomes),
            'successful_count': len(successful),
            'success_rate': len(successful) / len(entities) if entities else 0,
        }
        
        if outcomes:
            import numpy as np
            stats['outcome_mean'] = float(np.mean(outcomes))
            stats['outcome_std'] = float(np.std(outcomes))
            stats['outcome_min'] = float(np.min(outcomes))
            stats['outcome_max'] = float(np.max(outcomes))
        
        return stats
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all domains"""
        stats = {}
        for domain in DomainType:
            stats[domain.value] = self.get_statistics(domain)
        
        return stats

