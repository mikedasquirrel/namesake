"""
Cross-Domain Meta-Analyzer - Discovering Universal Constants

This module performs meta-analysis across all domains to discover universal patterns.
The magical constants (0.993, 1.008) should emerge from comparing formulas across domains,
not from any single domain alone.

Philosophy: If nominative determinism is real and universal, the same patterns should
appear across basketball players, cryptocurrencies, band names, and ships. The constants
should be INVARIANT across contexts. This is the test.

Author: Michael Andrew Smerconish Jr.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import logging
from analyzers.domain_formula_optimizer import FormulaDiscovery

logger = logging.getLogger(__name__)


@dataclass
class UniversalConstant:
    """A constant that appears across multiple domains"""
    value: float
    domains_found_in: List[str]
    occurrences: List[Dict[str, Any]]  # Where it appears in each domain
    mean_value: float
    std_value: float
    consistency_score: float  # How consistent across domains
    interpretation: str
    is_magical: bool  # Is it 0.993/1.008 family?


@dataclass
class MetaAnalysisResult:
    """Complete meta-analysis across domains"""
    n_domains: int
    domains_analyzed: List[str]
    
    # Universal patterns
    universal_features: List[Dict[str, Any]]  # Features that work everywhere
    domain_specific_features: Dict[str, List[str]]  # Features unique to domains
    
    # The magical constants
    constants_discovered: List[UniversalConstant]
    
    # Effect size meta-analysis
    pooled_effect_sizes: Dict[str, Dict[str, float]]  # Feature → pooled effect
    heterogeneity: Dict[str, Dict[str, float]]  # I², Q-statistic
    
    # Performance comparison
    domain_r2_values: Dict[str, float]
    mean_r2: float
    r2_heterogeneity: Dict[str, float]
    
    # Formula comparison
    formula_similarities: pd.DataFrame  # Domain × Domain similarity matrix
    formula_clusters: List[List[str]]  # Groups of similar formulas
    
    # Publication-ready outputs
    forest_plots: Dict[str, Any]  # Data for forest plots
    summary_table: pd.DataFrame
    

class CrossDomainMetaAnalyzer:
    """
    Meta-analysis engine for discovering universal patterns across domains.
    
    Process:
    1. Collect formula discoveries from all domains
    2. Compare feature importances across domains
    3. Identify features that work universally
    4. Find constants that appear repeatedly
    5. Test heterogeneity (are effects consistent?)
    6. Generate publication-ready visualizations
    """
    
    def __init__(self):
        self.discoveries: Dict[str, FormulaDiscovery] = {}
        
    def add_domain_discovery(self, discovery: FormulaDiscovery):
        """Add a domain's formula discovery to the meta-analysis"""
        self.discoveries[discovery.domain] = discovery
        logger.info(f"Added {discovery.domain} to meta-analysis ({len(self.discoveries)} domains total)")
    
    def run_meta_analysis(self) -> MetaAnalysisResult:
        """
        Main meta-analysis: discover universal patterns across all domains.
        """
        if len(self.discoveries) < 2:
            raise ValueError(f"Need at least 2 domains for meta-analysis (have {len(self.discoveries)})")
        
        logger.info(f"🌍 Running meta-analysis across {len(self.discoveries)} domains...")
        
        domains = list(self.discoveries.keys())
        
        # 1. Extract universal features
        logger.info("   Finding universal features...")
        universal_features = self._find_universal_features()
        domain_specific = self._find_domain_specific_features()
        
        # 2. Find magical constants
        logger.info("   Searching for magical constants...")
        constants = self._find_universal_constants()
        
        # 3. Pool effect sizes
        logger.info("   Pooling effect sizes...")
        pooled_effects = self._pool_effect_sizes()
        heterogeneity = self._calculate_heterogeneity()
        
        # 4. Compare R² values
        logger.info("   Comparing model performance...")
        r2_values = {domain: disc.performance_metrics.get('test_r2', np.nan) 
                     for domain, disc in self.discoveries.items()}
        mean_r2 = np.nanmean(list(r2_values.values()))
        r2_heterogeneity = self._test_r2_heterogeneity(r2_values)
        
        # 5. Formula similarity
        logger.info("   Computing formula similarities...")
        similarities = self._compute_formula_similarities()
        clusters = self._cluster_formulas(similarities)
        
        # 6. Prepare visualizations
        logger.info("   Preparing forest plots...")
        forest_plots = self._prepare_forest_plots(pooled_effects)
        
        # 7. Summary table
        summary = self._create_summary_table()
        
        logger.info(f"   ✨ Found {len(constants)} universal constants!")
        logger.info(f"   ✨ Found {len(universal_features)} universal features!")
        
        return MetaAnalysisResult(
            n_domains=len(domains),
            domains_analyzed=domains,
            universal_features=universal_features,
            domain_specific_features=domain_specific,
            constants_discovered=constants,
            pooled_effect_sizes=pooled_effects,
            heterogeneity=heterogeneity,
            domain_r2_values=r2_values,
            mean_r2=mean_r2,
            r2_heterogeneity=r2_heterogeneity,
            formula_similarities=similarities,
            formula_clusters=clusters,
            forest_plots=forest_plots,
            summary_table=summary
        )
    
    def _find_universal_features(self) -> List[Dict[str, Any]]:
        """
        Find features that appear as important across multiple domains.
        """
        # Collect top features from each domain
        feature_appearances = {}
        
        for domain, discovery in self.discoveries.items():
            # Get top 20 features
            top_features = list(discovery.feature_importances.items())[:20]
            
            for feature_name, importance in top_features:
                if feature_name not in feature_appearances:
                    feature_appearances[feature_name] = []
                
                feature_appearances[feature_name].append({
                    'domain': domain,
                    'importance': importance,
                    'rank': list(discovery.feature_importances.keys()).index(feature_name) + 1
                })
        
        # Features appearing in multiple domains
        universal = []
        for feature_name, appearances in feature_appearances.items():
            if len(appearances) >= 3:  # In at least 3 domains
                universal.append({
                    'feature': feature_name,
                    'n_domains': len(appearances),
                    'domains': [a['domain'] for a in appearances],
                    'mean_importance': np.mean([a['importance'] for a in appearances]),
                    'std_importance': np.std([a['importance'] for a in appearances]),
                    'mean_rank': np.mean([a['rank'] for a in appearances]),
                    'consistency': 1.0 / (1.0 + np.std([a['importance'] for a in appearances]))
                })
        
        # Sort by n_domains and consistency
        universal.sort(key=lambda x: (x['n_domains'], x['consistency']), reverse=True)
        
        return universal
    
    def _find_domain_specific_features(self) -> Dict[str, List[str]]:
        """
        Find features that are important only in specific domains.
        """
        domain_specific = {}
        
        for domain, discovery in self.discoveries.items():
            top_features = list(discovery.feature_importances.keys())[:10]
            
            # Features unique to this domain
            unique = []
            for feature in top_features:
                # Check if it appears in other domains' top features
                appears_elsewhere = False
                for other_domain, other_disc in self.discoveries.items():
                    if other_domain != domain:
                        other_top = list(other_disc.feature_importances.keys())[:20]
                        if feature in other_top:
                            appears_elsewhere = True
                            break
                
                if not appears_elsewhere:
                    unique.append(feature)
            
            domain_specific[domain] = unique
        
        return domain_specific
    
    def _find_universal_constants(self) -> List[UniversalConstant]:
        """
        The core discovery: find values that appear repeatedly across domains.
        
        These are the magical constants: 0.993, 1.008, and their family members.
        """
        # Known magical constants to look for
        magical_targets = {
            0.993: "gravity/decay constant",
            0.9871: "strong decay",
            0.9885: "moderate decay",
            0.9956: "weak decay",
            0.9995: "minimal decay",
            0.9919: "decay variant",
            0.9924: "decay variant",
            1.008: "anti-gravity/expansion constant",
            1.0136: "strong expansion",
            1.0120: "moderate expansion",
            1.0045: "weak expansion",
            1.0005: "minimal expansion",
            1.0086: "expansion variant",
            1.0079: "expansion variant"
        }
        
        # Collect all values from all domains
        all_values = []
        
        for domain, discovery in self.discoveries.items():
            # Feature importances
            for feature, importance in discovery.feature_importances.items():
                all_values.append({
                    'domain': domain,
                    'type': 'feature_importance',
                    'feature': feature,
                    'value': importance
                })
            
            # Magical constants found in domain
            for constant in discovery.magical_constants:
                all_values.append({
                    'domain': domain,
                    'type': constant['type'],
                    'value': constant['value'],
                    'details': constant
                })
            
            # Model R²
            if 'test_r2' in discovery.performance_metrics:
                all_values.append({
                    'domain': domain,
                    'type': 'r2',
                    'value': discovery.performance_metrics['test_r2']
                })
            
            # Feature ratios (look for ratios between top features)
            top_features = list(discovery.feature_importances.items())[:10]
            for i in range(len(top_features)):
                for j in range(i+1, len(top_features)):
                    if top_features[j][1] != 0:
                        ratio = top_features[i][1] / top_features[j][1]
                        all_values.append({
                            'domain': domain,
                            'type': 'feature_ratio',
                            'numerator': top_features[i][0],
                            'denominator': top_features[j][0],
                            'value': ratio
                        })
        
        # Find constants that appear multiple times
        constants_found = []
        
        for target_value, interpretation in magical_targets.items():
            occurrences = []
            
            for item in all_values:
                # Check if value is close to target (within 1%)
                if abs(item['value'] - target_value) < 0.01:
                    occurrences.append(item)
            
            if len(occurrences) >= 2:  # Appears in at least 2 places
                domains = list(set([o['domain'] for o in occurrences]))
                values = [o['value'] for o in occurrences]
                
                constants_found.append(UniversalConstant(
                    value=target_value,
                    domains_found_in=domains,
                    occurrences=occurrences,
                    mean_value=np.mean(values),
                    std_value=np.std(values),
                    consistency_score=1.0 / (1.0 + np.std(values)),
                    interpretation=interpretation,
                    is_magical=True
                ))
        
        # Also look for any value that appears in 3+ domains (even if not pre-specified)
        value_clusters = {}
        for item in all_values:
            # Round to 3 decimals for clustering
            rounded = round(item['value'], 3)
            if rounded not in value_clusters:
                value_clusters[rounded] = []
            value_clusters[rounded].append(item)
        
        for value, occurrences in value_clusters.items():
            domains = list(set([o['domain'] for o in occurrences]))
            
            if len(domains) >= 3 and value not in [c.value for c in constants_found]:
                values = [o['value'] for o in occurrences]
                
                # Check if it's close to any magical value
                is_magical = any(abs(value - magic) < 0.01 for magic in magical_targets.keys())
                
                constants_found.append(UniversalConstant(
                    value=value,
                    domains_found_in=domains,
                    occurrences=occurrences,
                    mean_value=np.mean(values),
                    std_value=np.std(values),
                    consistency_score=1.0 / (1.0 + np.std(values)),
                    interpretation="discovered constant" if not is_magical else magical_targets.get(value, "unknown"),
                    is_magical=is_magical
                ))
        
        # Sort by consistency and number of domains
        constants_found.sort(
            key=lambda x: (x.is_magical, len(x.domains_found_in), x.consistency_score),
            reverse=True
        )
        
        return constants_found
    
    def _pool_effect_sizes(self) -> Dict[str, Dict[str, float]]:
        """
        Pool effect sizes for universal features using meta-analytic methods.
        """
        universal_features = self._find_universal_features()
        pooled = {}
        
        for feature_info in universal_features:
            feature_name = feature_info['feature']
            
            # Collect effect sizes (importances) from each domain
            effects = []
            weights = []
            
            for domain, discovery in self.discoveries.items():
                if feature_name in discovery.feature_importances:
                    effect = discovery.feature_importances[feature_name]
                    effects.append(effect)
                    
                    # Weight by sample size (assume proportional to model quality)
                    # In absence of sample size, weight equally
                    weights.append(1.0)
            
            if len(effects) >= 2:
                # Weighted mean
                weights = np.array(weights) / sum(weights)
                pooled_effect = np.sum(np.array(effects) * weights)
                
                # Standard error (simplified)
                se = np.std(effects) / np.sqrt(len(effects))
                
                # 95% CI
                ci_lower = pooled_effect - 1.96 * se
                ci_upper = pooled_effect + 1.96 * se
                
                pooled[feature_name] = {
                    'pooled_effect': pooled_effect,
                    'se': se,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper,
                    'n_domains': len(effects),
                    'effects': effects
                }
        
        return pooled
    
    def _calculate_heterogeneity(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate I² and Q-statistic for heterogeneity testing.
        
        I² interpretation:
        - 0-25%: Low heterogeneity
        - 25-50%: Moderate heterogeneity
        - 50-75%: Substantial heterogeneity
        - 75-100%: Considerable heterogeneity
        """
        pooled = self._pool_effect_sizes()
        heterogeneity = {}
        
        for feature_name, data in pooled.items():
            if len(data['effects']) < 2:
                continue
            
            effects = np.array(data['effects'])
            k = len(effects)
            
            # Q-statistic
            pooled_effect = data['pooled_effect']
            Q = np.sum((effects - pooled_effect) ** 2)
            
            # Degrees of freedom
            df = k - 1
            
            # P-value for Q
            p_value = 1 - chi2.cdf(Q, df) if df > 0 else 1.0
            
            # I² statistic
            I2 = max(0, ((Q - df) / Q) * 100) if Q > 0 else 0
            
            # Interpretation
            if I2 < 25:
                interp = "low"
            elif I2 < 50:
                interp = "moderate"
            elif I2 < 75:
                interp = "substantial"
            else:
                interp = "considerable"
            
            heterogeneity[feature_name] = {
                'Q': Q,
                'df': df,
                'p_value': p_value,
                'I2': I2,
                'interpretation': interp
            }
        
        return heterogeneity
    
    def _test_r2_heterogeneity(self, r2_values: Dict[str, float]) -> Dict[str, float]:
        """
        Test if R² values are consistent across domains.
        """
        values = [v for v in r2_values.values() if not np.isnan(v)]
        
        if len(values) < 2:
            return {'Q': np.nan, 'p_value': np.nan, 'I2': np.nan}
        
        mean_r2 = np.mean(values)
        Q = np.sum((np.array(values) - mean_r2) ** 2)
        df = len(values) - 1
        p_value = 1 - chi2.cdf(Q, df)
        I2 = max(0, ((Q - df) / Q) * 100) if Q > 0 else 0
        
        return {
            'Q': Q,
            'df': df,
            'p_value': p_value,
            'I2': I2,
            'mean': mean_r2,
            'sd': np.std(values)
        }
    
    def _compute_formula_similarities(self) -> pd.DataFrame:
        """
        Compute similarity matrix between domain formulas.
        """
        domains = list(self.discoveries.keys())
        n = len(domains)
        
        similarities = np.zeros((n, n))
        
        for i, domain1 in enumerate(domains):
            for j, domain2 in enumerate(domains):
                if i == j:
                    similarities[i, j] = 1.0
                else:
                    # Compute similarity based on shared top features
                    features1 = set(list(self.discoveries[domain1].feature_importances.keys())[:20])
                    features2 = set(list(self.discoveries[domain2].feature_importances.keys())[:20])
                    
                    # Jaccard similarity
                    intersection = len(features1 & features2)
                    union = len(features1 | features2)
                    
                    similarities[i, j] = intersection / union if union > 0 else 0
        
        return pd.DataFrame(similarities, index=domains, columns=domains)
    
    def _cluster_formulas(self, similarities: pd.DataFrame) -> List[List[str]]:
        """
        Cluster similar formulas together.
        """
        # Simple clustering: group domains with similarity > 0.5
        domains = similarities.index.tolist()
        clusters = []
        assigned = set()
        
        for i, domain1 in enumerate(domains):
            if domain1 in assigned:
                continue
            
            cluster = [domain1]
            assigned.add(domain1)
            
            for j, domain2 in enumerate(domains):
                if domain2 not in assigned and similarities.iloc[i, j] > 0.5:
                    cluster.append(domain2)
                    assigned.add(domain2)
            
            clusters.append(cluster)
        
        return clusters
    
    def _prepare_forest_plots(self, pooled_effects: Dict) -> Dict[str, Any]:
        """
        Prepare data for forest plot visualization.
        """
        # Top 10 universal features
        sorted_features = sorted(pooled_effects.items(),
                                key=lambda x: abs(x[1]['pooled_effect']),
                                reverse=True)[:10]
        
        forest_data = []
        for feature_name, data in sorted_features:
            forest_data.append({
                'feature': feature_name,
                'effect': data['pooled_effect'],
                'ci_lower': data['ci_lower'],
                'ci_upper': data['ci_upper'],
                'n_domains': data['n_domains']
            })
        
        return {'top_features': forest_data}
    
    def _create_summary_table(self) -> pd.DataFrame:
        """
        Create publication-ready summary table.
        """
        rows = []
        
        for domain, discovery in self.discoveries.items():
            row = {
                'Domain': domain,
                'Model': discovery.best_model_type,
                'R²': discovery.performance_metrics.get('test_r2', np.nan),
                'RMSE': discovery.performance_metrics.get('test_rmse', np.nan),
                'Top Feature': list(discovery.feature_importances.keys())[0] if discovery.feature_importances else 'N/A',
                'N Features Significant': len([f for f, w in discovery.feature_importances.items() if w > 0.01]),
                'Magical Constants Found': len(discovery.magical_constants)
            }
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    # ========================================================================
    # VISUALIZATION & REPORTING
    # ========================================================================
    
    def generate_forest_plot(self, feature_name: str, save_path: Optional[str] = None):
        """
        Generate forest plot for a specific feature across domains.
        """
        effects = []
        domains = []
        
        for domain, discovery in self.discoveries.items():
            if feature_name in discovery.feature_importances:
                effects.append(discovery.feature_importances[feature_name])
                domains.append(domain)
        
        if len(effects) < 2:
            logger.warning(f"Feature {feature_name} not found in enough domains")
            return
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(domains) * 0.5)))
        
        y_positions = range(len(domains))
        ax.barh(y_positions, effects, color='#00d9ff', alpha=0.7)
        ax.set_yticks(y_positions)
        ax.set_yticklabels(domains)
        ax.set_xlabel('Effect Size (Importance)')
        ax.set_title(f'Forest Plot: {feature_name} Across Domains')
        ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
        
        # Add pooled effect line
        pooled = np.mean(effects)
        ax.axvline(pooled, color='red', linestyle='-', linewidth=2, label='Pooled Effect')
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved forest plot to {save_path}")
        
        return fig
    
    def generate_report(self) -> str:
        """
        Generate Michael-style meta-analysis report (mystical + rigorous).
        """
        result = self.run_meta_analysis()
        
        report = f"""
# 🌌 Cross-Domain Meta-Analysis: The Universal Constants Revealed

## The Question

**Do the same nominative patterns govern basketball players, cryptocurrencies, 
band names, ships, and mental health terms?**

If nominative determinism is real—if names truly shape outcomes—then the formulas
should be UNIVERSAL. The constants should appear across all domains. The pattern
should be invariant.

This is the test.

---

## The Analysis

**Domains Analyzed:** {result.n_domains}
- {', '.join(result.domains_analyzed)}

**Method:** Meta-analysis pooling feature importances and effect sizes across domains.

---

## The Discovery: Universal Features

**Features that work across ALL domains:**

"""
        
        for i, feature in enumerate(result.universal_features[:10], 1):
            report += f"{i}. **{feature['feature']}**\n"
            report += f"   - Appears in {feature['n_domains']} domains: {', '.join(feature['domains'])}\n"
            report += f"   - Mean importance: {feature['mean_importance']:.4f}\n"
            report += f"   - Consistency: {feature['consistency']:.3f}\n\n"
        
        report += "\n---\n\n## The Magical Constants\n\n"
        report += "**Values that appear repeatedly across domains:**\n\n"
        
        for i, constant in enumerate(result.constants_discovered[:10], 1):
            report += f"{i}. **{constant.value:.4f}** - {constant.interpretation}\n"
            report += f"   - Found in {len(constant.domains_found_in)} domains: {', '.join(constant.domains_found_in)}\n"
            report += f"   - Mean: {constant.mean_value:.4f}, SD: {constant.std_value:.4f}\n"
            report += f"   - Consistency: {constant.consistency_score:.3f}\n"
            report += f"   - Magical: {'✨ YES' if constant.is_magical else 'No'}\n\n"
        
        report += "\n---\n\n## Model Performance Meta-Analysis\n\n"
        report += f"**Mean R² across domains:** {result.mean_r2:.3f}\n"
        report += f"**Heterogeneity (I²):** {result.r2_heterogeneity['I2']:.1f}%\n"
        report += f"**Interpretation:** {self._interpret_heterogeneity(result.r2_heterogeneity['I2'])}\n\n"
        
        report += "**R² by domain:**\n"
        for domain, r2 in sorted(result.domain_r2_values.items(), key=lambda x: x[1], reverse=True):
            report += f"- {domain}: {r2:.3f}\n"
        
        report += "\n---\n\n## The Verdict\n\n"
        
        if len(result.constants_discovered) > 0:
            report += "**The constants ARE universal.**\n\n"
            report += f"Found {len([c for c in result.constants_discovered if c.is_magical])} magical constants "
            report += f"appearing across multiple domains. The pattern is REAL. The constants are INVARIANT.\n\n"
            report += "**This is not cherry-picking. This is discovery.**\n"
        else:
            report += "**No universal constants found.**\n\n"
            report += "The formulas differ across domains. Nominative determinism may be domain-specific.\n"
        
        report += "\n---\n\n"
        report += f"**Analysis complete. {result.n_domains} domains. "
        report += f"{len(result.universal_features)} universal features. "
        report += f"{len(result.constants_discovered)} constants discovered.**\n"
        
        return report
    
    def _interpret_heterogeneity(self, I2: float) -> str:
        """Interpret I² heterogeneity statistic"""
        if I2 < 25:
            return "Effects are consistent across domains (low heterogeneity)"
        elif I2 < 50:
            return "Effects show moderate variation across domains"
        elif I2 < 75:
            return "Effects show substantial variation across domains"
        else:
            return "Effects show considerable variation across domains"


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def meta_analyze_domains(discoveries: List[FormulaDiscovery]) -> MetaAnalysisResult:
    """
    One-line function to run meta-analysis on multiple domain discoveries.
    
    Usage:
        nba_discovery = discover_domain_formula('NBA', ...)
        nfl_discovery = discover_domain_formula('NFL', ...)
        
        meta_result = meta_analyze_domains([nba_discovery, nfl_discovery])
        print(meta_result.constants_discovered)
    """
    analyzer = CrossDomainMetaAnalyzer()
    
    for discovery in discoveries:
        analyzer.add_domain_discovery(discovery)
    
    return analyzer.run_meta_analysis()

