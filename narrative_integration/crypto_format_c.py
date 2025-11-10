"""
Cryptocurrency Data Transformation to Format C (Mixed Domain Data)

Transforms raw cryptocurrency dataset into Narrative Optimization Framework Format C.

Format C Structure:
- texts: Rich narrative descriptions
- features: Numerical feature matrix
- metadata: Per-sample metadata
- labels: Classification/regression targets

Author: Narrative Integration System
Date: November 2025
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CryptoFormatCTransformer:
    """Transform crypto data to Format C for narrative optimization framework."""
    
    def __init__(self, data_path: str):
        """
        Initialize transformer.
        
        Args:
            data_path: Path to crypto_with_competitive_context.json
        """
        self.data_path = Path(data_path)
        self.raw_data = None
        self.format_c_data = None
        
        # Technical morphemes for crypto domain
        self.tech_morphemes = [
            'bit', 'byte', 'crypto', 'coin', 'chain', 'block', 
            'digi', 'cyber', 'token', 'swap', 'finance', 'safe',
            'moon', 'rocket', 'doge', 'shib', 'inu'
        ]
        
    def load_data(self) -> None:
        """Load raw crypto data from JSON."""
        logger.info(f"Loading crypto data from {self.data_path}")
        with open(self.data_path, 'r') as f:
            self.raw_data = json.load(f)
        logger.info(f"Loaded {len(self.raw_data)} cryptocurrency records")
    
    def _detect_technical_morphemes(self, name: str) -> List[str]:
        """Detect technical morphemes in crypto name."""
        name_lower = name.lower()
        detected = []
        for morpheme in self.tech_morphemes:
            if morpheme in name_lower:
                detected.append(morpheme)
        return detected
    
    def _classify_name_strategy(self, name: str, symbol: str) -> str:
        """
        Classify the naming strategy used.
        
        Returns:
            One of: 'technical', 'playful', 'financial', 'abstract', 'descriptive'
        """
        name_lower = name.lower()
        
        # Technical: contains tech morphemes
        tech_morphemes_found = self._detect_technical_morphemes(name)
        if len(tech_morphemes_found) >= 2:
            return 'technical'
        
        # Playful: meme references, animals, emojis in concept
        playful_markers = ['doge', 'shib', 'inu', 'moon', 'rocket', 'baby', 'elon', 'pepe', 'cat', 'dog']
        if any(marker in name_lower for marker in playful_markers):
            return 'playful'
        
        # Financial: finance, value, money, gold, etc.
        financial_markers = ['finance', 'cash', 'money', 'gold', 'silver', 'value', 'asset', 'capital', 'bank']
        if any(marker in name_lower for marker in financial_markers):
            return 'financial'
        
        # Abstract: made-up words, exotic names
        if len(name) > 8 and not any(marker in name_lower for marker in self.tech_morphemes):
            return 'abstract'
        
        return 'descriptive'
    
    def _generate_narrative_description(self, record: Dict) -> str:
        """
        Generate rich narrative description for a cryptocurrency.
        
        This is the core text that transformers will analyze.
        """
        name = record['name']
        symbol = record['symbol']
        rank = record['rank']
        market_cap = record['market_cap']
        
        # Extract features
        syllables = record.get('syllables', 0)
        harshness = record.get('harshness', 0)
        length = len(name)
        
        # Competitive context
        comp_ctx = record.get('competitive_context', {})
        cohort_size = comp_ctx.get('cohort_size', 0)
        market_saturation = comp_ctx.get('market_saturation', 0.0)
        relative_features = comp_ctx.get('relative_features', {})
        
        # Detect morphemes and strategy
        tech_morphemes = self._detect_technical_morphemes(name)
        naming_strategy = self._classify_name_strategy(name, symbol)
        
        # Build narrative components
        narrative_parts = []
        
        # Opening with name and symbol
        narrative_parts.append(f"{name} ({symbol})")
        
        # Market position narrative
        if rank <= 10:
            position_desc = f"dominant market leader (rank {rank})"
        elif rank <= 50:
            position_desc = f"major cryptocurrency (rank {rank})"
        elif rank <= 200:
            position_desc = f"established mid-tier project (rank {rank})"
        elif rank <= 1000:
            position_desc = f"smaller cryptocurrency project (rank {rank})"
        else:
            position_desc = f"emerging or niche cryptocurrency (rank {rank})"
        narrative_parts.append(position_desc)
        
        # Naming strategy
        strategy_descriptions = {
            'technical': 'employs technical terminology signaling blockchain sophistication',
            'playful': 'uses playful memetic language appealing to community engagement',
            'financial': 'adopts traditional financial terminology suggesting stability',
            'abstract': 'presents unique abstract branding for distinctiveness',
            'descriptive': 'uses straightforward descriptive naming'
        }
        narrative_parts.append(strategy_descriptions[naming_strategy])
        
        # Technical morphemes
        if tech_morphemes:
            morpheme_str = ', '.join(f"'{m}'" for m in tech_morphemes)
            narrative_parts.append(f"incorporates technical morphemes: {morpheme_str}")
        
        # Phonetic characteristics
        phonetic_parts = []
        if syllables == 1:
            phonetic_parts.append("monosyllabic")
        elif syllables == 2:
            phonetic_parts.append("disyllabic")
        elif syllables >= 4:
            phonetic_parts.append("polysyllabic")
        
        if harshness > 2:
            phonetic_parts.append("harsh phonetic profile")
        elif harshness > 0:
            phonetic_parts.append("moderate phonetic harshness")
        else:
            phonetic_parts.append("soft phonetic profile")
        
        if length <= 4:
            phonetic_parts.append("short name length")
        elif length >= 10:
            phonetic_parts.append("long name length")
        
        if phonetic_parts:
            narrative_parts.append(f"Features {', '.join(phonetic_parts)}")
        
        # Competitive context
        if market_saturation > 0.7:
            narrative_parts.append(f"operates in highly saturated market (saturation: {market_saturation:.2f})")
        elif market_saturation > 0.4:
            narrative_parts.append(f"operates in moderately competitive market (saturation: {market_saturation:.2f})")
        else:
            narrative_parts.append(f"operates in less saturated market niche (saturation: {market_saturation:.2f})")
        
        # Relative positioning
        rel_syllables = relative_features.get('relative_syllables', 0)
        if rel_syllables < -0.5:
            narrative_parts.append("shorter name than typical in cohort")
        elif rel_syllables > 0.5:
            narrative_parts.append("longer name than typical in cohort")
        
        # Market cap context
        if market_cap > 1e11:  # > 100B
            narrative_parts.append(f"commands massive market capitalization (${market_cap/1e9:.1f}B)")
        elif market_cap > 1e10:  # > 10B
            narrative_parts.append(f"maintains substantial market capitalization (${market_cap/1e9:.1f}B)")
        elif market_cap > 1e9:  # > 1B
            narrative_parts.append(f"holds significant market capitalization (${market_cap/1e9:.2f}B)")
        elif market_cap > 1e8:  # > 100M
            narrative_parts.append(f"represents moderate market capitalization (${market_cap/1e6:.0f}M)")
        else:
            narrative_parts.append(f"maintains smaller market presence (${market_cap/1e6:.1f}M)")
        
        # Ecosystem role
        if rank <= 20:
            narrative_parts.append("Plays foundational role in cryptocurrency ecosystem")
        elif naming_strategy == 'playful':
            narrative_parts.append("Appeals to retail and community-driven investment")
        elif naming_strategy == 'technical':
            narrative_parts.append("Targets technically sophisticated crypto-native audience")
        
        # Combine all parts
        narrative = ". ".join(narrative_parts) + "."
        
        return narrative
    
    def _extract_features(self, record: Dict) -> np.ndarray:
        """
        Extract numerical feature vector.
        
        Features:
        - Phonetic: harshness, syllables, length, vowel_ratio
        - Competitive: relative_harshness, relative_syllables, relative_length
        - Market: market_saturation, cohort_size_normalized
        - Derived: tech_morpheme_count, naming_strategy_encoded
        """
        name = record['name']
        
        # Base phonetic features
        harshness = record.get('harshness', 0)
        syllables = record.get('syllables', 0)
        length = len(name)
        memorability = record.get('memorability', 0)
        
        # Calculate vowel ratio
        vowels = 'aeiouy'
        vowel_count = sum(1 for c in name.lower() if c in vowels)
        vowel_ratio = vowel_count / len(name) if len(name) > 0 else 0
        
        # Competitive context features
        comp_ctx = record.get('competitive_context', {})
        relative_features = comp_ctx.get('relative_features', {})
        
        relative_harshness = relative_features.get('relative_harshness', 0)
        relative_syllables = relative_features.get('relative_syllables', 0)
        relative_length = relative_features.get('relative_length', 0)
        relative_memorability = relative_features.get('relative_memorability', 0)
        
        zscore_harshness = relative_features.get('zscore_harshness', 0)
        zscore_syllables = relative_features.get('zscore_syllables', 0)
        zscore_length = relative_features.get('zscore_length', 0)
        zscore_memorability = relative_features.get('zscore_memorability', 0)
        
        # Market context
        market_saturation = comp_ctx.get('market_saturation', 0)
        cohort_size = comp_ctx.get('cohort_size', 0)
        cohort_size_normalized = cohort_size / 10000.0  # Normalize
        
        # Derived features
        tech_morphemes = self._detect_technical_morphemes(name)
        tech_morpheme_count = len(tech_morphemes)
        
        # Naming strategy (one-hot encoded)
        strategy = self._classify_name_strategy(name, record['symbol'])
        strategy_encoding = {
            'technical': [1, 0, 0, 0, 0],
            'playful': [0, 1, 0, 0, 0],
            'financial': [0, 0, 1, 0, 0],
            'abstract': [0, 0, 0, 1, 0],
            'descriptive': [0, 0, 0, 0, 1]
        }
        strategy_features = strategy_encoding.get(strategy, [0, 0, 0, 0, 0])
        
        # Rank features (log scale)
        rank = record.get('rank', 5000)
        log_rank = np.log10(rank + 1)
        
        # Combine all features
        feature_vector = [
            # Phonetic (7)
            harshness,
            syllables,
            length,
            memorability,
            vowel_ratio,
            1 if syllables == 1 else 0,  # is_monosyllabic
            1 if length <= 4 else 0,  # is_short
            
            # Competitive relative (8)
            relative_harshness,
            relative_syllables,
            relative_length,
            relative_memorability,
            zscore_harshness,
            zscore_syllables,
            zscore_length,
            zscore_memorability,
            
            # Market context (3)
            market_saturation,
            cohort_size_normalized,
            log_rank,
            
            # Derived (6 = 1 + 5)
            tech_morpheme_count,
            *strategy_features
        ]
        
        return np.array(feature_vector, dtype=np.float32)
    
    def _create_metadata(self, record: Dict) -> Dict:
        """Create metadata dictionary for a record."""
        return {
            'coin_id': record['id'],
            'name': record['name'],
            'symbol': record['symbol'],
            'rank': record['rank'],
            'market_cap': record['market_cap'],
            'created_date': record.get('created_date'),
            'cohort_key': record.get('competitive_context', {}).get('cohort_key'),
            'cohort_size': record.get('competitive_context', {}).get('cohort_size'),
            'cohort_mean_outcome': record.get('competitive_context', {}).get('cohort_stats', {}).get('mean_outcome'),
            'cohort_std_outcome': record.get('competitive_context', {}).get('cohort_stats', {}).get('std_outcome')
        }
    
    def _create_labels(self, record: Dict, market_cap_threshold: float) -> Tuple[int, float]:
        """
        Create classification and regression labels.
        
        Args:
            record: Crypto record
            market_cap_threshold: Threshold for binary classification (top 25% percentile)
        
        Returns:
            Tuple of (binary_label, log_market_cap)
        """
        market_cap = record['market_cap']
        
        # Binary: 1 if above threshold (top 25%), else 0
        binary_label = 1 if market_cap >= market_cap_threshold else 0
        
        # Regression: log market cap (for better distribution)
        log_market_cap = np.log10(market_cap + 1)
        
        return binary_label, log_market_cap
    
    def transform(self) -> Dict[str, Any]:
        """
        Transform raw data to Format C.
        
        Returns:
            Format C data structure
        """
        if self.raw_data is None:
            raise ValueError("Must call load_data() first")
        
        logger.info("Transforming data to Format C...")
        
        # Calculate market cap threshold (75th percentile)
        market_caps = [r['market_cap'] for r in self.raw_data]
        market_cap_threshold = np.percentile(market_caps, 75)
        logger.info(f"Market cap threshold (75th percentile): ${market_cap_threshold/1e6:.2f}M")
        
        # Transform each record
        texts = []
        features = []
        metadata = []
        labels_binary = []
        labels_regression = []
        
        for i, record in enumerate(self.raw_data):
            if i % 500 == 0:
                logger.info(f"Processed {i}/{len(self.raw_data)} records")
            
            # Generate narrative description
            text = self._generate_narrative_description(record)
            texts.append(text)
            
            # Extract features
            feature_vec = self._extract_features(record)
            features.append(feature_vec)
            
            # Create metadata
            meta = self._create_metadata(record)
            metadata.append(meta)
            
            # Create labels
            binary_label, log_market_cap = self._create_labels(record, market_cap_threshold)
            labels_binary.append(binary_label)
            labels_regression.append(log_market_cap)
        
        # Convert to numpy arrays
        features_array = np.array(features, dtype=np.float32)
        labels_binary_array = np.array(labels_binary, dtype=np.int32)
        labels_regression_array = np.array(labels_regression, dtype=np.float32)
        
        # Create Format C structure
        self.format_c_data = {
            'data': {
                'texts': texts,
                'features': features_array,
                'metadata': metadata,
                'labels_binary': labels_binary_array,
                'labels_regression': labels_regression_array
            },
            'schema': {
                'text_field': 'narrative_description',
                'feature_fields': [
                    # Phonetic (7)
                    'harshness', 'syllables', 'length', 'memorability', 'vowel_ratio',
                    'is_monosyllabic', 'is_short',
                    # Competitive relative (8)
                    'relative_harshness', 'relative_syllables', 'relative_length', 'relative_memorability',
                    'zscore_harshness', 'zscore_syllables', 'zscore_length', 'zscore_memorability',
                    # Market context (3)
                    'market_saturation', 'cohort_size_normalized', 'log_rank',
                    # Derived (6)
                    'tech_morpheme_count',
                    'strategy_technical', 'strategy_playful', 'strategy_financial', 
                    'strategy_abstract', 'strategy_descriptive'
                ],
                'metadata_fields': [
                    'coin_id', 'name', 'symbol', 'rank', 'market_cap', 'created_date',
                    'cohort_key', 'cohort_size', 'cohort_mean_outcome', 'cohort_std_outcome'
                ],
                'label_field_binary': 'top_25_percent',
                'label_field_regression': 'log_market_cap'
            },
            'metadata': {
                'domain': 'cryptocurrency_market_performance',
                'n_samples': len(texts),
                'n_features': features_array.shape[1],
                'n_classes_binary': 2,
                'task_binary': 'binary_classification',
                'task_regression': 'regression',
                'description': 'Cryptocurrency naming and market performance prediction',
                'source': 'crypto_with_competitive_context.json',
                'transformation_date': '2025-11-10',
                'class_distribution': {
                    'class_0': int(np.sum(labels_binary_array == 0)),
                    'class_1': int(np.sum(labels_binary_array == 1))
                },
                'market_cap_stats': {
                    'min': float(np.min(market_caps)),
                    'max': float(np.max(market_caps)),
                    'mean': float(np.mean(market_caps)),
                    'median': float(np.median(market_caps)),
                    'std': float(np.std(market_caps)),
                    'threshold_75th': float(market_cap_threshold)
                }
            }
        }
        
        logger.info(f"✅ Format C transformation complete!")
        logger.info(f"   - Samples: {len(texts)}")
        logger.info(f"   - Features: {features_array.shape[1]}")
        logger.info(f"   - Class 0: {np.sum(labels_binary_array == 0)}")
        logger.info(f"   - Class 1: {np.sum(labels_binary_array == 1)}")
        logger.info(f"   - Market cap range: ${np.min(market_caps)/1e6:.2f}M - ${np.max(market_caps)/1e9:.2f}B")
        
        return self.format_c_data
    
    def save(self, output_path: str) -> None:
        """
        Save Format C data to file.
        
        Args:
            output_path: Path to save pickle file
        """
        if self.format_c_data is None:
            raise ValueError("Must call transform() first")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        import pickle
        with open(output_path, 'wb') as f:
            pickle.dump(self.format_c_data, f)
        
        logger.info(f"✅ Saved Format C data to {output_path}")
        
        # Also save summary as JSON (without numpy arrays)
        summary = {
            'schema': self.format_c_data['schema'],
            'metadata': self.format_c_data['metadata'],
            'sample_texts': self.format_c_data['data']['texts'][:5],
            'sample_metadata': self.format_c_data['data']['metadata'][:5]
        }
        
        summary_path = output_path.parent / f"{output_path.stem}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✅ Saved summary to {summary_path}")
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names."""
        if self.format_c_data is None:
            raise ValueError("Must call transform() first")
        return self.format_c_data['schema']['feature_fields']
    
    def get_train_test_split(self, test_size: float = 0.2, random_state: int = 42):
        """
        Create train/test split with stratification.
        
        Args:
            test_size: Proportion for test set
            random_state: Random seed
        
        Returns:
            Dictionary with train/test splits
        """
        from sklearn.model_selection import train_test_split
        
        if self.format_c_data is None:
            raise ValueError("Must call transform() first")
        
        data = self.format_c_data['data']
        
        # Stratified split on binary labels
        indices = np.arange(len(data['texts']))
        train_idx, test_idx = train_test_split(
            indices,
            test_size=test_size,
            random_state=random_state,
            stratify=data['labels_binary']
        )
        
        split_data = {
            'X_train_text': [data['texts'][i] for i in train_idx],
            'X_train_features': data['features'][train_idx],
            'X_train_metadata': [data['metadata'][i] for i in train_idx],
            'y_train_binary': data['labels_binary'][train_idx],
            'y_train_regression': data['labels_regression'][train_idx],
            
            'X_test_text': [data['texts'][i] for i in test_idx],
            'X_test_features': data['features'][test_idx],
            'X_test_metadata': [data['metadata'][i] for i in test_idx],
            'y_test_binary': data['labels_binary'][test_idx],
            'y_test_regression': data['labels_regression'][test_idx]
        }
        
        logger.info(f"✅ Created train/test split:")
        logger.info(f"   - Train: {len(train_idx)} samples")
        logger.info(f"   - Test: {len(test_idx)} samples")
        
        return split_data


def main():
    """Main execution function."""
    # Paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / 'data' / 'crypto_with_competitive_context.json'
    output_path = project_root / 'narrative_integration' / 'data' / 'crypto_format_c.pkl'
    
    # Transform
    transformer = CryptoFormatCTransformer(str(data_path))
    transformer.load_data()
    format_c_data = transformer.transform()
    transformer.save(str(output_path))
    
    # Show sample
    print("\n" + "="*80)
    print("SAMPLE NARRATIVE DESCRIPTIONS (First 3)")
    print("="*80)
    for i, text in enumerate(format_c_data['data']['texts'][:3]):
        print(f"\n[{i+1}] {format_c_data['data']['metadata'][i]['name']}:")
        print(f"    {text}")
    
    print("\n" + "="*80)
    print("FEATURE SUMMARY")
    print("="*80)
    print(f"Feature names ({len(transformer.get_feature_names())}):")
    for i, fname in enumerate(transformer.get_feature_names(), 1):
        print(f"  {i:2d}. {fname}")
    
    print("\n" + "="*80)
    print("✅ FORMAT C TRANSFORMATION COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()

