"""
Database Migration: Add Failure Tracking Fields
Adds fields to track failures/delistings for statistical rigor (eliminate survivorship bias)

Run this script ONCE to add new columns to existing database
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Add failure tracking columns to existing tables"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            logger.info("Starting database migration...")
            
            # Get database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # ========================================
            # CRYPTOCURRENCY TABLE
            # ========================================
            logger.info("Adding columns to cryptocurrency table...")
            
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(cryptocurrency)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if 'is_active' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE cryptocurrency 
                    ADD COLUMN is_active BOOLEAN DEFAULT 1
                """)
                logger.info("  ✓ Added is_active column")
            else:
                logger.info("  - is_active already exists")
            
            if 'delisting_date' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE cryptocurrency 
                    ADD COLUMN delisting_date DATETIME
                """)
                logger.info("  ✓ Added delisting_date column")
            else:
                logger.info("  - delisting_date already exists")
            
            if 'failure_reason' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE cryptocurrency 
                    ADD COLUMN failure_reason VARCHAR(200)
                """)
                logger.info("  ✓ Added failure_reason column")
            else:
                logger.info("  - failure_reason already exists")
            
            # ========================================
            # DOMAIN TABLE
            # ========================================
            logger.info("Adding columns to domain table...")
            
            cursor.execute("PRAGMA table_info(domain)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if 'auction_failed' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE domain 
                    ADD COLUMN auction_failed BOOLEAN DEFAULT 0
                """)
                logger.info("  ✓ Added auction_failed column")
            else:
                logger.info("  - auction_failed already exists")
            
            if 'listing_price' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE domain 
                    ADD COLUMN listing_price FLOAT
                """)
                logger.info("  ✓ Added listing_price column")
            else:
                logger.info("  - listing_price already exists")
            
            if 'days_on_market' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE domain 
                    ADD COLUMN days_on_market INTEGER
                """)
                logger.info("  ✓ Added days_on_market column")
            else:
                logger.info("  - days_on_market already exists")
            
            # ========================================
            # STOCK TABLE
            # ========================================
            logger.info("Adding columns to stock table...")
            
            cursor.execute("PRAGMA table_info(stock)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if 'is_active' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE stock 
                    ADD COLUMN is_active BOOLEAN DEFAULT 1
                """)
                logger.info("  ✓ Added is_active column")
            else:
                logger.info("  - is_active already exists")
            
            if 'delisted_date' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE stock 
                    ADD COLUMN delisted_date DATETIME
                """)
                logger.info("  ✓ Added delisted_date column")
            else:
                logger.info("  - delisted_date already exists")
            
            if 'delisting_reason' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE stock 
                    ADD COLUMN delisting_reason VARCHAR(200)
                """)
                logger.info("  ✓ Added delisting_reason column")
            else:
                logger.info("  - delisting_reason already exists")
            
            if 'final_price' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE stock 
                    ADD COLUMN final_price FLOAT
                """)
                logger.info("  ✓ Added final_price column")
            else:
                logger.info("  - final_price already exists")
            
            # Commit changes
            connection.commit()
            
            # ========================================
            # BACKFILL EXISTING DATA
            # ========================================
            logger.info("\nBackfilling existing records with default values...")
            
            # Mark all existing cryptos as active (they're currently traded)
            cursor.execute("""
                UPDATE cryptocurrency 
                SET is_active = 1 
                WHERE is_active IS NULL
            """)
            crypto_count = cursor.rowcount
            logger.info(f"  ✓ Marked {crypto_count} existing cryptocurrencies as active")
            
            # Mark all existing domains as successful sales (not failed auctions)
            cursor.execute("""
                UPDATE domain 
                SET auction_failed = 0 
                WHERE auction_failed IS NULL
            """)
            domain_count = cursor.rowcount
            logger.info(f"  ✓ Marked {domain_count} existing domains as successful sales")
            
            # Mark all existing stocks as active
            cursor.execute("""
                UPDATE stock 
                SET is_active = 1 
                WHERE is_active IS NULL
            """)
            stock_count = cursor.rowcount
            logger.info(f"  ✓ Marked {stock_count} existing stocks as active")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info("\n" + "="*60)
            logger.info("✅ MIGRATION COMPLETE")
            logger.info("="*60)
            logger.info(f"Cryptocurrency: {crypto_count} records updated")
            logger.info(f"Domain: {domain_count} records updated")
            logger.info(f"Stock: {stock_count} records updated")
            logger.info("\nDatabase is now ready to track failures/delistings")
            logger.info("Next: Run data collectors to add mid-tier and failed assets")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            connection.rollback()
            raise


if __name__ == '__main__':
    migrate_database()

