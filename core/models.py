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


# =============================================================================
# ADULT FILM PERFORMER MODELS
# =============================================================================

class AdultPerformer(db.Model):
    """Adult film performer data - stage names and career metrics"""
    __tablename__ = 'adult_performers'
    __table_args__ = (
        db.Index('idx_performer_debut_year', 'debut_year'),
        db.Index('idx_performer_primary_genre', 'primary_genre'),
        db.Index('idx_performer_era_group', 'era_group'),
        db.Index('idx_performer_success_score', 'overall_success_score'),
    )
    
    id = db.Column(db.String(100), primary_key=True)  # Unique performer ID
    stage_name = db.Column(db.String(200), nullable=False, index=True)
    real_name = db.Column(db.String(200))  # If publicly known
    uses_real_name = db.Column(db.Boolean, default=False)
    
    # Career
    debut_year = db.Column(db.Integer, index=True)
    final_year = db.Column(db.Integer)
    years_active = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=False)
    
    # Era classification
    era_group = db.Column(db.String(30))  # golden_age (1970-1989), video_era (1990-2004), internet_era (2005-2014), streaming_era (2015-2024)
    
    # Career metrics
    film_count = db.Column(db.Integer)
    video_count = db.Column(db.Integer)  # Includes online content
    total_views = db.Column(db.BigInteger)  # Aggregate across platforms
    
    # Platform-specific
    pornhub_views = db.Column(db.BigInteger)
    pornhub_subscribers = db.Column(db.Integer)
    onlyfans_subscribers = db.Column(db.Integer)  # If publicly available
    
    # Recognition
    award_nominations = db.Column(db.Integer)
    awards_won = db.Column(db.Integer)
    avn_awards = db.Column(db.Integer)  # AVN (Adult Video News) Awards
    xbiz_awards = db.Column(db.Integer)
    
    # Genre/Specialization
    primary_genre = db.Column(db.String(50))
    genres = db.Column(db.Text)  # JSON list of all genres
    
    # Name history
    previous_stage_names = db.Column(db.Text)  # JSON list if changed names
    name_change_count = db.Column(db.Integer, default=0)
    
    # Career outcome tracking (CRITICAL for risk analysis)
    career_outcome = db.Column(db.String(50), index=True)  # 'active', 'retired', 'early_exit', 'tragic', 'deceased'
    exit_reason = db.Column(db.String(100))  # If known: 'natural', 'suicide', 'overdose', 'accident', 'illness', 'unknown'
    age_at_exit = db.Column(db.Integer)  # If applicable
    years_until_exit = db.Column(db.Float)  # From debut to exit/death
    early_exit = db.Column(db.Boolean, default=False, index=True)  # Career < 3 years
    tragic_outcome = db.Column(db.Boolean, default=False, index=True)  # Suicide/overdose/violent death
    
    # Success metrics (computed)
    popularity_score = db.Column(db.Float, index=True)  # 0-100 based on views/subscribers
    longevity_score = db.Column(db.Float)  # 0-100 based on career length and consistency
    achievement_score = db.Column(db.Float)  # 0-100 based on awards and recognition
    overall_success_score = db.Column(db.Float, index=True)  # Composite of above
    
    # Source metadata
    source = db.Column(db.String(50))  # IAFD, Pornhub, etc.
    data_quality = db.Column(db.String(20))  # high, medium, low
    last_updated = db.Column(db.DateTime)
    
    # Relationship
    analysis = db.relationship('AdultPerformerAnalysis', backref='performer', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AdultPerformer {self.stage_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'stage_name': self.stage_name,
            'debut_year': self.debut_year,
            'final_year': self.final_year,
            'years_active': self.years_active,
            'is_active': self.is_active,
            'era_group': self.era_group,
            'film_count': self.film_count,
            'video_count': self.video_count,
            'total_views': self.total_views,
            'award_nominations': self.award_nominations,
            'awards_won': self.awards_won,
            'primary_genre': self.primary_genre,
            'popularity_score': self.popularity_score,
            'longevity_score': self.longevity_score,
            'achievement_score': self.achievement_score,
            'overall_success_score': self.overall_success_score
        }


class AdultPerformerAnalysis(db.Model):
    """Phonetic and linguistic analysis of adult film performer stage names"""
    __tablename__ = 'adult_performer_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    performer_id = db.Column(db.String(100), db.ForeignKey('adult_performers.id'), nullable=False, unique=True)
    
    # Name structure
    syllable_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    first_name_syllables = db.Column(db.Integer)
    last_name_syllables = db.Column(db.Integer)
    first_name_length = db.Column(db.Integer)
    last_name_length = db.Column(db.Integer)
    
    # Standard phonetic features
    harshness_score = db.Column(db.Float)
    smoothness_score = db.Column(db.Float)
    softness_score = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    phonetic_complexity = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    # Advanced phonetic
    plosive_ratio = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    fricative_ratio = db.Column(db.Float)
    liquid_ratio = db.Column(db.Float)
    consonant_cluster_density = db.Column(db.Float)
    alliteration_score = db.Column(db.Float)
    
    # Stage name specific metrics
    sexy_score = db.Column(db.Float)  # Phonetic appeal/sensuality
    fantasy_score = db.Column(db.Float)  # Aspirational/fantasy elements
    accessibility_score = db.Column(db.Float)  # Easy to say/remember/search
    brand_strength_score = db.Column(db.Float)  # Overall branding power
    
    # Name composition analysis
    uses_first_last_format = db.Column(db.Boolean)  # "Firstname Lastname" format
    uses_single_name = db.Column(db.Boolean)  # Mononym
    has_title = db.Column(db.Boolean)  # Miss, Ms, etc.
    has_descriptor = db.Column(db.Boolean)  # "Little", "Big", etc.
    
    # Authenticity & Language (NEW - critical for contrast analysis)
    has_accent_marks = db.Column(db.Boolean, default=False)  # á, é, í, ñ, etc.
    language_origin = db.Column(db.String(50))  # anglo, latino, asian, european
    appears_anglicized = db.Column(db.Boolean)  # José → Joe pattern
    ethnic_name_strength = db.Column(db.Float)  # How strongly ethnic identity signals
    cross_linguistic_appeal = db.Column(db.Float)  # International-sounding score
    
    # Comparison to real name (if known)
    real_name_syllables = db.Column(db.Integer)
    syllable_delta = db.Column(db.Integer)  # Stage - real (positive = longer stage name)
    simplified_from_real = db.Column(db.Boolean)  # Stage name simpler than real
    
    # Genre alignment
    innocent_sounding_score = db.Column(db.Float)  # For certain genres
    aggressive_sounding_score = db.Column(db.Float)  # For other genres
    exotic_sounding_score = db.Column(db.Float)  # International appeal
    girl_next_door_score = db.Column(db.Float)  # Relatable/accessible
    
    # Clusters
    phonetic_cluster = db.Column(db.Integer)
    success_cluster = db.Column(db.Integer)
    era_cohort = db.Column(db.String(30))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdultPerformerAnalysis for performer_id={self.performer_id}>'


class SportsRosterAnalysis(db.Model):
    """Cross-domain analysis of professional sports roster composition and demographics
    
    Analyzes team-level roster characteristics comparing against American demographic baselines.
    Multi-level comparisons: team vs baseline, team vs league, sport vs sport.
    """
    __tablename__ = 'sports_roster_analyses'
    __table_args__ = (
        db.Index('idx_roster_sport', 'sport'),
        db.Index('idx_roster_team', 'team_id'),
        db.Index('idx_roster_americanness', 'americanness_score'),
        db.Index('idx_roster_melodiousness', 'melodiousness_score'),
        db.Index('idx_roster_season', 'season'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(50), nullable=False)  # Team identifier (abbrev or ID)
    team_name = db.Column(db.String(100), nullable=False)
    sport = db.Column(db.String(20), nullable=False)  # 'nfl', 'nba', 'mlb'
    league = db.Column(db.String(20))  # 'NFL', 'NBA', 'AL', 'NL'
    division = db.Column(db.String(50))  # Conference/division info
    season = db.Column(db.Integer)  # Season year
    
    # ===========================================================================
    # Core Metrics
    # ===========================================================================
    
    # Americanness Score (0-100): Phonetic patterns typical of Anglo-American names
    americanness_score = db.Column(db.Float, index=True)
    americanness_component_anglo_phonetics = db.Column(db.Float)
    americanness_component_intl_markers = db.Column(db.Float)
    americanness_component_syllable_structure = db.Column(db.Float)
    americanness_component_name_origin = db.Column(db.Float)
    
    # Melodiousness Score (0-100): Phonetic flow and harmony
    melodiousness_score = db.Column(db.Float, index=True)  # Raw score
    melodiousness_sport_adjusted = db.Column(db.Float, index=True)  # Adjusted for sport characteristics
    melodiousness_component_flow = db.Column(db.Float)
    melodiousness_component_vowel_harmony = db.Column(db.Float)
    melodiousness_component_rhythm = db.Column(db.Float)
    melodiousness_component_harshness_inverse = db.Column(db.Float)
    
    # ===========================================================================
    # Demographic Composition (percentages 0-100)
    # ===========================================================================
    demo_anglo_pct = db.Column(db.Float)
    demo_latino_pct = db.Column(db.Float)
    demo_asian_pct = db.Column(db.Float)
    demo_black_pct = db.Column(db.Float)
    demo_other_pct = db.Column(db.Float)
    
    # ===========================================================================
    # Roster Features (from existing player analyses)
    # ===========================================================================
    roster_size = db.Column(db.Integer)
    roster_harmony = db.Column(db.Float)  # Phonetic cohesion (0-100)
    mean_syllables = db.Column(db.Float)
    mean_harshness = db.Column(db.Float)
    mean_memorability = db.Column(db.Float)
    syllable_stddev = db.Column(db.Float)
    
    # ===========================================================================
    # Baseline Comparisons (Z-scores and statistical tests)
    # ===========================================================================
    
    # Americanness comparisons
    americanness_vs_random_baseline_zscore = db.Column(db.Float)
    americanness_vs_stratified_baseline_zscore = db.Column(db.Float)
    americanness_vs_league_zscore = db.Column(db.Float)
    americanness_vs_sport_zscore = db.Column(db.Float)
    
    # Melodiousness comparisons
    melodiousness_vs_random_baseline_zscore = db.Column(db.Float)
    melodiousness_vs_stratified_baseline_zscore = db.Column(db.Float)
    melodiousness_vs_league_zscore = db.Column(db.Float)
    melodiousness_vs_sport_zscore = db.Column(db.Float)
    
    # Demographic distribution tests
    demographic_chi_square = db.Column(db.Float)  # vs US Census baseline
    demographic_chi_square_pvalue = db.Column(db.Float)
    demographic_effect_size = db.Column(db.Float)  # Cramer's V
    
    # T-test results (roster metrics vs baseline)
    americanness_ttest_statistic = db.Column(db.Float)
    americanness_ttest_pvalue = db.Column(db.Float)
    melodiousness_ttest_statistic = db.Column(db.Float)
    melodiousness_ttest_pvalue = db.Column(db.Float)
    
    # ===========================================================================
    # Rankings (within league and overall)
    # ===========================================================================
    americanness_rank_in_league = db.Column(db.Integer)
    americanness_rank_overall = db.Column(db.Integer)
    melodiousness_rank_in_league = db.Column(db.Integer)
    melodiousness_rank_overall = db.Column(db.Integer)
    demographic_diversity_rank = db.Column(db.Integer)
    
    # ===========================================================================
    # Sport Characteristics (loaded from sport_characteristics.json)
    # ===========================================================================
    sport_contact_level = db.Column(db.Integer)  # 0-10 scale
    sport_action_speed = db.Column(db.Integer)  # 0-10 scale
    sport_precision_vs_power = db.Column(db.Integer)  # 0-10 scale
    sport_team_size = db.Column(db.Integer)  # Actual team size
    
    # ===========================================================================
    # Metadata
    # ===========================================================================
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SportsRosterAnalysis {self.sport.upper()} {self.team_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'team_name': self.team_name,
            'sport': self.sport,
            'league': self.league,
            'division': self.division,
            'season': self.season,
            
            # Core metrics
            'americanness_score': self.americanness_score,
            'melodiousness_score': self.melodiousness_score,
            'melodiousness_sport_adjusted': self.melodiousness_sport_adjusted,
            
            # Demographics
            'demographics': {
                'anglo_pct': self.demo_anglo_pct,
                'latino_pct': self.demo_latino_pct,
                'asian_pct': self.demo_asian_pct,
                'black_pct': self.demo_black_pct,
                'other_pct': self.demo_other_pct,
            },
            
            # Roster features
            'roster': {
                'size': self.roster_size,
                'harmony': self.roster_harmony,
                'mean_syllables': self.mean_syllables,
                'mean_harshness': self.mean_harshness,
                'mean_memorability': self.mean_memorability,
            },
            
            # Comparisons
            'comparisons': {
                'americanness_vs_baseline_z': self.americanness_vs_random_baseline_zscore,
                'americanness_vs_league_z': self.americanness_vs_league_zscore,
                'melodiousness_vs_baseline_z': self.melodiousness_vs_random_baseline_zscore,
                'demographic_chi_square': self.demographic_chi_square,
                'demographic_pvalue': self.demographic_chi_square_pvalue,
            },
            
            # Rankings
            'rankings': {
                'americanness_in_league': self.americanness_rank_in_league,
                'americanness_overall': self.americanness_rank_overall,
                'melodiousness_in_league': self.melodiousness_rank_in_league,
                'melodiousness_overall': self.melodiousness_rank_overall,
            },
            
            # Metadata
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
        }


class LiteraryWork(db.Model):
    """Literary works for name composition analysis
    
    Stores fiction, nonfiction, and gospels with metadata for cross-category comparison.
    """
    __tablename__ = 'literary_works'
    __table_args__ = (
        db.Index('idx_literary_category', 'category'),
        db.Index('idx_literary_genre', 'genre'),
        db.Index('idx_literary_year', 'publication_year'),
        db.Index('idx_literary_author', 'author'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'fiction', 'nonfiction', 'gospels'
    genre = db.Column(db.String(100))  # 'mystery', 'sci-fi', 'biography', etc.
    publication_year = db.Column(db.Integer)
    
    # Source information
    source = db.Column(db.String(100))  # 'Project Gutenberg', 'canonical text'
    source_id = db.Column(db.String(100))  # Gutenberg ID or other identifier
    source_url = db.Column(db.Text)
    
    # Text metadata
    word_count = db.Column(db.Integer)
    character_count_total = db.Column(db.Integer)  # Total characters extracted
    place_count = db.Column(db.Integer)  # Place names extracted
    term_count = db.Column(db.Integer)  # Invented terms extracted
    
    # Work-level analysis
    invented_name_pct = db.Column(db.Float)  # Percentage of invented vs real names
    mean_name_melodiousness = db.Column(db.Float)
    mean_name_americanness = db.Column(db.Float)
    mean_name_commonality = db.Column(db.Float)
    mean_name_syllables = db.Column(db.Float)
    
    # Statistical comparisons
    melodiousness_vs_baseline_zscore = db.Column(db.Float)
    commonality_vs_baseline_zscore = db.Column(db.Float)
    invented_name_ratio = db.Column(db.Float)  # Ratio to baseline
    
    # Quality metrics
    data_completeness_score = db.Column(db.Float)
    extraction_confidence = db.Column(db.Float)
    
    # Metadata
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyzed_at = db.Column(db.DateTime)
    
    # Relationships
    characters = db.relationship('LiteraryCharacter', backref='work', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LiteraryWork {self.title} ({self.category})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'source': self.source,
            'stats': {
                'word_count': self.word_count,
                'character_count': self.character_count_total,
                'place_count': self.place_count,
                'term_count': self.term_count,
                'invented_name_pct': self.invented_name_pct,
            },
            'means': {
                'melodiousness': self.mean_name_melodiousness,
                'americanness': self.mean_name_americanness,
                'commonality': self.mean_name_commonality,
                'syllables': self.mean_name_syllables,
            },
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
        }


class LiteraryCharacter(db.Model):
    """Characters extracted from literary works
    
    Stores character names with roles, outcomes, and importance for predictive analysis.
    """
    __tablename__ = 'literary_characters'
    __table_args__ = (
        db.Index('idx_character_work', 'work_id'),
        db.Index('idx_character_role', 'character_role'),
        db.Index('idx_character_outcome', 'character_outcome'),
        db.Index('idx_character_importance', 'importance_score'),
        db.Index('idx_character_name_type', 'name_type'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('literary_works.id'), nullable=False)
    
    # Name information
    full_name = db.Column(db.String(200), nullable=False, index=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    title = db.Column(db.String(50))  # Mr., Dr., Lord, etc.
    epithet = db.Column(db.String(200))  # "the Great", "the Wise", etc.
    
    # Character classification
    character_role = db.Column(db.String(50))  # 'protagonist', 'antagonist', 'supporting', 'minor'
    character_outcome = db.Column(db.String(50))  # 'survives', 'dies', 'succeeds', 'fails', 'transforms', 'static'
    character_importance = db.Column(db.String(50))  # 'major', 'supporting', 'minor'
    
    # Name type classification
    name_type = db.Column(db.String(50))  # 'real_common', 'real_uncommon', 'historical', 'invented_plausible', 'invented_fantastical'
    is_invented = db.Column(db.Boolean, default=False)
    is_place_name = db.Column(db.Boolean, default=False)
    is_invented_term = db.Column(db.Boolean, default=False)
    
    # Importance metrics
    mention_count = db.Column(db.Integer, default=0)  # How many times mentioned
    speaking_lines = db.Column(db.Integer)  # Dialogue/speaking instances
    importance_score = db.Column(db.Float)  # Calculated importance (0-100)
    first_appearance_position = db.Column(db.Float)  # Position in text (0.0-1.0)
    
    # Entity extraction metadata
    entity_type = db.Column(db.String(50))  # 'PERSON', 'GPE', 'LOC', etc. (NER tag)
    extraction_confidence = db.Column(db.Float)
    
    # Role prediction features (computed during analysis)
    predicted_role = db.Column(db.String(50))  # Model prediction
    role_prediction_confidence = db.Column(db.Float)
    predicted_outcome = db.Column(db.String(50))  # Model prediction
    outcome_prediction_confidence = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    name_analysis = db.relationship('LiteraryNameAnalysis', backref='character', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LiteraryCharacter {self.full_name} ({self.character_role})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'work_id': self.work_id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.character_role,
            'outcome': self.character_outcome,
            'importance': self.character_importance,
            'name_type': self.name_type,
            'is_invented': self.is_invented,
            'mention_count': self.mention_count,
            'importance_score': self.importance_score,
            'predictions': {
                'predicted_role': self.predicted_role,
                'role_confidence': self.role_prediction_confidence,
                'predicted_outcome': self.predicted_outcome,
                'outcome_confidence': self.outcome_prediction_confidence,
            },
            'name_analysis': self.name_analysis.to_dict() if self.name_analysis else None,
        }


class LiteraryNameAnalysis(db.Model):
    """Phonetic and linguistic analysis of literary character names
    
    Comprehensive name analysis for predictive nominative determinism testing.
    """
    __tablename__ = 'literary_name_analyses'
    __table_args__ = (
        db.Index('idx_literary_character', 'character_id'),
        db.Index('idx_literary_melodiousness', 'melodiousness_score'),
        db.Index('idx_literary_americanness', 'americanness_score'),
        db.Index('idx_literary_commonality', 'commonality_score'),
        db.Index('idx_literary_valence', 'name_valence'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('literary_characters.id'), nullable=False, unique=True)
    
    # ===========================================================================
    # Core Phonetic Analysis
    # ===========================================================================
    
    # Syllable and structure
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    vowel_count = db.Column(db.Integer)
    consonant_count = db.Column(db.Integer)
    
    # Melodiousness (0-100): Phonetic flow and pleasantness
    melodiousness_score = db.Column(db.Float, index=True)
    melodiousness_component_flow = db.Column(db.Float)
    melodiousness_component_vowel_harmony = db.Column(db.Float)
    melodiousness_component_rhythm = db.Column(db.Float)
    melodiousness_component_harshness_inverse = db.Column(db.Float)
    
    # Americanness (0-100): Anglo-American phonetic patterns
    americanness_score = db.Column(db.Float, index=True)
    americanness_component_anglo_phonetics = db.Column(db.Float)
    americanness_component_intl_markers = db.Column(db.Float)
    americanness_component_syllable_structure = db.Column(db.Float)
    americanness_component_name_origin = db.Column(db.Float)
    
    # Harshness and phonetic characteristics
    harshness_score = db.Column(db.Float)
    plosive_count = db.Column(db.Integer)
    fricative_count = db.Column(db.Integer)
    liquid_count = db.Column(db.Integer)
    nasal_count = db.Column(db.Integer)
    
    # ===========================================================================
    # Name Commonality and Familiarity
    # ===========================================================================
    commonality_score = db.Column(db.Float, index=True)  # 0-100: How common/familiar
    is_in_top_100_names = db.Column(db.Boolean, default=False)
    is_in_top_1000_names = db.Column(db.Boolean, default=False)
    census_rank_first = db.Column(db.Integer)  # SSA/Census rank for first name
    census_rank_last = db.Column(db.Integer)  # Census rank for last name
    
    # Historical/cultural context
    name_origin = db.Column(db.String(100))  # 'anglo', 'latino', 'asian', 'germanic', 'invented', etc.
    appears_historical = db.Column(db.Boolean)  # Biblical, classical, historical figure
    appears_modern = db.Column(db.Boolean)
    
    # ===========================================================================
    # Name Valence and Semantic Association
    # ===========================================================================
    name_valence = db.Column(db.Float)  # -100 to +100: Negative to positive associations
    has_positive_meaning = db.Column(db.Boolean)
    has_negative_meaning = db.Column(db.Boolean)
    has_neutral_meaning = db.Column(db.Boolean)
    meaning_strength = db.Column(db.Float)  # How strong the semantic association
    
    # Semantic categories
    suggests_strength = db.Column(db.Boolean)
    suggests_weakness = db.Column(db.Boolean)
    suggests_nobility = db.Column(db.Boolean)
    suggests_commonness = db.Column(db.Boolean)
    suggests_evil = db.Column(db.Boolean)
    suggests_goodness = db.Column(db.Boolean)
    
    # ===========================================================================
    # Memorability and Distinctiveness
    # ===========================================================================
    memorability_score = db.Column(db.Float)  # 0-100
    distinctiveness_score = db.Column(db.Float)  # 0-100: How unique/unusual
    pronounceability_score = db.Column(db.Float)  # 0-100: How easy to pronounce
    
    # Phonetic patterns
    has_alliteration = db.Column(db.Boolean)  # First and last name start same
    has_rhyme = db.Column(db.Boolean)
    has_repetition = db.Column(db.Boolean)
    
    # ===========================================================================
    # Cross-linguistic and Ethnic Markers
    # ===========================================================================
    has_accent_marks = db.Column(db.Boolean)
    language_origin_confidence = db.Column(db.Float)
    appears_anglicized = db.Column(db.Boolean)
    ethnic_name_strength = db.Column(db.Float)  # How strongly signals ethnicity
    cross_linguistic_appeal = db.Column(db.Float)  # International accessibility
    
    # ===========================================================================
    # Role/Outcome Prediction Features
    # ===========================================================================
    
    # Protagonist likelihood features
    protagonist_name_score = db.Column(db.Float)  # 0-100: Likelihood of protagonist
    hero_name_archetype = db.Column(db.Float)
    everyman_quality = db.Column(db.Float)
    
    # Antagonist likelihood features
    antagonist_name_score = db.Column(db.Float)  # 0-100: Likelihood of antagonist
    villain_name_archetype = db.Column(db.Float)
    threatening_quality = db.Column(db.Float)
    
    # Victim/vulnerable features
    vulnerable_sounding_score = db.Column(db.Float)
    delicate_quality = db.Column(db.Float)
    
    # Power/authority features
    authority_name_score = db.Column(db.Float)
    powerful_sounding = db.Column(db.Float)
    
    # ===========================================================================
    # Comparative Scores (vs baselines)
    # ===========================================================================
    melodiousness_vs_category_mean_zscore = db.Column(db.Float)
    americanness_vs_category_mean_zscore = db.Column(db.Float)
    commonality_vs_category_mean_zscore = db.Column(db.Float)
    melodiousness_vs_real_names_zscore = db.Column(db.Float)
    
    # ===========================================================================
    # Metadata
    # ===========================================================================
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LiteraryNameAnalysis for character_id={self.character_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'character_id': self.character_id,
            
            # Core metrics
            'syllable_count': self.syllable_count,
            'character_length': self.character_length,
            'melodiousness_score': self.melodiousness_score,
            'americanness_score': self.americanness_score,
            'commonality_score': self.commonality_score,
            'harshness_score': self.harshness_score,
            
            # Commonality
            'is_common': self.is_in_top_1000_names,
            'census_rank_first': self.census_rank_first,
            
            # Valence
            'name_valence': self.name_valence,
            'has_positive_meaning': self.has_positive_meaning,
            'has_negative_meaning': self.has_negative_meaning,
            
            # Memorability
            'memorability_score': self.memorability_score,
            'distinctiveness_score': self.distinctiveness_score,
            
            # Prediction scores
            'protagonist_score': self.protagonist_name_score,
            'antagonist_score': self.antagonist_name_score,
            'vulnerable_score': self.vulnerable_sounding_score,
            
            # Comparisons
            'melodiousness_vs_category_z': self.melodiousness_vs_category_mean_zscore,
            'commonality_vs_category_z': self.commonality_vs_category_mean_zscore,
            
            'computed_at': self.computed_at.isoformat() if self.computed_at else None,
        }


class Instrument(db.Model):
    """Musical instruments for Romance language cross-linguistic analysis
    
    Comprehensive dataset of 100+ instruments with names in 5 Romance languages,
    analyzing phonetic properties and correlating with cultural usage patterns.
    """
    __tablename__ = 'instruments'
    __table_args__ = (
        db.Index('idx_instrument_category', 'instrument_category'),
        db.Index('idx_instrument_origin_period', 'origin_period'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    base_name_english = db.Column(db.String(200), nullable=False, unique=True, index=True)
    instrument_category = db.Column(db.String(50))  # string, woodwind, brass, percussion, keyboard, folk, modern
    origin_period = db.Column(db.String(50))  # medieval, baroque, classical, romantic, modern
    physical_properties = db.Column(db.Text)  # JSON: {size, pitch_range, playing_technique}
    
    # Names across Romance Languages
    spanish_name = db.Column(db.String(200))
    french_name = db.Column(db.String(200))
    italian_name = db.Column(db.String(200))
    portuguese_name = db.Column(db.String(200))
    romanian_name = db.Column(db.String(200))
    
    # IPA Pronunciations
    spanish_ipa = db.Column(db.String(200))
    french_ipa = db.Column(db.String(200))
    italian_ipa = db.Column(db.String(200))
    portuguese_ipa = db.Column(db.String(200))
    romanian_ipa = db.Column(db.String(200))
    
    # Etymology & Linguistic Properties
    etymology_by_language = db.Column(db.Text)  # JSON: {spanish: {origin, path}, french: {...}, ...}
    is_native_word = db.Column(db.Text)  # JSON: {spanish: true/false, french: true/false, ...}
    descriptive_transparency = db.Column(db.Text)  # JSON: {spanish: score, french: score, ...}
    
    # Cultural Associations
    cultural_associations = db.Column(db.Text)  # Regional significance, symbolic meanings
    
    # Metadata
    source = db.Column(db.String(200))
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    name_analyses = db.relationship('InstrumentNameAnalysis', backref='instrument', lazy='dynamic', cascade='all, delete-orphan')
    usage_data = db.relationship('InstrumentUsageData', backref='instrument', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Instrument {self.base_name_english}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'base_name_english': self.base_name_english,
            'instrument_category': self.instrument_category,
            'origin_period': self.origin_period,
            'physical_properties': json.loads(self.physical_properties) if self.physical_properties else {},
            'names': {
                'spanish': self.spanish_name,
                'french': self.french_name,
                'italian': self.italian_name,
                'portuguese': self.portuguese_name,
                'romanian': self.romanian_name,
            },
            'ipa': {
                'spanish': self.spanish_ipa,
                'french': self.french_ipa,
                'italian': self.italian_ipa,
                'portuguese': self.portuguese_ipa,
                'romanian': self.romanian_ipa,
            },
            'etymology_by_language': json.loads(self.etymology_by_language) if self.etymology_by_language else {},
            'is_native_word': json.loads(self.is_native_word) if self.is_native_word else {},
            'descriptive_transparency': json.loads(self.descriptive_transparency) if self.descriptive_transparency else {},
            'cultural_associations': self.cultural_associations,
            'source': self.source,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class InstrumentNameAnalysis(db.Model):
    """Comprehensive phonetic analysis of instrument names per language
    
    Applies love words phonetic framework to each instrument name in each Romance language.
    Analyzes beauty, melodiousness, harshness, and other phonetic properties.
    """
    __tablename__ = 'instrument_name_analysis'
    __table_args__ = (
        db.Index('idx_inst_analysis_instrument', 'instrument_id'),
        db.Index('idx_inst_analysis_language', 'language'),
        db.Index('idx_inst_analysis_beauty', 'beauty_score'),
        db.Index('idx_inst_analysis_composite', 'instrument_id', 'language'),  # Composite index
    )
    
    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    language = db.Column(db.String(20), nullable=False)  # spanish, french, italian, portuguese, romanian
    
    # ===========================================================================
    # Core Phonetic Analysis (from CountryNameLinguistics / Love Words)
    # ===========================================================================
    
    # Basic Metrics
    character_length = db.Column(db.Integer)
    syllable_count = db.Column(db.Integer)
    
    # Sound Counts
    plosives_count = db.Column(db.Integer)  # p, t, k, b, d, g
    sibilants_count = db.Column(db.Integer)  # s, z, sh, ch
    liquids_nasals_count = db.Column(db.Integer)  # l, r, m, n
    vowels_count = db.Column(db.Integer)  # a, e, i, o, u
    
    # Density Ratios
    vowel_density = db.Column(db.Float)  # Vowels / total length
    consonant_density = db.Column(db.Float)
    liquid_density = db.Column(db.Float)  # Soft sounds / total length
    
    # Aesthetic Scores (0-100)
    harshness_score = db.Column(db.Float)  # Plosives + sibilants weighted
    melodiousness_score = db.Column(db.Float)  # Vowels + liquids + syllable flow
    beauty_score = db.Column(db.Float)  # melodiousness - (harshness * 0.3)
    
    # ===========================================================================
    # Advanced Phonetic Features
    # ===========================================================================
    
    # Consonant Clusters
    has_consonant_clusters = db.Column(db.Boolean)
    max_consonant_cluster_length = db.Column(db.Integer)
    consonant_cluster_count = db.Column(db.Integer)
    
    # Sound Symbolism
    sharp_sounds_count = db.Column(db.Integer)  # k, t, i, e (angular)
    round_sounds_count = db.Column(db.Integer)  # b, m, o, u (round)
    sound_symbolism_ratio = db.Column(db.Float)  # round / sharp
    
    # Phonetic Patterns
    starts_with_liquid = db.Column(db.Boolean)  # l, r, m, n
    ends_with_vowel = db.Column(db.Boolean)
    has_repeated_sounds = db.Column(db.Boolean)
    
    # Soft vs. Harsh
    soft_sound_dominance = db.Column(db.Float)  # Ratio of soft to harsh sounds
    
    # ===========================================================================
    # Linguistic Structure
    # ===========================================================================
    
    # Native vs. Borrowed
    native_word = db.Column(db.Boolean)  # Is this native Romance or borrowed?
    
    # Descriptive Transparency
    descriptive_transparency = db.Column(db.Float)  # 0-100: how descriptive is name?
    
    # Word Formation
    is_compound = db.Column(db.Boolean)  # Multi-morpheme word
    word_formation_notes = db.Column(db.Text)  # Analysis notes
    
    # ===========================================================================
    # Cross-Linguistic Comparisons
    # ===========================================================================
    
    # Rank within language
    beauty_rank_in_language = db.Column(db.Integer)
    
    # Rank across all instruments in this language
    beauty_percentile = db.Column(db.Float)  # 0-100
    
    # Deviation from means
    beauty_vs_language_mean_zscore = db.Column(db.Float)
    beauty_vs_category_mean_zscore = db.Column(db.Float)  # Within instrument category
    
    # Cross-language consistency
    cross_language_beauty_variance = db.Column(db.Float)  # How much does beauty vary across languages for this instrument?
    
    # ===========================================================================
    # Metadata
    # ===========================================================================
    
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_version = db.Column(db.String(20), default='1.0')
    
    def __repr__(self):
        return f'<InstrumentNameAnalysis {self.instrument_id} - {self.language}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'instrument_id': self.instrument_id,
            'language': self.language,
            
            # Core metrics
            'character_length': self.character_length,
            'syllable_count': self.syllable_count,
            
            # Sound counts
            'plosives': self.plosives_count,
            'sibilants': self.sibilants_count,
            'liquids_nasals': self.liquids_nasals_count,
            'vowels': self.vowels_count,
            
            # Densities
            'vowel_density': self.vowel_density,
            'liquid_density': self.liquid_density,
            
            # Aesthetic scores
            'harshness_score': self.harshness_score,
            'melodiousness_score': self.melodiousness_score,
            'beauty_score': self.beauty_score,
            
            # Advanced features
            'has_consonant_clusters': self.has_consonant_clusters,
            'sound_symbolism_ratio': self.sound_symbolism_ratio,
            'starts_with_liquid': self.starts_with_liquid,
            'ends_with_vowel': self.ends_with_vowel,
            'soft_sound_dominance': self.soft_sound_dominance,
            
            # Linguistic
            'native_word': self.native_word,
            'descriptive_transparency': self.descriptive_transparency,
            'is_compound': self.is_compound,
            
            # Rankings
            'beauty_rank_in_language': self.beauty_rank_in_language,
            'beauty_percentile': self.beauty_percentile,
            
            # Z-scores
            'beauty_z_language': self.beauty_vs_language_mean_zscore,
            'beauty_z_category': self.beauty_vs_category_mean_zscore,
            
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
        }


class InstrumentUsageData(db.Model):
    """Usage frequency data for instruments by Romance language region
    
    Combines multiple data sources: historical compositions, modern recordings,
    sheet music corpus, cultural surveys, and ensemble configurations to create
    comprehensive usage frequency metrics per region.
    """
    __tablename__ = 'instrument_usage_data'
    __table_args__ = (
        db.Index('idx_usage_instrument', 'instrument_id'),
        db.Index('idx_usage_region', 'language_region'),
        db.Index('idx_usage_score', 'normalized_usage_score'),
        db.Index('idx_usage_composite', 'instrument_id', 'language_region'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    language_region = db.Column(db.String(20), nullable=False)  # spain, france, italy, portugal, romania
    
    # ===========================================================================
    # Data Sources (Multiple Frequency Metrics)
    # ===========================================================================
    
    # A. Historical Composition Counts
    historical_composition_count = db.Column(db.Integer, default=0)  # Total appearances in major works
    historical_composition_score = db.Column(db.Float)  # Normalized 0-100
    
    # B. Modern Recording Frequency (Proxy)
    modern_recording_frequency = db.Column(db.Float)  # Based on genre popularity + typical instrumentation
    modern_recording_score = db.Column(db.Float)  # Normalized 0-100
    
    # C. Sheet Music Corpus Frequency
    sheet_music_corpus_frequency = db.Column(db.Integer, default=0)  # Mentions in digitized scores
    sheet_music_corpus_score = db.Column(db.Float)  # Normalized 0-100
    
    # D. Cultural Survey Prominence
    cultural_survey_prominence = db.Column(db.Float)  # 1-10 scale from ethnomusicology literature
    cultural_survey_score = db.Column(db.Float)  # Normalized 0-100
    
    # E. Ensemble Appearance Rate
    ensemble_appearance_rate = db.Column(db.Float)  # Percentage of standard ensembles featuring this instrument
    ensemble_appearance_score = db.Column(db.Float)  # Normalized 0-100
    
    # ===========================================================================
    # Time Period Breakdown
    # ===========================================================================
    
    period_breakdown = db.Column(db.Text)  # JSON: {medieval, baroque, classical, romantic, modern, contemporary}
    
    # ===========================================================================
    # Composite Metrics
    # ===========================================================================
    
    # Normalized Usage Score (0-100)
    normalized_usage_score = db.Column(db.Float)  # Weighted average of all sources
    weights_used = db.Column(db.Text)  # JSON: weights applied to each source
    
    # Regional Ranking
    usage_rank_within_region = db.Column(db.Integer)  # Rank among all instruments in this region
    usage_percentile = db.Column(db.Float)  # 0-100
    
    # Cross-regional Comparison
    usage_vs_global_mean_zscore = db.Column(db.Float)
    regional_specialization_score = db.Column(db.Float)  # How unique to this region vs. others
    
    # ===========================================================================
    # Data Quality Metrics
    # ===========================================================================
    
    data_completeness_score = db.Column(db.Float)  # 0-100: how many sources have data
    confidence_level = db.Column(db.String(20))  # high, medium, low
    sources_used = db.Column(db.Text)  # JSON: list of which sources provided data
    
    # ===========================================================================
    # Notes & Metadata
    # ===========================================================================
    
    usage_notes = db.Column(db.Text)  # Qualitative observations
    data_collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<InstrumentUsageData {self.instrument_id} - {self.language_region}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'instrument_id': self.instrument_id,
            'language_region': self.language_region,
            
            # Data sources
            'historical_composition_count': self.historical_composition_count,
            'historical_composition_score': self.historical_composition_score,
            'modern_recording_score': self.modern_recording_score,
            'sheet_music_corpus_frequency': self.sheet_music_corpus_frequency,
            'sheet_music_corpus_score': self.sheet_music_corpus_score,
            'cultural_survey_prominence': self.cultural_survey_prominence,
            'cultural_survey_score': self.cultural_survey_score,
            'ensemble_appearance_rate': self.ensemble_appearance_rate,
            'ensemble_appearance_score': self.ensemble_appearance_score,
            
            # Period breakdown
            'period_breakdown': json.loads(self.period_breakdown) if self.period_breakdown else {},
            
            # Composite metrics
            'normalized_usage_score': self.normalized_usage_score,
            'weights_used': json.loads(self.weights_used) if self.weights_used else {},
            'usage_rank_within_region': self.usage_rank_within_region,
            'usage_percentile': self.usage_percentile,
            
            # Comparisons
            'usage_z_score': self.usage_vs_global_mean_zscore,
            'regional_specialization': self.regional_specialization_score,
            
            # Data quality
            'data_completeness': self.data_completeness_score,
            'confidence_level': self.confidence_level,
            'sources_used': json.loads(self.sources_used) if self.sources_used else [],
            
            'usage_notes': self.usage_notes,
            'data_collected_at': self.data_collected_at.isoformat() if self.data_collected_at else None,
        }


class InstrumentEnsemble(db.Model):
    """Standard musical ensembles and their instrument configurations
    
    Tracks common ensemble types by region and analyzes phonetic coherence
    of instrument names within ensembles (e.g., do violino/viola/violoncello
    sound phonetically similar in Italian?).
    """
    __tablename__ = 'instrument_ensembles'
    __table_args__ = (
        db.Index('idx_ensemble_type', 'ensemble_type'),
        db.Index('idx_ensemble_region', 'language_region'),
        db.Index('idx_ensemble_period', 'time_period'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ensemble Identification
    ensemble_type = db.Column(db.String(100), nullable=False)  # string_quartet, brass_quintet, orchestra, folk_band, etc.
    ensemble_name = db.Column(db.String(200))  # Optional descriptive name
    language_region = db.Column(db.String(20))  # spain, france, italy, portugal, romania, general
    time_period = db.Column(db.String(50))  # baroque, classical, romantic, modern, contemporary
    
    # Instruments in Ensemble
    instruments = db.Column(db.Text, nullable=False)  # JSON: [instrument_id1, instrument_id2, ...]
    instrument_count = db.Column(db.Integer)
    
    # Frequency & Prominence
    frequency_score = db.Column(db.Float)  # 0-100: how common is this ensemble configuration
    cultural_prominence = db.Column(db.Float)  # 0-100: cultural importance
    
    # ===========================================================================
    # Phonetic Coherence Analysis
    # ===========================================================================
    
    # Do instrument names in this ensemble sound similar?
    phonetic_coherence_score = db.Column(db.Float)  # 0-100: phonetic similarity of names
    mean_beauty_score = db.Column(db.Float)  # Average beauty of all instrument names
    beauty_variance = db.Column(db.Float)  # How much do beauty scores vary?
    
    # Dominant phonetic features in ensemble
    dominant_phonetic_features = db.Column(db.Text)  # JSON: {high_liquid_density, open_vowels, etc.}
    
    # ===========================================================================
    # Ensemble Characteristics
    # ===========================================================================
    
    # Musical characteristics
    typical_repertoire = db.Column(db.Text)  # Representative works
    genre_associations = db.Column(db.Text)  # Classical, folk, popular, etc.
    
    # Regional variation
    regional_variants = db.Column(db.Text)  # JSON: How this ensemble differs by region
    
    # ===========================================================================
    # Metadata
    # ===========================================================================
    
    description = db.Column(db.Text)
    source = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<InstrumentEnsemble {self.ensemble_type} - {self.language_region}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ensemble_type': self.ensemble_type,
            'ensemble_name': self.ensemble_name,
            'language_region': self.language_region,
            'time_period': self.time_period,
            
            # Instruments
            'instruments': json.loads(self.instruments) if self.instruments else [],
            'instrument_count': self.instrument_count,
            
            # Frequency
            'frequency_score': self.frequency_score,
            'cultural_prominence': self.cultural_prominence,
            
            # Phonetic coherence
            'phonetic_coherence_score': self.phonetic_coherence_score,
            'mean_beauty_score': self.mean_beauty_score,
            'beauty_variance': self.beauty_variance,
            'dominant_phonetic_features': json.loads(self.dominant_phonetic_features) if self.dominant_phonetic_features else {},
            
            # Characteristics
            'typical_repertoire': self.typical_repertoire,
            'genre_associations': self.genre_associations,
            'regional_variants': json.loads(self.regional_variants) if self.regional_variants else {},
            
            'description': self.description,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# =====================================================
# FORETOLD NAMING & PROPHETIC ANALYSIS MODELS
# =====================================================

class NameEtymology(db.Model):
    """
    Etymology and prophetic meaning of names across cultures.
    Maps names to their historical, linguistic, and prophetic significance.
    """
    __tablename__ = 'name_etymology'
    __table_args__ = (
        db.Index('idx_name_etymology_name', 'name'),
        db.Index('idx_name_etymology_origin', 'cultural_origin'),
        db.Index('idx_name_etymology_category', 'destiny_category'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    
    # Core meaning
    literal_meaning = db.Column(db.Text)  # Direct translation/meaning
    prophetic_meaning = db.Column(db.Text)  # Symbolic/prophetic significance
    cultural_origin = db.Column(db.String(100))  # hebrew, greek, latin, arabic, etc.
    
    # Etymology breakdown
    etymology = db.Column(db.Text)  # Linguistic derivation
    name_prefix = db.Column(db.String(100))  # Prefix component
    name_root = db.Column(db.String(100))  # Root component
    name_suffix = db.Column(db.String(100))  # Suffix component
    
    # Semantic analysis
    semantic_valence = db.Column(db.String(50))  # positive, negative, neutral, ambiguous
    destiny_category = db.Column(db.String(100))  # virtue, power, wisdom, warrior, beauty, etc.
    symbolic_associations = db.Column(db.Text)  # JSON array of symbolic meanings
    
    # Historical context
    historical_figures = db.Column(db.Text)  # JSON array of notable bearers
    biblical_reference = db.Column(db.String(500))  # Biblical citation if applicable
    quranic_reference = db.Column(db.String(500))  # Quranic citation if applicable
    cultural_significance = db.Column(db.Text)  # Historical/cultural importance
    
    # Variants & translations
    variants = db.Column(db.Text)  # JSON array of name variants
    cross_cultural_equivalents = db.Column(db.Text)  # JSON dict of translations
    
    # Metadata
    gender = db.Column(db.String(20))  # M, F, M/F (unisex)
    popularity_peak = db.Column(db.String(200))  # Time period of peak usage
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    destiny_alignments = db.relationship('DestinyAlignment', backref='name_etymology', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'literal_meaning': self.literal_meaning,
            'prophetic_meaning': self.prophetic_meaning,
            'cultural_origin': self.cultural_origin,
            'etymology': self.etymology,
            'components': {
                'prefix': self.name_prefix,
                'root': self.name_root,
                'suffix': self.name_suffix
            },
            'semantic_valence': self.semantic_valence,
            'destiny_category': self.destiny_category,
            'symbolic_associations': json.loads(self.symbolic_associations) if self.symbolic_associations else [],
            'historical_figures': json.loads(self.historical_figures) if self.historical_figures else [],
            'biblical_reference': self.biblical_reference,
            'quranic_reference': self.quranic_reference,
            'cultural_significance': self.cultural_significance,
            'variants': json.loads(self.variants) if self.variants else [],
            'cross_cultural_equivalents': json.loads(self.cross_cultural_equivalents) if self.cross_cultural_equivalents else {},
            'gender': self.gender,
            'popularity_peak': self.popularity_peak,
        }


class DestinyAlignment(db.Model):
    """
    Tracks alignment between name prophetic meaning and actual outcomes.
    Tests nominative determinism via semantic similarity analysis.
    """
    __tablename__ = 'destiny_alignment'
    __table_args__ = (
        db.Index('idx_destiny_name_entity', 'name_etymology_id', 'entity_type', 'entity_id'),
        db.Index('idx_destiny_score', 'alignment_score'),
        db.Index('idx_destiny_domain', 'domain'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name_etymology_id = db.Column(db.Integer, db.ForeignKey('name_etymology.id'), nullable=False)
    
    # Entity being analyzed
    entity_type = db.Column(db.String(100))  # 'character', 'person', 'cryptocurrency', 'sports_team', etc.
    entity_id = db.Column(db.String(200))  # ID in respective domain
    entity_name = db.Column(db.String(500))  # Full name of entity
    domain = db.Column(db.String(100))  # 'literary', 'crypto', 'sports', 'business', etc.
    
    # Outcome data
    actual_outcome = db.Column(db.Text)  # Description of actual outcome
    outcome_category = db.Column(db.String(100))  # 'success', 'failure', 'heroic', 'tragic', etc.
    outcome_metrics = db.Column(db.Text)  # JSON dict of quantitative outcomes
    
    # Alignment analysis
    alignment_score = db.Column(db.Float)  # 0-1 score: how well name predicts outcome
    alignment_explanation = db.Column(db.Text)  # Textual explanation of alignment
    semantic_overlap = db.Column(db.Float)  # Word embedding similarity
    keyword_matches = db.Column(db.Text)  # JSON array of matching keywords
    
    # Statistical significance
    confidence_score = db.Column(db.Float)  # Statistical confidence in alignment
    sample_size_n = db.Column(db.Integer)  # Sample size for this category
    
    # Timestamps
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.entity_name,
            'entity_type': self.entity_type,
            'domain': self.domain,
            'actual_outcome': self.actual_outcome,
            'outcome_category': self.outcome_category,
            'outcome_metrics': json.loads(self.outcome_metrics) if self.outcome_metrics else {},
            'alignment_score': self.alignment_score,
            'alignment_explanation': self.alignment_explanation,
            'semantic_overlap': self.semantic_overlap,
            'keyword_matches': json.loads(self.keyword_matches) if self.keyword_matches else [],
            'confidence_score': self.confidence_score,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
        }


class CulturalNamingPattern(db.Model):
    """
    Cultural naming prophecies and expectations by region/era.
    Tracks hope-based naming patterns and cultural taboos.
    """
    __tablename__ = 'cultural_naming_pattern'
    __table_args__ = (
        db.Index('idx_cultural_region_era', 'region', 'era'),
        db.Index('idx_cultural_tradition', 'cultural_tradition'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Geographic/temporal context
    region = db.Column(db.String(200))  # Geographic region
    country = db.Column(db.String(200))  # Specific country if applicable
    cultural_tradition = db.Column(db.String(200))  # hebrew, islamic, christian, buddhist, etc.
    era = db.Column(db.String(200))  # Time period (e.g., "medieval", "19th century")
    start_year = db.Column(db.Integer)  # For temporal queries
    end_year = db.Column(db.Integer)
    
    # Naming pattern type
    pattern_type = db.Column(db.String(100))  # 'hope_based', 'prophetic', 'ancestral', 'religious', 'taboo'
    pattern_name = db.Column(db.String(300))  # Name of the pattern
    
    # Pattern characteristics
    description = db.Column(db.Text)  # Detailed description
    common_name_themes = db.Column(db.Text)  # JSON array of common themes
    example_names = db.Column(db.Text)  # JSON array of example names
    
    # Hope/expectation-based naming
    aspirational_meanings = db.Column(db.Text)  # JSON array: what parents hope for child
    virtue_emphasis = db.Column(db.Text)  # JSON array: emphasized virtues
    success_indicators = db.Column(db.Text)  # JSON array: markers of expected success
    
    # Taboos and avoidance
    avoided_meanings = db.Column(db.Text)  # JSON array: avoided name meanings
    taboo_names = db.Column(db.Text)  # JSON array: specific taboo names
    taboo_reasons = db.Column(db.Text)  # JSON dict: name -> reason for taboo
    
    # Gender patterns
    male_naming_patterns = db.Column(db.Text)  # JSON dict of male-specific patterns
    female_naming_patterns = db.Column(db.Text)  # JSON dict of female-specific patterns
    
    # Religious/spiritual influence
    religious_influence_level = db.Column(db.Float)  # 0-1: how much religion influences naming
    divine_name_usage = db.Column(db.Float)  # 0-1: frequency of divine/religious names
    saint_prophet_naming = db.Column(db.Float)  # 0-1: frequency of saint/prophet names
    
    # Outcome correlation
    success_correlation = db.Column(db.Float)  # Correlation between pattern and success
    outcome_data = db.Column(db.Text)  # JSON dict of outcome statistics
    
    # Sources and evidence
    source_documents = db.Column(db.Text)  # JSON array of source citations
    sample_size = db.Column(db.Integer)  # Number of names in sample
    confidence_level = db.Column(db.Float)  # Statistical confidence in pattern
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'region': self.region,
            'country': self.country,
            'cultural_tradition': self.cultural_tradition,
            'era': self.era,
            'time_range': {
                'start_year': self.start_year,
                'end_year': self.end_year
            },
            'pattern_type': self.pattern_type,
            'pattern_name': self.pattern_name,
            'description': self.description,
            'common_themes': json.loads(self.common_name_themes) if self.common_name_themes else [],
            'example_names': json.loads(self.example_names) if self.example_names else [],
            'aspirational': {
                'meanings': json.loads(self.aspirational_meanings) if self.aspirational_meanings else [],
                'virtues': json.loads(self.virtue_emphasis) if self.virtue_emphasis else [],
                'success_indicators': json.loads(self.success_indicators) if self.success_indicators else []
            },
            'taboos': {
                'avoided_meanings': json.loads(self.avoided_meanings) if self.avoided_meanings else [],
                'taboo_names': json.loads(self.taboo_names) if self.taboo_names else [],
                'reasons': json.loads(self.taboo_reasons) if self.taboo_reasons else {}
            },
            'gender_patterns': {
                'male': json.loads(self.male_naming_patterns) if self.male_naming_patterns else {},
                'female': json.loads(self.female_naming_patterns) if self.female_naming_patterns else {}
            },
            'religious_influence': {
                'level': self.religious_influence_level,
                'divine_usage': self.divine_name_usage,
                'saint_prophet_usage': self.saint_prophet_naming
            },
            'outcomes': {
                'success_correlation': self.success_correlation,
                'data': json.loads(self.outcome_data) if self.outcome_data else {}
            },
            'metadata': {
                'sources': json.loads(self.source_documents) if self.source_documents else [],
                'sample_size': self.sample_size,
                'confidence': self.confidence_level
            }
        }


# =====================================================
# ACOUSTIC ANALYSIS & PHONETIC UNIVERSALS MODELS
# =====================================================

class AcousticProfile(db.Model):
    """
    Deep acoustic analysis of names using signal processing techniques.
    Includes formant frequencies, spectral energy, prosody analysis.
    """
    __tablename__ = 'acoustic_profile'
    __table_args__ = (
        db.Index('idx_acoustic_name', 'name'),
        db.Index('idx_acoustic_harshness', 'harshness_score'),
        db.Index('idx_acoustic_melodiousness', 'melodiousness_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    
    # Formant frequencies (vowel quality)
    mean_f1 = db.Column(db.Float)  # First formant (vowel height)
    mean_f2 = db.Column(db.Float)  # Second formant (vowel frontness)
    mean_f3 = db.Column(db.Float)  # Third formant (rhoticity)
    f1_range = db.Column(db.Float)  # Variability in F1
    f2_range = db.Column(db.Float)  # Variability in F2
    
    # Spectral energy distribution
    low_frequency_energy = db.Column(db.Float)  # 0-500 Hz
    mid_frequency_energy = db.Column(db.Float)  # 500-2000 Hz
    high_frequency_energy = db.Column(db.Float)  # 2000+ Hz
    spectral_centroid = db.Column(db.Float)  # "Center of mass" of spectrum
    spectral_flatness = db.Column(db.Float)  # Noisiness vs tonality
    
    # Voice onset time (VOT) patterns
    mean_vot = db.Column(db.Float)  # Average VOT for stops
    vot_variance = db.Column(db.Float)  # Variability in VOT
    aspirated_stops_count = db.Column(db.Integer)  # Number of aspirated stops
    
    # Prosodic features
    stress_pattern = db.Column(db.String(100))  # 'initial', 'final', 'penultimate', etc.
    syllable_duration_mean = db.Column(db.Float)  # Average syllable length
    syllable_duration_variance = db.Column(db.Float)  # Rhythmic variability
    pitch_contour = db.Column(db.String(100))  # 'rising', 'falling', 'flat', 'complex'
    
    # Acoustic harshness vs softness
    harshness_score = db.Column(db.Float)  # 0-1: soft to harsh
    sibilance_score = db.Column(db.Float)  # Frequency of sibilants (s, z, sh)
    plosive_density = db.Column(db.Float)  # Frequency of stops (p, t, k, b, d, g)
    fricative_density = db.Column(db.Float)  # Frequency of fricatives
    sonorant_density = db.Column(db.Float)  # Frequency of resonants (l, r, m, n)
    
    # Overall acoustic characteristics
    melodiousness_score = db.Column(db.Float)  # 0-1: melodic quality
    rhythmic_regularity = db.Column(db.Float)  # 0-1: rhythmic predictability
    phonetic_complexity = db.Column(db.Float)  # 0-1: articulatory complexity
    
    # Consonant cluster analysis
    has_initial_clusters = db.Column(db.Boolean)
    has_final_clusters = db.Column(db.Boolean)
    max_cluster_size = db.Column(db.Integer)
    cluster_complexity_score = db.Column(db.Float)  # 0-1
    
    # Vowel sequence analysis
    vowel_sequence_pattern = db.Column(db.String(200))  # Pattern description
    diphthong_count = db.Column(db.Integer)
    vowel_harmony = db.Column(db.Float)  # 0-1: vowel similarity
    
    # Cross-linguistic pronounceability
    english_ease = db.Column(db.Float)  # 0-1: ease for English speakers
    spanish_ease = db.Column(db.Float)
    mandarin_ease = db.Column(db.Float)
    arabic_ease = db.Column(db.Float)
    hindi_ease = db.Column(db.Float)
    universal_pronounceability = db.Column(db.Float)  # Average across languages
    
    # Metadata
    analysis_method = db.Column(db.String(200))  # Description of analysis approach
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'formants': {
                'f1': {'mean': self.mean_f1, 'range': self.f1_range},
                'f2': {'mean': self.mean_f2, 'range': self.f2_range},
                'f3': {'mean': self.mean_f3}
            },
            'spectral': {
                'low_freq_energy': self.low_frequency_energy,
                'mid_freq_energy': self.mid_frequency_energy,
                'high_freq_energy': self.high_frequency_energy,
                'centroid': self.spectral_centroid,
                'flatness': self.spectral_flatness
            },
            'vot': {
                'mean': self.mean_vot,
                'variance': self.vot_variance,
                'aspirated_stops': self.aspirated_stops_count
            },
            'prosody': {
                'stress_pattern': self.stress_pattern,
                'syllable_duration_mean': self.syllable_duration_mean,
                'syllable_duration_variance': self.syllable_duration_variance,
                'pitch_contour': self.pitch_contour
            },
            'harshness': {
                'overall_score': self.harshness_score,
                'sibilance': self.sibilance_score,
                'plosive_density': self.plosive_density,
                'fricative_density': self.fricative_density,
                'sonorant_density': self.sonorant_density
            },
            'overall': {
                'melodiousness': self.melodiousness_score,
                'rhythmic_regularity': self.rhythmic_regularity,
                'phonetic_complexity': self.phonetic_complexity
            },
            'clusters': {
                'initial': self.has_initial_clusters,
                'final': self.has_final_clusters,
                'max_size': self.max_cluster_size,
                'complexity': self.cluster_complexity_score
            },
            'vowels': {
                'sequence_pattern': self.vowel_sequence_pattern,
                'diphthong_count': self.diphthong_count,
                'harmony': self.vowel_harmony
            },
            'pronounceability': {
                'english': self.english_ease,
                'spanish': self.spanish_ease,
                'mandarin': self.mandarin_ease,
                'arabic': self.arabic_ease,
                'hindi': self.hindi_ease,
                'universal': self.universal_pronounceability
            }
        }


class PhoneticUniversals(db.Model):
    """
    Cross-linguistic phonetic universal patterns and sound symbolism.
    Tests Bouba/Kiki effect and other universal sound-meaning associations.
    """
    __tablename__ = 'phonetic_universals'
    __table_args__ = (
        db.Index('idx_phonetic_name', 'name'),
        db.Index('idx_phonetic_bouba_kiki', 'bouba_kiki_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    
    # Bouba-Kiki effect
    bouba_kiki_score = db.Column(db.Float)  # -1 (angular/kiki) to +1 (round/bouba)
    roundness_score = db.Column(db.Float)  # 0-1: perceived roundness
    angularity_score = db.Column(db.Float)  # 0-1: perceived angularity
    
    # Size sound symbolism
    size_symbolism_score = db.Column(db.Float)  # -1 (small) to +1 (large)
    high_vowel_frequency = db.Column(db.Float)  # High vowels → smallness
    low_vowel_frequency = db.Column(db.Float)  # Low vowels → largeness
    
    # Speed/motion symbolism
    speed_symbolism_score = db.Column(db.Float)  # -1 (slow) to +1 (fast)
    fricative_frequency = db.Column(db.Float)  # Fricatives → speed
    stop_frequency = db.Column(db.Float)  # Stops → abruptness
    
    # Emotional valence (universal)
    universal_valence = db.Column(db.Float)  # -1 (negative) to +1 (positive)
    pleasantness_score = db.Column(db.Float)  # 0-1: cross-culturally pleasant
    harshness_perception = db.Column(db.Float)  # 0-1: cross-culturally harsh
    
    # Phoneme-level symbolism
    sonorant_ratio = db.Column(db.Float)  # Sonorants = positive valence
    voiceless_ratio = db.Column(db.Float)  # Voiceless = negative valence
    front_vowel_ratio = db.Column(db.Float)  # Front vowels = smallness, brightness
    back_vowel_ratio = db.Column(db.Float)  # Back vowels = darkness, largeness
    
    # Cross-linguistic semantic associations
    brightness_score = db.Column(db.Float)  # -1 (dark) to +1 (bright)
    hardness_score = db.Column(db.Float)  # -1 (soft) to +1 (hard)
    wetness_score = db.Column(db.Float)  # -1 (dry) to +1 (wet)
    
    # Language family patterns
    germanic_pattern_fit = db.Column(db.Float)  # 0-1: fits Germanic phonology
    romance_pattern_fit = db.Column(db.Float)  # 0-1: fits Romance phonology
    slavic_pattern_fit = db.Column(db.Float)  # 0-1: fits Slavic phonology
    sinitic_pattern_fit = db.Column(db.Float)  # 0-1: fits Chinese phonology
    semitic_pattern_fit = db.Column(db.Float)  # 0-1: fits Arabic/Hebrew phonology
    
    # Phonotactic universals
    violates_universals = db.Column(db.Boolean)  # Any universal violations?
    universal_violations = db.Column(db.Text)  # JSON array of violations
    cross_linguistic_rarity = db.Column(db.Float)  # 0-1: how rare is this pattern?
    
    # Iconicity scores
    onomatopoeia_score = db.Column(db.Float)  # 0-1: sound-imitative quality
    iconicity_rating = db.Column(db.Float)  # 0-1: form-meaning transparency
    
    # Metadata
    analysis_languages = db.Column(db.Text)  # JSON array of languages analyzed
    confidence_score = db.Column(db.Float)  # Statistical confidence
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bouba_kiki': {
                'score': self.bouba_kiki_score,
                'roundness': self.roundness_score,
                'angularity': self.angularity_score
            },
            'size_symbolism': {
                'score': self.size_symbolism_score,
                'high_vowel_freq': self.high_vowel_frequency,
                'low_vowel_freq': self.low_vowel_frequency
            },
            'speed_symbolism': {
                'score': self.speed_symbolism_score,
                'fricative_freq': self.fricative_frequency,
                'stop_freq': self.stop_frequency
            },
            'emotional_valence': {
                'universal': self.universal_valence,
                'pleasantness': self.pleasantness_score,
                'harshness': self.harshness_perception
            },
            'phoneme_ratios': {
                'sonorant': self.sonorant_ratio,
                'voiceless': self.voiceless_ratio,
                'front_vowel': self.front_vowel_ratio,
                'back_vowel': self.back_vowel_ratio
            },
            'semantic_associations': {
                'brightness': self.brightness_score,
                'hardness': self.hardness_score,
                'wetness': self.wetness_score
            },
            'language_families': {
                'germanic': self.germanic_pattern_fit,
                'romance': self.romance_pattern_fit,
                'slavic': self.slavic_pattern_fit,
                'sinitic': self.sinitic_pattern_fit,
                'semitic': self.semitic_pattern_fit
            },
            'universals': {
                'violates': self.violates_universals,
                'violations': json.loads(self.universal_violations) if self.universal_violations else [],
                'rarity': self.cross_linguistic_rarity
            },
            'iconicity': {
                'onomatopoeia': self.onomatopoeia_score,
                'overall': self.iconicity_rating
            },
            'metadata': {
                'languages_analyzed': json.loads(self.analysis_languages) if self.analysis_languages else [],
                'confidence': self.confidence_score
            }
        }


class SoundSymbolism(db.Model):
    """
    Phoneme-to-meaning associations across cultures.
    Documents which sounds carry which meanings universally.
    """
    __tablename__ = 'sound_symbolism'
    __table_args__ = (
        db.Index('idx_sound_phoneme', 'phoneme'),
        db.Index('idx_sound_feature', 'phonetic_feature'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Phoneme identification
    phoneme = db.Column(db.String(20), nullable=False)  # IPA symbol
    phoneme_type = db.Column(db.String(50))  # 'vowel', 'consonant', 'diphthong'
    phonetic_feature = db.Column(db.String(100))  # 'front_vowel', 'fricative', 'stop', etc.
    
    # Symbolic associations
    symbolic_meanings = db.Column(db.Text)  # JSON array of associated meanings
    emotional_valence = db.Column(db.Float)  # -1 (negative) to +1 (positive)
    
    # Cross-cultural frequency
    cultures_observed = db.Column(db.Text)  # JSON array of cultures/languages
    observation_count = db.Column(db.Integer)  # Number of studies documenting this
    universality_score = db.Column(db.Float)  # 0-1: how universal is this association?
    
    # Specific associations
    size_association = db.Column(db.String(50))  # 'small', 'large', 'neutral'
    shape_association = db.Column(db.String(50))  # 'round', 'angular', 'neutral'
    texture_association = db.Column(db.String(50))  # 'smooth', 'rough', 'neutral'
    motion_association = db.Column(db.String(50))  # 'fast', 'slow', 'static', 'neutral'
    
    # Perceptual qualities
    brightness_association = db.Column(db.Float)  # -1 (dark) to +1 (bright)
    hardness_association = db.Column(db.Float)  # -1 (soft) to +1 (hard)
    temperature_association = db.Column(db.Float)  # -1 (cold) to +1 (warm)
    
    # Examples and evidence
    example_words = db.Column(db.Text)  # JSON array of words exemplifying association
    source_studies = db.Column(db.Text)  # JSON array of research citations
    
    # Statistical support
    effect_size = db.Column(db.Float)  # Statistical effect size
    confidence_interval = db.Column(db.String(100))  # CI for effect
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'phoneme': self.phoneme,
            'phoneme_type': self.phoneme_type,
            'phonetic_feature': self.phonetic_feature,
            'symbolic_meanings': json.loads(self.symbolic_meanings) if self.symbolic_meanings else [],
            'emotional_valence': self.emotional_valence,
            'universality': {
                'cultures': json.loads(self.cultures_observed) if self.cultures_observed else [],
                'observation_count': self.observation_count,
                'score': self.universality_score
            },
            'associations': {
                'size': self.size_association,
                'shape': self.shape_association,
                'texture': self.texture_association,
                'motion': self.motion_association
            },
            'perceptual': {
                'brightness': self.brightness_association,
                'hardness': self.hardness_association,
                'temperature': self.temperature_association
            },
            'evidence': {
                'examples': json.loads(self.example_words) if self.example_words else [],
                'studies': json.loads(self.source_studies) if self.source_studies else [],
                'effect_size': self.effect_size,
                'confidence_interval': self.confidence_interval
            }
        }


# =====================================================
# GOSPEL SUCCESS & RELIGIOUS TEXT ANALYSIS MODELS
# =====================================================

class ReligiousText(db.Model):
    """
    Religious texts (gospels, sutras, etc.) with metadata and composition analysis.
    """
    __tablename__ = 'religious_text'
    __table_args__ = (
        db.Index('idx_religious_text_name', 'text_name'),
        db.Index('idx_religious_tradition', 'religious_tradition'),
        db.Index('idx_religious_composition_date', 'composition_year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identification
    text_name = db.Column(db.String(300), nullable=False)  # "Gospel of Matthew", "Quran", etc.
    text_type = db.Column(db.String(100))  # 'gospel', 'sutra', 'surah', 'scripture'
    religious_tradition = db.Column(db.String(100))  # 'christianity', 'islam', 'buddhism', etc.
    sub_tradition = db.Column(db.String(200))  # 'catholic', 'orthodox', 'sunni', 'mahayana', etc.
    
    # Composition details
    author_attributed = db.Column(db.String(200))  # Attributed author
    composition_year = db.Column(db.Integer)  # Approximate year
    composition_location = db.Column(db.String(200))  # Where composed
    original_language = db.Column(db.String(100))  # Hebrew, Greek, Arabic, Sanskrit, etc.
    
    # Text characteristics
    total_words = db.Column(db.Integer)
    total_characters = db.Column(db.Integer)
    unique_character_names = db.Column(db.Integer)
    unique_place_names = db.Column(db.Integer)
    
    # Linguistic complexity
    lexical_diversity = db.Column(db.Float)  # Type-token ratio
    mean_word_length = db.Column(db.Float)
    mean_sentence_length = db.Column(db.Float)
    reading_level = db.Column(db.Float)  # Flesch-Kincaid or equivalent
    
    # Name composition patterns
    mean_name_syllables = db.Column(db.Float)
    mean_name_length = db.Column(db.Float)
    name_melodiousness = db.Column(db.Float)  # Average across all names
    name_complexity = db.Column(db.Float)
    foreign_name_ratio = db.Column(db.Float)  # Ratio of non-native names
    
    # Translation history
    major_translations = db.Column(db.Text)  # JSON array of major translation info
    translation_count = db.Column(db.Integer)  # Number of languages translated to
    first_translation_year = db.Column(db.Integer)
    
    # Content summary
    narrative_style = db.Column(db.String(200))  # 'chronological', 'thematic', 'poetic', etc.
    key_themes = db.Column(db.Text)  # JSON array of major themes
    miracle_count = db.Column(db.Integer)
    parable_count = db.Column(db.Integer)
    
    # Full text storage (optional)
    full_text = db.Column(db.Text)  # Complete text if available
    text_url = db.Column(db.String(500))  # Link to canonical version
    
    # Relationships
    success_metrics = db.relationship('ReligiousTextSuccessMetrics', backref='religious_text', lazy='dynamic', cascade='all, delete-orphan')
    regional_adoptions = db.relationship('RegionalAdoptionAnalysis', backref='religious_text', lazy='dynamic', cascade='all, delete-orphan')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text_name': self.text_name,
            'text_type': self.text_type,
            'religious_tradition': self.religious_tradition,
            'sub_tradition': self.sub_tradition,
            'composition': {
                'author': self.author_attributed,
                'year': self.composition_year,
                'location': self.composition_location,
                'original_language': self.original_language
            },
            'text_stats': {
                'total_words': self.total_words,
                'total_characters': self.total_characters,
                'unique_names': self.unique_character_names,
                'unique_places': self.unique_place_names
            },
            'linguistic': {
                'lexical_diversity': self.lexical_diversity,
                'mean_word_length': self.mean_word_length,
                'mean_sentence_length': self.mean_sentence_length,
                'reading_level': self.reading_level
            },
            'name_patterns': {
                'mean_syllables': self.mean_name_syllables,
                'mean_length': self.mean_name_length,
                'melodiousness': self.name_melodiousness,
                'complexity': self.name_complexity,
                'foreign_ratio': self.foreign_name_ratio
            },
            'translations': {
                'major': json.loads(self.major_translations) if self.major_translations else [],
                'count': self.translation_count,
                'first_year': self.first_translation_year
            },
            'content': {
                'narrative_style': self.narrative_style,
                'themes': json.loads(self.key_themes) if self.key_themes else [],
                'miracles': self.miracle_count,
                'parables': self.parable_count
            }
        }


class ReligiousTextSuccessMetrics(db.Model):
    """
    Success metrics for religious texts by region and time period.
    Tracks adherent populations, geographic spread, cultural influence.
    """
    __tablename__ = 'religious_text_success_metrics'
    __table_args__ = (
        db.Index('idx_success_text_region_year', 'religious_text_id', 'region', 'year'),
        db.Index('idx_success_adherents', 'adherent_population'),
        db.Index('idx_success_year', 'year'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    religious_text_id = db.Column(db.Integer, db.ForeignKey('religious_text.id'), nullable=False)
    
    # Geographic/temporal context
    region = db.Column(db.String(200))  # Geographic region
    country = db.Column(db.String(200))  # Specific country if applicable
    continent = db.Column(db.String(100))
    year = db.Column(db.Integer)  # Measurement year
    century = db.Column(db.Integer)  # For easier temporal queries
    
    # Population metrics
    adherent_population = db.Column(db.BigInteger)  # Number of adherents
    percentage_of_population = db.Column(db.Float)  # % of regional population
    growth_rate_annual = db.Column(db.Float)  # Annual growth rate
    conversion_rate = db.Column(db.Float)  # New conversions per year
    
    # Geographic spread
    geographic_area_km2 = db.Column(db.Float)  # Area where practiced
    number_of_countries = db.Column(db.Integer)  # How many countries
    spread_velocity_km_per_year = db.Column(db.Float)  # Speed of geographic expansion
    persistence_score = db.Column(db.Float)  # 0-1: how long maintained in region
    
    # Cultural influence
    art_influence_score = db.Column(db.Float)  # 0-1: influence on art/architecture
    literature_influence_score = db.Column(db.Float)  # 0-1: influence on literature
    legal_influence_score = db.Column(db.Float)  # 0-1: influence on legal systems
    educational_influence_score = db.Column(db.Float)  # 0-1: influence on education
    overall_cultural_influence = db.Column(db.Float)  # 0-1: composite score
    
    # Linguistic adoption
    biblical_names_popularity = db.Column(db.Float)  # 0-1: how popular are biblical names
    liturgical_language_adoption = db.Column(db.Float)  # 0-1: liturgical lang influence
    vernacular_translations = db.Column(db.Integer)  # Number of vernacular translations
    
    # Institutional presence
    places_of_worship = db.Column(db.Integer)  # Number of churches/mosques/temples
    religious_schools = db.Column(db.Integer)
    monasteries_seminaries = db.Column(db.Integer)
    
    # Historical events
    major_events = db.Column(db.Text)  # JSON array of significant events
    persecution_periods = db.Column(db.Text)  # JSON array of persecution events
    revival_movements = db.Column(db.Text)  # JSON array of revival movements
    
    # Decline/persistence factors
    is_declining = db.Column(db.Boolean)
    decline_rate = db.Column(db.Float)  # If declining
    persistence_factors = db.Column(db.Text)  # JSON array: why it persisted/declined
    
    # Data sources
    data_source = db.Column(db.String(500))  # Citation for data
    data_quality = db.Column(db.String(50))  # 'high', 'medium', 'low', 'estimated'
    confidence_score = db.Column(db.Float)  # 0-1: confidence in data
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': {
                'region': self.region,
                'country': self.country,
                'continent': self.continent
            },
            'time': {
                'year': self.year,
                'century': self.century
            },
            'population': {
                'adherents': self.adherent_population,
                'percentage': self.percentage_of_population,
                'growth_rate': self.growth_rate_annual,
                'conversion_rate': self.conversion_rate
            },
            'spread': {
                'area_km2': self.geographic_area_km2,
                'countries': self.number_of_countries,
                'velocity': self.spread_velocity_km_per_year,
                'persistence': self.persistence_score
            },
            'cultural_influence': {
                'art': self.art_influence_score,
                'literature': self.literature_influence_score,
                'legal': self.legal_influence_score,
                'education': self.educational_influence_score,
                'overall': self.overall_cultural_influence
            },
            'linguistic': {
                'name_popularity': self.biblical_names_popularity,
                'liturgical_adoption': self.liturgical_language_adoption,
                'translations': self.vernacular_translations
            },
            'institutions': {
                'worship_places': self.places_of_worship,
                'schools': self.religious_schools,
                'monasteries': self.monasteries_seminaries
            },
            'history': {
                'major_events': json.loads(self.major_events) if self.major_events else [],
                'persecutions': json.loads(self.persecution_periods) if self.persecution_periods else [],
                'revivals': json.loads(self.revival_movements) if self.revival_movements else []
            },
            'trends': {
                'is_declining': self.is_declining,
                'decline_rate': self.decline_rate,
                'persistence_factors': json.loads(self.persistence_factors) if self.persistence_factors else []
            },
            'metadata': {
                'source': self.data_source,
                'quality': self.data_quality,
                'confidence': self.confidence_score
            }
        }


class RegionalAdoptionAnalysis(db.Model):
    """
    Correlation analysis between text linguistic features and regional adoption success.
    Tests whether simpler names, more accessible language leads to faster/wider adoption.
    """
    __tablename__ = 'regional_adoption_analysis'
    __table_args__ = (
        db.Index('idx_adoption_text_region', 'religious_text_id', 'region'),
        db.Index('idx_adoption_success', 'adoption_success_score'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    religious_text_id = db.Column(db.Integer, db.ForeignKey('religious_text.id'), nullable=False)
    
    # Region details
    region = db.Column(db.String(200))
    country = db.Column(db.String(200))
    dominant_language_family = db.Column(db.String(100))  # What lang family is dominant here?
    
    # Adoption success measurement
    adoption_success_score = db.Column(db.Float)  # 0-1: composite adoption success
    peak_adherent_percentage = db.Column(db.Float)  # Peak % of population
    years_to_peak = db.Column(db.Integer)  # How long to reach peak
    current_adherent_percentage = db.Column(db.Float)  # Current % (if still practiced)
    
    # Linguistic compatibility factors
    name_accessibility_score = db.Column(db.Float)  # 0-1: how accessible are names?
    phonetic_compatibility = db.Column(db.Float)  # 0-1: text phonology vs local phonology
    translation_quality = db.Column(db.Float)  # 0-1: quality of local translation
    linguistic_distance = db.Column(db.Float)  # Edit distance from original language
    
    # Cultural fit factors
    cultural_fit_score = db.Column(db.Float)  # 0-1: how well text fits local culture
    naming_pattern_similarity = db.Column(db.Float)  # 0-1: text names vs local names
    conceptual_compatibility = db.Column(db.Float)  # 0-1: concepts match local worldview
    
    # Correlation analysis
    linguistic_success_correlation = db.Column(db.Float)  # Correlation coefficient
    name_simplicity_effect = db.Column(db.Float)  # Effect of name simplicity on adoption
    accessibility_effect = db.Column(db.Float)  # Effect of linguistic accessibility
    
    # Statistical significance
    p_value = db.Column(db.Float)
    confidence_interval = db.Column(db.String(100))
    sample_size = db.Column(db.Integer)
    
    # Confounding factors
    political_support_level = db.Column(db.Float)  # 0-1: government support
    missionary_activity_level = db.Column(db.Float)  # 0-1: missionary presence
    competing_religions = db.Column(db.Text)  # JSON array of competing traditions
    
    # Explanation
    success_factors = db.Column(db.Text)  # JSON array: why it succeeded/failed here
    linguistic_barriers = db.Column(db.Text)  # JSON array: linguistic obstacles
    linguistic_advantages = db.Column(db.Text)  # JSON array: linguistic benefits
    
    # Case study notes
    case_study_summary = db.Column(db.Text)  # Detailed analysis
    notable_examples = db.Column(db.Text)  # JSON array of specific examples
    
    # Metadata
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    analyst_notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'region': {
                'name': self.region,
                'country': self.country,
                'language_family': self.dominant_language_family
            },
            'adoption_success': {
                'overall_score': self.adoption_success_score,
                'peak_percentage': self.peak_adherent_percentage,
                'years_to_peak': self.years_to_peak,
                'current_percentage': self.current_adherent_percentage
            },
            'linguistic_factors': {
                'name_accessibility': self.name_accessibility_score,
                'phonetic_compatibility': self.phonetic_compatibility,
                'translation_quality': self.translation_quality,
                'linguistic_distance': self.linguistic_distance
            },
            'cultural_fit': {
                'overall': self.cultural_fit_score,
                'naming_similarity': self.naming_pattern_similarity,
                'conceptual_compatibility': self.conceptual_compatibility
            },
            'correlations': {
                'linguistic_success': self.linguistic_success_correlation,
                'name_simplicity_effect': self.name_simplicity_effect,
                'accessibility_effect': self.accessibility_effect
            },
            'statistics': {
                'p_value': self.p_value,
                'confidence_interval': self.confidence_interval,
                'sample_size': self.sample_size
            },
            'confounds': {
                'political_support': self.political_support_level,
                'missionary_activity': self.missionary_activity_level,
                'competing': json.loads(self.competing_religions) if self.competing_religions else []
            },
            'analysis': {
                'success_factors': json.loads(self.success_factors) if self.success_factors else [],
                'barriers': json.loads(self.linguistic_barriers) if self.linguistic_barriers else [],
                'advantages': json.loads(self.linguistic_advantages) if self.linguistic_advantages else [],
                'summary': self.case_study_summary,
                'examples': json.loads(self.notable_examples) if self.notable_examples else []
            }
        }


# =============================================================================
# SPORTS BETTING MODELS
# =============================================================================

class SportsBet(db.Model):
    """Immutable record of placed bets (like ForwardPrediction)"""
    __tablename__ = 'sports_bet'
    __table_args__ = (
        db.Index('idx_bet_sport', 'sport'),
        db.Index('idx_bet_status', 'bet_status'),
        db.Index('idx_bet_date', 'placed_at'),
        db.Index('idx_bet_sport_type', 'sport', 'bet_type'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Bet identification (LOCKED at creation)
    bet_id = db.Column(db.String(50), unique=True, nullable=False)
    sport = db.Column(db.String(50), nullable=False)  # 'football', 'basketball', 'baseball'
    bet_type = db.Column(db.String(50), nullable=False)  # 'player_prop', 'spread', 'moneyline', 'futures'
    market_type = db.Column(db.String(100))  # 'rushing_yards', 'points', 'MVP', etc.
    
    # Player/team information
    player_name = db.Column(db.String(200))
    team_name = db.Column(db.String(200))
    opponent_name = db.Column(db.String(200))
    
    # Bet details (LOCKED)
    market_line = db.Column(db.Float)  # The line/total
    bet_side = db.Column(db.String(20))  # 'over', 'under', 'home', 'away', etc.
    odds = db.Column(db.Integer)  # American odds
    stake = db.Column(db.Float, nullable=False)  # Bet amount
    
    # Prediction at bet time (LOCKED)
    predicted_value = db.Column(db.Float)
    confidence_score = db.Column(db.Float)  # 0-100
    expected_value = db.Column(db.Float)  # EV at time of bet
    linguistic_score = db.Column(db.Float)  # Name pattern score
    
    # Linguistic features (for analysis)
    syllables = db.Column(db.Float)
    harshness = db.Column(db.Float)
    memorability = db.Column(db.Float)
    name_length = db.Column(db.Integer)
    
    # Bankroll management
    bankroll_at_bet = db.Column(db.Float)
    bet_percentage = db.Column(db.Float)  # % of bankroll
    kelly_fraction = db.Column(db.Float)  # Kelly sizing used
    
    # Bet metadata
    placed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    game_date = db.Column(db.DateTime)  # When game occurs
    is_locked = db.Column(db.Boolean, default=True)  # Cannot modify after creation
    
    # Outcome (filled in after game)
    actual_result = db.Column(db.Float)  # Actual stat value
    bet_status = db.Column(db.String(20), default='pending')  # 'pending', 'won', 'lost', 'push', 'cancelled'
    payout = db.Column(db.Float)  # Total payout if won (including stake)
    profit = db.Column(db.Float)  # Net profit/loss
    roi = db.Column(db.Float)  # Return on investment %
    
    # Result metadata
    settled_at = db.Column(db.DateTime)
    closing_line = db.Column(db.Float)  # Line at game time (for CLV)
    closing_odds = db.Column(db.Integer)  # Odds at close
    clv = db.Column(db.Float)  # Closing Line Value (our line vs closing line)
    
    # Analysis
    edge_realized = db.Column(db.Boolean)  # Did predicted edge materialize?
    prediction_error = db.Column(db.Float)  # Predicted vs actual
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bet_id': self.bet_id,
            'sport': self.sport,
            'bet_type': self.bet_type,
            'market_type': self.market_type,
            'player_name': self.player_name,
            'team_name': self.team_name,
            'market_line': self.market_line,
            'bet_side': self.bet_side,
            'odds': self.odds,
            'stake': self.stake,
            'predicted_value': self.predicted_value,
            'confidence_score': self.confidence_score,
            'expected_value': self.expected_value,
            'linguistic_score': self.linguistic_score,
            'placed_at': self.placed_at.isoformat() if self.placed_at else None,
            'game_date': self.game_date.isoformat() if self.game_date else None,
            'bet_status': self.bet_status,
            'actual_result': self.actual_result,
            'payout': self.payout,
            'profit': self.profit,
            'roi': self.roi,
            'settled_at': self.settled_at.isoformat() if self.settled_at else None,
            'clv': self.clv
        }


class BankrollHistory(db.Model):
    """Track bankroll over time"""
    __tablename__ = 'bankroll_history'
    __table_args__ = (
        db.Index('idx_bankroll_timestamp', 'timestamp'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Bankroll state
    balance = db.Column(db.Float, nullable=False)
    allocated_capital = db.Column(db.Float, default=0)
    available_capital = db.Column(db.Float)
    peak_balance = db.Column(db.Float)
    
    # Performance metrics
    total_roi = db.Column(db.Float)  # Overall ROI %
    current_drawdown = db.Column(db.Float)  # Current drawdown %
    total_bets = db.Column(db.Integer, default=0)
    consecutive_losses = db.Column(db.Integer, default=0)
    
    # Risk status
    is_halted = db.Column(db.Boolean, default=False)  # Trading halted due to drawdown
    
    # Trigger event (what caused this snapshot)
    event_type = db.Column(db.String(50))  # 'bet_placed', 'bet_settled', 'deposit', 'withdrawal'
    event_id = db.Column(db.String(100))  # Reference to bet_id or transaction
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'balance': self.balance,
            'allocated_capital': self.allocated_capital,
            'available_capital': self.available_capital,
            'total_roi': self.total_roi,
            'current_drawdown': self.current_drawdown,
            'total_bets': self.total_bets,
            'is_halted': self.is_halted
        }


class BettingPerformance(db.Model):
    """Aggregate performance statistics"""
    __tablename__ = 'betting_performance'
    __table_args__ = (
        db.Index('idx_performance_sport_market', 'sport', 'market_type'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dimension of analysis
    sport = db.Column(db.String(50))  # NULL = overall
    market_type = db.Column(db.String(100))  # NULL = all markets
    time_period = db.Column(db.String(50))  # 'all_time', 'last_30_days', 'last_90_days', 'ytd'
    
    # Volume metrics
    total_bets = db.Column(db.Integer, default=0)
    total_staked = db.Column(db.Float, default=0)
    total_returned = db.Column(db.Float, default=0)
    
    # Win/loss record
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    pushes = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float)  # Decimal
    
    # Profitability
    net_profit = db.Column(db.Float, default=0)
    roi = db.Column(db.Float)  # %
    avg_profit_per_bet = db.Column(db.Float)
    
    # Expected value tracking
    avg_ev = db.Column(db.Float)  # Average EV of bets
    avg_clv = db.Column(db.Float)  # Average closing line value
    positive_clv_rate = db.Column(db.Float)  # % of bets with +CLV
    
    # Risk metrics
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)  # Worst drawdown %
    longest_losing_streak = db.Column(db.Integer)
    largest_loss = db.Column(db.Float)
    
    # Bet sizing
    avg_bet_size = db.Column(db.Float)
    avg_bet_percentage = db.Column(db.Float)  # % of bankroll
    
    # Last updated
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_bet_date = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'sport': self.sport,
            'market_type': self.market_type,
            'time_period': self.time_period,
            'total_bets': self.total_bets,
            'win_rate': round(self.win_rate * 100, 2) if self.win_rate else 0,
            'roi': round(self.roi, 2) if self.roi else 0,
            'net_profit': self.net_profit,
            'avg_ev': self.avg_ev,
            'avg_clv': self.avg_clv,
            'positive_clv_rate': round(self.positive_clv_rate * 100, 2) if self.positive_clv_rate else 0,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


