#!/usr/bin/env python3
"""
Data Quality Validation Script
Checks data completeness and quality across all domains
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_databases():
    """Check if databases exist and are accessible"""
    results = {}
    
    # Check SQLite
    sqlite_path = Path('instance/namesake.db')
    results['sqlite'] = {
        'exists': sqlite_path.exists(),
        'size_mb': sqlite_path.stat().st_size / (1024*1024) if sqlite_path.exists() else 0,
        'path': str(sqlite_path)
    }
    
    # Check DuckDB
    duckdb_path = Path('name_study.duckdb')
    results['duckdb'] = {
        'exists': duckdb_path.exists(),
        'size_mb': duckdb_path.stat().st_size / (1024*1024) if duckdb_path.exists() else 0,
        'path': str(duckdb_path)
    }
    
    return results

def check_data_files():
    """Check data directory contents"""
    data_dir = Path('data')
    
    if not data_dir.exists():
        return {'error': 'data/ directory not found'}
    
    results = {
        'raw_files': 0,
        'processed_files': 0,
        'json_files': 0,
        'csv_files': 0,
        'parquet_files': 0,
        'total_size_mb': 0
    }
    
    for item in data_dir.rglob('*'):
        if item.is_file():
            size_mb = item.stat().st_size / (1024*1024)
            results['total_size_mb'] += size_mb
            
            if 'raw' in str(item):
                results['raw_files'] += 1
            elif 'processed' in str(item):
                results['processed_files'] += 1
            
            if item.suffix == '.json':
                results['json_files'] += 1
            elif item.suffix == '.csv':
                results['csv_files'] += 1
            elif item.suffix == '.parquet':
                results['parquet_files'] += 1
    
    results['total_size_mb'] = round(results['total_size_mb'], 2)
    
    return results

def check_domain_data():
    """Check if each domain has data files"""
    domains = {
        'crypto': 'Auto-collected on startup',
        'hurricanes': 'data/predictions_2026/hurricane_predictions_2026.csv',
        'mental_health': 'data/mental_health_nomenclature/',
        'ships': 'data/famous_ships_extended.json',
        'adult_film': 'data/pornhub_performers.json',
        'elections': 'data/international_relations/',
        'names_usa': 'data/raw/usa_ssa_names/',
        'names_processed': 'data/processed/',
    }
    
    results = {}
    for domain, path_str in domains.items():
        path = Path(path_str)
        results[domain] = {
            'path': path_str,
            'exists': path.exists(),
            'type': 'directory' if path.is_dir() else 'file' if path.exists() else 'missing'
        }
    
    return results

def check_collectors():
    """Check which collector scripts exist"""
    collectors_dir = Path('collectors')
    
    if not collectors_dir.exists():
        return {'error': 'collectors/ directory not found'}
    
    collectors = list(collectors_dir.glob('*_collector.py'))
    
    return {
        'total': len(collectors),
        'collectors': [c.stem for c in sorted(collectors)]
    }

def check_sqlite_tables():
    """Check SQLite database tables"""
    try:
        import sqlite3
        db_path = 'instance/namesake.db'
        
        if not Path(db_path).exists():
            return {'error': 'Database not found'}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get row counts
        table_counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_counts[table] = count
        
        conn.close()
        
        return {
            'tables': len(tables),
            'table_names': tables,
            'row_counts': table_counts
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=" * 80)
    print("DATA QUALITY VALIDATION")
    print("=" * 80)
    print()
    
    # Check databases
    print("📊 DATABASES")
    print("-" * 80)
    dbs = check_databases()
    for db_name, info in dbs.items():
        status = "✓ EXISTS" if info['exists'] else "✗ MISSING"
        size = f"({info['size_mb']:.1f} MB)" if info['exists'] else ""
        print(f"{db_name:15} {status:15} {size}")
    print()
    
    # Check SQLite tables
    if dbs['sqlite']['exists']:
        print("📑 SQLITE TABLES")
        print("-" * 80)
        tables_info = check_sqlite_tables()
        if 'error' not in tables_info:
            print(f"Total Tables: {tables_info['tables']}")
            for table, count in sorted(tables_info['row_counts'].items()):
                print(f"  {table:40} {count:>10,} rows")
        else:
            print(f"  Error: {tables_info['error']}")
        print()
    
    # Check data files
    print("📁 DATA FILES")
    print("-" * 80)
    files = check_data_files()
    if 'error' not in files:
        print(f"Raw Files:       {files['raw_files']}")
        print(f"Processed Files: {files['processed_files']}")
        print(f"JSON Files:      {files['json_files']}")
        print(f"CSV Files:       {files['csv_files']}")
        print(f"Parquet Files:   {files['parquet_files']}")
        print(f"Total Size:      {files['total_size_mb']:.1f} MB")
    else:
        print(f"Error: {files['error']}")
    print()
    
    # Check domain data
    print("🗂️  DOMAIN DATA")
    print("-" * 80)
    domains = check_domain_data()
    for domain, info in sorted(domains.items()):
        status = "✓" if info['exists'] else "✗"
        print(f"{status} {domain:20} {info['type']:12} {info['path']}")
    print()
    
    # Check collectors
    print("⚙️  COLLECTORS")
    print("-" * 80)
    collectors = check_collectors()
    if 'error' not in collectors:
        print(f"Total Collector Scripts: {collectors['total']}")
        print("\nAvailable collectors:")
        for collector in collectors['collectors'][:20]:  # First 20
            print(f"  • {collector}")
        if collectors['total'] > 20:
            print(f"  ... and {collectors['total'] - 20} more")
    else:
        print(f"Error: {collectors['error']}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    issues = []
    
    if not dbs['sqlite']['exists']:
        issues.append("🔴 SQLite database missing - run: python3 app.py")
    
    if not dbs['duckdb']['exists']:
        issues.append("🟡 DuckDB missing - name diversity analysis unavailable")
    
    domain_missing = sum(1 for d in domains.values() if not d['exists'])
    if domain_missing > 0:
        issues.append(f"🟡 {domain_missing} domains missing data files")
    
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ All critical data checks passed!")
    
    print()
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'databases': dbs,
        'data_files': files,
        'domains': domains,
        'collectors': collectors,
        'sqlite_tables': tables_info if dbs['sqlite']['exists'] else None,
        'issues': issues
    }
    
    report_path = Path('DATA_VALIDATION_REPORT.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_path}")
    print()

if __name__ == '__main__':
    main()

