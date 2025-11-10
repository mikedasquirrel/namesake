"""
Experiment Framework for Narrative Optimization

Provides tools for running experiments, evaluating models,
and testing hypotheses systematically.
"""

from .evaluation import NarrativeEvaluator
from .hypothesis_tests import HypothesisTest

__all__ = ['NarrativeEvaluator', 'HypothesisTest']

