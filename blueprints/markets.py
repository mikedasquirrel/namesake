"""
Markets Blueprint - Cryptocurrency, MTG, Board Games
"""

from flask import Blueprint, render_template

markets_bp = Blueprint('markets', __name__)


@markets_bp.route('/crypto/findings')
def crypto_findings():
    """Cryptocurrency research findings"""
    return render_template('crypto_findings.html')


@markets_bp.route('/mtg')
def mtg_page():
    """Magic: The Gathering card names research"""
    return render_template('mtg.html')


@markets_bp.route('/board-games')
def board_games_page():
    """Board games research findings"""
    return render_template('board_games.html')


@markets_bp.route('/board-games/findings')
def board_games_findings():
    """Board games research findings"""
    return render_template('board_games_findings.html')

