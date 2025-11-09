"""
Sports Blueprint - Sports research pages (NBA, NFL, MLB, etc.)
"""

from flask import Blueprint, render_template
import logging

logger = logging.getLogger(__name__)

sports_bp = Blueprint('sports', __name__, url_prefix='/sports')


@sports_bp.route('/meta-analysis')
def sports_meta_analysis():
    """Sports Meta-Analysis - Cross-sport linguistic pattern analysis"""
    return render_template('sports_meta_analysis.html')


@sports_bp.route('/nba')
def nba_page():
    """NBA research findings"""
    return render_template('nba.html')


@sports_bp.route('/nba/findings')
def nba_findings():
    """NBA player names research findings"""
    return render_template('nba_findings.html')


@sports_bp.route('/nfl')
def nfl_page():
    """NFL research findings"""
    return render_template('nfl.html')


@sports_bp.route('/nfl/findings')
def nfl_findings():
    """NFL player names research findings"""
    return render_template('nfl_findings.html')


@sports_bp.route('/mlb')
def mlb_page():
    """MLB research findings"""
    return render_template('mlb.html')


@sports_bp.route('/mlb/findings')
def mlb_findings():
    """MLB player names research findings"""
    return render_template('mlb_findings.html')


@sports_bp.route('/mlb/teams')
def mlb_teams_page():
    """MLB Teams research findings"""
    return render_template('mlb_teams.html')


@sports_bp.route('/mlb/teams/findings')
def mlb_teams_findings():
    """MLB Teams research findings"""
    return render_template('mlb_teams_findings.html')


@sports_bp.route('/roster-locality')
def sports_roster_locality():
    """Sports Roster Locality - Geographic surname patterns"""
    return render_template('sports_roster_locality.html')

