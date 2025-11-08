#!/usr/bin/env python3
"""Unified Domain Analysis Runner

Command-line interface for running any domain analysis with standardized pipeline.

Usage:
    # Run single domain analysis
    python scripts/run_domain_analysis.py --domain nfl --mode new --sample-size 1000
    
    # Re-analyze existing domain
    python scripts/run_domain_analysis.py --domain immigration --mode reanalyze
    
    # Run multiple domains sequentially
    python scripts/run_domain_analysis.py --domains nfl,nba,immigration --mode update
    
    # Run with custom parameters
    python scripts/run_domain_analysis.py --domain nfl --mode new --custom-params '{"positions": ["QB", "RB"]}'

Author: Michael Smerconish
Date: November 2025
"""

import sys
import os
import argparse
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.research_framework import FRAMEWORK
from core.domain_analysis_template import DomainAnalysisTemplate
from utils.progress_tracker import ProgressTracker


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_domain_config(domain_id: str) -> Dict:
    """
    Load domain configuration from YAML file.
    
    Args:
        domain_id: Domain identifier (e.g., 'nfl', 'nba')
    
    Returns:
        Domain configuration dictionary
    """
    config_file = Path(__file__).parent.parent / "core" / "domain_configs" / f"{domain_id}.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"Loaded configuration for domain: {config['display_name']}")
    return config


def create_domain_analyzer(domain_id: str, mode: str, custom_params: Optional[Dict] = None):
    """
    Create domain analyzer instance dynamically.
    
    Args:
        domain_id: Domain identifier
        mode: Analysis mode ('new', 'reanalyze', 'update')
        custom_params: Optional custom parameters
    
    Returns:
        Domain analyzer instance
    """
    # Load config
    config = load_domain_config(domain_id)
    
    # Get collector and analyzer classes
    collector_module, collector_class = config['collector_class'].rsplit('.', 1)
    
    # Import collector
    try:
        collector_mod = __import__(collector_module, fromlist=[collector_class])
        collector_cls = getattr(collector_mod, collector_class)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import collector {config['collector_class']}: {e}")
    
    # Import analyzer if specified
    analyzer_cls = None
    if 'analyzer_class' in config:
        try:
            analyzer_module, analyzer_class_name = config['analyzer_class'].rsplit('.', 1)
            analyzer_mod = __import__(analyzer_module, fromlist=[analyzer_class_name])
            analyzer_cls = getattr(analyzer_mod, analyzer_class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to import analyzer {config['analyzer_class']}: {e}")
    
    # Create concrete analyzer class
    class ConcreteDomainAnalyzer(DomainAnalysisTemplate):
        """Concrete implementation for this domain"""
        
        def __init__(self):
            super().__init__(domain_id, mode, custom_params)
            self.config = config
            self.collector = None
            self.analyzer = None
        
        def get_collector_class(self):
            return collector_cls
        
        def get_analyzer_class(self):
            return analyzer_cls
        
        def collect_data(self, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
            """Collect domain-specific data"""
            self.logger.info(f"Initializing {collector_class}...")
            
            # Initialize collector
            collector_params = self.config.get('collector_params', {})
            collector_params.update(custom_params or {})
            
            self.collector = collector_cls()
            
            # Determine collection strategy
            if mode == 'new':
                self.logger.info("Mode: NEW - Fresh data collection")
                target_size = custom_params.get('sample_size', config['target_sample_size'])
                
                if config.get('stratification', {}).get('enabled'):
                    self.logger.info("Using stratified sampling strategy")
                    strat_field = config['stratification']['field']
                    strat_targets = config['stratification']['targets']
                    
                    self.logger.info(f"Stratification: {strat_field}")
                    for key, target in strat_targets.items():
                        self.logger.info(f"  {key}: {target} samples")
                    
                    # Call stratified collection if available
                    if hasattr(self.collector, 'collect_stratified_sample'):
                        result = self.collector.collect_stratified_sample(
                            target_per_role=strat_targets
                        )
                    else:
                        self.logger.warning("Stratified method not available, using standard collection")
                        result = self.collector.collect_sample(target_size)
                else:
                    result = self.collector.collect_sample(target_size)
            
            elif mode == 'update':
                self.logger.info("Mode: UPDATE - Incremental data collection")
                if hasattr(self.collector, 'collect_updates'):
                    result = self.collector.collect_updates()
                else:
                    self.logger.warning("Update method not available, using full collection")
                    result = self.collector.collect_sample(config['target_sample_size'])
            
            else:  # reanalyze
                self.logger.info("Mode: REANALYZE - Using existing data")
                result = self._load_existing_data()
            
            return {
                'mode': mode,
                'sample_size': result.get('total_collected', 0) or result.get('total_analyzed', 0),
                'collection_stats': result,
                'timestamp': datetime.now().isoformat()
            }
        
        def analyze_data(self, data: Dict, progress_tracker: Optional[ProgressTracker] = None) -> Dict:
            """Analyze domain-specific data"""
            self.logger.info(f"Starting {domain_id} analysis...")
            
            if analyzer_cls:
                self.logger.info(f"Initializing {analyzer_class_name}...")
                self.analyzer = analyzer_cls()
                
                # Run full analysis
                if hasattr(self.analyzer, 'run_full_analysis'):
                    result = self.analyzer.run_full_analysis()
                elif hasattr(self.analyzer, 'analyze_all'):
                    result = self.analyzer.analyze_all()
                else:
                    self.logger.error(f"Analyzer {analyzer_class_name} has no standard analysis method")
                    result = {
                        'error': 'No standard analysis method available',
                        'sample_size': data['sample_size']
                    }
            else:
                self.logger.warning("No analyzer class specified, using basic analysis")
                result = {
                    'sample_size': data['sample_size'],
                    'basic_stats': 'computed',
                    'note': 'No domain-specific analyzer available'
                }
            
            # Add metadata
            result['domain_id'] = domain_id
            result['config'] = self.config
            result['sample_size'] = data['sample_size']
            
            return result
        
        def _load_existing_data(self) -> Dict:
            """Load existing data for reanalysis"""
            self.logger.info("Loading existing data from database...")
            
            # Try to get model counts
            models = self.config.get('models', [])
            counts = {}
            
            for model_name in models:
                try:
                    from core import models
                    model_cls = getattr(models, model_name)
                    count = model_cls.query.count()
                    counts[model_name] = count
                    self.logger.info(f"  {model_name}: {count:,} records")
                except Exception as e:
                    self.logger.warning(f"  {model_name}: Unable to count ({e})")
            
            total_sample = sum(counts.values()) or 0
            
            return {
                'mode': 'reanalysis',
                'sample_size': total_sample,
                'model_counts': counts,
                'data_source': 'database'
            }
    
    return ConcreteDomainAnalyzer()


def run_single_domain(domain_id: str, mode: str, custom_params: Optional[Dict] = None) -> Dict:
    """
    Run analysis for a single domain.
    
    Args:
        domain_id: Domain identifier
        mode: Analysis mode
        custom_params: Optional custom parameters
    
    Returns:
        Analysis results dictionary
    """
    print("\n" + "=" * 80)
    print(f"RUNNING DOMAIN ANALYSIS: {domain_id.upper()}")
    print("=" * 80)
    
    try:
        with app.app_context():
            analyzer = create_domain_analyzer(domain_id, mode, custom_params)
            results = analyzer.run_full_pipeline()
            
            return results
    
    except Exception as e:
        logger.error(f"Domain analysis failed for {domain_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'domain_id': domain_id,
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def run_multiple_domains(domain_ids: List[str], mode: str, custom_params: Optional[Dict] = None) -> List[Dict]:
    """
    Run analysis for multiple domains sequentially.
    
    Args:
        domain_ids: List of domain identifiers
        mode: Analysis mode
        custom_params: Optional custom parameters
    
    Returns:
        List of results dictionaries
    """
    print("\n" + "=" * 80)
    print(f"MULTI-DOMAIN ANALYSIS: {len(domain_ids)} DOMAINS")
    print("=" * 80)
    
    results = []
    
    for i, domain_id in enumerate(domain_ids, 1):
        print(f"\n[{i}/{len(domain_ids)}] Processing: {domain_id}")
        result = run_single_domain(domain_id, mode, custom_params)
        results.append(result)
        
        # Print summary
        if result.get('status') != 'failed':
            print(f"✓ {domain_id} completed successfully")
        else:
            print(f"✗ {domain_id} failed: {result.get('error', 'Unknown error')}")
    
    return results


def print_final_summary(results: List[Dict]):
    """Print final summary of all analyses"""
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    successful = [r for r in results if r.get('status') != 'failed']
    failed = [r for r in results if r.get('status') == 'failed']
    
    print(f"\nTotal Domains: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print("\n" + "-" * 80)
        print("Successful Analyses:")
        print("-" * 80)
        for result in successful:
            domain_name = result.get('domain_name', result.get('domain_id', 'unknown'))
            sample_size = result.get('analysis', {}).get('sample_size', 'N/A')
            elapsed = result.get('elapsed_time', 0)
            print(f"  ✓ {domain_name}: N={sample_size}, Time={elapsed/60:.1f}min")
    
    if failed:
        print("\n" + "-" * 80)
        print("Failed Analyses:")
        print("-" * 80)
        for result in failed:
            domain_id = result.get('domain_id', 'unknown')
            error = result.get('error', 'Unknown error')
            print(f"  ✗ {domain_id}: {error}")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Domain Analysis Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run NFL analysis with fresh data
  python scripts/run_domain_analysis.py --domain nfl --mode new
  
  # Re-analyze immigration data
  python scripts/run_domain_analysis.py --domain immigration --mode reanalyze
  
  # Run multiple domains
  python scripts/run_domain_analysis.py --domains nfl,nba,bands --mode update
  
  # Custom sample size
  python scripts/run_domain_analysis.py --domain nfl --sample-size 2000
        """
    )
    
    # Domain selection
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--domain', type=str, help='Single domain to analyze')
    group.add_argument('--domains', type=str, help='Comma-separated list of domains')
    group.add_argument('--all', action='store_true', help='Run all registered domains')
    
    # Mode
    parser.add_argument(
        '--mode',
        type=str,
        choices=['new', 'reanalyze', 'update'],
        default='new',
        help='Analysis mode (default: new)'
    )
    
    # Custom parameters
    parser.add_argument('--sample-size', type=int, help='Custom sample size target')
    parser.add_argument('--custom-params', type=str, help='JSON string of custom parameters')
    
    # Output
    parser.add_argument('--output', type=str, help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Build custom parameters
    custom_params = {}
    if args.sample_size:
        custom_params['sample_size'] = args.sample_size
    if args.custom_params:
        try:
            custom_params.update(json.loads(args.custom_params))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in --custom-params: {e}")
            sys.exit(1)
    
    # Determine domains to run
    if args.domain:
        domain_ids = [args.domain]
    elif args.domains:
        domain_ids = [d.strip() for d in args.domains.split(',')]
    else:  # --all
        domain_ids = FRAMEWORK.list_active_domains()
        print(f"Running ALL active domains: {', '.join(domain_ids)}")
    
    # Validate domains
    for domain_id in domain_ids:
        if not FRAMEWORK.get_domain(domain_id):
            logger.error(f"Unknown domain: {domain_id}")
            logger.info(f"Available domains: {', '.join(FRAMEWORK.list_active_domains())}")
            sys.exit(1)
    
    # Run analyses
    if len(domain_ids) == 1:
        results = [run_single_domain(domain_ids[0], args.mode, custom_params)]
    else:
        results = run_multiple_domains(domain_ids, args.mode, custom_params)
    
    # Print summary
    print_final_summary(results)
    
    # Save results if requested
    if args.output:
        output_file = Path(args.output)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {output_file}")


if __name__ == '__main__':
    main()

