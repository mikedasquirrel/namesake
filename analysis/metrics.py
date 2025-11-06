"""
Diversity Metrics Module
Computes Shannon entropy, Simpson index, Gini, Top-N concentration, and HHI.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class DiversityMetrics:
    """Calculates diversity indices for name distributions."""
    
    def __init__(self, processed_dir: str = "data/processed"):
        self.processed_dir = Path(processed_dir)
        self.results_dir = self.processed_dir / "metrics"
        self.results_dir.mkdir(exist_ok=True)
    
    def shannon_entropy(self, counts: pd.Series) -> float:
        """
        Calculate Shannon entropy H = -Σ(p_i * log2(p_i))
        Higher values = more diversity
        Theoretical max = log2(n) for uniform distribution
        """
        if len(counts) == 0:
            return 0.0
        
        total = counts.sum()
        if total == 0:
            return 0.0
        
        proportions = counts / total
        # Filter out zeros to avoid log(0)
        proportions = proportions[proportions > 0]
        
        entropy = -np.sum(proportions * np.log2(proportions))
        return entropy
    
    def simpson_index(self, counts: pd.Series) -> float:
        """
        Calculate Simpson's diversity index D = 1 - Σ(p_i²)
        Range: [0, 1], higher = more diversity
        Represents probability that two random individuals are different species/names
        """
        if len(counts) == 0:
            return 0.0
        
        total = counts.sum()
        if total == 0:
            return 0.0
        
        proportions = counts / total
        simpson = 1 - np.sum(proportions ** 2)
        return simpson
    
    def gini_coefficient(self, counts: pd.Series) -> float:
        """
        Calculate Gini coefficient (measure of inequality)
        Range: [0, 1], higher = more inequality (less diversity)
        0 = perfect equality, 1 = maximum inequality
        """
        if len(counts) == 0:
            return 0.0
        
        sorted_counts = np.sort(counts.values)
        n = len(sorted_counts)
        
        if n == 0 or sorted_counts.sum() == 0:
            return 0.0
        
        cumsum = np.cumsum(sorted_counts)
        gini = (2 * np.sum((np.arange(1, n + 1)) * sorted_counts)) / (n * cumsum[-1]) - (n + 1) / n
        
        return gini
    
    def top_n_concentration(self, counts: pd.Series, n: int = 10) -> float:
        """
        Calculate what percentage of total is held by top N names
        Range: [0, 100]
        """
        if len(counts) == 0:
            return 0.0
        
        total = counts.sum()
        if total == 0:
            return 0.0
        
        top_n = counts.nlargest(min(n, len(counts)))
        concentration = (top_n.sum() / total) * 100
        
        return concentration
    
    def herfindahl_hirschman_index(self, counts: pd.Series) -> float:
        """
        Calculate HHI = Σ(market_share_i²) * 10000
        Range: [0, 10000]
        <1500 = competitive/diverse
        1500-2500 = moderate concentration
        >2500 = high concentration
        """
        if len(counts) == 0:
            return 0.0
        
        total = counts.sum()
        if total == 0:
            return 0.0
        
        market_shares = (counts / total) * 100
        hhi = np.sum(market_shares ** 2)
        
        return hhi
    
    def effective_number_of_names(self, counts: pd.Series) -> float:
        """
        Calculate effective number of names (ENS) = exp(Shannon entropy)
        Interpretable as "equivalent number of equally-common names"
        """
        entropy = self.shannon_entropy(counts)
        return 2 ** entropy
    
    def compute_all_metrics(self, counts: pd.Series, label: str = "distribution") -> Dict:
        """Compute all diversity metrics for a name distribution."""
        metrics = {
            'label': label,
            'total_unique_names': len(counts),
            'total_count': int(counts.sum()),
            'shannon_entropy': self.shannon_entropy(counts),
            'simpson_index': self.simpson_index(counts),
            'gini_coefficient': self.gini_coefficient(counts),
            'top_10_concentration_pct': self.top_n_concentration(counts, 10),
            'top_50_concentration_pct': self.top_n_concentration(counts, 50),
            'top_100_concentration_pct': self.top_n_concentration(counts, 100),
            'hhi': self.herfindahl_hirschman_index(counts),
            'effective_num_names': self.effective_number_of_names(counts)
        }
        
        return metrics
    
    def analyze_usa_diversity(self) -> pd.DataFrame:
        """
        Analyze U.S. name diversity over time.
        Compute metrics by year, sex, and cumulatively.
        """
        print("Analyzing U.S. name diversity...")
        
        usa_file = self.processed_dir / "usa_names_processed.parquet"
        if not usa_file.exists():
            print("  ✗ U.S. processed data not found")
            return None
        
        df = pd.read_parquet(usa_file)
        
        results = []
        
        # Yearly metrics by sex
        for year in sorted(df['year'].unique()):
            year_data = df[df['year'] == year]
            
            for sex in ['M', 'F']:
                sex_data = year_data[year_data['sex'] == sex]
                if len(sex_data) == 0:
                    continue
                
                name_counts = sex_data.groupby('name')['count'].sum()
                metrics = self.compute_all_metrics(
                    name_counts, 
                    label=f"USA_{year}_{sex}"
                )
                metrics['year'] = year
                metrics['sex'] = sex
                metrics['country'] = 'USA'
                results.append(metrics)
        
        # Decade aggregates
        df['decade'] = (df['year'] // 10) * 10
        for decade in sorted(df['decade'].unique()):
            decade_data = df[df['decade'] == decade]
            
            for sex in ['M', 'F']:
                sex_data = decade_data[decade_data['sex'] == sex]
                if len(sex_data) == 0:
                    continue
                
                name_counts = sex_data.groupby('name')['count'].sum()
                metrics = self.compute_all_metrics(
                    name_counts,
                    label=f"USA_{decade}s_{sex}"
                )
                metrics['year'] = decade
                metrics['sex'] = sex
                metrics['country'] = 'USA'
                metrics['period_type'] = 'decade'
                results.append(metrics)
        
        results_df = pd.DataFrame(results)
        output_path = self.results_dir / "usa_diversity_metrics.parquet"
        results_df.to_parquet(output_path, index=False)
        
        print(f"  ✓ Computed {len(results_df):,} metric sets → {output_path}")
        return results_df
    
    def create_comparative_diversity_estimates(self) -> pd.DataFrame:
        """
        Create estimated diversity metrics for countries without full data.
        Based on dominant name prevalence and naming structures.
        """
        print("Creating comparative diversity estimates...")
        
        # Load dominant names data
        dominant_file = self.processed_dir / "dominant_names_prevalence.parquet"
        dominant_df = pd.read_parquet(dominant_file)
        
        estimates = []
        
        # For each country/decade, estimate diversity based on top name concentration
        countries = dominant_df['country'].unique()
        
        for country in countries:
            country_data = dominant_df[dominant_df['country'] == country]
            
            for decade in sorted(country_data['decade'].unique()):
                decade_data = country_data[country_data['decade'] == decade]
                
                # Calculate HHI estimate from top concentration
                if len(decade_data) > 0:
                    avg_hhi = decade_data['hhi_estimate'].mean() * 10000
                    avg_top_conc = decade_data['top_5_concentration'].mean()
                    
                    # Estimate other metrics from HHI
                    # High HHI → low Shannon, low Simpson
                    estimated_shannon = max(2.0, 15.0 - (avg_hhi / 500))
                    estimated_simpson = max(0.5, 0.98 - (avg_hhi / 5000))
                    estimated_gini = min(0.95, avg_hhi / 10500)
                    
                    estimates.append({
                        'country': country,
                        'decade': decade,
                        'hhi_estimate': avg_hhi,
                        'top_5_concentration_estimate': avg_top_conc,
                        'shannon_entropy_estimate': estimated_shannon,
                        'simpson_index_estimate': estimated_simpson,
                        'gini_estimate': estimated_gini,
                        'diversity_rank': self._rank_diversity(avg_hhi)
                    })
        
        estimates_df = pd.DataFrame(estimates)
        output_path = self.results_dir / "comparative_diversity_estimates.parquet"
        estimates_df.to_parquet(output_path, index=False)
        
        print(f"  ✓ Created diversity estimates → {output_path}")
        return estimates_df
    
    def _rank_diversity(self, hhi: float) -> str:
        """Categorize diversity level based on HHI."""
        if hhi < 150:
            return "Very High Diversity"
        elif hhi < 500:
            return "High Diversity"
        elif hhi < 1500:
            return "Moderate Diversity"
        elif hhi < 2500:
            return "Low Diversity"
        else:
            return "Very Low Diversity"
    
    def analyze_middle_name_effect(self) -> pd.DataFrame:
        """
        Analyze how middle name prevalence affects effective diversity.
        Hypothesis: Middle names expand the name space, increasing effective diversity.
        """
        print("Analyzing middle name effect on diversity...")
        
        middle_file = self.processed_dir / "middle_name_prevalence.parquet"
        middle_df = pd.read_parquet(middle_file)
        
        # Calculate effective diversity multiplier from middle names
        middle_df['diversity_multiplier'] = 1 + (middle_df['middle_name_prevalence'] * 0.5)
        # Assumption: middle names add ~50% more diversity when prevalent
        
        # Categorize countries by middle name adoption
        middle_df['middle_name_category'] = middle_df['middle_name_prevalence'].apply(
            lambda x: 'Very High (>80%)' if x > 0.8 else
                     'High (50-80%)' if x > 0.5 else
                     'Low (10-50%)' if x > 0.1 else
                     'None/Rare (<10%)'
        )
        
        output_path = self.results_dir / "middle_name_diversity_effect.parquet"
        middle_df.to_parquet(output_path, index=False)
        
        print(f"  ✓ Analyzed middle name effects → {output_path}")
        return middle_df
    
    def create_comprehensive_comparison(self) -> pd.DataFrame:
        """
        Create master comparison table across all countries.
        Combines actual metrics (USA) with estimates (others).
        """
        print("Creating comprehensive country comparison...")
        
        # Load taxonomy for context
        taxonomy_file = self.processed_dir / "naming_structure_taxonomy.parquet"
        taxonomy = pd.read_parquet(taxonomy_file)
        
        # Load diversity estimates
        estimates_file = self.results_dir / "comparative_diversity_estimates.parquet"
        if estimates_file.exists():
            estimates = pd.read_parquet(estimates_file)
            # Get most recent decade (2020)
            recent = estimates[estimates['decade'] == 2020].copy()
        else:
            recent = pd.DataFrame()
        
        # Load middle name data
        middle_file = self.results_dir / "middle_name_diversity_effect.parquet"
        if middle_file.exists():
            middle = pd.read_parquet(middle_file)
            recent_middle = middle[middle['decade'] == 2020][['country', 'middle_name_prevalence', 'middle_name_category']]
        else:
            recent_middle = pd.DataFrame()
        
        # Merge all data
        if len(recent) > 0 and len(recent_middle) > 0:
            comparison = taxonomy.merge(recent, on='country', how='left')
            comparison = comparison.merge(recent_middle, on='country', how='left')
        else:
            comparison = taxonomy
        
        output_path = self.results_dir / "comprehensive_country_comparison.parquet"
        comparison.to_parquet(output_path, index=False)
        
        # Also save as CSV for easy viewing
        comparison.to_csv(output_path.with_suffix('.csv'), index=False)
        
        print(f"  ✓ Created comprehensive comparison → {output_path}")
        return comparison
    
    def compute_all_metrics_pipeline(self):
        """Run complete metrics computation pipeline."""
        print("\n" + "="*60)
        print("DIVERSITY METRICS COMPUTATION")
        print("="*60 + "\n")
        
        results = {}
        
        # Analyze USA data (we have actual data)
        results['usa'] = self.analyze_usa_diversity()
        
        # Create estimates for other countries
        results['estimates'] = self.create_comparative_diversity_estimates()
        
        # Analyze middle name effect
        results['middle_names'] = self.analyze_middle_name_effect()
        
        # Create comprehensive comparison
        results['comparison'] = self.create_comprehensive_comparison()
        
        print("\n" + "="*60)
        print("METRICS COMPUTATION COMPLETE")
        print("="*60)
        print(f"✓ Results saved to {self.results_dir}")
        print("\nKey outputs:")
        print("  - usa_diversity_metrics.parquet: Full U.S. time series")
        print("  - comparative_diversity_estimates.parquet: Global estimates")
        print("  - middle_name_diversity_effect.parquet: Middle name analysis")
        print("  - comprehensive_country_comparison.csv: Master comparison")
        
        return results


if __name__ == "__main__":
    calculator = DiversityMetrics()
    calculator.compute_all_metrics_pipeline()

