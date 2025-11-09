"""
Natural Events Blueprint - Hurricanes, Earthquakes
"""

from flask import Blueprint, render_template

natural_events_bp = Blueprint('natural_events', __name__)


@natural_events_bp.route('/hurricanes')
def hurricanes_page():
    """Hurricane nomenclature research"""
    return render_template('hurricanes.html')


@natural_events_bp.route('/hurricanes/demographics')
def hurricane_demographics_page():
    """Hurricane Demographics - Impact by location and name"""
    return render_template('hurricane_demographics.html')


@natural_events_bp.route('/earthquakes')
def earthquakes_page():
    """Earthquake nomenclature research"""
    return render_template('earthquakes.html')


@natural_events_bp.route('/2026-predictions')
def predictions_2026():
    """2026 Hurricane Predictions - Pre-registered temporal precedence test"""
    return render_template('predictions_2026.html')

