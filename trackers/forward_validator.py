"""
Forward Prediction Validator
Tracks predictions made BEFORE outcomes are known
Proves theory works prospectively, not just in hindsight
"""

from core.models import db, ForwardPrediction, Cryptocurrency, Domain
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class ForwardValidator:
    """Track and validate forward predictions"""
    
    def make_crypto_prediction(self, crypto_id, prediction_type='will_reach_top_100', months_ahead=3):
        """
        Make a locked prediction about a cryptocurrency
        
        Args:
            crypto_id: Cryptocurrency ID
            prediction_type: Type of prediction
            months_ahead: How many months to check
        
        Returns: Prediction record
        """
        try:
            crypto = Cryptocurrency.query.get(crypto_id)
            if not crypto:
                return None
            
            # Get current baseline
            baseline_rank = crypto.rank or 999
            baseline_price = crypto.current_price or 0
            baseline_mcap = crypto.market_cap or 0
            
            # Calculate name score
            from analyzers.confidence_scorer import ConfidenceScorer
            scorer = ConfidenceScorer()
            score_data = scorer.score_cryptocurrency(crypto_id)
            
            # Create prediction
            prediction = ForwardPrediction(
                asset_type='crypto',
                asset_id=crypto_id,
                asset_name=crypto.name,
                prediction_type=prediction_type,
                predicted_outcome=json.dumps({
                    'will_reach_top_100': prediction_type == 'will_reach_top_100',
                    'expected_rank': 'top 100' if baseline_rank > 100 else 'maintain/improve',
                    'reasoning': f"High name score ({score_data['score']:.1f}) suggests market recognition"
                }),
                confidence_score=score_data['score'] if score_data else 50,
                baseline_rank=baseline_rank,
                baseline_price=baseline_price,
                baseline_market_cap=baseline_mcap,
                prediction_date=datetime.utcnow(),
                check_date=datetime.utcnow() + timedelta(days=30*months_ahead),
                is_locked=True,
                name_score=score_data['score'] if score_data else 50,
                pattern_matches=json.dumps(score_data.get('breakdown', {}) if score_data else {})
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            logger.info(f"✅ Forward prediction locked: {crypto.name} - {prediction_type}")
            
            return prediction.to_dict()
        
        except Exception as e:
            logger.error(f"Prediction creation error: {e}")
            db.session.rollback()
            return None
    
    def check_prediction(self, prediction_id):
        """
        Check if a prediction was correct (after check_date)
        
        Args:
            prediction_id: ID of prediction to check
        
        Returns: Updated prediction with outcome
        """
        try:
            prediction = ForwardPrediction.query.get(prediction_id)
            if not prediction:
                return None
            
            # Can only check after check_date
            if datetime.utcnow() < prediction.check_date:
                return {'error': 'Too early to check - wait until check_date'}
            
            if prediction.is_resolved:
                return prediction.to_dict()  # Already checked
            
            # Get current state of asset
            if prediction.asset_type == 'crypto':
                crypto = Cryptocurrency.query.get(prediction.asset_id)
                if not crypto:
                    return None
                
                current_rank = crypto.rank or 999
                current_price = crypto.current_price or 0
                
                # Check if prediction was correct
                predicted = json.loads(prediction.predicted_outcome)
                
                if prediction.prediction_type == 'will_reach_top_100':
                    is_correct = current_rank <= 100
                    actual_outcome = {
                        'reached_top_100': is_correct,
                        'final_rank': current_rank,
                        'rank_change': prediction.baseline_rank - current_rank,
                        'price_change_pct': ((current_price - prediction.baseline_price) / prediction.baseline_price * 100) if prediction.baseline_price > 0 else 0
                    }
                else:
                    is_correct = False  # Default
                    actual_outcome = {'status': 'unknown prediction type'}
                
                # Update prediction with outcome
                prediction.actual_outcome = json.dumps(actual_outcome)
                prediction.outcome_date = datetime.utcnow()
                prediction.is_correct = is_correct
                prediction.is_resolved = True
                
                db.session.commit()
                
                logger.info(f"Prediction resolved: {prediction.asset_name} - {'CORRECT' if is_correct else 'INCORRECT'}")
                
                return prediction.to_dict()
        
        except Exception as e:
            logger.error(f"Prediction check error: {e}")
            return None
    
    def get_accuracy_report(self):
        """
        Get overall accuracy of forward predictions
        
        Returns: dict with accuracy metrics
        """
        try:
            all_predictions = ForwardPrediction.query.all()
            resolved = [p for p in all_predictions if p.is_resolved]
            pending = [p for p in all_predictions if not p.is_resolved]
            
            if not resolved:
                return {
                    'total_predictions': len(all_predictions),
                    'resolved': 0,
                    'pending': len(pending),
                    'accuracy': 0,
                    'message': 'No resolved predictions yet'
                }
            
            correct = sum(1 for p in resolved if p.is_correct)
            accuracy = (correct / len(resolved) * 100) if resolved else 0
            
            return {
                'total_predictions': len(all_predictions),
                'resolved': len(resolved),
                'pending': len(pending),
                'correct': correct,
                'incorrect': len(resolved) - correct,
                'accuracy_percent': round(accuracy, 2),
                'predictions': [p.to_dict() for p in all_predictions]
            }
        
        except Exception as e:
            logger.error(f"Accuracy report error: {e}")
            return {'error': str(e)}
    
    def make_batch_predictions(self, crypto_ids, prediction_type='will_reach_top_100'):
        """
        Make predictions on multiple assets at once
        
        Args:
            crypto_ids: List of cryptocurrency IDs
            prediction_type: Type of prediction to make
        
        Returns: List of created predictions
        """
        predictions = []
        
        for crypto_id in crypto_ids:
            pred = self.make_crypto_prediction(crypto_id, prediction_type)
            if pred:
                predictions.append(pred)
        
        logger.info(f"Created {len(predictions)} forward predictions")
        
        return predictions

