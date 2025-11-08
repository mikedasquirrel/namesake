"""
Podcast Models for Visual vs Non-Visual Entertainment Contrast
Tests hypothesis: Names matter more when performance isn't visible
"""

from datetime import datetime
from core.models import db


class Podcast(db.Model):
    """Podcast show data - non-visual entertainment contrast"""
    __tablename__ = 'podcasts'
    __table_args__ = (
        db.Index('idx_podcast_chart_rank', 'chart_rank'),
        db.Index('idx_podcast_downloads', 'total_downloads'),
        db.Index('idx_podcast_genre', 'primary_genre'),
    )
    
    id = db.Column(db.String(100), primary_key=True)
    podcast_name = db.Column(db.String(300), nullable=False, index=True)
    host_names = db.Column(db.Text)  # JSON list of host names
    primary_host = db.Column(db.String(200))  # Main host for analysis
    
    # Authenticity tracking (CRITICAL)
    host_uses_real_name = db.Column(db.Boolean, default=True)  # vs pseudonym
    podcast_name_type = db.Column(db.String(50))  # 'host_based', 'topical', 'creative', 'brand'
    name_matches_host = db.Column(db.Boolean)  # "Joe Rogan Experience" = True
    
    # Language and Accent (NEW dimensions)
    has_accent_marks = db.Column(db.Boolean, default=False)  # José, María, etc.
    language_origin = db.Column(db.String(50))  # anglo, latino, asian, european, african
    is_anglicized = db.Column(db.Boolean)  # José → Joe pattern
    cross_linguistic = db.Column(db.Boolean)  # International-sounding
    
    # Career metrics
    launch_year = db.Column(db.Integer, index=True)
    years_active = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    
    # Success metrics (NON-VISUAL proxies)
    total_downloads = db.Column(db.BigInteger)  # Can't see, must choose by name/description
    subscriber_count = db.Column(db.Integer)
    episode_count = db.Column(db.Integer)
    avg_rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    chart_rank = db.Column(db.Integer, index=True)  # Best rank achieved
    
    # Platform presence
    on_apple_podcasts = db.Column(db.Boolean, default=False)
    on_spotify = db.Column(db.Boolean, default=False)
    on_youtube = db.Column(db.Boolean, default=False)
    
    # Genre/Category
    primary_genre = db.Column(db.String(50))
    genres = db.Column(db.Text)  # JSON list
    
    # Computed success scores
    popularity_score = db.Column(db.Float)  # Based on downloads/subscribers
    longevity_score = db.Column(db.Float)  # Based on years active
    recognition_score = db.Column(db.Float)  # Based on ratings/reviews
    overall_success_score = db.Column(db.Float, index=True)
    
    # Source metadata
    source = db.Column(db.String(50))
    data_quality = db.Column(db.String(20))
    last_updated = db.Column(db.DateTime)
    
    # Relationship
    analysis = db.relationship('PodcastAnalysis', backref='podcast', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Podcast {self.podcast_name}>'


class PodcastAnalysis(db.Model):
    """Linguistic analysis of podcast names - testing non-visual nominative effects"""
    __tablename__ = 'podcast_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    podcast_id = db.Column(db.String(100), db.ForeignKey('podcasts.id'), nullable=False, unique=True)
    
    # Standard phonetic features (for podcast name)
    syllable_count = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    
    harshness_score = db.Column(db.Float)
    softness_score = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    pronounceability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    brand_strength_score = db.Column(db.Float)
    
    # Phonetic details
    plosive_ratio = db.Column(db.Float)
    vowel_ratio = db.Column(db.Float)
    liquid_ratio = db.Column(db.Float)
    alliteration_score = db.Column(db.Float)
    
    # Host name analysis (separate from podcast name)
    host_syllable_count = db.Column(db.Integer)
    host_memorability = db.Column(db.Float)
    host_pronounceability = db.Column(db.Float)
    
    # Authenticity metrics (NEW)
    authenticity_score = db.Column(db.Float)  # How "real" vs constructed
    ethnic_signal_strength = db.Column(db.Float)  # How strongly ethnic identity signals
    anglicization_degree = db.Column(db.Float)  # 0=fully authentic, 100=fully anglicized
    
    # Language/Accent features (NEW)
    accent_mark_count = db.Column(db.Integer)  # Number of á, é, í, etc.
    non_english_phonemes = db.Column(db.Boolean)  # Has sounds not in English
    language_family = db.Column(db.String(50))  # Romance, Germanic, Asian, etc.
    
    # Individual differentiation (NEW - within competitive set)
    distinctiveness_score = db.Column(db.Float)  # How unique in genre
    phonetic_distance_from_competitors = db.Column(db.Float)  # Avg distance from similar podcasts
    memorability_advantage = db.Column(db.Float)  # Relative to genre average
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PodcastAnalysis for podcast_id={self.podcast_id}>'

