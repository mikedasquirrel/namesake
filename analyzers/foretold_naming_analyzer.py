"""
Foretold Naming Analyzer
=========================

Analyzes prophetic name meanings, cultural naming patterns, and destiny alignments.
Tests nominative determinism through semantic analysis of name meanings vs. outcomes.

Features:
- Prophetic meaning extraction from etymology database
- Destiny alignment scoring (name meaning vs actual outcome)
- Cultural naming pattern detection
- Name-to-fate prediction using ML
- Cross-cultural name prophecy analysis
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from scipy import stats
from collections import defaultdict, Counter

# Try importing ML libraries
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. ML features disabled.")

# Database imports
from core.models import db, NameEtymology, DestinyAlignment, CulturalNamingPattern

# Load etymology database
import sys
sys.path.append(str(Path(__file__).parent.parent / 'data' / 'etymology'))

try:
    from name_etymology_database import etymology_db
    ETYMOLOGY_DB_AVAILABLE = True
except ImportError:
    ETYMOLOGY_DB_AVAILABLE = False
    logging.warning("Etymology database not available")

logger = logging.getLogger(__name__)


class ForetoldNamingAnalyzer:
    """
    Comprehensive foretold naming and prophetic analysis system.
    """
    
    def __init__(self):
        """Initialize analyzer with etymology database and ML models."""
        self.logger = logging.getLogger(__name__)
        
        # Load etymology database
        if ETYMOLOGY_DB_AVAILABLE:
            self.etymology_db = etymology_db
            self.logger.info(f"Loaded etymology database with {len(self.etymology_db.names)} names")
        else:
            self.etymology_db = None
            self.logger.warning("Etymology database not available")
        
        # Initialize ML models (will be trained separately)
        self.fate_prediction_models = {}
        
        # Initialize text vectorizer for semantic similarity
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
        else:
            self.vectorizer = None
        
        # Cultural patterns cache
        self.cultural_patterns = {}
        
        self.logger.info("ForetoldNamingAnalyzer initialized")
    
    def analyze_name(self, name: str, context: Optional[Dict] = None) -> Dict:
        """
        Comprehensive prophetic analysis of a name.
        
        Args:
            name: Name to analyze
            context: Optional context (domain, entity_type, etc.)
        
        Returns:
            Complete prophetic analysis including etymology, destiny alignment, cultural patterns
        """
        result = {
            'name': name,
            'etymology': self._get_etymology(name),
            'prophetic_meaning': self._get_prophetic_meaning(name),
            'destiny_category': self._get_destiny_category(name),
            'cultural_origin': self._get_cultural_origin(name),
            'semantic_valence': self._get_semantic_valence(name),
            'symbolic_associations': self._get_symbolic_associations(name),
            'name_components': self._analyze_name_components(name),
            'cultural_patterns': self._get_cultural_patterns(name, context),
            'prophetic_score': self._calculate_prophetic_score(name, context),
        }
        
        # If context provided with outcome, calculate destiny alignment
        if context and 'outcome' in context:
            result['destiny_alignment'] = self._calculate_destiny_alignment(
                name, context['outcome']
            )
        
        return result
    
    def _get_etymology(self, name: str) -> Optional[Dict]:
        """Get etymological data for name."""
        if not self.etymology_db:
            return None
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            return {
                'literal_meaning': name_data.get('meaning'),
                'origin': name_data.get('origin'),
                'etymology': name_data.get('etymology'),
                'historical_figures': name_data.get('historical_figures', []),
                'cultural_significance': name_data.get('cultural_significance')
            }
        
        return None
    
    def _get_prophetic_meaning(self, name: str) -> Optional[str]:
        """Extract prophetic/symbolic meaning of name."""
        if not self.etymology_db:
            return None
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            return name_data.get('prophetic_meaning')
        
        return None
    
    def _get_destiny_category(self, name: str) -> Optional[str]:
        """Get destiny category (virtue, power, wisdom, etc.)."""
        if not self.etymology_db:
            return None
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            return name_data.get('destiny_category')
        
        return None
    
    def _get_cultural_origin(self, name: str) -> Optional[str]:
        """Get cultural origin of name."""
        if not self.etymology_db:
            return None
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            return name_data.get('origin')
        
        return None
    
    def _get_semantic_valence(self, name: str) -> Optional[str]:
        """Get semantic valence (positive/negative/neutral/ambiguous)."""
        if not self.etymology_db:
            return None
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            return name_data.get('valence')
        
        return None
    
    def _get_symbolic_associations(self, name: str) -> List[str]:
        """Get symbolic associations of name."""
        if not self.etymology_db:
            return []
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            return name_data.get('symbolic_associations', [])
        
        return []
    
    def _analyze_name_components(self, name: str) -> Dict:
        """Analyze name component structure (prefix, root, suffix)."""
        if not self.etymology_db:
            return {}
        
        name_data = self.etymology_db.get_name(name)
        if name_data:
            components = name_data.get('components', {})
            return {
                'prefix': components.get('prefix', ''),
                'root': components.get('root', ''),
                'suffix': components.get('suffix', ''),
                'prophetic_elements': self._identify_prophetic_elements(components)
            }
        
        return {}
    
    def _identify_prophetic_elements(self, components: Dict) -> List[str]:
        """Identify prophetic/divine elements in name components."""
        prophetic_elements = []
        
        # Common prophetic prefixes/suffixes
        divine_elements = {
            'el': 'God (Hebrew)',
            'theo': 'God (Greek)',
            'deo': 'God (Latin)',
            'allah': 'God (Arabic)',
            'dev': 'God (Sanskrit)',
            'divine': 'Divine',
        }
        
        for component_name, component_value in components.items():
            if component_value:
                component_lower = component_value.lower()
                for divine_elem, meaning in divine_elements.items():
                    if divine_elem in component_lower:
                        prophetic_elements.append(f"{component_name}: {meaning}")
        
        return prophetic_elements
    
    def _get_cultural_patterns(self, name: str, context: Optional[Dict]) -> Dict:
        """Analyze name against cultural naming patterns."""
        patterns = {
            'hope_based': False,
            'prophetic': False,
            'ancestral': False,
            'religious': False,
            'matches_cultural_expectations': None
        }
        
        # Check if name has prophetic meaning
        prophetic_meaning = self._get_prophetic_meaning(name)
        if prophetic_meaning:
            patterns['prophetic'] = True
        
        # Check for religious/divine associations
        symbolic = self._get_symbolic_associations(name)
        if any(s in ['divinity', 'divine', 'prophecy', 'holy'] for s in symbolic):
            patterns['religious'] = True
        
        # Check cultural context if provided
        if context and 'culture' in context:
            patterns['matches_cultural_expectations'] = self._check_cultural_fit(
                name, context['culture']
            )
        
        return patterns
    
    def _check_cultural_fit(self, name: str, culture: str) -> bool:
        """Check if name fits cultural naming expectations."""
        origin = self._get_cultural_origin(name)
        if not origin:
            return False
        
        # Simple matching - can be expanded
        culture_origin_map = {
            'western': ['greek', 'latin', 'germanic', 'celtic'],
            'middle_eastern': ['hebrew', 'arabic'],
            'asian': ['chinese', 'japanese', 'sanskrit'],
            'african': ['african'],
        }
        
        culture_lower = culture.lower()
        for culture_group, origins in culture_origin_map.items():
            if culture_group in culture_lower and origin in origins:
                return True
        
        return False
    
    def _calculate_prophetic_score(self, name: str, context: Optional[Dict]) -> float:
        """
        Calculate how prophetic/meaningful a name is.
        
        Returns score 0-1 where higher = more prophetic significance.
        """
        score = 0.5  # Base score
        
        # Has prophetic meaning?
        if self._get_prophetic_meaning(name):
            score += 0.2
        
        # Has divine/religious associations?
        symbolic = self._get_symbolic_associations(name)
        if any(s in ['divinity', 'divine', 'prophecy', 'holy', 'blessed'] for s in symbolic):
            score += 0.15
        
        # Has prophetic name components?
        components = self._analyze_name_components(name)
        if components.get('prophetic_elements'):
            score += 0.15
        
        # Historical figures with prophetic/religious significance?
        etymology = self._get_etymology(name)
        if etymology and etymology.get('historical_figures'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_destiny_alignment(self, name: str, outcome: str) -> Dict:
        """
        Calculate alignment between name meaning and actual outcome.
        
        Args:
            name: Name to analyze
            outcome: Description of actual outcome
        
        Returns:
            Alignment analysis with score, explanation, keyword matches
        """
        prophetic_meaning = self._get_prophetic_meaning(name)
        symbolic = ' '.join(self._get_symbolic_associations(name))
        
        if not prophetic_meaning:
            return {
                'alignment_score': 0.5,
                'explanation': 'No prophetic meaning available for comparison',
                'confidence': 'low'
            }
        
        # Use semantic similarity if available
        if self.vectorizer and SKLEARN_AVAILABLE:
            try:
                # Combine prophetic meaning and symbolic associations
                name_text = f"{prophetic_meaning} {symbolic}"
                
                # Fit and transform
                texts = [name_text, outcome]
                vectors = self.vectorizer.fit_transform(texts)
                
                # Calculate cosine similarity
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                
                # Keyword matching
                keyword_matches = self._find_keyword_matches(name_text, outcome)
                
                # Adjust score based on keywords
                alignment_score = similarity
                if keyword_matches:
                    alignment_score = min(alignment_score + 0.2, 1.0)
                
                return {
                    'alignment_score': float(alignment_score),
                    'semantic_similarity': float(similarity),
                    'keyword_matches': keyword_matches,
                    'explanation': self._generate_alignment_explanation(
                        prophetic_meaning, outcome, alignment_score, keyword_matches
                    ),
                    'confidence': 'high' if alignment_score > 0.7 else 'medium' if alignment_score > 0.4 else 'low'
                }
            except Exception as e:
                self.logger.error(f"Error calculating semantic similarity: {e}")
        
        # Fallback to simple keyword matching
        keyword_matches = self._find_keyword_matches(
            f"{prophetic_meaning} {symbolic}".lower(), 
            outcome.lower()
        )
        
        alignment_score = 0.5 + (len(keyword_matches) * 0.1)
        alignment_score = min(alignment_score, 1.0)
        
        return {
            'alignment_score': alignment_score,
            'keyword_matches': keyword_matches,
            'explanation': self._generate_alignment_explanation(
                prophetic_meaning, outcome, alignment_score, keyword_matches
            ),
            'confidence': 'medium' if keyword_matches else 'low'
        }
    
    def _find_keyword_matches(self, text1: str, text2: str) -> List[str]:
        """Find matching keywords between two texts."""
        # Extract meaningful words (remove stop words manually)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been'}
        
        words1 = set(re.findall(r'\b\w+\b', text1.lower())) - stop_words
        words2 = set(re.findall(r'\b\w+\b', text2.lower())) - stop_words
        
        # Find matches
        matches = words1.intersection(words2)
        
        # Filter out very short words
        matches = [w for w in matches if len(w) > 3]
        
        return sorted(matches)
    
    def _generate_alignment_explanation(self, prophetic_meaning: str, outcome: str, 
                                       score: float, keywords: List[str]) -> str:
        """Generate human-readable explanation of destiny alignment."""
        if score > 0.7:
            strength = "Strong"
        elif score > 0.4:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        explanation = f"{strength} alignment between prophetic meaning and outcome. "
        
        if keywords:
            explanation += f"Shared concepts: {', '.join(keywords)}. "
        
        if score > 0.7:
            explanation += "The name appears to predict or align with the actual outcome."
        elif score > 0.4:
            explanation += "Some correlation exists between name meaning and outcome."
        else:
            explanation += "Limited correlation between name meaning and outcome."
        
        return explanation
    
    def predict_fate_from_name(self, name: str, domain: str) -> Dict:
        """
        Predict likely fate/outcome based on name characteristics.
        
        Args:
            name: Name to analyze
            domain: Domain context ('literary', 'sports', 'business', etc.)
        
        Returns:
            Prediction with probabilities and confidence
        """
        # Get name features
        features = self._extract_name_features_for_prediction(name)
        
        # Check if we have a trained model for this domain
        if domain in self.fate_prediction_models:
            model = self.fate_prediction_models[domain]
            try:
                prediction = model.predict([features])[0]
                probabilities = model.predict_proba([features])[0]
                
                return {
                    'predicted_outcome': prediction,
                    'probabilities': dict(zip(model.classes_, probabilities)),
                    'confidence': float(np.max(probabilities)),
                    'model_domain': domain
                }
            except Exception as e:
                self.logger.error(f"Error predicting fate: {e}")
        
        # Fallback to rule-based prediction
        return self._rule_based_fate_prediction(name, features)
    
    def _extract_name_features_for_prediction(self, name: str) -> np.ndarray:
        """Extract numerical features from name for ML prediction."""
        features = []
        
        # Basic features
        features.append(len(name))  # Name length
        features.append(name.count(' ') + 1)  # Number of parts
        
        # Etymology-based features
        destiny_cat = self._get_destiny_category(name)
        destiny_encoding = {
            'divine': 5, 'power': 4, 'wisdom': 3, 'warrior': 2, 
            'virtue': 1, 'beauty': 1, 'protection': 3
        }
        features.append(destiny_encoding.get(destiny_cat, 0))
        
        # Valence
        valence = self._get_semantic_valence(name)
        valence_encoding = {'positive': 1, 'negative': -1, 'neutral': 0, 'ambiguous': 0}
        features.append(valence_encoding.get(valence, 0))
        
        # Prophetic score
        features.append(self._calculate_prophetic_score(name, None))
        
        return np.array(features)
    
    def _rule_based_fate_prediction(self, name: str, features: np.ndarray) -> Dict:
        """Rule-based fate prediction when no ML model available."""
        destiny_cat = self._get_destiny_category(name)
        valence = self._get_semantic_valence(name)
        
        # Simple rules
        if destiny_cat == 'divine':
            predicted = 'significant_achievement'
            confidence = 0.7
        elif destiny_cat == 'power':
            predicted = 'leadership_role'
            confidence = 0.65
        elif destiny_cat == 'warrior':
            predicted = 'conflict_or_victory'
            confidence = 0.6
        elif destiny_cat == 'wisdom':
            predicted = 'intellectual_achievement'
            confidence = 0.6
        elif valence == 'negative':
            predicted = 'tragic_outcome'
            confidence = 0.5
        else:
            predicted = 'neutral_outcome'
            confidence = 0.4
        
        return {
            'predicted_outcome': predicted,
            'confidence': confidence,
            'method': 'rule_based',
            'based_on': {'destiny_category': destiny_cat, 'valence': valence}
        }
    
    def analyze_cultural_naming_pattern(self, region: str, era: str, 
                                       sample_names: List[str]) -> Dict:
        """
        Analyze cultural naming patterns for a region/era.
        
        Args:
            region: Geographic region
            era: Time period
            sample_names: Sample of names from that region/era
        
        Returns:
            Pattern analysis including common themes, hopes, taboos
        """
        pattern_analysis = {
            'region': region,
            'era': era,
            'sample_size': len(sample_names),
            'common_destiny_categories': Counter(),
            'common_origins': Counter(),
            'common_themes': Counter(),
            'valence_distribution': Counter(),
            'hope_based_patterns': [],
            'prophetic_names_ratio': 0.0,
        }
        
        # Analyze each name
        prophetic_count = 0
        for name in sample_names:
            dest_cat = self._get_destiny_category(name)
            if dest_cat:
                pattern_analysis['common_destiny_categories'][dest_cat] += 1
            
            origin = self._get_cultural_origin(name)
            if origin:
                pattern_analysis['common_origins'][origin] += 1
            
            valence = self._get_semantic_valence(name)
            if valence:
                pattern_analysis['common_valence_distribution'][valence] += 1
            
            symbolic = self._get_symbolic_associations(name)
            for sym in symbolic:
                pattern_analysis['common_themes'][sym] += 1
            
            prophetic_score = self._calculate_prophetic_score(name, None)
            if prophetic_score > 0.6:
                prophetic_count += 1
        
        # Calculate ratios
        if sample_names:
            pattern_analysis['prophetic_names_ratio'] = prophetic_count / len(sample_names)
        
        # Identify hope-based patterns
        top_themes = pattern_analysis['common_themes'].most_common(5)
        pattern_analysis['hope_based_patterns'] = [
            theme for theme, count in top_themes 
            if theme in ['success', 'prosperity', 'wisdom', 'strength', 'peace', 'joy']
        ]
        
        return pattern_analysis
    
    def save_etymology_to_db(self, name: str) -> Optional[NameEtymology]:
        """Save name etymology from database to SQL database."""
        if not self.etymology_db:
            return None
        
        name_data = self.etymology_db.get_name(name)
        if not name_data:
            return None
        
        # Check if already exists
        existing = NameEtymology.query.filter_by(name=name).first()
        if existing:
            return existing
        
        # Create new entry
        etymology_entry = NameEtymology(
            name=name,
            literal_meaning=name_data.get('meaning'),
            prophetic_meaning=name_data.get('prophetic_meaning'),
            cultural_origin=name_data.get('origin'),
            etymology=name_data.get('etymology'),
            name_prefix=name_data.get('components', {}).get('prefix'),
            name_root=name_data.get('components', {}).get('root'),
            name_suffix=name_data.get('components', {}).get('suffix'),
            semantic_valence=name_data.get('valence'),
            destiny_category=name_data.get('destiny_category'),
            symbolic_associations=json.dumps(name_data.get('symbolic_associations', [])),
            historical_figures=json.dumps(name_data.get('historical_figures', [])),
            biblical_reference=name_data.get('biblical_reference'),
            cultural_significance=name_data.get('cultural_significance'),
            variants=json.dumps(name_data.get('variants', [])),
            gender=name_data.get('gender'),
            popularity_peak=name_data.get('popularity_peak'),
        )
        
        try:
            db.session.add(etymology_entry)
            db.session.commit()
            self.logger.info(f"Saved etymology for {name} to database")
            return etymology_entry
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error saving etymology to database: {e}")
            return None
    
    def calculate_and_save_destiny_alignment(self, name: str, entity_type: str,
                                            entity_id: str, domain: str,
                                            outcome: str, outcome_category: str,
                                            outcome_metrics: Optional[Dict] = None) -> Optional[DestinyAlignment]:
        """
        Calculate destiny alignment and save to database.
        
        Args:
            name: Name to analyze
            entity_type: Type of entity ('character', 'person', etc.)
            entity_id: Unique ID of entity
            domain: Domain ('literary', 'sports', etc.)
            outcome: Description of outcome
            outcome_category: Category of outcome ('success', 'tragic', etc.)
            outcome_metrics: Optional quantitative metrics
        
        Returns:
            DestinyAlignment object if successful
        """
        # Ensure etymology exists in database
        etymology_entry = self.save_etymology_to_db(name)
        if not etymology_entry:
            self.logger.warning(f"Could not save etymology for {name}")
            return None
        
        # Calculate alignment
        alignment = self._calculate_destiny_alignment(name, outcome)
        
        # Create destiny alignment entry
        destiny_entry = DestinyAlignment(
            name_etymology_id=etymology_entry.id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=name,
            domain=domain,
            actual_outcome=outcome,
            outcome_category=outcome_category,
            outcome_metrics=json.dumps(outcome_metrics or {}),
            alignment_score=alignment.get('alignment_score'),
            alignment_explanation=alignment.get('explanation'),
            semantic_overlap=alignment.get('semantic_similarity', 0.0),
            keyword_matches=json.dumps(alignment.get('keyword_matches', [])),
            confidence_score=0.8 if alignment.get('confidence') == 'high' else 0.5 if alignment.get('confidence') == 'medium' else 0.3,
        )
        
        try:
            db.session.add(destiny_entry)
            db.session.commit()
            self.logger.info(f"Saved destiny alignment for {name}")
            return destiny_entry
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error saving destiny alignment: {e}")
            return None
    
    def get_aggregate_alignment_statistics(self, domain: Optional[str] = None) -> Dict:
        """
        Get aggregate statistics on destiny alignment across all analyzed names.
        
        Args:
            domain: Optional domain filter
        
        Returns:
            Aggregate statistics
        """
        query = DestinyAlignment.query
        if domain:
            query = query.filter_by(domain=domain)
        
        alignments = query.all()
        
        if not alignments:
            return {'error': 'No alignments found'}
        
        scores = [a.alignment_score for a in alignments if a.alignment_score is not None]
        
        return {
            'total_analyzed': len(alignments),
            'domain': domain or 'all',
            'mean_alignment_score': float(np.mean(scores)) if scores else 0.0,
            'median_alignment_score': float(np.median(scores)) if scores else 0.0,
            'std_alignment_score': float(np.std(scores)) if scores else 0.0,
            'high_alignment_count': sum(1 for s in scores if s > 0.7),
            'low_alignment_count': sum(1 for s in scores if s < 0.3),
            'outcome_categories': Counter([a.outcome_category for a in alignments]).most_common(),
        }


# Create singleton instance
foretold_analyzer = ForetoldNamingAnalyzer()

