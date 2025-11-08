"""Research Framework - Comprehensive Nominative Determinism Platform Configuration

This module serves as the single source of truth for the entire research program.
All domain analyses inherit from this framework to ensure consistency, rigor, and quality.

Author: Michael Smerconish
Date: November 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class EffectSize(Enum):
    """Standard effect size interpretations (Cohen's conventions)"""
    NEGLIGIBLE = "negligible"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


class ValidationStrength(Enum):
    """Evidence strength classifications"""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"


@dataclass
class ResearchMission:
    """Core mission and objectives of the nominative determinism research program"""
    
    primary_question: str = (
        "Do names influence outcomes across domains, and if so, under what conditions?"
    )
    
    core_hypothesis: str = (
        "Names influence outcomes through cognitive, behavioral, and perception pathways, "
        "but effects are context-dependent and mediated by semantic space, temporal precedence, "
        "and cognitive processing capacity."
    )
    
    research_goals: List[str] = field(default_factory=lambda: [
        "Quantify nominative determinism effects across 8+ independent domains",
        "Identify universal principles and domain-specific patterns",
        "Establish boundary conditions where effects emerge vs. disappear",
        "Create reproducible statistical methodology for nominative research",
        "Generate publication-quality findings with transparent null results",
        "Build production-ready web platform for interactive exploration"
    ])
    
    philosophical_stance: str = (
        "Radical empiricism with transparent methodology. Report all findings—positive, "
        "negative, and null—with equal rigor. Let the data speak, but interpret carefully "
        "with proper causal consideration."
    )


@dataclass
class TheoreticalFramework:
    """The Formula and universal principles underlying nominative determinism"""
    
    formula_description: str = (
        "Four-level compositional framework for modeling name-outcome relationships"
    )
    
    formula_levels: Dict[str, str] = field(default_factory=lambda: {
        "level_1_phonetic": "P_score = Σ(phoneme_weights) × syllable_structure × stress_pattern",
        "level_2_semantic": "S_score = P_score × congruence_factor × (1 - saturation_penalty)",
        "level_3_nominative": "N_score = S_score × predetermined_features_vector",
        "level_4_outcome": "Outcome = N_score × fundamentals + ε"
    })
    
    universal_principles: Dict[str, str] = field(default_factory=lambda: {
        "cognitive_load_minimization": (
            "Brevity wins across ALL spheres. Shorter names consistently show advantages "
            "due to reduced cognitive load (working memory constraints)."
        ),
        "contextual_congruence": (
            "Phonetic features must match context. Harsh → aggressive contexts (hurricanes, combat), "
            "smooth → aesthetic contexts (art, music). Mismatches weaken effects."
        ),
        "relative_differentiation": (
            "Saturation degrades optimal patterns. As more names adopt 'winning' features, "
            "advantages diminish. Effects are relative, not absolute."
        ),
        "mechanistic_gating": (
            "Names gate cohort access, fundamentals determine outcomes within cohort. "
            "Names get you in the door; performance keeps you there."
        ),
        "sphere_specific_sign_flips": (
            "Same feature, opposite effects across domains. High memorability positive in MTG, "
            "negative in crypto. Context determines sign and magnitude."
        )
    })
    
    universal_laws: Dict[str, str] = field(default_factory=lambda: {
        "memorability_is_universal": (
            "Memorability matters across all domains, but direction flips by market maturity. "
            "Emerging markets: high memorability wins. Mature markets: moderate memorability optimal."
        ),
        "context_activates_features": (
            "No universal formula exists. Different contexts activate different phonetic features. "
            "Must analyze each domain independently."
        ),
        "nonlinearity_is_the_rule": (
            "Linear relationships are rare. Expect thresholds, inverse-U curves, interactions, "
            "and polynomial effects. Always test nonlinear models."
        )
    })
    
    boundary_conditions: Dict[str, List[str]] = field(default_factory=lambda: {
        "strong_effects_when": [
            "Assigned/chosen naming (not geographic)",
            "Low semantic associations (minimal pre-existing meaning)",
            "Warning periods exist (name encountered before outcome)",
            "Behavioral pathways available (decisions can be influenced)",
            "Novel domains (no established conventions)"
        ],
        "weak_effects_when": [
            "Geographic naming (inherent, cannot change)",
            "Heavy semantic overload (development, culture, history dominate)",
            "No warning period (unpredictable events)",
            "Post-hoc naming (names assigned after outcomes)",
            "Mature domains (established conventions dominate)"
        ]
    })


@dataclass
class StatisticalMethodology:
    """Standard statistical methods and thresholds for all analyses"""
    
    significance_level: float = 0.05
    bonferroni_alpha: float = 0.01
    confidence_level: float = 0.95
    
    standard_methods: List[str] = field(default_factory=lambda: [
        "Pearson correlation (parametric, linear relationships)",
        "Spearman correlation (non-parametric, monotonic relationships)",
        "Kendall tau (non-parametric, ordinal data)",
        "Linear regression (baseline predictive model)",
        "Multiple regression (multivariate relationships)",
        "Polynomial regression (nonlinear relationships)",
        "Logistic regression (binary outcomes)",
        "Ridge/Lasso regression (regularization, high-dimensional)",
        "Random forest (feature importance, interactions)",
        "Gradient boosting (XGBoost for prediction)",
        "t-tests (two-group comparisons)",
        "ANOVA (multi-group comparisons)",
        "Chi-square tests (categorical associations)",
        "Mann-Whitney U (non-parametric two-group)",
        "Kruskal-Wallis (non-parametric multi-group)",
        "Effect size calculations (Cohen's d, eta-squared, R²)",
        "Cross-validation (5-fold standard, out-of-sample testing)",
        "Permutation tests (distribution-free significance)",
        "Bootstrap confidence intervals (robust uncertainty)",
        "Principal component analysis (dimensionality reduction)",
        "Cluster analysis (k-means, hierarchical)",
        "Survival analysis (time-to-event, Kaplan-Meier)",
        "Propensity score matching (causal inference attempts)"
    ])
    
    multiple_testing_corrections: List[str] = field(default_factory=lambda: [
        "Bonferroni correction (conservative, family-wise error rate)",
        "Holm-Bonferroni (less conservative, sequential)",
        "False Discovery Rate (FDR, Benjamini-Hochberg)"
    ])
    
    effect_size_thresholds: Dict[str, Dict[str, Tuple[float, float]]] = field(default_factory=lambda: {
        "cohens_d": {
            "negligible": (0.0, 0.2),
            "small": (0.2, 0.5),
            "medium": (0.5, 0.8),
            "large": (0.8, 1.2),
            "very_large": (1.2, float('inf'))
        },
        "r_squared": {
            "negligible": (0.0, 0.01),
            "small": (0.01, 0.09),
            "medium": (0.09, 0.25),
            "large": (0.25, 0.50),
            "very_large": (0.50, 1.0)
        },
        "correlation": {
            "negligible": (0.0, 0.1),
            "small": (0.1, 0.3),
            "medium": (0.3, 0.5),
            "large": (0.5, 0.7),
            "very_large": (0.7, 1.0)
        }
    })
    
    minimum_sample_sizes: Dict[str, int] = field(default_factory=lambda: {
        "pilot_study": 50,
        "correlation_analysis": 100,
        "regression_basic": 200,
        "regression_multivariate": 500,
        "machine_learning": 1000,
        "publication_quality": 500,
        "meta_analysis": 2000
    })
    
    validation_requirements: List[str] = field(default_factory=lambda: [
        "Out-of-sample testing (train/test split minimum)",
        "Cross-validation (5-fold standard)",
        "Effect size reporting (not just p-values)",
        "Confidence intervals (bootstrap preferred)",
        "Assumption checking (normality, homoscedasticity)",
        "Outlier analysis (identify and report influence)",
        "Missing data handling (explicit strategy)",
        "Multiple comparison corrections (when testing >5 hypotheses)",
        "Power analysis (post-hoc, report detectable effects)",
        "Sensitivity analysis (test robustness to assumptions)"
    ])


@dataclass
class QualityStandards:
    """Publication-readiness criteria and quality benchmarks"""
    
    data_quality_criteria: Dict[str, str] = field(default_factory=lambda: {
        "completeness": "≥95% complete data for primary variables",
        "accuracy": "Validated against authoritative sources where possible",
        "timeliness": "Data currency documented, updates tracked",
        "consistency": "Cross-validation across multiple sources when available",
        "representativeness": "Stratification or weighting to ensure representativeness"
    })
    
    analysis_quality_criteria: Dict[str, str] = field(default_factory=lambda: {
        "reproducibility": "All analyses scripted, dependencies versioned, random seeds set",
        "transparency": "Full methodology documented, code available",
        "rigor": "Multiple methods applied, results triangulated",
        "interpretation": "Conservative claims, alternative explanations considered",
        "visualization": "Publication-quality figures with clear labels"
    })
    
    publication_readiness_checklist: List[str] = field(default_factory=lambda: [
        "Sample size ≥500 or justified by power analysis",
        "Multiple statistical methods converge on same conclusion",
        "Out-of-sample validation performed",
        "Effect sizes reported with confidence intervals",
        "Null results transparently reported",
        "Causal language appropriate (correlation vs. causation)",
        "Limitations section comprehensive",
        "Alternative explanations addressed",
        "Figures publication-quality (300+ DPI)",
        "Tables properly formatted (APA/journal style)",
        "Methods section allows full replication",
        "Code and data availability statement included"
    ])
    
    innovation_rating_criteria: Dict[int, str] = field(default_factory=lambda: {
        1: "Standard analysis, incremental findings",
        2: "Novel methodology or interesting patterns",
        3: "Paradigm-shifting, multiple breakthroughs"
    })


@dataclass
class DomainMetadata:
    """Template metadata for research domains"""
    
    domain_id: str
    display_name: str
    research_questions: List[str]
    sample_size_target: int
    effect_strength_expected: str  # "strong", "moderate", "weak"
    primary_outcome_variable: str
    key_predictors: List[str]
    control_variables: Optional[List[str]] = None
    stratification_needed: bool = False
    temporal_component: bool = False
    geographic_component: bool = False
    status: str = "planned"  # planned, active, complete, published
    innovation_rating: int = 1  # 1-3
    notes: Optional[str] = None


class ResearchFramework:
    """
    Central framework for all nominative determinism research.
    
    Provides:
    - Mission and theoretical foundations
    - Statistical methodology standards
    - Quality benchmarks
    - Domain registry and metadata
    """
    
    def __init__(self):
        self.mission = ResearchMission()
        self.theory = TheoreticalFramework()
        self.statistics = StatisticalMethodology()
        self.quality = QualityStandards()
        self.domains = self._initialize_domain_registry()
    
    def _initialize_domain_registry(self) -> Dict[str, DomainMetadata]:
        """Initialize registry of research domains with metadata"""
        return {
            "hurricanes": DomainMetadata(
                domain_id="hurricanes",
                display_name="Hurricane Nomenclature",
                research_questions=[
                    "Do phonetically harsh names predict higher casualties?",
                    "Does name memorability affect behavioral response?",
                    "Are gender effects (Jung et al.) robust or confounded?"
                ],
                sample_size_target=236,
                effect_strength_expected="strong",
                primary_outcome_variable="casualties",
                key_predictors=["phonetic_harshness", "memorability", "syllable_count"],
                control_variables=["wind_speed", "pressure", "landfall_category"],
                temporal_component=True,
                status="complete",
                innovation_rating=3,
                notes="Publication-ready manuscript complete. ROC AUC 0.916."
            ),
            "cryptocurrency": DomainMetadata(
                domain_id="cryptocurrency",
                display_name="Cryptocurrency Markets",
                research_questions=[
                    "Do name quality metrics predict 1-year returns?",
                    "Is there an optimal cluster of name features?",
                    "Do effects persist after controlling for market cap?"
                ],
                sample_size_target=2740,
                effect_strength_expected="moderate",
                primary_outcome_variable="price_1yr_change",
                key_predictors=["syllable_count", "memorability", "uniqueness", "phonetic_score"],
                control_variables=["market_cap", "rank", "total_volume"],
                status="complete",
                innovation_rating=2,
                notes="6-method validation complete. Cluster effects identified."
            ),
            "mtg": DomainMetadata(
                domain_id="mtg",
                display_name="Magic: The Gathering",
                research_questions=[
                    "Do card name features predict competitive pricing?",
                    "Is there a 'sticky collectibles' premium?",
                    "Do complex names suffer obviousness penalty?"
                ],
                sample_size_target=25000,
                effect_strength_expected="strong",
                primary_outcome_variable="price_usd",
                key_predictors=["name_length", "syllables", "comma_presence", "memorability"],
                control_variables=["rarity", "card_type", "set_name", "year"],
                status="complete",
                innovation_rating=3,
                notes="Five paradigm-shifting discoveries. 65,000+ words documentation."
            ),
            "bands": DomainMetadata(
                domain_id="bands",
                display_name="Music Band Names",
                research_questions=[
                    "Do phonetic features predict commercial success?",
                    "Does exonym pronunciation affect international reach?",
                    "Are there temporal shifts in naming conventions?"
                ],
                sample_size_target=1500,
                effect_strength_expected="moderate",
                primary_outcome_variable="success_metrics",
                key_predictors=["syllables", "phonetic_features", "memorability"],
                temporal_component=True,
                geographic_component=True,
                status="complete",
                innovation_rating=3,
                notes="11 theoretical frameworks. 100,000+ words. Nominative Darwinism."
            ),
            "nba": DomainMetadata(
                domain_id="nba",
                display_name="NBA Players",
                research_questions=[
                    "Do phonetic features predict playing position?",
                    "Has internationalization changed name patterns?",
                    "Do name features correlate with performance?"
                ],
                sample_size_target=2000,
                effect_strength_expected="moderate",
                primary_outcome_variable="position",
                key_predictors=["syllables", "phonetic_strength", "name_origin"],
                temporal_component=True,
                status="complete",
                innovation_rating=2,
                notes="68% position prediction accuracy. 1992 inflection point."
            ),
            "nfl": DomainMetadata(
                domain_id="nfl",
                display_name="NFL Players",
                research_questions=[
                    "Do phonetic features predict position?",
                    "Does name complexity correlate with QB performance?",
                    "Are there temporal naming trends?"
                ],
                sample_size_target=1000,
                effect_strength_expected="moderate",
                primary_outcome_variable="position",
                key_predictors=["syllables", "phonetic_features", "name_length"],
                temporal_component=True,
                status="active",
                innovation_rating=2,
                notes="Data collection in progress. Position analysis framework ready."
            ),
            "mental_health": DomainMetadata(
                domain_id="mental_health",
                display_name="Mental Health Terminology",
                research_questions=[
                    "Do complex drug names reduce adherence?",
                    "Does diagnosis terminology affect stigma?",
                    "Are brand names more memorable than generics?"
                ],
                sample_size_target=500,
                effect_strength_expected="moderate",
                primary_outcome_variable="adherence_rates",
                key_predictors=["pronounceability", "syllables", "brand_vs_generic"],
                status="complete",
                innovation_rating=2,
                notes="Clinical distance paradox identified. Evidence-based recommendations."
            ),
            "immigration": DomainMetadata(
                domain_id="immigration",
                display_name="Immigration Surname Semantics",
                research_questions=[
                    "Do toponymic surnames show different immigration patterns?",
                    "Does place importance correlate with migration rates?",
                    "Are there semantic category × origin interactions?"
                ],
                sample_size_target=2000,
                effect_strength_expected="moderate",
                primary_outcome_variable="immigration_rate",
                key_predictors=["semantic_category", "place_importance", "origin_country"],
                temporal_component=True,
                geographic_component=True,
                status="complete",
                innovation_rating=2,
                notes="Semantic meaning analysis. 5 surname categories analyzed."
            ),
            "elections": DomainMetadata(
                domain_id="elections",
                display_name="Electoral Politics & Nomenclature",
                research_questions=[
                    "Does 'America' vs 'United States' predict political identity?",
                    "Do pronunciation shibboleths signal tribal affiliation?",
                    "Are there regional naming patterns?"
                ],
                sample_size_target=5000,
                effect_strength_expected="moderate",
                primary_outcome_variable="political_identity",
                key_predictors=["nomenclature_variant", "pronunciation_features"],
                geographic_component=True,
                status="complete",
                innovation_rating=2,
                notes="America Paradox: 95 subjective vs 6.5 algorithmic. CHY-NAH case study."
            ),
            "ships": DomainMetadata(
                domain_id="ships",
                display_name="Naval Vessel Nomenclature",
                research_questions=[
                    "Do name features predict vessel longevity?",
                    "Are there naming convention patterns by vessel type?",
                    "Do historical name patterns shift over time?"
                ],
                sample_size_target=1000,
                effect_strength_expected="weak",
                primary_outcome_variable="vessel_longevity",
                key_predictors=["syllables", "semantic_features", "vessel_type"],
                temporal_component=True,
                status="complete",
                innovation_rating=1,
                notes="Standard analysis. Moderate effects identified."
            ),
            "earthquakes": DomainMetadata(
                domain_id="earthquakes",
                display_name="Earthquake Geographic Names",
                research_questions=[
                    "Do place name features predict impact perception?",
                    "Is semantic overload a boundary condition?"
                ],
                sample_size_target=100,
                effect_strength_expected="weak",
                primary_outcome_variable="impact_metrics",
                key_predictors=["syllables", "familiarity"],
                geographic_component=True,
                status="active",
                innovation_rating=1,
                notes="Boundary condition validation. Weak effects expected (semantic overload)."
            ),
            "band_members": DomainMetadata(
                domain_id="band_members",
                display_name="Band Member Role & Name Analysis",
                research_questions=[
                    "Do phonetic features predict which role (bassist/drummer/vocalist/etc.) a member plays?",
                    "Does name 'harshness' correlate with drummer/guitarist roles?",
                    "Do 'smoother' names correlate with vocalist/songwriter roles?",
                    "Does collective member name composition predict band commercial success?",
                    "Are there temporal shifts in name-role patterns?"
                ],
                sample_size_target=3000,
                effect_strength_expected="moderate",
                primary_outcome_variable="primary_role",
                key_predictors=["syllables", "phonetic_harshness", "memorability", "name_origin"],
                control_variables=["band_genre", "formation_year", "band_success"],
                stratification_needed=True,
                temporal_component=True,
                status="active",
                innovation_rating=2,
                notes="Individual band member analysis. Role prediction analogous to NFL/NBA. Multi-level modeling."
            )
        }
    
    def get_domain(self, domain_id: str) -> Optional[DomainMetadata]:
        """Retrieve domain metadata by ID"""
        return self.domains.get(domain_id)
    
    def list_active_domains(self) -> List[str]:
        """List all active research domains"""
        return [
            domain_id for domain_id, metadata in self.domains.items()
            if metadata.status in ["active", "complete"]
        ]
    
    def get_statistical_method(self, method_name: str) -> Optional[str]:
        """Get description of a statistical method"""
        for method in self.statistics.standard_methods:
            if method_name.lower() in method.lower():
                return method
        return None
    
    def interpret_effect_size(self, value: float, metric_type: str = "correlation") -> str:
        """Interpret effect size magnitude"""
        if metric_type not in self.statistics.effect_size_thresholds:
            return "unknown"
        
        thresholds = self.statistics.effect_size_thresholds[metric_type]
        abs_value = abs(value)
        
        for interpretation, (lower, upper) in thresholds.items():
            if lower <= abs_value < upper:
                return interpretation
        
        return "unknown"
    
    def check_publication_readiness(self, domain_id: str, sample_size: int,
                                   has_out_of_sample: bool, has_effect_sizes: bool,
                                   has_null_results: bool) -> Tuple[bool, List[str]]:
        """Check if analysis meets publication standards"""
        issues = []
        
        domain = self.get_domain(domain_id)
        if domain and sample_size < domain.sample_size_target:
            issues.append(f"Sample size {sample_size} below target {domain.sample_size_target}")
        
        if sample_size < self.statistics.minimum_sample_sizes["publication_quality"]:
            issues.append(f"Sample size {sample_size} below publication minimum")
        
        if not has_out_of_sample:
            issues.append("No out-of-sample validation performed")
        
        if not has_effect_sizes:
            issues.append("Effect sizes not reported")
        
        if not has_null_results:
            issues.append("Null results not transparently reported")
        
        return len(issues) == 0, issues
    
    def get_summary(self) -> str:
        """Generate framework summary"""
        summary = []
        summary.append("=" * 80)
        summary.append("NOMINATIVE DETERMINISM RESEARCH FRAMEWORK")
        summary.append("=" * 80)
        summary.append(f"\nMission: {self.mission.primary_question}")
        summary.append(f"\nActive Domains: {len(self.list_active_domains())}")
        summary.append(f"Statistical Methods: {len(self.statistics.standard_methods)}")
        summary.append(f"Quality Criteria: {len(self.quality.publication_readiness_checklist)}")
        summary.append("\nTheoretical Foundation:")
        summary.append("  - The Formula (4 compositional levels)")
        summary.append(f"  - {len(self.theory.universal_principles)} Universal Principles")
        summary.append(f"  - {len(self.theory.universal_laws)} Universal Laws")
        summary.append("  - Boundary Conditions Framework")
        summary.append("\n" + "=" * 80)
        return "\n".join(summary)


# Singleton instance
FRAMEWORK = ResearchFramework()

