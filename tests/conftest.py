"""
Pytest Configuration and Fixtures
Shared test configuration for all test modules
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app_refactored import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return flask_app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_names():
    """Sample names for testing"""
    return [
        {'name': 'John Smith', 'outcome': 75},
        {'name': 'Tank Destroyer', 'outcome': 90},
        {'name': 'Emily Rose', 'outcome': 60},
        {'name': 'Blaze Thunder', 'outcome': 85},
        {'name': 'Grace Kelly', 'outcome': 70},
    ]

@pytest.fixture
def sample_linguistic_features():
    """Sample linguistic features"""
    return {
        'syllables': 2,
        'harsh_consonants': True,
        'length': 10,
        'vowel_ratio': 0.4,
        'memorability': 0.8
    }

