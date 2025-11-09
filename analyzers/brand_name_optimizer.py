"""
AI Brand Name Generator and Optimizer
======================================

Generates optimal brand names based on target characteristics using genetic algorithms
and multi-objective optimization.

Features:
- Genetic algorithm for name evolution
- Multi-objective optimization (melodiousness, prophecy, universality)
- Constraint satisfaction (length, pronounceability, cultural fit)
- Phonetic pattern generation
- Success prediction for generated names
"""

import logging
import numpy as np
import random
from typing import Dict, List, Optional, Tuple
from collections import Counter

from analyzers.foretold_naming_analyzer import foretold_analyzer
from analyzers.acoustic_analyzer import acoustic_analyzer
from analyzers.phonetic_universals_analyzer import phonetic_universals_analyzer

logger = logging.getLogger(__name__)


class BrandNameOptimizer:
    """Generate and optimize brand names using AI."""
    
    # Phonetic building blocks
    CONSONANTS = list('bcdfghjklmnpqrstvwxyz')
    VOWELS = list('aeiou')
    SYLLABLE_PATTERNS = ['CV', 'CVC', 'V', 'VC', 'CCV', 'VCC']
    
    PREFIXES = ['neo', 'pro', 'ultra', 'meta', 'hyper', 'super', 'mega', 'omni', 'uni', 'bio']
    ROOTS = ['tech', 'zen', 'lux', 'nova', 'vita', 'sol', 'luna', 'terra', 'aqua', 'aero']
    SUFFIXES = ['ify', 'ize', 'ity', 'ist', 'ion', 'ics', 'ous', 'al', 'ic', 'ent']
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("BrandNameOptimizer initialized")
    
    def generate_optimized_names(self, target_characteristics: Dict, 
                                n_candidates: int = 20,
                                n_generations: int = 50) -> List[Dict]:
        """
        Generate optimized brand names using genetic algorithm.
        
        Args:
            target_characteristics: Dict specifying desired traits:
                - melodiousness: 0-1 target
                - prophetic_score: 0-1 target
                - universal_appeal: 0-1 target
                - length_min, length_max: character limits
                - cultural_origin: preferred origin (optional)
            n_candidates: Number of candidate names to generate
            n_generations: Genetic algorithm generations
        
        Returns:
            List of optimized names with scores
        """
        self.logger.info(f"Generating {n_candidates} names over {n_generations} generations")
        
        # Initialize population
        population = self._initialize_population(100, target_characteristics)
        
        # Evolve
        for generation in range(n_generations):
            # Evaluate fitness
            fitness_scores = []
            for name in population:
                fitness = self._evaluate_fitness(name, target_characteristics)
                fitness_scores.append((name, fitness))
            
            # Sort by fitness
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top performers
            survivors = [name for name, _ in fitness_scores[:50]]
            
            # Create next generation
            population = survivors.copy()
            
            # Crossover and mutation
            while len(population) < 100:
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                
                population.append(child)
            
            if (generation + 1) % 10 == 0:
                self.logger.info(f"Generation {generation+1}: Best fitness = {fitness_scores[0][1]:.3f}")
        
        # Final evaluation
        final_candidates = []
        for name in population[:n_candidates]:
            analysis = self._comprehensive_evaluation(name, target_characteristics)
            final_candidates.append(analysis)
        
        # Sort by overall score
        final_candidates.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return final_candidates
    
    def _initialize_population(self, size: int, targets: Dict) -> List[str]:
        """Initialize population of random names."""
        population = []
        
        for _ in range(size):
            # Random generation method
            method = random.choice(['syllabic', 'compound', 'phonetic'])
            
            if method == 'syllabic':
                name = self._generate_syllabic()
            elif method == 'compound':
                name = self._generate_compound()
            else:
                name = self._generate_phonetic()
            
            # Ensure length constraints
            min_len = targets.get('length_min', 4)
            max_len = targets.get('length_max', 12)
            
            if min_len <= len(name) <= max_len:
                population.append(name)
        
        return population
    
    def _generate_syllabic(self) -> str:
        """Generate name from syllable patterns."""
        n_syllables = random.randint(2, 4)
        name = ''
        
        for _ in range(n_syllables):
            pattern = random.choice(self.SYLLABLE_PATTERNS)
            for char_type in pattern:
                if char_type == 'C':
                    name += random.choice(self.CONSONANTS)
                else:
                    name += random.choice(self.VOWELS)
        
        return name.capitalize()
    
    def _generate_compound(self) -> str:
        """Generate compound name from prefix+root or root+suffix."""
        if random.random() < 0.5:
            return (random.choice(self.PREFIXES) + random.choice(self.ROOTS)).capitalize()
        else:
            return (random.choice(self.ROOTS) + random.choice(self.SUFFIXES)).capitalize()
    
    def _generate_phonetic(self) -> str:
        """Generate phonetically balanced name."""
        length = random.randint(5, 10)
        name = ''
        
        for i in range(length):
            if i % 2 == 0:
                name += random.choice(self.CONSONANTS)
            else:
                name += random.choice(self.VOWELS)
        
        return name.capitalize()
    
    def _evaluate_fitness(self, name: str, targets: Dict) -> float:
        """Evaluate fitness of name against targets."""
        try:
            # Get acoustic analysis
            acoustic = acoustic_analyzer.analyze(name)
            universals = phonetic_universals_analyzer.analyze(name)
            
            # Extract scores
            melodiousness = acoustic.get('overall', {}).get('melodiousness', 0.5)
            universal_pronounce = acoustic.get('pronounceability', {}).get('universal', 0.5)
            universal_valence = (universals.get('emotional_valence', {}).get('universal', 0) + 1) / 2  # Scale to 0-1
            
            # Calculate distance from targets
            target_melodiousness = targets.get('melodiousness', 0.7)
            target_universal = targets.get('universal_appeal', 0.7)
            target_valence = targets.get('emotional_valence', 0.7)
            
            melodiousness_dist = abs(melodiousness - target_melodiousness)
            universal_dist = abs(universal_pronounce - target_universal)
            valence_dist = abs(universal_valence - target_valence)
            
            # Fitness = 1 - average distance
            fitness = 1 - (melodiousness_dist + universal_dist + valence_dist) / 3
            
            # Penalty for length constraints
            min_len = targets.get('length_min', 4)
            max_len = targets.get('length_max', 12)
            
            if len(name) < min_len or len(name) > max_len:
                fitness *= 0.5
            
            return max(fitness, 0)
        
        except Exception as e:
            self.logger.error(f"Error evaluating {name}: {e}")
            return 0.0
    
    def _crossover(self, parent1: str, parent2: str) -> str:
        """Create child name from two parents."""
        # Split at random point
        split = random.randint(1, min(len(parent1), len(parent2)) - 1)
        
        if random.random() < 0.5:
            child = parent1[:split] + parent2[split:]
        else:
            child = parent2[:split] + parent1[split:]
        
        return child.capitalize()
    
    def _mutate(self, name: str, mutation_rate: float = 0.1) -> str:
        """Mutate name with small probability."""
        name_list = list(name.lower())
        
        for i in range(len(name_list)):
            if random.random() < mutation_rate:
                # Mutate this character
                if name_list[i] in self.VOWELS:
                    name_list[i] = random.choice(self.VOWELS)
                elif name_list[i] in self.CONSONANTS:
                    name_list[i] = random.choice(self.CONSONANTS)
        
        return ''.join(name_list).capitalize()
    
    def _comprehensive_evaluation(self, name: str, targets: Dict) -> Dict:
        """Comprehensive evaluation of generated name."""
        try:
            # Get all analyses
            acoustic = acoustic_analyzer.analyze(name)
            universals = phonetic_universals_analyzer.analyze(name)
            
            # Extract key metrics
            melodiousness = acoustic.get('overall', {}).get('melodiousness', 0.5)
            harshness = acoustic.get('harshness', {}).get('overall_score', 0.5)
            universal_pronounce = acoustic.get('pronounceability', {}).get('universal', 0.5)
            bouba_kiki = universals.get('bouba_kiki', {}).get('score', 0)
            emotional_valence = universals.get('emotional_valence', {}).get('universal', 0)
            
            # Overall score
            overall = (melodiousness + universal_pronounce + (emotional_valence + 1) / 2) / 3
            
            return {
                'name': name,
                'overall_score': float(overall),
                'metrics': {
                    'melodiousness': float(melodiousness),
                    'harshness': float(harshness),
                    'universal_pronounceability': float(universal_pronounce),
                    'bouba_kiki_score': float(bouba_kiki),
                    'emotional_valence': float(emotional_valence),
                },
                'fit_to_targets': {
                    'melodiousness': 1 - abs(melodiousness - targets.get('melodiousness', 0.7)),
                    'universal': 1 - abs(universal_pronounce - targets.get('universal_appeal', 0.7))
                },
                'recommendation': 'Excellent' if overall > 0.8 else 'Good' if overall > 0.6 else 'Fair'
            }
        
        except Exception as e:
            self.logger.error(f"Error evaluating {name}: {e}")
            return {'name': name, 'error': str(e)}


# Singleton
brand_optimizer = BrandNameOptimizer()

