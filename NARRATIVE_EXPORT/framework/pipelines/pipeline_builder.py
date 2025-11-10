"""
Narrative Pipeline Builder

Constructs sklearn pipelines from configuration specifications.
Handles transformer assembly, parameter setting, and pipeline creation.

Author: Narrative Integration System
Date: November 2025
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import logging

logger = logging.getLogger(__name__)


class NarrativePipelineBuilder:
    """Build narrative analysis pipelines from configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize pipeline builder.
        
        Args:
            config_path: Path to pipeline configuration JSON
        """
        self.config = None
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
    
    def build_pipeline(self, transformer_name: str, 
                      classifier_type: str = 'gradient_boosting',
                      transformer_params: Optional[Dict] = None,
                      classifier_params: Optional[Dict] = None) -> Pipeline:
        """
        Build a single narrative pipeline.
        
        Args:
            transformer_name: Name of transformer to use
            classifier_type: Type of classifier ('gradient_boosting', 'random_forest', 'logistic')
            transformer_params: Parameters for transformer
            classifier_params: Parameters for classifier
        
        Returns:
            Sklearn Pipeline
        """
        logger.info(f"Building pipeline: {transformer_name} + {classifier_type}")
        
        # Import transformers
        from narrative_integration.transformers import (
            NominativeAnalysisTransformer,
            NarrativePotentialTransformer,
            EnsembleNarrativeTransformer,
            RelationalValueTransformer,
            SemanticNarrativeTransformer,
            StatisticalTransformer
        )
        
        # Get transformer
        transformer_map = {
            'nominative': NominativeAnalysisTransformer,
            'potential': NarrativePotentialTransformer,
            'ensemble': EnsembleNarrativeTransformer,
            'relational': RelationalValueTransformer,
            'semantic': SemanticNarrativeTransformer,
            'statistical': StatisticalTransformer
        }
        
        if transformer_name not in transformer_map:
            raise ValueError(f"Unknown transformer: {transformer_name}")
        
        TransformerClass = transformer_map[transformer_name]
        
        # Instantiate transformer with params
        if transformer_params:
            transformer = TransformerClass(**transformer_params)
        else:
            transformer = TransformerClass()
        
        # Get classifier
        classifier = self._get_classifier(classifier_type, classifier_params)
        
        # Build pipeline
        pipeline = Pipeline([
            (transformer_name, transformer),
            ('classifier', classifier)
        ])
        
        logger.info(f"  ✓ Pipeline built: {transformer_name} -> {classifier_type}")
        
        return pipeline
    
    def build_combined_pipeline(self, transformer_names: List[str],
                               classifier_type: str = 'gradient_boosting',
                               transformer_params: Optional[Dict[str, Dict]] = None,
                               classifier_params: Optional[Dict] = None) -> Pipeline:
        """
        Build pipeline combining multiple transformers.
        
        Args:
            transformer_names: List of transformer names to combine
            classifier_type: Type of classifier
            transformer_params: Dict mapping transformer names to their params
            classifier_params: Parameters for classifier
        
        Returns:
            Sklearn Pipeline with FeatureUnion
        """
        from sklearn.pipeline import FeatureUnion
        from narrative_integration.transformers import (
            NominativeAnalysisTransformer,
            NarrativePotentialTransformer,
            EnsembleNarrativeTransformer,
            RelationalValueTransformer,
            SemanticNarrativeTransformer,
            StatisticalTransformer
        )
        
        logger.info(f"Building combined pipeline with {len(transformer_names)} transformers")
        
        transformer_map = {
            'nominative': NominativeAnalysisTransformer,
            'potential': NarrativePotentialTransformer,
            'ensemble': EnsembleNarrativeTransformer,
            'relational': RelationalValueTransformer,
            'semantic': SemanticNarrativeTransformer,
            'statistical': StatisticalTransformer
        }
        
        # Build transformer list for FeatureUnion
        transformers = []
        for name in transformer_names:
            if name not in transformer_map:
                logger.warning(f"Unknown transformer: {name}, skipping")
                continue
            
            TransformerClass = transformer_map[name]
            
            # Get params for this transformer
            params = transformer_params.get(name, {}) if transformer_params else {}
            transformer = TransformerClass(**params)
            
            transformers.append((name, transformer))
        
        # Create FeatureUnion
        feature_union = FeatureUnion(transformers)
        
        # Get classifier
        classifier = self._get_classifier(classifier_type, classifier_params)
        
        # Build pipeline
        pipeline = Pipeline([
            ('features', feature_union),
            ('classifier', classifier)
        ])
        
        logger.info(f"  ✓ Combined pipeline built with {len(transformers)} transformers")
        
        return pipeline
    
    def build_all_pipelines_from_config(self) -> Dict[str, Pipeline]:
        """
        Build all pipelines specified in configuration.
        
        Returns:
            Dict mapping pipeline names to Pipeline objects
        """
        if self.config is None:
            raise ValueError("Must load configuration first")
        
        pipelines = {}
        
        # Get configuration
        pipeline_config = self.config.get('pipeline_config', {})
        steps = pipeline_config.get('steps', [])
        
        # Build individual transformer pipelines
        transformer_steps = [s for s in steps if s['transformer'] != 'GradientBoostingClassifier']
        
        for step in transformer_steps:
            name = step['name']
            transformer_type = step['transformer']
            params = step.get('params', {})
            
            # Map transformer name
            transformer_map = {
                'NominativeAnalysisTransformer': 'nominative',
                'NarrativePotentialTransformer': 'potential',
                'EnsembleNarrativeTransformer': 'ensemble',
                'RelationalValueTransformer': 'relational',
                'SemanticNarrativeTransformer': 'semantic',
                'StatisticalTransformer': 'statistical'
            }
            
            transformer_name = transformer_map.get(transformer_type)
            if transformer_name:
                pipeline = self.build_pipeline(
                    transformer_name,
                    classifier_type='gradient_boosting',
                    transformer_params=params
                )
                pipelines[name] = pipeline
        
        # Build combined pipeline
        transformer_names = [transformer_map[s['transformer']] 
                           for s in transformer_steps 
                           if s['transformer'] in transformer_map]
        
        if len(transformer_names) > 1:
            transformer_params_dict = {
                transformer_map[s['transformer']]: s.get('params', {})
                for s in transformer_steps
                if s['transformer'] in transformer_map
            }
            
            combined_pipeline = self.build_combined_pipeline(
                transformer_names,
                classifier_type='gradient_boosting',
                transformer_params=transformer_params_dict
            )
            pipelines['combined'] = combined_pipeline
        
        logger.info(f"✓ Built {len(pipelines)} pipelines from configuration")
        
        return pipelines
    
    def build_baseline_pipelines(self) -> Dict[str, Pipeline]:
        """
        Build baseline pipelines for comparison.
        
        Returns:
            Dict of baseline pipelines
        """
        logger.info("Building baseline pipelines")
        
        baselines = {}
        
        # Statistical TF-IDF baseline
        baselines['statistical_baseline'] = self.build_pipeline(
            'statistical',
            classifier_type='gradient_boosting'
        )
        
        logger.info(f"✓ Built {len(baselines)} baseline pipelines")
        
        return baselines
    
    def _get_classifier(self, classifier_type: str, 
                       params: Optional[Dict] = None) -> Any:
        """
        Get classifier instance.
        
        Args:
            classifier_type: Type of classifier
            params: Classifier parameters
        
        Returns:
            Classifier instance
        """
        if params is None:
            params = {}
        
        # Default params
        if 'random_state' not in params:
            params['random_state'] = 42
        
        if classifier_type == 'gradient_boosting':
            if 'n_estimators' not in params:
                params['n_estimators'] = 100
            if 'learning_rate' not in params:
                params['learning_rate'] = 0.1
            if 'max_depth' not in params:
                params['max_depth'] = 5
            return GradientBoostingClassifier(**params)
        
        elif classifier_type == 'random_forest':
            if 'n_estimators' not in params:
                params['n_estimators'] = 100
            return RandomForestClassifier(**params)
        
        elif classifier_type == 'logistic':
            if 'max_iter' not in params:
                params['max_iter'] = 1000
            return LogisticRegression(**params)
        
        else:
            raise ValueError(f"Unknown classifier type: {classifier_type}")
    
    def save_pipeline(self, pipeline: Pipeline, output_path: str) -> None:
        """
        Save trained pipeline to disk.
        
        Args:
            pipeline: Trained pipeline
            output_path: Output path for pickle file
        """
        import pickle
        from pathlib import Path
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            pickle.dump(pipeline, f)
        
        logger.info(f"✓ Saved pipeline to {output_path}")
    
    def load_pipeline(self, input_path: str) -> Pipeline:
        """
        Load trained pipeline from disk.
        
        Args:
            input_path: Path to pickle file
        
        Returns:
            Pipeline instance
        """
        import pickle
        
        with open(input_path, 'rb') as f:
            pipeline = pickle.load(f)
        
        logger.info(f"✓ Loaded pipeline from {input_path}")
        
        return pipeline

