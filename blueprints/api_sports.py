"""
API Sports Blueprint - All sports-related API endpoints
Handles /api/sports-meta/* and other sports APIs
"""

from flask import Blueprint, request, jsonify
import json
import logging

logger = logging.getLogger(__name__)

api_sports_bp = Blueprint('api_sports', __name__, url_prefix='/api')


@api_sports_bp.route('/sports-meta/characteristics')
def get_sport_characteristics():
    """API: Get sport characteristic data"""
    try:
        with open('analysis_outputs/sports_meta_analysis/sport_characteristics.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'error': 'Sport characteristics data not found'}), 404
    except Exception as e:
        logger.error(f"Error loading sport characteristics: {e}")
        return jsonify({'error': str(e)}), 500


@api_sports_bp.route('/sports-meta/analysis/<sport>')
def get_sport_analysis(sport):
    """API: Get analysis for specific sport"""
    try:
        with open(f'analysis_outputs/sports_meta_analysis/{sport}_analysis.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'error': f'Analysis for {sport} not found'}), 404
    except Exception as e:
        logger.error(f"Error loading {sport} analysis: {e}")
        return jsonify({'error': str(e)}), 500


@api_sports_bp.route('/sports-meta/meta-results')
def get_meta_results():
    """API: Get cross-sport meta-analysis results"""
    try:
        with open('analysis_outputs/sports_meta_analysis/meta_regression_results.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'error': 'Meta-analysis results not found'}), 404
    except Exception as e:
        logger.error(f"Error loading meta-analysis results: {e}")
        return jsonify({'error': str(e)}), 500


@api_sports_bp.route('/sports-meta/predict', methods=['POST'])
def predict_sport_success():
    """API: Predict success for a name in a specific sport"""
    try:
        data = request.get_json()
        name = data.get('name')
        sport = data.get('sport')
        
        if not name or not sport:
            return jsonify({'error': 'Name and sport required'}), 400
        
        # Simple prediction logic (can be enhanced)
        syllables = len(name.split()) * 2  # Rough estimate
        has_harsh = any(c in name.lower() for c in 'kgptbdxz')
        
        # Load sport characteristics
        try:
            with open('analysis_outputs/sports_meta_analysis/sport_characteristics.json', 'r') as f:
                chars = json.load(f)['sports_characterized'].get(sport, {})
        except:
            chars = {}
        
        # Calculate score
        base_score = 50
        if syllables <= 2:
            base_score += 10
        if has_harsh and chars.get('contact_level', 0) > 6:
            base_score += 15
        
        return jsonify({
            'name': name,
            'sport': sport,
            'predicted_success_score': min(100, max(0, base_score)),
            'factors': {
                'syllable_count': syllables,
                'has_harsh_sounds': has_harsh,
                'sport_contact_level': chars.get('contact_level', 0)
            }
        })
    except Exception as e:
        logger.error(f"Error predicting sport success: {e}")
        return jsonify({'error': str(e)}), 500

