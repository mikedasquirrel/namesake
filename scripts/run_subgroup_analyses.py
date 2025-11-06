"""Hurricane Subgroup Analysis Script

Run regressive claims separately for different subgroups to test temporal stability,
regional variation, and identify moderating factors.

Subgroups:
- By decade (1950s, 60s, 70s, 80s, 90s, 2000s, 2010s, 2020s)
- By gender (male, female, neutral/ambiguous)
- By region (Gulf Coast, Atlantic Coast, Caribbean)
- By category (Cat 1-2 vs. Cat 3-5)
- By forecast era (pre-1990 vs. post-1990 - proxy for forecast quality)
"""

import logging
import sys
import os
from pathlib import Path
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from core.config import Config
from core.models import db, Hurricane, HurricaneAnalysis
from analyzers.regressive_proof import RegressiveProofEngine, RegressiveClaim, DEFAULT_CLAIMS
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_subgroup_analyses():
    """Run all regressive claims across multiple subgroups."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        engine = RegressiveProofEngine()
        
        # Get hurricane claims only (H1-H7)
        hurricane_claims = [c for c in DEFAULT_CLAIMS if c.claim_id.startswith('H')]
        
        logger.info(f"Running subgroup analyses for {len(hurricane_claims)} hurricane claims")
        logger.info("This will generate ~50+ separate regression runs")
        
        results = {
            'by_decade': run_decade_subgroups(engine, hurricane_claims),
            'by_gender': run_gender_subgroups(engine, hurricane_claims),
            'by_category': run_category_subgroups(engine, hurricane_claims),
            'by_region': run_region_subgroups(engine, hurricane_claims),
            'by_forecast_era': run_forecast_era_subgroups(engine, hurricane_claims)
        }
        
        # Save results
        output_dir = Path(__file__).parent.parent / 'analysis_outputs' / 'subgroup_analyses'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'subgroup_results.json'
        with output_file.open('w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ SUBGROUP ANALYSES COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Results saved to: {output_file}")
        
        # Print summary
        print_subgroup_summary(results)
        
        return results


def run_decade_subgroups(engine, claims):
    """Run claims separately for each decade."""
    logger.info("\n[SUBGROUP] Running decade analyses...")
    
    decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
    results = {}
    
    for decade in decades:
        logger.info(f"  Decade: {decade}s")
        decade_results = {}
        
        for claim in claims:
            # Add decade filter
            modified_claim = RegressiveClaim(
                claim_id=f"{claim.claim_id}_decade{decade}",
                asset_type=claim.asset_type,
                target_column=claim.target_column,
                target_kind=claim.target_kind,
                description=f"{claim.description} [Decade: {decade}s]",
                features=claim.features,
                control_features=claim.control_features,
                filters={**claim.filters, 'decade': decade},
                sample_floor=max(20, claim.sample_floor // 2)  # Lower threshold for subgroups
            )
            
            result = engine.run_claim(modified_claim)
            decade_results[claim.claim_id] = result
        
        results[str(decade)] = decade_results
    
    return results


def run_gender_subgroups(engine, claims):
    """Run claims separately for male, female, and neutral names."""
    logger.info("\n[SUBGROUP] Running gender analyses...")
    
    genders = ['male', 'female', 'neutral']
    results = {}
    
    for gender in genders:
        logger.info(f"  Gender: {gender}")
        gender_results = {}
        
        for claim in claims:
            # Create gender-specific filter
            if gender == 'neutral':
                gender_filter = {'gender_coded': {'op': 'in', 'value': ['neutral', 'ambiguous', None]}}
            else:
                gender_filter = {'gender_coded': gender}
            
            modified_claim = RegressiveClaim(
                claim_id=f"{claim.claim_id}_gender_{gender}",
                asset_type=claim.asset_type,
                target_column=claim.target_column,
                target_kind=claim.target_kind,
                description=f"{claim.description} [Gender: {gender}]",
                features=claim.features,
                control_features=claim.control_features,
                filters={**claim.filters, **gender_filter},
                sample_floor=max(15, claim.sample_floor // 3)
            )
            
            result = engine.run_claim(modified_claim)
            gender_results[claim.claim_id] = result
        
        results[gender] = gender_results
    
    return results


def run_category_subgroups(engine, claims):
    """Run claims for weaker (Cat 1-2) vs. stronger (Cat 3-5) storms."""
    logger.info("\n[SUBGROUP] Running category analyses...")
    
    categories = {
        'weak': {'saffir_simpson_category': {'op': 'in', 'value': [1, 2]}},
        'major': {'saffir_simpson_category': {'op': 'gte', 'value': 3}}
    }
    
    results = {}
    
    for cat_name, cat_filter in categories.items():
        logger.info(f"  Category: {cat_name}")
        cat_results = {}
        
        for claim in claims:
            modified_claim = RegressiveClaim(
                claim_id=f"{claim.claim_id}_cat_{cat_name}",
                asset_type=claim.asset_type,
                target_column=claim.target_column,
                target_kind=claim.target_kind,
                description=f"{claim.description} [Category: {cat_name}]",
                features=claim.features,
                control_features=claim.control_features,
                filters={**claim.filters, **cat_filter},
                sample_floor=max(20, claim.sample_floor // 2)
            )
            
            result = engine.run_claim(modified_claim)
            cat_results[claim.claim_id] = result
        
        results[cat_name] = cat_results
    
    return results


def run_region_subgroups(engine, claims):
    """Run claims by landfall region."""
    logger.info("\n[SUBGROUP] Running region analyses...")
    
    regions = {
        'gulf_coast': ['Louisiana', 'Texas', 'Mississippi', 'Alabama'],
        'atlantic_coast': ['Florida', 'Georgia', 'South Carolina', 'North Carolina', 'Virginia'],
        'caribbean': ['Puerto Rico', 'US Virgin Islands']
    }
    
    results = {}
    
    for region_name, states in regions.items():
        logger.info(f"  Region: {region_name}")
        region_results = {}
        
        for claim in claims:
            region_filter = {'landfall_state': {'op': 'in', 'value': states}}
            
            modified_claim = RegressiveClaim(
                claim_id=f"{claim.claim_id}_region_{region_name}",
                asset_type=claim.asset_type,
                target_column=claim.target_column,
                target_kind=claim.target_kind,
                description=f"{claim.description} [Region: {region_name}]",
                features=claim.features,
                control_features=claim.control_features,
                filters={**claim.filters, **region_filter},
                sample_floor=max(15, claim.sample_floor // 3)
            )
            
            result = engine.run_claim(modified_claim)
            region_results[claim.claim_id] = result
        
        results[region_name] = region_results
    
    return results


def run_forecast_era_subgroups(engine, claims):
    """Run claims for pre-1990 (poor forecasts) vs. post-1990 (good forecasts)."""
    logger.info("\n[SUBGROUP] Running forecast era analyses...")
    
    eras = {
        'pre_1990': {'year': {'op': 'lt', 'value': 1990}},
        'post_1990': {'year': {'op': 'gte', 'value': 1990}}
    }
    
    results = {}
    
    for era_name, era_filter in eras.items():
        logger.info(f"  Era: {era_name}")
        era_results = {}
        
        for claim in claims:
            modified_claim = RegressiveClaim(
                claim_id=f"{claim.claim_id}_era_{era_name}",
                asset_type=claim.asset_type,
                target_column=claim.target_column,
                target_kind=claim.target_kind,
                description=f"{claim.description} [Era: {era_name}]",
                features=claim.features,
                control_features=claim.control_features,
                filters={**claim.filters, **era_filter},
                sample_floor=max(25, claim.sample_floor // 2)
            )
            
            result = engine.run_claim(modified_claim)
            era_results[claim.claim_id] = result
        
        results[era_name] = era_results
    
    return results


def print_subgroup_summary(results):
    """Print summary of subgroup findings."""
    print("\n" + "="*60)
    print("SUBGROUP ANALYSIS SUMMARY")
    print("="*60)
    
    for subgroup_type, subgroup_data in results.items():
        print(f"\n{subgroup_type.upper().replace('_', ' ')}:")
        
        for subgroup_name, claims_results in subgroup_data.items():
            valid_claims = sum(1 for r in claims_results.values() if r.get('status') == 'ok')
            total_claims = len(claims_results)
            
            print(f"  {subgroup_name}: {valid_claims}/{total_claims} claims valid")
            
            # Show strongest finding in this subgroup
            best_r2 = 0
            best_claim = None
            for claim_id, result in claims_results.items():
                if result.get('status') == 'ok':
                    r2 = result.get('model_summary', {}).get('r_squared') or 0
                    if r2 > best_r2:
                        best_r2 = r2
                        best_claim = claim_id
            
            if best_claim:
                print(f"    Best: {best_claim} (R² = {best_r2:.3f})")


if __name__ == '__main__':
    run_subgroup_analyses()

