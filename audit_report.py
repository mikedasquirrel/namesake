#!/usr/bin/env python3
"""
Comprehensive Project Audit Script
Analyzes app.py routes, templates, analyzers, and data to determine what's actually functional
"""

import re
import os
from pathlib import Path
from collections import defaultdict
import json

def audit_routes():
    """Extract all routes from app.py and categorize them"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find all route definitions
    route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"]\s*(?:,\s*methods=\[([^\]]+)\])?\)\s*def\s+(\w+)\('
    routes = re.findall(route_pattern, content)
    
    categorized = defaultdict(list)
    
    for path, methods, func_name in routes:
        # Categorize by path prefix
        if path.startswith('/api/'):
            category = 'API'
        elif path.startswith('/betting') or 'betting' in path:
            category = 'Betting'
        elif any(sport in path for sport in ['/nba', '/nfl', '/mlb', '/sports']):
            category = 'Sports'
        elif path in ['/', '/overview', '/analysis']:
            category = 'Core'
        elif any(x in path for x in ['/crypto', '/mtg', '/board-games']):
            category = 'Markets'
        elif any(x in path for x in ['/hurricane', '/earthquake']):
            category = 'Natural Events'
        else:
            category = 'Other Research'
        
        categorized[category].append({
            'path': path,
            'methods': methods if methods else 'GET',
            'function': func_name
        })
    
    return categorized, len(routes)

def audit_templates():
    """Check which templates exist and which are used"""
    templates = list(Path('templates').glob('*.html'))
    
    # Read app.py to find template usage
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    used_templates = set(re.findall(r"render_template\(['\"]([^'\"]+)['\"]", app_content))
    
    template_files = {t.name for t in templates}
    unused = template_files - used_templates
    missing = used_templates - template_files
    
    return {
        'total': len(template_files),
        'used': len(used_templates),
        'unused': sorted(unused),
        'missing': sorted(missing)
    }

def audit_analyzers():
    """Check analyzer modules and their usage"""
    analyzers = list(Path('analyzers').glob('*.py'))
    analyzers = [a for a in analyzers if a.name != '__init__.py']
    
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    used = []
    unused = []
    
    for analyzer in analyzers:
        module_name = analyzer.stem
        # Check if imported in app.py
        if f'from analyzers.{module_name}' in app_content or f'analyzers.{module_name}' in app_content:
            used.append(module_name)
        else:
            unused.append(module_name)
    
    return {
        'total': len(analyzers),
        'used_in_app': len(used),
        'unused_in_app': len(unused),
        'unused_list': sorted(unused)[:20]  # First 20
    }

def audit_data_files():
    """Check data directory structure"""
    data_dir = Path('data')
    
    stats = {
        'raw_files': 0,
        'processed_files': 0,
        'json_files': 0,
        'csv_files': 0,
        'parquet_files': 0,
        'directories': []
    }
    
    for item in data_dir.rglob('*'):
        if item.is_file():
            if 'raw' in str(item):
                stats['raw_files'] += 1
            elif 'processed' in str(item):
                stats['processed_files'] += 1
            
            if item.suffix == '.json':
                stats['json_files'] += 1
            elif item.suffix == '.csv':
                stats['csv_files'] += 1
            elif item.suffix == '.parquet':
                stats['parquet_files'] += 1
        elif item.is_dir() and item.parent == data_dir:
            stats['directories'].append(item.name)
    
    return stats

def audit_documentation():
    """Count documentation files in root vs organized"""
    root_md = list(Path('.').glob('*.md'))
    root_md = [f for f in root_md if f.name != 'README.md']
    
    organized_md = list(Path('docs_organized').rglob('*.md')) if Path('docs_organized').exists() else []
    
    return {
        'root_md_files': len(root_md),
        'organized_md_files': len(organized_md),
        'root_files': [f.name for f in sorted(root_md, key=lambda x: x.stat().st_mtime, reverse=True)[:30]]
    }

def check_database_status():
    """Check if databases exist"""
    return {
        'sqlite_instance': Path('instance/namesake.db').exists(),
        'duckdb': Path('name_study.duckdb').exists(),
        'sqlite_size_mb': Path('instance/namesake.db').stat().st_size / (1024*1024) if Path('instance/namesake.db').exists() else 0
    }

def main():
    print("=" * 80)
    print("COMPREHENSIVE PROJECT AUDIT")
    print("=" * 80)
    print()
    
    # Routes audit
    print("📍 ROUTES AUDIT")
    print("-" * 80)
    categorized_routes, total_routes = audit_routes()
    print(f"Total Routes: {total_routes}")
    for category, routes in sorted(categorized_routes.items()):
        print(f"\n{category}: {len(routes)} routes")
        for route in routes[:5]:  # Show first 5
            print(f"  {route['methods']:8} {route['path']:40} -> {route['function']}")
        if len(routes) > 5:
            print(f"  ... and {len(routes) - 5} more")
    print()
    
    # Templates audit
    print("📄 TEMPLATES AUDIT")
    print("-" * 80)
    templates = audit_templates()
    print(f"Total Template Files: {templates['total']}")
    print(f"Used in Routes: {templates['used']}")
    print(f"Unused Templates: {len(templates['unused'])}")
    if templates['unused']:
        print(f"Examples: {', '.join(list(templates['unused'])[:10])}")
    if templates['missing']:
        print(f"⚠️  Missing Templates: {', '.join(templates['missing'])}")
    print()
    
    # Analyzers audit
    print("🔬 ANALYZERS AUDIT")
    print("-" * 80)
    analyzers = audit_analyzers()
    print(f"Total Analyzer Modules: {analyzers['total']}")
    print(f"Used in app.py: {analyzers['used_in_app']}")
    print(f"Not Imported in app.py: {analyzers['unused_in_app']}")
    if analyzers['unused_list']:
        print(f"Examples: {', '.join(analyzers['unused_list'][:10])}")
    print()
    
    # Data audit
    print("💾 DATA AUDIT")
    print("-" * 80)
    data = audit_data_files()
    print(f"Raw Data Files: {data['raw_files']}")
    print(f"Processed Data Files: {data['processed_files']}")
    print(f"JSON Files: {data['json_files']}")
    print(f"CSV Files: {data['csv_files']}")
    print(f"Parquet Files: {data['parquet_files']}")
    print(f"Data Directories: {', '.join(sorted(data['directories']))}")
    print()
    
    # Database audit
    print("🗄️  DATABASE AUDIT")
    print("-" * 80)
    db_status = check_database_status()
    print(f"SQLite DB (instance/namesake.db): {'✓ EXISTS' if db_status['sqlite_instance'] else '✗ MISSING'}")
    if db_status['sqlite_instance']:
        print(f"  Size: {db_status['sqlite_size_mb']:.1f} MB")
    print(f"DuckDB (name_study.duckdb): {'✓ EXISTS' if db_status['duckdb'] else '✗ MISSING'}")
    print()
    
    # Documentation audit
    print("📚 DOCUMENTATION AUDIT")
    print("-" * 80)
    docs = audit_documentation()
    print(f"Root-Level .md Files: {docs['root_md_files']} (SHOULD BE ~0-3)")
    print(f"Organized Documentation: {docs['organized_md_files']} files")
    print("\nRecent Root .md Files (first 30):")
    for filename in docs['root_files']:
        print(f"  {filename}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("🔴 CRITICAL ISSUES:")
    print(f"  • {total_routes} routes in single file (target: <50 per blueprint)")
    print(f"  • {docs['root_md_files']} markdown files in root (target: 2-3)")
    print(f"  • {templates['total']} templates ({len(templates['unused'])} unused)")
    print(f"  • {analyzers['total']} analyzer modules ({analyzers['unused_in_app']} not used in app.py)")
    print()
    print("✅ NEXT STEPS:")
    print("  1. Archive root markdown files to docs_archive/")
    print("  2. Split app.py into blueprints")
    print("  3. Archive unused templates")
    print("  4. Consolidate analyzer modules")
    print()
    
    # Save detailed report
    report = {
        'routes': {
            'total': total_routes,
            'by_category': {cat: len(routes) for cat, routes in categorized_routes.items()}
        },
        'templates': templates,
        'analyzers': analyzers,
        'data': data,
        'database': db_status,
        'documentation': docs
    }
    
    with open('AUDIT_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("📊 Detailed report saved to: AUDIT_REPORT.json")
    print()

if __name__ == '__main__':
    main()

