"""Band Phonetic Lineage Analyzer

Analyzes how band names "rhyme" with and influence each other across time:
- Phonetic similarity networks (which bands sound alike?)
- Temporal influence (did Led Zeppelin inspire later mythological names?)
- Cohort clustering (1970s bands that share phonetic DNA)
- Success propagation (do successful name patterns get copied?)
- Linguistic genealogy (family trees of name styles)

Key Concepts:
- **Phonetic Neighborhoods:** Bands that sound similar
- **Temporal Precedence:** Earlier successful bands → later imitators
- **Cohort Resonance:** Bands in same decade sharing phonetic patterns
- **Cross-Generational Rhyming:** How 1960s patterns echo in 2010s
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
from datetime import datetime
import Levenshtein
from scipy import stats
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from core.models import db, Band, BandAnalysis

logger = logging.getLogger(__name__)


class BandPhoneticLineageAnalyzer:
    """Analyze phonetic influence and linguistic genealogy across band names."""
    
    def __init__(self):
        self.similarity_threshold = 0.7  # Threshold for "phonetically similar"
        
        # Phonetic feature groups for similarity matching
        self.plosives = set('ptkbdg')
        self.fricatives = set('fvsθðszʃʒhç')
        self.nasals = set('mnŋ')
        self.liquids = set('lrɹ')
        self.vowels = set('aeiouæɛɪɔʊəʌ')
    
    def get_comprehensive_dataset(self) -> pd.DataFrame:
        """Load all bands with complete phonetic analysis."""
        query = db.session.query(Band, BandAnalysis).join(
            BandAnalysis,
            Band.id == BandAnalysis.band_id
        ).order_by(Band.formation_year)  # Temporal ordering crucial
        
        rows = []
        for band, analysis in query.all():
            try:
                row = {
                    'id': band.id,
                    'name': band.name,
                    'formation_year': band.formation_year,
                    'formation_decade': band.formation_decade,
                    'origin_country': band.origin_country,
                    'genre_cluster': band.genre_cluster,
                    'popularity_score': band.popularity_score or 0,
                    'longevity_score': band.longevity_score or 0,
                    
                    # Phonetic features for similarity
                    'syllable_count': analysis.syllable_count or 0,
                    'character_length': analysis.character_length or 0,
                    'memorability_score': analysis.memorability_score or 0,
                    'harshness_score': analysis.harshness_score or 0,
                    'softness_score': analysis.softness_score or 0,
                    'fantasy_score': analysis.fantasy_score or 0,
                    'vowel_ratio': analysis.vowel_ratio or 0,
                    'abstraction_score': analysis.abstraction_score or 0,
                }
                
                rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error loading band {band.name}: {e}")
                continue
        
        return pd.DataFrame(rows)
    
    def analyze_phonetic_influence_networks(self, df: pd.DataFrame) -> Dict:
        """Analyze how bands influence each other through phonetic similarity.
        
        Args:
            df: DataFrame with band data (must be temporally ordered)
            
        Returns:
            Phonetic influence network analysis
        """
        logger.info("Analyzing phonetic influence networks...")
        
        results = {
            'similarity_network': {},
            'temporal_influence': {},
            'cohort_resonance': {},
            'success_propagation': {},
            'phonetic_families': {}
        }
        
        # 1. Build similarity network
        results['similarity_network'] = self._build_similarity_network(df)
        
        # 2. Temporal influence (successful bands → later imitators)
        results['temporal_influence'] = self._analyze_temporal_influence(df)
        
        # 3. Cohort resonance (within-decade similarity)
        results['cohort_resonance'] = self._analyze_cohort_resonance(df)
        
        # 4. Success propagation (do successful patterns get copied?)
        results['success_propagation'] = self._analyze_success_propagation(df)
        
        # 5. Phonetic families (linguistic genealogy)
        results['phonetic_families'] = self._identify_phonetic_families(df)
        
        return results
    
    def _build_similarity_network(self, df: pd.DataFrame) -> Dict:
        """Build network of phonetically similar bands.
        
        Uses multiple similarity measures:
        - Levenshtein distance (edit distance)
        - Phonetic feature cosine similarity
        - Syllable pattern matching
        
        Args:
            df: DataFrame with bands
            
        Returns:
            Similarity network
        """
        bands = df.to_dict('records')
        
        # Compute all pairwise similarities
        similarity_edges = []
        
        for i, band1 in enumerate(bands):
            for j, band2 in enumerate(bands):
                if i >= j:  # Avoid duplicates and self-comparison
                    continue
                
                # Compute composite similarity
                similarity = self._compute_phonetic_similarity(band1, band2)
                
                if similarity >= self.similarity_threshold:
                    similarity_edges.append({
                        'band1': band1['name'],
                        'band2': band2['name'],
                        'band1_year': band1['formation_year'],
                        'band2_year': band2['formation_year'],
                        'similarity': similarity,
                        'year_gap': abs(band1['formation_year'] - band2['formation_year']) if band1['formation_year'] and band2['formation_year'] else None,
                        'same_decade': band1['formation_decade'] == band2['formation_decade'],
                        'same_genre': band1['genre_cluster'] == band2['genre_cluster']
                    })
        
        # Sort by similarity
        similarity_edges.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Network statistics
        network_stats = {
            'total_edges': len(similarity_edges),
            'avg_similarity': float(np.mean([e['similarity'] for e in similarity_edges])) if similarity_edges else 0,
            'same_decade_percentage': float(np.mean([e['same_decade'] for e in similarity_edges]) * 100) if similarity_edges else 0,
            'same_genre_percentage': float(np.mean([e['same_genre'] for e in similarity_edges]) * 100) if similarity_edges else 0
        }
        
        return {
            'top_similar_pairs': similarity_edges[:50],  # Top 50 most similar
            'network_statistics': network_stats,
            'total_bands': len(bands)
        }
    
    def _compute_phonetic_similarity(self, band1: Dict, band2: Dict) -> float:
        """Compute composite phonetic similarity between two bands.
        
        Combines:
        - String edit distance (Levenshtein)
        - Phonetic feature similarity
        - Structural similarity (syllables, length)
        
        Args:
            band1: First band dictionary
            band2: Second band dictionary
            
        Returns:
            Similarity score (0-1)
        """
        name1 = band1['name'].lower()
        name2 = band2['name'].lower()
        
        # 1. Levenshtein similarity (normalized)
        lev_distance = Levenshtein.distance(name1, name2)
        max_len = max(len(name1), len(name2))
        lev_similarity = 1 - (lev_distance / max_len) if max_len > 0 else 0
        
        # 2. Phonetic feature similarity
        features1 = np.array([
            band1.get('syllable_count', 0),
            band1.get('character_length', 0),
            band1.get('harshness_score', 0),
            band1.get('softness_score', 0),
            band1.get('vowel_ratio', 0) * 100,
            band1.get('fantasy_score', 0),
            band1.get('memorability_score', 0)
        ])
        
        features2 = np.array([
            band2.get('syllable_count', 0),
            band2.get('character_length', 0),
            band2.get('harshness_score', 0),
            band2.get('softness_score', 0),
            band2.get('vowel_ratio', 0) * 100,
            band2.get('fantasy_score', 0),
            band2.get('memorability_score', 0)
        ])
        
        # Cosine similarity of feature vectors
        if np.linalg.norm(features1) > 0 and np.linalg.norm(features2) > 0:
            feature_similarity = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
        else:
            feature_similarity = 0
        
        # 3. Structural similarity (syllable and length)
        syllable_diff = abs(band1.get('syllable_count', 0) - band2.get('syllable_count', 0))
        length_diff = abs(band1.get('character_length', 0) - band2.get('character_length', 0))
        
        structural_similarity = 1 - min(1, (syllable_diff + length_diff/10) / 5)
        
        # Composite similarity (weighted average)
        composite = (
            lev_similarity * 0.4 +      # String similarity
            feature_similarity * 0.4 +   # Phonetic features
            structural_similarity * 0.2   # Structure
        )
        
        return max(0, min(1, composite))
    
    def _analyze_temporal_influence(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal influence: successful early bands → later similar bands.
        
        Tests: Did Led Zeppelin (1968, successful) inspire later mythological metal bands?
        
        Args:
            df: DataFrame (must be time-ordered)
            
        Returns:
            Temporal influence analysis
        """
        influence_patterns = []
        
        # Define "highly successful" early bands (formation < 1980, high popularity)
        influential_bands = df[
            (df['formation_year'] < 1980) & 
            (df['popularity_score'] > 75)
        ]
        
        logger.info(f"Found {len(influential_bands)} highly successful early bands")
        
        for idx, influential in influential_bands.iterrows():
            # Find later bands that are phonetically similar
            later_bands = df[
                (df['formation_year'] > influential['formation_year']) &
                (df['formation_year'] < influential['formation_year'] + 20)  # Within 20 years
            ]
            
            similar_later = []
            
            for idx2, later in later_bands.iterrows():
                similarity = self._compute_phonetic_similarity(
                    influential.to_dict(),
                    later.to_dict()
                )
                
                if similarity >= 0.65:  # Lower threshold for influence detection
                    similar_later.append({
                        'name': later['name'],
                        'year': later['formation_year'],
                        'year_gap': later['formation_year'] - influential['formation_year'],
                        'similarity': float(similarity),
                        'genre': later['genre_cluster'],
                        'popularity': later['popularity_score']
                    })
            
            if similar_later:
                # Sort by similarity
                similar_later.sort(key=lambda x: x['similarity'], reverse=True)
                
                influence_patterns.append({
                    'influential_band': influential['name'],
                    'year': influential['formation_year'],
                    'popularity': influential['popularity_score'],
                    'genre': influential['genre_cluster'],
                    'influenced_count': len(similar_later),
                    'influenced_bands': similar_later[:10],  # Top 10 most similar
                    'avg_year_gap': float(np.mean([b['year_gap'] for b in similar_later])),
                    'avg_similarity': float(np.mean([b['similarity'] for b in similar_later]))
                })
        
        # Sort by influence (number of similar later bands)
        influence_patterns.sort(key=lambda x: x['influenced_count'], reverse=True)
        
        return {
            'top_influencers': influence_patterns[:20],  # Top 20 most influential
            'total_influence_patterns': len(influence_patterns),
            'avg_influenced_per_band': float(np.mean([p['influenced_count'] for p in influence_patterns])) if influence_patterns else 0
        }
    
    def _analyze_cohort_resonance(self, df: pd.DataFrame) -> Dict:
        """Analyze phonetic similarity within decade cohorts.
        
        Tests: Do 1970s prog bands sound more alike than expected by chance?
        
        Args:
            df: DataFrame
            
        Returns:
            Cohort resonance analysis
        """
        cohort_patterns = {}
        
        decades = df['formation_decade'].dropna().unique()
        
        for decade in sorted(decades):
            decade_bands = df[df['formation_decade'] == decade]
            
            if len(decade_bands) < 10:
                continue
            
            # Compute within-cohort similarity
            within_cohort_similarities = []
            
            bands_list = decade_bands.to_dict('records')
            
            for i, band1 in enumerate(bands_list):
                for j, band2 in enumerate(bands_list):
                    if i >= j:
                        continue
                    
                    similarity = self._compute_phonetic_similarity(band1, band2)
                    within_cohort_similarities.append(similarity)
            
            if not within_cohort_similarities:
                continue
            
            avg_similarity = np.mean(within_cohort_similarities)
            
            # Compare to cross-cohort similarity (baseline)
            other_decades = df[df['formation_decade'] != decade]
            cross_cohort_similarities = []
            
            for band1 in decade_bands.to_dict('records')[:50]:  # Sample for efficiency
                for band2 in other_decades.sample(min(50, len(other_decades))).to_dict('records'):
                    similarity = self._compute_phonetic_similarity(band1, band2)
                    cross_cohort_similarities.append(similarity)
            
            baseline_similarity = np.mean(cross_cohort_similarities) if cross_cohort_similarities else 0
            
            # Test if within-cohort > cross-cohort (resonance)
            if len(within_cohort_similarities) > 10 and len(cross_cohort_similarities) > 10:
                t_stat, p_value = stats.ttest_ind(within_cohort_similarities, cross_cohort_similarities)
            else:
                t_stat, p_value = 0, 1
            
            cohort_patterns[f"{int(decade)}s"] = {
                'decade': int(decade),
                'sample_size': len(decade_bands),
                'avg_within_cohort_similarity': float(avg_similarity),
                'avg_cross_cohort_similarity': float(baseline_similarity),
                'resonance_effect': float(avg_similarity - baseline_similarity),
                'resonance_percentage': float(((avg_similarity - baseline_similarity) / baseline_similarity) * 100) if baseline_similarity > 0 else 0,
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant_resonance': p_value < 0.05,
                'interpretation': 'Bands sound more alike within decade' if avg_similarity > baseline_similarity else 'No cohort effect'
            }
        
        # Identify decade with strongest resonance
        resonance_values = [(d, p['resonance_effect']) for d, p in cohort_patterns.items() if p.get('significant_resonance')]
        
        if resonance_values:
            strongest_decade = max(resonance_values, key=lambda x: x[1])
        else:
            strongest_decade = None
        
        return {
            'by_decade': cohort_patterns,
            'strongest_resonance_decade': strongest_decade[0] if strongest_decade else None,
            'strongest_resonance_effect': strongest_decade[1] if strongest_decade else 0,
            'summary': f"Found significant cohort resonance in {len([p for p in cohort_patterns.values() if p.get('significant_resonance')])} decades"
        }
    
    def _analyze_success_propagation(self, df: pd.DataFrame) -> Dict:
        """Analyze if successful name patterns get copied by later bands.
        
        Tests: Do post-1970 bands copy Led Zeppelin-style mythological names?
        
        Args:
            df: DataFrame
            
        Returns:
            Success propagation analysis
        """
        logger.info("Analyzing success propagation...")
        
        results = {
            'pattern_propagation': [],
            'successful_patterns': [],
            'failed_patterns': []
        }
        
        # Define successful bands (top quartile popularity, formed before 1990)
        early_successful = df[
            (df['formation_year'] < 1990) &
            (df['popularity_score'] >= df['popularity_score'].quantile(0.75))
        ].copy()
        
        logger.info(f"Identified {len(early_successful)} early successful bands")
        
        # Group by phonetic archetype
        archetypes = self._classify_phonetic_archetypes(early_successful)
        
        for archetype_name, archetype_bands in archetypes.items():
            if len(archetype_bands) < 3:
                continue
            
            # Get average features of this archetype
            archetype_features = {
                'avg_syllables': np.mean([b['syllable_count'] for b in archetype_bands]),
                'avg_harshness': np.mean([b['harshness_score'] for b in archetype_bands]),
                'avg_fantasy': np.mean([b['fantasy_score'] for b in archetype_bands]),
                'avg_memorability': np.mean([b['memorability_score'] for b in archetype_bands])
            }
            
            # Find later bands (1990+) matching this archetype
            later_bands = df[df['formation_year'] >= 1990]
            
            matching_later = []
            for idx, later in later_bands.iterrows():
                # Check if later band matches archetype
                if self._matches_archetype(later.to_dict(), archetype_features):
                    matching_later.append({
                        'name': later['name'],
                        'year': later['formation_year'],
                        'popularity': later['popularity_score']
                    })
            
            if matching_later:
                # Compute average success of copycat bands
                avg_copycat_success = np.mean([b['popularity'] for b in matching_later])
                avg_original_success = np.mean([b['popularity_score'] for b in archetype_bands])
                
                results['pattern_propagation'].append({
                    'archetype': archetype_name,
                    'original_bands': [b['name'] for b in archetype_bands[:5]],
                    'original_avg_success': float(avg_original_success),
                    'copycat_count': len(matching_later),
                    'copycat_avg_success': float(avg_copycat_success),
                    'success_delta': float(avg_copycat_success - avg_original_success),
                    'propagation_rate': float((avg_copycat_success / avg_original_success)) if avg_original_success > 0 else 0,
                    'example_copycats': [b['name'] for b in matching_later[:5]]
                })
        
        # Sort by copycat count (most propagated patterns)
        results['pattern_propagation'].sort(key=lambda x: x['copycat_count'], reverse=True)
        
        return results
    
    def _classify_phonetic_archetypes(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Classify bands into phonetic archetypes.
        
        Args:
            df: DataFrame
            
        Returns:
            Dictionary of archetype → bands
        """
        archetypes = defaultdict(list)
        
        for idx, band in df.iterrows():
            band_dict = band.to_dict()
            
            # Classify based on phonetic signature
            syllables = band_dict.get('syllable_count', 0)
            harshness = band_dict.get('harshness_score', 0)
            fantasy = band_dict.get('fantasy_score', 0)
            
            if harshness > 65 and syllables <= 3:
                archetype = 'harsh_short'  # Metallica, Slayer
            elif fantasy > 65 and syllables > 3:
                archetype = 'epic_fantasy'  # Led Zeppelin, Iron Maiden
            elif syllables == 1:
                archetype = 'monosyllabic'  # Rush, Muse, Tool
            elif fantasy > 60 and harshness > 60:
                archetype = 'dark_mythic'  # Black Sabbath, Dio
            elif harshness < 35 and syllables > 2:
                archetype = 'soft_melodic'  # Simon & Garfunkel, Fleet Foxes
            else:
                archetype = 'balanced'
            
            archetypes[archetype].append(band_dict)
        
        return dict(archetypes)
    
    def _matches_archetype(self, band: Dict, archetype_features: Dict, tolerance: float = 0.3) -> bool:
        """Check if a band matches an archetype (within tolerance).
        
        Args:
            band: Band dictionary
            archetype_features: Average features of archetype
            tolerance: Matching tolerance (0-1)
            
        Returns:
            True if matches archetype
        """
        # Compute normalized distance in feature space
        features_to_check = ['avg_syllables', 'avg_harshness', 'avg_fantasy', 'avg_memorability']
        
        distances = []
        for feature in features_to_check:
            archetype_val = archetype_features.get(feature, 0)
            
            # Map to band features
            band_feature = feature.replace('avg_', '') + '_score'
            if 'syllables' in feature:
                band_feature = 'syllable_count'
            
            band_val = band.get(band_feature, 0)
            
            # Normalized distance
            if archetype_val > 0:
                normalized_dist = abs(band_val - archetype_val) / archetype_val
                distances.append(normalized_dist)
        
        # Average distance
        avg_distance = np.mean(distances) if distances else 1
        
        return avg_distance <= tolerance
    
    def _identify_phonetic_families(self, df: pd.DataFrame) -> Dict:
        """Identify phonetic families (genealogical trees of similar names).
        
        Like evolutionary trees: Common ancestors → branching lineages
        
        Args:
            df: DataFrame
            
        Returns:
            Phonetic family trees
        """
        logger.info("Identifying phonetic families...")
        
        families = {}
        
        # Seed families with highly influential bands
        seeds = [
            {'name': 'The Beatles', 'pattern': 'The_[Animal/Insect]', 'features': 'simple_memorable'},
            {'name': 'Led Zeppelin', 'pattern': 'Mythological_Reference', 'features': 'epic_fantasy'},
            {'name': 'Black Sabbath', 'pattern': 'Dark_Ominous', 'features': 'occult_harsh'},
            {'name': 'The Ramones', 'pattern': 'The_[Surname]', 'features': 'punk_simple'},
            {'name': 'Metallica', 'pattern': '[Metal]_Suffix', 'features': 'harsh_monosyllabic'},
        ]
        
        for seed in seeds:
            seed_name = seed['name']
            seed_band = df[df['name'] == seed_name]
            
            if len(seed_band) == 0:
                # If exact name not found, skip (will exist after collection)
                families[seed['pattern']] = {
                    'archetype': seed_name,
                    'pattern_description': seed['pattern'],
                    'phonetic_features': seed['features'],
                    'descendants': [],
                    'descendant_count': 0,
                    'avg_descendant_success': 0,
                    'status': 'pending_data_collection'
                }
                continue
            
            seed_dict = seed_band.iloc[0].to_dict()
            seed_year = seed_dict.get('formation_year')
            
            # Find descendants (later similar bands)
            if seed_year:
                later_bands = df[df['formation_year'] > seed_year]
                
                descendants = []
                for idx, later in later_bands.iterrows():
                    similarity = self._compute_phonetic_similarity(seed_dict, later.to_dict())
                    
                    if similarity >= 0.65:
                        descendants.append({
                            'name': later['name'],
                            'year': later['formation_year'],
                            'year_gap': later['formation_year'] - seed_year,
                            'similarity': float(similarity),
                            'popularity': later['popularity_score']
                        })
                
                families[seed['pattern']] = {
                    'archetype': seed_name,
                    'year': seed_year,
                    'pattern_description': seed['pattern'],
                    'phonetic_features': seed['features'],
                    'descendants': descendants[:20],  # Top 20
                    'descendant_count': len(descendants),
                    'avg_descendant_success': float(np.mean([d['popularity'] for d in descendants])) if descendants else 0,
                    'original_success': float(seed_dict.get('popularity_score', 0))
                }
        
        return families
    
    def analyze_cross_generational_rhyming(self, df: pd.DataFrame) -> Dict:
        """Analyze how naming patterns cycle across generations.
        
        Tests: Do 2010s bands revive 1960s simplicity after 1990s complexity?
        
        Args:
            df: DataFrame
            
        Returns:
            Cross-generational rhyming analysis
        """
        logger.info("Analyzing cross-generational rhyming...")
        
        results = {
            'decade_similarity_matrix': {},
            'rhyming_patterns': [],
            'cyclical_trends': {}
        }
        
        decades = sorted([d for d in df['formation_decade'].dropna().unique() if d >= 1960])
        
        # Build similarity matrix (decade × decade)
        similarity_matrix = {}
        
        for decade1 in decades:
            similarity_matrix[f"{int(decade1)}s"] = {}
            
            bands1 = df[df['formation_decade'] == decade1].to_dict('records')
            
            for decade2 in decades:
                if decade1 == decade2:
                    continue
                
                bands2 = df[df['formation_decade'] == decade2].to_dict('records')
                
                # Compute average cross-decade similarity
                similarities = []
                
                for band1 in bands1[:100]:  # Sample for efficiency
                    for band2 in bands2[:100]:
                        sim = self._compute_phonetic_similarity(band1, band2)
                        similarities.append(sim)
                
                avg_sim = np.mean(similarities) if similarities else 0
                
                similarity_matrix[f"{int(decade1)}s"][f"{int(decade2)}s"] = float(avg_sim)
        
        results['decade_similarity_matrix'] = similarity_matrix
        
        # Identify rhyming patterns (non-adjacent decades with high similarity)
        for decade1_str, decade2_sims in similarity_matrix.items():
            decade1_year = int(decade1_str.replace('s', ''))
            
            for decade2_str, similarity in decade2_sims.items():
                decade2_year = int(decade2_str.replace('s', ''))
                
                year_gap = abs(decade2_year - decade1_year)
                
                # Look for high similarity in non-adjacent decades
                if year_gap >= 20 and similarity >= 0.35:
                    results['rhyming_patterns'].append({
                        'decade1': decade1_str,
                        'decade2': decade2_str,
                        'year_gap': year_gap,
                        'similarity': float(similarity),
                        'pattern': f"{decade1_str} ↔ {decade2_str}",
                        'interpretation': self._interpret_rhyming(decade1_year, decade2_year, similarity)
                    })
        
        # Sort by similarity (strongest rhymes first)
        results['rhyming_patterns'].sort(key=lambda x: x['similarity'], reverse=True)
        
        # Detect cyclical trends
        results['cyclical_trends'] = self._detect_cyclical_patterns(similarity_matrix, decades)
        
        return results
    
    def _interpret_rhyming(self, decade1: int, decade2: int, similarity: float) -> str:
        """Interpret a cross-generational rhyming pattern.
        
        Args:
            decade1: First decade
            decade2: Second decade
            similarity: Similarity score
            
        Returns:
            Interpretation string
        """
        gap = abs(decade2 - decade1)
        
        if gap == 20:
            return f"20-year echo: {decade1}s patterns resurface in {decade2}s"
        elif gap == 30:
            return f"Generational revival: {decade2}s resurrects {decade1}s aesthetics"
        elif gap == 40:
            return f"Long-term cycle: {decade2}s reaches back to {decade1}s roots"
        elif gap >= 50:
            return f"Full-circle return: {decade2}s returns to {decade1}s fundamentals after intervening complexity"
        else:
            return f"Cross-generational similarity: {gap}-year gap"
    
    def _detect_cyclical_patterns(self, similarity_matrix: Dict, decades: List) -> Dict:
        """Detect cyclical patterns in naming trends.
        
        Tests: Complexity → Simplicity → Complexity cycles
        
        Args:
            similarity_matrix: Decade similarity matrix
            decades: List of decades
            
        Returns:
            Cyclical pattern analysis
        """
        # Hypothesis: 1960s simple → 1970s complex → 1990s simple → 2010s complex
        
        # Find if 1960s and 1990s are more similar than expected (both "simple" eras)
        # Find if 1970s and 2010s are more similar than expected (both "complex" eras)
        
        cycles = []
        
        simple_eras = [1960, 1990]  # Hypothesized simple eras
        complex_eras = [1970, 2000]  # Hypothesized complex eras
        
        # Check within-group similarity
        if f"{simple_eras[0]}s" in similarity_matrix and f"{simple_eras[1]}s" in similarity_matrix[f"{simple_eras[0]}s"]:
            simple_similarity = similarity_matrix[f"{simple_eras[0]}s"][f"{simple_eras[1]}s"]
            
            cycles.append({
                'cycle_type': 'Simple eras',
                'decades': f"{simple_eras[0]}s & {simple_eras[1]}s",
                'similarity': float(simple_similarity),
                'interpretation': 'Return to simplicity after complex 1970s-1980s'
            })
        
        if f"{complex_eras[0]}s" in similarity_matrix and f"{complex_eras[1]}s" in similarity_matrix[f"{complex_eras[0]}s"]:
            complex_similarity = similarity_matrix[f"{complex_eras[0]}s"][f"{complex_eras[1]}s"]
            
            cycles.append({
                'cycle_type': 'Complex eras',
                'decades': f"{complex_eras[0]}s & {complex_eras[1]}s",
                'similarity': float(complex_similarity),
                'interpretation': 'Shared complexity aesthetic across generations'
            })
        
        return {
            'detected_cycles': cycles,
            'cyclical_hypothesis': 'Alternating simplicity/complexity cycle',
            'status': 'Testable with full dataset'
        }
    
    def identify_phonetic_neighborhoods(self, df: pd.DataFrame, target_band: str) -> Dict:
        """Identify phonetic neighborhood for a specific band.
        
        Like finding musical "relatives" based on name sound.
        
        Args:
            df: DataFrame
            target_band: Band name to analyze
            
        Returns:
            Phonetic neighborhood analysis
        """
        target = df[df['name'].str.lower() == target_band.lower()]
        
        if len(target) == 0:
            return {'error': f'Band "{target_band}" not found'}
        
        target_dict = target.iloc[0].to_dict()
        
        # Compute similarity to all other bands
        neighbors = []
        
        for idx, other in df.iterrows():
            if other['name'].lower() == target_band.lower():
                continue
            
            similarity = self._compute_phonetic_similarity(target_dict, other.to_dict())
            
            if similarity >= 0.5:  # Moderate threshold
                neighbors.append({
                    'name': other['name'],
                    'similarity': float(similarity),
                    'year': other['formation_year'],
                    'year_relative': 'earlier' if other['formation_year'] < target_dict['formation_year'] else 'later',
                    'genre': other['genre_cluster'],
                    'popularity': other['popularity_score']
                })
        
        # Sort by similarity
        neighbors.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Classify neighbors
        earlier_neighbors = [n for n in neighbors if n['year_relative'] == 'earlier']
        later_neighbors = [n for n in neighbors if n['year_relative'] == 'later']
        same_genre = [n for n in neighbors if n['genre'] == target_dict['genre_cluster']]
        
        return {
            'target_band': target_band,
            'target_year': target_dict['formation_year'],
            'target_genre': target_dict['genre_cluster'],
            'total_neighbors': len(neighbors),
            'closest_neighbors': neighbors[:10],
            'earlier_influences': earlier_neighbors[:5],
            'later_influenced': later_neighbors[:5],
            'same_genre_neighbors': same_genre[:5],
            'neighborhood_density': len(neighbors),
            'interpretation': self._interpret_neighborhood(neighbors, target_dict)
        }
    
    def _interpret_neighborhood(self, neighbors: List[Dict], target: Dict) -> str:
        """Interpret the phonetic neighborhood.
        
        Args:
            neighbors: List of neighbor bands
            target: Target band
            
        Returns:
            Interpretation string
        """
        if len(neighbors) == 0:
            return "Highly unique name, no close phonetic neighbors"
        elif len(neighbors) < 5:
            return "Distinctive name with few phonetic relatives"
        elif len(neighbors) < 15:
            return "Moderately common phonetic pattern"
        else:
            earlier = len([n for n in neighbors if n['year_relative'] == 'earlier'])
            later = len([n for n in neighbors if n['year_relative'] == 'later'])
            
            if earlier > later * 2:
                return f"Influenced by {earlier} earlier bands, minimal propagation"
            elif later > earlier * 2:
                return f"Highly influential: {later} later bands share phonetic DNA"
            else:
                return f"Part of broad phonetic trend spanning decades"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = BandPhoneticLineageAnalyzer()
    df = analyzer.get_comprehensive_dataset()
    
    if len(df) >= 50:
        print("\n" + "="*80)
        print("PHONETIC LINEAGE & INFLUENCE ANALYSIS")
        print("="*80)
        
        # Analyze influence networks
        print("\n🎸 Analyzing phonetic influence networks...")
        influence_results = analyzer.analyze_phonetic_influence_networks(df)
        
        # Print top influencers
        if 'temporal_influence' in influence_results:
            print("\nTop Influential Bands (inspired later similar names):")
            for influencer in influence_results['temporal_influence'].get('top_influencers', [])[:5]:
                print(f"\n{influencer['influential_band']} ({influencer['year']}):")
                print(f"  Influenced: {influencer['influenced_count']} later bands")
                print(f"  Examples: {', '.join([b['name'] for b in influencer['influenced_bands'][:3]])}")
        
        # Cross-generational rhyming
        print("\n\n🔄 Analyzing cross-generational rhyming...")
        rhyming_results = analyzer.analyze_cross_generational_rhyming(df)
        
        if rhyming_results['rhyming_patterns']:
            print("\nStrongest Cross-Generational Rhymes:")
            for rhyme in rhyming_results['rhyming_patterns'][:5]:
                print(f"\n{rhyme['pattern']}: similarity {rhyme['similarity']:.3f}")
                print(f"  {rhyme['interpretation']}")
        
        # Cohort resonance
        if 'cohort_resonance' in influence_results:
            print("\n\n🎭 Cohort Resonance (within-decade similarity):")
            for decade, data in influence_results['cohort_resonance']['by_decade'].items():
                if data.get('significant_resonance'):
                    print(f"\n{decade}: +{data['resonance_percentage']:.1f}% higher within-cohort similarity")
                    print(f"  p = {data['p_value']:.4f} ⭐")
        
    else:
        print("Insufficient data. Run: python3 scripts/collect_bands.py")

