"""Domain Analysis Template - Abstract Base Class for All Domain Analyses

Provides standardized pipeline, progress tracking, and quality control for nominative
determinism research across all domains.

All domain analyses inherit from this template to ensure:
- Consistent methodology and statistical rigor
- Automatic progress tracking with ETA
- Standard validation and quality checks
- Automatic page data updates
- Comprehensive error handling and logging

Author: Michael Smerconish
Date: November 2025
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
import json
import time
import traceback
import numpy as np
from scipy import stats
from pathlib import Path

from core.research_framework import FRAMEWORK
from core.models import db, PreComputedStats
from utils.progress_tracker import ProgressTracker, MultiTaskProgressTracker


class DomainAnalysisTemplate(ABC):
    """
    Abstract base class for domain-specific analyses.
    
    Provides complete pipeline with automatic:
    - Research framework inheritance
    - Progress tracking and logging
    - Statistical validation
    - Results storage
    - Page data updates
    
    Subclasses must implement:
    - collect_data(): Domain-specific data collection
    - analyze_data(): Domain-specific analysis
    - get_collector_class(): Return collector class
    - get_analyzer_class(): Return analyzer class (optional)
    """
    
    def __init__(self, domain_id: str, mode: str = 'new', 
                 custom_params: Optional[Dict] = None):
        """
        Initialize domain analysis.
        
        Args:
            domain_id: Domain identifier from research framework
            mode: 'new' (fresh collection), 'reanalyze' (use existing data), 
                  'update' (incremental)
            custom_params: Optional custom parameters for the analysis
        """
        self.domain_id = domain_id
        self.mode = mode
        self.custom_params = custom_params or {}
        
        # Load framework and domain metadata
        self.framework = FRAMEWORK
        self.domain_meta = self.framework.get_domain(domain_id)
        
        if not self.domain_meta:
            raise ValueError(f"Unknown domain: {domain_id}")
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize tracking
        self.start_time = time.time()
        self.results = {}
        self.errors = []
        self.warnings = []
        
        # Stats
        self.collection_stats = {}
        self.analysis_stats = {}
        self.validation_stats = {}
        
        self.logger.info("="*80)
        self.logger.info(f"DOMAIN ANALYSIS: {self.domain_meta.display_name}")
        self.logger.info("="*80)
        self.logger.info(f"Domain ID: {domain_id}")
        self.logger.info(f"Mode: {mode}")
        self.logger.info(f"Research Questions: {len(self.domain_meta.research_questions)}")
        for i, q in enumerate(self.domain_meta.research_questions, 1):
            self.logger.info(f"  {i}. {q}")
        self.logger.info(f"Target Sample Size: {self.domain_meta.sample_size_target:,}")
        self.logger.info("="*80 + "\n")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup domain-specific logging"""
        logger = logging.getLogger(f"domain_analysis.{self.domain_id}")
        
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # File handler
            log_file = f"{self.domain_id}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.INFO)
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            
            logger.addHandler(fh)
            logger.addHandler(ch)
        
        return logger
    
    @abstractmethod
    def collect_data(self, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
        """
        Collect domain-specific data.
        
        Args:
            progress_tracker: Optional progress tracker for updates
        
        Returns:
            Dictionary with collected data and metadata
        """
        pass
    
    @abstractmethod
    def analyze_data(self, data: Dict, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
        """
        Analyze domain-specific data.
        
        Args:
            data: Collected data from collect_data()
            progress_tracker: Optional progress tracker for updates
        
        Returns:
            Dictionary with analysis results
        """
        pass
    
    @abstractmethod
    def get_collector_class(self):
        """Return the collector class for this domain"""
        pass
    
    def get_analyzer_class(self):
        """Return the analyzer class for this domain (optional)"""
        return None
    
    def run_full_pipeline(self) -> Dict:
        """
        Execute complete analysis pipeline with progress tracking.
        
        Pipeline steps:
        1. Data collection (or load existing)
        2. Data analysis
        3. Results validation
        4. Findings generation
        5. Page data update
        
        Returns:
            Complete results dictionary
        """
        pipeline_tracker = MultiTaskProgressTracker(
            task_names=[
                "Data Collection",
                "Data Analysis", 
                "Validation",
                "Findings Generation",
                "Page Update"
            ],
            task_weights=[0.3, 0.4, 0.1, 0.1, 0.1]
        )
        
        try:
            # Step 1: Data Collection
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 1: DATA COLLECTION")
            self.logger.info("="*80)
            
            if self.mode == 'reanalyze':
                self.logger.info("Mode: REANALYZE - Loading existing data from database")
                collection_result = self._load_existing_data()
            else:
                self.logger.info(f"Mode: {self.mode.upper()} - Collecting fresh data")
                collection_result = self.collect_data()
            
            self.collection_stats = collection_result
            pipeline_tracker.update_task(0, 100, f"Collected {collection_result.get('sample_size', 0)} records")
            
            # Step 2: Data Analysis
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 2: DATA ANALYSIS")
            self.logger.info("="*80)
            
            analysis_result = self.analyze_data(collection_result)
            self.analysis_stats = analysis_result
            pipeline_tracker.update_task(1, 100, "Analysis complete")
            
            # Step 3: Validation
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 3: RESULTS VALIDATION")
            self.logger.info("="*80)
            
            validation_result = self._validate_results(analysis_result)
            self.validation_stats = validation_result
            pipeline_tracker.update_task(2, 100, f"Validation: {validation_result.get('status', 'unknown')}")
            
            # Step 4: Generate Findings
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 4: FINDINGS GENERATION")
            self.logger.info("="*80)
            
            findings = self._generate_findings(analysis_result, validation_result)
            pipeline_tracker.update_task(3, 100, "Findings generated")
            
            # Step 5: Update Page Data
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 5: PAGE DATA UPDATE")
            self.logger.info("="*80)
            
            self._update_page_data(findings, analysis_result)
            pipeline_tracker.update_task(4, 100, "Page data updated")
            
            # Complete
            pipeline_tracker.complete()
            
            # Compile final results
            self.results = {
                'domain_id': self.domain_id,
                'domain_name': self.domain_meta.display_name,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat(),
                'elapsed_time': time.time() - self.start_time,
                'collection': self.collection_stats,
                'analysis': self.analysis_stats,
                'validation': self.validation_stats,
                'findings': findings,
                'errors': self.errors,
                'warnings': self.warnings
            }
            
            self._print_summary()
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.logger.error(traceback.format_exc())
            self.errors.append(str(e))
            
            return {
                'domain_id': self.domain_id,
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'errors': self.errors,
                'warnings': self.warnings
            }
    
    def _load_existing_data(self) -> Dict:
        """Load existing data from database for reanalysis"""
        self.logger.info("Loading existing data from database...")
        
        # Subclasses can override this, but here's a default implementation
        # that returns basic stats
        return {
            'mode': 'reanalysis',
            'sample_size': 0,
            'data_source': 'database',
            'note': 'Subclass should override _load_existing_data() for specific loading logic'
        }
    
    def _validate_results(self, results: Dict) -> Dict:
        """
        Validate analysis results against quality standards.
        
        Checks:
        - Sample size adequacy
        - Effect size reporting
        - Statistical significance
        - Publication readiness
        
        Args:
            results: Analysis results dictionary
        
        Returns:
            Validation results with issues/warnings
        """
        self.logger.info("Validating results against quality standards...")
        
        validation = {
            'timestamp': datetime.now().isoformat(),
            'checks_performed': [],
            'issues': [],
            'warnings': [],
            'passed': True
        }
        
        # Check 1: Sample size
        sample_size = results.get('sample_size', 0)
        target_size = self.domain_meta.sample_size_target
        
        validation['checks_performed'].append('sample_size')
        if sample_size < target_size:
            msg = f"Sample size {sample_size} below target {target_size}"
            validation['warnings'].append(msg)
            self.logger.warning(msg)
        else:
            self.logger.info(f"✓ Sample size adequate: {sample_size:,} (target: {target_size:,})")
        
        # Check 2: Effect sizes reported
        validation['checks_performed'].append('effect_sizes')
        has_effect_sizes = any(
            'effect_size' in str(key).lower() or 'cohens_d' in str(key).lower() or 'r_squared' in str(key).lower()
            for key in results.keys()
        )
        
        if not has_effect_sizes:
            msg = "No effect sizes found in results"
            validation['warnings'].append(msg)
            self.logger.warning(msg)
        else:
            self.logger.info("✓ Effect sizes reported")
        
        # Check 3: Statistical tests
        validation['checks_performed'].append('statistical_tests')
        has_stats = any(
            'p_value' in str(key).lower() or 'correlation' in str(key).lower() or 'regression' in str(key).lower()
            for key in results.keys()
        )
        
        if not has_stats:
            msg = "No statistical tests found in results"
            validation['issues'].append(msg)
            validation['passed'] = False
            self.logger.error(msg)
        else:
            self.logger.info("✓ Statistical tests performed")
        
        # Check 4: Publication readiness
        validation['checks_performed'].append('publication_readiness')
        pub_ready, pub_issues = self.framework.check_publication_readiness(
            domain_id=self.domain_id,
            sample_size=sample_size,
            has_out_of_sample=results.get('has_out_of_sample_validation', False),
            has_effect_sizes=has_effect_sizes,
            has_null_results=results.get('has_null_results', False)
        )
        
        if not pub_ready:
            validation['warnings'].extend(pub_issues)
            for issue in pub_issues:
                self.logger.warning(f"Publication readiness: {issue}")
        else:
            self.logger.info("✓ Publication quality standards met")
        
        # Summary
        validation['status'] = 'passed' if validation['passed'] else 'failed'
        validation['num_issues'] = len(validation['issues'])
        validation['num_warnings'] = len(validation['warnings'])
        
        self.logger.info(f"\nValidation Summary:")
        self.logger.info(f"  Status: {validation['status'].upper()}")
        self.logger.info(f"  Checks: {len(validation['checks_performed'])}")
        self.logger.info(f"  Issues: {validation['num_issues']}")
        self.logger.info(f"  Warnings: {validation['num_warnings']}")
        
        return validation
    
    def _generate_findings(self, analysis: Dict, validation: Dict) -> str:
        """
        Generate standardized findings summary.
        
        Args:
            analysis: Analysis results
            validation: Validation results
        
        Returns:
            Formatted findings text
        """
        self.logger.info("Generating findings summary...")
        
        findings = []
        findings.append("=" * 80)
        findings.append(f"{self.domain_meta.display_name} - Key Findings")
        findings.append("=" * 80)
        findings.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        findings.append(f"Domain: {self.domain_id}")
        findings.append(f"Mode: {self.mode}")
        
        # Research questions
        findings.append("\n" + "-" * 80)
        findings.append("Research Questions")
        findings.append("-" * 80)
        for i, q in enumerate(self.domain_meta.research_questions, 1):
            findings.append(f"{i}. {q}")
        
        # Sample
        findings.append("\n" + "-" * 80)
        findings.append("Sample")
        findings.append("-" * 80)
        findings.append(f"N = {analysis.get('sample_size', 'N/A'):,}")
        findings.append(f"Target = {self.domain_meta.sample_size_target:,}")
        
        # Key results (subclass can enhance this)
        findings.append("\n" + "-" * 80)
        findings.append("Key Results")
        findings.append("-" * 80)
        findings.append("See detailed analysis results in database and web interface.")
        
        # Validation
        findings.append("\n" + "-" * 80)
        findings.append("Quality Validation")
        findings.append("-" * 80)
        findings.append(f"Status: {validation.get('status', 'unknown').upper()}")
        findings.append(f"Checks Performed: {len(validation.get('checks_performed', []))}")
        findings.append(f"Issues: {validation.get('num_issues', 0)}")
        findings.append(f"Warnings: {validation.get('num_warnings', 0)}")
        
        # Theoretical framework
        findings.append("\n" + "-" * 80)
        findings.append("Theoretical Framework")
        findings.append("-" * 80)
        findings.append("This analysis follows the comprehensive nominative determinism")
        findings.append("research framework with:")
        findings.append(f"  - {len(self.framework.theory.universal_principles)} Universal Principles")
        findings.append(f"  - {len(self.framework.theory.universal_laws)} Universal Laws")
        findings.append(f"  - {len(self.framework.statistics.standard_methods)} Statistical Methods")
        findings.append("  - Boundary Conditions Framework")
        
        findings.append("\n" + "=" * 80)
        
        findings_text = "\n".join(findings)
        self.logger.info("Findings summary generated")
        
        return findings_text
    
    def _update_page_data(self, findings: str, analysis: Dict):
        """
        Update PreComputedStats for instant page loads.
        
        Args:
            findings: Generated findings text
            analysis: Full analysis results
        """
        self.logger.info("Updating page data in database...")
        
        try:
            # Mark old results as not current
            PreComputedStats.query.filter_by(
                stat_type=f"{self.domain_id}_findings",
                is_current=True
            ).update({'is_current': False})
            
            # Store new findings
            findings_stat = PreComputedStats(
                stat_type=f"{self.domain_id}_findings",
                data_json=json.dumps({
                    'findings_text': findings,
                    'analysis_summary': {
                        'sample_size': analysis.get('sample_size', 0),
                        'timestamp': datetime.now().isoformat(),
                        'mode': self.mode
                    }
                }),
                sample_size=analysis.get('sample_size', 0),
                computed_at=datetime.utcnow(),
                computation_duration=time.time() - self.start_time,
                is_current=True
            )
            
            db.session.add(findings_stat)
            
            # Store full analysis results
            analysis_stat = PreComputedStats(
                stat_type=f"{self.domain_id}_analysis",
                data_json=json.dumps(analysis),
                sample_size=analysis.get('sample_size', 0),
                computed_at=datetime.utcnow(),
                computation_duration=time.time() - self.start_time,
                is_current=True
            )
            
            db.session.add(analysis_stat)
            db.session.commit()
            
            self.logger.info("✓ Page data updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating page data: {e}")
            db.session.rollback()
            self.errors.append(f"Page data update failed: {e}")
    
    def _print_summary(self):
        """Print final summary"""
        elapsed = time.time() - self.start_time
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("ANALYSIS COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Domain: {self.domain_meta.display_name}")
        self.logger.info(f"Mode: {self.mode}")
        self.logger.info(f"Sample Size: {self.analysis_stats.get('sample_size', 'N/A'):,}")
        self.logger.info(f"Total Time: {elapsed/60:.1f} minutes")
        self.logger.info(f"Errors: {len(self.errors)}")
        self.logger.info(f"Warnings: {len(self.warnings)}")
        
        if self.validation_stats.get('status') == 'passed':
            self.logger.info("✓ Quality validation: PASSED")
        else:
            self.logger.info("✗ Quality validation: FAILED")
        
        self.logger.info("=" * 80 + "\n")
    
    # Utility methods for statistical analysis
    
    def calculate_correlation(self, x: List[float], y: List[float], 
                            method: str = 'pearson') -> Tuple[float, float]:
        """
        Calculate correlation with p-value.
        
        Args:
            x: First variable
            y: Second variable
            method: 'pearson', 'spearman', or 'kendall'
        
        Returns:
            (correlation, p_value)
        """
        x_clean = np.array([v for v in x if not np.isnan(v)])
        y_clean = np.array([v for v in y if not np.isnan(v)])
        
        if len(x_clean) != len(y_clean) or len(x_clean) < 3:
            return np.nan, np.nan
        
        if method == 'pearson':
            return stats.pearsonr(x_clean, y_clean)
        elif method == 'spearman':
            return stats.spearmanr(x_clean, y_clean)
        elif method == 'kendall':
            return stats.kendalltau(x_clean, y_clean)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def calculate_effect_size_cohens_d(self, group1: List[float], group2: List[float]) -> float:
        """
        Calculate Cohen's d effect size.
        
        Args:
            group1: First group values
            group2: Second group values
        
        Returns:
            Cohen's d
        """
        g1 = np.array([v for v in group1 if not np.isnan(v)])
        g2 = np.array([v for v in group2 if not np.isnan(v)])
        
        if len(g1) < 2 or len(g2) < 2:
            return np.nan
        
        mean1, mean2 = np.mean(g1), np.mean(g2)
        std1, std2 = np.std(g1, ddof=1), np.std(g2, ddof=1)
        
        # Pooled standard deviation
        n1, n2 = len(g1), len(g2)
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return np.nan
        
        return (mean1 - mean2) / pooled_std
    
    def interpret_effect_size(self, value: float, metric_type: str = 'correlation') -> str:
        """
        Interpret effect size using framework standards.
        
        Args:
            value: Effect size value
            metric_type: 'correlation', 'cohens_d', or 'r_squared'
        
        Returns:
            Interpretation string
        """
        return self.framework.interpret_effect_size(value, metric_type)
    
    def apply_bonferroni_correction(self, p_values: List[float]) -> List[bool]:
        """
        Apply Bonferroni correction for multiple comparisons.
        
        Args:
            p_values: List of p-values
        
        Returns:
            List of booleans indicating significance after correction
        """
        alpha = self.framework.statistics.bonferroni_alpha
        corrected_alpha = alpha / len(p_values)
        return [p < corrected_alpha for p in p_values]

