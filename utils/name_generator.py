"""
AI Name Generator
Generate optimal cryptocurrency names using evolutionary algorithms
"""

import random
import string
from predictor import NamePredictor
from analyzers.advanced_analyzer import AdvancedAnalyzer
from analyzers.esoteric_analyzer import EsotericAnalyzer
from analyzers.name_analyzer import NameAnalyzer


class NameGenerator:
    """Generate and optimize cryptocurrency names"""
    
    def __init__(self):
        self.predictor = NamePredictor()
        self.name_analyzer = NameAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.esoteric_analyzer = EsotericAnalyzer()
        
        # Building blocks for name generation
        self.prefixes = [
            'bit', 'byte', 'coin', 'cash', 'pay', 'swap', 'chain', 'link', 'net',
            'cyber', 'meta', 'ultra', 'hyper', 'mega', 'giga', 'nano', 'micro',
            'quantum', 'neo', 'prime', 'pro', 'alpha', 'beta', 'omega', 'apex',
            'stellar', 'luna', 'sol', 'terra', 'cosmos', 'nexus', 'aether'
        ]
        
        self.suffixes = [
            'coin', 'token', 'cash', 'pay', 'swap', 'trade', 'finance', 'network',
            'protocol', 'chain', 'link', 'verse', 'space', 'world', 'hub', 'lab',
            'dao', 'defi', 'fi', 'ex', 'x', 'z', 'ai', 'io', 'ly'
        ]
        
        self.roots = [
            'star', 'moon', 'sun', 'fire', 'water', 'earth', 'wind', 'gold',
            'silver', 'diamond', 'crystal', 'titan', 'dragon', 'phoenix', 'wolf',
            'bear', 'lion', 'eagle', 'shark', 'whale', 'safe', 'trust', 'secure',
            'fast', 'instant', 'quick', 'smart', 'wise', 'power', 'magic', 'zen'
        ]
        
        self.vowels = 'aeiou'
        self.consonants = 'bcdfghjklmnpqrstvwxyz'
    
    def generate(self, count=100, constraints=None):
        """
        Generate cryptocurrency names
        
        Args:
            count: Number of names to generate
            constraints: Dict with generation constraints
                - min_length: Minimum name length
                - max_length: Maximum name length
                - target_memorability: Target memorability score
                - target_uniqueness: Target uniqueness score
                - required_pattern: Required pattern (e.g., 'starts_with_b')
                - name_type: Preferred type (animal, tech, etc.)
                - no_numbers: Avoid numbers if True
                
        Returns:
            List of generated names with scores
        """
        constraints = constraints or {}
        
        candidates = []
        generation_methods = [
            self._generate_compound,
            self._generate_portmanteau,
            self._generate_phonetic,
            self._generate_random_syllables,
            self._generate_mutated
        ]
        
        # Generate initial population
        for _ in range(count):
            method = random.choice(generation_methods)
            name = method(constraints)
            
            if name and self._meets_constraints(name, constraints):
                candidates.append(name)
        
        # Remove duplicates
        candidates = list(set(candidates))
        
        # Score each candidate
        scored_candidates = []
        for name in candidates:
            try:
                score = self._score_name(name, constraints)
                scored_candidates.append({
                    'name': name,
                    'score': score['total_score'],
                    'details': score
                })
            except:
                continue
        
        # Sort by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_candidates
    
    def evolve(self, population_size=50, generations=10, constraints=None):
        """
        Use evolutionary algorithm to generate optimal names
        
        Args:
            population_size: Size of each generation
            generations: Number of generations to evolve
            constraints: Generation constraints
            
        Returns:
            Best names from final generation
        """
        # Initialize population
        population = self.generate(population_size, constraints)
        
        for gen in range(generations):
            # Select top performers (elitism)
            elite_count = max(5, population_size // 5)
            elite = population[:elite_count]
            
            # Generate offspring through crossover and mutation
            offspring = []
            
            while len(offspring) + len(elite) < population_size:
                # Select parents (tournament selection)
                parent1 = self._tournament_select(population)
                parent2 = self._tournament_select(population)
                
                # Crossover
                child = self._crossover(parent1['name'], parent2['name'])
                
                # Mutation
                if random.random() < 0.3:  # 30% mutation rate
                    child = self._mutate(child)
                
                if child and self._meets_constraints(child, constraints):
                    score = self._score_name(child, constraints)
                    offspring.append({
                        'name': child,
                        'score': score['total_score'],
                        'details': score
                    })
            
            # New generation
            population = elite + offspring
            population.sort(key=lambda x: x['score'], reverse=True)
            population = population[:population_size]
        
        return population
    
    def _generate_compound(self, constraints):
        """Generate compound name (prefix + root/suffix)"""
        patterns = [
            lambda: random.choice(self.prefixes) + random.choice(self.roots),
            lambda: random.choice(self.roots) + random.choice(self.suffixes),
            lambda: random.choice(self.prefixes) + random.choice(self.suffixes),
        ]
        
        name = random.choice(patterns)()
        return self._capitalize_name(name)
    
    def _generate_portmanteau(self, constraints):
        """Generate portmanteau (blend two words)"""
        word1 = random.choice(self.roots + self.prefixes)
        word2 = random.choice(self.roots + self.suffixes)
        
        # Take first part of word1 and last part of word2
        split1 = random.randint(2, len(word1) - 1)
        split2 = random.randint(1, len(word2) - 2)
        
        name = word1[:split1] + word2[split2:]
        return self._capitalize_name(name)
    
    def _generate_phonetic(self, constraints):
        """Generate phonetically pleasing name"""
        # Alternate consonants and vowels
        length = random.randint(4, 8)
        name = ''
        
        start_with_consonant = random.choice([True, False])
        
        for i in range(length):
            if (i % 2 == 0) == start_with_consonant:
                name += random.choice(self.consonants)
            else:
                name += random.choice(self.vowels)
        
        return self._capitalize_name(name)
    
    def _generate_random_syllables(self, constraints):
        """Generate name from random syllables"""
        syllable_count = random.randint(2, 4)
        
        name = ''
        for _ in range(syllable_count):
            # Consonant + vowel or consonant + vowel + consonant
            if random.random() < 0.5:
                syl = random.choice(self.consonants) + random.choice(self.vowels)
            else:
                syl = random.choice(self.consonants) + random.choice(self.vowels) + \
                      random.choice(self.consonants)
            name += syl
        
        return self._capitalize_name(name)
    
    def _generate_mutated(self, constraints):
        """Generate by mutating existing successful pattern"""
        base = random.choice(self.prefixes + self.roots)
        
        operations = [
            lambda x: x + random.choice(self.vowels),  # Add vowel
            lambda x: x + random.choice(self.consonants),  # Add consonant
            lambda x: x[:-1] if len(x) > 3 else x,  # Remove last char
            lambda x: x[0] + random.choice(self.vowels) + x[1:],  # Insert vowel
        ]
        
        name = random.choice(operations)(base)
        return self._capitalize_name(name)
    
    def _capitalize_name(self, name):
        """Apply capitalization pattern"""
        patterns = [
            lambda x: x.lower(),  # all lowercase
            lambda x: x.capitalize(),  # First letter capital
            lambda x: x.upper() if len(x) <= 4 else x.capitalize(),  # Acronym style
        ]
        
        return random.choice(patterns)(name)
    
    def _meets_constraints(self, name, constraints):
        """Check if name meets constraints"""
        if not name:
            return False
        
        if 'min_length' in constraints:
            if len(name) < constraints['min_length']:
                return False
        
        if 'max_length' in constraints:
            if len(name) > constraints['max_length']:
                return False
        
        if constraints.get('no_numbers') and any(c.isdigit() for c in name):
            return False
        
        if 'required_pattern' in constraints:
            pattern = constraints['required_pattern']
            if pattern.startswith('starts_with_'):
                char = pattern.split('_')[-1]
                if not name.lower().startswith(char):
                    return False
        
        return True
    
    def _score_name(self, name, constraints=None):
        """
        Score a name based on all metrics
        
        Returns:
            Dict with component scores and total
        """
        constraints = constraints or {}
        
        # Get all analyses
        basic = self.name_analyzer.analyze_name(name, None)
        advanced = self.advanced_analyzer.analyze(name, None)
        esoteric = self.esoteric_analyzer.analyze(name, None)
        
        # Component scores (0-100 each)
        scores = {
            'memorability': basic.get('memorability_score', 50),
            'uniqueness': basic.get('uniqueness_score', 50) if basic.get('uniqueness_score') else 50,
            'phonetic_appeal': basic.get('phonetic_score', 50),
            'pronounceability': basic.get('pronounceability_score', 50),
            'authority': advanced.get('authority_score', 50),
            'innovation': advanced.get('innovation_score', 50),
            'trust': advanced.get('trust_score', 50),
            'logo_friendliness': advanced.get('logo_friendliness', 50),
        }
        
        # Apply weights based on constraints
        weights = {
            'memorability': constraints.get('memorability_weight', 1.5),
            'uniqueness': constraints.get('uniqueness_weight', 1.2),
            'phonetic_appeal': 1.0,
            'pronounceability': 1.0,
            'authority': 0.8,
            'innovation': constraints.get('innovation_weight', 1.0),
            'trust': 0.8,
            'logo_friendliness': 0.7,
        }
        
        # Calculate weighted total
        total = 0
        total_weight = 0
        
        for component, score in scores.items():
            weight = weights.get(component, 1.0)
            total += score * weight
            total_weight += weight
        
        total_score = total / total_weight if total_weight > 0 else 50
        
        return {
            'component_scores': scores,
            'weights': weights,
            'total_score': round(total_score, 2),
            'length': len(name),
            'syllables': basic.get('syllable_count', 0)
        }
    
    def _tournament_select(self, population, tournament_size=3):
        """Select individual through tournament selection"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x['score'])
    
    def _crossover(self, parent1, parent2):
        """Create offspring by crossing over two parent names"""
        if len(parent1) < 2 or len(parent2) < 2:
            return parent1
        
        # Single-point crossover
        point1 = random.randint(1, len(parent1) - 1)
        point2 = random.randint(1, len(parent2) - 1)
        
        # Try different crossover strategies
        strategies = [
            parent1[:point1] + parent2[point2:],
            parent2[:point2] + parent1[point1:],
            parent1[:point1] + parent2[point2:point2+2] if point2+2 <= len(parent2) else parent1[:point1] + parent2[point2:],
        ]
        
        child = random.choice(strategies)
        
        # Ensure reasonable length
        if len(child) < 3:
            child = parent1[:2] + parent2[:2]
        elif len(child) > 15:
            child = child[:15]
        
        return child
    
    def _mutate(self, name):
        """Mutate a name"""
        if not name or len(name) < 2:
            return name
        
        mutations = [
            self._swap_random_char,
            self._insert_random_char,
            self._delete_random_char,
            self._change_capitalization,
        ]
        
        mutator = random.choice(mutations)
        return mutator(name)
    
    def _swap_random_char(self, name):
        """Swap a random character"""
        pos = random.randint(0, len(name) - 1)
        char_type = 'vowel' if name[pos].lower() in self.vowels else 'consonant'
        
        if char_type == 'vowel':
            new_char = random.choice(self.vowels)
        else:
            new_char = random.choice(self.consonants)
        
        return name[:pos] + new_char + name[pos+1:]
    
    def _insert_random_char(self, name):
        """Insert a random character"""
        if len(name) >= 12:
            return name
        
        pos = random.randint(0, len(name))
        char = random.choice(self.vowels + self.consonants)
        
        return name[:pos] + char + name[pos:]
    
    def _delete_random_char(self, name):
        """Delete a random character"""
        if len(name) <= 3:
            return name
        
        pos = random.randint(0, len(name) - 1)
        return name[:pos] + name[pos+1:]
    
    def _change_capitalization(self, name):
        """Change capitalization pattern"""
        patterns = [
            str.lower,
            str.upper,
            str.capitalize,
            str.title,
        ]
        
        pattern = random.choice(patterns)
        return pattern(name)
    
    def generate_themed(self, theme, count=50):
        """
        Generate names based on a specific theme
        
        Args:
            theme: Theme name (tech, nature, finance, power, etc.)
            count: Number of names to generate
            
        Returns:
            List of themed names
        """
        theme_words = {
            'tech': self.prefixes + ['tech', 'digital', 'cyber', 'net', 'web', 'data'],
            'nature': ['terra', 'sol', 'luna', 'star', 'ocean', 'forest', 'mountain'],
            'finance': ['pay', 'bank', 'trade', 'exchange', 'vault', 'treasury'],
            'power': ['titan', 'apex', 'supreme', 'prime', 'alpha', 'omega', 'ultra'],
            'animal': ['wolf', 'bear', 'lion', 'eagle', 'shark', 'dragon', 'phoenix'],
            'mythical': ['titan', 'dragon', 'phoenix', 'griffin', 'hydra', 'zeus']
        }
        
        words = theme_words.get(theme.lower(), self.roots)
        
        # Generate names using theme words
        themed_names = []
        for _ in range(count):
            base = random.choice(words)
            
            # Apply variations
            variations = [
                base,
                base + random.choice(self.suffixes),
                random.choice(self.prefixes) + base,
                base + random.choice(self.vowels) + random.choice(self.consonants),
            ]
            
            name = random.choice(variations)
            themed_names.append(self._capitalize_name(name))
        
        # Score and return
        scored = []
        for name in set(themed_names):
            score = self._score_name(name)
            scored.append({
                'name': name,
                'theme': theme,
                'score': score['total_score'],
                'details': score
            })
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:count]

