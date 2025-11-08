"""
Expansion Models - Database Models for New Domains

Defines database schemas for 15 new research domains being added to the
Formula Evolution Engine for comprehensive nominative determinism testing.
"""

from core.models import db
from datetime import datetime


# =============================================================================
# YOUTUBE CHANNELS
# =============================================================================

class YouTubeChannel(db.Model):
    """YouTube channel data"""
    __tablename__ = 'youtube_channels'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    channel_url = db.Column(db.String(300))
    
    # Metrics (outcomes)
    subscriber_count = db.Column(db.Integer, index=True)
    total_views = db.Column(db.BigInteger)
    video_count = db.Column(db.Integer)
    average_views_per_video = db.Column(db.Integer)
    
    # Categorization
    category = db.Column(db.String(50), index=True)
    created_year = db.Column(db.Integer)
    country = db.Column(db.String(50))
    
    # Success indicators
    verified = db.Column(db.Boolean, default=False)
    monetized = db.Column(db.Boolean)
    
    # Metadata
    description = db.Column(db.Text)
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class YouTubeChannelAnalysis(db.Model):
    """Linguistic analysis of YouTube channel names"""
    __tablename__ = 'youtube_channel_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(50), db.ForeignKey('youtube_channels.id'), unique=True)
    
    # Standard suite
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic
    harshness_score = db.Column(db.Float)
    smoothness_score = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    plosive_ratio = db.Column(db.Float)
    
    # Semantic
    name_type = db.Column(db.String(50))
    brandability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    tech_association = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# STARTUPS / COMPANIES
# =============================================================================

class Startup(db.Model):
    """Startup company data"""
    __tablename__ = 'startups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    website = db.Column(db.String(300))
    
    # Outcomes
    total_funding = db.Column(db.Float, index=True)  # USD millions
    valuation = db.Column(db.Float)  # USD millions
    employee_count = db.Column(db.Integer)
    
    # Classification
    industry = db.Column(db.String(100), index=True)
    founded_year = db.Column(db.Integer)
    stage = db.Column(db.String(50))  # seed, series_a, etc.
    
    # Success indicators
    is_unicorn = db.Column(db.Boolean, default=False)
    ipo_status = db.Column(db.String(20))
    acquired = db.Column(db.Boolean, default=False)
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class StartupAnalysis(db.Model):
    """Linguistic analysis of startup names"""
    __tablename__ = 'startup_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), unique=True)
    
    # Standard suite
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    
    # Semantic
    name_type = db.Column(db.String(50))
    brandability_score = db.Column(db.Float)
    innovation_score = db.Column(db.Float)
    tech_association = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# PODCASTS
# =============================================================================

class Podcast(db.Model):
    """Podcast data"""
    __tablename__ = 'podcasts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    url = db.Column(db.String(300))
    
    # Outcomes
    subscriber_count = db.Column(db.Integer, index=True)
    average_downloads = db.Column(db.Integer)
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    
    # Classification
    category = db.Column(db.String(100), index=True)
    launch_year = db.Column(db.Integer)
    episode_count = db.Column(db.Integer)
    frequency = db.Column(db.String(20))  # daily, weekly, etc.
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class PodcastAnalysis(db.Model):
    """Linguistic analysis of podcast names"""
    __tablename__ = 'podcast_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    podcast_id = db.Column(db.Integer, db.ForeignKey('podcasts.id'), unique=True)
    
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    conversational_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# VIDEO GAMES
# =============================================================================

class VideoGame(db.Model):
    """Video game data"""
    __tablename__ = 'video_games'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    
    # Outcomes
    metacritic_score = db.Column(db.Float, index=True)
    user_score = db.Column(db.Float)
    copies_sold = db.Column(db.Integer)
    revenue = db.Column(db.Float)  # USD millions
    
    # Classification
    genre = db.Column(db.String(100), index=True)
    platform = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    developer = db.Column(db.String(200))
    
    # Success indicators
    game_of_year = db.Column(db.Boolean, default=False)
    franchise = db.Column(db.Boolean, default=False)
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class VideoGameAnalysis(db.Model):
    """Linguistic analysis of video game names"""
    __tablename__ = 'video_game_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('video_games.id'), unique=True)
    
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    fantasy_score = db.Column(db.Float)
    action_score = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# CEOS / BUSINESS LEADERS
# =============================================================================

class CEO(db.Model):
    """CEO/Business leader data"""
    __tablename__ = 'ceos'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    
    # Company association
    company_name = db.Column(db.String(200))
    company_ticker = db.Column(db.String(10))
    
    # Outcomes
    company_market_cap = db.Column(db.Float, index=True)  # USD billions
    tenure_years = db.Column(db.Float)
    stock_performance = db.Column(db.Float)  # % change during tenure
    
    # Classification
    industry = db.Column(db.String(100), index=True)
    appointment_year = db.Column(db.Integer)
    still_active = db.Column(db.Boolean, default=True)
    
    # Success indicators
    fortune_500 = db.Column(db.Boolean, default=False)
    awards = db.Column(db.Text)  # JSON list
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class CEOAnalysis(db.Model):
    """Linguistic analysis of CEO names"""
    __tablename__ = 'ceo_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    ceo_id = db.Column(db.Integer, db.ForeignKey('ceos.id'), unique=True)
    
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # Phonetic
    authority_score = db.Column(db.Float)
    prestige_score = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    power_connotation_score = db.Column(db.Float)
    
    # Name structure
    first_name_syllables = db.Column(db.Integer)
    last_name_syllables = db.Column(db.Integer)
    name_origin = db.Column(db.String(50))
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# Add similar model pairs for remaining domains:
# - Tennis, TennisAnalysis
# - Soccer, SoccerAnalysis  
# - Musician, MusicianAnalysis
# - Author, AuthorAnalysis
# - Scientist, ScientistAnalysis
# - Restaurant, RestaurantAnalysis
# - Brand, BrandAnalysis
# - City, CityAnalysis
# - PharmaDrug, PharmaDrugAnalysis
# - Boxer, BoxerAnalysis
# =============================================================================


def create_expansion_tables():
    """Create all expansion domain tables"""
    logger = logging.getLogger(__name__)
    
    from app import app
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        logger.info("Expansion domain tables created:")
        logger.info("  - youtube_channels, youtube_channel_analyses")
        logger.info("  - startups, startup_analyses")
        logger.info("  - podcasts, podcast_analyses")
        logger.info("  - video_games, video_game_analyses")
        logger.info("  - ceos, ceo_analyses")

