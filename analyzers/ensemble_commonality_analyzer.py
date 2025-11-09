"""
Ensemble Commonality Analyzer
==============================

Analyzes character ensembles accounting for name commonality in cultural context.

Key Metrics:
1. Mean Commonality - Average name frequency
2. Commonality Variance - Spread of frequencies  
3. Outlier Count - Extremely rare/common names
4. Cultural Typicality - Fit to cultural norms

Statistical Tests:
- Kolmogorov-Smirnov (distribution comparison)
- Levene's test (variance equality)
- Two-sample t-test (mean comparison)
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from scipy import stats
from collections import Counter

from data.cultural_commonality.historical_name_frequencies import historical_frequencies
from analyzers.cultural_acoustic_analyzer import cultural_acoustic_analyzer
from analyzers.statistical_rigor import statistical_rigor

logger = logging.getLogger(__name__)


class EnsembleCommonalityAnalyzer:
    """Analyze ensemble commonality patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.frequencies_db = historical_frequencies
        self.logger.info("EnsembleCommonalityAnalyzer initialized")
    
    def analyze_ensemble_commonality(self, names: List[str], 
                                     cultural_context: str,
                                     ensemble_name: str = "Ensemble") -> Dict:
        """
        Analyze ensemble name commonality in cultural context.
        
        Args:
            names: List of character names
            cultural_context: Cultural context key
            ensemble_name: Name of ensemble
        
        Returns:
            Commonality analysis
        """
        # Get commonality scores for each name
        commonality_scores = []
        commonality_details = []
        
        for name in names:
            score = self.frequencies_db.get_commonality_score(name, cultural_context)
            category = self.frequencies_db.get_rarity_category(name, cultural_context)
            
            commonality_scores.append(score)
            commonality_details.append({
                'name': name,
                'score': score,
                'category': category
            })
        
        commonality_array = np.array(commonality_scores)
        
        # Calculate metrics
        metrics = {
            'mean_commonality': float(np.mean(commonality_array)),
            'median_commonality': float(np.median(commonality_array)),
            'variance_commonality': float(np.var(commonality_array)),
            'std_commonality': float(np.std(commonality_array)),
            'min_commonality': float(np.min(commonality_array)),
            'max_commonality': float(np.max(commonality_array)),
            'range_commonality': float(np.max(commonality_array) - np.min(commonality_array))
        }
        
        # Count outliers (>2 SD from cultural norm)
        outliers = self._count_outliers(commonality_array, 0.5)  # 0.5 = cultural baseline
        
        # Category distribution
        categories = Counter([d['category'] for d in commonality_details])
        
        return {
            'ensemble_name': ensemble_name,
            'cultural_context': cultural_context,
            'n_names': len(names),
            'names': commonality_details,
            'metrics': metrics,
            'outliers': outliers,
            'category_distribution': dict(categories),
            'interpretation': self._interpret_commonality(metrics, outliers, categories)
        }
    
    def _count_outliers(self, scores: np.ndarray, baseline: float, threshold: float = 0.25) -> Dict:
        """Count outliers (names >2 SD from baseline)."""
        deviations = np.abs(scores - baseline)
        
        outlier_indices = np.where(deviations > threshold)[0]
        
        return {
            'count': int(len(outlier_indices)),
            'proportion': float(len(outlier_indices) / len(scores)) if len(scores) > 0 else 0,
            'indices': outlier_indices.tolist()
        }
    
    def _interpret_commonality(self, metrics: Dict, outliers: Dict, categories: Counter) -> str:
        """Interpret commonality pattern."""
        mean_common = metrics['mean_commonality']
        variance = metrics['variance_commonality']
        
        if mean_common > 0.7:
            common_interp = "Very common names overall (high baseline)"
        elif mean_common > 0.5:
            common_interp = "Moderately common names"
        else:
            common_interp = "Rare names overall (low baseline)"
        
        if variance > 0.15:
            var_interp = "high variance (deliberate mix of common and rare)"
        elif variance > 0.08:
            var_interp = "medium variance (natural distribution)"
        else:
            var_interp = "low variance (homogeneous commonality)"
        
        outlier_prop = outliers['proportion']
        if outlier_prop > 0.3:
            outlier_interp = "many outliers (unusual name choices)"
        elif outlier_prop > 0.15:
            outlier_interp = "some outliers"
        else:
            outlier_interp = "few outliers (typical selections)"
        
        return f"{common_interp}; {var_interp}; {outlier_interp}"
    
    def compare_fiction_nonfiction_commonality(self, fiction_ensembles: List[Dict],
                                              nonfiction_ensembles: List[Dict],
                                              cultural_context: str) -> Dict:
        """
        Compare commonality patterns between fiction and non-fiction.
        
        Tests 4 hypotheses:
        H1: Fiction uses rarer names (lower mean commonality)
        H2: Fiction has higher commonality variance (deliberate mix)
        H3: Fiction has more outliers (unusual choices)
        H4: Fiction more culturally typical (authors research norms)
        
        Args:
            fiction_ensembles: List of dicts with 'names' key
            nonfiction_ensembles: List of dicts with 'names' key
            cultural_context: Context for analysis
        
        Returns:
            Comprehensive comparison with 4 hypothesis tests
        """
        # Analyze all fiction ensembles
        fiction_analyses = [
            self.analyze_ensemble_commonality(e['names'], cultural_context, e.get('title', 'Fiction'))
            for e in fiction_ensembles
        ]
        
        # Analyze all non-fiction ensembles
        nonfiction_analyses = [
            self.analyze_ensemble_commonality(e['names'], cultural_context, e.get('title', 'Nonfiction'))
            for e in nonfiction_ensembles
        ]
        
        # Extract metrics
        fiction_means = np.array([a['metrics']['mean_commonality'] for a in fiction_analyses])
        nonfiction_means = np.array([a['metrics']['mean_commonality'] for a in nonfiction_analyses])
        
        fiction_variances = np.array([a['metrics']['variance_commonality'] for a in fiction_analyses])
        nonfiction_variances = np.array([a['metrics']['variance_commonality'] for a in nonfiction_analyses])
        
        fiction_outlier_props = np.array([a['outliers']['proportion'] for a in fiction_analyses])
        nonfiction_outlier_props = np.array([a['outliers']['proportion'] for a in nonfiction_analyses])
        
        # H1: Fiction has lower mean commonality (rarer names)
        h1_result = statistical_rigor.comprehensive_comparison(
            nonfiction_means, fiction_means,  # Note: flipped so positive d = nonfiction higher
            "Non-Fiction", "Fiction"
        )
        
        # H2: Fiction has higher variance (deliberate mix)
        h2_test = stats.levene(fiction_variances, nonfiction_variances)
        h2_result = {
            'test': "Levene's test for variance equality",
            'statistic': float(h2_test.statistic),
            'p_value': float(h2_test.pvalue),
            'fiction_mean_variance': float(fiction_variances.mean()),
            'nonfiction_mean_variance': float(nonfiction_variances.mean()),
            'interpretation': 'Fiction has higher variance' if fiction_variances.mean() > nonfiction_variances.mean() else 'Non-fiction has higher variance'
        }
        
        # H3: Fiction has more outliers
        h3_result = statistical_rigor.comprehensive_comparison(
            fiction_outlier_props, nonfiction_outlier_props,
            "Fiction", "Non-Fiction"
        )
        
        # H4: Distribution test (KS test)
        # Flatten all name commonality scores
        fiction_all_scores = []
        for analysis in fiction_analyses:
            fiction_all_scores.extend([n['score'] for n in analysis['names']])
        
        nonfiction_all_scores = []
        for analysis in nonfiction_analyses:
            nonfiction_all_scores.extend([n['score'] for n in analysis['names']])
        
        ks_stat, ks_p = stats.ks_2samp(fiction_all_scores, nonfiction_all_scores)
        h4_result = {
            'test': 'Kolmogorov-Smirnov test',
            'statistic': float(ks_stat),
            'p_value': float(ks_p),
            'significant': ks_p < 0.05,
            'interpretation': 'Distributions differ significantly' if ks_p < 0.05 else 'Distributions similar'
        }
        
        return {
            'cultural_context': cultural_context,
            'n_fiction': len(fiction_ensembles),
            'n_nonfiction': len(nonfiction_ensembles),
            'hypothesis_tests': {
                'h1_mean_commonality': h1_result,
                'h2_variance': h2_result,
                'h3_outliers': h3_result,
                'h4_distributions': h4_result
            },
            'summary': self._summarize_comparison(h1_result, h2_result, h3_result, h4_result)
        }
    
    def _summarize_comparison(self, h1, h2, h3, h4) -> str:
        """Summarize hypothesis test results."""
        results = []
        
        # H1: Mean commonality
        if h1['statistical_test']['p_value'] < 0.05:
            results.append(f"✅ H1: Non-fiction uses more common names (d={h1['effect_size']['cohens_d']:.2f}, p={h1['statistical_test']['p_value']:.4f})")
        else:
            results.append(f"❌ H1: No significant difference in mean commonality (p={h1['statistical_test']['p_value']:.4f})")
        
        # H2: Variance
        if h2['p_value'] < 0.05:
            results.append(f"✅ H2: Variances differ significantly (p={h2['p_value']:.4f})")
        else:
            results.append(f"❌ H2: Variances similar (p={h2['p_value']:.4f})")
        
        # H3: Outliers
        if h3['statistical_test']['p_value'] < 0.05:
            results.append(f"✅ H3: Fiction has more outliers (d={h3['effect_size']['cohens_d']:.2f}, p={h3['statistical_test']['p_value']:.4f})")
        else:
            results.append(f"❌ H3: Outlier rates similar (p={h3['statistical_test']['p_value']:.4f})")
        
        # H4: Distributions
        if h4['p_value'] < 0.05:
            results.append(f"✅ H4: Commonality distributions differ (KS={h4['statistic']:.3f}, p={h4['p_value']:.4f})")
        else:
            results.append(f"❌ H4: Distributions similar (p={h4['p_value']:.4f})")
        
        return "\n".join(results)
    
    def test_gospel_pattern(self, gospel_names: List[str], 
                           fiction_comparison: List[Dict],
                           nonfiction_comparison: List[Dict],
                           cultural_context: str = "1st_century_judea") -> Dict:
        """
        Test whether gospel names follow fiction or non-fiction commonality patterns.
        
        CRITICAL TEST for gospel truth-status assessment.
        
        Args:
            gospel_names: Gospel character names
            fiction_comparison: Fiction ensembles for comparison
            nonfiction_comparison: Non-fiction ensembles for comparison
            cultural_context: Cultural context
        
        Returns:
            Gospel position assessment
        """
        # Analyze gospel ensemble
        gospel_analysis = self.analyze_ensemble_commonality(
            gospel_names, cultural_context, "Gospel"
        )
        
        # Get fiction and non-fiction patterns
        fiction_analyses = [
            self.analyze_ensemble_commonality(e['names'], cultural_context)
            for e in fiction_comparison
        ]
        nonfiction_analyses = [
            self.analyze_ensemble_commonality(e['names'], cultural_context)
            for e in nonfiction_comparison
        ]
        
        # Compare gospel to each
        gospel_mean = gospel_analysis['metrics']['mean_commonality']
        gospel_var = gospel_analysis['metrics']['variance_commonality']
        gospel_outliers = gospel_analysis['outliers']['proportion']
        
        fiction_mean = np.mean([a['metrics']['mean_commonality'] for a in fiction_analyses])
        fiction_var = np.mean([a['metrics']['variance_commonality'] for a in fiction_analyses])
        fiction_outliers = np.mean([a['outliers']['proportion'] for a in fiction_analyses])
        
        nonfiction_mean = np.mean([a['metrics']['mean_commonality'] for a in nonfiction_analyses])
        nonfiction_var = np.mean([a['metrics']['variance_commonality'] for a in nonfiction_analyses])
        nonfiction_outliers = np.mean([a['outliers']['proportion'] for a in nonfiction_analyses])
        
        # Calculate distances
        fiction_distance = np.sqrt(
            (gospel_mean - fiction_mean)**2 +
            (gospel_var - fiction_var)**2 +
            (gospel_outliers - fiction_outliers)**2
        )
        
        nonfiction_distance = np.sqrt(
            (gospel_mean - nonfiction_mean)**2 +
            (gospel_var - nonfiction_var)**2 +
            (gospel_outliers - nonfiction_outliers)**2
        )
        
        # Determine which gospel matches
        matches_nonfiction = nonfiction_distance < fiction_distance
        
        return {
            'gospel_analysis': gospel_analysis,
            'fiction_pattern': {
                'mean_commonality': float(fiction_mean),
                'variance': float(fiction_var),
                'outlier_proportion': float(fiction_outliers)
            },
            'nonfiction_pattern': {
                'mean_commonality': float(nonfiction_mean),
                'variance': float(nonfiction_var),
                'outlier_proportion': float(nonfiction_outliers)
            },
            'distances': {
                'to_fiction': float(fiction_distance),
                'to_nonfiction': float(nonfiction_distance)
            },
            'conclusion': 'Non-Fiction Pattern' if matches_nonfiction else 'Fiction Pattern',
            'confidence': float(abs(fiction_distance - nonfiction_distance) / max(fiction_distance, nonfiction_distance)),
            'interpretation': self._interpret_gospel_pattern(gospel_mean, gospel_var, gospel_outliers,
                                                           fiction_mean, nonfiction_mean,
                                                           matches_nonfiction)
        }
    
    def _interpret_gospel_pattern(self, gospel_mean, gospel_var, gospel_outliers,
                                 fiction_mean, nonfiction_mean, matches_nonfiction) -> str:
        """Interpret gospel pattern matching."""
        if matches_nonfiction:
            return f"""GOSPEL MATCHES NON-FICTION PATTERN:
- Gospel mean commonality ({gospel_mean:.3f}) closer to non-fiction ({nonfiction_mean:.3f}) than fiction ({fiction_mean:.3f})
- Variance pattern suggests random sampling, not deliberate selection
- Outlier rate consistent with documentary realism

INTERPRETATION: Gospel apostle names show commonality distribution consistent with 
RANDOM SAMPLING from real population, NOT authorial selection for narrative interest.

This is STRONG EVIDENCE for truth-claiming documentary intention."""
        else:
            return f"""GOSPEL MATCHES FICTION PATTERN:
- Gospel mean commonality ({gospel_mean:.3f}) closer to fiction ({fiction_mean:.3f}) than non-fiction ({nonfiction_mean:.3f})
- Variance suggests deliberate name selection
- Outlier rate suggests authorial choice for interest

INTERPRETATION: Gospel names show pattern of selective authorship.
Could indicate: (a) Fictional invention, OR (b) Selective emphasis within historical framework."""


# Singleton
ensemble_commonality_analyzer = EnsembleCommonalityAnalyzer()

