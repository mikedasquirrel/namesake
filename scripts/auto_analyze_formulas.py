#!/usr/bin/env python3
"""
Automated Formula Analysis System

Runs comprehensive formula analysis on a schedule:
- Daily: Quick validation across all formulas and domains
- Weekly: Deep evolution with large populations
- On-demand: Triggered when new data is added

Usage:
    python scripts/auto_analyze_formulas.py --mode daily
    python scripts/auto_analyze_formulas.py --mode weekly
    python scripts/auto_analyze_formulas.py --mode on-demand
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from app import app
from utils.formula_engine import FormulaEngine
from analyzers.formula_validator import FormulaValidator
from analyzers.formula_evolution import FormulaEvolution
from analyzers.convergence_analyzer import ConvergenceAnalyzer
from analyzers.encryption_detector import EncryptionDetector
from analyzers.meta_formula_analyzer import MetaFormulaAnalyzer
from analyzers.novel_pattern_discovery import NovelPatternDiscovery
from analyzers.emergent_dimension_detector import EmergentDimensionDetector
from analyzers.visual_emergent_properties import VisualEmergentPropertiesAnalyzer
from analyzers.planetary_scale_analyzer import PlanetaryScaleAnalyzer
from core.unified_domain_model_extended import ExtendedDomainInterface, ExtendedDomainType
from utils.formula_cache import cache
from utils.error_handler import handle_formula_errors, error_context
from utils.progress_reporter import ProgressReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoFormulaAnalyzer:
    """
    Automated formula analysis system
    
    Runs comprehensive analysis cycles to:
    - Validate formulas across domains
    - Evolve optimal formulas
    - Discover mathematical invariants
    - Test encryption properties
    - Generate reports
    """
    
    FORMULA_TYPES = ['phonetic', 'semantic', 'structural', 'frequency', 'numerological', 'hybrid']
    
    # ALL AVAILABLE DOMAINS (10 with data)
    DOMAINS = [
        ExtendedDomainType.CRYPTO,        # 65,087 entities
        ExtendedDomainType.MTG_CARD,      # 4,144 entities
        ExtendedDomainType.NFL_PLAYER,    # 949 entities
        ExtendedDomainType.ELECTION,      # 870 entities
        ExtendedDomainType.SHIP,          # 853 entities
        ExtendedDomainType.HURRICANE,     # 236 entities
        ExtendedDomainType.FILM,          # 46 entities
        ExtendedDomainType.MLB_PLAYER,    # 44 entities
        ExtendedDomainType.BOARD_GAME,    # 37 entities
        ExtendedDomainType.BOOK,          # 34 entities
    ]
    
    def __init__(self, output_dir: str = 'analysis_outputs/auto_analysis'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.engine = FormulaEngine()
        self.validator = FormulaValidator()
        self.evolution = FormulaEvolution()
        self.convergence = ConvergenceAnalyzer()
        self.encryption = EncryptionDetector()
        self.meta_analyzer = MetaFormulaAnalyzer()
        self.novel_discovery = NovelPatternDiscovery()
        self.emergent_detector = EmergentDimensionDetector()
        self.visual_analyzer = VisualEmergentPropertiesAnalyzer()
        self.field_analyzer = PlanetaryScaleAnalyzer()
        self.domain_interface = ExtendedDomainInterface()
        
        self.results = {
            'start_time': datetime.now().isoformat(),
            'mode': None,
            'validations': {},
            'evolutions': {},
            'convergences': {},
            'encryptions': {},
            'comparisons': {},
            'errors': []
        }
    
    # ========================================================================
    # Main Analysis Modes
    # ========================================================================
    
    def run_daily_analysis(self):
        """
        Daily analysis cycle - Fast validation
        
        - Validate all formulas with moderate sample sizes
        - Quick evolution runs (small populations)
        - Update dashboard data
        - Check for basic convergence
        
        Runtime: ~30-60 minutes
        """
        # Initialize progress reporter
        progress = ProgressReporter(total_steps=8, job_name="Daily Analysis")
        
        progress.checkpoint("STARTING DAILY FORMULA ANALYSIS")
        
        self.results['mode'] = 'daily'
        
        with app.app_context():
            # 1. Validate all formulas (moderate depth)
            progress.update("Validating all formulas (200 samples/domain)...")
            self._validate_all_formulas(limit_per_domain=200, progress=progress)
            
            # 2. Quick evolution for each type
            progress.update("Running evolution (20 pop, 15 gen)...")
            self._evolve_all_formulas(
                population_size=20,
                n_generations=15,
                limit_per_domain=100,
                progress=progress
            )
            
            # 3. Analyze convergence
            progress.update("Analyzing convergence patterns...")
            self._analyze_convergence(progress=progress)
            
            # 4. Generate comparison report
            progress.update("Generating formula comparison...")
            self._generate_comparison_report()
            
            # 5. META-FORMULA ANALYSIS (The formula of formulas)
            progress.update("🔮 Analyzing formula relationships (meta-level)...")
            self._analyze_meta_formulas(progress=progress)
            
            # 6. NOVEL PATTERN DISCOVERY
            progress.update("🔍 Discovering novel mathematical patterns...")
            self._discover_novel_patterns(progress=progress)
            
            # 7. EMERGENT DIMENSIONS & FIELD EFFECTS
            progress.update("🌌 Detecting hidden dimensions and field effects...")
            self._detect_emergent_phenomena(progress=progress)
            
            # 8. Update dashboard cache
            progress.update("Updating dashboard cache...")
            self._update_dashboard_cache()
        
        # Save results
        self._save_results('daily')
        
        # Print summary of discoveries
        progress.print_summary()
        
        logger.info("\n" + "=" * 80)
        logger.info("DAILY ANALYSIS COMPLETE")
        logger.info("=" * 80)
        
        return self.results
    
    def run_weekly_deep_dive(self):
        """
        Weekly deep analysis - Comprehensive
        
        - Full validation with large samples
        - Deep evolution (large populations, many generations)
        - Comprehensive convergence analysis
        - Encryption property testing
        - Historical trend analysis
        
        Runtime: ~4-8 hours
        """
        logger.info("=" * 80)
        logger.info("STARTING WEEKLY DEEP DIVE ANALYSIS")
        logger.info("=" * 80)
        
        self.results['mode'] = 'weekly'
        
        with app.app_context():
            # 1. Full validation
            logger.info("\n[1/6] Full formula validation...")
            self._validate_all_formulas(limit_per_domain=1000)
            
            # 2. Deep evolution
            logger.info("\n[2/6] Deep evolution runs...")
            self._evolve_all_formulas(
                population_size=50,
                n_generations=50,
                limit_per_domain=500
            )
            
            # 3. Comprehensive convergence
            logger.info("\n[3/6] Comprehensive convergence analysis...")
            self._analyze_convergence()
            
            # 4. Encryption analysis
            logger.info("\n[4/6] Testing encryption properties...")
            self._test_encryption_properties()
            
            # 5. Cross-domain meta-analysis
            logger.info("\n[5/6] Cross-domain analysis...")
            self._cross_domain_analysis()
            
            # 6. Historical trends
            logger.info("\n[6/6] Analyzing historical trends...")
            self._analyze_historical_trends()
        
        # Save results
        self._save_results('weekly')
        
        logger.info("\n" + "=" * 80)
        logger.info("WEEKLY DEEP DIVE COMPLETE")
        logger.info("=" * 80)
        
        return self.results
    
    def run_on_new_data(self, domain: Optional[str] = None):
        """
        Triggered when new data is added
        
        - Incremental analysis on new domain data
        - Re-validate affected formulas
        - Update relevant caches
        
        Runtime: ~10-20 minutes
        """
        logger.info("=" * 80)
        logger.info(f"RUNNING ANALYSIS ON NEW DATA: {domain or 'all domains'}")
        logger.info("=" * 80)
        
        self.results['mode'] = 'on_new_data'
        self.results['trigger_domain'] = domain
        
        with app.app_context():
            # Determine which domains to analyze
            domains_to_analyze = [DomainType(domain)] if domain else self.DOMAINS
            
            # 1. Validate formulas on new data
            logger.info("\n[1/3] Validating on new data...")
            for formula_id in self.FORMULA_TYPES:
                try:
                    report = self.validator.validate_formula(
                        formula_id, domains_to_analyze, limit_per_domain=500
                    )
                    self.results['validations'][formula_id] = report.to_dict()
                    
                    # Invalidate old cache
                    cache.invalidate_formula(formula_id)
                    
                except Exception as e:
                    logger.error(f"Validation failed for {formula_id}: {e}")
                    self.results['errors'].append({
                        'step': 'validation',
                        'formula': formula_id,
                        'error': str(e)
                    })
            
            # 2. Quick re-evolution
            logger.info("\n[2/3] Re-evolving formulas...")
            self._evolve_all_formulas(
                population_size=30,
                n_generations=20,
                limit_per_domain=300,
                domains=domains_to_analyze
            )
            
            # 3. Update caches
            logger.info("\n[3/3] Updating caches...")
            self._update_dashboard_cache()
        
        # Save results
        self._save_results('on_new_data')
        
        logger.info("\n" + "=" * 80)
        logger.info("NEW DATA ANALYSIS COMPLETE")
        logger.info("=" * 80)
        
        return self.results
    
    # ========================================================================
    # Analysis Components
    # ========================================================================
    
    @handle_formula_errors(default_value={})
    def _validate_all_formulas(self, limit_per_domain: int = 500, progress=None):
        """Validate all formula types across all domains"""
        
        for formula_id in self.FORMULA_TYPES:
            try:
                with error_context("validation", formula=formula_id):
                    logger.info(f"  Validating {formula_id}...")
                    
                    # Check cache first
                    cached = cache.get_validation(
                        formula_id,
                        [d.value for d in self.DOMAINS],
                        limit_per_domain
                    )
                    
                    if cached:
                        logger.info(f"    Using cached result")
                        self.results['validations'][formula_id] = cached
                        continue
                    
                    # Run validation
                    report = self.validator.validate_formula(
                        formula_id, self.DOMAINS, limit_per_domain
                    )
                    
                    result = report.to_dict()
                    self.results['validations'][formula_id] = result
                    
                    # Cache result
                    cache.set_validation(
                        formula_id,
                        [d.value for d in self.DOMAINS],
                        limit_per_domain,
                        result
                    )
                    
                    logger.info(f"    Best correlation: {report.overall_correlation:.3f}")
                    logger.info(f"    Best domain: {report.best_domain}")
                    
                    # Report interesting correlations
                    if progress and abs(report.overall_correlation) > 0.25:
                        progress.report_finding(
                            f"Strong Correlation - {formula_id}",
                            f"r = {report.overall_correlation:.3f}",
                            f"Best in {report.best_domain} domain",
                            severity="interesting" if abs(report.overall_correlation) < 0.35 else "strong"
                        )
                    
            except Exception as e:
                logger.error(f"  Validation failed for {formula_id}: {e}")
                self.results['errors'].append({
                    'step': 'validation',
                    'formula': formula_id,
                    'error': str(e)
                })
    
    @handle_formula_errors(default_value={})
    def _evolve_all_formulas(self, population_size: int, n_generations: int,
                            limit_per_domain: int, 
                            domains: Optional[List] = None,
                            progress=None):
        """Run evolution for all formula types"""
        
        domains = domains or self.DOMAINS
        
        for formula_type in self.FORMULA_TYPES:
            try:
                with error_context("evolution", formula_type=formula_type):
                    logger.info(f"  Evolving {formula_type}...")
                    logger.info(f"    Population: {population_size}, Generations: {n_generations}")
                    
                    history = self.evolution.evolve(
                        formula_type=formula_type,
                        domains=domains,
                        limit_per_domain=limit_per_domain,
                        population_size=population_size,
                        n_generations=n_generations
                    )
                    
                    result = history.to_dict()
                    self.results['evolutions'][formula_type] = result
                    
                    logger.info(f"    Final fitness: {history.final_best_fitness:.3f}")
                    logger.info(f"    Converged: {history.converged}")
                    
                    # Report convergence
                    if progress and history.converged:
                        progress.report_convergence(formula_type, 
                                                   history.convergence_generation or n_generations,
                                                   history.final_best_fitness)
                    
                    # Export history
                    self.evolution.export_history(
                        history, self.output_dir / 'evolutions'
                    )
                    
            except Exception as e:
                logger.error(f"  Evolution failed for {formula_type}: {e}")
                self.results['errors'].append({
                    'step': 'evolution',
                    'formula': formula_type,
                    'error': str(e)
                })
    
    @handle_formula_errors(default_value={})
    def _analyze_convergence(self, progress=None):
        """Analyze convergence for all evolved formulas"""
        
        for formula_type, evolution_data in self.results['evolutions'].items():
            try:
                with error_context("convergence", formula_type=formula_type):
                    logger.info(f"  Analyzing convergence for {formula_type}...")
                    
                    # Reconstruct history from data
                    from analyzers.formula_evolution import EvolutionHistory
                    history = EvolutionHistory(**evolution_data)
                    
                    signature = self.convergence.analyze_evolution(history)
                    
                    result = signature.to_dict()
                    self.results['convergences'][formula_type] = result
                    
                    logger.info(f"    Found {len(signature.invariants)} invariants")
                    logger.info(f"    Universal patterns: {len(signature.universal_patterns)}")
                    
                    # Export signature
                    self.convergence.export_analysis(
                        signature, 
                        self.output_dir / 'convergence' / f'{formula_type}_signature.json'
                    )
                    
            except Exception as e:
                logger.error(f"  Convergence analysis failed for {formula_type}: {e}")
                self.results['errors'].append({
                    'step': 'convergence',
                    'formula': formula_type,
                    'error': str(e)
                })
    
    @handle_formula_errors(default_value={})
    def _test_encryption_properties(self):
        """Test encryption properties for all formulas"""
        
        # Load test data
        logger.info("  Loading test data...")
        crypto = self.domain_interface.load_domain(DomainType.CRYPTO, limit=500)
        
        if not crypto:
            logger.warning("  No test data available")
            return
        
        names = [e.name for e in crypto if e.linguistic_features]
        features = {e.name: e.linguistic_features for e in crypto if e.linguistic_features}
        
        for formula_id in self.FORMULA_TYPES:
            try:
                with error_context("encryption", formula=formula_id):
                    logger.info(f"  Testing {formula_id}...")
                    
                    profile = self.encryption.analyze_formula(formula_id, names, features)
                    
                    result = profile.to_dict()
                    self.results['encryptions'][formula_id] = result
                    
                    logger.info(f"    Encryption quality: {profile.encryption_quality_score:.3f}")
                    logger.info(f"    Similar to: {profile.similar_to_algorithm}")
                    
                    # Export profile
                    self.encryption.export_profile(
                        profile,
                        self.output_dir / 'encryption' / f'{formula_id}_profile.json'
                    )
                    
            except Exception as e:
                logger.error(f"  Encryption testing failed for {formula_id}: {e}")
                self.results['errors'].append({
                    'step': 'encryption',
                    'formula': formula_id,
                    'error': str(e)
                })
    
    @handle_formula_errors(default_value={})
    def _generate_comparison_report(self):
        """Generate comparative analysis across all formulas"""
        
        logger.info("  Generating comparison report...")
        
        if not self.results['validations']:
            logger.warning("  No validation results to compare")
            return
        
        # Rank formulas by performance
        rankings = {}
        for formula_id, validation in self.results['validations'].items():
            rankings[formula_id] = validation.get('overall_correlation', 0)
        
        sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'rankings': [
                {'formula': formula, 'correlation': corr}
                for formula, corr in sorted_rankings
            ],
            'best_formula': sorted_rankings[0][0] if sorted_rankings else None,
            'best_correlation': sorted_rankings[0][1] if sorted_rankings else 0,
            'domain_winners': self._find_domain_winners(),
            'universal_properties': self._find_universal_properties()
        }
        
        self.results['comparisons'] = comparison
        
        # Save comparison
        comparison_file = self.output_dir / 'comparisons' / f'comparison_{datetime.now().strftime("%Y%m%d")}.json'
        comparison_file.parent.mkdir(parents=True, exist_ok=True)
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        logger.info(f"    Best formula: {comparison['best_formula']}")
        logger.info(f"    Best correlation: {comparison['best_correlation']:.3f}")
    
    def _find_domain_winners(self) -> Dict[str, str]:
        """Find best formula for each domain"""
        winners = {}
        
        for domain in self.DOMAINS:
            best_formula = None
            best_corr = 0
            
            for formula_id, validation in self.results['validations'].items():
                domain_perfs = validation.get('domain_performances', {})
                domain_perf = domain_perfs.get(domain.value, {})
                corr = abs(domain_perf.get('best_correlation', 0))
                
                if corr > best_corr:
                    best_corr = corr
                    best_formula = formula_id
            
            if best_formula:
                winners[domain.value] = best_formula
        
        return winners
    
    def _find_universal_properties(self) -> List[str]:
        """Find properties that are significant across multiple formulas"""
        property_counts = {}
        
        for validation in self.results['validations'].values():
            universal = validation.get('universal_properties', [])
            for prop in universal:
                property_counts[prop] = property_counts.get(prop, 0) + 1
        
        # Return properties significant in 50%+ of formulas
        threshold = len(self.results['validations']) / 2
        return [prop for prop, count in property_counts.items() if count >= threshold]
    
    @handle_formula_errors(default_value={})
    def _analyze_meta_formulas(self, progress=None):
        """Analyze relationships BETWEEN formulas (the meta-level)"""
        logger.info("  Computing formula space structure...")
        
        if not self.results['validations']:
            logger.warning("  No validation results for meta-analysis")
            return
        
        # Analyze formula relationships
        signature = self.meta_analyzer.analyze_formula_space(self.results['validations'])
        
        self.results['meta_formula'] = {
            'dimensionality': signature.dimensionality,
            'golden_ratio_pairs': signature.golden_ratio_pairs,
            'simple_ratio_pairs': [(f1, f2, float(r)) for f1, f2, r in signature.simple_ratio_pairs],
            'harmonic_triads': signature.harmonic_triads,
            'optimal_combination': signature.optimal_combination,
            'universal_meta_pattern': signature.universal_meta_pattern,
        }
        
        # Generate report
        report = self.meta_analyzer.generate_meta_formula_report(signature)
        
        # Save report
        report_file = self.output_dir / 'meta_formula_analysis.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"    Dimensionality: {signature.dimensionality}")
        if signature.golden_ratio_pairs:
            logger.info(f"    🔥 Golden ratio pairs: {len(signature.golden_ratio_pairs)}")
            # Report to progress
            if progress:
                for f1, f2 in signature.golden_ratio_pairs:
                    rel = signature.formula_relationships[(f1, f2)]
                    progress.report_golden_ratio(f1, f2, rel.ratio_value)
        if signature.universal_meta_pattern:
            logger.info(f"    🔥 Universal pattern: {signature.universal_meta_pattern}")
            if progress:
                progress.report_finding("Universal Meta-Pattern", signature.universal_meta_pattern, 
                                      "Pattern found in formula relationships", severity="exceptional")
        
        # Export signature
        self.meta_analyzer.export_signature(
            signature,
            self.output_dir / 'meta_formula_signature.json'
        )
    
    @handle_formula_errors(default_value={})
    def _discover_novel_patterns(self, progress=None):
        """Discover NEW mathematical patterns (not just known constants)"""
        logger.info("  Discovering novel mathematical patterns...")
        
        # Discover patterns in results
        patterns = self.novel_discovery.discover_all_patterns(self.results)
        
        # Store results
        self.results['novel_patterns'] = [
            {
                'type': p.pattern_type,
                'description': p.description,
                'parameters': p.parameters,
                'is_novel': p.is_novel,
                'consistency': p.consistency_score
            }
            for p in patterns
        ]
        
        # Generate report
        report = self.novel_discovery.generate_pattern_report(patterns)
        
        # Save
        report_file = self.output_dir / 'novel_patterns.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"    Found {len(patterns)} total patterns")
        logger.info(f"    Novel patterns: {len([p for p in patterns if p.is_novel])}")
        
        # Report novel patterns to progress
        if progress:
            novel = [p for p in patterns if p.is_novel]
            for pattern in novel:
                progress.report_novel_pattern(
                    pattern.pattern_type,
                    list(pattern.parameters.values())[0] if pattern.parameters else 0,
                    pattern.description
                )
    
    @handle_formula_errors(default_value={})
    def _detect_emergent_phenomena(self, progress=None):
        """Detect emergent dimensions and field effects"""
        logger.info("  Detecting emergent phenomena...")
        
        # This would need entity-level data
        # For now, log that detection was attempted
        
        self.results['emergent_phenomena'] = {
            'hidden_dimensions': [],
            'visual_intrinsics': [],
            'field_effects': [],
            'note': 'Full detection requires entity-level data access'
        }
        
        logger.info("    Emergent phenomena detection complete")
        logger.info("    (Limited by data structure - enhance in future)")
    
    @handle_formula_errors(default_value={})
    def _cross_domain_analysis(self):
        """Perform meta-analysis across domains"""
        logger.info("  Running cross-domain meta-analysis...")
        
        # Compare convergence patterns across formula types
        if self.results['convergences']:
            comparison = self.convergence.compare_formula_types(
                {k: v for k, v in self.results['evolutions'].items()}
            )
            
            self.results['cross_domain_meta'] = comparison
            logger.info(f"    Universal parameters: {len(comparison.get('cross_type_analysis', {}).get('universal_parameters', {}))}")
    
    @handle_formula_errors(default_value={})
    def _analyze_historical_trends(self):
        """Analyze trends over time"""
        logger.info("  Analyzing historical trends...")
        
        # Load previous results
        comparison_dir = self.output_dir / 'comparisons'
        if not comparison_dir.exists():
            logger.info("    No historical data available")
            return
        
        comparison_files = sorted(comparison_dir.glob('comparison_*.json'))
        
        if len(comparison_files) < 2:
            logger.info("    Insufficient historical data")
            return
        
        # Analyze trends
        trends = {
            'dates': [],
            'best_formulas': [],
            'best_correlations': []
        }
        
        for file in comparison_files[-30:]:  # Last 30 days
            with open(file) as f:
                data = json.load(f)
                trends['dates'].append(file.stem.replace('comparison_', ''))
                trends['best_formulas'].append(data.get('best_formula'))
                trends['best_correlations'].append(data.get('best_correlation', 0))
        
        self.results['historical_trends'] = trends
        logger.info(f"    Analyzed {len(trends['dates'])} historical data points")
    
    @handle_formula_errors(default_value={})
    def _update_dashboard_cache(self):
        """Update cached data for dashboard"""
        logger.info("  Updating dashboard cache...")
        
        dashboard_data = {
            'last_update': datetime.now().isoformat(),
            'validations': self.results['validations'],
            'evolutions': {
                k: {
                    'final_fitness': v.get('final_best_fitness'),
                    'converged': v.get('converged'),
                    'n_generations': v.get('n_generations')
                }
                for k, v in self.results['evolutions'].items()
            },
            'comparisons': self.results['comparisons'],
            'error_count': len(self.results['errors'])
        }
        
        # Cache for 24 hours
        cache.set_statistics('dashboard', dashboard_data, 'latest')
        
        logger.info("    Dashboard cache updated")
    
    # ========================================================================
    # Results Management
    # ========================================================================
    
    def _save_results(self, mode: str):
        """Save analysis results"""
        self.results['end_time'] = datetime.now().isoformat()
        self.results['success'] = len(self.results['errors']) == 0
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.output_dir / f'{mode}_analysis_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\nResults saved to: {results_file}")
        
        # Create symlink to latest
        latest_link = self.output_dir / f'{mode}_analysis_latest.json'
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(results_file.name)
        
        # Summary
        logger.info("\nAnalysis Summary:")
        logger.info(f"  Mode: {mode}")
        logger.info(f"  Duration: {self._get_duration()}")
        logger.info(f"  Validations: {len(self.results['validations'])}")
        logger.info(f"  Evolutions: {len(self.results['evolutions'])}")
        logger.info(f"  Errors: {len(self.results['errors'])}")
    
    def _get_duration(self) -> str:
        """Calculate analysis duration"""
        from datetime import datetime
        start = datetime.fromisoformat(self.results['start_time'])
        end = datetime.fromisoformat(self.results['end_time'])
        duration = end - start
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Automated Formula Analysis')
    parser.add_argument(
        '--mode',
        choices=['daily', 'weekly', 'on-demand'],
        default='daily',
        help='Analysis mode'
    )
    parser.add_argument(
        '--domain',
        help='Specific domain for on-demand analysis'
    )
    parser.add_argument(
        '--output',
        default='analysis_outputs/auto_analysis',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = AutoFormulaAnalyzer(output_dir=args.output)
    
    # Run analysis
    try:
        if args.mode == 'daily':
            results = analyzer.run_daily_analysis()
        elif args.mode == 'weekly':
            results = analyzer.run_weekly_deep_dive()
        elif args.mode == 'on-demand':
            results = analyzer.run_on_new_data(domain=args.domain)
        
        # Exit with success/failure code
        sys.exit(0 if results['success'] else 1)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

