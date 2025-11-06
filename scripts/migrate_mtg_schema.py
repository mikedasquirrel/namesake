"""Migrate MTG database schema to support comprehensive analysis.

Adds new columns for:
- Format legalities
- Set year
- Reprint data
- Advanced linguistic analysis fields
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_schema():
    """Add new columns to MTG tables."""
    
    with app.app_context():
        try:
            logger.info("Migrating MTG database schema...")
            
            # MTGCard table migrations
            mtg_migrations = [
                "ALTER TABLE mtg_card ADD COLUMN IF NOT EXISTS set_year INTEGER",
                "ALTER TABLE mtg_card ADD COLUMN IF NOT EXISTS format_legalities TEXT",
                "ALTER TABLE mtg_card ADD COLUMN IF NOT EXISTS reprint_count INTEGER DEFAULT 0",
                "ALTER TABLE mtg_card ADD COLUMN IF NOT EXISTS first_printing_set VARCHAR(10)",
            ]
            
            # MTGCardAnalysis table migrations
            analysis_migrations = [
                "ALTER TABLE mtg_card_analysis ADD COLUMN IF NOT EXISTS phonosemantic_data TEXT",
                "ALTER TABLE mtg_card_analysis ADD COLUMN IF NOT EXISTS constructed_lang_data TEXT",
                "ALTER TABLE mtg_card_analysis ADD COLUMN IF NOT EXISTS narrative_data TEXT",
                "ALTER TABLE mtg_card_analysis ADD COLUMN IF NOT EXISTS semantic_data TEXT",
                "ALTER TABLE mtg_card_analysis ADD COLUMN IF NOT EXISTS format_affinity_data TEXT",
                "ALTER TABLE mtg_card_analysis ADD COLUMN IF NOT EXISTS intertextual_data TEXT",
            ]
            
            all_migrations = mtg_migrations + analysis_migrations
            
            for migration in all_migrations:
                try:
                    db.session.execute(db.text(migration))
                    logger.info(f"  ✓ {migration[:60]}...")
                except Exception as e:
                    logger.warning(f"  ⚠ {migration[:60]}... (may already exist)")
            
            db.session.commit()
            
            logger.info("✅ Schema migration complete!")
            return True
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = migrate_schema()
    sys.exit(0 if success else 1)

