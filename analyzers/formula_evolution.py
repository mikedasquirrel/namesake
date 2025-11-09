"""
Formula Evolution - Genetic Algorithm for Formula Optimization

Uses evolutionary algorithms to discover optimal transformation formulas:
1. Generate population of random formulas
2. Test fitness (predictive power across domains)
3. Select best performers
4. Breed and mutate to create next generation
5. Repeat until convergence

This discovers: What mathematical structure best captures nominative determinism?
"""

import numpy as np
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import logging
import json
from datetime import datetime
from pathlib import Path

from utils.formula_engine import (
    FormulaEngine, FormulaBase, PhoneticFormula, SemanticFormula,
    StructuralFormula, FrequencyFormula, NumerologicalFormula, HybridFormula
)
from analyzers.formula_validator import FormulaValidator, CrossDomainReport
from core.unified_domain_model import DomainType

logger = logging.getLogger(__name__)


@dataclass
class Individual:
    """An individual in the evolutionary population"""
    formula: FormulaBase
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'formula_id': self.formula.formula_id,
            'weights': self.formula.get_weights(),
            'fitness': self.fitness,
            'generation': self.generation,
            'parent_ids': self.parent_ids,
        }


@dataclass
class Generation:
    """A generation in the evolutionary process"""
    generation_number: int
    individuals: List[Individual] = field(default_factory=list)
    best_fitness: float = 0.0
    mean_fitness: float = 0.0
    fitness_std: float = 0.0
    best_individual: Optional[Individual] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'generation_number': self.generation_number,
            'population_size': len(self.individuals),
            'best_fitness': self.best_fitness,
            'mean_fitness': self.mean_fitness,
            'fitness_std': self.fitness_std,
            'best_individual': self.best_individual.to_dict() if self.best_individual else None,
        }


@dataclass
class EvolutionHistory:
    """Complete history of evolutionary run"""
    formula_type: str
    population_size: int
    n_generations: int
    mutation_rate: float
    
    generations: List[Generation] = field(default_factory=list)
    
    # Convergence metrics
    converged: bool = False
    convergence_generation: Optional[int] = None
    final_best_fitness: float = 0.0
    
    # Best formula discovered
    best_formula: Optional[Dict] = None
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['generations'] = [g.to_dict() for g in self.generations]
        return result


class FormulaEvolution:
    """
    Genetic algorithm for evolving optimal transformation formulas
    """
    
    def __init__(self, validator: Optional[FormulaValidator] = None):
        self.validator = validator or FormulaValidator()
        self.formula_engine = FormulaEngine()
        
        # Evolution parameters
        self.population_size = 50
        self.n_generations = 50
        self.mutation_rate = 0.1
        self.elite_size = 5  # Top N kept unchanged
        self.tournament_size = 3
        
        # Convergence criteria
        self.convergence_threshold = 0.001  # Stop if fitness change < this for 5 generations
        self.convergence_patience = 5
    
    def evolve(self, formula_type: str = "hybrid",
              domains: Optional[List[DomainType]] = None,
              limit_per_domain: Optional[int] = 100,
              population_size: Optional[int] = None,
              n_generations: Optional[int] = None) -> EvolutionHistory:
        """
        Run evolutionary algorithm to discover optimal formula
        
        Args:
            formula_type: Base type of formulas to evolve
            domains: Which domains to test on
            limit_per_domain: Max entities per domain for testing
            population_size: Population size (overrides default)
            n_generations: Number of generations (overrides default)
            
        Returns:
            EvolutionHistory with complete evolutionary trajectory
        """
        if population_size:
            self.population_size = population_size
        if n_generations:
            self.n_generations = n_generations
        
        if domains is None:
            domains = list(DomainType)
        
        logger.info(f"Starting evolution of {formula_type} formulas")
        logger.info(f"Population: {self.population_size}, Generations: {self.n_generations}")
        logger.info(f"Testing on domains: {[d.value if hasattr(d, 'value') else d for d in domains]}")
        
        history = EvolutionHistory(
            formula_type=formula_type,
            population_size=self.population_size,
            n_generations=self.n_generations,
            mutation_rate=self.mutation_rate
        )
        
        # Initialize population
        population = self._initialize_population(formula_type)
        
        # Track convergence
        no_improvement_count = 0
        last_best_fitness = 0.0
        
        # Evolution loop
        for gen in range(self.n_generations):
            logger.info(f"\n{'='*60}")
            logger.info(f"Generation {gen + 1}/{self.n_generations}")
            logger.info(f"{'='*60}")
            
            # Evaluate fitness
            self._evaluate_population(population, domains, limit_per_domain)
            
            # Create generation record
            generation = self._record_generation(population, gen)
            history.generations.append(generation)
            
            logger.info(f"Best Fitness: {generation.best_fitness:.4f}")
            logger.info(f"Mean Fitness: {generation.mean_fitness:.4f}")
            logger.info(f"Std Fitness: {generation.fitness_std:.4f}")
            
            # Check for convergence
            fitness_improvement = generation.best_fitness - last_best_fitness
            
            if fitness_improvement < self.convergence_threshold:
                no_improvement_count += 1
                logger.info(f"No significant improvement ({no_improvement_count}/{self.convergence_patience})")
            else:
                no_improvement_count = 0
            
            if no_improvement_count >= self.convergence_patience:
                logger.info(f"Converged at generation {gen + 1}")
                history.converged = True
                history.convergence_generation = gen + 1
                break
            
            last_best_fitness = generation.best_fitness
            
            # Create next generation
            if gen < self.n_generations - 1:
                population = self._create_next_generation(population, gen + 1)
        
        # Record final results
        final_gen = history.generations[-1]
        history.final_best_fitness = final_gen.best_fitness
        
        if final_gen.best_individual:
            history.best_formula = final_gen.best_individual.to_dict()
        
        logger.info(f"\n{'='*60}")
        logger.info("Evolution Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Final Best Fitness: {history.final_best_fitness:.4f}")
        logger.info(f"Converged: {history.converged}")
        
        return history
    
    def _initialize_population(self, formula_type: str) -> List[Individual]:
        """Create initial random population"""
        logger.info(f"Initializing population of {self.population_size} {formula_type} formulas")
        
        population = []
        
        for i in range(self.population_size):
            formula = self.formula_engine.create_random_formula(formula_type)
            individual = Individual(formula=formula, generation=0)
            population.append(individual)
        
        return population
    
    def _evaluate_population(self, population: List[Individual],
                            domains: List[DomainType],
                            limit_per_domain: Optional[int]):
        """Evaluate fitness of all individuals"""
        logger.info("Evaluating population fitness...")
        
        for i, individual in enumerate(population):
            if i % 10 == 0:
                logger.info(f"  Evaluating individual {i + 1}/{len(population)}")
            
            fitness = self._calculate_fitness(
                individual.formula,
                domains,
                limit_per_domain
            )
            individual.fitness = fitness
    
    def _calculate_fitness(self, formula: FormulaBase,
                          domains: List[DomainType],
                          limit_per_domain: Optional[int]) -> float:
        """
        Calculate fitness score for a formula
        
        Fitness = weighted combination of:
        - Correlation strength (70%)
        - Cross-domain consistency (20%)
        - Simplicity (10% - penalize overly complex formulas)
        """
        # Register formula temporarily
        self.formula_engine.register_formula(formula)
        
        try:
            # Validate formula
            report = self.validator.validate_formula(
                formula.formula_id,
                domains=domains,
                limit_per_domain=limit_per_domain
            )
            
            # Fitness components
            correlation_score = report.overall_correlation
            consistency_score = report.consistency_score
            
            # Simplicity score: penalize extreme weight values
            weights = formula.get_weights()
            weight_values = list(weights.values())
            
            if weight_values:
                # Prefer weights close to 1.0
                weight_deviation = np.mean([abs(w - 1.0) for w in weight_values])
                simplicity_score = max(0, 1.0 - weight_deviation / 2.0)
            else:
                simplicity_score = 1.0
            
            # Combined fitness
            fitness = (
                correlation_score * 0.70 +
                consistency_score * 0.20 +
                simplicity_score * 0.10
            )
            
            return fitness
            
        except Exception as e:
            logger.error(f"Error calculating fitness: {e}")
            return 0.0
    
    def _record_generation(self, population: List[Individual],
                          gen_number: int) -> Generation:
        """Record statistics for a generation"""
        fitnesses = [ind.fitness for ind in population]
        
        best_individual = max(population, key=lambda x: x.fitness)
        
        generation = Generation(
            generation_number=gen_number,
            individuals=population.copy(),
            best_fitness=best_individual.fitness,
            mean_fitness=float(np.mean(fitnesses)),
            fitness_std=float(np.std(fitnesses)),
            best_individual=best_individual
        )
        
        return generation
    
    def _create_next_generation(self, population: List[Individual],
                               gen_number: int) -> List[Individual]:
        """Create next generation through selection, crossover, and mutation"""
        next_generation = []
        
        # Elitism: Keep top performers
        sorted_pop = sorted(population, key=lambda x: x.fitness, reverse=True)
        elite = sorted_pop[:self.elite_size]
        
        for ind in elite:
            next_generation.append(Individual(
                formula=ind.formula,
                fitness=ind.fitness,
                generation=gen_number,
                parent_ids=[ind.formula.formula_id]
            ))
        
        logger.info(f"Kept {self.elite_size} elite individuals")
        
        # Fill rest through tournament selection and breeding
        while len(next_generation) < self.population_size:
            # Select parents
            parent1 = self._tournament_selection(population)
            parent2 = self._tournament_selection(population)
            
            # Crossover
            try:
                child_formula = FormulaBase.crossover(parent1.formula, parent2.formula)
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child_formula = child_formula.mutate(self.mutation_rate)
                
                child = Individual(
                    formula=child_formula,
                    generation=gen_number,
                    parent_ids=[parent1.formula.formula_id, parent2.formula.formula_id]
                )
                
                next_generation.append(child)
                
            except Exception as e:
                logger.error(f"Error in breeding: {e}")
                # Add random individual instead
                formula_type = type(parent1.formula).__name__.replace('Formula', '').lower()
                random_formula = self.formula_engine.create_random_formula(formula_type)
                child = Individual(formula=random_formula, generation=gen_number)
                next_generation.append(child)
        
        return next_generation
    
    def _tournament_selection(self, population: List[Individual]) -> Individual:
        """Select individual using tournament selection"""
        tournament = random.sample(population, min(self.tournament_size, len(population)))
        winner = max(tournament, key=lambda x: x.fitness)
        return winner
    
    def export_history(self, history: EvolutionHistory, output_dir: str):
        """Export evolution history to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export full history as JSON
        history_file = output_path / f"evolution_history_{history.timestamp[:19].replace(':', '-')}.json"
        with open(history_file, 'w') as f:
            json.dump(history.to_dict(), f, indent=2)
        
        logger.info(f"Evolution history saved to {history_file}")
        
        # Export best formula
        if history.best_formula:
            best_file = output_path / f"best_formula_{history.formula_type}.json"
            with open(best_file, 'w') as f:
                json.dump(history.best_formula, f, indent=2)
            
            logger.info(f"Best formula saved to {best_file}")
        
        # Export generation summary CSV
        summary_file = output_path / f"evolution_summary_{history.formula_type}.csv"
        with open(summary_file, 'w') as f:
            f.write("generation,best_fitness,mean_fitness,std_fitness\n")
            for gen in history.generations:
                f.write(f"{gen.generation_number},{gen.best_fitness},{gen.mean_fitness},{gen.fitness_std}\n")
        
        logger.info(f"Generation summary saved to {summary_file}")
    
    def compare_formula_types(self, 
                             formula_types: Optional[List[str]] = None,
                             domains: Optional[List[DomainType]] = None,
                             limit_per_domain: int = 100,
                             n_generations: int = 30,
                             population_size: int = 30) -> Dict[str, EvolutionHistory]:
        """
        Evolve multiple formula types and compare results
        
        Returns:
            Dictionary mapping formula_type to EvolutionHistory
        """
        if formula_types is None:
            formula_types = ['phonetic', 'semantic', 'structural', 'frequency', 'numerological', 'hybrid']
        
        results = {}
        
        for formula_type in formula_types:
            logger.info(f"\n{'#'*80}")
            logger.info(f"EVOLVING {formula_type.upper()} FORMULAS")
            logger.info(f"{'#'*80}\n")
            
            history = self.evolve(
                formula_type=formula_type,
                domains=domains,
                limit_per_domain=limit_per_domain,
                n_generations=n_generations,
                population_size=population_size
            )
            
            results[formula_type] = history
        
        # Generate comparison report
        self._generate_comparison_report(results)
        
        return results
    
    def _generate_comparison_report(self, results: Dict[str, EvolutionHistory]):
        """Generate report comparing evolved formula types"""
        logger.info(f"\n{'='*80}")
        logger.info("FORMULA TYPE COMPARISON")
        logger.info(f"{'='*80}\n")
        
        # Rank by final fitness
        rankings = sorted(results.items(), key=lambda x: x[1].final_best_fitness, reverse=True)
        
        for i, (formula_type, history) in enumerate(rankings, 1):
            logger.info(f"{i}. {formula_type.upper()}")
            logger.info(f"   Final Best Fitness: {history.final_best_fitness:.4f}")
            logger.info(f"   Converged: {history.converged}")
            if history.converged:
                logger.info(f"   Convergence Generation: {history.convergence_generation}")
            logger.info("")

