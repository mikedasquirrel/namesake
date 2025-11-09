"""
Core Blueprint - Homepage and main navigation pages
"""

from flask import Blueprint, render_template

core_bp = Blueprint('core', __name__)


@core_bp.route('/')
def overview():
    """Overview - Executive dashboard"""
    return render_template('overview.html')


@core_bp.route('/analysis')
def analysis():
    """Analysis - Narrative statistical findings"""
    return render_template('analysis.html')


@core_bp.route('/nominative-dashboard')
def nominative_dashboard():
    """Comprehensive nominative determinism and synchronicity dashboard"""
    return render_template('nominative_dashboard.html')


@core_bp.route('/formula')
def formula():
    """The Formula - Cross-sphere mathematical framework"""
    return render_template('formula.html')


@core_bp.route('/the-nail')
def the_nail():
    """The Nail - Living generative research artwork (simple viewer)"""
    return render_template('the_nail.html')


@core_bp.route('/the-word-made-flesh')
def the_word_made_flesh():
    """The Word Made Flesh - Complete philosophical presentation of The Nail"""
    return render_template('the_word_made_flesh.html')


@core_bp.route('/unknown-known')
def unknown_known():
    """The Unknown Known - Philosophical synthesis of nominative findings"""
    return render_template('unknown_known.html')


@core_bp.route('/research-dashboard')
def research_dashboard():
    """Advanced Research Dashboard - Complete nominative traits framework"""
    return render_template('research_dashboard.html')


@core_bp.route('/philosophical-implications')
def philosophical_implications_interactive():
    """Interactive Philosophical Implications"""
    return render_template('philosophical_implications_interactive.html')

