"""
Error Handler - Comprehensive Error Management for Formula Engine

Provides custom exceptions, decorators, and utilities for graceful error handling
across all formula engine operations.
"""

import logging
from functools import wraps
from flask import jsonify
from typing import Any, Dict, Optional, Callable
import traceback

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exception Classes
# ============================================================================

class FormulaEngineError(Exception):
    """Base exception for all formula engine errors"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(FormulaEngineError):
    """Invalid input or parameters"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class ConvergenceError(FormulaEngineError):
    """Evolution failed to converge"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "CONVERGENCE_ERROR", details)


class DataError(FormulaEngineError):
    """Insufficient or invalid data"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "DATA_ERROR", details)


class TransformationError(FormulaEngineError):
    """Error during name transformation"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "TRANSFORMATION_ERROR", details)


class CacheError(FormulaEngineError):
    """Cache operation failed"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "CACHE_ERROR", details)


class JobQueueError(FormulaEngineError):
    """Job queue operation failed"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "JOB_QUEUE_ERROR", details)


# ============================================================================
# Error Response Builders
# ============================================================================

def error_response(error: Exception, status_code: int = 500) -> tuple:
    """Build standardized error response"""
    
    if isinstance(error, FormulaEngineError):
        response = {
            'status': 'error',
            'error_code': error.code,
            'message': error.message,
            'details': error.details
        }
        
        # Suggest recovery based on error type
        if isinstance(error, ValidationError):
            response['suggestion'] = "Check your input parameters and try again"
            status_code = 400
        elif isinstance(error, DataError):
            response['suggestion'] = "Ensure sufficient data is available for analysis"
            status_code = 422
        elif isinstance(error, ConvergenceError):
            response['suggestion'] = "Try increasing population size or generations"
            status_code = 422
        else:
            response['suggestion'] = "Contact support if issue persists"
    else:
        # Unexpected error
        response = {
            'status': 'error',
            'error_code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred',
            'details': {'error_type': type(error).__name__}
        }
        response['suggestion'] = "Please try again or contact support"
    
    return jsonify(response), status_code


def default_response(error: Exception, default_value: Any = None) -> Dict:
    """Return default response when error occurs"""
    logger.warning(f"Using default response due to error: {error}")
    
    return {
        'status': 'partial_success',
        'message': 'Operation completed with fallback values',
        'data': default_value,
        'warning': str(error)
    }


# ============================================================================
# Decorators
# ============================================================================

def handle_formula_errors(default_value: Any = None, reraise: bool = False):
    """
    Decorator for graceful error handling in formula operations
    
    Args:
        default_value: Value to return on error (if not reraising)
        reraise: Whether to reraise the exception after logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except ValidationError as e:
                logger.warning(f"Validation error in {func.__name__}: {e.message}", 
                             extra={'details': e.details})
                if reraise:
                    raise
                return default_response(e, default_value)
            
            except DataError as e:
                logger.warning(f"Data error in {func.__name__}: {e.message}",
                             extra={'details': e.details})
                if reraise:
                    raise
                return default_response(e, default_value)
            
            except ConvergenceError as e:
                logger.warning(f"Convergence error in {func.__name__}: {e.message}",
                             extra={'details': e.details})
                if reraise:
                    raise
                return default_response(e, default_value)
            
            except FormulaEngineError as e:
                logger.error(f"Formula engine error in {func.__name__}: {e.message}",
                           extra={'details': e.details})
                if reraise:
                    raise
                return default_response(e, default_value)
            
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", 
                           exc_info=True)
                if reraise:
                    raise
                return default_response(e, default_value)
        
        return wrapper
    return decorator


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator specifically for Flask API routes
    Returns proper HTTP responses with error codes
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except ValidationError as e:
            logger.warning(f"API validation error: {e.message}")
            return error_response(e, 400)
        
        except DataError as e:
            logger.warning(f"API data error: {e.message}")
            return error_response(e, 422)
        
        except ConvergenceError as e:
            logger.warning(f"API convergence error: {e.message}")
            return error_response(e, 422)
        
        except FormulaEngineError as e:
            logger.error(f"API formula error: {e.message}")
            return error_response(e, 500)
        
        except Exception as e:
            logger.error(f"API unexpected error: {str(e)}", exc_info=True)
            return error_response(e, 500)
    
    return wrapper


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_formula_id(formula_id: str) -> None:
    """Validate formula ID"""
    valid_formulas = ['phonetic', 'semantic', 'structural', 'frequency', 'numerological', 'hybrid']
    
    if not formula_id:
        raise ValidationError("Formula ID is required", 
                            {'valid_options': valid_formulas})
    
    if formula_id not in valid_formulas:
        raise ValidationError(f"Invalid formula ID: {formula_id}",
                            {'provided': formula_id, 'valid_options': valid_formulas})


def validate_domain_list(domains: list) -> None:
    """Validate domain list"""
    valid_domains = ['crypto', 'election', 'ship', 'board_game', 'mlb_player']
    
    if not domains:
        raise ValidationError("At least one domain is required",
                            {'valid_options': valid_domains})
    
    for domain in domains:
        if domain not in valid_domains:
            raise ValidationError(f"Invalid domain: {domain}",
                                {'provided': domain, 'valid_options': valid_domains})


def validate_positive_integer(value: Any, name: str, max_value: Optional[int] = None) -> None:
    """Validate positive integer parameter"""
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{name} must be an integer",
                            {'provided': value, 'type': type(value).__name__})
    
    if int_value <= 0:
        raise ValidationError(f"{name} must be positive",
                            {'provided': int_value, 'minimum': 1})
    
    if max_value and int_value > max_value:
        raise ValidationError(f"{name} exceeds maximum",
                            {'provided': int_value, 'maximum': max_value})


def validate_name_input(name: str) -> None:
    """Validate name input"""
    if not name:
        raise ValidationError("Name is required")
    
    if not isinstance(name, str):
        raise ValidationError("Name must be a string",
                            {'provided_type': type(name).__name__})
    
    if len(name) > 200:
        raise ValidationError("Name too long",
                            {'length': len(name), 'maximum': 200})
    
    # Check for reasonable characters
    if not any(c.isalnum() for c in name):
        raise ValidationError("Name must contain at least one alphanumeric character")


def validate_evolution_params(population_size: int, n_generations: int, mutation_rate: float) -> None:
    """Validate evolution parameters"""
    validate_positive_integer(population_size, "population_size", max_value=1000)
    validate_positive_integer(n_generations, "n_generations", max_value=500)
    
    try:
        rate = float(mutation_rate)
    except (TypeError, ValueError):
        raise ValidationError("mutation_rate must be a number",
                            {'provided': mutation_rate})
    
    if not 0.0 < rate < 1.0:
        raise ValidationError("mutation_rate must be between 0 and 1",
                            {'provided': rate, 'valid_range': '0.0 < rate < 1.0'})


# ============================================================================
# Retry Logic
# ============================================================================

def retry_on_error(max_attempts: int = 3, delay: float = 1.0, 
                   backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on specific exceptions
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                                     f"Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            # All attempts failed
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# Context Managers
# ============================================================================

class error_context:
    """Context manager for enhanced error reporting"""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
    
    def __enter__(self):
        logger.debug(f"Starting operation: {self.operation}", extra={'context': self.context})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Error in operation '{self.operation}': {exc_val}",
                       extra={'context': self.context},
                       exc_info=True)
            # Don't suppress exception
            return False
        
        logger.debug(f"Completed operation: {self.operation}")
        return False


# ============================================================================
# Error Recovery Strategies
# ============================================================================

class ErrorRecovery:
    """Utilities for recovering from errors"""
    
    @staticmethod
    def get_cached_or_default(cache_key: str, default_generator: Callable, 
                             cache_client=None) -> Any:
        """Try to get from cache, fall back to generating default"""
        if cache_client:
            try:
                cached = cache_client.get(cache_key)
                if cached:
                    logger.info(f"Using cached value for recovery: {cache_key}")
                    return cached
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")
        
        # Generate default
        try:
            return default_generator()
        except Exception as e:
            logger.error(f"Default generator failed: {e}")
            return None
    
    @staticmethod
    def partial_results(func: Callable, items: list, **kwargs) -> tuple:
        """
        Process items individually, collecting successes and failures
        
        Returns:
            (successes, failures) tuple
        """
        successes = []
        failures = []
        
        for item in items:
            try:
                result = func(item, **kwargs)
                successes.append((item, result))
            except Exception as e:
                logger.warning(f"Failed to process {item}: {e}")
                failures.append((item, str(e)))
        
        return successes, failures

