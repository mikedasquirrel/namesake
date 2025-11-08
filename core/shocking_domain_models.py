"""
Shocking Domain Models - The Reality-Breaking Data

Database models for domains that test whether nominative determinism
affects the most intimate human choices: marriage, children, pets, friendships.

IF PATTERNS EMERGE: Free will is questionable.
"""

from core.models import db
from datetime import datetime


# =============================================================================
# MARRIAGE & DIVORCE
# =============================================================================

class MarriageRecord(db.Model):
    """Marriage and divorce data"""
    __tablename__ = 'marriage_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Partners
    person1_name = db.Column(db.String(200), nullable=False, index=True)
    person2_name = db.Column(db.String(200), nullable=False, index=True)
    
    # Outcome
    status = db.Column(db.String(20), index=True)  # 'married', 'divorced', 'widowed'
    marriage_date = db.Column(db.Date)
    end_date = db.Column(db.Date)  # Divorce or death
    duration_years = db.Column(db.Float, index=True)
    
    # Context
    marriage_location = db.Column(db.String(100))
    both_first_marriage = db.Column(db.Boolean)
    has_children = db.Column(db.Boolean)
    
    # Celebrity status (easier to verify)
    is_celebrity = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(100))  # Where data came from
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'person1': self.person1_name,
            'person2': self.person2_name,
            'status': self.status,
            'duration_years': self.duration_years
        }


class MarriageCompatibilityAnalysis(db.Model):
    """Relationship formula analysis of marriage"""
    __tablename__ = 'marriage_compatibility_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    marriage_id = db.Column(db.Integer, db.ForeignKey('marriage_records.id'), unique=True)
    
    # Compatibility metrics
    compatibility_score = db.Column(db.Float, index=True)
    distance_score = db.Column(db.Float)
    resonance_score = db.Column(db.Float)
    balance_score = db.Column(db.Float)
    
    # Special tests
    golden_ratio_proximity = db.Column(db.Float, index=True)
    color_harmony = db.Column(db.Float)
    complexity_balance = db.Column(db.Float)
    
    # Classification
    relationship_type = db.Column(db.String(50))  # harmonic/complementary/discordant
    
    # Prediction
    predicted_divorce_risk = db.Column(db.Float, index=True)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# PARENT-CHILD NAMING
# =============================================================================

class ParentChildRecord(db.Model):
    """Parent and child name relationships"""
    __tablename__ = 'parent_child_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Names
    mother_name = db.Column(db.String(200), index=True)
    father_name = db.Column(db.String(200), index=True)
    child_name = db.Column(db.String(200), nullable=False, index=True)
    
    # Child info
    child_birth_year = db.Column(db.Integer)
    child_gender = db.Column(db.String(10))
    birth_order = db.Column(db.Integer)  # 1st child, 2nd child, etc.
    
    # Context
    location = db.Column(db.String(100))
    cultural_background = db.Column(db.String(50))
    
    # Verification
    is_celebrity = db.Column(db.Boolean, default=False)
    source = db.Column(db.String(100))
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class ParentChildNamingAnalysis(db.Model):
    """Analysis of naming inheritance patterns"""
    __tablename__ = 'parent_child_naming_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('parent_child_records.id'), unique=True)
    
    # Inheritance scores (how much does child inherit from parents?)
    phonetic_inheritance = db.Column(db.Float)  # 0-1
    visual_inheritance = db.Column(db.Float)  # 0-1
    semantic_inheritance = db.Column(db.Float)  # 0-1
    
    # Specific patterns
    mother_similarity = db.Column(db.Float)  # How similar to mother
    father_similarity = db.Column(db.Float)  # How similar to father
    blend_score = db.Column(db.Float)  # Is it a blend or dominant?
    
    # Prediction accuracy
    predicted_hue = db.Column(db.Float)
    actual_hue = db.Column(db.Float)
    prediction_error = db.Column(db.Float)
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# PET OWNERSHIP
# =============================================================================

class PetOwnerRecord(db.Model):
    """Pet ownership data"""
    __tablename__ = 'pet_owner_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Owner
    owner_name = db.Column(db.String(200), nullable=False, index=True)
    
    # Pet
    pet_name = db.Column(db.String(200), nullable=False, index=True)
    pet_type = db.Column(db.String(50), index=True)  # dog/cat/bird/reptile/fish/other
    pet_breed = db.Column(db.String(100))
    
    # Context
    owner_age = db.Column(db.Integer)
    owner_gender = db.Column(db.String(10))
    location = db.Column(db.String(100))
    
    # Verification
    source = db.Column(db.String(100))  # instagram/reddit/registry
    verified = db.Column(db.Boolean, default=False)
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class PetCompatibilityAnalysis(db.Model):
    """Analysis of owner-pet name relationship"""
    __tablename__ = 'pet_compatibility_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('pet_owner_records.id'), unique=True)
    
    # Pattern type
    pattern_type = db.Column(db.String(50))  # compensatory/extension/completion
    
    # Scores
    similarity_score = db.Column(db.Float)  # How similar are the names?
    projection_score = db.Column(db.Float)  # Is this psychological projection?
    completion_score = db.Column(db.Float)  # Does pet complete owner pattern?
    
    # Specific tests
    harshness_relationship = db.Column(db.String(50))  # same/opposite/neutral
    complexity_relationship = db.Column(db.String(50))
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


class PetTypePredictor(db.Model):
    """Prediction: Owner name → Pet type"""
    __tablename__ = 'pet_type_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Owner name pattern
    owner_name_pattern = db.Column(db.String(50))  # cluster ID
    
    # Predicted preferences
    dog_probability = db.Column(db.Float)
    cat_probability = db.Column(db.Float)
    other_probability = db.Column(db.Float)
    
    # Accuracy tracking
    n_predictions = db.Column(db.Integer)
    accuracy = db.Column(db.Float)
    
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# FRIENDSHIP NETWORKS
# =============================================================================

class FriendshipRecord(db.Model):
    """Best friend pair data"""
    __tablename__ = 'friendship_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Friends
    person1_name = db.Column(db.String(200), nullable=False, index=True)
    person2_name = db.Column(db.String(200), nullable=False, index=True)
    
    # Strength
    friendship_duration_years = db.Column(db.Integer)
    friendship_strength = db.Column(db.String(20))  # 'best', 'close', 'casual'
    
    # Context
    met_context = db.Column(db.String(100))  # school/work/online
    age_met = db.Column(db.Integer)
    
    # Verification
    source = db.Column(db.String(100))
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class FriendshipCompatibilityAnalysis(db.Model):
    """Analysis of friendship name patterns"""
    __tablename__ = 'friendship_compatibility_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    friendship_id = db.Column(db.Integer, db.ForeignKey('friendship_records.id'), unique=True)
    
    # Compatibility
    name_similarity = db.Column(db.Float)
    visual_similarity = db.Column(db.Float)
    phonetic_similarity = db.Column(db.Float)
    
    # Compared to random pairs
    similarity_vs_random = db.Column(db.Float)  # Are BFFs more similar than chance?
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# NAME CHANGES & LIFE OUTCOMES
# =============================================================================

class NameChangeRecord(db.Model):
    """Legal name changes with before/after outcomes"""
    __tablename__ = 'name_change_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Names
    original_name = db.Column(db.String(200), nullable=False, index=True)
    new_name = db.Column(db.String(200), nullable=False, index=True)
    
    # Change details
    change_date = db.Column(db.Date)
    reason = db.Column(db.String(100))  # marriage/divorce/trans/preference/other
    
    # Outcomes (if trackable)
    income_before = db.Column(db.Float)
    income_after = db.Column(db.Float)
    career_success_before = db.Column(db.Float)  # 0-10 scale
    career_success_after = db.Column(db.Float)
    
    # Changes
    years_after = db.Column(db.Integer)  # Years of follow-up data
    
    # Context
    age_at_change = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class NameChangeAnalysis(db.Model):
    """Analysis of name change effects"""
    __tablename__ = 'name_change_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    change_id = db.Column(db.Integer, db.ForeignKey('name_change_records.id'), unique=True)
    
    # Visual encoding changes
    original_encoding_summary = db.Column(db.Text)  # JSON
    new_encoding_summary = db.Column(db.Text)  # JSON
    encoding_distance = db.Column(db.Float)
    
    # Predicted vs actual
    predicted_outcome_change = db.Column(db.Float)
    actual_outcome_change = db.Column(db.Float)
    prediction_accuracy = db.Column(db.Float)
    
    # Pattern type
    change_pattern = db.Column(db.String(50))  # improvement/decline/lateral
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


# =============================================================================
# TWINS (ULTIMATE CONTROL)
# =============================================================================

class TwinRecord(db.Model):
    """Identical twin pairs with different names and outcomes"""
    __tablename__ = 'twin_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Twins
    twin1_name = db.Column(db.String(200), nullable=False)
    twin2_name = db.Column(db.String(200), nullable=False)
    
    # Outcomes (any measurable difference)
    twin1_outcome = db.Column(db.Float, index=True)
    twin2_outcome = db.Column(db.Float, index=True)
    outcome_type = db.Column(db.String(50))  # income/education/career/health
    
    # Twin info
    birth_year = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    age_measured = db.Column(db.Integer)
    
    # Context
    raised_together = db.Column(db.Boolean)
    same_environment = db.Column(db.Boolean)
    
    # Verification
    twin_study_source = db.Column(db.String(200))
    
    collected_date = db.Column(db.DateTime, default=datetime.utcnow)


class TwinAnalysis(db.Model):
    """Analysis of twin outcome divergence"""
    __tablename__ = 'twin_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    twin_id = db.Column(db.Integer, db.ForeignKey('twin_records.id'), unique=True)
    
    # Name difference
    name_distance = db.Column(db.Float)  # Visual encoding distance
    phonetic_distance = db.Column(db.Float)
    semantic_distance = db.Column(db.Float)
    
    # Outcome difference
    outcome_difference = db.Column(db.Float)
    
    # Correlation
    # Does name_distance predict outcome_difference?
    correlation_strength = db.Column(db.Float)
    
    # Interpretation
    name_overrides_genetics = db.Column(db.Boolean)  # True if strong correlation
    
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)


def create_shocking_domain_tables():
    """Create all shocking domain tables"""
    from app import app
    import logging
    
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        db.create_all()
        
        logger.info("Shocking domain tables created:")
        logger.info("  - marriage_records")
        logger.info("  - marriage_compatibility_analyses")
        logger.info("  - parent_child_records")
        logger.info("  - parent_child_naming_analyses")
        logger.info("  - pet_owner_records")
        logger.info("  - pet_compatibility_analyses")
        logger.info("  - friendship_records")
        logger.info("  - name_change_records")
        logger.info("  - twin_records")

