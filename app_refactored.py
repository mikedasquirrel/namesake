"""
Nominative Determinism Research Platform - Main Application
Refactored to use Flask Blueprints for modular route organization

Original app.py (9,975 lines, 332 routes) split into focused blueprints
See blueprints/ directory for route implementations
"""

from flask import Flask, render_template, jsonify
from pathlib import Path
from core.config import Config
from core.models import db, Cryptocurrency
from collectors.data_collector import DataCollector
from utils.statistics import StatisticalAnalyzer
from utils.predictor import NamePredictor
from utils.portfolio_optimizer_engine import PortfolioOptimizer
from analyzers.confidence_scorer import ConfidenceScorer
from analyzers.backtester import Backtester
from analyzers.risk_analyzer import RiskAnalyzer
from analyzers.pattern_discovery import PatternDiscovery
from analyzers.breakout_predictor import BreakoutPredictor
from trackers.forward_validator import ForwardValidator
from scanners.opportunity_finder import OpportunityFinder
import logging
import json
import pandas as pd
import numpy as np
import time
import os

# =============================================================================
# CONFIGURATION & UTILITIES
# =============================================================================

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}

def get_cached(key, ttl_seconds=300):
    """Get cached value if not expired - DISABLED FOR NOW TO PREVENT STALE DATA"""
    return None  # Cache disabled

def set_cached(key, value):
    """Set cache value with timestamp"""
    _cache[key] = value
    _cache_timestamps[key] = time.time()
    return value

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif pd.isna(obj):
            return None
        return super(NumpyEncoder, self).default(obj)

def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    return obj

# =============================================================================
# FLASK APPLICATION INITIALIZATION
# =============================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Set custom JSON encoder
try:
    app.json_encoder = NumpyEncoder
except AttributeError:
    # Flask 2.2+ uses json_provider_class
    from flask.json.provider import DefaultJSONProvider
    
    class NumpyJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif pd.isna(obj):
                return None
            return super().default(obj)
    
    app.json = NumpyJSONProvider(app)

# Initialize database
db.init_app(app)

# Initialize services
data_collector = DataCollector()
stats_analyzer = StatisticalAnalyzer()
name_predictor = NamePredictor()
confidence_scorer = ConfidenceScorer()
backtester = Backtester()
risk_analyzer = RiskAnalyzer()
portfolio_optimizer = PortfolioOptimizer()
pattern_discovery = PatternDiscovery()
breakout_predictor = BreakoutPredictor()
forward_validator = ForwardValidator()
opportunity_finder = OpportunityFinder()

# =============================================================================
# DATABASE SETUP
# =============================================================================

with app.app_context():
    db.create_all()
    logger.info("Database initialized")
    
    # Auto-populate if database is empty (optional - can be disabled)
    skip_populate = os.getenv('SKIP_AUTO_POPULATE', '').lower() in ('true', '1', 'yes')
    
    if not skip_populate:
        crypto_count = Cryptocurrency.query.count()
        if crypto_count < 100:
            logger.info(f"Database has only {crypto_count} cryptocurrencies")
            logger.info("AUTO-POPULATING DATABASE WITH 500 CRYPTOCURRENCIES...")
            logger.info("This will take 10-15 minutes. Please wait...")
            logger.info("="*60)
            
            try:
                stats = data_collector.collect_all_data(500)
                total = stats['cryptocurrencies_added'] + stats['cryptocurrencies_updated']
                
                logger.info("="*60)
                logger.info(f"✅ DATABASE POPULATED: {total} cryptocurrencies")
                logger.info(f"   Name analyses: {stats['name_analyses_added']}")
                logger.info(f"   Price records: {stats['price_histories_added']}")
                logger.info("="*60)
            except Exception as e:
                logger.error(f"Auto-population failed: {e}")
                logger.error("You can manually run data collection scripts")
        else:
            logger.info(f"Database ready: {crypto_count} cryptocurrencies")

# =============================================================================
# BLUEPRINT REGISTRATION
# =============================================================================

from blueprints import (
    core_bp,
    betting_bp,
    sports_bp,
    markets_bp,
    natural_events_bp,
    research_bp,
    api_betting_bp,
    api_sports_bp
)

# Register all blueprints
app.register_blueprint(core_bp)
app.register_blueprint(betting_bp)
app.register_blueprint(sports_bp)
app.register_blueprint(markets_bp)
app.register_blueprint(natural_events_bp)
app.register_blueprint(research_bp)
app.register_blueprint(api_betting_bp)
app.register_blueprint(api_sports_bp)

logger.info("✓ All blueprints registered")
logger.info("  - Core pages (/, /analysis, etc.)")
logger.info("  - Betting (/betting/*)")
logger.info("  - Sports (/sports/*)")
logger.info("  - Markets (/crypto, /mtg, /board-games)")
logger.info("  - Natural Events (/hurricanes, /earthquakes)")
logger.info("  - Research (various research domains)")
logger.info("  - API: Betting (/api/betting/*)")
logger.info("  - API: Sports (/api/sports-meta/*)")

# =============================================================================
# BACKWARD COMPATIBILITY ROUTES
# =============================================================================
# These maintain URL compatibility with the old app.py structure

@app.route('/sports-betting')
def sports_betting_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('betting.sports_betting_dashboard'))

@app.route('/live-betting')
def live_betting_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('betting.live_betting_dashboard'))

@app.route('/betting-performance')
def betting_performance_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('betting.betting_performance'))

@app.route('/portfolio-history')
def portfolio_history_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('betting.portfolio_history'))

@app.route('/nba')
def nba_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('sports.nba_page'))

@app.route('/nfl')
def nfl_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('sports.nfl_page'))

@app.route('/mlb')
def mlb_redirect():
    """Redirect old URL to new blueprint URL"""
    from flask import redirect, url_for
    return redirect(url_for('sports.mlb_page'))

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return render_template('500.html'), 500

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    port = 5000
    if '--port' in sys.argv:
        port_idx = sys.argv.index('--port') + 1
        if port_idx < len(sys.argv):
            port = int(sys.argv[port_idx])
    
    logger.info("="*80)
    logger.info("NOMINATIVE DETERMINISM RESEARCH PLATFORM")
    logger.info("="*80)
    logger.info(f"Starting Flask application on http://localhost:{port}")
    logger.info("Press Ctrl+C to quit")
    logger.info("")
    logger.info("Key URLs:")
    logger.info(f"  • Home:          http://localhost:{port}/")
    logger.info(f"  • Live Betting:  http://localhost:{port}/betting/live")
    logger.info(f"  • Sports:        http://localhost:{port}/sports/meta-analysis")
    logger.info(f"  • API Docs:      See AUDIT_REPORT.json for endpoint list")
    logger.info("="*80)
    logger.info("")
    
    app.run(debug=True, host='0.0.0.0', port=port)

