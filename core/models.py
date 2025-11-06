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


