#!/usr/bin/env python3
"""
Populate Missing Data - Analyze Names for All 3,500 Cryptos
Run this script to analyze all cryptocurrency names in the database
"""

from app import app, db, Cryptocurrency, NameAnalysis
from analyzers.name_analyzer import NameAnalyzer
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_all_names():
    """Analyze names for ALL cryptos in database"""
    with app.app_context():
        analyzer = NameAnalyzer()
        
        # Get all cryptos
        all_cryptos = Cryptocurrency.query.all()
        logger.info(f"Found {len(all_cryptos)} cryptocurrencies in database")
        
        # Get all names for uniqueness calculation
        all_names = [c.name for c in all_cryptos]
        
        added = 0
        skipped = 0
        
        for i, crypto in enumerate(all_cryptos):
            if i % 100 == 0:
                logger.info(f"Progress: {i}/{len(all_cryptos)}")
            
            # Check if analysis exists
            existing = NameAnalysis.query.filter_by(crypto_id=crypto.id).first()
            if existing:
                skipped += 1
                continue
            
            try:
                # Analyze the name
                analysis_result = analyzer.analyze_name(crypto.name, all_names)
                
                # Create NameAnalysis record
                name_analysis = NameAnalysis(
                    crypto_id=crypto.id,
                    syllable_count=analysis_result.get('syllable_count'),
                    character_length=analysis_result.get('character_length'),
                    word_count=analysis_result.get('word_count'),
                    phonetic_score=analysis_result.get('phonetic_score'),
                    vowel_ratio=analysis_result.get('vowel_ratio'),
                    consonant_clusters=analysis_result.get('consonant_clusters'),
                    memorability_score=analysis_result.get('memorability_score'),
                    pronounceability_score=analysis_result.get('pronounceability_score'),
                    name_type=analysis_result.get('name_type'),
                    category_tags=json.dumps(analysis_result.get('category_tags', [])),
                    uniqueness_score=analysis_result.get('uniqueness_score'),
                    has_numbers=analysis_result.get('has_numbers'),
                    has_special_chars=analysis_result.get('has_special_chars'),
                    capital_pattern=analysis_result.get('capital_pattern'),
                    is_real_word=analysis_result.get('is_real_word')
                )
                
                db.session.add(name_analysis)
                added += 1
                
                # Commit every 100 to avoid memory issues
                if added % 100 == 0:
                    db.session.commit()
                    logger.info(f"Committed {added} name analyses...")
            
            except Exception as e:
                logger.error(f"Error analyzing {crypto.name}: {e}")
                db.session.rollback()
        
        # Final commit
        db.session.commit()
        
        logger.info("="*60)
        logger.info(f"NAME ANALYSIS COMPLETE!")
        logger.info(f"  Added: {added}")
        logger.info(f"  Already existed: {skipped}")
        logger.info(f"  Total: {len(all_cryptos)}")
        logger.info("="*60)
        
        return {'added': added, 'skipped': skipped, 'total': len(all_cryptos)}

if __name__ == '__main__':
    print("\n" + "="*60)
    print("ANALYZING ALL CRYPTOCURRENCY NAMES")
    print("="*60)
    print("This will analyze ~2,500 missing names (FAST - no API calls)")
    print("Estimated time: 2-3 minutes")
    print("="*60 + "\n")
    
    result = analyze_all_names()
    
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print(f"   Names analyzed: {result['added']}")
    print(f"   Already existed: {result['skipped']}")
    print(f"   Total in database: {result['total']}")
    print("="*60)
    print("\nNow run: curl -X POST http://localhost:PORT/api/admin/clear-cache")
    print("Then refresh your validation page!")
    print("="*60 + "\n")

