"""
API Betting Blueprint - All betting-related API endpoints
Handles /api/betting/* routes
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

api_betting_bp = Blueprint('api_betting', __name__, url_prefix='/api/betting')


@api_betting_bp.route('/opportunities')
def get_betting_opportunities():
    """API: Get current top betting opportunities across all sports"""
    try:
        from analyzers.sports_betting_analyzer import SportsBettingAnalyzer
        
        analyzer = SportsBettingAnalyzer()
        sport = request.args.get('sport')
        min_score = float(request.args.get('min_score', 60))
        min_confidence = float(request.args.get('min_confidence', 50))
        limit = int(request.args.get('limit', 20))
        
        if sport:
            opportunities = analyzer.identify_opportunities(
                sport, min_score=min_score, min_confidence=min_confidence, limit=limit
            )
        else:
            # Get opportunities from all sports
            all_opportunities = []
            for s in ['football', 'basketball', 'baseball']:
                opps = analyzer.identify_opportunities(
                    s, min_score=min_score, min_confidence=min_confidence, limit=limit
                )
                all_opportunities.extend(opps)
            
            # Sort by edge
            all_opportunities.sort(key=lambda x: abs(x.get('edge', 0)), reverse=True)
            opportunities = all_opportunities[:limit]
        
        return jsonify({
            'total_opportunities': len(opportunities),
            'opportunities': opportunities
        })
    except Exception as e:
        logger.error(f"Error getting betting opportunities: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/opportunities/<sport>')
def get_sport_betting_opportunities(sport):
    """API: Get betting opportunities for specific sport"""
    try:
        from analyzers.sports_betting_analyzer import SportsBettingAnalyzer
        
        analyzer = SportsBettingAnalyzer()
        min_score = float(request.args.get('min_score', 60))
        min_confidence = float(request.args.get('min_confidence', 50))
        limit = int(request.args.get('limit', 20))
        
        opportunities = analyzer.identify_opportunities(
            sport, min_score=min_score, min_confidence=min_confidence, limit=limit
        )
        
        return jsonify({
            'sport': sport,
            'total_opportunities': len(opportunities),
            'opportunities': opportunities
        })
    except Exception as e:
        logger.error(f"Error getting {sport} opportunities: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/analyze-prop', methods=['POST'])
def analyze_prop_bet():
    """API: Analyze specific player prop bet"""
    try:
        from analyzers.player_prop_analyzer import PlayerPropAnalyzer
        
        data = request.get_json()
        
        required_fields = ['player_name', 'sport', 'prop_type', 'linguistic_features', 
                          'baseline_average', 'market_line']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        analyzer = PlayerPropAnalyzer()
        analysis = analyzer.analyze_prop_bet(
            player_name=data['player_name'],
            sport=data['sport'],
            prop_type=data['prop_type'],
            linguistic_features=data['linguistic_features'],
            baseline_average=data['baseline_average'],
            market_line=data['market_line'],
            over_odds=data.get('over_odds', -110),
            under_odds=data.get('under_odds', -110)
        )
        
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error analyzing prop bet: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/performance')
def get_betting_performance():
    """API: Get historical betting performance"""
    try:
        from analyzers.betting_performance_analyzer import BettingPerformanceAnalyzer
        
        analyzer = BettingPerformanceAnalyzer()
        sport = request.args.get('sport')
        market_type = request.args.get('market_type')
        days = request.args.get('days', type=int)
        
        if days:
            performance = analyzer.calculate_recent_performance(days)
        elif sport:
            performance = analyzer.calculate_sport_performance(sport)
        elif market_type:
            performance = analyzer.calculate_market_performance(market_type)
        else:
            performance = analyzer.calculate_overall_performance()
        
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Error getting betting performance: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/bankroll/status')
def get_bankroll_status():
    """API: Get current bankroll status"""
    try:
        from utils.betting_bankroll_manager import BettingBankrollManager
        
        # In production, load from session/database
        # For now, create instance with defaults
        manager = BettingBankrollManager(initial_bankroll=10000)
        status = manager.get_status()
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting bankroll status: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/place-bet', methods=['POST'])
def place_bet():
    """API: Log a placed bet"""
    try:
        from trackers.bet_tracker import BetTracker
        
        data = request.get_json()
        
        required_fields = ['sport', 'bet_type', 'odds', 'stake']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        tracker = BetTracker()
        
        # Get bankroll state (in production, from session/database)
        bankroll_state = {
            'current_bankroll': data.get('current_bankroll', 10000),
            'allocated_capital': data.get('allocated_capital', 0)
        }
        
        bet = tracker.place_bet(data, bankroll_state)
        
        return jsonify({
            'success': True,
            'bet': bet.to_dict()
        })
    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/live-recommendations')
def get_live_recommendations():
    """API: Get live betting recommendations"""
    try:
        from analyzers.realtime_recommendation_engine import RealtimeRecommendationEngine
        
        engine = RealtimeRecommendationEngine()
        sport = request.args.get('sport')
        priority_min = int(request.args.get('priority_min', 3))
        
        recommendations = engine.get_live_recommendations(
            sport=sport, 
            priority_min=priority_min
        )
        
        return jsonify({
            'generated_at': recommendations['generated_at'],
            'total_opportunities': len(recommendations['opportunities']),
            'opportunities': recommendations['opportunities']
        })
    except Exception as e:
        logger.error(f"Error getting live recommendations: {e}")
        return jsonify({'error': str(e)}), 500


@api_betting_bp.route('/portfolio-history')
def get_portfolio_history():
    """API: Get historical portfolio performance by season"""
    try:
        from analyzers.historical_season_analyzer import HistoricalSeasonAnalyzer
        
        analyzer = HistoricalSeasonAnalyzer()
        sport = request.args.get('sport')
        
        if sport:
            history = analyzer.get_sport_history(sport)
        else:
            history = analyzer.get_complete_history()
        
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting portfolio history: {e}")
        return jsonify({'error': str(e)}), 500

