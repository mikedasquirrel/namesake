"""Migrate Hurricane Table Schema

Adds new columns to the hurricane table for the demographic expansion.
Run this before using the demographic analysis features.

Usage:
    python3 scripts/migrate_hurricane_schema.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from core.models import db
import sqlite3

def migrate_hurricane_table():
    """Add new columns to hurricane table."""
    
    db_path = PROJECT_ROOT / 'instance' / 'database.db'
    
    print("="*80)
    print("MIGRATING HURRICANE TABLE SCHEMA")
    print("="*80)
    
    # List of new columns to add
    new_columns = [
        ('deaths_direct', 'INTEGER'),
        ('deaths_indirect', 'INTEGER'),
        ('missing_persons', 'INTEGER'),
        ('insured_losses_usd', 'REAL'),
        ('agricultural_losses_usd', 'REAL'),
        ('displaced_persons', 'INTEGER'),
        ('homes_destroyed', 'INTEGER'),
        ('homes_damaged', 'INTEGER'),
        ('power_outages_peak', 'INTEGER'),
        ('power_outage_duration_days', 'REAL'),
        ('evacuations_ordered', 'INTEGER'),
        ('evacuations_actual', 'INTEGER'),
        ('shelters_opened', 'INTEGER'),
        ('shelter_peak_occupancy', 'INTEGER'),
        ('search_rescue_operations', 'INTEGER'),
        ('search_rescue_persons_saved', 'INTEGER'),
        ('forecast_error_24h_miles', 'REAL'),
        ('forecast_error_48h_miles', 'REAL'),
        ('forecast_error_72h_miles', 'REAL'),
        ('media_mentions_prelandfall', 'INTEGER'),
        ('media_mentions_postlandfall', 'INTEGER'),
        ('social_media_sentiment', 'REAL'),
        ('coastal_population_exposed', 'INTEGER'),
        ('prior_hurricanes_5yr', 'INTEGER'),
        ('landfall_location', 'VARCHAR(200)'),
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(hurricane)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    print(f"\nExisting columns: {len(existing_columns)}")
    
    # Add missing columns
    added_count = 0
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                alter_sql = f"ALTER TABLE hurricane ADD COLUMN {column_name} {column_type}"
                cursor.execute(alter_sql)
                print(f"✓ Added column: {column_name} ({column_type})")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"✗ Error adding {column_name}: {e}")
        else:
            print(f"- Already exists: {column_name}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"✅ MIGRATION COMPLETE: {added_count} columns added")
    print(f"{'='*80}\n")


def create_new_tables():
    """Create the new demographic tables."""
    print("="*80)
    print("CREATING NEW DEMOGRAPHIC TABLES")
    print("="*80)
    
    with app.app_context():
        # This will create any missing tables
        db.create_all()
        print("✓ Created geographic_demographics table")
        print("✓ Created hurricane_geography table")
        print("✓ Created hurricane_demographic_impact table")
    
    print(f"{'='*80}")
    print("✅ NEW TABLES CREATED")
    print(f"{'='*80}\n")


def main():
    """Run all migrations."""
    print("\n🔧 Starting database migration...")
    print()
    
    # Step 1: Migrate existing hurricane table
    migrate_hurricane_table()
    
    # Step 2: Create new demographic tables
    create_new_tables()
    
    print("="*80)
    print("✅ ALL MIGRATIONS COMPLETE")
    print("="*80)
    print("\nYou can now run the demographic collection scripts:")
    print("  python3 scripts/collect_hurricane_demographics.py --hurricane AL092005")
    print()


if __name__ == '__main__':
    main()

