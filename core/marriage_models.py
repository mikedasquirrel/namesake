"""
Marriage Domain Models - Database schemas for relationship research

Models for storing couple data, relationship outcomes, and compatibility analysis.
Part of the Nominative Matchmaker research study.
"""

from core.models import db
from datetime import datetime
from sqlalchemy import Index


# =============================================================================
# MARRIED COUPLE DATA
# =============================================================================

class MarriedCouple(db.Model):
    """Married couple record with outcome data"""
    __tablename__ = 'married_couples'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Partner 1 (convention: listed first in record)
    partner1_first = db.Column(db.String(100), nullable=False, index=True)
    partner1_middle = db.Column(db.String(100))
    partner1_last_maiden = db.Column(db.String(100))
    partner1_last_married = db.Column(db.String(100))
    partner1_full_name = db.Column(db.String(300), index=True)
    
    # Partner 2
    partner2_first = db.Column(db.String(100), nullable=False, index=True)
    partner2_middle = db.Column(db.String(100))
    partner2_last_maiden = db.Column(db.String(100))
    partner2_last_married = db.Column(db.String(100))
    partner2_full_name = db.Column(db.String(300), index=True)
    
    # Marriage details
    marriage_date = db.Column(db.Date, index=True)
    marriage_year = db.Column(db.Integer, index=True)
    marriage_location_city = db.Column(db.String(100))
    marriage_location_state = db.Column(db.String(50))
    marriage_location_country = db.Column(db.String(50), default='USA')
    
    # Ages at marriage (critical control variable)
    partner1_age_at_marriage = db.Column(db.Integer)
    partner2_age_at_marriage = db.Column(db.Integer)
    age_difference = db.Column(db.Integer)  # Abs(age1 - age2)
    
    # Outcome variables
    relationship_status = db.Column(db.String(20), index=True)  # married/divorced/widowed
    divorce_date = db.Column(db.Date)
    divorce_year = db.Column(db.Integer, index=True)
    marriage_duration_years = db.Column(db.Float, index=True)  # Years together
    
    # Success metrics
    is_divorced = db.Column(db.Boolean, default=False, index=True)
    is_long_term = db.Column(db.Boolean, default=False)  # 10+ years
    is_very_long_term = db.Column(db.Boolean, default=False)  # 20+ years
    
    # Surname patterns (research variable)
    surname_pattern = db.Column(db.String(50))  # traditional/hyphenated/separate/reversed
    hyphenated_surname = db.Column(db.String(200))  # If applicable
    
    # Children (for sub-analysis)
    has_children = db.Column(db.Boolean)
    child_count = db.Column(db.Integer)
    
    # Control variables
    cohort_era = db.Column(db.String(20), index=True)  # 1980s/1990s/2000s/2010s/2020s
    geographic_region = db.Column(db.String(50))  # Northeast/South/Midwest/West
    urban_rural = db.Column(db.String(20))  # urban/suburban/rural
    
    # Data source metadata
    data_source = db.Column(db.String(50))  # public_records/celebrity/historical
    source_reliability = db.Column(db.Float)  # 0-1 confidence score
    
    # Collection metadata
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)
    collector_version = db.Column(db.String(20))
    
    # Relationships
    analysis = db.relationship('MarriageAnalysis', backref='couple', uselist=False, cascade='all, delete-orphan')
    children = db.relationship('ChildName', backref='parents', cascade='all, delete-orphan')
    
    # Indices for common queries
    __table_args__ = (
        Index('idx_marriage_outcome', 'is_divorced', 'marriage_duration_years'),
        Index('idx_era_outcome', 'cohort_era', 'is_divorced'),
        Index('idx_age_outcome', 'partner1_age_at_marriage', 'partner2_age_at_marriage', 'is_divorced'),
    )
    
    def calculate_derived_fields(self):
        """Calculate derived fields after data entry"""
        # Calculate ages if birthdates available
        if self.partner1_age_at_marriage and self.partner2_age_at_marriage:
            self.age_difference = abs(self.partner1_age_at_marriage - self.partner2_age_at_marriage)
        
        # Calculate duration
        if self.marriage_date:
            if self.divorce_date:
                delta = self.divorce_date - self.marriage_date
                self.marriage_duration_years = delta.days / 365.25
                self.is_divorced = True
            else:
                # Ongoing marriage
                delta = datetime.now().date() - self.marriage_date
                self.marriage_duration_years = delta.days / 365.25
                self.is_divorced = False
        
        # Long-term flags
        if self.marriage_duration_years:
            self.is_long_term = self.marriage_duration_years >= 10.0
            self.is_very_long_term = self.marriage_duration_years >= 20.0
        
        # Cohort era
        if self.marriage_year:
            if self.marriage_year < 1990:
                self.cohort_era = '1980s'
            elif self.marriage_year < 2000:
                self.cohort_era = '1990s'
            elif self.marriage_year < 2010:
                self.cohort_era = '2000s'
            elif self.marriage_year < 2020:
                self.cohort_era = '2010s'
            else:
                self.cohort_era = '2020s'
        
        # Full names
        self.partner1_full_name = f"{self.partner1_first} {self.partner1_middle or ''} {self.partner1_last_married or self.partner1_last_maiden or ''}".strip()
        self.partner2_full_name = f"{self.partner2_first} {self.partner2_middle or ''} {self.partner2_last_married or self.partner2_last_maiden or ''}".strip()


# =============================================================================
# MARRIAGE NAME COMPATIBILITY ANALYSIS
# =============================================================================

class MarriageAnalysis(db.Model):
    """Nominative determinism analysis of married couple names"""
    __tablename__ = 'marriage_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('married_couples.id'), unique=True, nullable=False)
    
    # =================================================================
    # INDIVIDUAL NAME FEATURES (Partner 1)
    # =================================================================
    
    # Partner 1 - Phonetic
    p1_syllable_count = db.Column(db.Integer)
    p1_character_length = db.Column(db.Integer)
    p1_harshness_score = db.Column(db.Float)
    p1_smoothness_score = db.Column(db.Float)
    p1_memorability_score = db.Column(db.Float)
    p1_pronounceability = db.Column(db.Float)
    p1_vowel_ratio = db.Column(db.Float)
    
    # Partner 1 - Semantic
    p1_name_type = db.Column(db.String(50))
    p1_cultural_origin = db.Column(db.String(50))
    p1_uniqueness_score = db.Column(db.Float)
    
    # =================================================================
    # INDIVIDUAL NAME FEATURES (Partner 2)
    # =================================================================
    
    # Partner 2 - Phonetic
    p2_syllable_count = db.Column(db.Integer)
    p2_character_length = db.Column(db.Integer)
    p2_harshness_score = db.Column(db.Float)
    p2_smoothness_score = db.Column(db.Float)
    p2_memorability_score = db.Column(db.Float)
    p2_pronounceability = db.Column(db.Float)
    p2_vowel_ratio = db.Column(db.Float)
    
    # Partner 2 - Semantic
    p2_name_type = db.Column(db.String(50))
    p2_cultural_origin = db.Column(db.String(50))
    p2_uniqueness_score = db.Column(db.Float)
    
    # =================================================================
    # PAIRWISE INTERACTION FEATURES (THE CORE ANALYSIS)
    # =================================================================
    
    # Visual/geometric compatibility (from original formula engine)
    compatibility_score = db.Column(db.Float, index=True)
    distance_score = db.Column(db.Float)
    resonance_score = db.Column(db.Float)
    balance_score = db.Column(db.Float)
    
    # Golden ratio test
    golden_ratio_proximity = db.Column(db.Float, index=True)
    syllable_ratio = db.Column(db.Float)
    syllable_ratio_to_phi = db.Column(db.Float)
    
    # Color/harmonic theory
    color_harmony = db.Column(db.Float)
    complexity_balance = db.Column(db.Float)
    symmetry_match = db.Column(db.Float)
    
    # NEW: Advanced phonetic interactions
    phonetic_distance = db.Column(db.Float, index=True)
    vowel_harmony = db.Column(db.Float)
    consonant_compatibility = db.Column(db.Float)
    stress_alignment = db.Column(db.Float)
    
    # NEW: Cultural/social alignment
    cultural_origin_match = db.Column(db.Float)
    social_class_alignment = db.Column(db.Float)
    
    # Relationship pattern classification
    relationship_type = db.Column(db.String(50))  # harmonic/complementary/discordant/resonant/neutral
    
    # =================================================================
    # THEORY-SPECIFIC SCORES
    # =================================================================
    
    # Theory 1: Similarity (similar → compatible)
    similarity_theory_score = db.Column(db.Float)
    
    # Theory 2: Complementarity (opposite → balance)
    complementarity_theory_score = db.Column(db.Float)
    
    # Theory 3: Golden Ratio (φ → harmony)
    golden_ratio_theory_score = db.Column(db.Float)
    
    # Theory 4: Resonance (harmonic ratios → success)
    resonance_theory_score = db.Column(db.Float)
    
    # =================================================================
    # PREDICTED OUTCOMES (LOCKED BEFORE SEEING ACTUAL)
    # =================================================================
    
    predicted_compatibility = db.Column(db.Float)  # 0-1
    predicted_divorce_risk = db.Column(db.Float)  # 0-1
    predicted_longevity_years = db.Column(db.Float)
    prediction_confidence = db.Column(db.Float)  # 0-1
    
    # =================================================================
    # RELATIVE SUCCESS CALCULATION
    # =================================================================
    
    # Baseline expectations (from cohort data)
    expected_divorce_rate = db.Column(db.Float)  # Based on age/era/location
    expected_marriage_duration = db.Column(db.Float)  # Median for cohort
    
    # Relative success (actual / expected)
    relative_success_score = db.Column(db.Float, index=True)
    exceeds_expectations = db.Column(db.Boolean)
    
    # =================================================================
    # METADATA
    # =================================================================
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    analyzer_version = db.Column(db.String(20))
    formula_id = db.Column(db.String(50))  # Which formula was used


# =============================================================================
# CHILDREN'S NAMES (Sub-analysis)
# =============================================================================

class ChildName(db.Model):
    """Children's names for parent-child name pattern analysis"""
    __tablename__ = 'child_names'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('married_couples.id'), nullable=False)
    
    # Child name details
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    full_name = db.Column(db.String(300))
    
    # Birth details (if available)
    birth_year = db.Column(db.Integer)
    birth_order = db.Column(db.Integer)  # 1st child, 2nd child, etc.
    
    # Linguistic analysis
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    name_type = db.Column(db.String(50))
    
    # Pattern analysis (relative to parents)
    similarity_to_parent1 = db.Column(db.Float)  # 0-1
    similarity_to_parent2 = db.Column(db.Float)  # 0-1
    blending_score = db.Column(db.Float)  # Is it between parents?
    innovation_score = db.Column(db.Float)  # How creative/unique?
    
    # Which parent's style dominates?
    dominant_parent = db.Column(db.String(10))  # partner1/partner2/balanced
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# COHORT BASELINES (for relative success calculation)
# =============================================================================

class DivorceBaseline(db.Model):
    """Baseline divorce rates by cohort for relative success calculation"""
    __tablename__ = 'divorce_baselines'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Cohort definition
    marriage_year_start = db.Column(db.Integer, index=True)
    marriage_year_end = db.Column(db.Integer, index=True)
    age_bracket = db.Column(db.String(20), index=True)  # 18-24, 25-29, 30-34, 35+
    geographic_region = db.Column(db.String(50))  # USA regions
    urban_rural = db.Column(db.String(20))  # urban/rural
    
    # Baseline statistics
    sample_size = db.Column(db.Integer)
    divorce_rate = db.Column(db.Float)  # Proportion divorced
    median_marriage_duration = db.Column(db.Float)  # Years
    median_divorce_timing = db.Column(db.Float)  # Years until divorce (if divorced)
    
    # Confidence intervals
    divorce_rate_ci_lower = db.Column(db.Float)
    divorce_rate_ci_upper = db.Column(db.Float)
    
    # Data source
    data_source = db.Column(db.String(100))  # Census, CDC, etc.
    year_published = db.Column(db.Integer)
    
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cohort_lookup', 'marriage_year_start', 'marriage_year_end', 'age_bracket', 'geographic_region'),
    )


# =============================================================================
# CELEBRITY MARRIAGES (Sub-dataset with extra quality indicators)
# =============================================================================

class CelebrityMarriage(db.Model):
    """Celebrity marriages with additional quality/satisfaction indicators"""
    __tablename__ = 'celebrity_marriages'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('married_couples.id'), unique=True)
    
    # Celebrity details
    celebrity_name = db.Column(db.String(200))  # Who is the celebrity?
    celebrity_type = db.Column(db.String(50))  # actor/musician/politician/athlete/business
    fame_level = db.Column(db.String(20))  # A-list/B-list/C-list/public-figure
    
    # Additional quality indicators (where available)
    public_conflicts = db.Column(db.Integer)  # Count of publicized conflicts
    positive_media_mentions = db.Column(db.Integer)  # Positive press
    joint_appearances = db.Column(db.Integer)  # Public appearances together
    
    # Divorce details (often more complete for celebrities)
    divorce_litigation_intensity = db.Column(db.String(20))  # low/medium/high/contentious
    custody_disputes = db.Column(db.Boolean)
    prenup_disclosed = db.Column(db.Boolean)
    
    # Data sources (celebrities have multiple)
    wikipedia_url = db.Column(db.String(300))
    imdb_url = db.Column(db.String(300))
    news_article_count = db.Column(db.Integer)
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# PREDICTION AUDIT TRAIL (for blind testing)
# =============================================================================

class PredictionLock(db.Model):
    """Locked predictions BEFORE seeing outcomes (scientific rigor)"""
    __tablename__ = 'prediction_locks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Batch information
    batch_id = db.Column(db.String(50), index=True)  # Group predictions together
    locked_timestamp = db.Column(db.DateTime, nullable=False, index=True)
    predictor_version = db.Column(db.String(20))
    
    # Couple identifier (NOT outcome)
    couple_id = db.Column(db.Integer, db.ForeignKey('married_couples.id'))
    partner1_name = db.Column(db.String(300))  # For reference
    partner2_name = db.Column(db.String(300))
    
    # LOCKED PREDICTIONS (before outcome revealed)
    predicted_compatibility = db.Column(db.Float)
    predicted_divorce_probability = db.Column(db.Float)
    predicted_longevity_years = db.Column(db.Float)
    dominant_theory = db.Column(db.String(50))  # Which theory predicts best?
    
    # ACTUAL OUTCOMES (filled in later, after predictions locked)
    actual_is_divorced = db.Column(db.Boolean)
    actual_marriage_duration = db.Column(db.Float)
    outcomes_revealed_timestamp = db.Column(db.DateTime)
    
    # MATCH SCORES (calculated after reveal)
    compatibility_match_score = db.Column(db.Float)  # 0-1
    divorce_prediction_correct = db.Column(db.Boolean)
    longevity_prediction_error = db.Column(db.Float)  # Abs(predicted - actual)
    overall_prediction_accuracy = db.Column(db.Float)  # 0-1
    
    __table_args__ = (
        Index('idx_batch_timestamp', 'batch_id', 'locked_timestamp'),
    )

