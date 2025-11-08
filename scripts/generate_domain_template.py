#!/usr/bin/env python3
"""Domain Template Generator

Scaffolding generator for new research domains. Creates all necessary files
with proper structure and boilerplate code.

Usage:
    # Generate complete scaffolding for a new domain
    python scripts/generate_domain_template.py --domain soccer --create-all
    
    # Generate specific files only
    python scripts/generate_domain_template.py --domain soccer --create-config
    python scripts/generate_domain_template.py --domain soccer --create-collector
    python scripts/generate_domain_template.py --domain soccer --create-analyzer

Author: Michael Smerconish
Date: November 2025
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.research_framework import FRAMEWORK


def generate_config_yaml(domain_id: str, display_name: str, params: Dict) -> str:
    """Generate domain configuration YAML"""
    template = f"""# {display_name} Domain Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d')}

domain: {domain_id}
display_name: "{display_name}"

research_questions:
  - "Research question 1?"
  - "Research question 2?"
  - "Research question 3?"

# Data collection configuration
collector_class: "collectors.{domain_id}_collector.{params['collector_class']}"
collector_params:
  source: "data_source_name"
  rate_limit_seconds: 2.0

# Analysis configuration
analyzer_class: "analyzers.{domain_id}_statistical_analyzer.{params['analyzer_class']}"
analyzer_params:
  statistical_rigor: "high"

# Database models
models:
  - {params['model_name']}
  - {params['analysis_model_name']}

# Sample targets
target_sample_size: {params.get('target_sample_size', 1000)}
min_sample_size: {params.get('min_sample_size', 500)}

# Stratification strategy (if applicable)
stratification:
  enabled: {str(params.get('stratification_enabled', False)).lower()}
  field: "category_field"
  targets:
    category_1: 250
    category_2: 250
    category_3: 250
    category_4: 250

# Primary analysis variables
primary_outcome_variable: "outcome_variable"
secondary_outcome_variables:
  - "secondary_var_1"
  - "secondary_var_2"

key_predictors:
  - "syllable_count"
  - "phonetic_features"
  - "memorability"
  - "name_length"

control_variables:
  - "control_var_1"
  - "control_var_2"

# Temporal analysis
temporal_component: {str(params.get('temporal', False)).lower()}
temporal_field: "date_field"

# Geographic analysis
geographic_component: {str(params.get('geographic', False)).lower()}
geographic_field: "location_field"

# Web interface
page_template: "{domain_id}.html"
findings_cache_key: "{domain_id}_findings"
api_endpoints:
  - "/api/{domain_id}/stats"
  - "/api/{domain_id}/analysis"

# Expected outcomes
effect_strength_expected: "moderate"
expected_correlations:
  predictor_outcome: 0.25

# Quality thresholds
quality_checks:
  min_data_completeness: 0.95
  require_out_of_sample_validation: true
  require_cross_validation: true

# Status
status: "planned"
innovation_rating: 1
priority: "medium"

notes: |
  New domain generated from template.
  Customize all sections for your specific research requirements.
"""
    return template


def generate_collector(domain_id: str, class_name: str, model_name: str) -> str:
    """Generate collector class"""
    template = f'''"""{class_name} - Data Collection for {domain_id.title()} Domain

Collects data for nominative determinism research in {domain_id} domain.

Usage:
    collector = {class_name}()
    results = collector.collect_sample(target_size=1000)

Generated: {datetime.now().strftime('%Y-%m-%d')}
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

from core.models import db, {model_name}
from core.research_framework import FRAMEWORK
from utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class {class_name}:
    """Collector for {domain_id} domain data"""
    
    def __init__(self):
        """Initialize collector"""
        self.domain_meta = FRAMEWORK.get_domain('{domain_id}')
        logger.info(f"Initialized {{self.__class__.__name__}}")
        
    def collect_sample(self, target_size: int = 1000) -> Dict:
        """
        Collect a sample of data.
        
        Args:
            target_size: Number of records to collect
        
        Returns:
            Collection statistics
        """
        logger.info(f"Starting data collection for {{target_size}} records...")
        
        tracker = ProgressTracker(
            total_steps=target_size,
            print_interval=max(1, target_size // 20),
            task_name="{domain_id.title()} Data Collection"
        )
        
        collected = 0
        updated = 0
        errors = []
        
        try:
            # TODO: Implement your data collection logic here
            # Example structure:
            
            # for i in range(target_size):
            #     try:
            #         # Fetch data from source
            #         record_data = self._fetch_record(i)
            #         
            #         # Check if exists
            #         existing = {model_name}.query.filter_by(
            #             id=record_data['id']
            #         ).first()
            #         
            #         if existing:
            #             # Update
            #             self._update_record(existing, record_data)
            #             updated += 1
            #         else:
            #             # Create new
            #             new_record = {model_name}(**record_data)
            #             db.session.add(new_record)
            #             collected += 1
            #         
            #         if (collected + updated) % 100 == 0:
            #             db.session.commit()
            #         
            #         tracker.update(1, message=f"Collected: {{collected}}, Updated: {{updated}}")
            #         
            #         # Rate limiting
            #         time.sleep(0.5)
            #         
            #     except Exception as e:
            #         logger.error(f"Error collecting record {{i}}: {{e}}")
            #         errors.append(str(e))
            
            # Final commit
            db.session.commit()
            
            tracker.complete(f"Collection complete: {{collected}} new, {{updated}} updated")
            
            return {{
                'total_collected': collected,
                'total_updated': updated,
                'total_errors': len(errors),
                'errors': errors[:10],  # First 10 errors only
                'timestamp': datetime.now().isoformat()
            }}
            
        except Exception as e:
            logger.error(f"Collection failed: {{e}}")
            tracker.error(str(e))
            db.session.rollback()
            raise
    
    def collect_stratified_sample(self, target_per_stratum: Dict[str, int]) -> Dict:
        """
        Collect stratified sample across categories.
        
        Args:
            target_per_stratum: Dict mapping stratum to target count
        
        Returns:
            Collection statistics
        """
        logger.info("Starting stratified data collection...")
        
        results = {{
            'total_collected': 0,
            'total_updated': 0,
            'strata': {{}}
        }}
        
        for stratum, target in target_per_stratum.items():
            logger.info(f"Collecting {{target}} records for stratum: {{stratum}}")
            
            # TODO: Implement stratified collection logic
            # stratum_result = self._collect_stratum(stratum, target)
            # results['strata'][stratum] = stratum_result
            # results['total_collected'] += stratum_result['collected']
            # results['total_updated'] += stratum_result['updated']
        
        return results
    
    def _fetch_record(self, index: int) -> Dict:
        """Fetch a single record from data source"""
        # TODO: Implement data fetching logic
        raise NotImplementedError("Implement data fetching for your source")
    
    def _update_record(self, record, data: Dict):
        """Update existing record with new data"""
        # TODO: Implement update logic
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
'''
    return template


def generate_analyzer(domain_id: str, class_name: str, model_name: str) -> str:
    """Generate analyzer class"""
    template = f'''"""{class_name} - Statistical Analysis for {domain_id.title()} Domain

Comprehensive statistical analysis for {domain_id} nominative determinism research.

Generated: {datetime.now().strftime('%Y-%m-%d')}
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
from datetime import datetime

from core.models import db, {model_name}
from core.research_framework import FRAMEWORK
from utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class {class_name}:
    """Statistical analyzer for {domain_id} domain"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.domain_meta = FRAMEWORK.get_domain('{domain_id}')
        self.framework = FRAMEWORK
        logger.info(f"Initialized {{self.__class__.__name__}}")
    
    def run_full_analysis(self) -> Dict:
        """
        Run complete statistical analysis pipeline.
        
        Returns:
            Comprehensive analysis results
        """
        logger.info("="*80)
        logger.info("{domain_id.upper()} STATISTICAL ANALYSIS")
        logger.info("="*80)
        
        results = {{
            'domain_id': '{domain_id}',
            'analysis_date': datetime.now().isoformat(),
            'sample_size': 0,
            'descriptive_stats': {{}},
            'correlations': {{}},
            'regressions': {{}},
            'hypotheses_tests': {{}},
            'has_out_of_sample_validation': False,
            'has_effect_sizes': True,
            'has_null_results': True
        }}
        
        # Load data
        logger.info("Loading data from database...")
        df = self._load_data()
        results['sample_size'] = len(df)
        
        logger.info(f"Loaded {{len(df):,}} records")
        
        if len(df) < 100:
            logger.warning("Sample size too small for robust analysis")
            results['warning'] = 'Insufficient sample size'
            return results
        
        # Descriptive statistics
        logger.info("\\nComputing descriptive statistics...")
        results['descriptive_stats'] = self._compute_descriptive_stats(df)
        
        # Correlation analysis
        logger.info("\\nComputing correlations...")
        results['correlations'] = self._compute_correlations(df)
        
        # Regression analysis
        logger.info("\\nRunning regression models...")
        results['regressions'] = self._run_regressions(df)
        
        # Hypothesis tests
        logger.info("\\nTesting hypotheses...")
        results['hypotheses_tests'] = self._test_hypotheses(df)
        
        # Out-of-sample validation
        if len(df) >= 200:
            logger.info("\\nPerforming out-of-sample validation...")
            results['validation'] = self._validate_out_of_sample(df)
            results['has_out_of_sample_validation'] = True
        
        logger.info("\\n" + "="*80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*80)
        
        return results
    
    def _load_data(self) -> pd.DataFrame:
        """Load data from database into DataFrame"""
        # TODO: Customize data loading
        records = {model_name}.query.all()
        
        data = []
        for record in records:
            data.append({{
                'id': record.id,
                # Add your fields here
                # 'name': record.name,
                # 'outcome': record.outcome_variable,
                # 'syllables': record.syllable_count,
            }})
        
        return pd.DataFrame(data)
    
    def _compute_descriptive_stats(self, df: pd.DataFrame) -> Dict:
        """Compute descriptive statistics"""
        stats_dict = {{}}
        
        # TODO: Implement descriptive statistics
        # Example:
        # numeric_cols = df.select_dtypes(include=[np.number]).columns
        # for col in numeric_cols:
        #     stats_dict[col] = {{
        #         'mean': float(df[col].mean()),
        #         'std': float(df[col].std()),
        #         'median': float(df[col].median()),
        #         'min': float(df[col].min()),
        #         'max': float(df[col].max())
        #     }}
        
        return stats_dict
    
    def _compute_correlations(self, df: pd.DataFrame) -> Dict:
        """Compute correlation analysis"""
        correlations = {{}}
        
        # TODO: Implement correlation analysis
        # Example:
        # predictors = ['syllables', 'phonetic_score', 'memorability']
        # outcome = 'outcome_variable'
        # 
        # for predictor in predictors:
        #     if predictor in df.columns and outcome in df.columns:
        #         r, p = stats.pearsonr(df[predictor], df[outcome])
        #         correlations[predictor] = {{
        #             'correlation': float(r),
        #             'p_value': float(p),
        #             'significant': bool(p < 0.05),
        #             'effect_size': self.framework.interpret_effect_size(r, 'correlation')
        #         }}
        
        return correlations
    
    def _run_regressions(self, df: pd.DataFrame) -> Dict:
        """Run regression models"""
        regressions = {{}}
        
        # TODO: Implement regression analysis
        # Use sklearn or statsmodels
        
        return regressions
    
    def _test_hypotheses(self, df: pd.DataFrame) -> Dict:
        """Test research hypotheses"""
        tests = {{}}
        
        # TODO: Implement hypothesis testing for each research question
        # Reference self.domain_meta.research_questions
        
        return tests
    
    def _validate_out_of_sample(self, df: pd.DataFrame) -> Dict:
        """Perform out-of-sample validation"""
        # TODO: Implement train/test split and validation
        
        return {{
            'method': 'train_test_split',
            'test_size': 0.2,
            'results': 'not_implemented'
        }}
'''
    return template


def generate_models_code(domain_id: str, model_name: str, analysis_model_name: str) -> str:
    """Generate model class definitions"""
    template = f'''# Add these model classes to core/models.py

class {model_name}(db.Model):
    """{domain_id.title()} data model"""
    __tablename__ = '{domain_id}_records'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    
    # TODO: Add domain-specific fields
    # outcome_variable = db.Column(db.Float)
    # category = db.Column(db.String(100))
    # date_field = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    analysis = db.relationship('{analysis_model_name}', backref='{domain_id}_record', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {{
            'id': self.id,
            'name': self.name,
            # Add your fields
        }}


class {analysis_model_name}(db.Model):
    """{domain_id.title()} linguistic analysis"""
    __tablename__ = '{domain_id}_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('{domain_id}_records.id'), nullable=False, unique=True)
    
    # Phonetic features
    syllable_count = db.Column(db.Integer)
    character_length = db.Column(db.Integer)
    phonetic_score = db.Column(db.Float)
    memorability_score = db.Column(db.Float)
    uniqueness_score = db.Column(db.Float)
    
    # TODO: Add domain-specific analysis fields
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {{
            'syllables': self.syllable_count,
            'length': self.character_length,
            'phonetic': self.phonetic_score,
            'memorability': self.memorability_score,
            'uniqueness': self.uniqueness_score,
        }}
'''
    return template


def generate_runner_script(domain_id: str, collector_class: str) -> str:
    """Generate collection runner script"""
    template = f'''#!/usr/bin/env python3
"""{domain_id.title()} Comprehensive Collection

Collect data for {domain_id} nominative determinism research.

Usage:
    python scripts/collect_{domain_id}_comprehensive.py

Generated: {datetime.now().strftime('%Y-%m-%d')}
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from collectors.{domain_id}_collector import {collector_class}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('{domain_id}_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run comprehensive {domain_id} collection."""
    print("\\n" + "=" * 70)
    print("{domain_id.upper()} COMPREHENSIVE COLLECTION".center(70))
    print("=" * 70 + "\\n")
    
    start_time = datetime.now()
    
    with app.app_context():
        collector = {collector_class}()
        
        logger.info("Starting {domain_id} data collection...")
        
        # Customize collection parameters
        stats = collector.collect_sample(target_size=1000)
        
        print("\\n" + "=" * 70)
        print("Collection Complete".center(70))
        print("=" * 70)
        print(f"\\nTotal Collected: {{stats['total_collected']}}")
        print(f"Total Updated: {{stats['total_updated']}}")
        print(f"Errors: {{stats.get('total_errors', 0)}}")
        
        elapsed = datetime.now() - start_time
        print(f"\\nTotal Time: {{elapsed}}")
        
        logger.info(f"{domain_id} collection complete: {{stats['total_collected']}} records in {{elapsed}}")


if __name__ == "__main__":
    main()
'''
    return template


def generate_html_template(domain_id: str, display_name: str) -> str:
    """Generate HTML findings page template"""
    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ display_name }}}} - Nominative Determinism Research</title>
    <link rel="stylesheet" href="{{{{ url_for('static', filename='style.css') }}}}">
</head>
<body>
    <div class="container">
        <header>
            <h1>{display_name}</h1>
            <p class="subtitle">Nominative Determinism Research Platform</p>
        </header>
        
        <nav>
            <a href="{{{{ url_for('index') }}}}">Home</a>
            <a href="{{{{ url_for('overview') }}}}">Overview</a>
            <a href="{{{{ url_for('{domain_id}_findings') }}}}" class="active">{domain_id.title()}</a>
        </nav>
        
        <main>
            <section class="research-questions">
                <h2>Research Questions</h2>
                <ol>
                    <li>Research question 1?</li>
                    <li>Research question 2?</li>
                    <li>Research question 3?</li>
                </ol>
            </section>
            
            <section class="sample">
                <h2>Sample</h2>
                <p><strong>N</strong> = {{{{ stats.get('sample_size', 'N/A') }}}}</p>
                <p><strong>Data Source:</strong> [Specify source]</p>
            </section>
            
            <section class="findings">
                <h2>Key Findings</h2>
                <!-- TODO: Add findings visualization and results -->
                <p>Analysis in progress. Check back for results.</p>
            </section>
            
            <section class="methodology">
                <h2>Methodology</h2>
                <p>
                    This analysis follows the comprehensive nominative determinism 
                    research framework with standardized statistical methods,
                    quality validation, and transparent reporting.
                </p>
            </section>
        </main>
        
        <footer>
            <p>&copy; 2025 Nominative Determinism Research Platform</p>
        </footer>
    </div>
</body>
</html>
'''
    return template


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate scaffolding for new research domain',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--domain', type=str, required=True, help='Domain identifier (e.g., soccer)')
    parser.add_argument('--display-name', type=str, help='Display name (e.g., "Soccer Player Analysis")')
    parser.add_argument('--target-sample-size', type=int, default=1000, help='Target sample size')
    parser.add_argument('--stratification', action='store_true', help='Enable stratification')
    parser.add_argument('--temporal', action='store_true', help='Enable temporal analysis')
    parser.add_argument('--geographic', action='store_true', help='Enable geographic analysis')
    
    # File generation flags
    parser.add_argument('--create-all', action='store_true', help='Create all files')
    parser.add_argument('--create-config', action='store_true', help='Create config YAML')
    parser.add_argument('--create-collector', action='store_true', help='Create collector class')
    parser.add_argument('--create-analyzer', action='store_true', help='Create analyzer class')
    parser.add_argument('--create-runner', action='store_true', help='Create runner script')
    parser.add_argument('--create-template', action='store_true', help='Create HTML template')
    parser.add_argument('--create-models', action='store_true', help='Generate model code')
    
    args = parser.parse_args()
    
    domain_id = args.domain.lower()
    display_name = args.display_name or f"{domain_id.title()} Analysis"
    
    # Check if domain already exists
    if FRAMEWORK.get_domain(domain_id):
        print(f"WARNING: Domain '{domain_id}' already exists in framework!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Determine what to create
    create_all = args.create_all
    
    # Setup parameters
    collector_class = f"{domain_id.title().replace('_', '')}Collector"
    analyzer_class = f"{domain_id.title().replace('_', '')}StatisticalAnalyzer"
    model_name = f"{domain_id.title().replace('_', '')}"
    analysis_model_name = f"{model_name}Analysis"
    
    params = {
        'collector_class': collector_class,
        'analyzer_class': analyzer_class,
        'model_name': model_name,
        'analysis_model_name': analysis_model_name,
        'target_sample_size': args.target_sample_size,
        'min_sample_size': args.target_sample_size // 2,
        'stratification_enabled': args.stratification,
        'temporal': args.temporal,
        'geographic': args.geographic
    }
    
    project_root = Path(__file__).parent.parent
    
    print("\n" + "=" * 80)
    print("DOMAIN TEMPLATE GENERATOR")
    print("=" * 80)
    print(f"Domain: {domain_id}")
    print(f"Display Name: {display_name}")
    print(f"Target Sample Size: {args.target_sample_size}")
    print("=" * 80 + "\n")
    
    # Create config
    if create_all or args.create_config:
        config_path = project_root / "core" / "domain_configs" / f"{domain_id}.yaml"
        print(f"Creating: {config_path}")
        config_content = generate_config_yaml(domain_id, display_name, params)
        config_path.write_text(config_content)
        print("✓ Config created\n")
    
    # Create collector
    if create_all or args.create_collector:
        collector_path = project_root / "collectors" / f"{domain_id}_collector.py"
        print(f"Creating: {collector_path}")
        collector_content = generate_collector(domain_id, collector_class, model_name)
        collector_path.write_text(collector_content)
        print("✓ Collector created\n")
    
    # Create analyzer
    if create_all or args.create_analyzer:
        analyzer_path = project_root / "analyzers" / f"{domain_id}_statistical_analyzer.py"
        print(f"Creating: {analyzer_path}")
        analyzer_content = generate_analyzer(domain_id, analyzer_class, model_name)
        analyzer_path.write_text(analyzer_content)
        print("✓ Analyzer created\n")
    
    # Create runner script
    if create_all or args.create_runner:
        runner_path = project_root / "scripts" / f"collect_{domain_id}_comprehensive.py"
        print(f"Creating: {runner_path}")
        runner_content = generate_runner_script(domain_id, collector_class)
        runner_path.write_text(runner_content)
        runner_path.chmod(0o755)
        print("✓ Runner script created\n")
    
    # Create HTML template
    if create_all or args.create_template:
        template_path = project_root / "templates" / f"{domain_id}.html"
        print(f"Creating: {template_path}")
        html_content = generate_html_template(domain_id, display_name)
        template_path.write_text(html_content)
        print("✓ HTML template created\n")
    
    # Generate model code
    if create_all or args.create_models:
        models_code = generate_models_code(domain_id, model_name, analysis_model_name)
        models_file = project_root / f"{domain_id}_models.py"
        print(f"Generating model code: {models_file}")
        models_file.write_text(models_code)
        print("✓ Model code generated")
        print(f"  → Copy classes from {models_file} to core/models.py\n")
    
    print("=" * 80)
    print("SCAFFOLDING COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review and customize generated files")
    print("2. Add model classes to core/models.py")
    print("3. Update research_framework.py to register domain")
    print("4. Implement data collection logic in collector")
    print("5. Implement statistical analysis in analyzer")
    print(f"6. Run: python scripts/run_domain_analysis.py --domain {domain_id} --mode new")
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()

