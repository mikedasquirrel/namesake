"""
Betting Blueprint - Sports betting dashboards and interfaces
"""

from flask import Blueprint, render_template

betting_bp = Blueprint('betting', __name__, url_prefix='/betting')


@betting_bp.route('/dashboard')
def sports_betting_dashboard():
    """Sports Betting Dashboard - Main betting opportunities interface"""
    return render_template('sports_betting_dashboard.html')


@betting_bp.route('/live')
def live_betting_dashboard():
    """Live Betting Dashboard - Real-time recommendations"""
    return render_template('live_betting_dashboard.html')


@betting_bp.route('/performance')
def betting_performance():
    """Betting Performance Dashboard"""
    return render_template('betting_performance.html')


@betting_bp.route('/portfolio')
def portfolio_history():
    """Portfolio History - Season-by-season performance"""
    return render_template('portfolio_history.html')

