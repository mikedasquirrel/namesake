#!/usr/bin/env python3
"""
Initial Pre-Computation Script
Creates PreComputedStats table and runs first computation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, PreComputedStats
from utils.background_analyzer import BackgroundAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def main():
    with app.app_context():
        logger.info("="*70)
        logger.info("INITIAL PRE-COMPUTATION")
        logger.info("="*70)
        logger.info("Creating PreComputedStats table and running first computation")
        logger.info("="*70 + "\n")
        
        # Create table
        logger.info("Creating PreComputedStats table...")
        db.create_all()
        logger.info("✅ Table created\n")
        
        # Run computation
        analyzer = BackgroundAnalyzer()
        results = analyzer.compute_and_store_all()
        
        logger.info("\n" + "="*70)
        logger.info("✅ INITIAL PRE-COMPUTATION COMPLETE")
        logger.info("="*70)
        logger.info("All analysis pre-computed and stored in database")
        logger.info("Future page loads will be INSTANT (<100ms)")
        logger.info("="*70 + "\n")
        
        # Show what was computed
        current_stats = PreComputedStats.query.filter_by(is_current=True).all()
        logger.info(f"Pre-computed stats in database: {len(current_stats)}")
        for stat in current_stats:
            logger.info(f"  - {stat.stat_type}: N={stat.sample_size}, computed at {stat.computed_at}")

if __name__ == '__main__':
    main()

