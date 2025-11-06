"""
GDELT News Corpus Sentiment Analysis
Tracks "America" vs "United States" variant usage and tone in global news 2015-2024.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
from datetime import datetime, timedelta
import time
import json


class GDELTVariantAnalyzer:
    """Pull GDELT mentions of America variants and extract sentiment/tone."""
    
    def __init__(self, cache_dir="data/raw/gdelt_variants", processed_dir="data/processed/america_variants"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        self.variants = [
            "America",
            "United States",
            "USA",
            "US",
            "the States"
        ]
    
    def query_gdelt_doc_api(self, variant: str, start_date: str, end_date: str):
        """
        Query GDELT 2.0 DOC API for article counts and tone.
        Free tier: 250 queries/day
        """
        base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        
        params = {
            'query': f'"{variant}"',
            'mode': 'timelinevol',
            'format': 'json',
            'startdatetime': start_date,
            'enddatetime': end_date
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"  ⚠️ GDELT query failed for {variant}: {e}")
            return None
    
    def create_simulated_sentiment_data(self):
        """
        Create simulated news sentiment data based on known patterns.
        Real GDELT requires API limits management; this provides proof-of-concept.
        """
        print("Creating simulated news sentiment data...")
        
        records = []
        
        # Simulate 2015-2024 yearly data
        for year in range(2015, 2025):
            # America: peaks in patriotic contexts, negative in critical coverage
            # United States: more formal/neutral
            # USA/US: abbreviated, neutral-positive
            
            for variant in self.variants:
                # Base frequency (relative)
                if variant == "United States":
                    base_freq = 100.0
                    base_sentiment = 0.05  # Neutral
                elif variant == "America":
                    base_freq = 75.0
                    # More polarized: positive in patriotic contexts, negative in critical
                    base_sentiment = 0.15 if year < 2020 else -0.05
                elif variant == "USA":
                    base_freq = 120.0
                    base_sentiment = 0.10
                elif variant == "US":
                    base_freq = 200.0  # Most common abbreviation
                    base_sentiment = 0.08
                elif variant == "the States":
                    base_freq = 15.0  # Colloquial, less formal
                    base_sentiment = 0.12
                
                # Add noise
                freq = base_freq * np.random.uniform(0.9, 1.1)
                sentiment = base_sentiment + np.random.normal(0, 0.05)
                
                records.append({
                    'year': year,
                    'variant': variant,
                    'article_count_estimate': int(freq * 10000),  # Scale to realistic counts
                    'avg_tone': np.clip(sentiment, -1, 1),
                    'source': 'simulated_news_corpus',
                    'note': 'Simulated based on observed patterns; replace with real GDELT'
                })
        
        df = pd.DataFrame(records)
        output_path = self.processed_dir / "news_variant_sentiment.parquet"
        df.to_parquet(output_path, index=False)
        
        print(f"  ✓ Simulated news sentiment → {output_path}")
        return df
    
    def create_opinion_correlation_stub(self):
        """
        Create structure for linking variant usage to public opinion.
        ANES/GSS/Pew micro-data requires manual download.
        """
        print("Creating opinion correlation structure...")
        
        # Simulated correlation pattern
        opinion_data = []
        
        for year in range(2000, 2025, 4):  # Election years
            # Hypothesis: "America" usage correlates with patriotism/conservatism
            # "United States" correlates with formality/liberal usage
            
            opinion_data.append({
                'year': year,
                'variant_preference': 'America',
                'avg_patriotism_scale': np.random.uniform(7.2, 8.5),  # 0-10 scale
                'conservative_pct': np.random.uniform(55, 68),
                'liberal_pct': np.random.uniform(32, 45),
                'data_source': 'simulated_anes_pattern'
            })
            
            opinion_data.append({
                'year': year,
                'variant_preference': 'United States',
                'avg_patriotism_scale': np.random.uniform(6.5, 7.8),
                'conservative_pct': np.random.uniform(42, 52),
                'liberal_pct': np.random.uniform(48, 58),
                'data_source': 'simulated_anes_pattern'
            })
        
        df = pd.DataFrame(opinion_data)
        output_path = self.processed_dir / "opinion_variant_correlation.parquet"
        df.to_parquet(output_path, index=False)
        
        print(f"  ✓ Opinion correlation structure → {output_path}")
        print(f"     Note: Replace with real ANES/GSS micro-data for publication")
        return df
    
    def run_pipeline(self):
        """Execute full GDELT + opinion pipeline."""
        print("\n" + "="*60)
        print("AMERICA VARIANT SENTIMENT ANALYSIS")
        print("="*60 + "\n")
        
        results = {}
        
        # News sentiment (simulated for now)
        results['news'] = self.create_simulated_sentiment_data()
        
        # Opinion correlation (structure)
        results['opinion'] = self.create_opinion_correlation_stub()
        
        print("\n" + "="*60)
        print("SENTIMENT ANALYSIS COMPLETE")
        print("="*60)
        print("\nOutputs:")
        print(f"  - {self.processed_dir / 'news_variant_sentiment.parquet'}")
        print(f"  - {self.processed_dir / 'opinion_variant_correlation.parquet'}")
        print("\nNext: Load into DuckDB `variants_sentiment` table")
        
        return results


if __name__ == "__main__":
    analyzer = GDELTVariantAnalyzer()
    analyzer.run_pipeline()

