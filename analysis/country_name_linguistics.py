"""
Country Name Linguistics Module
Analyzes exonyms, endonyms, phonetic properties, and subjective beauty of country names.
Tests hypothesis: Does the beauty/harshness of a country's name affect its perception?
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import re


class CountryNameLinguistics:
    """Analyzes phonetic and aesthetic properties of country names."""
    
    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.results_dir = self.processed_dir / "country_linguistics"
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def count_plosives(self, text: str) -> int:
        """Count plosive consonants (p, t, k, b, d, g) - harsh sounds."""
        if pd.isna(text):
            return 0
        text = text.lower()
        plosives = re.findall(r'[ptkbdg]', text)
        return len(plosives)
    
    def count_sibilants(self, text: str) -> int:
        """Count sibilant sounds (s, z, sh, zh, ch) - hissing sounds."""
        if pd.isna(text):
            return 0
        text = text.lower()
        # Count s, z, x
        sibilants = re.findall(r'[szx]', text)
        # Check for 'ch', 'sh'
        sibilants += re.findall(r'ch|sh', text)
        return len(sibilants)
    
    def count_liquids_nasals(self, text: str) -> int:
        """Count liquid/nasal consonants (l, r, m, n) - soft, flowing sounds."""
        if pd.isna(text):
            return 0
        text = text.lower()
        liquids = re.findall(r'[lrmn]', text)
        return len(liquids)
    
    def count_open_vowels(self, text: str) -> int:
        """Count open vowels (a, e, i, o, u, y) - melodious sounds."""
        if pd.isna(text):
            return 0
        text = text.lower()
        vowels = re.findall(r'[aeiouy]', text)
        return len(vowels)
    
    def estimate_syllables(self, text: str) -> int:
        """Estimate syllable count."""
        if pd.isna(text):
            return 0
        text = text.lower()
        vowel_groups = re.findall(r'[aeiouy]+', text)
        count = len(vowel_groups)
        # Adjust for silent e
        if text.endswith('e') and count > 1:
            count -= 1
        return max(1, count)
    
    def phonetic_harshness_score(self, text: str) -> float:
        """
        Calculate phonetic harshness score (0-100).
        Higher = harsher, more aggressive sound.
        Based on plosives, sibilants vs. vowels, liquids.
        """
        if pd.isna(text) or text == '':
            return 0.0
        
        plosives = self.count_plosives(text)
        sibilants = self.count_sibilants(text)
        liquids = self.count_liquids_nasals(text)
        vowels = self.count_open_vowels(text)
        length = len(text)
        
        if length == 0:
            return 0.0
        
        # Harsh sounds
        harsh_score = (plosives * 15 + sibilants * 10) / length * 100
        
        # Soft sounds (reduce harshness)
        soft_score = (liquids * 8 + vowels * 5) / length * 100
        
        # Net harshness
        harshness = max(0, min(100, harsh_score - (soft_score * 0.5)))
        
        return harshness
    
    def melodiousness_score(self, text: str) -> float:
        """
        Calculate melodiousness (0-100).
        Higher = more melodious, pleasant sounding.
        Based on vowels, liquids, syllable flow.
        """
        if pd.isna(text) or text == '':
            return 0.0
        
        vowels = self.count_open_vowels(text)
        liquids = self.count_liquids_nasals(text)
        syllables = self.estimate_syllables(text)
        length = len(text)
        
        if length == 0:
            return 0.0
        
        # Vowel richness
        vowel_density = (vowels / length) * 100
        
        # Liquid/nasal flow
        liquid_density = (liquids / length) * 100
        
        # Syllable smoothness (3-4 syllables often most melodious)
        syllable_score = 100 - abs(syllables - 3.5) * 10
        syllable_score = max(0, min(100, syllable_score))
        
        melodiousness = (vowel_density * 0.4 + liquid_density * 0.3 + syllable_score * 0.3)
        
        return min(100, melodiousness)
    
    def analyze_country_names(self) -> pd.DataFrame:
        """
        Analyze phonetic properties of country names.
        Load base data and compute all linguistic features.
        """
        print("Analyzing country name phonetics...")
        
        # Load base country names
        country_file = self.raw_dir / "country_names" / "country_names_core.csv"
        if not country_file.exists():
            print("  ✗ Country names data not found")
            return None
        
        df = pd.read_csv(country_file)
        
        # Analyze each name variant
        name_columns = ['endonym', 'common_english', 'abbreviation_english', 'spanish_name']
        
        for col in name_columns:
            if col in df.columns:
                df[f'{col}_plosives'] = df[col].apply(self.count_plosives)
                df[f'{col}_sibilants'] = df[col].apply(self.count_sibilants)
                df[f'{col}_liquids'] = df[col].apply(self.count_liquids_nasals)
                df[f'{col}_vowels'] = df[col].apply(self.count_open_vowels)
                df[f'{col}_syllables'] = df[col].apply(self.estimate_syllables)
                df[f'{col}_harshness'] = df[col].apply(self.phonetic_harshness_score)
                df[f'{col}_melodiousness'] = df[col].apply(self.melodiousness_score)
        
        # Focus on main analysis: English common name
        df['length'] = df['common_english'].str.len()
        
        # Beauty ranking (user hypothesis: America is most beautiful)
        # Create comparative beauty score
        df['phonetic_beauty_score'] = df['common_english_melodiousness'] - (df['common_english_harshness'] * 0.3)
        
        output_path = self.results_dir / "country_names_phonetic_analysis.parquet"
        df.to_parquet(output_path, index=False)
        
        # Also CSV for easy inspection
        df.to_csv(output_path.with_suffix('.csv'), index=False)
        
        print(f"  ✓ Analyzed {len(df)} country names → {output_path}")
        return df
    
    def analyze_america_hypothesis(self) -> pd.DataFrame:
        """
        Deep dive: Is "America" subjectively the most beautiful country name?
        Compare to alternatives and analyze what makes it appealing.
        """
        print("Testing 'America beauty' hypothesis...")
        
        # Load phonetic analysis
        analysis_file = self.results_dir / "country_names_phonetic_analysis.parquet"
        if analysis_file.exists():
            df = pd.read_parquet(analysis_file)
        else:
            df = self.analyze_country_names()
        
        # Extract America's metrics
        america_row = df[df['country_code'] == 'USA'].iloc[0] if len(df[df['country_code'] == 'USA']) > 0 else None
        
        if america_row is None:
            print("  ✗ America data not found")
            return None
        
        # Detailed breakdown of "America"
        america_analysis = {
            'name': 'America',
            'syllables': self.estimate_syllables('America'),
            'vowels': self.count_open_vowels('America'),
            'plosives': self.count_plosives('America'),
            'sibilants': self.count_sibilants('America'),
            'liquids_nasals': self.count_liquids_nasals('America'),
            'harshness_score': self.phonetic_harshness_score('America'),
            'melodiousness_score': self.melodiousness_score('America'),
            'vowel_density_pct': (self.count_open_vowels('America') / len('America')) * 100,
            'liquid_density_pct': (self.count_liquids_nasals('America') / len('America')) * 100,
            'beauty_interpretation': 'High vowel density (4/7), soft liquids (m, r), melodious 4 syllables',
            'user_subjective_rating': 95,  # User's stated rating
            'phonetic_beauty_score': america_row['phonetic_beauty_score']
        }
        
        # Compare to other names
        comparison_names = [
            'China', 'Germany', 'Brazil', 'India', 'France', 'Japan',
            'Canada', 'Mexico', 'Spain', 'Egypt', 'Nigeria'
        ]
        
        comparisons = []
        for name in comparison_names:
            comparisons.append({
                'name': name,
                'harshness': self.phonetic_harshness_score(name),
                'melodiousness': self.melodiousness_score(name),
                'beauty_score': self.melodiousness_score(name) - (self.phonetic_harshness_score(name) * 0.3)
            })
        
        # Add America
        comparisons.append({
            'name': 'America',
            'harshness': america_analysis['harshness_score'],
            'melodiousness': america_analysis['melodiousness_score'],
            'beauty_score': america_analysis['phonetic_beauty_score']
        })
        
        comparison_df = pd.DataFrame(comparisons)
        comparison_df = comparison_df.sort_values('beauty_score', ascending=False)
        comparison_df['beauty_rank'] = range(1, len(comparison_df) + 1)
        
        # Analysis summary
        america_rank = comparison_df[comparison_df['name'] == 'America']['beauty_rank'].iloc[0]
        
        summary = pd.DataFrame([{
            'hypothesis': 'America is subjectively the most beautiful country name',
            'phonetic_beauty_rank': int(america_rank),
            'total_compared': len(comparison_df),
            'user_subjective_rating': 95,
            'calculated_beauty_score': america_analysis['phonetic_beauty_score'],
            'key_features': 'High vowel density, soft consonants (m, r), 4 melodious syllables',
            'comparison_notes': 'Ranks highly but phonetic analysis alone may not capture full subjective appeal',
            'alternative_hypothesis': 'Subjective beauty influenced by: familiarity, national identity, cultural associations beyond pure phonetics'
        }])
        
        # Save outputs
        output_path = self.results_dir / "america_beauty_hypothesis.csv"
        summary.to_csv(output_path, index=False)
        
        comparison_path = self.results_dir / "country_name_beauty_rankings.csv"
        comparison_df.to_csv(comparison_path, index=False)
        
        print(f"  ✓ America ranks #{america_rank} of {len(comparison_df)} in phonetic beauty")
        print(f"  ✓ Analysis saved → {output_path}")
        
        return summary
    
    def analyze_exonym_endonym_differences(self) -> pd.DataFrame:
        """
        Analyze differences between how countries call themselves vs. how others call them.
        Example: China (English) vs. Zhōngguó (endonym)
        """
        print("Analyzing exonym vs. endonym differences...")
        
        # Load analysis
        analysis_file = self.results_dir / "country_names_phonetic_analysis.parquet"
        if analysis_file.exists():
            df = pd.read_parquet(analysis_file)
        else:
            df = self.analyze_country_names()
        
        # Compare endonym vs. English name
        comparisons = []
        
        for idx, row in df.iterrows():
            if pd.notna(row['endonym']) and pd.notna(row['common_english']):
                # Skip if they're the same
                if row['endonym'].split(' (')[0].lower() != row['common_english'].split('/')[0].strip().lower():
                    comparisons.append({
                        'country_code': row['country_code'],
                        'endonym': row['endonym'].split(' (')[0],  # Remove script notation
                        'english_name': row['common_english'].split('/')[0].strip(),
                        'endonym_harshness': row.get('endonym_harshness', 0),
                        'english_harshness': row.get('common_english_harshness', 0),
                        'endonym_melodiousness': row.get('endonym_melodiousness', 0),
                        'english_melodiousness': row.get('common_english_melodiousness', 0),
                        'harshness_difference': row.get('common_english_harshness', 0) - row.get('endonym_harshness', 0),
                        'melodiousness_difference': row.get('common_english_melodiousness', 0) - row.get('endonym_melodiousness', 0),
                        'syllable_difference': row.get('common_english_syllables', 0) - row.get('endonym_syllables', 0)
                    })
        
        comparison_df = pd.DataFrame(comparisons)
        
        if len(comparison_df) > 0:
            # Interpretation
            comparison_df['english_more_melodious'] = comparison_df['melodiousness_difference'] > 5
            comparison_df['endonym_more_melodious'] = comparison_df['melodiousness_difference'] < -5
            
            output_path = self.results_dir / "exonym_endonym_comparison.csv"
            comparison_df.to_csv(output_path, index=False)
            
            print(f"  ✓ Analyzed {len(comparison_df)} exonym/endonym pairs → {output_path}")
        else:
            print("  ⚠ No significant exonym/endonym differences found")
            comparison_df = pd.DataFrame()
        
        return comparison_df
    
    def analyze_trump_china_pronunciation(self) -> pd.DataFrame:
        """
        Special analysis: Trump's pronunciation of "China" emphasizes the harsh 'Ch' plosive.
        Compare standard vs. emphasized pronunciation effects.
        """
        print("Analyzing 'China' pronunciation variants...")
        
        # Standard pronunciation: "CHY-nuh" 
        # Trump emphasis: "CHY-NAH" with hard terminal
        
        variants = [
            {
                'variant': 'Standard English (CHY-nuh)',
                'transcription': 'China',
                'plosives': self.count_plosives('China'),
                'sibilants': self.count_sibilants('China'),
                'harshness': self.phonetic_harshness_score('China'),
                'emphasis': 'soft terminal',
                'perceived_tone': 'neutral'
            },
            {
                'variant': 'Trump emphasis (CHY-NAH)',
                'transcription': 'CHINA',  # Caps to represent emphasis
                'plosives': self.count_plosives('CHINA') + 1,  # +1 for emphasized terminal
                'sibilants': self.count_sibilants('CHINA'),
                'harshness': self.phonetic_harshness_score('CHINA') * 1.3,  # Emphasis multiplier
                'emphasis': 'hard terminal, stressed initial plosive',
                'perceived_tone': 'aggressive/assertive'
            },
            {
                'variant': 'Mandarin (Zhōngguó)',
                'transcription': 'Zhongguo',
                'plosives': self.count_plosives('Zhongguo'),
                'sibilants': self.count_sibilants('Zhongguo'),
                'harshness': self.phonetic_harshness_score('Zhongguo'),
                'emphasis': 'nasal quality',
                'perceived_tone': 'neutral/cultural'
            }
        ]
        
        df = pd.DataFrame(variants)
        
        # Analysis summary
        df['harshness_vs_standard'] = df['harshness'] - df.iloc[0]['harshness']
        
        output_path = self.results_dir / "china_pronunciation_analysis.csv"
        df.to_csv(output_path, index=False)
        
        print(f"  ✓ China pronunciation analysis → {output_path}")
        print(f"     Standard harshness: {df.iloc[0]['harshness']:.1f}")
        print(f"     Trump emphasis harshness: {df.iloc[1]['harshness']:.1f} (+{df.iloc[1]['harshness_vs_standard']:.1f})")
        
        return df
    
    def run_full_analysis(self):
        """Execute complete country name linguistics pipeline."""
        print("\n" + "="*60)
        print("COUNTRY NAME LINGUISTICS ANALYSIS")
        print("="*60 + "\n")
        
        results = {}
        
        # Core phonetic analysis
        results['phonetics'] = self.analyze_country_names()
        
        # America beauty hypothesis
        results['america'] = self.analyze_america_hypothesis()
        
        # Exonym vs endonym
        results['exonyms'] = self.analyze_exonym_endonym_differences()
        
        # China pronunciation
        results['china'] = self.analyze_trump_china_pronunciation()
        
        print("\n" + "="*60)
        print("LINGUISTICS ANALYSIS COMPLETE")
        print("="*60)
        print(f"✓ Results saved to {self.results_dir}")
        print("\nKey findings:")
        print("  - Country name phonetic properties quantified")
        print("  - America beauty hypothesis tested")
        print("  - Exonym/endonym differences analyzed")
        print("  - China pronunciation variants compared")
        
        return results


if __name__ == "__main__":
    analyzer = CountryNameLinguistics()
    analyzer.run_full_analysis()

