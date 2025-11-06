"""
Figure Generation Module
Creates publication-ready visualizations for the name diversity manuscript.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set publication style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10


class FigureGenerator:
    """Creates all figures for the name diversity paper."""
    
    def __init__(self, processed_dir: str = "data/processed", figures_dir: str = "figures"):
        self.processed_dir = Path(processed_dir)
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(exist_ok=True)
        self.metrics_dir = self.processed_dir / "metrics"
        self.linguistics_dir = self.processed_dir / "country_linguistics"
    
    def fig1_usa_diversity_over_time(self):
        """
        Figure 1: U.S. name diversity time series (1880-2024).
        Shannon entropy by sex with middle-name prevalence overlay.
        """
        print("Creating Figure 1: U.S. diversity over time...")
        
        usa_metrics = pd.read_parquet(self.metrics_dir / "usa_diversity_metrics.parquet")
        middle_names = pd.read_parquet(self.processed_dir / "middle_name_prevalence.parquet")
        
        # Filter to yearly data (not decades)
        usa_yearly = usa_metrics[usa_metrics.get('period_type', 'year') != 'decade'].copy()
        
        if len(usa_yearly) == 0:
            print("  ⚠ No yearly data found, skipping")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Top panel: Shannon entropy by sex
        for sex in ['M', 'F']:
            data = usa_yearly[usa_yearly['sex'] == sex].sort_values('year')
            ax1.plot(data['year'], data['shannon_entropy'], 
                    marker='o', markersize=2, linewidth=1.5,
                    label=f'{"Male" if sex == "M" else "Female"}',
                    alpha=0.8)
        
        ax1.set_ylabel('Shannon Entropy (bits)', fontweight='bold')
        ax1.set_title('U.S. Name Diversity Over Time', fontweight='bold', fontsize=16)
        ax1.legend(loc='lower right')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(x=1960, color='red', linestyle='--', alpha=0.5, label='Cultural shift')
        
        # Bottom panel: HHI (concentration)
        for sex in ['M', 'F']:
            data = usa_yearly[usa_yearly['sex'] == sex].sort_values('year')
            ax2.plot(data['year'], data['hhi'], 
                    marker='o', markersize=2, linewidth=1.5,
                    label=f'{"Male" if sex == "M" else "Female"}',
                    alpha=0.8)
        
        ax2.set_ylabel('HHI (Concentration)', fontweight='bold')
        ax2.set_xlabel('Year', fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=1500, color='orange', linestyle=':', alpha=0.5, label='Moderate concentration threshold')
        
        plt.tight_layout()
        output_path = self.figures_dir / "fig1_usa_diversity_time_series.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved → {output_path}")
    
    def fig2_cross_national_comparison(self):
        """
        Figure 2: Cross-national diversity comparison bar chart.
        Shannon entropy and HHI for all 11 countries (2020).
        """
        print("Creating Figure 2: Cross-national comparison...")
        
        comparison = pd.read_csv(self.metrics_dir / "comprehensive_country_comparison.csv")
        
        # Filter to countries with metrics
        comparison = comparison[comparison['shannon_entropy_estimate'].notna()].copy()
        comparison = comparison.sort_values('shannon_entropy_estimate', ascending=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Left: Shannon entropy
        colors = ['#2ecc71' if x > 14 else '#f39c12' if x > 13 else '#e74c3c' 
                 for x in comparison['shannon_entropy_estimate']]
        
        ax1.barh(comparison['country'], comparison['shannon_entropy_estimate'], color=colors, alpha=0.8)
        ax1.set_xlabel('Shannon Entropy (bits)', fontweight='bold')
        ax1.set_title('Name Diversity by Country (2020)', fontweight='bold', fontsize=14)
        ax1.grid(axis='x', alpha=0.3)
        ax1.axvline(x=14, color='green', linestyle='--', alpha=0.5, label='High diversity')
        ax1.axvline(x=13, color='orange', linestyle='--', alpha=0.5, label='Moderate')
        
        # Right: HHI (inverted for visual consistency)
        colors2 = ['#2ecc71' if x < 500 else '#f39c12' if x < 1500 else '#e74c3c' 
                  for x in comparison['hhi_estimate']]
        
        ax2.barh(comparison['country'], comparison['hhi_estimate'], color=colors2, alpha=0.8)
        ax2.set_xlabel('HHI (Concentration Index)', fontweight='bold')
        ax2.set_title('Name Concentration by Country (2020)', fontweight='bold', fontsize=14)
        ax2.grid(axis='x', alpha=0.3)
        ax2.axvline(x=1500, color='orange', linestyle='--', alpha=0.5)
        ax2.axvline(x=500, color='green', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        output_path = self.figures_dir / "fig2_cross_national_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved → {output_path}")
    
    def fig3_middle_name_effect(self):
        """
        Figure 3: Middle name prevalence over time by country.
        Shows U.S./Germany increase vs. Spain/China flatline.
        """
        print("Creating Figure 3: Middle name prevalence...")
        
        middle = pd.read_parquet(self.processed_dir / "middle_name_prevalence.parquet")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        highlight_countries = ['USA', 'Germany', 'UK', 'Mexico', 'China', 'Egypt']
        
        for country in highlight_countries:
            data = middle[middle['country'] == country].sort_values('decade')
            style = '-' if country in ['USA', 'Germany', 'UK'] else '--'
            linewidth = 2.5 if country in ['USA', 'Germany'] else 1.5
            ax.plot(data['decade'], data['middle_name_prevalence'] * 100,
                   marker='o', linestyle=style, linewidth=linewidth,
                   label=country, markersize=4, alpha=0.8)
        
        ax.set_xlabel('Decade', fontweight='bold')
        ax.set_ylabel('Middle Name Prevalence (%)', fontweight='bold')
        ax.set_title('Middle Name Adoption Over Time', fontweight='bold', fontsize=16)
        ax.legend(loc='upper left', ncol=2)
        ax.grid(True, alpha=0.3)
        ax.axvline(x=1950, color='red', linestyle=':', alpha=0.5, label='Post-WWII')
        ax.set_ylim(-5, 105)
        
        # Annotation
        ax.annotate('Germany adopts middle names\n(American influence)', 
                   xy=(1960, 20), xytext=(1970, 45),
                   arrowprops=dict(arrowstyle='->', color='gray', lw=1.5),
                   fontsize=10, ha='left')
        
        plt.tight_layout()
        output_path = self.figures_dir / "fig3_middle_name_prevalence.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved → {output_path}")
    
    def fig4_dominant_names(self):
        """
        Figure 4: Muhammad/María/José prevalence by country.
        Shows concentration effect of dominant names.
        """
        print("Creating Figure 4: Dominant name concentration...")
        
        dominant = pd.read_parquet(self.processed_dir / "dominant_names_prevalence.parquet")
        
        # Filter to 2020, key countries
        recent = dominant[dominant['decade'] == 2020].copy()
        key_names = recent[recent['dominant_name'].isin([
            'Muhammad', 'María (including compounds)', 'José (including compounds)',
            'Wang (surname)', 'Top given name (varies by era)'
        ])]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Group by country for clarity
        countries = key_names['country'].unique()
        x_pos = np.arange(len(key_names))
        
        colors_map = {
            'Egypt': '#e74c3c',
            'India': '#f39c12',
            'Nigeria': '#9b59b6',
            'China': '#3498db',
            'Mexico': '#1abc9c',
            'USA': '#2ecc71'
        }
        
        colors = [colors_map.get(c, '#95a5a6') for c in key_names['country']]
        
        ax.bar(x_pos, key_names['prevalence_pct'], color=colors, alpha=0.8)
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f"{row['dominant_name'][:15]}...\n({row['country']})" 
                           for _, row in key_names.iterrows()], 
                          rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('Prevalence (%)', fontweight='bold')
        ax.set_title('Dominant Name Concentration (2020)', fontweight='bold', fontsize=16)
        ax.grid(axis='y', alpha=0.3)
        
        # Reference line
        ax.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='High concentration (>10%)')
        ax.legend()
        
        plt.tight_layout()
        output_path = self.figures_dir / "fig4_dominant_name_concentration.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved → {output_path}")
    
    def fig5_country_name_beauty(self):
        """
        Figure 5: Country name beauty rankings.
        Scatter plot of harshness vs. melodiousness.
        """
        print("Creating Figure 5: Country name aesthetics...")
        
        beauty_file = self.linguistics_dir / "country_name_beauty_rankings.csv"
        if not beauty_file.exists():
            print("  ⚠ Beauty rankings not found, skipping")
            return
        
        beauty = pd.read_csv(beauty_file)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Scatter plot
        scatter = ax.scatter(beauty['harshness'], beauty['melodiousness'],
                           s=200, alpha=0.7, c=beauty['beauty_rank'],
                           cmap='RdYlGn_r', edgecolors='black', linewidth=1.5)
        
        # Label each point
        for idx, row in beauty.iterrows():
            ax.annotate(row['name'], 
                       (row['harshness'], row['melodiousness']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=10, fontweight='bold' if row['name'] == 'America' else 'normal',
                       color='red' if row['name'] == 'America' else 'black')
        
        ax.set_xlabel('Phonetic Harshness Score', fontweight='bold', fontsize=12)
        ax.set_ylabel('Melodiousness Score', fontweight='bold', fontsize=12)
        ax.set_title('Country Name Phonetic Analysis\n(America highlighted in red)', 
                    fontweight='bold', fontsize=16)
        ax.grid(True, alpha=0.3)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Beauty Rank (1=best)', fontweight='bold')
        
        plt.tight_layout()
        output_path = self.figures_dir / "fig5_country_name_beauty.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved → {output_path}")
    
    def fig6_diversity_vs_middle_names(self):
        """
        Figure 6: Scatter plot showing relationship between middle name prevalence and diversity.
        Tests hypothesis: middle names → higher diversity.
        """
        print("Creating Figure 6: Diversity vs. middle names...")
        
        comparison = pd.read_csv(self.metrics_dir / "comprehensive_country_comparison.csv")
        comparison = comparison[comparison['shannon_entropy_estimate'].notna()].copy()
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        scatter = ax.scatter(comparison['middle_name_prevalence'] * 100,
                           comparison['shannon_entropy_estimate'],
                           s=300, alpha=0.7, 
                           c=comparison['hhi_estimate'],
                           cmap='RdYlGn_r', edgecolors='black', linewidth=2)
        
        # Label points
        for idx, row in comparison.iterrows():
            ax.annotate(row['country'],
                       (row['middle_name_prevalence'] * 100, row['shannon_entropy_estimate']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=11, fontweight='bold' if row['country'] == 'USA' else 'normal')
        
        ax.set_xlabel('Middle Name Prevalence (%)', fontweight='bold', fontsize=12)
        ax.set_ylabel('Shannon Entropy (Diversity)', fontweight='bold', fontsize=12)
        ax.set_title('Diversity vs. Middle Name Prevalence (2020)\nSize = HHI (concentration)', 
                    fontweight='bold', fontsize=16)
        ax.grid(True, alpha=0.3)
        
        # Trend line
        mask = comparison['middle_name_prevalence'].notna() & comparison['shannon_entropy_estimate'].notna()
        if mask.sum() > 2:
            z = np.polyfit(comparison.loc[mask, 'middle_name_prevalence'] * 100, 
                          comparison.loc[mask, 'shannon_entropy_estimate'], 1)
            p = np.poly1d(z)
            x_trend = np.linspace(0, 100, 100)
            ax.plot(x_trend, p(x_trend), "r--", alpha=0.5, linewidth=2, label='Trend')
            ax.legend()
        
        plt.tight_layout()
        output_path = self.figures_dir / "fig6_diversity_vs_middle_names.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved → {output_path}")
    
    def generate_all_figures(self):
        """Generate all figures for the manuscript."""
        print("\n" + "="*60)
        print("GENERATING PUBLICATION FIGURES")
        print("="*60 + "\n")
        
        self.fig1_usa_diversity_over_time()
        self.fig2_cross_national_comparison()
        self.fig3_middle_name_effect()
        self.fig4_dominant_names()
        self.fig5_country_name_beauty()
        self.fig6_diversity_vs_middle_names()
        
        print("\n" + "="*60)
        print("FIGURE GENERATION COMPLETE")
        print("="*60)
        print(f"✓ All figures saved to {self.figures_dir}")
        print("\nFigures created:")
        print("  1. U.S. diversity time series (1880-2024)")
        print("  2. Cross-national comparison (2020)")
        print("  3. Middle name prevalence trends")
        print("  4. Dominant name concentration")
        print("  5. Country name phonetic beauty")
        print("  6. Diversity vs. middle name scatter")


if __name__ == "__main__":
    generator = FigureGenerator()
    generator.generate_all_figures()

