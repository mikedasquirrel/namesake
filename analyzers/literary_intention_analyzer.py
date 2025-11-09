"""
Literary Intention & Truth-Claims Analysis
===========================================

Sophisticated framework for distinguishing fictional vs. truth-claiming narratives
and analyzing how authorial intention affects nominative patterns.

Core Questions:
1. Are names invented for narrative effect (fiction) or documented as historical (truth-claims)?
2. How do naming patterns differ between fiction-aware and truth-claiming texts?
3. What does nominative optimization reveal about authorial intention?
4. Can we detect the "fingerprint" of invention vs. documentation?

Philosophical Framework:
- Fiction: Author knows they're creating, optimizes for narrative effect
- Truth-Claims: Author believes/claims historical accuracy, constrained by reality
- Hybrid: Theological truth via narrative construction (gospel genre)
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from scipy import stats

logger = logging.getLogger(__name__)


class LiteraryIntentionAnalyzer:
    """
    Analyze literary intention and truth-claims in texts.
    """
    
    # Markers of fictional invention vs. historical documentation
    FICTION_MARKERS = {
        'narrative_optimization': [
            'names_too_perfect',  # All protagonists melodious, all villains harsh
            'symbolic_transparency',  # Names obviously symbolic (Mr. Darcy = darkness)
            'phonetic_clustering',  # Similar-sounding names grouped by role
            'invented_name_ratio_high',  # >40% clearly invented
            'aesthetic_optimization',  # All names highly melodious or memorable
        ],
        'genre_conventions': [
            'hero_name_pattern',  # Protagonists follow predictable patterns
            'villain_name_harsh',  # Antagonists systematically harsher
            'love_interest_melodious',  # Romantic leads optimized for beauty
            'comic_relief_unusual',  # Side characters have distinctive names
        ]
    }
    
    TRUTH_CLAIM_MARKERS = {
        'historical_constraints': [
            'culturally_authentic',  # Names match culture/era accurately
            'name_repetition',  # Multiple Johns, Marys (realistic)
            'mundane_names',  # Not all names optimized or symbolic
            'historical_verification',  # Names match external records
            'linguistic_accuracy',  # Names follow period-appropriate patterns
        ],
        'documentary_style': [
            'genealogies_present',  # Detailed lineages (historical claim)
            'geographic_specificity',  # Real places with accuracy
            'date_anchoring',  # Claims to specific times
            'eyewitness_language',  # "We saw", "I witnessed"
            'mundane_details',  # Unnecessary if inventing
        ]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("LiteraryIntentionAnalyzer initialized")
    
    def analyze_text_intention(self, text_data: Dict, character_names: List[Dict],
                               text_metadata: Dict) -> Dict:
        """
        Comprehensive analysis of literary intention (fiction vs. truth-claim).
        
        Args:
            text_data: Text content and statistics
            character_names: List of character name analyses
            text_metadata: Genre, authorship, cultural context
        
        Returns:
            Intention analysis with evidence for fiction vs. truth-claiming
        """
        # Analyze nominative patterns
        name_patterns = self._analyze_nominative_patterns(character_names)
        
        # Check for fictional optimization
        fiction_evidence = self._detect_fiction_markers(name_patterns, character_names)
        
        # Check for truth-claim markers
        truth_evidence = self._detect_truth_markers(text_data, text_metadata)
        
        # Synthesize assessment
        assessment = self._synthesize_intention_assessment(
            fiction_evidence, truth_evidence, text_metadata
        )
        
        return {
            'text': text_metadata.get('title', 'Unknown'),
            'nominative_patterns': name_patterns,
            'fiction_evidence': fiction_evidence,
            'truth_claim_evidence': truth_evidence,
            'intention_assessment': assessment,
            'philosophical_implications': self._analyze_philosophical_implications(assessment),
            'epistemic_status': self._determine_epistemic_status(assessment)
        }
    
    def _analyze_nominative_patterns(self, character_names: List[Dict]) -> Dict:
        """Analyze patterns in character naming that reveal intention."""
        
        if not character_names:
            return {}
        
        # Group by role if available
        by_role = defaultdict(list)
        for char in character_names:
            role = char.get('role', 'unknown')
            by_role[role].append(char)
        
        patterns = {
            'protagonist_melodiousness': None,
            'antagonist_melodiousness': None,
            'melodiousness_by_role_correlation': None,
            'name_role_alignment': None,
            'invented_name_ratio': None,
            'symbolic_transparency': None,
            'historical_authenticity': None,
            'name_repetition_pattern': None
        }
        
        # Calculate protagonist vs antagonist melodiousness
        if 'protagonist' in by_role and len(by_role['protagonist']) > 0:
            prot_melodious = [c.get('melodiousness', 0.5) for c in by_role['protagonist']]
            patterns['protagonist_melodiousness'] = float(np.mean(prot_melodious))
        
        if 'antagonist' in by_role and len(by_role['antagonist']) > 0:
            antag_melodious = [c.get('melodiousness', 0.5) for c in by_role['antagonist']]
            patterns['antagonist_melodiousness'] = float(np.mean(antag_melodious))
        
        # Test if melodiousness correlates TOO perfectly with role (sign of invention)
        if patterns['protagonist_melodiousness'] and patterns['antagonist_melodiousness']:
            diff = patterns['protagonist_melodiousness'] - patterns['antagonist_melodiousness']
            
            # If difference > 0.3, suspiciously optimized (fictional)
            # If difference < 0.1, realistic distribution (truth-claiming)
            patterns['melodiousness_by_role_correlation'] = float(diff)
            patterns['optimization_suspicion'] = diff > 0.3
        
        # Check for invented names
        invented_count = sum(1 for c in character_names if c.get('is_invented', False))
        patterns['invented_name_ratio'] = invented_count / len(character_names)
        
        # Check for name repetition (realistic in historical texts)
        name_counts = Counter([c.get('name', '') for c in character_names])
        repeated_names = sum(1 for count in name_counts.values() if count > 1)
        patterns['name_repetition_pattern'] = repeated_names / len(character_names) if character_names else 0
        
        # High repetition = more realistic (truth-claim marker)
        # Low repetition = optimized for clarity (fiction marker)
        
        return patterns
    
    def _detect_fiction_markers(self, patterns: Dict, character_names: List[Dict]) -> Dict:
        """Detect evidence of fictional invention."""
        
        evidence = {
            'markers_detected': [],
            'confidence_score': 0.0,
            'strongest_indicator': None
        }
        
        # Marker 1: Names too perfectly optimized
        if patterns.get('optimization_suspicion', False):
            evidence['markers_detected'].append({
                'marker': 'names_too_perfect',
                'description': 'Protagonists systematically more melodious than antagonists',
                'evidence': f"Δmelodiousness = {patterns.get('melodiousness_by_role_correlation', 0):.2f}",
                'weight': 0.3
            })
            evidence['confidence_score'] += 0.3
        
        # Marker 2: Very low invented name ratio suggests invention paradox
        # (Real history has mundane names; fiction optimizes every name)
        invented_ratio = patterns.get('invented_name_ratio', 0)
        if invented_ratio < 0.05:  # Suspiciously few "invented" = all sound real (fiction mimicking reality)
            evidence['markers_detected'].append({
                'marker': 'mimetic_authenticity',
                'description': 'Names may be crafted to sound historically authentic',
                'evidence': f"Invented ratio: {invented_ratio:.1%}",
                'weight': 0.2
            })
            evidence['confidence_score'] += 0.2
        
        # Marker 3: Low name repetition (fictional optimization for clarity)
        repetition = patterns.get('name_repetition_pattern', 0)
        if repetition < 0.1:  # < 10% repeated names
            evidence['markers_detected'].append({
                'marker': 'optimized_distinctiveness',
                'description': 'Each character has unique name (narrative clarity)',
                'evidence': f"Repetition: {repetition:.1%}",
                'weight': 0.25
            })
            evidence['confidence_score'] += 0.25
        
        # Identify strongest indicator
        if evidence['markers_detected']:
            evidence['strongest_indicator'] = max(
                evidence['markers_detected'], 
                key=lambda x: x['weight']
            )['marker']
        
        return evidence
    
    def _detect_truth_markers(self, text_data: Dict, text_metadata: Dict) -> Dict:
        """Detect evidence of truth-claiming/historical documentation."""
        
        evidence = {
            'markers_detected': [],
            'confidence_score': 0.0,
            'strongest_indicator': None
        }
        
        # Marker 1: High name repetition (realistic)
        # Gospel has multiple Marys, Johns, James - historically accurate
        
        # Marker 2: Culturally authentic names
        # All names match the cultural/linguistic context (1st century Judea)
        
        # Marker 3: Genealogies present
        if text_metadata.get('has_genealogy', False):
            evidence['markers_detected'].append({
                'marker': 'genealogical_specificity',
                'description': 'Detailed genealogies imply historical claim',
                'evidence': 'Genealogies present',
                'weight': 0.35
            })
            evidence['confidence_score'] += 0.35
        
        # Marker 4: Geographic anchoring
        if text_metadata.get('geographic_specificity', 0) > 0.7:
            evidence['markers_detected'].append({
                'marker': 'geographic_anchoring',
                'description': 'Specific real places documented',
                'evidence': f"Specificity: {text_metadata.get('geographic_specificity', 0):.1%}",
                'weight': 0.3
            })
            evidence['confidence_score'] += 0.3
        
        # Marker 5: Eyewitness language
        if text_metadata.get('eyewitness_claims', False):
            evidence['markers_detected'].append({
                'marker': 'eyewitness_language',
                'description': 'First-person or eyewitness testimony claimed',
                'evidence': 'Eyewitness language present',
                'weight': 0.4
            })
            evidence['confidence_score'] += 0.4
        
        # Marker 6: Mundane details (unnecessary if inventing)
        if text_metadata.get('mundane_detail_density', 0) > 0.5:
            evidence['markers_detected'].append({
                'marker': 'mundane_details',
                'description': 'Includes details unnecessary for narrative',
                'evidence': 'High mundane detail density',
                'weight': 0.25
            })
            evidence['confidence_score'] += 0.25
        
        if evidence['markers_detected']:
            evidence['strongest_indicator'] = max(
                evidence['markers_detected'],
                key=lambda x: x['weight']
            )['marker']
        
        return evidence
    
    def _synthesize_intention_assessment(self, fiction_evidence: Dict, 
                                        truth_evidence: Dict, 
                                        metadata: Dict) -> Dict:
        """
        Synthesize overall assessment of authorial intention.
        
        Returns assessment on spectrum from pure fiction to pure truth-claim.
        """
        fiction_score = fiction_evidence['confidence_score']
        truth_score = truth_evidence['confidence_score']
        
        # Normalize to 0-1 scale
        total = fiction_score + truth_score
        if total > 0:
            fiction_prob = fiction_score / total
            truth_prob = truth_score / total
        else:
            fiction_prob = 0.5
            truth_prob = 0.5
        
        # Categorize on spectrum
        if truth_prob > 0.7:
            category = 'truth_claiming'
            interpretation = 'Strong evidence of historical truth claim'
        elif truth_prob > 0.5:
            category = 'historical_theological'
            interpretation = 'Theological truth via historical events'
        elif fiction_prob > 0.7:
            category = 'fiction_aware'
            interpretation = 'Author consciously inventing narrative'
        elif fiction_prob > 0.5:
            category = 'literary_embellishment'
            interpretation = 'Historical core with literary enhancement'
        else:
            category = 'ambiguous'
            interpretation = 'Unclear intention - requires deeper analysis'
        
        # Gospel-specific assessment
        if metadata.get('genre') == 'gospel':
            genre_assessment = self._assess_gospel_genre(fiction_prob, truth_prob)
        else:
            genre_assessment = None
        
        return {
            'category': category,
            'spectrum_position': {
                'fiction_probability': float(fiction_prob),
                'truth_claim_probability': float(truth_prob)
            },
            'interpretation': interpretation,
            'confidence': max(fiction_prob, truth_prob),
            'genre_specific': genre_assessment
        }
    
    def _assess_gospel_genre(self, fiction_prob: float, truth_prob: float) -> Dict:
        """
        Special assessment for gospel genre.
        
        Gospels are unique: they claim historical truth but use literary techniques.
        This creates a hybrid form: "theological history" or "interpretive biography"
        """
        assessment = {
            'genre': 'gospel',
            'unique_characteristics': [
                'Claims historical truth',
                'Uses literary construction',
                'Theological interpretation embedded',
                'Eye-witness testimony claimed (some gospels)',
                'Written decades after events'
            ],
            'epistemological_status': None,
            'nominative_implications': None
        }
        
        # Gospels exist in liminal space
        if truth_prob > 0.6:
            assessment['epistemological_status'] = 'historically_grounded_theology'
            assessment['nominative_implications'] = """
Names are constrained by historical reality (real people had these names) 
but selected and arranged for theological significance. 
The nominative analysis reveals BOTH:
1. Historical authenticity (names match 1st century Judean patterns)
2. Theological selection (which names to emphasize reveals theological intent)
"""
        
        elif fiction_prob > 0.6:
            assessment['epistemological_status'] = 'theological_fiction'
            assessment['nominative_implications'] = """
Names are invented or heavily modified for theological symbolism.
The nominative analysis reveals authorial theology through name choices.
Even if historical core exists, names optimized for message.
"""
        
        else:
            assessment['epistemological_status'] = 'hybrid_historiography'
            assessment['nominative_implications'] = """
Names represent selective historical memory shaped by theological interpretation.
Some names historically accurate, others embellished or symbolic.
Nominative analysis reveals the interplay of history and theology.
"""
        
        # The critical question for research methodology
        assessment['methodological_implication'] = """
For nominative determinism research, this matters because:

IF FICTION: Names are chosen to fit narrative roles → names CAUSE our perception of outcomes
IF TRUTH-CLAIMING: Names are documentary → actual outcomes influenced real-life nominative patterns
IF HYBRID: Both operate simultaneously → recursive causation (names→outcomes→selection of which names to document)

The gospel genre forces us to confront: Can a text be both TRUE (claims historical accuracy) 
and CONSTRUCTED (literary artistry)? The answer determines how we interpret nominative correlations.
"""
        
        return assessment
    
    def compare_fiction_vs_gospel_naming(self, fiction_names: List[Dict], 
                                        gospel_names: List[Dict]) -> Dict:
        """
        Statistical comparison of naming patterns between admitted fiction and gospels.
        
        If gospels were fiction, they should show fictional naming patterns.
        If gospels are truth-claiming documentation, patterns should differ.
        
        Args:
            fiction_names: Character names from acknowledged fiction
            gospel_names: Character names from gospels
        
        Returns:
            Comparative analysis with implications for gospel truth-status
        """
        from analyzers.statistical_rigor import statistical_rigor
        
        # Extract melodiousness scores
        fiction_melodious = np.array([n.get('melodiousness', 0.5) for n in fiction_names])
        gospel_melodious = np.array([n.get('melodiousness', 0.5) for n in gospel_names])
        
        # Statistical comparison
        melodious_comparison = statistical_rigor.comprehensive_comparison(
            fiction_melodious, gospel_melodious,
            "Fiction Names", "Gospel Names"
        )
        
        # Role optimization analysis
        fiction_optimization = self._measure_role_optimization(fiction_names)
        gospel_optimization = self._measure_role_optimization(gospel_names)
        
        # Name repetition (realism marker)
        fiction_repetition = self._measure_name_repetition(fiction_names)
        gospel_repetition = self._measure_name_repetition(gospel_names)
        
        # Invented name ratio
        fiction_invented = sum(1 for n in fiction_names if n.get('is_invented', False)) / len(fiction_names)
        gospel_invented = sum(1 for n in gospel_names if n.get('is_invented', False)) / len(gospel_names)
        
        # Synthesis
        similarities = []
        differences = []
        
        # Melodiousness comparison
        if melodious_comparison['statistical_test']['p_value'] > 0.05:
            similarities.append("No significant difference in overall melodiousness")
        else:
            differences.append(f"Gospels {'more' if gospel_melodious.mean() > fiction_melodious.mean() else 'less'} melodious than fiction (p={melodious_comparison['statistical_test']['p_value']:.4f})")
        
        # Role optimization
        if abs(fiction_optimization - gospel_optimization) < 0.1:
            similarities.append(f"Similar role-based name optimization ({fiction_optimization:.2f} vs {gospel_optimization:.2f})")
        else:
            differences.append(f"Different optimization: Fiction={fiction_optimization:.2f}, Gospel={gospel_optimization:.2f}")
        
        # Name repetition (KEY MARKER)
        if gospel_repetition > fiction_repetition * 1.5:
            differences.append(f"Gospels show realistic name repetition ({gospel_repetition:.1%} vs fiction {fiction_repetition:.1%}) - TRUTH MARKER")
        
        return {
            'comparison_type': 'Fiction vs. Gospel Naming Patterns',
            'statistical_tests': {
                'melodiousness': melodious_comparison,
            },
            'pattern_analysis': {
                'fiction_optimization': float(fiction_optimization),
                'gospel_optimization': float(gospel_optimization),
                'fiction_repetition': float(fiction_repetition),
                'gospel_repetition': float(gospel_repetition),
                'fiction_invented_ratio': float(fiction_invented),
                'gospel_invented_ratio': float(gospel_invented)
            },
            'similarities': similarities,
            'differences': differences,
            'interpretation': self._interpret_fiction_gospel_comparison(similarities, differences),
            'implication_for_gospel_status': self._assess_gospel_truth_status(differences, gospel_repetition, gospel_optimization)
        }
    
    def _measure_role_optimization(self, names: List[Dict]) -> float:
        """
        Measure how much names are optimized for narrative roles.
        
        High optimization = fictional invention
        Low optimization = historical documentation
        
        Returns: Optimization score 0-1
        """
        by_role = defaultdict(list)
        for name in names:
            role = name.get('role', 'unknown')
            melodious = name.get('melodiousness', 0.5)
            by_role[role].append(melodious)
        
        if len(by_role) < 2:
            return 0.0
        
        # Calculate variance between role means
        role_means = [np.mean(scores) for scores in by_role.values() if scores]
        
        if len(role_means) < 2:
            return 0.0
        
        between_variance = np.var(role_means)
        
        # High between-role variance = optimization
        optimization = min(between_variance * 2, 1.0)
        
        return float(optimization)
    
    def _measure_name_repetition(self, names: List[Dict]) -> float:
        """Measure name repetition rate."""
        name_strings = [n.get('name', '') for n in names]
        name_counts = Counter(name_strings)
        
        repeated = sum(1 for count in name_counts.values() if count > 1)
        
        return repeated / len(name_counts) if name_counts else 0.0
    
    def _interpret_fiction_gospel_comparison(self, similarities: List[str], 
                                            differences: List[str]) -> str:
        """Interpret what comparison reveals about gospel nature."""
        
        if len(differences) > len(similarities):
            return """Gospels show distinct naming patterns from acknowledged fiction, 
suggesting different authorial intention. The presence of realistic features 
(name repetition, lack of optimization) supports truth-claiming rather than 
conscious invention."""
        
        elif len(similarities) > len(differences):
            return """Gospels show similar naming patterns to fiction, suggesting 
authors used literary techniques common to narrative construction. This doesn't 
prove fiction, but indicates literary artistry in composition."""
        
        else:
            return """Gospels show mixed patterns - some fictional techniques, some 
truth-claiming markers. This supports the 'interpretive history' model: real events 
shaped by theological interpretation."""
    
    def _assess_gospel_truth_status(self, differences: List[str], 
                                   repetition: float, optimization: float) -> str:
        """
        Assess implications for gospel historical truth status based on nominative evidence.
        """
        # High repetition + low optimization = truth-claiming documentation
        # Low repetition + high optimization = fictional invention
        
        truth_score = repetition - optimization
        
        if truth_score > 0.3:
            return """EVIDENCE FAVORS TRUTH-CLAIMING: High name repetition and low role-based 
optimization suggest authors documented real people rather than invented characters for 
narrative effect. This doesn't prove historicity, but nominative patterns align with 
documentary rather than fictional intention."""
        
        elif truth_score < -0.3:
            return """EVIDENCE FAVORS FICTION/CONSTRUCTION: Low repetition and high optimization 
suggest names were selected or invented for narrative and theological effect. This indicates 
literary construction, though historical core may exist."""
        
        else:
            return """EVIDENCE AMBIGUOUS: Nominative patterns show both realistic (documentation) 
and optimized (construction) features. This supports the scholarly consensus that gospels are 
'interpreted history'—real events shaped by theological purposes. Authors believed truth but 
used literary techniques to convey it."""
    
    def _analyze_philosophical_implications(self, assessment: Dict) -> Dict:
        """Analyze philosophical implications of the intention assessment."""
        
        category = assessment['category']
        
        implications = {
            'ontological': None,  # What exists
            'epistemological': None,  # How we know
            'ethical': None,  # What we should do
            'theological': None  # Religious implications
        }
        
        if category == 'truth_claiming':
            implications['ontological'] = "Claims: Events really happened; names document reality"
            implications['epistemological'] = "Knowledge claim: Author witnessed or received reliable testimony"
            implications['ethical'] = "Readers obligated to take seriously as truth claims"
            implications['theological'] = "If true, has religious authority; if false, deception"
        
        elif category == 'fiction_aware':
            implications['ontological'] = "No claim that characters existed"
            implications['epistemological'] = "Knowledge of general truths via invented particulars"
            implications['ethical'] = "Reader free to accept or reject without moral obligation"
            implications['theological'] = "No religious authority claims"
        
        elif category == 'historical_theological':
            implications['ontological'] = "Claims historical core + theological interpretation"
            implications['epistemological'] = "Mixed: some events documented, interpretation added"
            implications['ethical'] = "Complex: truth claims exist but mediated by interpretation"
            implications['theological'] = "Religious authority claimed but acknowledges interpretive element"
        
        return implications
    
    def _determine_epistemic_status(self, assessment: Dict) -> Dict:
        """
        Determine the epistemological status of the text.
        
        This is crucial for research methodology: How we analyze names depends on 
        whether we're studying INVENTION or DOCUMENTATION.
        """
        category = assessment['category']
        
        return {
            'status': category,
            'research_implications': self._get_research_implications(category),
            'methodological_requirements': self._get_methodological_requirements(category)
        }
    
    def _get_research_implications(self, category: str) -> str:
        """What this intention means for nominative determinism research."""
        
        if category == 'truth_claiming':
            return """If truth-claiming, nominative correlations reveal ACTUAL nominative 
determinism in history. Names really did influence outcomes, or prophetic meanings 
really did align with fates. This is the strongest evidence for nominative determinism."""
        
        elif category == 'fiction_aware':
            return """If fiction, nominative correlations reveal AUTHORIAL BELIEFS about 
nominative determinism. Authors create name-outcome patterns because they believe 
(consciously or unconsciously) that names should predict fates. This tests cultural 
assumptions about names."""
        
        elif category == 'historical_theological':
            return """If hybrid, nominative correlations reveal BOTH: 
1. Actual historical patterns (some names really influenced outcomes)
2. Theological interpretation (which stories to emphasize, how to frame them)

This is the most complex: real nominative determinism PLUS literary selection bias."""
        
        else:
            return "Ambiguous - requires deeper analysis of authorial intention"
    
    def _get_methodological_requirements(self, category: str) -> List[str]:
        """What methodological considerations are required for each category."""
        
        requirements = {
            'truth_claiming': [
                "Treat names as historical data",
                "Control for historical confounds (era, culture, class)",
                "Verify names against external historical sources",
                "Consider documentary selection bias (which people got documented?)",
                "Test if nominative patterns match contemporary populations"
            ],
            'fiction_aware': [
                "Treat names as authorial choices",
                "Analyze author's cultural background and beliefs",
                "Compare to author's other works",
                "Study genre conventions of the period",
                "Test if patterns match readers' expectations"
            ],
            'historical_theological': [
                "Separate documentary core from theological interpretation",
                "Identify which names are historically verified vs. literary",
                "Analyze theological purpose of name selection",
                "Control for both historical AND literary factors",
                "Acknowledge irreducible ambiguity in some cases"
            ]
        }
        
        return requirements.get(category, ["Determine intention before proceeding"])
    
    def gospel_specific_analysis(self, gospel_name: str, text_data: Dict,
                                character_names: List[Dict]) -> Dict:
        """
        Gospel-specific analysis accounting for unique genre.
        
        Gospels are not:
        - Pure fiction (claim historical truth)
        - Pure history (literary construction present)
        - Pure theology (ground claims in events)
        
        They are: "Theological history" or "Interpreted events"
        """
        
        # Standard intention analysis
        intention = self.analyze_text_intention(text_data, character_names, 
                                               {'title': gospel_name, 'genre': 'gospel'})
        
        # Gospel-specific dimensions
        gospel_analysis = {
            'gospel_name': gospel_name,
            'standard_analysis': intention,
            'historicity_assessment': self._assess_historicity(character_names),
            'theological_purpose': self._detect_theological_purpose(character_names),
            'selection_bias': self._analyze_selection_bias(character_names),
            'nominative_theology': self._extract_nominative_theology(character_names)
        }
        
        return gospel_analysis
    
    def _assess_historicity(self, names: List[Dict]) -> Dict:
        """Assess historical authenticity of names."""
        
        # Check cultural authenticity
        origins = [n.get('cultural_origin', 'unknown') for n in names]
        authentic = sum(1 for o in origins if o in ['hebrew', 'aramaic', 'greek'])
        
        authenticity_ratio = authentic / len(names) if names else 0
        
        # Check against external historical sources
        verified_count = sum(1 for n in names if n.get('historically_verified', False))
        
        return {
            'cultural_authenticity': float(authenticity_ratio),
            'externally_verified': verified_count,
            'verification_ratio': verified_count / len(names) if names else 0,
            'assessment': 'High' if authenticity_ratio > 0.8 else 'Medium' if authenticity_ratio > 0.5 else 'Low',
            'interpretation': self._interpret_historicity(authenticity_ratio, verified_count)
        }
    
    def _detect_theological_purpose(self, names: List[Dict]) -> Dict:
        """Detect theological purpose in name selection/emphasis."""
        
        # Which names get emphasized (high mention count)?
        emphasized_names = sorted(names, key=lambda x: x.get('mention_count', 0), reverse=True)[:10]
        
        # Check if emphasized names have theological significance
        theological_emphasis = []
        for name in emphasized_names:
            prophetic_meaning = name.get('prophetic_meaning', '')
            if any(word in prophetic_meaning.lower() for word in ['messiah', 'savior', 'prophet', 'divine', 'god']):
                theological_emphasis.append(name.get('name', ''))
        
        return {
            'emphasized_names': [n.get('name', '') for n in emphasized_names],
            'theologically_significant': theological_emphasis,
            'theological_emphasis_ratio': len(theological_emphasis) / len(emphasized_names) if emphasized_names else 0,
            'interpretation': f"{len(theological_emphasis)}/{len(emphasized_names)} most-emphasized names have theological significance"
        }
    
    def _analyze_selection_bias(self, names: List[Dict]) -> Dict:
        """
        Analyze selection bias in gospel authorship.
        
        Authors chose WHICH stories to tell, WHICH names to emphasize.
        Even if events are historical, selection reveals theology.
        """
        
        # Protagonists vs. minor characters
        major_chars = [n for n in names if n.get('importance', 0) > 0.7]
        minor_chars = [n for n in names if n.get('importance', 0) < 0.3]
        
        # Do major characters have more prophetically significant names?
        if major_chars and minor_chars:
            major_prophetic = np.mean([n.get('prophetic_score', 0.5) for n in major_chars])
            minor_prophetic = np.mean([n.get('prophetic_score', 0.5) for n in minor_chars])
            
            bias_detected = major_prophetic - minor_prophetic > 0.2
        else:
            bias_detected = False
            major_prophetic = 0.5
            minor_prophetic = 0.5
        
        return {
            'selection_bias_detected': bias_detected,
            'major_character_prophetic_score': float(major_prophetic),
            'minor_character_prophetic_score': float(minor_prophetic),
            'interpretation': """If major characters have more prophetic names, this reveals 
EITHER: (1) Theological selection (author chose which people to emphasize based on names)
OR: (2) Nominative determinism in action (people with prophetic names became major figures)
OR: (3) Both (recursive causation: names→importance→documentation)"""
        }
    
    def _extract_nominative_theology(self, names: List[Dict]) -> Dict:
        """
        Extract the implicit "theology of names" from the text.
        
        What does the gospel BELIEVE about names based on how it uses them?
        """
        
        # Check if names are explained/interpreted in text
        names_with_explanation = [n for n in names if n.get('name_explained', False)]
        
        # Check if name changes occur (theological significance)
        name_changes = [n for n in names if n.get('name_changed', False)]
        
        # Check if prophetic names cluster around Jesus
        # (Does gospel create nominative halo effect?)
        
        theology = {
            'explicit_name_theology': len(names_with_explanation) > 0,
            'name_explanation_count': len(names_with_explanation),
            'name_change_events': len(name_changes),
            'examples': [n.get('name', '') for n in names_with_explanation][:5]
        }
        
        # Synthesize implied belief about names
        if len(names_with_explanation) > 0:
            theology['implied_belief'] = "Gospel treats names as theologically significant—explains meanings, records changes"
        elif len(name_changes) > 0:
            theology['implied_belief'] = "Gospel recognizes transformative power of names (name changes mark identity shifts)"
        else:
            theology['implied_belief'] = "Gospel treats names as neutral identifiers—no explicit theology of names"
        
        return theology
    
    def _interpret_historicity(self, authenticity: float, verified: int) -> str:
        """Interpret historicity assessment."""
        if authenticity > 0.8 and verified > 5:
            return "Strong evidence of historical authenticity"
        elif authenticity > 0.6:
            return "Moderate evidence of historical basis"
        else:
            return "Limited evidence of historical authenticity"


# Singleton
literary_intention_analyzer = LiteraryIntentionAnalyzer()

