#!/usr/bin/env python3
"""
Formula Engine CLI - Command Line Management Tool

Provides command-line interface for managing formula analysis system:
- Scheduler control (start/stop/status)
- Manual analysis triggers
- Results viewing and comparison
- Cache management
- System status

Usage:
    python scripts/formula_cli.py scheduler start
    python scripts/formula_cli.py analyze --mode daily
    python scripts/formula_cli.py results --latest
    python scripts/formula_cli.py status
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import json
from datetime import datetime
from tabulate import tabulate

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print styled header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {text}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {text}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {text}")


# ============================================================================
# Scheduler Commands
# ============================================================================

def scheduler_start(args):
    """Start the scheduler"""
    from scripts.scheduler import initialize_scheduler, get_scheduler_status
    
    print_header("STARTING FORMULA ANALYSIS SCHEDULER")
    
    try:
        if initialize_scheduler(config_path=args.config):
            print_success("Scheduler started successfully")
            
            # Show status
            status = get_scheduler_status()
            print_info(f"Running {status['job_count']} scheduled jobs")
            
            for job in status['jobs']:
                print(f"  • {job['name']}")
                print(f"    Next run: {job['next_run']}")
            
            print("\nScheduler is running. Press Ctrl+C to stop.")
            
            # Keep running
            import time
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n")
                scheduler_stop(args)
        else:
            print_error("Failed to start scheduler")
            sys.exit(1)
    
    except Exception as e:
        print_error(f"Scheduler error: {e}")
        sys.exit(1)


def scheduler_stop(args):
    """Stop the scheduler"""
    from scripts.scheduler import shutdown_scheduler
    
    print_info("Stopping scheduler...")
    shutdown_scheduler()
    print_success("Scheduler stopped")


def scheduler_status(args):
    """Show scheduler status"""
    from scripts.scheduler import initialize_scheduler, get_scheduler_status, shutdown_scheduler
    
    print_header("SCHEDULER STATUS")
    
    try:
        initialize_scheduler(config_path=args.config)
        status = get_scheduler_status()
        
        if status['running']:
            print_success(f"Scheduler is RUNNING with {status['job_count']} jobs")
            
            if status['jobs']:
                print("\nScheduled Jobs:")
                table_data = []
                for job in status['jobs']:
                    table_data.append([
                        job['id'],
                        job['name'],
                        job['next_run'] or 'N/A',
                        str(job['trigger'])[:50]
                    ])
                
                print(tabulate(table_data,
                             headers=['ID', 'Name', 'Next Run', 'Trigger'],
                             tablefmt='grid'))
        else:
            print_error("Scheduler is STOPPED")
        
        shutdown_scheduler()
    
    except Exception as e:
        print_error(f"Status check failed: {e}")
        sys.exit(1)


def scheduler_trigger(args):
    """Trigger a job immediately"""
    from scripts.scheduler import initialize_scheduler, trigger_job_now, shutdown_scheduler
    
    if not args.job:
        print_error("--job parameter required")
        sys.exit(1)
    
    print_header(f"TRIGGERING JOB: {args.job}")
    
    try:
        initialize_scheduler(config_path=args.config)
        
        if trigger_job_now(args.job):
            print_success(f"Job '{args.job}' triggered successfully")
        else:
            print_error(f"Failed to trigger job '{args.job}'")
            sys.exit(1)
        
        shutdown_scheduler()
    
    except Exception as e:
        print_error(f"Trigger failed: {e}")
        sys.exit(1)


# ============================================================================
# Analysis Commands
# ============================================================================

def analyze(args):
    """Run analysis"""
    from scripts.auto_analyze_formulas import AutoFormulaAnalyzer
    
    mode = args.mode or 'daily'
    
    print_header(f"RUNNING {mode.upper()} ANALYSIS")
    
    try:
        analyzer = AutoFormulaAnalyzer(output_dir=args.output)
        
        if mode == 'daily':
            results = analyzer.run_daily_analysis()
        elif mode == 'weekly':
            results = analyzer.run_weekly_deep_dive()
        elif mode == 'on-demand':
            results = analyzer.run_on_new_data(domain=args.domain)
        else:
            print_error(f"Unknown mode: {mode}")
            sys.exit(1)
        
        # Summary
        if results['success']:
            print_success("Analysis completed successfully")
        else:
            print_error(f"Analysis completed with {len(results['errors'])} errors")
        
        print(f"\nDuration: {results.get('duration', 'N/A')}")
        print(f"Validations: {len(results.get('validations', {}))}")
        print(f"Evolutions: {len(results.get('evolutions', {}))}")
        
        if results.get('errors'):
            print("\nErrors:")
            for error in results['errors']:
                print(f"  • {error.get('step')}: {error.get('error')}")
    
    except Exception as e:
        print_error(f"Analysis failed: {e}")
        sys.exit(1)


# ============================================================================
# Results Commands
# ============================================================================

def results_latest(args):
    """Show latest results"""
    mode = args.mode or 'daily'
    output_dir = Path(args.output)
    
    latest_file = output_dir / f'{mode}_analysis_latest.json'
    
    print_header(f"LATEST {mode.upper()} ANALYSIS RESULTS")
    
    if not latest_file.exists():
        print_error(f"No results found: {latest_file}")
        sys.exit(1)
    
    try:
        with open(latest_file) as f:
            results = json.load(f)
        
        print(f"Mode: {results.get('mode')}")
        print(f"Time: {results.get('start_time')}")
        print(f"Duration: {results.get('duration', 'N/A')}")
        print(f"Success: {results.get('success')}")
        
        # Validations summary
        if results.get('validations'):
            print("\nValidation Results:")
            table_data = []
            for formula, validation in results['validations'].items():
                table_data.append([
                    formula,
                    f"{validation.get('overall_correlation', 0):.3f}",
                    validation.get('best_domain', 'N/A')
                ])
            
            print(tabulate(table_data,
                         headers=['Formula', 'Correlation', 'Best Domain'],
                         tablefmt='grid'))
        
        # Evolution summary
        if results.get('evolutions'):
            print("\nEvolution Results:")
            table_data = []
            for formula, evolution in results['evolutions'].items():
                table_data.append([
                    formula,
                    f"{evolution.get('final_best_fitness', 0):.3f}",
                    'Yes' if evolution.get('converged') else 'No'
                ])
            
            print(tabulate(table_data,
                         headers=['Formula', 'Final Fitness', 'Converged'],
                         tablefmt='grid'))
        
        # Errors
        if results.get('errors'):
            print(f"\nErrors: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5
                print(f"  • {error.get('step')}: {error.get('error')[:60]}")
    
    except Exception as e:
        print_error(f"Failed to load results: {e}")
        sys.exit(1)


def results_compare(args):
    """Compare two result versions"""
    if not args.v1 or not args.v2:
        print_error("Both --v1 and --v2 required for comparison")
        sys.exit(1)
    
    print_header("COMPARING RESULTS")
    
    output_dir = Path(args.output)
    
    file1 = output_dir / args.v1
    file2 = output_dir / args.v2
    
    if not file1.exists() or not file2.exists():
        print_error("One or both result files not found")
        sys.exit(1)
    
    try:
        with open(file1) as f:
            results1 = json.load(f)
        with open(file2) as f:
            results2 = json.load(f)
        
        print(f"Version 1: {file1.name}")
        print(f"Version 2: {file2.name}\n")
        
        # Compare validations
        if results1.get('validations') and results2.get('validations'):
            print("Validation Comparison:")
            table_data = []
            for formula in results1['validations']:
                if formula in results2['validations']:
                    corr1 = results1['validations'][formula].get('overall_correlation', 0)
                    corr2 = results2['validations'][formula].get('overall_correlation', 0)
                    diff = corr2 - corr1
                    table_data.append([
                        formula,
                        f"{corr1:.3f}",
                        f"{corr2:.3f}",
                        f"{diff:+.3f}"
                    ])
            
            print(tabulate(table_data,
                         headers=['Formula', 'V1 Corr', 'V2 Corr', 'Change'],
                         tablefmt='grid'))
    
    except Exception as e:
        print_error(f"Comparison failed: {e}")
        sys.exit(1)


# ============================================================================
# Status Commands
# ============================================================================

def status(args):
    """Show system status"""
    from utils.formula_cache import cache
    from app import app
    
    print_header("FORMULA ENGINE SYSTEM STATUS")
    
    # Cache status
    print("Cache Status:")
    cache_stats = cache.get_stats()
    
    if cache_stats.get('enabled'):
        if cache_stats.get('connected'):
            print_success(f"  Redis connected ({cache_stats.get('total_keys', 0)} keys)")
            print(f"    Memory: {cache_stats.get('used_memory', 'N/A')}")
        else:
            print_error("  Redis connection failed")
    else:
        print_info("  Cache disabled")
    
    # Scheduler status
    print("\nScheduler Status:")
    try:
        from scripts.scheduler import get_scheduler_status
        sched_status = get_scheduler_status()
        
        if sched_status['running']:
            print_success(f"  Running ({sched_status['job_count']} jobs)")
        else:
            print_info("  Not running")
    except:
        print_info("  Not initialized")
    
    # Database status
    print("\nDatabase Status:")
    try:
        with app.app_context():
            from core.models import db, Cryptocurrency
            count = Cryptocurrency.query.count()
            print_success(f"  Connected ({count} cryptocurrencies)")
    except Exception as e:
        print_error(f"  Connection failed: {e}")
    
    # Disk usage
    print("\nStorage Usage:")
    output_dir = Path(args.output)
    if output_dir.exists():
        total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
        total_files = len(list(output_dir.rglob('*')))
        print_info(f"  {total_files} files, {total_size / 1024 / 1024:.1f} MB")
    else:
        print_info("  No results directory")


# ============================================================================
# Cache Commands
# ============================================================================

def cache_clear(args):
    """Clear cache"""
    from utils.formula_cache import cache
    
    print_header("CLEARING CACHE")
    
    if args.confirm != 'yes':
        print_error("This will delete all cached data. Use --confirm yes to proceed.")
        sys.exit(1)
    
    try:
        if cache.clear_all():
            print_success("Cache cleared successfully")
        else:
            print_error("Cache clear failed (cache may be disabled)")
    except Exception as e:
        print_error(f"Cache clear failed: {e}")
        sys.exit(1)


def cache_stats(args):
    """Show cache statistics"""
    from utils.formula_cache import cache
    
    print_header("CACHE STATISTICS")
    
    stats = cache.get_stats()
    
    print(f"Enabled: {stats.get('enabled')}")
    print(f"Connected: {stats.get('connected')}")
    print(f"Total Keys: {stats.get('total_keys', 0)}")
    print(f"Memory Used: {stats.get('used_memory', 'N/A')}")
    print(f"Hit Rate: {stats.get('hit_rate', 'N/A')}")


# ============================================================================
# Export Commands
# ============================================================================

def export_results(args):
    """Export results in various formats"""
    print_header(f"EXPORTING RESULTS AS {args.format.upper()}")
    
    output_dir = Path(args.output)
    latest_file = output_dir / f'{args.mode}_analysis_latest.json'
    
    if not latest_file.exists():
        print_error(f"No results found: {latest_file}")
        sys.exit(1)
    
    try:
        with open(latest_file) as f:
            results = json.load(f)
        
        if args.format == 'json':
            # Already JSON, just copy
            export_file = Path(args.file or f'export_{args.mode}.json')
            with open(export_file, 'w') as f:
                json.dump(results, f, indent=2)
            print_success(f"Exported to {export_file}")
        
        elif args.format == 'csv':
            import csv
            export_file = Path(args.file or f'export_{args.mode}.csv')
            
            # Export validations as CSV
            if results.get('validations'):
                with open(export_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Formula', 'Correlation', 'Consistency', 'Best Domain'])
                    
                    for formula, validation in results['validations'].items():
                        writer.writerow([
                            formula,
                            validation.get('overall_correlation', 0),
                            validation.get('consistency_score', 0),
                            validation.get('best_domain', 'N/A')
                        ])
                
                print_success(f"Exported to {export_file}")
            else:
                print_error("No validation results to export")
        
        elif args.format == 'pdf':
            print_error("PDF export not yet implemented")
            sys.exit(1)
    
    except Exception as e:
        print_error(f"Export failed: {e}")
        sys.exit(1)


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Formula Engine CLI - Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scheduler start
  %(prog)s scheduler status
  %(prog)s analyze --mode daily
  %(prog)s results --latest
  %(prog)s status
  %(prog)s cache clear --confirm yes
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scheduler commands
    scheduler_parser = subparsers.add_parser('scheduler', help='Scheduler control')
    scheduler_parser.add_argument('action', choices=['start', 'stop', 'status', 'trigger'])
    scheduler_parser.add_argument('--job', help='Job ID (for trigger)')
    scheduler_parser.add_argument('--config', default='config/auto_analysis.yaml')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run analysis')
    analyze_parser.add_argument('--mode', choices=['daily', 'weekly', 'on-demand'], default='daily')
    analyze_parser.add_argument('--domain', help='Domain for on-demand analysis')
    analyze_parser.add_argument('--output', default='analysis_outputs/auto_analysis')
    
    # Results commands
    results_parser = subparsers.add_parser('results', help='View results')
    results_parser.add_argument('--latest', action='store_true', help='Show latest results')
    results_parser.add_argument('--compare', action='store_true', help='Compare versions')
    results_parser.add_argument('--mode', choices=['daily', 'weekly'], default='daily')
    results_parser.add_argument('--v1', help='First version for comparison')
    results_parser.add_argument('--v2', help='Second version for comparison')
    results_parser.add_argument('--output', default='analysis_outputs/auto_analysis')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='System status')
    status_parser.add_argument('--output', default='analysis_outputs/auto_analysis')
    
    # Cache commands
    cache_parser = subparsers.add_parser('cache', help='Cache management')
    cache_parser.add_argument('action', choices=['clear', 'stats'])
    cache_parser.add_argument('--confirm', help='Confirmation (use "yes")')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export results')
    export_parser.add_argument('--format', choices=['json', 'csv', 'pdf'], default='json')
    export_parser.add_argument('--mode', choices=['daily', 'weekly'], default='daily')
    export_parser.add_argument('--file', help='Output file path')
    export_parser.add_argument('--output', default='analysis_outputs/auto_analysis')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate function
    try:
        if args.command == 'scheduler':
            if args.action == 'start':
                scheduler_start(args)
            elif args.action == 'stop':
                scheduler_stop(args)
            elif args.action == 'status':
                scheduler_status(args)
            elif args.action == 'trigger':
                scheduler_trigger(args)
        
        elif args.command == 'analyze':
            analyze(args)
        
        elif args.command == 'results':
            if args.compare:
                results_compare(args)
            else:
                results_latest(args)
        
        elif args.command == 'status':
            status(args)
        
        elif args.command == 'cache':
            if args.action == 'clear':
                cache_clear(args)
            elif args.action == 'stats':
                cache_stats(args)
        
        elif args.command == 'export':
            export_results(args)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Command failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

