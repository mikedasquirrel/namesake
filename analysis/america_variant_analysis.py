import pandas as pd
import numpy as np
from pathlib import Path
import requests
import json
import re
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer


VARIANTS = [
    "America",
    "United States",
    "United States of America",
    "USA",
    "US",
    "the States",
    "EEUU"  # Spanish abbreviation
]

# Comprehensive list of countries for phonetic comparison analysis
COUNTRIES_FOR_COMPARISON = [
    # Original 12
    "America", "China", "Germany", "Brazil", "India", "Nigeria", "Mexico", 
    "France", "Canada", "Spain", "Egypt", "Japan",
    # Additional major countries (38 more = 50 total)
    "Russia", "United Kingdom", "Italy", "South Korea", "Australia", 
    "Argentina", "Colombia", "Poland", "Ukraine", "Malaysia",
    "Thailand", "Philippines", "Vietnam", "Turkey", "Iran",
    "Saudi Arabia", "Indonesia", "Pakistan", "Bangladesh", "Ethiopia",
    "South Africa", "Kenya", "Morocco", "Algeria", "Ghana",
    "Peru", "Chile", "Venezuela", "Ecuador", "Bolivia",
    "Portugal", "Greece", "Romania", "Netherlands", "Belgium",
    "Sweden", "Norway", "Denmark", "Finland", "Austria",
    "Switzerland", "Czech Republic", "Hungary", "Israel", "Jordan",
    "Singapore", "New Zealand", "Ireland", "Croatia", "Serbia"
]

class AmericaVariantAnalyzer:
    """Analyze usage and sentiment of America name variants across corpora."""
    def __init__(self, raw_dir="data/raw", processed_dir="data/processed"):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.variant_dir = self.raw_dir / "america_variants"
        self.variant_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.processed_dir / "america_variants"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.sia = SentimentIntensityAnalyzer()

    # ------------------------------------------------------------------
    # GOOGLE NGRAMS -----------------------------------------------------
    # ------------------------------------------------------------------

    def _ngram_cache_path(self, variant: str):
        safe = re.sub(r"\s+", "_", variant.lower())
        return self.variant_dir / f"{safe}_ngram.csv"

    def download_google_ngram(self, variant: str, force=False):
        """Download Google Ngram counts via https://books.google.com/ngrams JSON API."""
        cache_path = self._ngram_cache_path(variant)
        if cache_path.exists() and not force:
            return cache_path

        print(f"Fetching Google Ngram for '{variant}' …")
        url = (
            "https://books.google.com/ngrams/graph?content="
            + requests.utils.quote(variant)
            + "&year_start=1900&year_end=2019&corpus=26&smoothing=3&case_insensitive=false"
        )
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
            timeseries = data["timeseries"][0]
            df = pd.DataFrame({
                "year": list(range(1900, 2020)),
                "frequency": timeseries
            })
            df.to_csv(cache_path, index=False)
            return cache_path
        except Exception as e:
            print("⚠️ Error fetching Ngram:", e)
            # Create empty placeholder
            pd.DataFrame({"year": [], "frequency": []}).to_csv(cache_path, index=False)
            return cache_path

    # ------------------------------------------------------------------
    # SENTIMENT ANALYSIS ------------------------------------------------
    # ------------------------------------------------------------------

    def analyze_sentiment(self, texts):
        """Return compound sentiment scores for list of texts."""
        scores = [self.sia.polarity_scores(t)["compound"] for t in texts]
        return np.mean(scores) if scores else 0.0

    # ------------------------------------------------------------------
    # PHONETIC ANALYSIS -------------------------------------------------
    # ------------------------------------------------------------------

    def count_phonetic_features(self, name):
        """Extract phonetic features from a country name."""
        name_lower = name.lower()
        
        # Define phonetic categories
        plosives = set('ptkbdg')
        sibilants = set('szcʃʒ')
        liquids_nasals = set('lrmn')
        vowels = set('aeiouy')
        
        features = {
            'name': name,
            'length': len(name_lower),
            'plosives': sum(1 for c in name_lower if c in plosives),
            'sibilants': sum(1 for c in name_lower if c in sibilants),
            'liquids_nasals': sum(1 for c in name_lower if c in liquids_nasals),
            'vowels': sum(1 for c in name_lower if c in vowels),
            'syllables': max(1, sum(1 for c in name_lower if c in vowels))  # Rough syllable estimate
        }
        
        # Calculate derived metrics
        features['vowel_density'] = features['vowels'] / features['length'] if features['length'] > 0 else 0
        features['harsh_sounds'] = features['plosives'] + features['sibilants']
        features['soft_sounds'] = features['liquids_nasals'] + features['vowels']
        
        # Harshness score (0-100): weighted sum of harsh sounds
        features['harshness'] = min(100, (
            features['plosives'] * 15 +
            features['sibilants'] * 12
        ))
        
        # Melodiousness score (0-100): vowels, liquids, syllable flow
        melodiousness_raw = (
            features['vowels'] * 8 +
            features['liquids_nasals'] * 6 +
            (features['syllables'] * 4 if features['syllables'] <= 4 else 16 - (features['syllables'] - 4) * 2)
        )
        features['melodiousness'] = min(100, melodiousness_raw)
        
        # Composite beauty score: melodiousness minus weighted harshness
        features['beauty_score'] = max(0, features['melodiousness'] - (features['harshness'] * 0.3))
        
        return features

    def analyze_country_phonetics(self):
        """Analyze phonetic properties of all countries and create comparison dataset."""
        print(f"Analyzing phonetic properties of {len(COUNTRIES_FOR_COMPARISON)} countries...")
        
        results = []
        for country in tqdm(COUNTRIES_FOR_COMPARISON):
            features = self.count_phonetic_features(country)
            results.append(features)
        
        df = pd.DataFrame(results)
        
        # Rank by beauty score
        df['beauty_rank'] = df['beauty_score'].rank(ascending=False, method='min').astype(int)
        df['melodiousness_rank'] = df['melodiousness'].rank(ascending=False, method='min').astype(int)
        df['harshness_rank'] = df['harshness'].rank(ascending=True, method='min').astype(int)
        
        # Sort by beauty rank
        df = df.sort_values('beauty_rank')
        
        # Save results
        out_path = self.results_dir / "country_phonetic_comparison.csv"
        df.to_csv(out_path, index=False)
        print(f"✓ Phonetic analysis complete → {out_path}")
        
        # Create visualization
        self.create_phonetic_visualization(df)
        
        return df

    def create_phonetic_visualization(self, df):
        """Create visualization of country name phonetic properties."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Top 20 most beautiful
        top20 = df.head(20)
        axes[0, 0].barh(range(len(top20)), top20['beauty_score'], color='#5eead4')
        axes[0, 0].set_yticks(range(len(top20)))
        axes[0, 0].set_yticklabels(top20['name'])
        axes[0, 0].set_xlabel('Beauty Score')
        axes[0, 0].set_title('Top 20 Most "Beautiful" Country Names (Phonetic Algorithm)')
        axes[0, 0].invert_yaxis()
        
        # Highlight America
        america_idx = top20[top20['name'] == 'America'].index
        if len(america_idx) > 0:
            idx_in_top20 = list(top20.index).index(america_idx[0])
            axes[0, 0].get_children()[idx_in_top20].set_color('#e06060')
        
        # Bottom 20 least beautiful
        bottom20 = df.tail(20).iloc[::-1]
        axes[0, 1].barh(range(len(bottom20)), bottom20['beauty_score'], color='#e06060')
        axes[0, 1].set_yticks(range(len(bottom20)))
        axes[0, 1].set_yticklabels(bottom20['name'])
        axes[0, 1].set_xlabel('Beauty Score')
        axes[0, 1].set_title('Bottom 20 Least "Beautiful" Country Names')
        axes[0, 1].invert_yaxis()
        
        # Scatter: Harshness vs Melodiousness
        axes[1, 0].scatter(df['harshness'], df['melodiousness'], alpha=0.6, s=80)
        
        # Highlight America
        america_row = df[df['name'] == 'America']
        if len(america_row) > 0:
            axes[1, 0].scatter(america_row['harshness'], america_row['melodiousness'], 
                             color='#e06060', s=200, marker='*', edgecolors='black', linewidths=2,
                             label='America', zorder=5)
            axes[1, 0].annotate('America', 
                              (america_row['harshness'].values[0], america_row['melodiousness'].values[0]),
                              xytext=(10, 10), textcoords='offset points', fontsize=10, fontweight='bold')
        
        axes[1, 0].set_xlabel('Harshness Score')
        axes[1, 0].set_ylabel('Melodiousness Score')
        axes[1, 0].set_title('Harshness vs Melodiousness (All Countries)')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)
        
        # Distribution of beauty scores
        axes[1, 1].hist(df['beauty_score'], bins=20, color='#3b82f6', alpha=0.7, edgecolor='black')
        axes[1, 1].set_xlabel('Beauty Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Distribution of Beauty Scores Across All Countries')
        
        # Add vertical line for America
        if len(america_row) > 0:
            axes[1, 1].axvline(america_row['beauty_score'].values[0], color='#e06060', 
                             linestyle='--', linewidth=2, label='America')
            axes[1, 1].legend()
        
        plt.tight_layout()
        out_path = self.results_dir / "country_phonetic_comparison.png"
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Visualization saved → {out_path}")

    # ------------------------------------------------------------------
    # PROCESSING --------------------------------------------------------
    # ------------------------------------------------------------------

    def build_ngram_dataset(self):
        records = []
        for variant in VARIANTS:
            csv_path = self.download_google_ngram(variant)
            df = pd.read_csv(csv_path)
            df["variant"] = variant
            records.append(df)
        full = pd.concat(records, ignore_index=True)
        out = self.results_dir / "ngram_variant_usage.parquet"
        full.to_parquet(out, index=False)
        print(f"✓ Saved Ngram dataset → {out}")
        return full

    # ------------------------------------------------------------------
    def create_summary_figure(self, df):
        sns.set_palette("husl")
        plt.figure(figsize=(14, 8))
        for variant in VARIANTS:
            data = df[df.variant == variant]
            plt.plot(data.year, data.frequency, label=variant)
        plt.title("Google Books Ngram Frequency of America Variants (1900-2019)")
        plt.xlabel("Year")
        plt.ylabel("Relative Frequency")
        plt.legend(ncol=2)
        path = self.results_dir / "ngram_variant_usage.png"
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        print(f"✓ Saved figure → {path}")

    # ------------------------------------------------------------------
    def run_pipeline(self, include_phonetics=True):
        """Run complete analysis pipeline."""
        print("\n" + "="*70)
        print("AMERICA VARIANT ANALYSIS PIPELINE")
        print("="*70 + "\n")
        
        # Step 1: N-gram analysis
        print("Step 1: Building N-gram dataset...")
        df = self.build_ngram_dataset()
        self.create_summary_figure(df)
        
        # Step 2: Sentiment analysis
        print("\nStep 2: Analyzing sentiment...")
        df_group = df.groupby("variant")["frequency"].mean().reset_index()
        sentiment_scores = []
        for v in VARIANTS:
            sentiment_scores.append({"variant": v, "avg_sentiment": self.analyze_sentiment([v])})
        sentiment_df = pd.DataFrame(sentiment_scores)
        summary = df_group.merge(sentiment_df, on="variant")
        summary_path = self.results_dir / "variant_summary.csv"
        summary.to_csv(summary_path, index=False)
        print(f"✓ Summary saved → {summary_path}")
        
        # Step 3: Phonetic comparison analysis
        if include_phonetics:
            print(f"\nStep 3: Analyzing phonetic properties of {len(COUNTRIES_FOR_COMPARISON)} countries...")
            phonetic_df = self.analyze_country_phonetics()
            
            # Print America's ranking
            america_row = phonetic_df[phonetic_df['name'] == 'America']
            if len(america_row) > 0:
                rank = america_row['beauty_rank'].values[0]
                score = america_row['beauty_score'].values[0]
                melodiousness = america_row['melodiousness'].values[0]
                harshness = america_row['harshness'].values[0]
                print(f"\n{'='*70}")
                print(f"AMERICA PHONETIC ANALYSIS RESULTS:")
                print(f"{'='*70}")
                print(f"Beauty Rank: {rank} out of {len(COUNTRIES_FOR_COMPARISON)} countries")
                print(f"Beauty Score: {score:.1f}/100")
                print(f"Melodiousness: {melodiousness:.1f}/100")
                print(f"Harshness: {harshness:.1f}/100")
                print(f"{'='*70}\n")
        
        print("✓ Pipeline complete!\n")


if __name__ == "__main__":
    analyzer = AmericaVariantAnalyzer()
    analyzer.run_pipeline()
