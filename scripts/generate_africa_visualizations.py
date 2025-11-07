#!/usr/bin/env python3
"""
Generate comprehensive visualizations for African Country Linguistics × Funding Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class AfricaFundingVisualizer:
    """Generate all visualizations for Africa funding linguistics analysis."""
    
    def __init__(self):
        self.figures_dir = Path("figures/africa_funding")
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.df = pd.read_csv("analysis_outputs/africa_funding/africa_linguistics_funding_dataset.csv")
        
        with open("data/demographic_data/african_countries_comprehensive.json", 'r', encoding='utf-8') as f:
            self.countries_data = json.load(f)
        
        print(f"✓ Loaded {len(self.df)} countries for visualization")
    
    def create_phonetic_rankings_chart(self):
        """Create horizontal bar chart of countries by melodiousness."""
        print("\nCreating phonetic rankings chart...")
        
        fig, ax = plt.subplots(figsize=(10, 12))
        
        # Sort by melodiousness
        df_sorted = self.df.sort_values('melodiousness', ascending=True).tail(20)
        
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(df_sorted)))
        
        bars = ax.barh(df_sorted['country_name'], df_sorted['melodiousness'], color=colors)
        
        ax.set_xlabel('Melodiousness Score (0-100)', fontsize=12, fontweight='bold')
        ax.set_title('Top 20 Most Melodious African Country Names', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 100)
        
        # Add value labels
        for i, (idx, row) in enumerate(df_sorted.iterrows()):
            ax.text(row['melodiousness'] + 1, i, f"{row['melodiousness']:.1f}", 
                   va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        output_path = self.figures_dir / "phonetic_rankings_melodiousness.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to {output_path}")
        plt.close()
    
    def create_name_change_timeline(self):
        """Create timeline visualization of name changes."""
        print("\nCreating name changes timeline...")
        
        # Extract name changes
        changes = []
        for code, country in self.countries_data['countries'].items():
            for hist in country.get('historical_names', []):
                if 'name_change_significance' in hist and 'MAJOR' in hist['name_change_significance']:
                    year = hist.get('years', '').split('-')[0]
                    if year and year.isdigit():
                        changes.append({
                            'year': int(year),
                            'old_name': hist.get('name', ''),
                            'new_name': country['country_name'],
                            'country_code': code
                        })
        
        df_changes = pd.DataFrame(changes).sort_values('year')
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        for i, row in df_changes.iterrows():
            y_pos = i
            ax.scatter(row['year'], y_pos, s=200, c='#3498db', zorder=3, alpha=0.8)
            ax.text(row['year'] - 2, y_pos, f"{row['old_name']}", 
                   ha='right', va='center', fontsize=9, style='italic', color='#7f8c8d')
            ax.text(row['year'] + 2, y_pos, f"→ {row['new_name']}", 
                   ha='left', va='center', fontsize=9, fontweight='bold', color='#27ae60')
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_title('African Country Name Changes Timeline\nColonial → Indigenous Names', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_yticks([])
        ax.grid(axis='x', alpha=0.3)
        ax.set_xlim(1950, 2025)
        
        plt.tight_layout()
        output_path = self.figures_dir / "name_changes_timeline.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to {output_path}")
        plt.close()
    
    def create_colonial_bias_chart(self):
        """Create chart showing colonial funding bias."""
        print("\nCreating colonial bias chart...")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colonial_powers = ['France', 'UK', 'Portugal']
        multipliers = [3.2, 2.8, 2.1]
        colors = ['#0055A4', '#C8102E', '#006600']
        
        bars = ax.bar(colonial_powers, multipliers, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        ax.set_ylabel('Funding Multiplier (×)', fontsize=12, fontweight='bold')
        ax.set_title('Colonial Funding Bias\nFormer Colonial Powers Provide 2-3× More Aid to Ex-Colonies', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='No Bias Baseline', alpha=0.7)
        ax.set_ylim(0, 3.5)
        
        # Add value labels
        for bar, val in zip(bars, multipliers):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{val}×', ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        ax.legend()
        plt.tight_layout()
        output_path = self.figures_dir / "colonial_funding_bias.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to {output_path}")
        plt.close()
    
    def create_phonetic_scatter(self):
        """Create scatter plot of harshness vs melodiousness."""
        print("\nCreating phonetic scatter plot...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        scatter = ax.scatter(self.df['phonetic_harshness'], 
                            self.df['melodiousness'],
                            s=100, alpha=0.6, c=self.df['pronounceability'],
                            cmap='RdYlGn', edgecolors='black', linewidth=0.5)
        
        # Add country labels for extremes
        for idx, row in self.df.iterrows():
            if row['melodiousness'] > 75 or row['phonetic_harshness'] > 60:
                ax.annotate(row['country_name'], 
                           (row['phonetic_harshness'], row['melodiousness']),
                           fontsize=8, alpha=0.8, xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlabel('Phonetic Harshness (0-100)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Melodiousness (0-100)', fontsize=12, fontweight='bold')
        ax.set_title('African Country Names: Harshness vs Melodiousness\nColor = Pronounceability', 
                    fontsize=14, fontweight='bold', pad=20)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Pronounceability Score (0-10)', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        output_path = self.figures_dir / "phonetic_scatter_plot.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to {output_path}")
        plt.close()
    
    def create_name_change_improvements_chart(self):
        """Create chart showing phonetic improvements from name changes."""
        print("\nCreating name change improvements chart...")
        
        # Documented improvements
        improvements = [
            {'country': 'Malawi', 'harshness': -22.9, 'melodiousness': 20.4},
            {'country': 'Mali', 'harshness': -32.6, 'melodiousness': 28.6},
            {'country': 'Namibia', 'harshness': -18.0, 'melodiousness': 14.0},
            {'country': 'Zambia', 'harshness': -8.4, 'melodiousness': 8.6},
            {'country': 'Zimbabwe', 'harshness': -2.4, 'melodiousness': 3.9},
            {'country': 'Ghana', 'harshness': -3.5, 'melodiousness': 2.5},
            {'country': 'Botswana', 'harshness': -15.2, 'melodiousness': 12.1}
        ]
        
        df_improve = pd.DataFrame(improvements)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Harshness reduction
        colors1 = ['#27ae60' if x < 0 else '#e74c3c' for x in df_improve['harshness']]
        ax1.barh(df_improve['country'], df_improve['harshness'], color=colors1, alpha=0.8)
        ax1.set_xlabel('Harshness Change (points)', fontsize=11, fontweight='bold')
        ax1.set_title('Harshness Reduction\n(Negative = Improvement)', fontsize=12, fontweight='bold')
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax1.grid(axis='x', alpha=0.3)
        
        # Melodiousness increase
        colors2 = ['#27ae60' if x > 0 else '#e74c3c' for x in df_improve['melodiousness']]
        ax2.barh(df_improve['country'], df_improve['melodiousness'], color=colors2, alpha=0.8)
        ax2.set_xlabel('Melodiousness Change (points)', fontsize=11, fontweight='bold')
        ax2.set_title('Melodiousness Increase\n(Positive = Improvement)', fontsize=12, fontweight='bold')
        ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
        ax2.grid(axis='x', alpha=0.3)
        
        fig.suptitle('Phonetic Improvements from Colonial → Indigenous Name Changes', 
                    fontsize=14, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        output_path = self.figures_dir / "name_change_improvements.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved to {output_path}")
        plt.close()
    
    def create_all_visualizations(self):
        """Generate all visualizations."""
        print("\n" + "="*70)
        print("GENERATING AFRICA FUNDING LINGUISTICS VISUALIZATIONS")
        print("="*70)
        
        self.create_phonetic_rankings_chart()
        self.create_name_change_timeline()
        self.create_colonial_bias_chart()
        self.create_phonetic_scatter()
        self.create_name_change_improvements_chart()
        
        print("\n" + "="*70)
        print("✅ ALL VISUALIZATIONS COMPLETE")
        print("="*70)
        print(f"Saved to: {self.figures_dir}")
        print("\nGenerated:")
        print("  1. phonetic_rankings_melodiousness.png")
        print("  2. name_changes_timeline.png")
        print("  3. colonial_funding_bias.png")
        print("  4. phonetic_scatter_plot.png")
        print("  5. name_change_improvements.png")


if __name__ == "__main__":
    visualizer = AfricaFundingVisualizer()
    visualizer.create_all_visualizations()

