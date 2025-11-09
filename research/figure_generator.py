"""
Publication-Quality Figure Generator
====================================

Generates high-resolution, publication-ready figures for academic papers.
Meets Nature/Science journal standards with proper styling, color-blind friendly palettes.

Features:
- Vector graphics (SVG, PDF) for scalability
- Color-blind friendly palettes (viridis, plasma, colorblind-safe)
- Consistent styling across all figures
- Statistical annotations (p-values, effect sizes, n, CI bands)
- Multiple figure types (scatter, violin, forest plots, heatmaps, etc.)
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class PublicationFigureGenerator:
    """Generate publication-quality figures."""
    
    # Journal-approved color palettes (colorblind-safe)
    PALETTES = {
        'nature': ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4'],
        'science': ['#3B4992', '#EE0000', '#008B45', '#631879', '#008280', '#BB0021'],
        'colorblind': ['#0173b2', '#de8f05', '#029e73', '#cc78bc', '#ca9161', '#fbafe4'],
        'viridis': None,  # Use matplotlib's viridis
        'plasma': None,   # Use matplotlib's plasma
    }
    
    # Publication standards
    FIGURE_SIZES = {
        'single_column': (3.5, 2.625),  # inches
        'double_column': (7.0, 5.25),
        'full_page': (7.0, 9.0),
        'square': (4.0, 4.0)
    }
    
    DPI = 300  # Minimum for publication
    FONT_SIZES = {
        'title': 12,
        'axis_label': 10,
        'tick_label': 8,
        'legend': 8,
        'annotation': 7
    }
    
    def __init__(self, style: str = 'nature', output_dir: str = 'research/figures'):
        """
        Initialize figure generator.
        
        Args:
            style: Visual style ('nature', 'science', 'colorblind')
            output_dir: Directory to save figures
        """
        self.logger = logging.getLogger(__name__)
        self.style = style
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set matplotlib style
        self._configure_matplotlib()
        
        self.logger.info(f"PublicationFigureGenerator initialized (style: {style})")
    
    def _configure_matplotlib(self):
        """Configure matplotlib for publication quality."""
        plt.style.use('seaborn-v0_8-paper')
        
        # Set font to Times/Arial (commonly accepted)
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
        
        # Font sizes
        plt.rcParams['font.size'] = self.FONT_SIZES['tick_label']
        plt.rcParams['axes.labelsize'] = self.FONT_SIZES['axis_label']
        plt.rcParams['axes.titlesize'] = self.FONT_SIZES['title']
        plt.rcParams['xtick.labelsize'] = self.FONT_SIZES['tick_label']
        plt.rcParams['ytick.labelsize'] = self.FONT_SIZES['tick_label']
        plt.rcParams['legend.fontsize'] = self.FONT_SIZES['legend']
        
        # Line widths
        plt.rcParams['axes.linewidth'] = 1.0
        plt.rcParams['xtick.major.width'] = 1.0
        plt.rcParams['ytick.major.width'] = 1.0
        
        # DPI
        plt.rcParams['figure.dpi'] = self.DPI
        plt.rcParams['savefig.dpi'] = self.DPI
    
    def get_colors(self, n: int = None) -> List[str]:
        """Get colorblind-safe colors."""
        if self.style in ['viridis', 'plasma']:
            cmap = plt.cm.get_cmap(self.style)
            if n:
                return [cmap(i / n) for i in range(n)]
            return cmap
        
        colors = self.PALETTES.get(self.style, self.PALETTES['colorblind'])
        if n and n > len(colors):
            # Repeat colors if needed
            colors = colors * (n // len(colors) + 1)
        return colors[:n] if n else colors
    
    def scatter_with_regression(self, x: np.ndarray, y: np.ndarray,
                               xlabel: str, ylabel: str, title: str,
                               add_stats: bool = True,
                               figsize: str = 'single_column',
                               filename: Optional[str] = None) -> str:
        """
        Create scatter plot with regression line and confidence interval.
        
        Args:
            x, y: Data arrays
            xlabel, ylabel, title: Labels
            add_stats: Whether to add statistical annotations
            figsize: Figure size preset
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZES[figsize])
        
        colors = self.get_colors()
        
        # Scatter plot
        ax.scatter(x, y, alpha=0.6, s=30, color=colors[0], edgecolors='black', linewidth=0.5)
        
        # Regression line with CI
        from scipy import stats as sp_stats
        slope, intercept, r_value, p_value, std_err = sp_stats.linregress(x, y)
        
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        
        ax.plot(x_line, y_line, color=colors[1], linewidth=2, label=f'R² = {r_value**2:.3f}')
        
        # Confidence interval
        predict_error = np.sqrt(np.sum((y - (slope * x + intercept))**2) / (len(x) - 2))
        ci = 1.96 * predict_error  # 95% CI
        
        ax.fill_between(x_line, y_line - ci, y_line + ci, alpha=0.2, color=colors[1])
        
        # Statistical annotation
        if add_stats:
            stats_text = f'r = {r_value:.3f}\np = {p_value:.4f}\nn = {len(x)}'
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                   fontsize=self.FONT_SIZES['annotation'])
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(frameon=True, fancybox=False, edgecolor='black')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Save
        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_scatter.pdf"
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        fig.savefig(filepath.with_suffix('.png'), format='png', bbox_inches='tight')
        
        plt.close(fig)
        
        self.logger.info(f"Saved scatter plot to {filepath}")
        return str(filepath)
    
    def violin_plot_comparison(self, data: Dict[str, np.ndarray], ylabel: str, title: str,
                               add_stats: bool = True, figsize: str = 'single_column',
                               filename: Optional[str] = None) -> str:
        """
        Create violin plot for comparing distributions.
        
        Args:
            data: Dictionary mapping group names to data arrays
            ylabel: Y-axis label
            title: Plot title
            add_stats: Whether to add statistical annotations
            figsize: Figure size preset
            filename: Output filename
        
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZES[figsize])
        
        colors = self.get_colors(len(data))
        
        # Prepare data for seaborn
        plot_data = []
        for group, values in data.items():
            for val in values:
                plot_data.append({'Group': group, 'Value': val})
        
        import pandas as pd
        df = pd.DataFrame(plot_data)
        
        # Violin plot
        parts = ax.violinplot([data[g] for g in data.keys()], 
                             positions=range(len(data)),
                             showmeans=True, showmedians=True)
        
        # Color violins
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.7)
        
        # Statistical comparisons
        if add_stats and len(data) == 2:
            from scipy import stats as sp_stats
            groups = list(data.keys())
            t_stat, p_val = sp_stats.ttest_ind(data[groups[0]], data[groups[1]])
            
            # Add significance bar
            y_max = max([d.max() for d in data.values()])
            y_pos = y_max * 1.1
            
            ax.plot([0, 1], [y_pos, y_pos], 'k-', linewidth=1)
            
            # Significance stars
            if p_val < 0.001:
                sig_text = '***'
            elif p_val < 0.01:
                sig_text = '**'
            elif p_val < 0.05:
                sig_text = '*'
            else:
                sig_text = 'ns'
            
            ax.text(0.5, y_pos * 1.02, sig_text, ha='center',
                   fontsize=self.FONT_SIZES['annotation'])
        
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data.keys())
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Save
        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_violin.pdf"
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        fig.savefig(filepath.with_suffix('.png'), format='png', bbox_inches='tight')
        
        plt.close(fig)
        
        self.logger.info(f"Saved violin plot to {filepath}")
        return str(filepath)
    
    def forest_plot_effect_sizes(self, studies: List[Dict], title: str,
                                 figsize: str = 'single_column',
                                 filename: Optional[str] = None) -> str:
        """
        Create forest plot for effect sizes with confidence intervals.
        
        Args:
            studies: List of dicts with 'name', 'effect_size', 'ci_lower', 'ci_upper'
            title: Plot title
            figsize: Figure size preset
            filename: Output filename
        
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZES[figsize])
        
        colors = self.get_colors()
        
        n_studies = len(studies)
        y_positions = np.arange(n_studies)
        
        # Plot effect sizes and CIs
        for i, study in enumerate(studies):
            effect = study['effect_size']
            ci_lower = study['ci_lower']
            ci_upper = study['ci_upper']
            
            # Point estimate
            ax.plot(effect, i, 'o', color=colors[0], markersize=8, zorder=3)
            
            # CI line
            ax.plot([ci_lower, ci_upper], [i, i], color=colors[0], linewidth=2, zorder=2)
        
        # Reference line at 0
        ax.axvline(0, color='gray', linestyle='--', linewidth=1, zorder=1)
        
        # Labels
        ax.set_yticks(y_positions)
        ax.set_yticklabels([s['name'] for s in studies])
        ax.set_xlabel('Effect Size (Cohen\'s d)')
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Save
        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_forest.pdf"
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        fig.savefig(filepath.with_suffix('.png'), format='png', bbox_inches='tight')
        
        plt.close(fig)
        
        self.logger.info(f"Saved forest plot to {filepath}")
        return str(filepath)
    
    def heatmap_correlation(self, correlation_matrix: np.ndarray, labels: List[str],
                          title: str, figsize: str = 'square',
                          filename: Optional[str] = None) -> str:
        """
        Create correlation heatmap.
        
        Args:
            correlation_matrix: Square correlation matrix
            labels: Variable labels
            title: Plot title
            figsize: Figure size preset
            filename: Output filename
        
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZES[figsize])
        
        # Heatmap
        im = ax.imshow(correlation_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation', rotation=270, labelpad=20)
        
        # Ticks and labels
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)
        
        # Annotate with values
        for i in range(len(labels)):
            for j in range(len(labels)):
                text = ax.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                             ha='center', va='center', color='black' if abs(correlation_matrix[i, j]) < 0.5 else 'white',
                             fontsize=self.FONT_SIZES['annotation'])
        
        ax.set_title(title)
        
        plt.tight_layout()
        
        # Save
        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_heatmap.pdf"
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        fig.savefig(filepath.with_suffix('.png'), format='png', bbox_inches='tight')
        
        plt.close(fig)
        
        self.logger.info(f"Saved heatmap to {filepath}")
        return str(filepath)
    
    def time_series_with_ci(self, time: np.ndarray, values: np.ndarray,
                           ci_lower: np.ndarray, ci_upper: np.ndarray,
                           xlabel: str, ylabel: str, title: str,
                           figsize: str = 'double_column',
                           filename: Optional[str] = None) -> str:
        """
        Create time series plot with confidence intervals.
        
        Args:
            time: Time points
            values: Mean values
            ci_lower, ci_upper: Confidence interval bounds
            xlabel, ylabel, title: Labels
            figsize: Figure size preset
            filename: Output filename
        
        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.FIGURE_SIZES[figsize])
        
        colors = self.get_colors()
        
        # Main line
        ax.plot(time, values, color=colors[0], linewidth=2, label='Mean')
        
        # CI band
        ax.fill_between(time, ci_lower, ci_upper, alpha=0.3, color=colors[0], label='95% CI')
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(frameon=True, fancybox=False, edgecolor='black')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Save
        if not filename:
            filename = f"{title.replace(' ', '_').lower()}_timeseries.pdf"
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        fig.savefig(filepath.with_suffix('.png'), format='png', bbox_inches='tight')
        
        plt.close(fig)
        
        self.logger.info(f"Saved time series to {filepath}")
        return str(filepath)
    
    def multi_panel_figure(self, panel_configs: List[Dict], 
                          layout: Tuple[int, int],
                          figsize: str = 'double_column',
                          filename: str = 'multi_panel_figure.pdf') -> str:
        """
        Create multi-panel figure (common in academic papers).
        
        Args:
            panel_configs: List of panel specifications
            layout: (rows, cols) layout
            figsize: Figure size preset
            filename: Output filename
        
        Returns:
            Path to saved figure
        """
        fig = plt.figure(figsize=self.FIGURE_SIZES[figsize])
        gs = GridSpec(layout[0], layout[1], figure=fig, hspace=0.4, wspace=0.4)
        
        for i, config in enumerate(panel_configs):
            row = i // layout[1]
            col = i % layout[1]
            ax = fig.add_subplot(gs[row, col])
            
            # Add panel label (A, B, C, etc.)
            panel_label = chr(65 + i)  # A, B, C...
            ax.text(-0.1, 1.1, panel_label, transform=ax.transAxes,
                   fontsize=self.FONT_SIZES['title'], fontweight='bold')
            
            # Plot based on type
            # This would dispatch to appropriate plotting function
            # Simplified for now
            ax.set_title(config.get('title', ''))
        
        filepath = self.output_dir / filename
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        fig.savefig(filepath.with_suffix('.png'), format='png', bbox_inches='tight')
        
        plt.close(fig)
        
        self.logger.info(f"Saved multi-panel figure to {filepath}")
        return str(filepath)


# Singleton
figure_generator = PublicationFigureGenerator()

