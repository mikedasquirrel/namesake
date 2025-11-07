"""Mental Health Term Analyzer

Specialized linguistic analysis for mental health diagnoses and medications.
Focuses on:
- Stigma linguistic markers
- Medicalization (Latin/Greek roots)
- Patient accessibility vs clinical precision
- Brand vs generic naming patterns
"""

import logging
import re
from typing import Dict, List, Optional
import json

from analyzers.name_analyzer import NameAnalyzer
from analyzers.phonemic_analyzer import PhonemicAnalyzer
from analyzers.semantic_analyzer import SemanticAnalyzer
from analyzers.sound_symbolism_analyzer import SoundSymbolismAnalyzer

logger = logging.getLogger(__name__)


class MentalHealthAnalyzer:
    """Analyze mental health terms with specialized metrics."""
    
    def __init__(self):
        """Initialize with standard analyzers."""
        self.name_analyzer = NameAnalyzer()
        self.phonemic_analyzer = PhonemicAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.sound_symbolism_analyzer = SoundSymbolismAnalyzer()
        
        # Latin/Greek medical roots (common in psychiatric terminology)
        self.latin_greek_roots = {
            'psych', 'schizo', 'mania', 'phobia', 'therapia', 'phren',
            'neur', 'psycho', 'para', 'hyper', 'hypo', 'dis', 'dys',
            'anti', 'pro', 'post', 'pre', 'trans', 'bi', 'uni', 'poly',
            'auto', 'hetero', 'homo', 'macro', 'micro', 'mega',
            'soma', 'path', 'ia', 'osis', 'itis', 'oid', 'ine', 'yl',
            'morph', 'logy', 'pathy', 'therapy', 'tropic', 'genic',
            'active', 'depressive', 'obsessive', 'compulsive', 'anxious',
            'zolam', 'azepam', 'pine', 'pram', 'traline', 'oxetine',
            'triptan', 'done', 'afil', 'olol', 'pril', 'sartan'
        }
        
        # Stigmatizing phonetic markers (harsh, abrupt sounds)
        self.harsh_phonemes = {
            'k', 'g', 'z', 'ʃ', 'ʒ', 'tʃ', 'dʒ', 'x', 'ð', 'θ'
        }
        
        # Patient-friendly phonetic markers (soft, flowing sounds)
        self.soft_phonemes = {
            'm', 'n', 'l', 'w', 'j', 'r', 'v'
        }
    
    def analyze(self, term_name: str, term_type: str = 'unknown', 
                all_terms: Optional[List[str]] = None) -> Dict:
        """
        Perform comprehensive mental health-specific analysis.
        
        Args:
            term_name: The diagnosis or medication name
            term_type: 'diagnosis', 'medication', 'condition', or 'system'
            all_terms: List of all terms for uniqueness comparison
            
        Returns:
            Dict with mental health-specific metrics
        """
        try:
            # Base linguistic analysis
            base_analysis = self.name_analyzer.analyze(term_name)
            
            # Phonemic analysis
            try:
                phonemic_data = self.phonemic_analyzer.analyze(term_name)
            except Exception as e:
                logger.warning(f"Phonemic analysis failed for {term_name}: {e}")
                phonemic_data = {}
            
            # Semantic analysis
            try:
                semantic_data = self.semantic_analyzer.analyze(term_name)
            except Exception as e:
                logger.warning(f"Semantic analysis failed for {term_name}: {e}")
                semantic_data = {}
            
            # Sound symbolism
            try:
                sound_data = self.sound_symbolism_analyzer.analyze(term_name)
            except Exception as e:
                logger.warning(f"Sound symbolism failed for {term_name}: {e}")
                sound_data = {}
            
            # Mental health-specific metrics
            latin_score = self._calculate_latin_greek_score(term_name)
            stigma_markers = self._calculate_stigma_markers(term_name, phonemic_data)
            pronounce_clinical = self._calculate_clinical_pronounceability(term_name, base_analysis)
            patient_friendly = self._calculate_patient_friendliness(term_name, base_analysis)
            
            # Etymology analysis
            etymology_data = self._analyze_etymology(term_name)
            
            return {
                # Standard metrics
                'character_length': base_analysis.get('character_length', len(term_name)),
                'syllable_count': base_analysis.get('syllable_count', 0),
                'phoneme_count': phonemic_data.get('phoneme_count', 0),
                'consonant_count': phonemic_data.get('consonant_count', 0),
                'vowel_count': phonemic_data.get('vowel_count', 0),
                'memorability_score': base_analysis.get('memorability_score', 50.0),
                'pronounceability_score': base_analysis.get('pronounceability_score', 50.0),
                'uniqueness_score': base_analysis.get('uniqueness_score', 50.0),
                
                # Mental health-specific
                'pronounceability_clinical': pronounce_clinical,
                'patient_friendliness': patient_friendly,
                'latin_roots_score': latin_score,
                'stigma_linguistic_markers': stigma_markers,
                
                # Phonetic features
                'harshness_score': sound_data.get('harshness', 50.0),
                'speed_score': sound_data.get('speed', 50.0),
                'strength_score': sound_data.get('strength', 50.0),
                
                # JSON data
                'phonetic_data': phonemic_data,
                'semantic_data': semantic_data,
                'etymology_data': etymology_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {term_name}: {e}")
            return self._get_default_analysis(term_name)
    
    def _calculate_latin_greek_score(self, term: str) -> float:
        """
        Calculate how medicalized/clinical a term is based on Latin/Greek roots.
        Higher score = more clinical/medical terminology.
        
        Args:
            term: The term to analyze
            
        Returns:
            Score from 0-100
        """
        term_lower = term.lower()
        
        # Count matches with medical roots
        matches = 0
        for root in self.latin_greek_roots:
            if root in term_lower:
                matches += 1
        
        # More matches = higher medicalization
        # Cap at 100
        score = min(100.0, matches * 25.0)
        
        # Bonus for common medication suffixes
        med_suffixes = ['azepam', 'zolam', 'pine', 'pram', 'traline', 'oxetine', 'olol', 'pril']
        for suffix in med_suffixes:
            if term_lower.endswith(suffix):
                score += 15.0
                break
        
        # Bonus for Greek/Latin prefixes
        medical_prefixes = ['anti', 'pro', 'pre', 'post', 'hyper', 'hypo', 'dis', 'dys']
        for prefix in medical_prefixes:
            if term_lower.startswith(prefix):
                score += 10.0
                break
        
        return min(100.0, score)
    
    def _calculate_stigma_markers(self, term: str, phonemic_data: Dict) -> float:
        """
        Calculate linguistic stigma markers (harsh sounds, abrupt patterns).
        Higher score = more stigmatizing phonetics.
        
        Args:
            term: The term to analyze
            phonemic_data: Phonemic analysis results
            
        Returns:
            Score from 0-100
        """
        score = 0.0
        
        # Check for harsh phonemes
        if phonemic_data and 'phonemes' in phonemic_data:
            phonemes = phonemic_data['phonemes']
            harsh_count = sum(1 for p in phonemes if p in self.harsh_phonemes)
            harsh_ratio = harsh_count / max(1, len(phonemes))
            score += harsh_ratio * 40.0
        
        # Check for harsh consonant clusters
        harsh_consonants = ['sch', 'scr', 'spr', 'str', 'thr', 'chr', 'phr']
        term_lower = term.lower()
        for cluster in harsh_consonants:
            if cluster in term_lower:
                score += 10.0
        
        # Check for stigmatizing word components
        stigma_components = ['psycho', 'schizo', 'para', 'patho', 'manic', 'disorder']
        for component in stigma_components:
            if component in term_lower:
                score += 15.0
                break
        
        # Abbreviations can feel clinical and distant
        if term.isupper() and len(term) <= 6:  # e.g., "PTSD", "OCD", "ADHD"
            score += 10.0
        
        return min(100.0, score)
    
    def _calculate_clinical_pronounceability(self, term: str, base_analysis: Dict) -> float:
        """
        How easy is this for medical professionals to pronounce?
        Medical professionals are familiar with Latin/Greek roots.
        
        Args:
            term: The term to analyze
            base_analysis: Base analysis results
            
        Returns:
            Score from 0-100
        """
        base_pronounce = base_analysis.get('pronounceability_score', 50.0)
        
        # Medical professionals are familiar with standard medical suffixes/prefixes
        term_lower = term.lower()
        
        # Boost for familiar medical patterns
        boost = 0.0
        if any(root in term_lower for root in self.latin_greek_roots):
            boost += 15.0
        
        # Standard medication naming patterns are easy for clinicians
        if any(term_lower.endswith(suffix) for suffix in ['azepam', 'pine', 'pram', 'traline']):
            boost += 10.0
        
        return min(100.0, base_pronounce + boost)
    
    def _calculate_patient_friendliness(self, term: str, base_analysis: Dict) -> float:
        """
        How accessible is this term for patients (non-medical speakers)?
        
        Args:
            term: The term to analyze
            base_analysis: Base analysis results
            
        Returns:
            Score from 0-100
        """
        base_pronounce = base_analysis.get('pronounceability_score', 50.0)
        base_memory = base_analysis.get('memorability_score', 50.0)
        
        # Start with average of pronounceability and memorability
        score = (base_pronounce + base_memory) / 2
        
        # Penalty for Latin/Greek clinical terminology
        latin_score = self._calculate_latin_greek_score(term)
        score -= (latin_score * 0.3)  # 30% penalty for medicalization
        
        # Penalty for long terms
        if len(term) > 12:
            score -= 10.0
        
        # Penalty for complex syllable patterns
        syllables = base_analysis.get('syllable_count', 0)
        if syllables > 4:
            score -= (syllables - 4) * 5.0
        
        # Boost for common words or brand names (typically simpler)
        if term[0].isupper() and len(term) <= 8 and not any(c.isupper() for c in term[1:]):
            # Looks like a brand name (e.g., "Prozac", "Zoloft")
            score += 15.0
        
        return max(0.0, min(100.0, score))
    
    def _analyze_etymology(self, term: str) -> Dict:
        """
        Analyze word roots and etymology.
        
        Args:
            term: The term to analyze
            
        Returns:
            Dict with etymology information
        """
        term_lower = term.lower()
        
        roots_found = []
        for root in self.latin_greek_roots:
            if root in term_lower:
                roots_found.append(root)
        
        # Detect common patterns
        is_brand_name = (
            term[0].isupper() and 
            len(term) <= 10 and 
            not any(c.isupper() for c in term[1:]) and
            not term.isupper()
        )
        
        is_generic_medication = any(
            term_lower.endswith(suffix) 
            for suffix in ['azepam', 'zolam', 'pine', 'pram', 'traline', 'oxetine']
        )
        
        is_dsm_diagnosis = any(
            component in term_lower 
            for component in ['disorder', 'syndrome', 'disease', 'condition']
        )
        
        return {
            'latin_greek_roots': roots_found,
            'root_count': len(roots_found),
            'likely_brand_name': is_brand_name,
            'likely_generic_medication': is_generic_medication,
            'likely_dsm_diagnosis': is_dsm_diagnosis,
            'has_medical_suffix': any(
                term_lower.endswith(suffix) 
                for suffix in ['ia', 'osis', 'itis', 'ine', 'yl', 'oid']
            ),
            'has_medical_prefix': any(
                term_lower.startswith(prefix)
                for prefix in ['anti', 'pro', 'pre', 'post', 'hyper', 'hypo', 'dis', 'dys']
            )
        }
    
    def _get_default_analysis(self, term: str) -> Dict:
        """
        Return default analysis if main analysis fails.
        
        Args:
            term: The term being analyzed
            
        Returns:
            Dict with default values
        """
        return {
            'character_length': len(term),
            'syllable_count': 0,
            'phoneme_count': 0,
            'consonant_count': 0,
            'vowel_count': 0,
            'memorability_score': 50.0,
            'pronounceability_score': 50.0,
            'uniqueness_score': 50.0,
            'pronounceability_clinical': 50.0,
            'patient_friendliness': 50.0,
            'latin_roots_score': 0.0,
            'stigma_linguistic_markers': 50.0,
            'harshness_score': 50.0,
            'speed_score': 50.0,
            'strength_score': 50.0,
            'phonetic_data': {},
            'semantic_data': {},
            'etymology_data': {}
        }
    
    def compare_brand_vs_generic(self, brand_name: str, generic_name: str) -> Dict:
        """
        Compare brand name vs generic name for same medication.
        
        Args:
            brand_name: Brand name (e.g., "Prozac")
            generic_name: Generic name (e.g., "Fluoxetine")
            
        Returns:
            Dict with comparative analysis
        """
        brand_analysis = self.analyze(brand_name, 'medication')
        generic_analysis = self.analyze(generic_name, 'medication')
        
        return {
            'brand': {
                'name': brand_name,
                'memorability': brand_analysis['memorability_score'],
                'patient_friendliness': brand_analysis['patient_friendliness'],
                'syllables': brand_analysis['syllable_count'],
                'length': brand_analysis['character_length']
            },
            'generic': {
                'name': generic_name,
                'memorability': generic_analysis['memorability_score'],
                'patient_friendliness': generic_analysis['patient_friendliness'],
                'syllables': generic_analysis['syllable_count'],
                'length': generic_analysis['character_length']
            },
            'differences': {
                'memorability_advantage': brand_analysis['memorability_score'] - generic_analysis['memorability_score'],
                'patient_friendliness_advantage': brand_analysis['patient_friendliness'] - generic_analysis['patient_friendliness'],
                'syllable_difference': brand_analysis['syllable_count'] - generic_analysis['syllable_count'],
                'length_difference': brand_analysis['character_length'] - generic_analysis['character_length']
            },
            'brand_advantage_percentage': (
                (brand_analysis['memorability_score'] - generic_analysis['memorability_score']) / 
                max(1, generic_analysis['memorability_score']) * 100
            )
        }



