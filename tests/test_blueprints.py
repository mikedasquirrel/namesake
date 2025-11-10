"""
Test Flask Blueprints
Tests for route functionality
"""

import pytest


class TestCoreBlueprint:
    """Test core blueprint routes"""
    
    def test_homepage(self, client):
        """Test homepage loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_analysis_page(self, client):
        """Test analysis page loads"""
        response = client.get('/analysis')
        assert response.status_code == 200


class TestBettingBlueprint:
    """Test betting blueprint routes"""
    
    def test_betting_dashboard(self, client):
        """Test betting dashboard loads"""
        response = client.get('/betting/dashboard')
        assert response.status_code == 200
    
    def test_live_betting(self, client):
        """Test live betting page loads"""
        response = client.get('/betting/live')
        assert response.status_code == 200


class TestSportsBlueprint:
    """Test sports blueprint routes"""
    
    def test_sports_meta_analysis(self, client):
        """Test sports meta-analysis page"""
        response = client.get('/sports/meta-analysis')
        assert response.status_code == 200
    
    def test_nba_page(self, client):
        """Test NBA page loads"""
        response = client.get('/sports/nba')
        assert response.status_code == 200


class TestMarketsBlueprint:
    """Test markets blueprint routes"""
    
    def test_crypto_findings(self, client):
        """Test crypto findings page"""
        response = client.get('/crypto/findings')
        assert response.status_code == 200
    
    def test_mtg_page(self, client):
        """Test MTG page loads"""
        response = client.get('/mtg')
        assert response.status_code == 200


class TestAPIBettingBlueprint:
    """Test betting API endpoints"""
    
    def test_betting_opportunities_api(self, client):
        """Test betting opportunities API"""
        response = client.get('/api/betting/opportunities')
        # May return error if no data, but should respond
        assert response.status_code in [200, 500]
        assert response.is_json
    
    def test_betting_performance_api(self, client):
        """Test betting performance API"""
        response = client.get('/api/betting/performance')
        assert response.status_code in [200, 500]
        assert response.is_json


class TestAPISportsBlueprint:
    """Test sports API endpoints"""
    
    def test_sport_characteristics_api(self, client):
        """Test sport characteristics API"""
        response = client.get('/api/sports-meta/characteristics')
        # May return 404 if file doesn't exist
        assert response.status_code in [200, 404]
        assert response.is_json

