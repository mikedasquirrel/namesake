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
# HURRICANE TABLES
# =============================================================================

class Hurricane(db.Model):
    """Hurricane/tropical storm data from NOAA"""
    __tablename__ = 'hurricane'
    __table_args__ = (
        db.Index('idx_hurricane_year', 'year'),
        db.Index('idx_hurricane_category', 'saffir_simpson_category'),
        db.Index('idx_hurricane_landfall_state', 'landfall_state'),
    )
    
    id = db.Column(db.String(50), primary_key=True)  # NOAA storm ID (e.g., AL092005 for Katrina)
    name = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    basin = db.Column(db.String(20))  # Atlantic, Pacific
    
    # Intensity metrics
    max_wind_mph = db.Column(db.Integer)
    max_wind_kts = db.Column(db.Integer)
    min_pressure_mb = db.Column(db.Integer)
    saffir_simpson_category = db.Column(db.Integer)  # 1-5, null if tropical storm
    
    # Landfall information
    landfall_date = db.Column(db.Date)
    landfall_state = db.Column(db.String(50))
    landfall_location = db.Column(db.String(200))
    
    # Outcomes - Casualties
    deaths = db.Column(db.Integer)  # Total deaths
    deaths_direct = db.Column(db.Integer)  # Immediate storm impact
    deaths_indirect = db.Column(db.Integer)  # Post-storm (accidents, medical, etc.)
    injuries = db.Column(db.Integer)
    missing_persons = db.Column(db.Integer)
    
    # Outcomes - Economic
    damage_usd = db.Column(db.Float)  # Inflation-adjusted to 2023 dollars
    damage_usd_year = db.Column(db.Integer)  # Year of original damage estimate
    insured_losses_usd = db.Column(db.Float)
    fema_aid_usd = db.Column(db.Float)
    agricultural_losses_usd = db.Column(db.Float)
    
    # Outcomes - Displacement & Impact
    displaced_persons = db.Column(db.Integer)  # Made homeless
    homes_destroyed = db.Column(db.Integer)
    homes_damaged = db.Column(db.Integer)
    power_outages_peak = db.Column(db.Integer)  # Peak customers without power
    power_outage_duration_days = db.Column(db.Float)  # Average restoration time
    
    # Response & Preparedness
    evacuations_ordered = db.Column(db.Integer)  # Population ordered to evacuate
    evacuations_actual = db.Column(db.Integer)  # Estimated actual evacuees
    shelters_opened = db.Column(db.Integer)  # Count of shelters
    shelter_peak_occupancy = db.Column(db.Integer)  # Max persons in shelters
    search_rescue_operations = db.Column(db.Integer)  # Number of missions
    search_rescue_persons_saved = db.Column(db.Integer)
    
    # Forecast & Media (control variables)
    forecast_error_24h_miles = db.Column(db.Float)  # 24h track error
    forecast_error_48h_miles = db.Column(db.Float)  # 48h track error
    forecast_error_72h_miles = db.Column(db.Float)  # 72h track error
    media_mentions_prelandfall = db.Column(db.Integer)  # GDELT 7 days before
    media_mentions_postlandfall = db.Column(db.Integer)  # GDELT 7 days after
    social_media_sentiment = db.Column(db.Float)  # -1.0 to +1.0
    
    # Population controls
    coastal_population_exposed = db.Column(db.Integer)  # Census at landfall location
    prior_hurricanes_5yr = db.Column(db.Integer)  # Major storms in region past 5 years
    
    # Legacy (keep for backward compatibility)
    evacuation_orders_issued = db.Column(db.Boolean)
    news_mention_count = db.Column(db.Integer)
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hurricane_analysis = db.relationship('HurricaneAnalysis', backref='hurricane', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'basin': self.basin,
            'max_wind_mph': self.max_wind_mph,
            'min_pressure_mb': self.min_pressure_mb,
            'saffir_simpson_category': self.saffir_simpson_category,
            'landfall_date': self.landfall_date.isoformat() if self.landfall_date else None,
            'landfall_state': self.landfall_state,
            'deaths': self.deaths,
            'injuries': self.injuries,
            'damage_usd': self.damage_usd,
            'fema_aid_usd': self.fema_aid_usd,
            'news_mention_count': self.news_mention_count,
            'hurricane_analysis': self.hurricane_analysis.to_dict() if self.hurricane_analysis else None
        }


class HurricaneAnalysis(db.Model):
    """Linguistic analysis of hurricane names"""
    __tablename__ = 'hurricane_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    hurricane_id = db.Column(db.String(50), db.ForeignKey('hurricane.id'), nullable=False, unique=True)
    
    # Standard name metrics
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # Hurricane-specific metrics
    phonetic_harshness_score = db.Column(db.Float)  # Plosives, fricatives weighting
    gender_coded = db.Column(db.String(20))  # 'male', 'female', 'neutral', 'ambiguous'
    sentiment_polarity = db.Column(db.Float)  # -1.0 (negative) to +1.0 (positive)
    alphabetical_position = db.Column(db.Integer)  # A=1, Z=26 (seasonal position proxy)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'phonetic_score': self.phonetic_score,
            'memorability_score': self.memorability_score,
            'phonetic_harshness_score': self.phonetic_harshness_score,
            'gender_coded': self.gender_coded,
            'sentiment_polarity': self.sentiment_polarity,
            'alphabetical_position': self.alphabetical_position
        }


class GeographicDemographics(db.Model):
    """Census demographic baseline data for geographic areas"""
    __tablename__ = 'geographic_demographics'
    __table_args__ = (
        db.Index('idx_geo_demo_code_level', 'geographic_code', 'geographic_level'),
        db.Index('idx_geo_demo_year', 'year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    geographic_code = db.Column(db.String(50), nullable=False)  # FIPS code (county/tract/zip)
    geographic_level = db.Column(db.String(20), nullable=False)  # 'county', 'tract', 'zip'
    year = db.Column(db.Integer, nullable=False)  # Census/ACS year
    
    # Population totals
    total_population = db.Column(db.Integer)
    
    # Race/ethnicity breakdown (JSON for flexibility)
    race_breakdown = db.Column(db.Text)  # JSON: {white, black, asian, hispanic, native, pacific, other, multiracial}
    
    # Income distribution (JSON)
    income_breakdown = db.Column(db.Text)  # JSON: {quintile_1, quintile_2, ..., quintile_5}
    median_income = db.Column(db.Float)
    poverty_rate = db.Column(db.Float)  # Percentage below poverty line
    
    # Age distribution (JSON)
    age_breakdown = db.Column(db.Text)  # JSON: {under_18, 18_34, 35_49, 50_64, 65_74, 75_plus}
    
    # Additional socioeconomic indicators
    education_bachelors_plus_pct = db.Column(db.Float)
    homeownership_rate = db.Column(db.Float)
    median_home_value = db.Column(db.Float)
    
    # Metadata
    source = db.Column(db.String(100))  # 'ACS_5YR', 'DECENNIAL', etc.
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'geographic_code': self.geographic_code,
            'geographic_level': self.geographic_level,
            'year': self.year,
            'total_population': self.total_population,
            'race_breakdown': json.loads(self.race_breakdown) if self.race_breakdown else {},
            'income_breakdown': json.loads(self.income_breakdown) if self.income_breakdown else {},
            'median_income': self.median_income,
            'poverty_rate': self.poverty_rate,
            'age_breakdown': json.loads(self.age_breakdown) if self.age_breakdown else {},
            'education_bachelors_plus_pct': self.education_bachelors_plus_pct,
            'homeownership_rate': self.homeownership_rate,
            'median_home_value': self.median_home_value
        }


class HurricaneGeography(db.Model):
    """Hurricane impact zones mapped to Census geographies"""
    __tablename__ = 'hurricane_geography'
    __table_args__ = (
        db.Index('idx_hurr_geo_hurricane', 'hurricane_id'),
        db.Index('idx_hurr_geo_code', 'geographic_code'),
        db.Index('idx_hurr_geo_severity', 'impact_severity'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    hurricane_id = db.Column(db.String(50), db.ForeignKey('hurricane.id'), nullable=False)
    geographic_code = db.Column(db.String(50), nullable=False)  # FIPS code
    geographic_level = db.Column(db.String(20), nullable=False)  # 'county', 'tract', 'zip'
    
    # Impact classification
    impact_severity = db.Column(db.String(20))  # 'direct' (0-50mi), 'moderate' (50-100mi), 'peripheral' (100-200mi)
    distance_from_track_miles = db.Column(db.Float)  # Distance from hurricane center track
    
    # Track information
    closest_approach_date = db.Column(db.DateTime)  # When hurricane was closest
    max_wind_at_location_mph = db.Column(db.Integer)  # Estimated wind at this location
    
    # Geographic identifiers for joining
    state_fips = db.Column(db.String(2))
    county_fips = db.Column(db.String(3))
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'hurricane_id': self.hurricane_id,
            'geographic_code': self.geographic_code,
            'geographic_level': self.geographic_level,
            'impact_severity': self.impact_severity,
            'distance_from_track_miles': self.distance_from_track_miles,
            'closest_approach_date': self.closest_approach_date.isoformat() if self.closest_approach_date else None,
            'max_wind_at_location_mph': self.max_wind_at_location_mph
        }


class HurricaneDemographicImpact(db.Model):
    """Junction table linking hurricanes to demographic-specific outcomes"""
    __tablename__ = 'hurricane_demographic_impact'
    __table_args__ = (
        db.Index('idx_hurr_demo_hurricane', 'hurricane_id'),
        db.Index('idx_hurr_demo_category', 'demographic_category'),
        db.Index('idx_hurr_demo_geo', 'geographic_code'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    hurricane_id = db.Column(db.String(50), db.ForeignKey('hurricane.id'), nullable=False)
    
    # Geographic scope
    geographic_code = db.Column(db.String(50), nullable=False)  # FIPS code
    geographic_level = db.Column(db.String(20), nullable=False)  # 'county', 'tract', 'zip'
    
    # Demographic dimension
    demographic_category = db.Column(db.String(30), nullable=False)  # 'race', 'income_quintile', 'age_group'
    demographic_value = db.Column(db.String(50), nullable=False)  # e.g., 'white', 'quintile_1', '18_34'
    
    # Population at risk (baseline)
    population_at_risk = db.Column(db.Integer)  # Census count for this demographic in this geography
    
    # Outcomes - Casualties
    deaths = db.Column(db.Integer)  # Deaths in this demographic group
    injuries = db.Column(db.Integer)
    missing = db.Column(db.Integer)
    
    # Outcomes - Displacement
    displaced_persons = db.Column(db.Integer)  # Estimated displaced
    fema_applications = db.Column(db.Integer)  # FEMA Individual Assistance applications
    shelter_occupancy = db.Column(db.Integer)  # Peak shelter use by this demographic
    
    # Outcomes - Economic
    damage_estimate_usd = db.Column(db.Float)  # Estimated damage to this demographic's property
    fema_aid_received_usd = db.Column(db.Float)  # Aid distributed to this demographic
    
    # Calculated rates (for convenience)
    death_rate_per_1000 = db.Column(db.Float)  # deaths / population_at_risk * 1000
    displacement_rate = db.Column(db.Float)  # displaced / population_at_risk
    fema_application_rate = db.Column(db.Float)  # applications / population_at_risk
    
    # Data quality
    data_source = db.Column(db.String(100))  # Where this data came from
    confidence_level = db.Column(db.String(20))  # 'high', 'medium', 'low', 'estimated'
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'hurricane_id': self.hurricane_id,
            'geographic_code': self.geographic_code,
            'geographic_level': self.geographic_level,
            'demographic_category': self.demographic_category,
            'demographic_value': self.demographic_value,
            'population_at_risk': self.population_at_risk,
            'deaths': self.deaths,
            'injuries': self.injuries,
            'displaced_persons': self.displaced_persons,
            'fema_applications': self.fema_applications,
            'damage_estimate_usd': self.damage_estimate_usd,
            'fema_aid_received_usd': self.fema_aid_received_usd,
            'death_rate_per_1000': self.death_rate_per_1000,
            'displacement_rate': self.displacement_rate,
            'fema_application_rate': self.fema_application_rate,
            'confidence_level': self.confidence_level
        }


# =============================================================================
# MAGIC: THE GATHERING CARD TABLES
# =============================================================================

class MTGCard(db.Model):
    """Magic: The Gathering card data from Scryfall"""
    __tablename__ = 'mtg_card'
    __table_args__ = (
        db.Index('idx_mtg_rarity', 'rarity'),
        db.Index('idx_mtg_card_type', 'card_type'),
        db.Index('idx_mtg_price', 'price_usd'),
        db.Index('idx_mtg_is_legendary', 'is_legendary'),
    )
    
    id = db.Column(db.String(100), primary_key=True)  # Scryfall UUID
    name = db.Column(db.String(200), nullable=False, index=True)
    set_code = db.Column(db.String(10))
    set_name = db.Column(db.String(200))
    rarity = db.Column(db.String(20))  # common, uncommon, rare, mythic
    
    # Mechanical properties (controls for regression)
    mana_cost = db.Column(db.String(50))  # {3}{U}{U}
    converted_mana_cost = db.Column(db.Integer)  # Total mana value
    card_type = db.Column(db.String(100))  # "Creature — Dragon", "Instant", etc.
    power = db.Column(db.String(10))  # Creature power (can be *, X, number)
    toughness = db.Column(db.String(10))  # Creature toughness
    
    # Market data (outcomes)
    price_usd = db.Column(db.Float)
    price_usd_foil = db.Column(db.Float)
    price_eur = db.Column(db.Float)
    
    # Popularity/playability proxies (controls)
    edhrec_rank = db.Column(db.Integer)  # Commander format popularity (lower = more popular)
    num_decks = db.Column(db.Integer)  # Deck inclusion count
    
    # Metadata
    artist = db.Column(db.String(200))
    flavor_text = db.Column(db.Text)
    oracle_text = db.Column(db.Text)  # Rules text
    release_date = db.Column(db.Date)
    set_year = db.Column(db.Integer)  # Year of release
    
    # Format legalities (JSON: {format: 'legal'/'banned'/'restricted'/'not_legal'})
    format_legalities = db.Column(db.Text)  # JSON
    
    # Reprint data
    reprint_count = db.Column(db.Integer, default=0)  # How many times reprinted
    first_printing_set = db.Column(db.String(10))  # Original set code
    
    # Derived fields (for regression)
    log_price_usd = db.Column(db.Float)
    rarity_tier = db.Column(db.Integer)  # 1=common, 2=uncommon, 3=rare, 4=mythic
    is_legendary = db.Column(db.Boolean, default=False)
    is_creature = db.Column(db.Boolean, default=False)
    is_instant_sorcery = db.Column(db.Boolean, default=False)
    color_identity = db.Column(db.String(10))  # WUBRG
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    card_analysis = db.relationship('MTGCardAnalysis', backref='mtg_card', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'set_code': self.set_code,
            'set_name': self.set_name,
            'rarity': self.rarity,
            'mana_cost': self.mana_cost,
            'converted_mana_cost': self.converted_mana_cost,
            'card_type': self.card_type,
            'power': self.power,
            'toughness': self.toughness,
            'price_usd': self.price_usd,
            'price_usd_foil': self.price_usd_foil,
            'edhrec_rank': self.edhrec_rank,
            'is_legendary': self.is_legendary,
            'is_creature': self.is_creature,
            'artist': self.artist,
            'flavor_text': self.flavor_text,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'card_analysis': self.card_analysis.to_dict() if self.card_analysis else None
        }


class MTGCardAnalysis(db.Model):
    """Linguistic analysis of MTG card names"""
    __tablename__ = 'mtg_card_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(100), db.ForeignKey('mtg_card.id'), nullable=False, unique=True)
    
    # Standard name metrics
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # MTG-specific metrics
    fantasy_score = db.Column(db.Float)  # How "fantasy" sounding (0-100)
    power_connotation_score = db.Column(db.Float)  # Aggressive vs. gentle (-100 to +100)
    mythic_resonance_score = db.Column(db.Float)  # Epic/legendary linguistic quality (0-100)
    flavor_text_sentiment = db.Column(db.Float)  # Sentiment of flavor text (-1.0 to +1.0)
    constructed_language_score = db.Column(db.Float)  # Elven/Draconic/invented language feel
    
    # Advanced nominative dimensions (JSON fields for complex data)
    phonosemantic_data = db.Column(db.Text)  # JSON: phoneme alignment, color alignment, etc.
    constructed_lang_data = db.Column(db.Text)  # JSON: language archetypes, sophistication
    narrative_data = db.Column(db.Text)  # JSON: journey stage, transformation, agency
    semantic_data = db.Column(db.Text)  # JSON: semantic field scores, polar tensions
    format_affinity_data = db.Column(db.Text)  # JSON: format affinity scores
    intertextual_data = db.Column(db.Text)  # JSON: mythological/literary references
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'phonetic_score': self.phonetic_score,
            'memorability_score': self.memorability_score,
            'fantasy_score': self.fantasy_score,
            'power_connotation_score': self.power_connotation_score,
            'mythic_resonance_score': self.mythic_resonance_score,
            'flavor_text_sentiment': self.flavor_text_sentiment,
            'constructed_language_score': self.constructed_language_score
        }


# =============================================================================
# BAND TABLES
# =============================================================================

class Band(db.Model):
    """Musical band/artist data from MusicBrainz and Last.fm"""
    __tablename__ = 'band'
    __table_args__ = (
        db.Index('idx_band_formation_year', 'formation_year'),
        db.Index('idx_band_origin_country', 'origin_country'),
        db.Index('idx_band_popularity', 'popularity_score'),
        db.Index('idx_band_decade', 'formation_decade'),
    )
    
    id = db.Column(db.String(100), primary_key=True)  # MusicBrainz MBID
    name = db.Column(db.String(300), nullable=False, index=True)
    
    # Geographic origin
    origin_country = db.Column(db.String(100))  # Country code (US, GB, etc.)
    origin_country_name = db.Column(db.String(200))  # Full country name
    origin_city = db.Column(db.String(200))
    origin_state = db.Column(db.String(100))  # For US bands
    origin_region = db.Column(db.String(100))  # Geographic grouping
    
    # Temporal data
    formation_year = db.Column(db.Integer)
    formation_decade = db.Column(db.Integer)  # 1960, 1970, etc.
    dissolution_year = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    years_active = db.Column(db.Integer)  # Longevity metric
    
    # Genres (JSON array)
    genres = db.Column(db.Text)  # JSON list of genres
    primary_genre = db.Column(db.String(100))  # Main genre
    genre_cluster = db.Column(db.String(50))  # rock, pop, metal, electronic, etc.
    
    # Popularity metrics (from Last.fm)
    listeners_count = db.Column(db.Integer)  # Unique listeners
    play_count = db.Column(db.Integer)  # Total plays
    popularity_score = db.Column(db.Float)  # Normalized 0-100
    
    # Success indicators
    chart_success = db.Column(db.Boolean, default=False)  # Billboard/chart presence
    critical_acclaim_score = db.Column(db.Float)  # If available
    longevity_score = db.Column(db.Float)  # Multi-decade relevance
    cross_generational_appeal = db.Column(db.Boolean, default=False)  # Still popular 20+ years later
    
    # Fan base geographic data (JSON) - for post-2000 bands
    fan_base_countries = db.Column(db.Text)  # JSON: {country_code: listener_percentage}
    primary_market = db.Column(db.String(100))  # Where most popular
    
    # Linguistic/Cultural Demographics (from country data)
    language_family = db.Column(db.String(50))  # Germanic, Romance, Slavic, Uralic, etc.
    native_language = db.Column(db.String(50))  # Primary language of origin country
    linguistic_diversity_index = db.Column(db.Float)  # Country's linguistic diversity
    primary_script = db.Column(db.String(50))  # Latin, Cyrillic, Arabic, etc.
    english_native_speaker = db.Column(db.Boolean, default=False)  # English-speaking country
    english_proficiency_index = db.Column(db.Float)  # EPI score for non-native
    
    # Phonological features (from native language)
    allows_consonant_clusters = db.Column(db.Boolean)  # Native language permits clusters
    max_onset_complexity = db.Column(db.Integer)  # Max consonants in onset
    vowel_system_size = db.Column(db.Integer)  # Number of vowels in native language
    has_l_r_distinction = db.Column(db.Boolean, default=True)  # Japanese/Korean = False
    
    # Colonial History
    former_colony = db.Column(db.Boolean, default=False)  # Was a colony
    colonial_power = db.Column(db.String(50))  # Britain, Spain, France, etc.
    independence_year = db.Column(db.Integer)  # Year of independence
    years_independent = db.Column(db.Integer)  # Years since independence
    was_colonial_power = db.Column(db.Boolean, default=False)  # Was an empire
    
    # Socioeconomic Indicators
    gdp_per_capita = db.Column(db.Float)  # GDP per capita (USD)
    hdi_score = db.Column(db.Float)  # Human Development Index (0-1)
    education_index = db.Column(db.Float)  # HDI education component
    gini_coefficient = db.Column(db.Float)  # Income inequality (0-100)
    urbanization_rate = db.Column(db.Float)  # % urban population
    population_millions = db.Column(db.Float)  # Country population
    internet_penetration = db.Column(db.Float)  # % with internet access
    
    # Cultural Dimensions (Hofstede)
    hofstede_individualism = db.Column(db.Float)  # 0-100
    hofstede_power_distance = db.Column(db.Float)  # 0-100
    hofstede_masculinity = db.Column(db.Float)  # 0-100
    hofstede_uncertainty_avoidance = db.Column(db.Float)  # 0-100
    hofstede_long_term_orientation = db.Column(db.Float)  # 0-100
    hofstede_indulgence = db.Column(db.Float)  # 0-100
    
    # Cultural Values (World Values Survey)
    world_values_traditional_secular = db.Column(db.Float)  # -2 to +2
    world_values_survival_expression = db.Column(db.Float)  # -2 to +2
    globalization_index = db.Column(db.Float)  # KOF index (0-100)
    cultural_tightness_looseness = db.Column(db.Float)  # 0-10 scale
    
    # Religious/Cultural Context
    majority_religion = db.Column(db.String(50))  # Christian, Muslim, Hindu, etc.
    religious_diversity_index = db.Column(db.Float)  # 0-1 (higher = more diverse)
    secular_score = db.Column(db.Float)  # 0-10 (higher = more secular)
    
    # Immigration/Diaspora (for US/UK bands primarily)
    immigrant_generation = db.Column(db.Integer)  # 1st, 2nd, 3rd+ gen (if identifiable)
    diaspora_community = db.Column(db.String(100))  # e.g., "Irish-American", "British-Australian"
    has_foreign_surname = db.Column(db.Boolean, default=False)  # Non-English surname
    ethnic_markers_in_name = db.Column(db.Boolean, default=False)  # Spanish, Asian, etc. markers
    
    # Music Industry Context
    music_market_size = db.Column(db.Float)  # Billions USD
    music_market_rank = db.Column(db.Integer)  # Country rank
    bands_per_capita = db.Column(db.Float)  # Bands per million population
    
    # Metadata
    musicbrainz_url = db.Column(db.String(500))
    lastfm_url = db.Column(db.String(500))
    demographics_enriched = db.Column(db.Boolean, default=False)  # Has demographic data
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    band_analysis = db.relationship('BandAnalysis', backref='band', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'origin_country': self.origin_country,
            'origin_country_name': self.origin_country_name,
            'origin_city': self.origin_city,
            'formation_year': self.formation_year,
            'formation_decade': self.formation_decade,
            'dissolution_year': self.dissolution_year,
            'is_active': self.is_active,
            'years_active': self.years_active,
            'genres': json.loads(self.genres) if self.genres else [],
            'primary_genre': self.primary_genre,
            'genre_cluster': self.genre_cluster,
            'listeners_count': self.listeners_count,
            'play_count': self.play_count,
            'popularity_score': self.popularity_score,
            'chart_success': self.chart_success,
            'longevity_score': self.longevity_score,
            'cross_generational_appeal': self.cross_generational_appeal,
            'fan_base_countries': json.loads(self.fan_base_countries) if self.fan_base_countries else {},
            'primary_market': self.primary_market,
            'band_analysis': self.band_analysis.to_dict() if self.band_analysis else None
        }


class BandAnalysis(db.Model):
    """Linguistic analysis of band names"""
    __tablename__ = 'band_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    band_id = db.Column(db.String(100), db.ForeignKey('band.id'), nullable=False, unique=True)
    
    # Standard name metrics (matching other spheres)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # Band-specific linguistic metrics
    fantasy_score = db.Column(db.Float)  # Mythological/fantasy elements
    power_connotation_score = db.Column(db.Float)  # Aggressive vs gentle
    harshness_score = db.Column(db.Float)  # Phonetic harshness (for metal/punk)
    softness_score = db.Column(db.Float)  # Phonetic softness (for pop/folk)
    abstraction_score = db.Column(db.Float)  # Abstract vs concrete (0-100)
    literary_reference_score = db.Column(db.Float)  # Literary/cultural references
    
    # Temporal cohort metrics
    temporal_cohort = db.Column(db.String(20))  # '1960s', '1970s', etc.
    era_typicality_score = db.Column(db.Float)  # How typical for the era (0-100)
    temporal_innovation_score = db.Column(db.Float)  # How innovative for the time
    
    # Geographic cluster metrics
    geographic_cluster = db.Column(db.String(50))  # US_West, UK_North, Nordic, etc.
    regional_typicality_score = db.Column(db.Float)  # How typical for the region
    
    # Advanced nominative dimensions (JSON fields for complex data)
    phonosemantic_data = db.Column(db.Text)  # JSON: detailed phoneme analysis
    semantic_data = db.Column(db.Text)  # JSON: semantic field scores
    prosodic_data = db.Column(db.Text)  # JSON: rhythmic patterns
    sound_symbolism_data = db.Column(db.Text)  # JSON: sound symbolism features
    
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
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type,
            'fantasy_score': self.fantasy_score,
            'power_connotation_score': self.power_connotation_score,
            'harshness_score': self.harshness_score,
            'softness_score': self.softness_score,
            'abstraction_score': self.abstraction_score,
            'literary_reference_score': self.literary_reference_score,
            'temporal_cohort': self.temporal_cohort,
            'era_typicality_score': self.era_typicality_score,
            'temporal_innovation_score': self.temporal_innovation_score,
            'geographic_cluster': self.geographic_cluster,
            'regional_typicality_score': self.regional_typicality_score,
            'phonosemantic_data': json.loads(self.phonosemantic_data) if self.phonosemantic_data else {},
            'semantic_data': json.loads(self.semantic_data) if self.semantic_data else {},
            'prosodic_data': json.loads(self.prosodic_data) if self.prosodic_data else {},
            'sound_symbolism_data': json.loads(self.sound_symbolism_data) if self.sound_symbolism_data else {}
        }


# =============================================================================
# BAND MEMBER TABLES (INDIVIDUAL MEMBER NAME ANALYSIS)
# =============================================================================

class BandMember(db.Model):
    """Individual band member data"""
    __tablename__ = 'band_member'
    __table_args__ = (
        db.Index('idx_band_member_name', 'name'),
        db.Index('idx_band_member_role', 'primary_role'),
        db.Index('idx_band_member_band', 'band_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    band_id = db.Column(db.String(100), db.ForeignKey('band.id'))
    
    # Role information
    primary_role = db.Column(db.String(50))  # vocalist, guitarist, bassist, drummer, keyboardist
    secondary_roles = db.Column(db.Text)  # JSON array
    is_songwriter = db.Column(db.Boolean, default=False)
    is_lead_vocalist = db.Column(db.Boolean, default=False)
    is_founding_member = db.Column(db.Boolean, default=False)
    
    # Member metadata
    birth_year = db.Column(db.Integer)
    nationality = db.Column(db.String(100))
    years_active_start = db.Column(db.Integer)
    years_active_end = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to band
    band = db.relationship('Band', backref='members')
    analysis = db.relationship('BandMemberAnalysis', backref='member', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'band_id': self.band_id,
            'primary_role': self.primary_role,
            'secondary_roles': json.loads(self.secondary_roles) if self.secondary_roles else [],
            'is_songwriter': self.is_songwriter,
            'is_lead_vocalist': self.is_lead_vocalist,
            'is_founding_member': self.is_founding_member,
            'birth_year': self.birth_year,
            'nationality': self.nationality,
            'years_active_start': self.years_active_start,
            'years_active_end': self.years_active_end,
            'analysis': self.analysis.to_dict() if self.analysis else None
        }


class BandMemberAnalysis(db.Model):
    """Linguistic analysis of band member names"""
    __tablename__ = 'band_member_analysis'
    __table_args__ = (
        db.Index('idx_band_member_analysis_syllables', 'syllable_count'),
        db.Index('idx_band_member_analysis_harshness', 'phonetic_harshness'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('band_member.id'), nullable=False, unique=True)
    
    # Standard phonetic features
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    phonetic_harshness = db.Column(db.Float)
    phonetic_smoothness = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    
    # Name origin features
    name_origin = db.Column(db.String(50))  # Anglo, Nordic, Italian, etc.
    stage_name_indicator = db.Column(db.Boolean, default=False)  # vs birth name
    
    # Vowel/consonant features
    vowel_ratio = db.Column(db.Float)
    consonant_cluster_score = db.Column(db.Float)
    
    # Advanced features (JSON)
    phonetic_features_json = db.Column(db.Text)  # JSON: detailed phonetic breakdown
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllables': self.syllable_count,
            'length': self.character_length,
            'phonetic_harshness': self.phonetic_harshness,
            'phonetic_smoothness': self.phonetic_smoothness,
            'memorability': self.memorability_score,
            'uniqueness': self.uniqueness_score,
            'pronounceability': self.pronounceability_score,
            'name_origin': self.name_origin,
            'stage_name': self.stage_name_indicator,
            'vowel_ratio': self.vowel_ratio
        }


# =============================================================================
# NBA PLAYER TABLES
# =============================================================================

class NBAPlayer(db.Model):
    """NBA player data from Basketball Reference and other sources"""
    __tablename__ = 'nba_player'
    __table_args__ = (
        db.Index('idx_nba_debut_year', 'debut_year'),
        db.Index('idx_nba_position', 'position'),
        db.Index('idx_nba_era', 'era'),
        db.Index('idx_nba_performance', 'performance_score'),
    )
    
    id = db.Column(db.String(100), primary_key=True)  # Basketball Reference player ID
    name = db.Column(db.String(200), nullable=False, index=True)
    full_name = db.Column(db.String(300))  # Full legal name if available
    
    # Position data
    position = db.Column(db.String(10))  # PG, SG, SF, PF, C, or combinations (PG-SG)
    position_group = db.Column(db.String(20))  # Guard, Forward, Center
    primary_position = db.Column(db.String(5))  # Single primary position
    
    # Career span
    debut_year = db.Column(db.Integer)
    final_year = db.Column(db.Integer)
    years_active = db.Column(db.Integer)  # Total seasons played
    is_active = db.Column(db.Boolean, default=False)
    
    # Era classification
    era = db.Column(db.Integer)  # Decade of debut: 1950, 1960, etc.
    era_group = db.Column(db.String(30))  # Classic (pre-1980), Modern (1980-2000), Contemporary (2000+)
    
    # Performance statistics (career averages)
    games_played = db.Column(db.Integer)
    ppg = db.Column(db.Float)  # Points per game
    apg = db.Column(db.Float)  # Assists per game
    rpg = db.Column(db.Float)  # Rebounds per game
    spg = db.Column(db.Float)  # Steals per game
    bpg = db.Column(db.Float)  # Blocks per game
    fg_percentage = db.Column(db.Float)  # Field goal percentage
    three_point_percentage = db.Column(db.Float)  # 3-point percentage (null for pre-1979)
    ft_percentage = db.Column(db.Float)  # Free throw percentage
    
    # Advanced statistics
    per = db.Column(db.Float)  # Player Efficiency Rating
    career_ws = db.Column(db.Float)  # Win Shares (career total)
    ws_per_48 = db.Column(db.Float)  # Win Shares per 48 minutes
    vorp = db.Column(db.Float)  # Value Over Replacement Player
    bpm = db.Column(db.Float)  # Box Plus/Minus
    
    # Career achievements
    all_star_count = db.Column(db.Integer, default=0)  # All-Star selections
    all_nba_first_count = db.Column(db.Integer, default=0)  # First-team All-NBA
    all_nba_count = db.Column(db.Integer, default=0)  # Total All-NBA teams
    mvp_count = db.Column(db.Integer, default=0)  # MVP awards
    championship_count = db.Column(db.Integer, default=0)  # Championships won
    finals_mvp_count = db.Column(db.Integer, default=0)  # Finals MVP awards
    dpoy_count = db.Column(db.Integer, default=0)  # Defensive Player of Year
    hof_inducted = db.Column(db.Boolean, default=False)  # Hall of Fame
    hof_year = db.Column(db.Integer)  # Year inducted to HOF
    
    # Derived success metrics (0-100 scale)
    performance_score = db.Column(db.Float)  # Based on stats (PPG, APG, RPG, PER)
    career_achievement_score = db.Column(db.Float)  # Based on awards/honors
    longevity_score = db.Column(db.Float)  # Based on years active + sustained performance
    overall_success_score = db.Column(db.Float)  # Weighted combination of above
    
    # Physical attributes (if available)
    height_inches = db.Column(db.Integer)  # Height in inches
    weight_lbs = db.Column(db.Integer)  # Weight in pounds
    
    # College/origin
    college = db.Column(db.String(200))
    country = db.Column(db.String(100))  # Country of birth
    draft_year = db.Column(db.Integer)
    draft_round = db.Column(db.Integer)
    draft_pick = db.Column(db.Integer)
    
    # Teams played for (JSON list)
    teams = db.Column(db.Text)  # JSON array of team codes
    primary_team = db.Column(db.String(50))  # Team most associated with
    
    # Metadata
    basketball_reference_url = db.Column(db.String(500))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player_analysis = db.relationship('NBAPlayerAnalysis', backref='player', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'position': self.position,
            'position_group': self.position_group,
            'primary_position': self.primary_position,
            'debut_year': self.debut_year,
            'final_year': self.final_year,
            'years_active': self.years_active,
            'is_active': self.is_active,
            'era': self.era,
            'era_group': self.era_group,
            'games_played': self.games_played,
            'ppg': self.ppg,
            'apg': self.apg,
            'rpg': self.rpg,
            'per': self.per,
            'career_ws': self.career_ws,
            'all_star_count': self.all_star_count,
            'mvp_count': self.mvp_count,
            'championship_count': self.championship_count,
            'hof_inducted': self.hof_inducted,
            'performance_score': self.performance_score,
            'career_achievement_score': self.career_achievement_score,
            'longevity_score': self.longevity_score,
            'overall_success_score': self.overall_success_score,
            'height_inches': self.height_inches,
            'weight_lbs': self.weight_lbs,
            'college': self.college,
            'country': self.country,
            'teams': json.loads(self.teams) if self.teams else [],
            'primary_team': self.primary_team,
            'player_analysis': self.player_analysis.to_dict() if self.player_analysis else None
        }


class NBAPlayerAnalysis(db.Model):
    """Linguistic analysis of NBA player names"""
    __tablename__ = 'nba_player_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(100), db.ForeignKey('nba_player.id'), nullable=False, unique=True)
    
    # Standard name metrics (matching other spheres)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # First name analysis
    first_name_syllables = db.Column(db.Integer)
    first_name_length = db.Column(db.Integer)
    first_name_memorability = db.Column(db.Float)
    
    # Last name analysis
    last_name_syllables = db.Column(db.Integer)
    last_name_length = db.Column(db.Integer)
    last_name_memorability = db.Column(db.Float)
    
    # NBA-specific linguistic metrics
    power_connotation_score = db.Column(db.Float)  # Aggressive vs gentle
    harshness_score = db.Column(db.Float)  # Phonetic harshness (stops, fricatives)
    softness_score = db.Column(db.Float)  # Phonetic softness (liquids, glides)
    speed_association_score = db.Column(db.Float)  # Quick-sounding vs slow-sounding
    strength_association_score = db.Column(db.Float)  # Strong vs weak connotations
    
    # Phonetic complexity
    consonant_cluster_complexity = db.Column(db.Float)  # Difficulty of consonant combinations
    rhythm_score = db.Column(db.Float)  # Rhythmic flow (0-100)
    alliteration_score = db.Column(db.Float)  # First/last name alliteration
    
    # Cultural/ethnic indicators
    ethnic_origin_indicator = db.Column(db.String(50))  # Based on name pattern (indicative only)
    international_name_score = db.Column(db.Float)  # How "international" vs "American" sounding
    
    # Temporal cohort metrics
    temporal_cohort = db.Column(db.String(20))  # '1950s', '1960s', etc.
    era_typicality_score = db.Column(db.Float)  # How typical for the era (0-100)
    
    # Position cluster metrics
    position_cluster = db.Column(db.String(20))  # Guard, Forward, Center
    position_typicality_score = db.Column(db.Float)  # How typical for position
    
    # Advanced nominative dimensions (JSON fields for complex data)
    phonosemantic_data = db.Column(db.Text)  # JSON: detailed phoneme analysis
    semantic_data = db.Column(db.Text)  # JSON: semantic field scores
    prosodic_data = db.Column(db.Text)  # JSON: rhythmic patterns
    sound_symbolism_data = db.Column(db.Text)  # JSON: sound symbolism features
    
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
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type,
            'first_name_syllables': self.first_name_syllables,
            'first_name_length': self.first_name_length,
            'first_name_memorability': self.first_name_memorability,
            'last_name_syllables': self.last_name_syllables,
            'last_name_length': self.last_name_length,
            'last_name_memorability': self.last_name_memorability,
            'power_connotation_score': self.power_connotation_score,
            'harshness_score': self.harshness_score,
            'softness_score': self.softness_score,
            'speed_association_score': self.speed_association_score,
            'strength_association_score': self.strength_association_score,
            'consonant_cluster_complexity': self.consonant_cluster_complexity,
            'rhythm_score': self.rhythm_score,
            'alliteration_score': self.alliteration_score,
            'ethnic_origin_indicator': self.ethnic_origin_indicator,
            'international_name_score': self.international_name_score,
            'temporal_cohort': self.temporal_cohort,
            'era_typicality_score': self.era_typicality_score,
            'position_cluster': self.position_cluster,
            'position_typicality_score': self.position_typicality_score,
            'phonosemantic_data': json.loads(self.phonosemantic_data) if self.phonosemantic_data else {},
            'semantic_data': json.loads(self.semantic_data) if self.semantic_data else {},
            'prosodic_data': json.loads(self.prosodic_data) if self.prosodic_data else {},
            'sound_symbolism_data': json.loads(self.sound_symbolism_data) if self.sound_symbolism_data else {}
        }


# =============================================================================
# NFL PLAYER ANALYSIS
# =============================================================================

class NFLPlayer(db.Model):
    """NFL player data from Pro Football Reference and other sources"""
    __tablename__ = 'nfl_player'
    __table_args__ = (
        db.Index('idx_nfl_debut_year', 'debut_year'),
        db.Index('idx_nfl_position', 'position'),
        db.Index('idx_nfl_position_group', 'position_group'),
        db.Index('idx_nfl_era', 'era'),
        db.Index('idx_nfl_rule_era', 'rule_era'),
        db.Index('idx_nfl_performance', 'performance_score'),
    )
    
    id = db.Column(db.String(100), primary_key=True)  # Pro Football Reference player ID
    name = db.Column(db.String(200), nullable=False, index=True)
    full_name = db.Column(db.String(300))  # Full legal name if available
    
    # Position data
    position = db.Column(db.String(10))  # QB, RB, WR, TE, OT, OG, C, DE, DT, LB, CB, S, K, P, etc.
    position_group = db.Column(db.String(20))  # Offense, Defense, Special Teams
    position_category = db.Column(db.String(30))  # Skill, Offensive Line, Defensive Line, Linebackers, Defensive Backs, Special Teams
    primary_position = db.Column(db.String(5))  # Single primary position
    
    # Career span
    debut_year = db.Column(db.Integer)
    final_year = db.Column(db.Integer)
    years_active = db.Column(db.Integer)  # Total seasons played
    is_active = db.Column(db.Boolean, default=False)
    
    # Era classification (dual system)
    era = db.Column(db.Integer)  # Decade of debut: 1950, 1960, etc.
    era_group = db.Column(db.String(30))  # Pre-Modern (pre-1978), Modern (1978-2010), Contemporary (2010+)
    rule_era = db.Column(db.String(30))  # Dead Ball, Modern, Passing Era, Modern Offense
    
    # Basic career statistics
    games_played = db.Column(db.Integer)
    games_started = db.Column(db.Integer)
    
    # QB Statistics
    passing_attempts = db.Column(db.Integer)
    passing_completions = db.Column(db.Integer)
    completion_pct = db.Column(db.Float)  # Completion percentage
    passing_yards = db.Column(db.Integer)
    passing_tds = db.Column(db.Integer)  # Passing touchdowns
    interceptions = db.Column(db.Integer)
    passer_rating = db.Column(db.Float)  # NFL passer rating
    qbr = db.Column(db.Float)  # ESPN's Total QBR
    yards_per_attempt = db.Column(db.Float)  # Yards per pass attempt
    td_int_ratio = db.Column(db.Float)  # TD to INT ratio
    
    # RB/Rushing Statistics
    rushing_attempts = db.Column(db.Integer)
    rushing_yards = db.Column(db.Integer)
    rushing_tds = db.Column(db.Integer)
    yards_per_carry = db.Column(db.Float)  # Yards per rushing attempt
    rushing_fumbles = db.Column(db.Integer)
    
    # WR/TE/Receiving Statistics
    receptions = db.Column(db.Integer)
    receiving_yards = db.Column(db.Integer)
    receiving_tds = db.Column(db.Integer)
    yards_per_reception = db.Column(db.Float)
    catch_rate = db.Column(db.Float)  # Receptions / Targets
    targets = db.Column(db.Integer)
    drops = db.Column(db.Integer)
    yards_after_catch = db.Column(db.Float)  # Average YAC
    
    # Offensive Line Statistics (limited availability)
    sacks_allowed = db.Column(db.Integer)
    penalties = db.Column(db.Integer)
    
    # Defensive Statistics
    tackles = db.Column(db.Integer)  # Total tackles
    solo_tackles = db.Column(db.Integer)
    assisted_tackles = db.Column(db.Integer)
    sacks = db.Column(db.Float)  # Sacks (can be fractional)
    tackles_for_loss = db.Column(db.Integer)
    qb_hits = db.Column(db.Integer)
    defensive_interceptions = db.Column(db.Integer)
    pass_deflections = db.Column(db.Integer)
    forced_fumbles = db.Column(db.Integer)
    fumble_recoveries = db.Column(db.Integer)
    defensive_tds = db.Column(db.Integer)
    
    # Special Teams Statistics
    field_goals_made = db.Column(db.Integer)
    field_goals_attempted = db.Column(db.Integer)
    field_goal_pct = db.Column(db.Float)
    extra_points_made = db.Column(db.Integer)
    extra_points_attempted = db.Column(db.Integer)
    extra_point_pct = db.Column(db.Float)
    punts = db.Column(db.Integer)
    punting_avg = db.Column(db.Float)  # Average punt distance
    punts_inside_20 = db.Column(db.Integer)
    touchback_pct = db.Column(db.Float)
    
    # Advanced metrics
    approximate_value = db.Column(db.Float)  # Pro Football Reference's AV metric
    career_av = db.Column(db.Float)  # Career total AV
    weighted_career_av = db.Column(db.Float)  # Weighted career AV
    
    # Career achievements
    pro_bowl_count = db.Column(db.Integer, default=0)  # Pro Bowl selections
    all_pro_first_count = db.Column(db.Integer, default=0)  # First-team All-Pro
    all_pro_count = db.Column(db.Integer, default=0)  # Total All-Pro teams (1st + 2nd)
    mvp_count = db.Column(db.Integer, default=0)  # MVP awards
    championship_count = db.Column(db.Integer, default=0)  # Championships won (Super Bowls)
    super_bowl_mvp_count = db.Column(db.Integer, default=0)  # Super Bowl MVP awards
    dpoy_count = db.Column(db.Integer, default=0)  # Defensive Player of Year
    opoy_count = db.Column(db.Integer, default=0)  # Offensive Player of Year
    oroy_count = db.Column(db.Integer, default=0)  # Offensive Rookie of Year
    droy_count = db.Column(db.Integer, default=0)  # Defensive Rookie of Year
    hof_inducted = db.Column(db.Boolean, default=False)  # Hall of Fame
    hof_year = db.Column(db.Integer)  # Year inducted to HOF
    
    # Derived success metrics (0-100 scale)
    performance_score = db.Column(db.Float)  # Based on position-specific stats
    career_achievement_score = db.Column(db.Float)  # Based on awards/honors
    longevity_score = db.Column(db.Float)  # Based on years active + sustained performance
    overall_success_score = db.Column(db.Float)  # Weighted combination of above
    
    # Physical attributes (if available)
    height_inches = db.Column(db.Integer)  # Height in inches
    weight_lbs = db.Column(db.Integer)  # Weight in pounds
    
    # College/origin
    college = db.Column(db.String(200))
    draft_year = db.Column(db.Integer)
    draft_round = db.Column(db.Integer)
    draft_pick = db.Column(db.Integer)
    draft_team = db.Column(db.String(50))
    
    # Teams played for (JSON list)
    teams = db.Column(db.Text)  # JSON array of team codes
    primary_team = db.Column(db.String(50))  # Team most associated with
    
    # Metadata
    pro_football_reference_url = db.Column(db.String(500))
    nfl_com_id = db.Column(db.String(100))  # NFL.com player ID
    espn_id = db.Column(db.String(100))  # ESPN player ID
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player_analysis = db.relationship('NFLPlayerAnalysis', backref='player', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'position': self.position,
            'position_group': self.position_group,
            'position_category': self.position_category,
            'primary_position': self.primary_position,
            'debut_year': self.debut_year,
            'final_year': self.final_year,
            'years_active': self.years_active,
            'is_active': self.is_active,
            'era': self.era,
            'era_group': self.era_group,
            'rule_era': self.rule_era,
            'games_played': self.games_played,
            'games_started': self.games_started,
            # QB stats
            'completion_pct': self.completion_pct,
            'passing_yards': self.passing_yards,
            'passing_tds': self.passing_tds,
            'interceptions': self.interceptions,
            'passer_rating': self.passer_rating,
            'qbr': self.qbr,
            'yards_per_attempt': self.yards_per_attempt,
            'td_int_ratio': self.td_int_ratio,
            # RB stats
            'rushing_yards': self.rushing_yards,
            'rushing_tds': self.rushing_tds,
            'yards_per_carry': self.yards_per_carry,
            'rushing_fumbles': self.rushing_fumbles,
            # Receiving stats
            'receptions': self.receptions,
            'receiving_yards': self.receiving_yards,
            'receiving_tds': self.receiving_tds,
            'yards_per_reception': self.yards_per_reception,
            'catch_rate': self.catch_rate,
            'yards_after_catch': self.yards_after_catch,
            # Defensive stats
            'tackles': self.tackles,
            'sacks': self.sacks,
            'defensive_interceptions': self.defensive_interceptions,
            'forced_fumbles': self.forced_fumbles,
            'pass_deflections': self.pass_deflections,
            # Special teams
            'field_goal_pct': self.field_goal_pct,
            'punting_avg': self.punting_avg,
            # Advanced metrics
            'approximate_value': self.approximate_value,
            'career_av': self.career_av,
            # Achievements
            'pro_bowl_count': self.pro_bowl_count,
            'all_pro_count': self.all_pro_count,
            'mvp_count': self.mvp_count,
            'championship_count': self.championship_count,
            'super_bowl_mvp_count': self.super_bowl_mvp_count,
            'hof_inducted': self.hof_inducted,
            # Success scores
            'performance_score': self.performance_score,
            'career_achievement_score': self.career_achievement_score,
            'longevity_score': self.longevity_score,
            'overall_success_score': self.overall_success_score,
            # Physical
            'height_inches': self.height_inches,
            'weight_lbs': self.weight_lbs,
            # Other
            'college': self.college,
            'draft_year': self.draft_year,
            'draft_round': self.draft_round,
            'teams': json.loads(self.teams) if self.teams else [],
            'primary_team': self.primary_team,
            'player_analysis': self.player_analysis.to_dict() if self.player_analysis else None
        }


class NFLPlayerAnalysis(db.Model):
    """Linguistic analysis of NFL player names"""
    __tablename__ = 'nfl_player_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(100), db.ForeignKey('nfl_player.id'), nullable=False, unique=True)
    
    # Standard name metrics (matching other spheres)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # First name analysis
    first_name_syllables = db.Column(db.Integer)
    first_name_length = db.Column(db.Integer)
    first_name_memorability = db.Column(db.Float)
    
    # Last name analysis
    last_name_syllables = db.Column(db.Integer)
    last_name_length = db.Column(db.Integer)
    last_name_memorability = db.Column(db.Float)
    
    # NFL-specific linguistic metrics
    power_connotation_score = db.Column(db.Float)  # Aggressive vs gentle
    harshness_score = db.Column(db.Float)  # Phonetic harshness (stops, fricatives)
    softness_score = db.Column(db.Float)  # Phonetic softness (liquids, glides)
    speed_association_score = db.Column(db.Float)  # Quick-sounding vs slow-sounding
    strength_association_score = db.Column(db.Float)  # Strong vs weak connotations
    toughness_score = db.Column(db.Float)  # Toughness association (relevant for contact sport)
    
    # Phonetic complexity
    consonant_cluster_complexity = db.Column(db.Float)  # Difficulty of consonant combinations
    rhythm_score = db.Column(db.Float)  # Rhythmic flow (0-100)
    alliteration_score = db.Column(db.Float)  # First/last name alliteration
    
    # Cultural/ethnic indicators
    ethnic_origin_indicator = db.Column(db.String(50))  # Based on name pattern (indicative only)
    international_name_score = db.Column(db.Float)  # How "international" vs "American" sounding
    
    # Temporal cohort metrics
    temporal_cohort = db.Column(db.String(20))  # '1950s', '1960s', etc.
    era_typicality_score = db.Column(db.Float)  # How typical for the era (0-100)
    rule_era_cohort = db.Column(db.String(30))  # Dead Ball, Modern, Passing Era, Modern Offense
    
    # Position cluster metrics
    position_cluster = db.Column(db.String(30))  # Offense, Defense, Special Teams
    position_category_cluster = db.Column(db.String(30))  # Skill, Line, etc.
    position_typicality_score = db.Column(db.Float)  # How typical for position
    
    # Advanced nominative dimensions (JSON fields for complex data)
    phonosemantic_data = db.Column(db.Text)  # JSON: detailed phoneme analysis
    semantic_data = db.Column(db.Text)  # JSON: semantic field scores
    prosodic_data = db.Column(db.Text)  # JSON: rhythmic patterns
    sound_symbolism_data = db.Column(db.Text)  # JSON: sound symbolism features
    
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
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type,
            'first_name_syllables': self.first_name_syllables,
            'first_name_length': self.first_name_length,
            'first_name_memorability': self.first_name_memorability,
            'last_name_syllables': self.last_name_syllables,
            'last_name_length': self.last_name_length,
            'last_name_memorability': self.last_name_memorability,
            'power_connotation_score': self.power_connotation_score,
            'harshness_score': self.harshness_score,
            'softness_score': self.softness_score,
            'speed_association_score': self.speed_association_score,
            'strength_association_score': self.strength_association_score,
            'toughness_score': self.toughness_score,
            'consonant_cluster_complexity': self.consonant_cluster_complexity,
            'rhythm_score': self.rhythm_score,
            'alliteration_score': self.alliteration_score,
            'ethnic_origin_indicator': self.ethnic_origin_indicator,
            'international_name_score': self.international_name_score,
            'temporal_cohort': self.temporal_cohort,
            'era_typicality_score': self.era_typicality_score,
            'rule_era_cohort': self.rule_era_cohort,
            'position_cluster': self.position_cluster,
            'position_category_cluster': self.position_category_cluster,
            'position_typicality_score': self.position_typicality_score,
            'phonosemantic_data': json.loads(self.phonosemantic_data) if self.phonosemantic_data else {},
            'semantic_data': json.loads(self.semantic_data) if self.semantic_data else {},
            'prosodic_data': json.loads(self.prosodic_data) if self.prosodic_data else {},
            'sound_symbolism_data': json.loads(self.sound_symbolism_data) if self.sound_symbolism_data else {}
        }


# =============================================================================
# MENTAL HEALTH TERMS (DIAGNOSES & MEDICATIONS)
# =============================================================================

class MentalHealthTerm(db.Model):
    """Mental health diagnoses, conditions, and medications"""
    __tablename__ = 'mental_health_term'
    __table_args__ = (
        db.Index('idx_mh_type', 'term_type'),
        db.Index('idx_mh_category', 'category'),
        db.Index('idx_mh_prevalence', 'prevalence_rate'),
        db.Index('idx_mh_usage_rank', 'usage_rank'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    term_type = db.Column(db.String(50), nullable=False)  # 'diagnosis', 'medication', 'condition', 'system'
    category = db.Column(db.String(100))  # 'mood_disorder', 'antidepressant', 'antipsychotic', 'DSM-5', etc.
    subcategory = db.Column(db.String(100))  # 'SSRI', 'anxiety', 'bipolar_spectrum', etc.
    
    # Performance/usage metrics
    prevalence_rate = db.Column(db.Float)  # Diagnostic prevalence or prescription frequency (%)
    usage_rank = db.Column(db.Integer)  # Prescription frequency rank or diagnostic frequency rank
    
    # Temporal data
    year_introduced = db.Column(db.Integer)  # When diagnosis/medication entered use
    
    # Classification
    official_classification = db.Column(db.String(100))  # DSM-5-TR code, ICD-11 code, FDA approval
    
    # Medication-specific fields
    brand_names = db.Column(db.Text)  # Comma-separated brand names
    generic_name = db.Column(db.String(200))  # For brand name entries, link to generic
    
    # Stigma and obsolescence
    stigma_score = db.Column(db.Float)  # Calculated metric based on sentiment/usage patterns
    is_obsolete = db.Column(db.Boolean, default=False)  # For deprecated diagnoses
    
    # Timestamps
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = db.relationship('MentalHealthAnalysis', backref='term', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'term_type': self.term_type,
            'category': self.category,
            'subcategory': self.subcategory,
            'prevalence_rate': self.prevalence_rate,
            'usage_rank': self.usage_rank,
            'year_introduced': self.year_introduced,
            'official_classification': self.official_classification,
            'brand_names': self.brand_names,
            'generic_name': self.generic_name,
            'stigma_score': self.stigma_score,
            'is_obsolete': self.is_obsolete,
            'analysis': self.analysis.to_dict() if self.analysis else None
        }


class MentalHealthAnalysis(db.Model):
    """Linguistic analysis of mental health terms"""
    __tablename__ = 'mental_health_analysis'
    __table_args__ = (
        db.Index('idx_mh_analysis_memorability', 'memorability_score'),
        db.Index('idx_mh_analysis_pronounce', 'pronounceability_clinical'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('mental_health_term.id'), nullable=False, unique=True)
    
    # Standard linguistic metrics
    character_length = db.Column(db.Integer)
    syllable_count = db.Column(db.Integer)
    phoneme_count = db.Column(db.Integer)
    consonant_count = db.Column(db.Integer)
    vowel_count = db.Column(db.Integer)
    
    # Memorability & pronounceability
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    # Mental health specific metrics
    pronounceability_clinical = db.Column(db.Float)  # Ease for medical professionals
    patient_friendliness = db.Column(db.Float)  # Ease for patients to remember/say
    latin_roots_score = db.Column(db.Float)  # Medical terminology linguistic pattern
    stigma_linguistic_markers = db.Column(db.Float)  # Harsh phonemes, negative associations
    
    # Phonetic features
    harshness_score = db.Column(db.Float)
    speed_score = db.Column(db.Float)
    strength_score = db.Column(db.Float)
    
    # Advanced features (JSON)
    phonetic_data = db.Column(db.Text)  # JSON with detailed phonetic breakdown
    semantic_data = db.Column(db.Text)  # JSON with semantic associations
    etymology_data = db.Column(db.Text)  # JSON with root word analysis
    
    # Analysis metadata
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'character_length': self.character_length,
            'syllable_count': self.syllable_count,
            'phoneme_count': self.phoneme_count,
            'consonant_count': self.consonant_count,
            'vowel_count': self.vowel_count,
            'memorability_score': self.memorability_score,
            'pronounceability_score': self.pronounceability_score,
            'uniqueness_score': self.uniqueness_score,
            'pronounceability_clinical': self.pronounceability_clinical,
            'patient_friendliness': self.patient_friendliness,
            'latin_roots_score': self.latin_roots_score,
            'stigma_linguistic_markers': self.stigma_linguistic_markers,
            'harshness_score': self.harshness_score,
            'speed_score': self.speed_score,
            'strength_score': self.strength_score,
            'phonetic_data': json.loads(self.phonetic_data) if self.phonetic_data else {},
            'semantic_data': json.loads(self.semantic_data) if self.semantic_data else {},
            'etymology_data': json.loads(self.etymology_data) if self.etymology_data else {}
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


# =============================================================================
# ACADEMIC NAMES ANALYSIS (NOMINATIVE DETERMINISM IN ACADEMIA)
# =============================================================================

class Academic(db.Model):
    """University professor data for nominative determinism analysis"""
    __tablename__ = 'academic'
    __table_args__ = (
        db.Index('idx_academic_university_rank', 'university_name', 'academic_rank'),
        db.Index('idx_academic_ranking', 'university_ranking'),
        db.Index('idx_academic_field', 'field_broad'),
        db.Index('idx_academic_tier', 'university_tier'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(300), nullable=False, index=True)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), index=True)
    
    # Academic position
    academic_rank = db.Column(db.String(50), index=True)  # 'assistant', 'associate', 'full', 'distinguished', 'endowed', 'emeritus'
    title = db.Column(db.String(200))  # Full title (e.g., "John Smith Endowed Chair in Physics")
    
    # University affiliation
    university_name = db.Column(db.String(200), nullable=False, index=True)
    university_ranking = db.Column(db.Integer)  # US News ranking (lower = better)
    university_tier = db.Column(db.String(20))  # 'top_20', 'top_50', 'top_100', 'teaching_focused', 'other'
    
    # Department and field
    department = db.Column(db.String(200))
    field_broad = db.Column(db.String(50), index=True)  # 'stem', 'humanities', 'social_science', 'professional', 'interdisciplinary'
    field_specific = db.Column(db.String(100))  # 'physics', 'english', 'economics', 'medicine', etc.
    
    # Career information
    years_at_institution = db.Column(db.Integer)
    phd_institution = db.Column(db.String(200))
    phd_year = db.Column(db.Integer)
    phd_institution_ranking = db.Column(db.Integer)  # PhD institution prestige
    
    # Contact and profile
    email = db.Column(db.String(200))
    profile_url = db.Column(db.String(500))
    google_scholar_id = db.Column(db.String(100))
    google_scholar_url = db.Column(db.String(500))
    
    # Collection metadata
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_source = db.Column(db.String(100))  # 'university_directory', 'manual', 'api'
    
    # Relationships
    analysis = db.relationship('AcademicAnalysis', backref='academic', uselist=False, cascade='all, delete-orphan')
    research_metrics = db.relationship('AcademicResearchMetrics', backref='academic', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'academic_rank': self.academic_rank,
            'title': self.title,
            'university_name': self.university_name,
            'university_ranking': self.university_ranking,
            'university_tier': self.university_tier,
            'department': self.department,
            'field_broad': self.field_broad,
            'field_specific': self.field_specific,
            'years_at_institution': self.years_at_institution,
            'phd_institution': self.phd_institution,
            'phd_year': self.phd_year,
            'profile_url': self.profile_url,
            'analysis': self.analysis.to_dict() if self.analysis else None,
            'research_metrics': self.research_metrics.to_dict() if self.research_metrics else None
        }


class AcademicAnalysis(db.Model):
    """Phonetic and linguistic analysis of academic names"""
    __tablename__ = 'academic_analysis'
    __table_args__ = (
        db.Index('idx_academic_analysis_authority', 'authority_score'),
        db.Index('idx_academic_analysis_sophistication', 'intellectual_sophistication_score'),
        db.Index('idx_academic_analysis_memorability', 'memorability_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    academic_id = db.Column(db.Integer, db.ForeignKey('academic.id'), nullable=False, unique=True)
    
    # Basic linguistic metrics (from NameAnalyzer)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic analysis (from NameAnalyzer)
    phonetic_score = db.Column(db.Float)  # Overall euphony (0-100)
    vowel_ratio = db.Column(db.Float)
    consonant_clusters = db.Column(db.Integer)
    
    # Memorability and pronounceability (from NameAnalyzer)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    # Advanced phonetic features (from AdvancedAnalyzer)
    phonestheme_score = db.Column(db.Float)
    phonestheme_type = db.Column(db.String(50))
    vowel_brightness = db.Column(db.Float)
    vowel_emotion_profile = db.Column(db.String(50))
    consonant_hardness = db.Column(db.Float)
    
    # Psychological impact (from AdvancedAnalyzer)
    authority_score = db.Column(db.Float, index=True)
    innovation_score = db.Column(db.Float)
    trust_score = db.Column(db.Float)
    
    # Phonemic features (from PhonemicAnalyzer)
    plosive_ratio = db.Column(db.Float)
    fricative_ratio = db.Column(db.Float)
    voicing_ratio = db.Column(db.Float)
    initial_is_plosive = db.Column(db.Boolean)
    
    # Academic-specific composite scores
    intellectual_sophistication_score = db.Column(db.Float, index=True)  # Composite: syllables + phonetic complexity + uniqueness
    prestige_phonetic_alignment = db.Column(db.Float)  # Similarity to top-20 professor names (0-100)
    academic_authority_composite = db.Column(db.Float)  # Composite: authority + consonant hardness + memorability
    
    # Name categorization
    name_type = db.Column(db.String(50))
    has_numbers = db.Column(db.Boolean, default=False)
    has_special_chars = db.Column(db.Boolean, default=False)
    capital_pattern = db.Column(db.String(50))
    
    # Cultural/ethnic coding (for controls)
    likely_ethnic_origin = db.Column(db.String(50))  # 'western_european', 'asian', 'hispanic', 'middle_eastern', etc.
    gender_coding = db.Column(db.String(20))  # 'masculine', 'feminine', 'neutral', 'ambiguous'
    
    # Analysis metadata
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'phonetic_score': self.phonetic_score,
            'vowel_ratio': self.vowel_ratio,
            'consonant_clusters': self.consonant_clusters,
            'memorability_score': self.memorability_score,
            'pronounceability_score': self.pronounceability_score,
            'uniqueness_score': self.uniqueness_score,
            'authority_score': self.authority_score,
            'innovation_score': self.innovation_score,
            'trust_score': self.trust_score,
            'consonant_hardness': self.consonant_hardness,
            'vowel_brightness': self.vowel_brightness,
            'intellectual_sophistication_score': self.intellectual_sophistication_score,
            'prestige_phonetic_alignment': self.prestige_phonetic_alignment,
            'academic_authority_composite': self.academic_authority_composite,
            'gender_coding': self.gender_coding
        }


class AcademicResearchMetrics(db.Model):
    """Google Scholar research productivity metrics"""
    __tablename__ = 'academic_research_metrics'
    __table_args__ = (
        db.Index('idx_research_h_index', 'h_index'),
        db.Index('idx_research_citations', 'total_citations'),
        db.Index('idx_research_productivity', 'citations_per_year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    academic_id = db.Column(db.Integer, db.ForeignKey('academic.id'), nullable=False, unique=True)
    
    # Core Google Scholar metrics
    h_index = db.Column(db.Integer, index=True)  # Primary productivity measure
    total_citations = db.Column(db.Integer, index=True)
    i10_index = db.Column(db.Integer)  # Papers with 10+ citations
    
    # Temporal metrics
    years_publishing = db.Column(db.Integer)  # Years since first publication
    first_publication_year = db.Column(db.Integer)
    most_recent_publication_year = db.Column(db.Integer)
    
    # Derived productivity metrics
    citations_per_year = db.Column(db.Float, index=True)  # total_citations / years_publishing
    h_index_per_year = db.Column(db.Float)  # h_index / years_publishing
    papers_per_year = db.Column(db.Float)  # Estimated publication rate
    
    # Field normalization
    field_normalized_citations = db.Column(db.Float)  # Citations relative to field median
    field_normalized_h_index = db.Column(db.Float)  # h-index relative to field median
    
    # Top publications
    most_cited_paper_title = db.Column(db.String(500))
    most_cited_paper_citations = db.Column(db.Integer)
    most_cited_paper_year = db.Column(db.Integer)
    
    # Co-authorship
    total_coauthors = db.Column(db.Integer)
    average_coauthors_per_paper = db.Column(db.Float)
    
    # Collection metadata
    collected_from_google_scholar = db.Column(db.Boolean, default=False)
    google_scholar_last_updated = db.Column(db.DateTime)
    collection_errors = db.Column(db.Text)  # Any errors during collection
    
    def to_dict(self):
        return {
            'h_index': self.h_index,
            'total_citations': self.total_citations,
            'i10_index': self.i10_index,
            'years_publishing': self.years_publishing,
            'citations_per_year': self.citations_per_year,
            'field_normalized_citations': self.field_normalized_citations,
            'field_normalized_h_index': self.field_normalized_h_index,
            'most_cited_paper_title': self.most_cited_paper_title,
            'most_cited_paper_citations': self.most_cited_paper_citations
        }


# =============================================================================
# SHIP TABLES (NOMINATIVE DETERMINISM IN MARITIME HISTORY)
# =============================================================================

class Ship(db.Model):
    """Historical ship data for nominative determinism analysis"""
    __tablename__ = 'ship'
    __table_args__ = (
        db.Index('idx_ship_type', 'ship_type'),
        db.Index('idx_ship_nation', 'nation'),
        db.Index('idx_ship_era', 'era'),
        db.Index('idx_ship_significance', 'historical_significance_score'),
        db.Index('idx_ship_name_category', 'name_category'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    full_designation = db.Column(db.String(250))  # e.g., "HMS Beagle", "USS Constitution"
    prefix = db.Column(db.String(20))  # HMS, USS, RMS, SS, etc.
    
    # Classification
    ship_type = db.Column(db.String(50), index=True)  # 'naval', 'exploration', 'commercial', 'passenger'
    ship_class = db.Column(db.String(100))  # Ship class (e.g., "Cherokee-class brig-sloop")
    nation = db.Column(db.String(100), index=True)  # Country of origin
    
    # Temporal data
    launch_year = db.Column(db.Integer)
    decommission_year = db.Column(db.Integer)
    years_active = db.Column(db.Integer)  # Longevity metric
    era = db.Column(db.String(50), index=True)  # 'age_of_sail', 'steam_era', 'modern', 'age_of_discovery'
    era_decade = db.Column(db.Integer)  # Launch decade
    
    # Achievement metrics (OUTCOMES)
    historical_significance_score = db.Column(db.Float, index=True)  # 0-100 composite score
    major_events_count = db.Column(db.Integer)  # Number of notable events/battles/discoveries
    battles_participated = db.Column(db.Integer)  # For naval vessels
    battles_won = db.Column(db.Integer)
    ships_sunk = db.Column(db.Integer)  # Enemy vessels defeated
    
    # Exploration/Scientific achievement
    major_discoveries = db.Column(db.Text)  # JSON list of discoveries
    famous_voyages = db.Column(db.Text)  # JSON list of notable voyages
    scientific_contributions = db.Column(db.Text)  # JSON: scientific achievements
    notable_crew_members = db.Column(db.Text)  # JSON: famous people aboard (Darwin, Cook, etc.)
    
    # Mission/Purpose
    primary_purpose = db.Column(db.String(200))  # Main mission type
    secondary_purposes = db.Column(db.Text)  # JSON list
    
    # Geographic data
    home_port = db.Column(db.String(200))
    primary_theater = db.Column(db.String(200))  # Main area of operation
    regions_operated = db.Column(db.Text)  # JSON list of regions
    
    # Physical specifications (control variables)
    tonnage = db.Column(db.Integer)
    crew_size = db.Column(db.Integer)
    armament = db.Column(db.String(200))  # For naval vessels
    
    # Outcome tracking
    crew_casualties = db.Column(db.Integer)  # Total casualties during service
    notable_achievements = db.Column(db.Text)  # JSON list of achievements
    awards_decorations = db.Column(db.Text)  # JSON list of honors
    
    # Failure tracking (survivorship bias elimination)
    was_sunk = db.Column(db.Boolean, default=False)
    sunk_year = db.Column(db.Integer)
    sunk_reason = db.Column(db.String(200))  # 'battle', 'storm', 'accident', 'scuttled', etc.
    sunk_location = db.Column(db.String(200))
    
    # Name categorization (for primary analysis)
    name_category = db.Column(db.String(50), index=True)  # 'geographic', 'saint', 'monarch', 'virtue', 'mythological', 'animal', 'other'
    geographic_origin = db.Column(db.String(200))  # If geographic name, which place?
    geographic_lat = db.Column(db.Float)  # Geocoded location of place name
    geographic_lon = db.Column(db.Float)
    
    # Cultural prestige (for geographic names)
    place_cultural_prestige_score = db.Column(db.Float)  # Historical/cultural importance of place (0-100)
    place_population = db.Column(db.Integer)  # Population of place at time of naming
    place_type = db.Column(db.String(50))  # 'city', 'region', 'country', 'landmark'
    
    # Data quality and sources
    data_completeness_score = db.Column(db.Float)  # 0-100, how complete is the data
    primary_source = db.Column(db.String(200))  # Wikipedia, Naval Archives, etc.
    wikipedia_url = db.Column(db.String(500))
    external_references = db.Column(db.Text)  # JSON list of sources
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ship_analysis = db.relationship('ShipAnalysis', backref='ship', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'full_designation': self.full_designation,
            'prefix': self.prefix,
            'ship_type': self.ship_type,
            'ship_class': self.ship_class,
            'nation': self.nation,
            'launch_year': self.launch_year,
            'decommission_year': self.decommission_year,
            'years_active': self.years_active,
            'era': self.era,
            'historical_significance_score': self.historical_significance_score,
            'major_events_count': self.major_events_count,
            'battles_participated': self.battles_participated,
            'battles_won': self.battles_won,
            'ships_sunk': self.ships_sunk,
            'major_discoveries': json.loads(self.major_discoveries) if self.major_discoveries else [],
            'famous_voyages': json.loads(self.famous_voyages) if self.famous_voyages else [],
            'scientific_contributions': json.loads(self.scientific_contributions) if self.scientific_contributions else [],
            'notable_crew_members': json.loads(self.notable_crew_members) if self.notable_crew_members else [],
            'primary_purpose': self.primary_purpose,
            'home_port': self.home_port,
            'primary_theater': self.primary_theater,
            'regions_operated': json.loads(self.regions_operated) if self.regions_operated else [],
            'tonnage': self.tonnage,
            'crew_size': self.crew_size,
            'was_sunk': self.was_sunk,
            'sunk_year': self.sunk_year,
            'sunk_reason': self.sunk_reason,
            'name_category': self.name_category,
            'geographic_origin': self.geographic_origin,
            'place_cultural_prestige_score': self.place_cultural_prestige_score,
            'data_completeness_score': self.data_completeness_score,
            'ship_analysis': self.ship_analysis.to_dict() if self.ship_analysis else None
        }


class ShipAnalysis(db.Model):
    """Linguistic and semantic analysis of ship names"""
    __tablename__ = 'ship_analysis'
    __table_args__ = (
        db.Index('idx_ship_analysis_category', 'name_category'),
        db.Index('idx_ship_analysis_memorability', 'memorability_score'),
        db.Index('idx_ship_analysis_semantic', 'semantic_alignment_score'),
        db.Index('idx_ship_analysis_authority', 'authority_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    ship_id = db.Column(db.Integer, db.ForeignKey('ship.id'), nullable=False, unique=True)
    
    # Standard linguistic metrics (from NameAnalyzer)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    consonant_clusters = db.Column(db.Integer)
    memorability_score = db.Column(db.Float, index=True)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # Ship-specific name categorization
    name_category = db.Column(db.String(50), index=True)  # 'geographic', 'saint', 'monarch', 'virtue', 'mythological', 'animal', 'other'
    subcategory = db.Column(db.String(50))  # More specific categorization
    
    # Geographic name analysis
    is_geographic_name = db.Column(db.Boolean, default=False)
    geographic_specificity = db.Column(db.String(50))  # 'city', 'region', 'country', 'landmark', 'none'
    geographic_origin_name = db.Column(db.String(200))  # Name of the place
    geographic_cultural_importance = db.Column(db.Float)  # Cultural/historical importance of place (0-100)
    
    # Saint name analysis
    is_saint_name = db.Column(db.Boolean, default=False)
    saint_name = db.Column(db.String(200))  # Which saint
    saint_feast_day = db.Column(db.String(50))  # Religious calendar date
    saint_patronage = db.Column(db.String(200))  # What the saint is patron of
    
    # Other categorizations
    is_monarch_name = db.Column(db.Boolean, default=False)
    is_virtue_name = db.Column(db.Boolean, default=False)  # Victory, Endeavour, Enterprise, etc.
    is_mythological_name = db.Column(db.Boolean, default=False)
    is_animal_name = db.Column(db.Boolean, default=False)
    
    # Phonetic power analysis (for warships)
    authority_score = db.Column(db.Float, index=True)  # How authoritative/commanding (0-100)
    power_connotation_score = db.Column(db.Float)  # Aggressive vs gentle (-100 to +100)
    harshness_score = db.Column(db.Float)  # Phonetic harshness (plosives, fricatives)
    softness_score = db.Column(db.Float)  # Phonetic softness (liquids, glides)
    
    # Semantic analysis
    semantic_alignment_score = db.Column(db.Float, index=True)  # Does name align with achievements? (0-100)
    semantic_alignment_explanation = db.Column(db.Text)  # How name aligns with ship's history
    semantic_categories = db.Column(db.Text)  # JSON list of semantic associations
    
    # Prestige and sophistication
    prestige_score = db.Column(db.Float)  # Overall prestige of the name (0-100)
    intellectual_sophistication_score = db.Column(db.Float)  # Complexity/sophistication
    
    # Phonestheme analysis
    phonestheme_score = db.Column(db.Float)
    phonestheme_type = db.Column(db.String(50))
    vowel_brightness = db.Column(db.Float)
    vowel_emotion_profile = db.Column(db.String(50))
    consonant_hardness = db.Column(db.Float)
    
    # Phonemic features
    plosive_ratio = db.Column(db.Float)
    fricative_ratio = db.Column(db.Float)
    voicing_ratio = db.Column(db.Float)
    initial_is_plosive = db.Column(db.Boolean)
    
    # Advanced features (JSON storage)
    phonosemantic_data = db.Column(db.Text)  # JSON: detailed phonetic analysis
    semantic_data = db.Column(db.Text)  # JSON: semantic associations
    cultural_context_data = db.Column(db.Text)  # JSON: cultural/historical context
    nominative_determinism_data = db.Column(db.Text)  # JSON: specific name-outcome alignments
    
    # Analysis metadata
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'ship_id': self.ship_id,
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'word_count': self.word_count,
            'phonetic_score': self.phonetic_score,
            'vowel_ratio': self.vowel_ratio,
            'consonant_clusters': self.consonant_clusters,
            'memorability_score': self.memorability_score,
            'pronounceability_score': self.pronounceability_score,
            'uniqueness_score': self.uniqueness_score,
            'name_type': self.name_type,
            'name_category': self.name_category,
            'subcategory': self.subcategory,
            'is_geographic_name': self.is_geographic_name,
            'geographic_specificity': self.geographic_specificity,
            'geographic_origin_name': self.geographic_origin_name,
            'geographic_cultural_importance': self.geographic_cultural_importance,
            'is_saint_name': self.is_saint_name,
            'saint_name': self.saint_name,
            'is_monarch_name': self.is_monarch_name,
            'is_virtue_name': self.is_virtue_name,
            'is_mythological_name': self.is_mythological_name,
            'is_animal_name': self.is_animal_name,
            'authority_score': self.authority_score,
            'power_connotation_score': self.power_connotation_score,
            'harshness_score': self.harshness_score,
            'softness_score': self.softness_score,
            'semantic_alignment_score': self.semantic_alignment_score,
            'semantic_alignment_explanation': self.semantic_alignment_explanation,
            'prestige_score': self.prestige_score,
            'intellectual_sophistication_score': self.intellectual_sophistication_score,
            'phonestheme_score': self.phonestheme_score,
            'vowel_brightness': self.vowel_brightness,
            'consonant_hardness': self.consonant_hardness,
            'phonosemantic_data': json.loads(self.phonosemantic_data) if self.phonosemantic_data else {},
            'semantic_data': json.loads(self.semantic_data) if self.semantic_data else {},
            'cultural_context_data': json.loads(self.cultural_context_data) if self.cultural_context_data else {},
            'nominative_determinism_data': json.loads(self.nominative_determinism_data) if self.nominative_determinism_data else {}
        }


# =============================================================================
# IMMIGRATION SURNAME SEMANTIC ANALYSIS MODELS
# =============================================================================

class ImmigrantSurname(db.Model):
    """Core surname data for semantic meaning analysis"""
    __tablename__ = 'immigrant_surname'
    __table_args__ = (
        db.Index('idx_surname_origin', 'origin_country'),
        db.Index('idx_surname_semantic', 'semantic_category'),
        db.Index('idx_surname_toponymic', 'is_toponymic'),
        db.Index('idx_surname_name', 'surname'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(200), nullable=False, unique=True, index=True)
    
    # Origin classification
    origin_country = db.Column(db.String(100), index=True)  # Primary origin
    origin_language = db.Column(db.String(50))  # Original language
    alternative_origins = db.Column(db.Text)  # JSON list of possible origins
    
    # Semantic meaning classification
    semantic_category = db.Column(db.String(50), index=True, nullable=False)  # 'toponymic', 'occupational', 'descriptive', 'patronymic', 'religious', etc.
    semantic_subcategory = db.Column(db.String(50))  # More specific
    meaning_in_original = db.Column(db.String(500))  # What the name means
    is_toponymic = db.Column(db.Boolean, default=False, index=True)  # Has place/geographic meaning
    
    # Place reference (for toponymic surnames)
    place_name = db.Column(db.String(200))  # The actual place referenced (e.g., "Rome" for Romano)
    place_type = db.Column(db.String(50))  # 'city', 'region', 'country', 'landmark'
    place_country = db.Column(db.String(100))  # Country where place is located
    place_cultural_importance = db.Column(db.Float)  # Cultural significance of place (0-100)
    
    # Linguistic features (JSON)
    linguistic_features = db.Column(db.Text)  # JSON: etymology, morphology, etc.
    phonetic_signature = db.Column(db.String(200))  # Metaphone/Soundex signature
    
    # Phonetic analysis
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    
    # Historical frequency data
    earliest_us_census_year = db.Column(db.Integer)  # First appearance in US census
    total_bearers_historical = db.Column(db.Integer)  # Total people with surname historically
    total_bearers_current = db.Column(db.Integer)  # Current bearers (2020 census)
    frequency_rank = db.Column(db.Integer)  # Rank by frequency (1 = most common)
    
    # Classification metadata
    classifier_version = db.Column(db.String(20))  # Version of classification algorithm
    classification_date = db.Column(db.DateTime, default=datetime.utcnow)
    classification_confidence = db.Column(db.Float)  # Confidence in classification (0-100)
    
    # Data sources
    data_sources = db.Column(db.Text)  # JSON list of sources (etymology databases, etc.)
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    immigration_records = db.relationship('ImmigrationRecord', backref='surname_obj', lazy='dynamic', cascade='all, delete-orphan')
    settlement_patterns = db.relationship('SettlementPattern', backref='surname_obj', lazy='dynamic', cascade='all, delete-orphan')
    classification = db.relationship('SurnameClassification', backref='surname_obj', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'surname': self.surname,
            'origin_country': self.origin_country,
            'origin_language': self.origin_language,
            'alternative_origins': json.loads(self.alternative_origins) if self.alternative_origins else [],
            'semantic_category': self.semantic_category,
            'semantic_subcategory': self.semantic_subcategory,
            'meaning_in_original': self.meaning_in_original,
            'is_toponymic': self.is_toponymic,
            'place_name': self.place_name,
            'place_type': self.place_type,
            'place_country': self.place_country,
            'place_cultural_importance': self.place_cultural_importance,
            'linguistic_features': json.loads(self.linguistic_features) if self.linguistic_features else {},
            'phonetic_signature': self.phonetic_signature,
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'earliest_us_census_year': self.earliest_us_census_year,
            'total_bearers_historical': self.total_bearers_historical,
            'total_bearers_current': self.total_bearers_current,
            'frequency_rank': self.frequency_rank,
            'classification': self.classification.to_dict() if self.classification else None
        }


class ImmigrationRecord(db.Model):
    """Historical immigration data by surname and year"""
    __tablename__ = 'immigration_record'
    __table_args__ = (
        db.Index('idx_immigration_surname', 'surname_id'),
        db.Index('idx_immigration_year', 'year'),
        db.Index('idx_immigration_decade', 'decade'),
        db.Index('idx_immigration_origin', 'origin_country'),
        db.Index('idx_immigration_surname_year', 'surname_id', 'year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    surname_id = db.Column(db.Integer, db.ForeignKey('immigrant_surname.id'), nullable=False)
    
    # Temporal data
    year = db.Column(db.Integer, nullable=False, index=True)
    decade = db.Column(db.Integer, index=True)  # For aggregation (1880, 1890, etc.)
    immigration_wave = db.Column(db.String(50))  # 'first_wave', 'second_wave', 'modern'
    
    # Immigration counts
    immigrant_count = db.Column(db.Integer)  # Number of immigrants that year
    cumulative_count = db.Column(db.Integer)  # Running total
    
    # Origin data
    origin_country = db.Column(db.String(100), index=True)
    origin_port = db.Column(db.String(200))  # Departure port if available
    
    # Destination data
    entry_port = db.Column(db.String(200))  # US entry port (Ellis Island, Angel Island, etc.)
    initial_destination_state = db.Column(db.String(50))  # First settlement state
    
    # Demographics (where available)
    male_count = db.Column(db.Integer)
    female_count = db.Column(db.Integer)
    avg_age = db.Column(db.Float)
    
    # Data quality
    data_source = db.Column(db.String(200))  # Census, Ellis Island, INS, etc.
    data_quality_score = db.Column(db.Float)  # 0-100, confidence in data
    is_estimated = db.Column(db.Boolean, default=False)  # True if interpolated/estimated
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'surname': self.surname_obj.surname if self.surname_obj else None,
            'year': self.year,
            'decade': self.decade,
            'immigration_wave': self.immigration_wave,
            'immigrant_count': self.immigrant_count,
            'cumulative_count': self.cumulative_count,
            'origin_country': self.origin_country,
            'entry_port': self.entry_port,
            'initial_destination_state': self.initial_destination_state,
            'data_source': self.data_source,
            'data_quality_score': self.data_quality_score
        }


class SettlementPattern(db.Model):
    """Geographic distribution and settlement patterns of surnames over time"""
    __tablename__ = 'settlement_pattern'
    __table_args__ = (
        db.Index('idx_settlement_surname', 'surname_id'),
        db.Index('idx_settlement_state', 'state'),
        db.Index('idx_settlement_year', 'year'),
        db.Index('idx_settlement_concentration', 'concentration_index'),
        db.Index('idx_settlement_surname_state_year', 'surname_id', 'state', 'year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    surname_id = db.Column(db.Integer, db.ForeignKey('immigrant_surname.id'), nullable=False)
    
    # Geographic location
    state = db.Column(db.String(50), nullable=False, index=True)
    county = db.Column(db.String(100))  # More specific location
    city = db.Column(db.String(100))  # Even more specific if available
    
    # Temporal
    year = db.Column(db.Integer, nullable=False, index=True)
    decade = db.Column(db.Integer, index=True)
    generation = db.Column(db.Integer)  # 1st, 2nd, 3rd generation estimate
    
    # Population counts
    population_count = db.Column(db.Integer)  # People with surname in this location
    total_population = db.Column(db.Integer)  # Total population of location
    percentage_of_total = db.Column(db.Float)  # Percentage of local population
    
    # Concentration metrics
    concentration_index = db.Column(db.Float, index=True)  # Local concentration (0-100)
    relative_concentration = db.Column(db.Float)  # Compared to national average
    
    # Geographic clustering
    distance_from_entry_port = db.Column(db.Float)  # Miles from primary entry port
    nearest_entry_port = db.Column(db.String(100))  # NYC, SF, Miami, etc.
    is_ethnic_enclave = db.Column(db.Boolean, default=False)  # High concentration area
    
    # Dispersion metrics (assimilation proxy)
    dispersion_score = db.Column(db.Float)  # 0-100, higher = more dispersed
    years_since_arrival = db.Column(db.Integer)  # Time since first immigration
    
    # Economic indicators (where available)
    median_income = db.Column(db.Float)
    homeownership_rate = db.Column(db.Float)
    
    # Data sources
    data_source = db.Column(db.String(200))  # Census, survey data, etc.
    data_quality_score = db.Column(db.Float)
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'surname': self.surname_obj.surname if self.surname_obj else None,
            'state': self.state,
            'county': self.county,
            'city': self.city,
            'year': self.year,
            'decade': self.decade,
            'generation': self.generation,
            'population_count': self.population_count,
            'percentage_of_total': self.percentage_of_total,
            'concentration_index': self.concentration_index,
            'relative_concentration': self.relative_concentration,
            'distance_from_entry_port': self.distance_from_entry_port,
            'nearest_entry_port': self.nearest_entry_port,
            'is_ethnic_enclave': self.is_ethnic_enclave,
            'dispersion_score': self.dispersion_score,
            'years_since_arrival': self.years_since_arrival
        }


class SurnameClassification(db.Model):
    """Detailed classification results for surname semantic meaning"""
    __tablename__ = 'surname_classification'
    __table_args__ = (
        db.Index('idx_classification_surname', 'surname_id'),
        db.Index('idx_classification_toponymic', 'is_toponymic'),
        db.Index('idx_classification_category', 'semantic_category'),
        db.Index('idx_classification_confidence', 'confidence_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    surname_id = db.Column(db.Integer, db.ForeignKey('immigrant_surname.id'), nullable=False, unique=True)
    
    # Primary classification
    is_toponymic = db.Column(db.Boolean, nullable=False, index=True)  # Has place/geographic meaning
    semantic_category = db.Column(db.String(50), index=True)  # 'toponymic', 'occupational', 'descriptive', 'patronymic', 'religious'
    confidence_score = db.Column(db.Float, index=True)  # 0-100
    
    # Etymology analysis
    etymology_features = db.Column(db.Text)  # JSON: specific etymological features
    meaning_analysis = db.Column(db.Text)  # JSON: semantic meaning breakdown
    
    # Classification evidence
    etymology_sources = db.Column(db.Text)  # JSON: sources confirming etymology
    linguistic_evidence = db.Column(db.Text)  # JSON: linguistic markers
    
    # For toponymic surnames
    place_specificity = db.Column(db.String(50))  # 'city', 'region', 'country', 'landmark', 'n/a'
    place_importance = db.Column(db.Float)  # Cultural/historical importance (0-100)
    
    # Linguistic analysis
    morphological_analysis = db.Column(db.Text)  # JSON: word formation analysis
    semantic_components = db.Column(db.Text)  # JSON: meaning components
    
    # Etymology database matches
    database_matches = db.Column(db.Text)  # JSON: matches from etymology databases
    database_confidence = db.Column(db.Float)  # 0-100
    
    # Additional semantic categories found
    alternative_meanings = db.Column(db.Text)  # JSON: other possible meanings
    meaning_ambiguity_score = db.Column(db.Float)  # How ambiguous the meaning is (0-100)
    
    # Classification metadata
    classifier_version = db.Column(db.String(20))
    classification_method = db.Column(db.String(100))  # 'hybrid', 'database', 'algorithmic'
    classification_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Manual review (if applicable)
    manually_reviewed = db.Column(db.Boolean, default=False)
    reviewer_notes = db.Column(db.Text)
    
    # Alternative classifications
    alternative_classifications = db.Column(db.Text)  # JSON: other possible classifications
    
    # Metadata
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'surname': self.surname_obj.surname if self.surname_obj else None,
            'is_toponymic': self.is_toponymic,
            'semantic_category': self.semantic_category,
            'confidence_score': self.confidence_score,
            'etymology_features': json.loads(self.etymology_features) if self.etymology_features else {},
            'meaning_analysis': json.loads(self.meaning_analysis) if self.meaning_analysis else {},
            'place_specificity': self.place_specificity,
            'place_importance': self.place_importance,
            'morphological_analysis': json.loads(self.morphological_analysis) if self.morphological_analysis else {},
            'semantic_components': json.loads(self.semantic_components) if self.semantic_components else {},
            'database_matches': json.loads(self.database_matches) if self.database_matches else [],
            'database_confidence': self.database_confidence,
            'alternative_meanings': json.loads(self.alternative_meanings) if self.alternative_meanings else [],
            'meaning_ambiguity_score': self.meaning_ambiguity_score,
            'classifier_version': self.classifier_version,
            'classification_method': self.classification_method
        }


# =============================================================================
# ELECTION LINGUISTICS ANALYSIS
# =============================================================================

class ElectionCandidate(db.Model):
    """Election candidate data for nominative determinism in democratic outcomes"""
    __tablename__ = 'election_candidate'
    __table_args__ = (
        db.Index('idx_election_position_year', 'position', 'election_year'),
        db.Index('idx_election_state', 'state'),
        db.Index('idx_election_party', 'party'),
        db.Index('idx_election_outcome', 'won_election'),
        db.Index('idx_election_vote_share', 'vote_share_percent'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Name information
    full_name = db.Column(db.String(300), nullable=False, index=True)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), index=True)
    ballot_name = db.Column(db.String(300))  # As it appears on ballot
    nickname = db.Column(db.String(100))  # Common nickname used in campaign
    
    # Position and election details
    position = db.Column(db.String(100), nullable=False, index=True)  # 'President', 'Senate', 'House', 'Governor', etc.
    position_level = db.Column(db.String(20), index=True)  # 'federal', 'state', 'local'
    position_type = db.Column(db.String(50))  # 'executive', 'legislative', 'judicial'
    election_year = db.Column(db.Integer, nullable=False, index=True)
    election_date = db.Column(db.Date)
    election_type = db.Column(db.String(30))  # 'general', 'primary', 'runoff', 'special'
    
    # Geographic location
    state = db.Column(db.String(50), index=True)
    district = db.Column(db.String(50))  # Congressional district, state senate district, etc.
    city = db.Column(db.String(100))  # For local elections
    
    # Party and political details
    party = db.Column(db.String(50), index=True)  # 'Democratic', 'Republican', 'Independent', etc.
    party_simplified = db.Column(db.String(20))  # 'D', 'R', 'I', 'O' for analysis
    incumbent = db.Column(db.Boolean, default=False, index=True)
    prior_office = db.Column(db.String(200))  # Previous offices held
    years_in_politics = db.Column(db.Integer)
    
    # Election outcome
    won_election = db.Column(db.Boolean, index=True)
    vote_count = db.Column(db.Integer)
    vote_share_percent = db.Column(db.Float)  # Percentage of votes received
    margin_of_victory = db.Column(db.Float)  # Percentage point margin (positive if won)
    total_votes_cast = db.Column(db.Integer)  # Total votes in race
    
    # Competitiveness metrics
    district_pvi = db.Column(db.Float)  # Cook PVI or partisan lean score
    race_competitiveness = db.Column(db.String(30))  # 'safe', 'likely', 'lean', 'toss-up'
    number_of_candidates = db.Column(db.Integer)  # Total candidates in race
    
    # Campaign metrics
    campaign_spending = db.Column(db.Float)  # Total spending in dollars
    opponent_spending = db.Column(db.Float)  # Top opponent's spending
    spending_ratio = db.Column(db.Float)  # Candidate spending / opponent spending
    
    # Running mate information (for President/VP, Governor/Lt. Gov)
    has_running_mate = db.Column(db.Boolean, default=False)
    running_mate_id = db.Column(db.Integer, db.ForeignKey('election_candidate.id'))
    running_mate = db.relationship('ElectionCandidate', remote_side=[id], backref='ticket_leader', foreign_keys=[running_mate_id])
    
    # Ballot structure reference
    ballot_id = db.Column(db.Integer, db.ForeignKey('ballot_structure.id'))
    ballot_position = db.Column(db.Integer)  # Position on ballot (for alphabetical effects)
    
    # National/state political environment
    presidential_approval = db.Column(db.Float)  # If available for that year
    generic_ballot = db.Column(db.Float)  # Generic ballot polling for that party
    wave_year = db.Column(db.String(10))  # 'R_wave', 'D_wave', 'neutral'
    
    # Data sources and metadata
    data_source = db.Column(db.String(200))  # 'MIT_Election_Lab', 'FEC', 'Ballotpedia', etc.
    data_quality = db.Column(db.String(20))  # 'complete', 'partial', 'limited'
    notes = db.Column(db.Text)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    linguistic_analysis = db.relationship('ElectionCandidateAnalysis', backref='candidate', uselist=False, cascade='all, delete-orphan')
    tickets = db.relationship('RunningMateTicket', foreign_keys='RunningMateTicket.primary_candidate_id', backref='primary', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'ballot_name': self.ballot_name,
            'position': self.position,
            'position_level': self.position_level,
            'election_year': self.election_year,
            'election_type': self.election_type,
            'state': self.state,
            'district': self.district,
            'party': self.party,
            'incumbent': self.incumbent,
            'won_election': self.won_election,
            'vote_share_percent': self.vote_share_percent,
            'margin_of_victory': self.margin_of_victory,
            'campaign_spending': self.campaign_spending,
            'number_of_candidates': self.number_of_candidates,
            'race_competitiveness': self.race_competitiveness,
            'linguistic_analysis': self.linguistic_analysis.to_dict() if self.linguistic_analysis else None
        }


class RunningMateTicket(db.Model):
    """Presidential/VP or Governor/Lt. Gov ticket pairings for phonetic harmony analysis"""
    __tablename__ = 'running_mate_ticket'
    __table_args__ = (
        db.Index('idx_ticket_year_position', 'election_year', 'position_type'),
        db.Index('idx_ticket_won', 'won_election'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ticket details
    primary_candidate_id = db.Column(db.Integer, db.ForeignKey('election_candidate.id'), nullable=False)
    running_mate_candidate_id = db.Column(db.Integer, db.ForeignKey('election_candidate.id'), nullable=False)
    
    # Election details
    position_type = db.Column(db.String(50))  # 'Presidential', 'Gubernatorial'
    election_year = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(50))  # For gubernatorial races
    party = db.Column(db.String(50))
    
    # Outcome
    won_election = db.Column(db.Boolean, index=True)
    vote_share_percent = db.Column(db.Float)
    
    # Phonetic harmony metrics (computed)
    syllable_pattern_match = db.Column(db.Float)  # 0-100, how well syllable counts match
    vowel_harmony_score = db.Column(db.Float)  # 0-100, vowel pattern compatibility
    rhythm_compatibility = db.Column(db.Float)  # 0-100, overall phonetic rhythm match
    combined_memorability = db.Column(db.Float)  # Average memorability of both names
    combined_pronounceability = db.Column(db.Float)  # Average pronounceability
    name_length_similarity = db.Column(db.Float)  # How similar name lengths are
    
    # Phonetic analysis details (JSON)
    phonetic_analysis = db.Column(db.Text)  # Detailed phonetic breakdown
    harmony_components = db.Column(db.Text)  # JSON: specific harmony elements
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    primary_cand = db.relationship('ElectionCandidate', foreign_keys=[primary_candidate_id], backref='ticket_as_primary')
    running_mate_cand = db.relationship('ElectionCandidate', foreign_keys=[running_mate_candidate_id], backref='ticket_as_mate')
    
    def to_dict(self):
        return {
            'id': self.id,
            'primary_candidate': self.primary_cand.full_name if self.primary_cand else None,
            'running_mate': self.running_mate_cand.full_name if self.running_mate_cand else None,
            'position_type': self.position_type,
            'election_year': self.election_year,
            'state': self.state,
            'party': self.party,
            'won_election': self.won_election,
            'vote_share_percent': self.vote_share_percent,
            'syllable_pattern_match': self.syllable_pattern_match,
            'vowel_harmony_score': self.vowel_harmony_score,
            'rhythm_compatibility': self.rhythm_compatibility,
            'combined_memorability': self.combined_memorability,
            'phonetic_analysis': json.loads(self.phonetic_analysis) if self.phonetic_analysis else {}
        }


class BallotStructure(db.Model):
    """Full ballot structure for analyzing phonetic clustering among candidates"""
    __tablename__ = 'ballot_structure'
    __table_args__ = (
        db.Index('idx_ballot_election', 'election_year', 'position', 'state'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ballot identification
    position = db.Column(db.String(100), nullable=False)  # The office being contested
    election_year = db.Column(db.Integer, nullable=False)
    election_type = db.Column(db.String(30))  # 'general', 'primary'
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    
    # Ballot details
    total_candidates = db.Column(db.Integer)
    ballot_format = db.Column(db.String(50))  # 'alphabetical', 'random', 'party_grouped', etc.
    primary_party = db.Column(db.String(50))  # For primary elections
    
    # Phonetic clustering metrics (computed across all candidates)
    avg_name_similarity = db.Column(db.Float)  # Average pairwise phonetic similarity
    max_name_similarity = db.Column(db.Float)  # Highest pairwise similarity
    clustering_coefficient = db.Column(db.Float)  # Overall phonetic clustering
    
    # Similarity analysis (JSON)
    similarity_matrix = db.Column(db.Text)  # JSON: pairwise similarity scores
    clustering_analysis = db.Column(db.Text)  # JSON: detailed clustering metrics
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    candidates = db.relationship('ElectionCandidate', backref='ballot', foreign_keys='ElectionCandidate.ballot_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position,
            'election_year': self.election_year,
            'election_type': self.election_type,
            'state': self.state,
            'district': self.district,
            'total_candidates': self.total_candidates,
            'ballot_format': self.ballot_format,
            'avg_name_similarity': self.avg_name_similarity,
            'max_name_similarity': self.max_name_similarity,
            'clustering_coefficient': self.clustering_coefficient,
            'candidates': [c.to_dict() for c in self.candidates] if self.candidates else [],
            'similarity_matrix': json.loads(self.similarity_matrix) if self.similarity_matrix else {}
        }


class ElectionCandidateAnalysis(db.Model):
    """Comprehensive linguistic analysis of candidate names"""
    __tablename__ = 'election_candidate_analysis'
    __table_args__ = (
        db.Index('idx_election_analysis_memorability', 'memorability_score'),
        db.Index('idx_election_analysis_syllables', 'syllable_count'),
        db.Index('idx_election_analysis_title_euphony', 'title_euphony_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('election_candidate.id'), nullable=False, unique=True)
    
    # Basic metrics
    syllable_count = db.Column(db.Integer)  # Full name syllables
    first_name_syllables = db.Column(db.Integer)
    last_name_syllables = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)  # Number of name parts
    
    # Phonetic analysis
    phonetic_score = db.Column(db.Float)  # Overall euphony
    vowel_ratio = db.Column(db.Float)  # Vowels / total letters
    consonant_clusters = db.Column(db.Integer)  # Number of consonant clusters
    
    # Memorability and pronounceability
    memorability_score = db.Column(db.Float)  # 0-100
    pronounceability_score = db.Column(db.Float)  # 0-100
    uniqueness_score = db.Column(db.Float)  # How distinctive the name is
    
    # Sound characteristics
    harshness_score = db.Column(db.Float)  # Plosives and harsh sounds
    softness_score = db.Column(db.Float)  # Soft, flowing sounds
    power_connotation_score = db.Column(db.Float)  # Authority/power associations
    trustworthiness_score = db.Column(db.Float)  # Trust-inducing phonetic qualities
    
    # Name structure
    has_middle_name = db.Column(db.Boolean, default=False)
    has_nickname = db.Column(db.Boolean, default=False)
    alliteration_score = db.Column(db.Float)  # First/last name alliteration
    rhythm_score = db.Column(db.Float)  # Overall rhythmic quality
    
    # Position title euphony (KEY METRIC)
    title_euphony_score = db.Column(db.Float)  # How well "Senator Smith" flows
    title_name_consonance = db.Column(db.Float)  # Phonetic compatibility of title + name
    title_name_analysis = db.Column(db.Text)  # JSON: detailed title + name analysis
    
    # Similarity to other names
    similarity_to_famous = db.Column(db.Float)  # Similarity to famous political names
    closest_famous_name = db.Column(db.String(200))
    
    # Alphabetical position effects
    alphabetical_advantage = db.Column(db.Float)  # A-M vs N-Z
    first_letter = db.Column(db.String(1))
    
    # Ethnic/cultural name analysis
    name_ethnicity = db.Column(db.String(100))  # Perceived ethnicity/origin
    name_cultural_markers = db.Column(db.Text)  # JSON: cultural associations
    
    # Advanced phonetic features (JSON storage)
    phoneme_breakdown = db.Column(db.Text)  # JSON: individual phonemes
    stress_pattern = db.Column(db.Text)  # JSON: syllable stress pattern
    sound_symbolism = db.Column(db.Text)  # JSON: sound-meaning associations
    
    # Comparative metrics
    percentile_memorability = db.Column(db.Float)  # Percentile among all candidates
    percentile_pronounceability = db.Column(db.Float)
    percentile_title_euphony = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'candidate_id': self.candidate_id,
            'syllable_count': self.syllable_count,
            'first_name_syllables': self.first_name_syllables,
            'last_name_syllables': self.last_name_syllables,
            'character_length': self.character_length,
            'phonetic_score': self.phonetic_score,
            'memorability_score': self.memorability_score,
            'pronounceability_score': self.pronounceability_score,
            'uniqueness_score': self.uniqueness_score,
            'harshness_score': self.harshness_score,
            'softness_score': self.softness_score,
            'power_connotation_score': self.power_connotation_score,
            'trustworthiness_score': self.trustworthiness_score,
            'has_middle_name': self.has_middle_name,
            'alliteration_score': self.alliteration_score,
            'rhythm_score': self.rhythm_score,
            'title_euphony_score': self.title_euphony_score,
            'title_name_consonance': self.title_name_consonance,
            'title_name_analysis': json.loads(self.title_name_analysis) if self.title_name_analysis else {},
            'similarity_to_famous': self.similarity_to_famous,
            'closest_famous_name': self.closest_famous_name,
            'alphabetical_advantage': self.alphabetical_advantage,
            'first_letter': self.first_letter,
            'name_ethnicity': self.name_ethnicity,
            'percentile_memorability': self.percentile_memorability,
            'percentile_pronounceability': self.percentile_pronounceability,
            'percentile_title_euphony': self.percentile_title_euphony,
            'phoneme_breakdown': json.loads(self.phoneme_breakdown) if self.phoneme_breakdown else {},
            'stress_pattern': json.loads(self.stress_pattern) if self.stress_pattern else {},
            'sound_symbolism': json.loads(self.sound_symbolism) if self.sound_symbolism else {}
        }


# =============================================================================
# BOARD GAME MODELS
# =============================================================================

class BoardGame(db.Model):
    """Board game entity with BGG data"""
    __tablename__ = 'board_games'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    bgg_id = db.Column(db.Integer, unique=True, index=True)
    year_published = db.Column(db.Integer, index=True)
    
    # Ratings & Metrics
    bgg_rating = db.Column(db.Float)  # BGG weighted rating
    average_rating = db.Column(db.Float)
    num_ratings = db.Column(db.Integer)
    complexity_weight = db.Column(db.Float)  # 1-5 scale
    ownership_count = db.Column(db.Integer)
    
    # Game Characteristics
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    playing_time = db.Column(db.Integer)  # minutes
    min_age = db.Column(db.Integer)
    
    # Classification
    category = db.Column(db.String(100), index=True)  # strategy, party, family, etc.
    primary_mechanic = db.Column(db.String(100))
    designer = db.Column(db.String(255))
    designer_nationality = db.Column(db.String(50), index=True)  # US, DE, JP, etc.
    publisher = db.Column(db.String(255))
    
    # Rankings
    bgg_rank = db.Column(db.Integer)  # Overall BGG rank
    category_rank = db.Column(db.Integer)  # Rank within category
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = db.relationship('BoardGameAnalysis', backref='game', 
                              lazy=True, uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BoardGame {self.name} ({self.year_published})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bgg_id': self.bgg_id,
            'year_published': self.year_published,
            'bgg_rating': self.bgg_rating,
            'average_rating': self.average_rating,
            'num_ratings': self.num_ratings,
            'complexity_weight': self.complexity_weight,
            'ownership_count': self.ownership_count,
            'min_players': self.min_players,
            'max_players': self.max_players,
            'playing_time': self.playing_time,
            'min_age': self.min_age,
            'category': self.category,
            'primary_mechanic': self.primary_mechanic,
            'designer': self.designer,
            'designer_nationality': self.designer_nationality,
            'publisher': self.publisher,
            'bgg_rank': self.bgg_rank,
            'category_rank': self.category_rank
        }


class BoardGameAnalysis(db.Model):
    """Phonetic and linguistic analysis of board game names"""
    __tablename__ = 'board_game_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('board_games.id'), nullable=False, unique=True)
    
    # Name Structure
    word_count = db.Column(db.Integer)
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    contains_colon = db.Column(db.Boolean)  # Base game vs expansion pattern
    contains_number = db.Column(db.Boolean)
    contains_article = db.Column(db.Boolean)  # "The", "A", etc.
    
    # Phonetic Features (standard suite)
    harshness_score = db.Column(db.Float)
    smoothness_score = db.Column(db.Float)
    plosive_ratio = db.Column(db.Float)
    fricative_ratio = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    consonant_cluster_density = db.Column(db.Float)
    
    # Advanced Phonetic
    phonetic_complexity = db.Column(db.Float)
    sound_symbolism_score = db.Column(db.Float)
    alliteration_score = db.Column(db.Float)
    
    # Semantic Features
    name_type = db.Column(db.String(50))  # descriptive, abstract, thematic, compound, portmanteau
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    semantic_transparency = db.Column(db.Float)  # How clear is the theme from name?
    
    # Cultural/Linguistic
    is_fantasy_name = db.Column(db.Boolean)  # Made-up words (Carcassonne, Splendor)
    is_latin_derived = db.Column(db.Boolean)
    is_compound_word = db.Column(db.Boolean)
    primary_language = db.Column(db.String(20))  # en, de, fr, jp, etc.
    
    # Classification Clusters
    phonetic_cluster = db.Column(db.Integer)
    semantic_cluster = db.Column(db.Integer)
    combined_cluster = db.Column(db.Integer)
    
    # Composite Scores
    name_quality_score = db.Column(db.Float)  # Overall name effectiveness
    cultural_alignment_score = db.Column(db.Float)  # Match to tradition
    thematic_resonance = db.Column(db.Float)  # Name-game theme alignment
    
    # Era Classification
    era = db.Column(db.String(50))  # classic, golden, modern, contemporary
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BoardGameAnalysis for game_id={self.game_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'word_count': self.word_count,
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'contains_colon': self.contains_colon,
            'contains_number': self.contains_number,
            'contains_article': self.contains_article,
            'harshness_score': self.harshness_score,
            'smoothness_score': self.smoothness_score,
            'plosive_ratio': self.plosive_ratio,
            'fricative_ratio': self.fricative_ratio,
            'vowel_ratio': self.vowel_ratio,
            'consonant_cluster_density': self.consonant_cluster_density,
            'phonetic_complexity': self.phonetic_complexity,
            'sound_symbolism_score': self.sound_symbolism_score,
            'alliteration_score': self.alliteration_score,
            'name_type': self.name_type,
            'memorability_score': self.memorability_score,
            'pronounceability_score': self.pronounceability_score,
            'semantic_transparency': self.semantic_transparency,
            'is_fantasy_name': self.is_fantasy_name,
            'is_latin_derived': self.is_latin_derived,
            'is_compound_word': self.is_compound_word,
            'primary_language': self.primary_language,
            'phonetic_cluster': self.phonetic_cluster,
            'semantic_cluster': self.semantic_cluster,
            'combined_cluster': self.combined_cluster,
            'name_quality_score': self.name_quality_score,
            'cultural_alignment_score': self.cultural_alignment_score,
            'thematic_resonance': self.thematic_resonance,
            'era': self.era
        }


# =============================================================================
# MLB PLAYER MODELS
# =============================================================================

class MLBPlayer(db.Model):
    """MLB player data from Baseball Reference"""
    __tablename__ = 'mlb_players'
    __table_args__ = (
        db.Index('idx_mlb_debut_year', 'debut_year'),
        db.Index('idx_mlb_position', 'position'),
        db.Index('idx_mlb_position_group', 'position_group'),
        db.Index('idx_mlb_era_group', 'era_group'),
    )
    
    id = db.Column(db.String(100), primary_key=True)  # Baseball Reference player ID
    name = db.Column(db.String(200), nullable=False, index=True)
    full_name = db.Column(db.String(300))
    
    # Position
    position = db.Column(db.String(10), index=True)  # P, C, 1B, 2B, 3B, SS, LF, CF, RF, DH
    position_group = db.Column(db.String(20), index=True)  # Pitcher, Catcher, Infield, Outfield, DH
    pitcher_role = db.Column(db.String(20))  # SP (starter), RP (reliever), CL (closer)
    
    # Team assignment (for roster amalgamation analysis)
    team_id = db.Column(db.String(10), db.ForeignKey('mlb_teams.id'), index=True)  # Current team
    
    # Career
    debut_year = db.Column(db.Integer, index=True)
    final_year = db.Column(db.Integer)
    years_active = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=False)
    
    # Era classification
    era_group = db.Column(db.String(30))  # classic (1950-1979), modern (1980-1999), contemporary (2000-2024)
    
    # Batting Stats (for position players)
    games_played = db.Column(db.Integer)
    at_bats = db.Column(db.Integer)
    batting_average = db.Column(db.Float)
    home_runs = db.Column(db.Integer, index=True)  # Indexed for power analysis
    rbis = db.Column(db.Integer)
    stolen_bases = db.Column(db.Integer)
    ops = db.Column(db.Float)  # On-base plus slugging
    slugging_percentage = db.Column(db.Float)
    on_base_percentage = db.Column(db.Float)
    
    # Pitching Stats (for pitchers)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    era = db.Column(db.Float)  # Earned run average
    strikeouts = db.Column(db.Integer)
    saves = db.Column(db.Integer)
    innings_pitched = db.Column(db.Float)
    whip = db.Column(db.Float)  # Walks + hits per inning
    games_started = db.Column(db.Integer)
    complete_games = db.Column(db.Integer)
    
    # Achievements
    all_star_count = db.Column(db.Integer)
    mvp_awards = db.Column(db.Integer)
    cy_young_awards = db.Column(db.Integer)
    gold_gloves = db.Column(db.Integer)
    silver_sluggers = db.Column(db.Integer)
    hof_inducted = db.Column(db.Boolean, default=False)
    
    # Demographics
    birth_country = db.Column(db.String(50), index=True)
    birth_state = db.Column(db.String(50))
    ethnicity = db.Column(db.String(50))  # For internationalization analysis
    
    # Composite scores
    performance_score = db.Column(db.Float)
    career_achievement_score = db.Column(db.Float)
    power_score = db.Column(db.Float)  # For power hitters
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = db.relationship('MLBPlayerAnalysis', backref='player',
                              lazy=True, uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MLBPlayer {self.name} ({self.position})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'position_group': self.position_group,
            'pitcher_role': self.pitcher_role,
            'debut_year': self.debut_year,
            'years_active': self.years_active,
            'era_group': self.era_group,
            'batting_average': self.batting_average,
            'home_runs': self.home_runs,
            'era': self.era,
            'strikeouts': self.strikeouts,
            'all_star_count': self.all_star_count,
            'hof_inducted': self.hof_inducted,
            'birth_country': self.birth_country
        }


class MLBPlayerAnalysis(db.Model):
    """Phonetic and linguistic analysis of MLB player names"""
    __tablename__ = 'mlb_player_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(100), db.ForeignKey('mlb_players.id'), nullable=False, unique=True)
    
    # Name structure
    syllable_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    first_name_syllables = db.Column(db.Integer)
    last_name_syllables = db.Column(db.Integer)
    first_name_length = db.Column(db.Integer)
    last_name_length = db.Column(db.Integer)
    
    # Phonetic features (standard suite)
    harshness_score = db.Column(db.Float)
    smoothness_score = db.Column(db.Float)
    power_connotation_score = db.Column(db.Float)  # For power hitter analysis
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    phonetic_complexity = db.Column(db.Float)
    
    # Advanced phonetic
    plosive_ratio = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    consonant_cluster_density = db.Column(db.Float)
    alliteration_score = db.Column(db.Float)
    
    # Name origin classification
    name_origin = db.Column(db.String(50))  # Anglo, Latino, Asian, European, African
    is_nickname = db.Column(db.Boolean)
    has_accent = db.Column(db.Boolean)  # Accented characters (José, Ramón)
    
    # Position-specific scores
    pitcher_name_score = db.Column(db.Float)  # Complexity/professionalism
    power_name_score = db.Column(db.Float)  # Harshness for sluggers
    speed_name_score = db.Column(db.Float)  # For base stealers
    
    # Clusters
    position_cluster = db.Column(db.Integer)
    phonetic_cluster = db.Column(db.Integer)
    temporal_cohort = db.Column(db.String(30))  # Era-based naming cohort
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MLBPlayerAnalysis for player_id={self.player_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'syllable_count': self.syllable_count,
            'word_count': self.word_count,
            'harshness_score': self.harshness_score,
            'power_connotation_score': self.power_connotation_score,
            'memorability_score': self.memorability_score,
            'name_origin': self.name_origin,
            'position_cluster': self.position_cluster
        }


# =============================================================================
# MLB TEAM MODELS (Team-Level Analysis with Roster Amalgamation)
# =============================================================================

class MLBTeam(db.Model):
    """MLB team entity with historical data and performance metrics"""
    __tablename__ = 'mlb_teams'
    __table_args__ = (
        db.Index('idx_mlb_team_win_pct', 'win_percentage'),
        db.Index('idx_mlb_team_city', 'city'),
        db.Index('idx_mlb_team_ws_titles', 'world_series_titles'),
    )
    
    id = db.Column(db.String(10), primary_key=True)  # Team abbreviation (NYY, BOS, LAD, etc.)
    name = db.Column(db.String(100), nullable=False)  # Team name (Yankees, Red Sox, Dodgers)
    full_name = db.Column(db.String(150))  # New York Yankees
    city = db.Column(db.String(100), nullable=False, index=True)  # New York, Boston, Los Angeles
    state = db.Column(db.String(50))
    
    # League structure
    league = db.Column(db.String(10))  # AL, NL
    division = db.Column(db.String(20))  # AL East, NL West, etc.
    
    # Historical data
    founded_year = db.Column(db.Integer)
    franchise_relocations = db.Column(db.Text)  # JSON of relocations
    name_changes = db.Column(db.Text)  # JSON of name changes
    previous_names = db.Column(db.Text)  # JSON array of historical names
    
    # Performance metrics (current/recent)
    wins_season = db.Column(db.Integer)
    losses_season = db.Column(db.Integer)
    win_percentage = db.Column(db.Float, index=True)
    runs_scored = db.Column(db.Integer)
    runs_allowed = db.Column(db.Integer)
    
    # Historical success
    playoff_appearances = db.Column(db.Integer)
    division_titles = db.Column(db.Integer)
    pennants = db.Column(db.Integer)
    world_series_titles = db.Column(db.Integer, index=True)
    
    # Stadium
    stadium_name = db.Column(db.String(150))
    stadium_capacity = db.Column(db.Integer)
    
    # Market
    market_size_rank = db.Column(db.Integer)  # 1-30 by metro population
    payroll = db.Column(db.Integer)  # For confound control
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = db.relationship('MLBTeamAnalysis', backref='team',
                              lazy=True, uselist=False, cascade='all, delete-orphan')
    home_matchups = db.relationship('MLBMatchup', foreign_keys='MLBMatchup.home_team_id',
                                   backref='home_team', lazy='dynamic')
    away_matchups = db.relationship('MLBMatchup', foreign_keys='MLBMatchup.away_team_id',
                                   backref='away_team', lazy='dynamic')
    
    def __repr__(self):
        return f'<MLBTeam {self.full_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.full_name,
            'city': self.city,
            'league': self.league,
            'division': self.division,
            'wins': self.wins_season,
            'losses': self.losses_season,
            'win_percentage': self.win_percentage,
            'world_series_titles': self.world_series_titles,
            'playoff_appearances': self.playoff_appearances
        }


class MLBTeamAnalysis(db.Model):
    """3-Layer linguistic analysis: Team Name + City Name + Roster Amalgamation"""
    __tablename__ = 'mlb_team_analyses'
    __table_args__ = (
        db.Index('idx_mlb_team_analysis_composite', 'composite_linguistic_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(10), db.ForeignKey('mlb_teams.id'), nullable=False, unique=True)
    
    # ===========================================================================
    # LAYER 1: Team Name Analysis
    # ===========================================================================
    team_name_syllables = db.Column(db.Integer)
    team_name_character_length = db.Column(db.Integer)
    team_name_memorability = db.Column(db.Float)
    team_name_power_score = db.Column(db.Float)
    team_name_prestige = db.Column(db.Float)
    team_name_harshness = db.Column(db.Float)
    team_name_type = db.Column(db.String(50))  # Animal, Color, Historical, Regional, Occupation, etc.
    team_name_semantic_category = db.Column(db.String(50))  # For typology
    
    # ===========================================================================
    # LAYER 2: City Name Analysis
    # ===========================================================================
    city_syllables = db.Column(db.Integer)
    city_character_length = db.Column(db.Integer)
    city_prestige_score = db.Column(db.Float, index=True)  # NYC, LA, Boston = high; TB, Oak = low
    city_memorability = db.Column(db.Float)
    city_phonetic_authority = db.Column(db.Float)
    city_vowel_ratio = db.Column(db.Float)
    city_market_tier = db.Column(db.String(20))  # Major, Mid, Small
    
    # ===========================================================================
    # LAYER 3: Roster Amalgamation (Aggregate of all 25 players' names)
    # ===========================================================================
    roster_size = db.Column(db.Integer)  # Number of players analyzed
    roster_mean_syllables = db.Column(db.Float)
    roster_mean_harshness = db.Column(db.Float)
    roster_mean_memorability = db.Column(db.Float)
    roster_mean_power_score = db.Column(db.Float)
    
    # Roster diversity/harmony
    roster_syllable_stddev = db.Column(db.Float)  # Diversity measure
    roster_harmony_score = db.Column(db.Float)  # Low stddev = high harmony
    roster_phonetic_diversity = db.Column(db.Float)  # Range of phonetic features
    
    # Roster composition
    roster_international_percentage = db.Column(db.Float)  # % Latino/Asian names
    roster_anglo_percentage = db.Column(db.Float)
    roster_latino_percentage = db.Column(db.Float)
    roster_asian_percentage = db.Column(db.Float)
    
    # Roster extremes
    roster_max_syllables = db.Column(db.Integer)  # Longest name on roster
    roster_min_syllables = db.Column(db.Integer)  # Shortest name on roster
    roster_harshest_player = db.Column(db.Float)
    roster_softest_player = db.Column(db.Float)
    
    # ===========================================================================
    # COMPOSITE SCORES (Combination of all 3 layers)
    # ===========================================================================
    composite_linguistic_score = db.Column(db.Float, index=True)  # Weighted: team 30% + city 20% + roster 50%
    composite_memorability = db.Column(db.Float)
    composite_prestige = db.Column(db.Float)
    composite_power = db.Column(db.Float)
    composite_harmony = db.Column(db.Float)  # Overall phonetic cohesion
    
    # Cluster assignments
    team_name_cluster = db.Column(db.Integer)
    roster_cluster = db.Column(db.Integer)
    composite_cluster = db.Column(db.Integer)
    
    # Metadata
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    roster_season = db.Column(db.Integer)  # Season for which roster was analyzed
    
    def __repr__(self):
        return f'<MLBTeamAnalysis for {self.team_id}>'
    
    def to_dict(self):
        return {
            'team_id': self.team_id,
            'team_name_syllables': self.team_name_syllables,
            'team_name_type': self.team_name_type,
            'city_prestige_score': self.city_prestige_score,
            'roster_mean_syllables': self.roster_mean_syllables,
            'roster_harmony_score': self.roster_harmony_score,
            'roster_international_percentage': self.roster_international_percentage,
            'composite_linguistic_score': self.composite_linguistic_score,
            'composite_cluster': self.composite_cluster
        }


class MLBMatchup(db.Model):
    """Head-to-head team matchups for linguistic prediction analysis"""
    __tablename__ = 'mlb_matchups'
    __table_args__ = (
        db.Index('idx_mlb_matchup_season', 'season'),
        db.Index('idx_mlb_matchup_teams', 'home_team_id', 'away_team_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False, index=True)
    game_date = db.Column(db.Date)
    game_number = db.Column(db.Integer)  # Game # of season
    
    # Teams
    home_team_id = db.Column(db.String(10), db.ForeignKey('mlb_teams.id'), nullable=False)
    away_team_id = db.Column(db.String(10), db.ForeignKey('mlb_teams.id'), nullable=False)
    
    # Outcome
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    winner_id = db.Column(db.String(10))  # Team ID of winner
    is_home_win = db.Column(db.Boolean)
    
    # Linguistic differentials (home - away)
    composite_differential = db.Column(db.Float)  # Home composite - away composite
    roster_differential = db.Column(db.Float)
    city_differential = db.Column(db.Float)
    team_name_differential = db.Column(db.Float)
    
    # Prediction
    predicted_winner_id = db.Column(db.String(10))  # Based on linguistic model
    prediction_correct = db.Column(db.Boolean)
    prediction_confidence = db.Column(db.Float)  # 0-1
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MLBMatchup {self.home_team_id} vs {self.away_team_id} ({self.season})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'season': self.season,
            'home_team': self.home_team_id,
            'away_team': self.away_team_id,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'winner': self.winner_id,
            'composite_differential': self.composite_differential,
            'predicted_winner': self.predicted_winner_id,
            'prediction_correct': self.prediction_correct
        }


