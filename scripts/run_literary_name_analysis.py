"""Run Literary Name Composition Analysis

Main execution script to run the complete literary name composition analysis pipeline.

Usage:
    python scripts/run_literary_name_analysis.py [--mode new|update] [--skip-collection]

Author: Michael Smerconish
Date: November 2025
"""

import sys
import os
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from core.models import LiteraryWork, LiteraryCharacter, LiteraryNameAnalysis
from collectors.literary_name_collector import LiteraryNameCollector
from analyzers.literary_name_analyzer import LiteraryNameAnalyzer
from utils.progress_tracker import ProgressTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'literary_name_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run literary name composition analysis')
    parser.add_argument('--mode', choices=['new', 'update'], default='new',
                        help='Analysis mode: new (fresh analysis) or update (update existing)')
    parser.add_argument('--skip-collection', action='store_true',
                        help='Skip data collection, use existing data')
    parser.add_argument('--fiction-count', type=int, default=50,
                        help='Number of fiction works to collect')
    parser.add_argument('--nonfiction-count', type=int, default=30,
                        help='Number of nonfiction works to collect')
    parser.add_argument('--save-results', action='store_true', default=True,
                        help='Save results to JSON file')
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()
    
    logger.info("="*80)
    logger.info("LITERARY NAME COMPOSITION ANALYSIS")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Skip collection: {args.skip_collection}")
    logger.info(f"Fiction target: {args.fiction_count}")
    logger.info(f"Nonfiction target: {args.nonfiction_count}")
    logger.info("="*80)
    
    # Create app context
    with app.app_context():
        try:
            # Initialize database tables
            logger.info("\nInitializing database...")
            db.create_all()
            logger.info("Database initialized successfully")
            
            # Initialize analyzer
            logger.info("\nInitializing analyzer...")
            analyzer = LiteraryNameAnalyzer(mode=args.mode)
            
            # Collect data (unless skipped)
            if not args.skip_collection:
                logger.info("\n" + "="*80)
                logger.info("STEP 1: DATA COLLECTION")
                logger.info("="*80)
                
                data = analyzer.collect_data()
                
                logger.info(f"\nData collection summary:")
                logger.info(f"  Total works: {data['work_count']}")
                logger.info(f"  Total characters: {data['sample_size']}")
                
            else:
                logger.info("\nSkipping data collection, loading existing data...")
                # Load existing data from database
                data = load_existing_data()
            
            # Analyze data
            logger.info("\n" + "="*80)
            logger.info("STEP 2: DATA ANALYSIS")
            logger.info("="*80)
            
            results = analyzer.analyze_data(data)
            
            # Save results to database
            logger.info("\n" + "="*80)
            logger.info("STEP 3: SAVING TO DATABASE")
            logger.info("="*80)
            
            save_to_database(data, results)
            
            # Save results to JSON (if requested)
            if args.save_results:
                logger.info("\n" + "="*80)
                logger.info("STEP 4: SAVING RESULTS TO FILE")
                logger.info("="*80)
                
                save_results_to_file(results)
            
            # Display summary
            logger.info("\n" + "="*80)
            logger.info("ANALYSIS COMPLETE - SUMMARY")
            logger.info("="*80)
            display_summary(results)
            
            logger.info("\n✓ Literary name composition analysis completed successfully!")
            logger.info("  View results at: http://localhost:5000/literary_name_composition")
            
            return 0
            
        except Exception as e:
            logger.error(f"\n✗ Error during analysis: {e}", exc_info=True)
            return 1


def load_existing_data() -> dict:
    """Load existing data from database."""
    logger.info("Loading works from database...")
    works = LiteraryWork.query.all()
    
    logger.info("Loading characters from database...")
    characters = LiteraryCharacter.query.all()
    
    logger.info(f"Loaded {len(works)} works and {len(characters)} characters")
    
    # Organize data
    data = {
        'sample_size': len(characters),
        'work_count': len(works),
        'data': {
            'works': {},
            'characters': {},
            'baselines': {},
            'total_works': len(works),
            'total_characters': len(characters),
        },
        'collection_timestamp': datetime.now().isoformat(),
    }
    
    # Group by category
    for work in works:
        category = work.category
        if category not in data['data']['works']:
            data['data']['works'][category] = {}
        
        data['data']['works'][category][str(work.id)] = {
            'work_id': str(work.id),
            'title': work.title,
            'author': work.author,
            'category': category,
            'genre': work.genre,
            'publication_year': work.publication_year,
            'source': work.source,
            'word_count': work.word_count,
        }
    
    # Add characters
    for character in characters:
        work_id = str(character.work_id)
        if work_id not in data['data']['characters']:
            data['data']['characters'][work_id] = {}
        
        data['data']['characters'][work_id][str(character.id)] = {
            'character_id': str(character.id),
            'work_id': work_id,
            'full_name': character.full_name,
            'first_name': character.first_name,
            'last_name': character.last_name,
            'character_role': character.character_role,
            'character_outcome': character.character_outcome,
            'importance': character.character_importance,
            'name_type': character.name_type,
            'is_invented': character.is_invented,
            'mention_count': character.mention_count,
            'importance_score': character.importance_score,
        }
    
    # Generate baselines
    from data.common_american_names import generate_population_names
    data['data']['baselines'] = {
        'random': {'names': generate_population_names(10000), 'sample_size': 10000},
        'stratified': {'names': generate_population_names(10000), 'sample_size': 10000},
    }
    
    return data


def save_to_database(data: dict, results: dict):
    """Save analysis results to database."""
    logger.info("Saving works to database...")
    works_saved = 0
    
    for category, work_dict in data['data']['works'].items():
        for work_id, work_data in work_dict.items():
            # Check if work exists
            work = LiteraryWork.query.filter_by(source_id=work_data.get('source_id', work_id)).first()
            
            if not work:
                work = LiteraryWork(
                    title=work_data['title'],
                    author=work_data['author'],
                    category=category,
                    genre=work_data.get('genre'),
                    publication_year=work_data.get('publication_year'),
                    source=work_data.get('source', 'unknown'),
                    source_id=work_data.get('source_id', work_id),
                    source_url=work_data.get('source_url'),
                    word_count=work_data.get('word_count', 0),
                    collected_at=datetime.now(),
                )
                db.session.add(work)
                works_saved += 1
    
    db.session.commit()
    logger.info(f"Saved {works_saved} works to database")
    
    # Save characters
    logger.info("Saving characters to database...")
    chars_saved = 0
    
    for char_analysis in results.get('character_analyses', []):
        # Find work
        work = LiteraryWork.query.filter_by(source_id=str(char_analysis['work_id'])).first()
        if not work:
            continue
        
        # Check if character exists
        character = LiteraryCharacter.query.filter_by(
            work_id=work.id,
            full_name=char_analysis['full_name']
        ).first()
        
        if not character:
            character = LiteraryCharacter(
                work_id=work.id,
                full_name=char_analysis['full_name'],
                first_name=char_analysis.get('first_name'),
                last_name=char_analysis.get('last_name'),
                character_role=char_analysis.get('character_role'),
                character_outcome=char_analysis.get('character_outcome'),
                character_importance=char_analysis.get('importance'),
                name_type=char_analysis.get('name_type'),
                is_invented=char_analysis.get('is_invented', False),
                mention_count=char_analysis.get('mention_count', 0),
                importance_score=char_analysis.get('importance_score', 0),
                created_at=datetime.now(),
            )
            db.session.add(character)
            chars_saved += 1
        
        # Save name analysis
        if not character.name_analysis:
            analysis = LiteraryNameAnalysis(
                character_id=character.id,
                syllable_count=char_analysis.get('syllable_count'),
                character_length=char_analysis.get('character_length'),
                melodiousness_score=char_analysis.get('melodiousness_score'),
                americanness_score=char_analysis.get('americanness_score'),
                commonality_score=char_analysis.get('commonality_score'),
                harshness_score=char_analysis.get('harshness_score'),
                name_valence=char_analysis.get('name_valence'),
                plosive_count=char_analysis.get('plosive_count'),
                fricative_count=char_analysis.get('fricative_count'),
                liquid_count=char_analysis.get('liquid_count'),
                nasal_count=char_analysis.get('nasal_count'),
                vowel_count=char_analysis.get('vowel_count'),
                consonant_count=char_analysis.get('consonant_count'),
                is_in_top_100_names=char_analysis.get('is_in_top_100_names', False),
                is_in_top_1000_names=char_analysis.get('is_in_top_1000_names', False),
                protagonist_name_score=char_analysis.get('protagonist_score'),
                antagonist_name_score=char_analysis.get('antagonist_score'),
                vulnerable_sounding_score=char_analysis.get('vulnerable_score'),
                memorability_score=char_analysis.get('memorability_score'),
                distinctiveness_score=char_analysis.get('distinctiveness_score'),
                computed_at=datetime.now(),
            )
            db.session.add(analysis)
    
    db.session.commit()
    logger.info(f"Saved {chars_saved} characters to database")
    
    # Update work aggregates
    logger.info("Updating work-level aggregates...")
    for work_analysis in results.get('work_analyses', []):
        work = LiteraryWork.query.filter_by(source_id=str(work_analysis['work_id'])).first()
        if work:
            work.character_count_total = work_analysis.get('character_count', 0)
            work.mean_name_melodiousness = work_analysis.get('mean_melodiousness')
            work.mean_name_americanness = work_analysis.get('mean_americanness')
            work.mean_name_commonality = work_analysis.get('mean_commonality')
            work.mean_name_syllables = work_analysis.get('mean_syllables')
            work.invented_name_pct = work_analysis.get('invented_pct')
            work.analyzed_at = datetime.now()
    
    db.session.commit()
    logger.info("Database save complete")


def save_results_to_file(results: dict):
    """Save results to JSON file."""
    output_dir = Path("analysis_outputs/literary_name_composition")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"literary_analysis_{timestamp}.json"
    
    # Remove large character list for summary file
    summary = {
        'sample_size': results['sample_size'],
        'work_count': results['work_count'],
        'characters_analyzed': results['characters_analyzed'],
        'baseline_statistics': results['baseline_statistics'],
        'category_aggregates': results['category_aggregates'],
        'comparison_results': results['comparison_results'],
        'prediction_results': results.get('prediction_results', {}),
        'cross_category_results': results.get('cross_category_results', {}),
        'timestamp': results['timestamp'],
    }
    
    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Results saved to: {filename}")
    
    # Save full results with characters
    full_filename = output_dir / f"literary_analysis_full_{timestamp}.json"
    with open(full_filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Full results saved to: {full_filename}")


def display_summary(results: dict):
    """Display analysis summary."""
    logger.info(f"\nCharacters analyzed: {results['characters_analyzed']}")
    logger.info(f"Works analyzed: {results['work_count']}")
    
    logger.info("\nCategory Aggregates:")
    for category, stats in results.get('category_aggregates', {}).items():
        logger.info(f"\n  {category.upper()}:")
        logger.info(f"    Characters: {stats['character_count']}")
        logger.info(f"    Mean melodiousness: {stats['mean_melodiousness']:.1f}")
        logger.info(f"    Mean commonality: {stats['mean_commonality']:.1f}")
        logger.info(f"    Invented names: {stats['invented_pct']:.1f}%")
    
    if 'prediction_results' in results and 'role_prediction' in results['prediction_results']:
        pred = results['prediction_results']['role_prediction']
        logger.info(f"\nRole Prediction Accuracy: {pred['accuracy']:.3f}")
        logger.info(f"Cross-validation accuracy: {pred['cv_mean_accuracy']:.3f} ± {pred['cv_std_accuracy']:.3f}")
        logger.info(f"Better than chance: {pred['better_than_chance']}")
    
    logger.info("\n" + "="*80)


if __name__ == '__main__':
    sys.exit(main())

