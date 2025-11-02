from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Cryptocurrency(db.Model):
    """Core cryptocurrency data"""
    __tablename__ = 'cryptocurrency'
    __table_args__ = (
        db.Index('idx_crypto_rank', 'rank'),  # For rank-based queries
        db.Index('idx_crypto_market_cap', 'market_cap'),  # For market cap filtering
        db.Index('idx_crypto_active', 'is_active'),  # For filtering active/inactive coins
    )
    
    id = db.Column(db.String(100), primary_key=True)  # CoinGecko ID
    name = db.Column(db.String(200), nullable=False, index=True)  # Index for name searches
    symbol = db.Column(db.String(50), nullable=False, index=True)  # Index for symbol searches
    rank = db.Column(db.Integer)
    market_cap = db.Column(db.Float)
    current_price = db.Column(db.Float)
    total_volume = db.Column(db.Float)
    circulating_supply = db.Column(db.Float)
    max_supply = db.Column(db.Float)
    ath = db.Column(db.Float)  # All-time high
    ath_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Failure tracking (for statistical rigor - eliminate survivorship bias)
    is_active = db.Column(db.Boolean, default=True)  # False for dead/delisted coins
    delisting_date = db.Column(db.DateTime)  # When removed from major exchanges
    failure_reason = db.Column(db.String(200))  # 'scam', 'abandoned', 'bankrupt', 'merged', etc.
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='cryptocurrency', lazy='dynamic', cascade='all, delete-orphan')
    name_analysis = db.relationship('NameAnalysis', backref='cryptocurrency', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'rank': self.rank,
            'market_cap': self.market_cap,
            'current_price': self.current_price,
            'total_volume': self.total_volume,
            'ath': self.ath,
            'ath_date': self.ath_date.isoformat() if self.ath_date else None,
            'is_active': self.is_active,
            'delisting_date': self.delisting_date.isoformat() if self.delisting_date else None,
            'failure_reason': self.failure_reason,
            'name_analysis': self.name_analysis.to_dict() if self.name_analysis else None
        }


class PriceHistory(db.Model):
    """Historical price data and performance metrics"""
    __tablename__ = 'price_history'
    __table_args__ = (
        db.Index('idx_price_crypto_date', 'crypto_id', 'date'),  # Compound index for latest price queries
        db.Index('idx_price_1yr_change', 'price_1yr_change'),  # For performance filtering
    )
    
    id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(db.String(100), db.ForeignKey('cryptocurrency.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    market_cap = db.Column(db.Float)
    volume = db.Column(db.Float)
    
    # Performance metrics
    price_30d_change = db.Column(db.Float)  # Percentage change
    price_90d_change = db.Column(db.Float)
    price_1yr_change = db.Column(db.Float)
    price_ath_change = db.Column(db.Float)  # Distance from ATH
    
    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'price': self.price,
            'price_30d_change': self.price_30d_change,
            'price_90d_change': self.price_90d_change,
            'price_1yr_change': self.price_1yr_change,
            'price_ath_change': self.price_ath_change
        }


class NameAnalysis(db.Model):
    """Comprehensive linguistic analysis of cryptocurrency names"""
    __tablename__ = 'name_analysis'
    __table_args__ = (
        db.Index('idx_name_syllables', 'syllable_count'),  # For syllable-based queries
        db.Index('idx_name_length', 'character_length'),  # For length-based queries
        db.Index('idx_name_type', 'name_type'),  # For name type filtering
        db.Index('idx_name_memorability', 'memorability_score'),  # For memorability filtering
    )
    
    id = db.Column(db.Integer, primary_key=True)
    crypto_id = db.Column(db.String(100), db.ForeignKey('cryptocurrency.id'), nullable=False, unique=True)
    
    # Basic metrics
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic analysis
    phonetic_score = db.Column(db.Float)  # Overall euphony
    vowel_ratio = db.Column(db.Float)  # Vowels / total letters
    consonant_clusters = db.Column(db.Integer)  # Number of consonant clusters
    
    # Memorability
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    
    # Categorization
    name_type = db.Column(db.String(50))  # Primary category
    category_tags = db.Column(db.Text)  # JSON array of all applicable categories
    
    # Uniqueness metrics
    uniqueness_score = db.Column(db.Float)  # 0-100, higher = more unique
    avg_similarity_distance = db.Column(db.Float)  # Average Levenshtein distance to other names
    closest_match = db.Column(db.String(200))  # Name of most similar crypto
    closest_match_distance = db.Column(db.Integer)
    
    # Character composition
    has_numbers = db.Column(db.Boolean, default=False)
    has_special_chars = db.Column(db.Boolean, default=False)
    capital_pattern = db.Column(db.String(50))  # 'lowercase', 'uppercase', 'mixed', 'camelcase'
    
    # Semantic analysis
    is_real_word = db.Column(db.Boolean, default=False)
    semantic_category = db.Column(db.String(100))  # What the name refers to
    
    # Scarcity
    name_type_count = db.Column(db.Integer)  # How many others share this type
    name_type_percentile = db.Column(db.Float)  # Rarity percentile
    
    # Advanced metrics (JSON storage for flexibility)
    advanced_metrics = db.Column(db.Text)  # JSON: sound symbolism, psychology, typography
    esoteric_metrics = db.Column(db.Text)  # JSON: numerology, archetypes, frequencies
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'word_count': self.word_count,
            'phonetic_score': self.phonetic_score,
            'vowel_ratio': self.vowel_ratio,
            'memorability_score': self.memorability_score,
            'pronounceability_score': self.pronounceability_score,
            'name_type': self.name_type,
            'category_tags': json.loads(self.category_tags) if self.category_tags else [],
            'uniqueness_score': self.uniqueness_score,
            'avg_similarity_distance': self.avg_similarity_distance,
            'closest_match': self.closest_match,
            'has_numbers': self.has_numbers,
            'has_special_chars': self.has_special_chars,
            'capital_pattern': self.capital_pattern,
            'is_real_word': self.is_real_word,
            'name_type_count': self.name_type_count,
            'name_type_percentile': self.name_type_percentile,
            'advanced_metrics': json.loads(self.advanced_metrics) if self.advanced_metrics else {},
            'esoteric_metrics': json.loads(self.esoteric_metrics) if self.esoteric_metrics else {}
        }


class Study(db.Model):
    """Research studies and hypothesis tests"""
    __tablename__ = 'study'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    hypothesis = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')  # active, completed, archived
    
    # Results stored as JSON
    results_json = db.Column(db.Text)  # Statistical test results
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hypothesis': self.hypothesis,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'results': json.loads(self.results_json) if self.results_json else None,
            'notes': self.notes
        }


class CustomQuery(db.Model):
    """Saved custom queries"""
    __tablename__ = 'custom_query'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    query_text = db.Column(db.Text, nullable=False)
    filters_json = db.Column(db.Text)  # Parsed filter structure
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime)
    result_count = db.Column(db.Integer)
    is_preset = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'query_text': self.query_text,
            'filters': json.loads(self.filters_json) if self.filters_json else None,
            'created_date': self.created_date.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'result_count': self.result_count,
            'is_preset': self.is_preset
        }


# =============================================================================
# DOMAIN ANALYSIS TABLES
# =============================================================================

class Domain(db.Model):
    """Web domain data and sales information"""
    __tablename__ = 'domain'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # Domain without TLD
    tld = db.Column(db.String(20), nullable=False)  # .com, .io, .ai, etc.
    full_domain = db.Column(db.String(250), nullable=False, unique=True)  # name + tld
    
    # Availability and pricing
    is_available = db.Column(db.Boolean, default=False)
    sale_price = db.Column(db.Float)  # Historical sale price if sold
    sale_date = db.Column(db.DateTime)
    estimated_value_low = db.Column(db.Float)
    estimated_value_high = db.Column(db.Float)
    
    # Domain-specific metrics
    keyword_score = db.Column(db.Float)  # Commercial keyword value
    brandability_score = db.Column(db.Float)  # How good as a brand
    search_volume = db.Column(db.Integer)  # Monthly searches for related keywords
    tld_premium_multiplier = db.Column(db.Float)  # Value multiplier for this TLD
    
    # Failure tracking (for statistical rigor - eliminate survivorship bias)
    auction_failed = db.Column(db.Boolean, default=False)  # True if listed but didn't sell
    listing_price = db.Column(db.Float)  # Original asking price if available
    days_on_market = db.Column(db.Integer)  # How long listed before sale/failure
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domain_analysis = db.relationship('DomainAnalysis', backref='domain', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tld': self.tld,
            'full_domain': self.full_domain,
            'is_available': self.is_available,
            'sale_price': self.sale_price,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'estimated_value': {
                'low': self.estimated_value_low,
                'high': self.estimated_value_high
            },
            'keyword_score': self.keyword_score,
            'brandability_score': self.brandability_score,
            'auction_failed': self.auction_failed,
            'listing_price': self.listing_price,
            'days_on_market': self.days_on_market
        }


class DomainAnalysis(db.Model):
    """Name analysis for domains (mirrors NameAnalysis structure)"""
    __tablename__ = 'domain_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), nullable=False, unique=True)
    
    # Basic metrics (same as cryptocurrency analysis)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic analysis
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    consonant_clusters = db.Column(db.Integer)
    
    # Memorability
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    
    # Categorization
    name_type = db.Column(db.String(50))
    category_tags = db.Column(db.Text)
    
    # Uniqueness
    uniqueness_score = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'memorability_score': self.memorability_score,
            'uniqueness_score': self.uniqueness_score,
            'phonetic_score': self.phonetic_score,
            'name_type': self.name_type
        }


class CrossSpherePattern(db.Model):
    """Patterns discovered across multiple asset spheres"""
    __tablename__ = 'cross_sphere_pattern'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(200), nullable=False)
    pattern_description = db.Column(db.Text)
    
    # Crypto metrics
    crypto_correlation = db.Column(db.Float)
    crypto_p_value = db.Column(db.Float)
    crypto_sample_size = db.Column(db.Integer)
    crypto_effect_size = db.Column(db.Float)
    
    # Domain metrics
    domain_correlation = db.Column(db.Float)
    domain_p_value = db.Column(db.Float)
    domain_sample_size = db.Column(db.Integer)
    domain_effect_size = db.Column(db.Float)
    
    # Cross-sphere analysis
    universal_strength = db.Column(db.Float)  # 0-100 score
    is_universal = db.Column(db.Boolean, default=False)  # Works in both spheres
    transferability_score = db.Column(db.Float)  # How well pattern transfers
    
    discovered_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pattern_name': self.pattern_name,
            'description': self.pattern_description,
            'crypto': {
                'correlation': self.crypto_correlation,
                'p_value': self.crypto_p_value,
                'sample_size': self.crypto_sample_size,
                'effect_size': self.crypto_effect_size
            },
            'domains': {
                'correlation': self.domain_correlation,
                'p_value': self.domain_p_value,
                'sample_size': self.domain_sample_size,
                'effect_size': self.domain_effect_size
            },
            'universal_strength': self.universal_strength,
            'is_universal': self.is_universal,
            'transferability_score': self.transferability_score
        }


class ForwardPrediction(db.Model):
    """Forward predictions for validation (locked, cannot be changed after creation)"""
    __tablename__ = 'forward_prediction'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # What we're predicting
    asset_type = db.Column(db.String(20), nullable=False)  # 'crypto', 'domain', 'stock'
    asset_id = db.Column(db.String(200), nullable=False)  # Crypto ID or domain name
    asset_name = db.Column(db.String(200), nullable=False)
    
    # Prediction details (LOCKED at creation)
    prediction_type = db.Column(db.String(50), nullable=False)  # 'will_reach_top_100', 'breakout', 'value_increase'
    predicted_outcome = db.Column(db.Text, nullable=False)  # JSON with specific prediction
    confidence_score = db.Column(db.Float)  # 0-100
    
    # Baseline data at prediction time
    baseline_rank = db.Column(db.Integer)  # For cryptos
    baseline_price = db.Column(db.Float)  # Current price at prediction
    baseline_market_cap = db.Column(db.Float)
    
    # Prediction metadata
    prediction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_date = db.Column(db.DateTime, nullable=False)  # When to check outcome
    is_locked = db.Column(db.Boolean, default=True)  # Cannot modify after creation
    
    # Outcome (filled in after check_date)
    actual_outcome = db.Column(db.Text)  # JSON with actual result
    outcome_date = db.Column(db.DateTime)
    is_correct = db.Column(db.Boolean)  # Was prediction accurate?
    is_resolved = db.Column(db.Boolean, default=False)
    
    # Analysis
    name_score = db.Column(db.Float)  # Name quality score at prediction time
    pattern_matches = db.Column(db.Text)  # JSON list of matched patterns
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_type': self.asset_type,
            'asset_name': self.asset_name,
            'prediction_type': self.prediction_type,
            'predicted_outcome': json.loads(self.predicted_outcome) if self.predicted_outcome else None,
            'confidence_score': self.confidence_score,
            'prediction_date': self.prediction_date.isoformat(),
            'check_date': self.check_date.isoformat(),
            'is_resolved': self.is_resolved,
            'is_correct': self.is_correct,
            'actual_outcome': json.loads(self.actual_outcome) if self.actual_outcome else None,
            'baseline': {
                'rank': self.baseline_rank,
                'price': self.baseline_price,
                'market_cap': self.baseline_market_cap
            },
            'name_score': self.name_score
        }


# =============================================================================
# STOCK MARKET TABLES
# =============================================================================

class Stock(db.Model):
    """Stock market data"""
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    market_cap = db.Column(db.Float)
    current_price = db.Column(db.Float)
    return_1yr = db.Column(db.Float)
    return_5yr = db.Column(db.Float)
    founded_year = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Failure tracking (for statistical rigor - eliminate survivorship bias)
    is_active = db.Column(db.Boolean, default=True)  # False for delisted companies
    delisted_date = db.Column(db.DateTime)  # When removed from exchange
    delisting_reason = db.Column(db.String(200))  # 'bankruptcy', 'merger', 'acquisition', 'failure', etc.
    final_price = db.Column(db.Float)  # Last trading price before delisting
    
    stock_analysis = db.relationship('StockAnalysis', backref='stock', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'ticker': self.ticker,
            'company_name': self.company_name,
            'sector': self.sector,
            'market_cap': self.market_cap,
            'current_price': self.current_price,
            'return_1yr': self.return_1yr,
            'return_5yr': self.return_5yr,
            'is_active': self.is_active,
            'delisted_date': self.delisted_date.isoformat() if self.delisted_date else None,
            'delisting_reason': self.delisting_reason,
            'final_price': self.final_price
        }


class StockAnalysis(db.Model):
    """Name analysis for stocks (company name + ticker)"""
    __tablename__ = 'stock_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), unique=True)
    
    # Company name analysis
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # Ticker analysis
    ticker_length = db.Column(db.Integer)
    ticker_pronounceability = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'memorability_score': self.memorability_score,
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type,
            'ticker_length': self.ticker_length
        }


# =============================================================================
# FILM TABLES
# =============================================================================

class Film(db.Model):
    """Film data"""
    __tablename__ = 'film'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    revenue = db.Column(db.Float)
    budget = db.Column(db.Float)
    roi = db.Column(db.Float)
    rating = db.Column(db.Float)
    genre = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    film_analysis = db.relationship('FilmAnalysis', backref='film', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'title': self.title,
            'year': self.year,
            'revenue': self.revenue,
            'roi': self.roi
        }


class FilmAnalysis(db.Model):
    """Title analysis for films"""
    __tablename__ = 'film_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), unique=True)
    
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'word_count': self.word_count,
            'memorability_score': self.memorability_score,
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type
        }


# =============================================================================
# BOOK TABLES
# =============================================================================

class Book(db.Model):
    """Book data"""
    __tablename__ = 'book'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    author = db.Column(db.String(200))
    year = db.Column(db.Integer)
    sales_estimate = db.Column(db.Integer)
    weeks_on_list = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    performance_score = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    book_analysis = db.relationship('BookAnalysis', backref='book', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'title': self.title,
            'author': self.author,
            'sales_estimate': self.sales_estimate,
            'weeks_on_list': self.weeks_on_list
        }


class BookAnalysis(db.Model):
    """Title analysis for books"""
    __tablename__ = 'book_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), unique=True)
    
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'word_count': self.word_count,
            'memorability_score': self.memorability_score,
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type
        }


# =============================================================================
# PEOPLE TABLES
# =============================================================================

class Person(db.Model):
    """People data"""
    __tablename__ = 'person'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    net_worth = db.Column(db.Float)
    field = db.Column(db.String(100))
    achievement = db.Column(db.String(300))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    person_analysis = db.relationship('PersonAnalysis', backref='person', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'net_worth': self.net_worth,
            'field': self.field
        }


class PersonAnalysis(db.Model):
    """Name analysis for people"""
    __tablename__ = 'person_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), unique=True)
    
    # First name analysis
    first_syllables = db.Column(db.Integer)
    first_length = db.Column(db.Integer)
    first_memorability = db.Column(db.Float)
    
    # Last name analysis
    last_syllables = db.Column(db.Integer)
    last_length = db.Column(db.Integer)
    last_memorability = db.Column(db.Float)
    
    # Full name analysis
    total_syllables = db.Column(db.Integer)
    total_length = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'first_syllables': self.first_syllables,
            'first_length': self.first_length,
            'first_memorability': self.first_memorability,
            'last_syllables': self.last_syllables,
            'last_length': self.last_length,
            'last_memorability': self.last_memorability,
            'total_syllables': self.total_syllables,
            'total_length': self.total_length,
            'memorability_score': self.memorability_score,
            'uniqueness_score': self.uniqueness_score
        }


# =============================================================================
# PRE-COMPUTED ANALYSIS RESULTS (FOR INSTANT PAGE LOADS)
# =============================================================================

class PreComputedStats(db.Model):
    """Pre-computed analysis results - updated periodically for instant page loads"""
    __tablename__ = 'precomputed_stats'
    __table_args__ = (
        db.Index('idx_precomputed_type_current', 'stat_type', 'is_current'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    stat_type = db.Column(db.String(50), nullable=False, index=True)  # 'advanced_stats', 'validation', 'patterns', etc.
    data_json = db.Column(db.Text, nullable=False)  # Stored JSON results
    sample_size = db.Column(db.Integer)  # How many cryptos analyzed
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)
    computation_duration = db.Column(db.Float)  # Seconds to compute
    is_current = db.Column(db.Boolean, default=True, index=True)  # Only one current per type
    
    def to_dict(self):
        return {
            'stat_type': self.stat_type,
            'data': json.loads(self.data_json) if self.data_json else None,
            'sample_size': self.sample_size,
            'computed_at': self.computed_at.isoformat() if self.computed_at else None,
            'computation_duration': self.computation_duration
        }


