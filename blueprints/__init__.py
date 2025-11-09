"""
Flask Blueprints for Modular Route Organization
Each blueprint handles a specific domain or feature set
"""

from .core import core_bp
from .betting import betting_bp
from .sports import sports_bp
from .markets import markets_bp
from .natural_events import natural_events_bp
from .research import research_bp
from .api_betting import api_betting_bp
from .api_sports import api_sports_bp

__all__ = [
    'core_bp',
    'betting_bp',
    'sports_bp',
    'markets_bp',
    'natural_events_bp',
    'research_bp',
    'api_betting_bp',
    'api_sports_bp',
]

