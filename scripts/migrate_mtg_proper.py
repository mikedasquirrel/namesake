"""Proper MTG schema migration that checks column existence before adding."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app, db
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return column_name in columns


def migrate_schema():
    """Add new columns to MTG tables if they don't exist."""
    
    logger.info("Migrating MTG database schema...")
    
    # MTGCard columns to add
    mtg_card_columns = [
        ("set_year", "INTEGER"),
        ("format_legalities", "TEXT"),
        ("reprint_count", "INTEGER DEFAULT 0"),
        ("first_printing_set", "VARCHAR(10)"),
    ]
    
    # MTGCardAnalysis columns to add
    mtg_analysis_columns = [
        ("phonosemantic_data", "TEXT"),
        ("constructed_lang_data", "TEXT"),
        ("narrative_data", "TEXT"),
        ("semantic_data", "TEXT"),
        ("format_affinity_data", "TEXT"),
        ("intertextual_data", "TEXT"),
    ]
    
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Add MTGCard columns
    for col_name, col_type in mtg_card_columns:
        if not column_exists('mtg_card', col_name):
            try:
                cursor.execute(f"ALTER TABLE mtg_card ADD COLUMN {col_name} {col_type}")
                logger.info(f"  ✓ Added mtg_card.{col_name}")
            except Exception as e:
                logger.error(f"  ✗ Failed to add mtg_card.{col_name}: {e}")
        else:
            logger.info(f"  ✓ mtg_card.{col_name} already exists")
    
    # Add MTGCardAnalysis columns
    for col_name, col_type in mtg_analysis_columns:
        if not column_exists('mtg_card_analysis', col_name):
            try:
                cursor.execute(f"ALTER TABLE mtg_card_analysis ADD COLUMN {col_name} {col_type}")
                logger.info(f"  ✓ Added mtg_card_analysis.{col_name}")
            except Exception as e:
                logger.error(f"  ✗ Failed to add mtg_card_analysis.{col_name}: {e}")
        else:
            logger.info(f"  ✓ mtg_card_analysis.{col_name} already exists")
    
    conn.commit()
    conn.close()
    
    logger.info("✅ Schema migration complete!")
    return True


if __name__ == '__main__':
    success = migrate_schema()
    sys.exit(0 if success else 1)

