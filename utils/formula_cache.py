"""
Formula Cache - Redis-based Caching System

Caches expensive operations like transformations, validations, and evolution results
with intelligent TTL management and cache invalidation strategies.
"""

import json
import hashlib
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

# Graceful degradation if Redis not available
try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - caching disabled")


class FormulaCache:
    """Redis-based caching for formula engine operations"""
    
    # Cache TTLs (seconds)
    TTL_TRANSFORMATION = 3600        # 1 hour
    TTL_VALIDATION = 86400           # 24 hours
    TTL_EVOLUTION = 604800           # 7 days
    TTL_STATISTICS = 86400           # 24 hours
    TTL_CONVERGENCE = 604800         # 7 days
    TTL_ENCRYPTION = 86400           # 24 hours
    
    def __init__(self, host='localhost', port=6379, db=0, enabled=True):
        """
        Initialize cache
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            enabled: Whether caching is enabled
        """
        self.enabled = enabled and REDIS_AVAILABLE
        self.redis_client = None
        
        if self.enabled:
            try:
                self.redis_client = Redis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1
                )
                # Test connection
                self.redis_client.ping()
                logger.info(f"Formula cache connected to Redis at {host}:{port}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None
    
    def _make_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        # Create stable hash from arguments
        key_parts = [str(arg) for arg in args]
        key_string = "|".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
        return f"formula:{prefix}:{key_hash}"
    
    def _serialize(self, data: Any) -> str:
        """Serialize data for storage"""
        return json.dumps(data, default=str)
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize data from storage"""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    
    # ========================================================================
    # Transformation Caching
    # ========================================================================
    
    def get_transformation(self, name: str, formula_id: str) -> Optional[Dict]:
        """Get cached transformation result"""
        if not self.enabled:
            return None
        
        key = self._make_key("transform", name, formula_id)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: transformation {name} with {formula_id}")
                return self._deserialize(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def set_transformation(self, name: str, formula_id: str, encoding: Dict) -> bool:
        """Cache transformation result"""
        if not self.enabled:
            return False
        
        key = self._make_key("transform", name, formula_id)
        
        try:
            serialized = self._serialize(encoding)
            self.redis_client.setex(key, self.TTL_TRANSFORMATION, serialized)
            logger.debug(f"Cached transformation: {name} with {formula_id}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    def get_all_transformations(self, name: str) -> Optional[Dict[str, Dict]]:
        """Get all formula transformations for a name"""
        if not self.enabled:
            return None
        
        key = self._make_key("transform_all", name)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: all transformations for {name}")
                return self._deserialize(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def set_all_transformations(self, name: str, encodings: Dict[str, Dict]) -> bool:
        """Cache all formula transformations for a name"""
        if not self.enabled:
            return False
        
        key = self._make_key("transform_all", name)
        
        try:
            serialized = self._serialize(encodings)
            self.redis_client.setex(key, self.TTL_TRANSFORMATION, serialized)
            logger.debug(f"Cached all transformations: {name}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    # ========================================================================
    # Validation Caching
    # ========================================================================
    
    def get_validation(self, formula_id: str, domains: List[str], limit: int) -> Optional[Dict]:
        """Get cached validation report"""
        if not self.enabled:
            return None
        
        domains_str = ",".join(sorted(domains))
        key = self._make_key("validate", formula_id, domains_str, limit)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: validation {formula_id}")
                return self._deserialize(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def set_validation(self, formula_id: str, domains: List[str], limit: int, 
                      report: Dict) -> bool:
        """Cache validation report"""
        if not self.enabled:
            return False
        
        domains_str = ",".join(sorted(domains))
        key = self._make_key("validate", formula_id, domains_str, limit)
        
        try:
            serialized = self._serialize(report)
            self.redis_client.setex(key, self.TTL_VALIDATION, serialized)
            logger.debug(f"Cached validation: {formula_id}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    # ========================================================================
    # Evolution Caching
    # ========================================================================
    
    def get_evolution(self, formula_type: str, params_hash: str) -> Optional[Dict]:
        """Get cached evolution result"""
        if not self.enabled:
            return None
        
        key = self._make_key("evolution", formula_type, params_hash)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: evolution {formula_type}")
                return self._deserialize(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def set_evolution(self, formula_type: str, params_hash: str, 
                     history: Dict) -> bool:
        """Cache evolution result (long TTL - expensive operation)"""
        if not self.enabled:
            return False
        
        key = self._make_key("evolution", formula_type, params_hash)
        
        try:
            serialized = self._serialize(history)
            self.redis_client.setex(key, self.TTL_EVOLUTION, serialized)
            logger.debug(f"Cached evolution: {formula_type}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    # ========================================================================
    # Statistics Caching
    # ========================================================================
    
    def get_statistics(self, stat_type: str, *identifiers) -> Optional[Dict]:
        """Get cached statistics"""
        if not self.enabled:
            return None
        
        key = self._make_key("stats", stat_type, *identifiers)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: statistics {stat_type}")
                return self._deserialize(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def set_statistics(self, stat_type: str, data: Dict, *identifiers) -> bool:
        """Cache statistics"""
        if not self.enabled:
            return False
        
        key = self._make_key("stats", stat_type, *identifiers)
        
        try:
            serialized = self._serialize(data)
            self.redis_client.setex(key, self.TTL_STATISTICS, serialized)
            logger.debug(f"Cached statistics: {stat_type}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    # ========================================================================
    # Convergence Analysis Caching
    # ========================================================================
    
    def get_convergence(self, formula_type: str, version: str) -> Optional[Dict]:
        """Get cached convergence analysis"""
        if not self.enabled:
            return None
        
        key = self._make_key("convergence", formula_type, version)
        
        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug(f"Cache hit: convergence {formula_type}")
                return self._deserialize(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def set_convergence(self, formula_type: str, version: str, 
                       signature: Dict) -> bool:
        """Cache convergence analysis"""
        if not self.enabled:
            return False
        
        key = self._make_key("convergence", formula_type, version)
        
        try:
            serialized = self._serialize(signature)
            self.redis_client.setex(key, self.TTL_CONVERGENCE, serialized)
            logger.debug(f"Cached convergence: {formula_type}")
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    # ========================================================================
    # Cache Management
    # ========================================================================
    
    def invalidate_formula(self, formula_id: str) -> int:
        """Invalidate all cache entries for a formula"""
        if not self.enabled:
            return 0
        
        pattern = f"formula:*:{formula_id}:*"
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries for {formula_id}")
                return deleted
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
        
        return 0
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        if not self.enabled:
            return 0
        
        full_pattern = f"formula:{pattern}"
        
        try:
            keys = self.redis_client.keys(full_pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries matching {pattern}")
                return deleted
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
        
        return 0
    
    def clear_all(self) -> bool:
        """Clear all formula cache entries"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys("formula:*")
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
            return True
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.enabled:
            return {'enabled': False}
        
        try:
            info = self.redis_client.info()
            keys = self.redis_client.keys("formula:*")
            
            return {
                'enabled': True,
                'connected': True,
                'total_keys': len(keys),
                'used_memory': info.get('used_memory_human', 'unknown'),
                'hit_rate': 'N/A',  # Would need tracking
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Cache stats failed: {e}")
            return {'enabled': True, 'connected': False, 'error': str(e)}
    
    # ========================================================================
    # Decorator for Automatic Caching
    # ========================================================================
    
    def cached(self, ttl: int = 3600, key_prefix: str = "func"):
        """
        Decorator for automatic function result caching
        
        Usage:
            @cache.cached(ttl=3600, key_prefix="my_func")
            def expensive_function(arg1, arg2):
                ...
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                # Generate cache key from function name and arguments
                key = self._make_key(key_prefix, func.__name__, *args, 
                                    *[f"{k}={v}" for k, v in sorted(kwargs.items())])
                
                # Try to get from cache
                try:
                    cached = self.redis_client.get(key)
                    if cached:
                        logger.debug(f"Cache hit: {func.__name__}")
                        return self._deserialize(cached)
                except Exception as e:
                    logger.warning(f"Cache get failed: {e}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                try:
                    serialized = self._serialize(result)
                    self.redis_client.setex(key, ttl, serialized)
                    logger.debug(f"Cached result: {func.__name__}")
                except Exception as e:
                    logger.warning(f"Cache set failed: {e}")
                
                return result
            
            return wrapper
        return decorator


# ============================================================================
# Global Cache Instance
# ============================================================================

# Initialize with environment variables or defaults
import os

cache = FormulaCache(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
)


# ============================================================================
# Cache Warming Functions
# ============================================================================

def warm_transformation_cache(names: List[str], formula_ids: List[str]):
    """Pre-populate cache with common transformations"""
    from utils.formula_engine import FormulaEngine
    from analyzers.name_analyzer import NameAnalyzer
    
    logger.info(f"Warming cache for {len(names)} names x {len(formula_ids)} formulas")
    
    engine = FormulaEngine()
    analyzer = NameAnalyzer()
    
    warmed = 0
    for name in names:
        try:
            features = analyzer.analyze_name(name)
            for formula_id in formula_ids:
                encoding = engine.transform(name, features, formula_id)
                cache.set_transformation(name, formula_id, encoding.to_dict())
                warmed += 1
        except Exception as e:
            logger.warning(f"Cache warming failed for {name}: {e}")
    
    logger.info(f"Warmed {warmed} cache entries")
    return warmed


def warm_validation_cache(formula_ids: List[str], domains: List[str]):
    """Pre-populate cache with validation results"""
    from analyzers.formula_validator import FormulaValidator
    from core.unified_domain_model import DomainType
    
    logger.info(f"Warming validation cache for {len(formula_ids)} formulas")
    
    validator = FormulaValidator()
    
    for formula_id in formula_ids:
        try:
            domain_types = [DomainType(d) for d in domains]
            report = validator.validate_formula(formula_id, domain_types, limit_per_domain=100)
            cache.set_validation(formula_id, domains, 100, report.to_dict())
        except Exception as e:
            logger.warning(f"Cache warming failed for {formula_id}: {e}")
    
    logger.info("Validation cache warmed")

