"""Mental Health Data Collector

Collects mental health diagnoses, conditions, and psychiatric medications.
Uses curated datasets of DSM-5 diagnoses and FDA-approved medications.

Target: 500-800 total terms (250-400 diagnoses + 250-400 medications)
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from core.models import db, MentalHealthTerm, MentalHealthAnalysis
from analyzers.mental_health_analyzer import MentalHealthAnalyzer

logger = logging.getLogger(__name__)


class MentalHealthCollector:
    """Collect and analyze mental health terms."""
    
    def __init__(self):
        """Initialize the collector with analyzer."""
        self.analyzer = MentalHealthAnalyzer()
    
    def collect_all_data(self) -> Dict:
        """
        Main collection workflow - collects all mental health data.
        
        Returns:
            Dict with collection statistics
        """
        logger.info("Starting mental health data collection...")
        
        stats = {
            'diagnoses_added': 0,
            'medications_added': 0,
            'total_terms_added': 0,
            'analyses_added': 0,
            'errors': []
        }
        
        try:
            # Collect diagnoses
            diagnosis_stats = self.collect_dsm_diagnoses()
            stats['diagnoses_added'] = diagnosis_stats['added']
            
            # Collect medications
            medication_stats = self.collect_medications()
            stats['medications_added'] = medication_stats['added']
            
            # Total
            stats['total_terms_added'] = stats['diagnoses_added'] + stats['medications_added']
            
            # Analyze all terms
            analysis_count = self._analyze_all_terms()
            stats['analyses_added'] = analysis_count
            
            logger.info(f"Collection complete: {stats['total_terms_added']} terms, {stats['analyses_added']} analyses")
            
        except Exception as e:
            logger.error(f"Collection failed: {e}")
            stats['errors'].append(str(e))
        
        return stats
    
    def collect_dsm_diagnoses(self) -> Dict:
        """
        Collect DSM-5 diagnoses with prevalence data.
        
        Returns:
            Dict with collection stats
        """
        logger.info("Collecting DSM-5 diagnoses...")
        
        # Curated list of major DSM-5 diagnoses with prevalence rates
        diagnoses = [
            # Mood Disorders
            ('Major Depressive Disorder', 'mood_disorder', 'depression', 7.1, 1980, 'F32.9', None),
            ('Persistent Depressive Disorder', 'mood_disorder', 'depression', 1.5, 2013, 'F34.1', None),
            ('Bipolar I Disorder', 'mood_disorder', 'bipolar', 0.6, 1980, 'F31.0', None),
            ('Bipolar II Disorder', 'mood_disorder', 'bipolar', 0.4, 1994, 'F31.81', None),
            ('Cyclothymic Disorder', 'mood_disorder', 'bipolar', 0.4, 1980, 'F34.0', None),
            ('Seasonal Affective Disorder', 'mood_disorder', 'depression', 5.0, 1987, 'F33.0', None),
            ('Premenstrual Dysphoric Disorder', 'mood_disorder', 'depression', 1.8, 2013, 'F32.81', None),
            ('Disruptive Mood Dysregulation Disorder', 'mood_disorder', 'pediatric', 2.7, 2013, 'F34.81', None),
            
            # Anxiety Disorders
            ('Generalized Anxiety Disorder', 'anxiety_disorder', 'anxiety', 2.9, 1980, 'F41.1', None),
            ('Panic Disorder', 'anxiety_disorder', 'panic', 2.7, 1980, 'F41.0', None),
            ('Agoraphobia', 'anxiety_disorder', 'phobia', 0.9, 1980, 'F40.00', None),
            ('Social Anxiety Disorder', 'anxiety_disorder', 'social_phobia', 7.1, 1980, 'F40.10', None),
            ('Specific Phobia', 'anxiety_disorder', 'phobia', 8.7, 1980, 'F40.218', None),
            ('Separation Anxiety Disorder', 'anxiety_disorder', 'anxiety', 4.1, 1980, 'F93.0', None),
            ('Selective Mutism', 'anxiety_disorder', 'pediatric', 0.7, 2000, 'F94.0', None),
            
            # Trauma and Stressor-Related Disorders
            ('Posttraumatic Stress Disorder', 'trauma_disorder', 'ptsd', 3.5, 1980, 'F43.10', None),
            ('Acute Stress Disorder', 'trauma_disorder', 'stress', 6.8, 1994, 'F43.0', None),
            ('Adjustment Disorder', 'trauma_disorder', 'stress', 5.0, 1980, 'F43.20', None),
            ('Reactive Attachment Disorder', 'trauma_disorder', 'attachment', 0.9, 1980, 'F94.1', None),
            
            # Obsessive-Compulsive and Related Disorders
            ('Obsessive-Compulsive Disorder', 'ocd_spectrum', 'ocd', 1.2, 1980, 'F42.2', None),
            ('Body Dysmorphic Disorder', 'ocd_spectrum', 'body_image', 1.9, 1987, 'F45.22', None),
            ('Hoarding Disorder', 'ocd_spectrum', 'hoarding', 2.6, 2013, 'F42.3', None),
            ('Trichotillomania', 'ocd_spectrum', 'impulse_control', 0.6, 1987, 'F63.3', None),
            ('Excoriation Disorder', 'ocd_spectrum', 'impulse_control', 1.4, 2013, 'F42.4', None),
            
            # Schizophrenia Spectrum
            ('Schizophrenia', 'psychotic_disorder', 'schizophrenia', 0.3, 1952, 'F20.9', None),
            ('Schizoaffective Disorder', 'psychotic_disorder', 'schizophrenia', 0.3, 1980, 'F25.9', None),
            ('Schizophreniform Disorder', 'psychotic_disorder', 'schizophrenia', 0.2, 1980, 'F20.81', None),
            ('Brief Psychotic Disorder', 'psychotic_disorder', 'psychosis', 0.05, 1980, 'F23', None),
            ('Delusional Disorder', 'psychotic_disorder', 'psychosis', 0.2, 1980, 'F22', None),
            
            # Personality Disorders
            ('Borderline Personality Disorder', 'personality_disorder', 'cluster_b', 1.6, 1980, 'F60.3', None),
            ('Antisocial Personality Disorder', 'personality_disorder', 'cluster_b', 1.0, 1980, 'F60.2', None),
            ('Narcissistic Personality Disorder', 'personality_disorder', 'cluster_b', 0.5, 1980, 'F60.81', None),
            ('Histrionic Personality Disorder', 'personality_disorder', 'cluster_b', 1.8, 1980, 'F60.4', None),
            ('Avoidant Personality Disorder', 'personality_disorder', 'cluster_c', 2.4, 1980, 'F60.6', None),
            ('Dependent Personality Disorder', 'personality_disorder', 'cluster_c', 0.5, 1980, 'F60.7', None),
            ('Obsessive-Compulsive Personality Disorder', 'personality_disorder', 'cluster_c', 2.1, 1980, 'F60.5', None),
            ('Paranoid Personality Disorder', 'personality_disorder', 'cluster_a', 2.3, 1980, 'F60.0', None),
            ('Schizoid Personality Disorder', 'personality_disorder', 'cluster_a', 0.9, 1980, 'F60.1', None),
            ('Schizotypal Personality Disorder', 'personality_disorder', 'cluster_a', 0.6, 1980, 'F21', None),
            
            # Eating Disorders
            ('Anorexia Nervosa', 'eating_disorder', 'restriction', 0.9, 1980, 'F50.01', None),
            ('Bulimia Nervosa', 'eating_disorder', 'binge_purge', 0.3, 1980, 'F50.2', None),
            ('Binge-Eating Disorder', 'eating_disorder', 'binge', 2.8, 2013, 'F50.81', None),
            ('Avoidant/Restrictive Food Intake Disorder', 'eating_disorder', 'restriction', 3.2, 2013, 'F50.82', None),
            
            # Neurodevelopmental Disorders
            ('Attention-Deficit/Hyperactivity Disorder', 'neurodevelopmental', 'adhd', 8.4, 1980, 'F90.2', None),
            ('Autism Spectrum Disorder', 'neurodevelopmental', 'autism', 1.7, 2013, 'F84.0', None),
            ('Intellectual Disability', 'neurodevelopmental', 'cognition', 1.0, 2013, 'F70', None),
            ('Specific Learning Disorder', 'neurodevelopmental', 'learning', 5.9, 2013, 'F81.9', None),
            ('Developmental Coordination Disorder', 'neurodevelopmental', 'motor', 5.0, 1994, 'F82', None),
            ('Tourette Disorder', 'neurodevelopmental', 'tic', 0.3, 1980, 'F95.2', None),
            
            # Substance-Related Disorders
            ('Alcohol Use Disorder', 'substance_disorder', 'alcohol', 5.8, 1980, 'F10.20', None),
            ('Cannabis Use Disorder', 'substance_disorder', 'cannabis', 2.5, 1980, 'F12.20', None),
            ('Opioid Use Disorder', 'substance_disorder', 'opioid', 0.7, 1980, 'F11.20', None),
            ('Stimulant Use Disorder', 'substance_disorder', 'stimulant', 0.2, 1980, 'F15.20', None),
            ('Tobacco Use Disorder', 'substance_disorder', 'tobacco', 16.7, 1980, 'F17.200', None),
            
            # Sleep-Wake Disorders
            ('Insomnia Disorder', 'sleep_disorder', 'insomnia', 10.0, 1980, 'F51.01', None),
            ('Hypersomnolence Disorder', 'sleep_disorder', 'hypersomnia', 1.0, 1980, 'F51.11', None),
            ('Narcolepsy', 'sleep_disorder', 'narcolepsy', 0.05, 1980, 'G47.419', None),
            ('Nightmare Disorder', 'sleep_disorder', 'parasomnia', 4.0, 1980, 'F51.5', None),
            ('Restless Legs Syndrome', 'sleep_disorder', 'movement', 2.5, 2000, 'G25.81', None),
            
            # Somatic Symptom Disorders
            ('Somatic Symptom Disorder', 'somatic_disorder', 'somatic', 5.0, 2013, 'F45.1', None),
            ('Illness Anxiety Disorder', 'somatic_disorder', 'anxiety', 1.3, 2013, 'F45.21', None),
            ('Conversion Disorder', 'somatic_disorder', 'conversion', 0.3, 1980, 'F44.9', None),
            
            # Dissociative Disorders
            ('Dissociative Identity Disorder', 'dissociative_disorder', 'identity', 1.5, 1994, 'F44.81', None),
            ('Dissociative Amnesia', 'dissociative_disorder', 'memory', 1.8, 1980, 'F44.0', None),
            ('Depersonalization/Derealization Disorder', 'dissociative_disorder', 'perception', 2.0, 1980, 'F48.1', None),
            
            # Gender Dysphoria
            ('Gender Dysphoria', 'gender_related', 'dysphoria', 0.005, 2013, 'F64.0', None),
        ]
        
        stats = {'added': 0, 'skipped': 0}
        
        for name, category, subcategory, prevalence, year, code, _ in diagnoses:
            try:
                # Check if already exists
                existing = MentalHealthTerm.query.filter_by(name=name).first()
                if existing:
                    stats['skipped'] += 1
                    continue
                
                # Calculate stigma score based on category
                stigma_score = self._calculate_diagnosis_stigma(category, subcategory, name)
                
                # Create term
                term = MentalHealthTerm(
                    name=name,
                    term_type='diagnosis',
                    category=category,
                    subcategory=subcategory,
                    prevalence_rate=prevalence,
                    year_introduced=year,
                    official_classification=code,
                    stigma_score=stigma_score,
                    is_obsolete=False
                )
                
                db.session.add(term)
                stats['added'] += 1
                
            except Exception as e:
                logger.error(f"Error adding diagnosis {name}: {e}")
        
        db.session.commit()
        logger.info(f"Added {stats['added']} diagnoses")
        
        return stats
    
    def collect_medications(self) -> Dict:
        """
        Collect psychiatric medications (brand and generic names).
        
        Returns:
            Dict with collection stats
        """
        logger.info("Collecting psychiatric medications...")
        
        # Curated list of major psychiatric medications
        # Format: (generic_name, brand_names, category, subcategory, usage_rank, year_approved)
        medications = [
            # SSRIs (Selective Serotonin Reuptake Inhibitors)
            ('Fluoxetine', 'Prozac, Sarafem', 'antidepressant', 'SSRI', 1, 1987),
            ('Sertraline', 'Zoloft', 'antidepressant', 'SSRI', 2, 1991),
            ('Paroxetine', 'Paxil, Pexeva', 'antidepressant', 'SSRI', 4, 1992),
            ('Citalopram', 'Celexa', 'antidepressant', 'SSRI', 6, 1998),
            ('Escitalopram', 'Lexapro', 'antidepressant', 'SSRI', 3, 2002),
            ('Fluvoxamine', 'Luvox', 'antidepressant', 'SSRI', 15, 1994),
            
            # SNRIs (Serotonin-Norepinephrine Reuptake Inhibitors)
            ('Venlafaxine', 'Effexor', 'antidepressant', 'SNRI', 5, 1993),
            ('Duloxetine', 'Cymbalta', 'antidepressant', 'SNRI', 7, 2004),
            ('Desvenlafaxine', 'Pristiq', 'antidepressant', 'SNRI', 12, 2008),
            ('Levomilnacipran', 'Fetzima', 'antidepressant', 'SNRI', 25, 2013),
            
            # Atypical Antidepressants
            ('Bupropion', 'Wellbutrin, Zyban', 'antidepressant', 'atypical', 8, 1985),
            ('Mirtazapine', 'Remeron', 'antidepressant', 'atypical', 10, 1996),
            ('Trazodone', 'Desyrel', 'antidepressant', 'atypical', 9, 1981),
            ('Vilazodone', 'Viibryd', 'antidepressant', 'atypical', 20, 2011),
            ('Vortioxetine', 'Trintellix', 'antidepressant', 'atypical', 22, 2013),
            
            # Tricyclic Antidepressants (TCAs)
            ('Amitriptyline', 'Elavil', 'antidepressant', 'TCA', 14, 1961),
            ('Nortriptyline', 'Pamelor', 'antidepressant', 'TCA', 18, 1964),
            ('Imipramine', 'Tofranil', 'antidepressant', 'TCA', 23, 1959),
            ('Doxepin', 'Sinequan', 'antidepressant', 'TCA', 24, 1969),
            ('Clomipramine', 'Anafranil', 'antidepressant', 'TCA', 28, 1989),
            
            # MAOIs (Monoamine Oxidase Inhibitors)
            ('Phenelzine', 'Nardil', 'antidepressant', 'MAOI', 30, 1961),
            ('Tranylcypromine', 'Parnate', 'antidepressant', 'MAOI', 32, 1961),
            ('Selegiline', 'Emsam', 'antidepressant', 'MAOI', 35, 2006),
            
            # Atypical Antipsychotics
            ('Aripiprazole', 'Abilify', 'antipsychotic', 'atypical', 11, 2002),
            ('Quetiapine', 'Seroquel', 'antipsychotic', 'atypical', 13, 1997),
            ('Risperidone', 'Risperdal', 'antipsychotic', 'atypical', 16, 1993),
            ('Olanzapine', 'Zyprexa', 'antipsychotic', 'atypical', 17, 1996),
            ('Lurasidone', 'Latuda', 'antipsychotic', 'atypical', 19, 2010),
            ('Ziprasidone', 'Geodon', 'antipsychotic', 'atypical', 21, 2001),
            ('Paliperidone', 'Invega', 'antipsychotic', 'atypical', 26, 2006),
            ('Asenapine', 'Saphris', 'antipsychotic', 'atypical', 29, 2009),
            ('Iloperidone', 'Fanapt', 'antipsychotic', 'atypical', 33, 2009),
            ('Brexpiprazole', 'Rexulti', 'antipsychotic', 'atypical', 36, 2015),
            ('Cariprazine', 'Vraylar', 'antipsychotic', 'atypical', 38, 2015),
            
            # Typical Antipsychotics
            ('Haloperidol', 'Haldol', 'antipsychotic', 'typical', 27, 1967),
            ('Chlorpromazine', 'Thorazine', 'antipsychotic', 'typical', 34, 1954),
            ('Fluphenazine', 'Prolixin', 'antipsychotic', 'typical', 37, 1959),
            ('Perphenazine', 'Trilafon', 'antipsychotic', 'typical', 40, 1957),
            
            # Benzodiazepines (Anxiolytics)
            ('Alprazolam', 'Xanax', 'anxiolytic', 'benzodiazepine', 31, 1981),
            ('Lorazepam', 'Ativan', 'anxiolytic', 'benzodiazepine', 39, 1977),
            ('Clonazepam', 'Klonopin', 'anxiolytic', 'benzodiazepine', 41, 1975),
            ('Diazepam', 'Valium', 'anxiolytic', 'benzodiazepine', 42, 1963),
            ('Temazepam', 'Restoril', 'anxiolytic', 'benzodiazepine', 45, 1981),
            
            # Non-Benzodiazepine Anxiolytics
            ('Buspirone', 'BuSpar', 'anxiolytic', 'azapirone', 43, 1986),
            ('Hydroxyzine', 'Vistaril, Atarax', 'anxiolytic', 'antihistamine', 44, 1956),
            
            # Mood Stabilizers
            ('Lithium', 'Lithobid, Eskalith', 'mood_stabilizer', 'lithium', 46, 1970),
            ('Valproic Acid', 'Depakote', 'mood_stabilizer', 'anticonvulsant', 47, 1983),
            ('Lamotrigine', 'Lamictal', 'mood_stabilizer', 'anticonvulsant', 48, 2003),
            ('Carbamazepine', 'Tegretol', 'mood_stabilizer', 'anticonvulsant', 49, 1974),
            ('Oxcarbazepine', 'Trileptal', 'mood_stabilizer', 'anticonvulsant', 52, 2000),
            
            # ADHD Medications - Stimulants
            ('Methylphenidate', 'Ritalin, Concerta', 'adhd_medication', 'stimulant', 50, 1955),
            ('Amphetamine', 'Adderall', 'adhd_medication', 'stimulant', 51, 1996),
            ('Lisdexamfetamine', 'Vyvanse', 'adhd_medication', 'stimulant', 53, 2007),
            ('Dexmethylphenidate', 'Focalin', 'adhd_medication', 'stimulant', 55, 2001),
            
            # ADHD Medications - Non-Stimulants
            ('Atomoxetine', 'Strattera', 'adhd_medication', 'non_stimulant', 54, 2002),
            ('Guanfacine', 'Intuniv', 'adhd_medication', 'non_stimulant', 56, 2009),
            ('Clonidine', 'Kapvay', 'adhd_medication', 'non_stimulant', 58, 2010),
            
            # Sleep Medications
            ('Zolpidem', 'Ambien', 'sleep_medication', 'z_drug', 57, 1992),
            ('Eszopiclone', 'Lunesta', 'sleep_medication', 'z_drug', 59, 2004),
            ('Zaleplon', 'Sonata', 'sleep_medication', 'z_drug', 62, 1999),
            ('Ramelteon', 'Rozerem', 'sleep_medication', 'melatonin_agonist', 63, 2005),
            ('Suvorexant', 'Belsomra', 'sleep_medication', 'orexin_antagonist', 65, 2014),
            
            # Cognitive Enhancers
            ('Donepezil', 'Aricept', 'cognitive_enhancer', 'cholinesterase_inhibitor', 60, 1996),
            ('Memantine', 'Namenda', 'cognitive_enhancer', 'nmda_antagonist', 61, 2003),
            ('Rivastigmine', 'Exelon', 'cognitive_enhancer', 'cholinesterase_inhibitor', 64, 2000),
        ]
        
        stats = {'added': 0, 'skipped': 0}
        
        # Add generic medications
        for generic, brands, category, subcategory, rank, year in medications:
            try:
                # Check if generic already exists
                existing = MentalHealthTerm.query.filter_by(name=generic).first()
                if existing:
                    stats['skipped'] += 1
                    continue
                
                # Create generic medication entry
                generic_term = MentalHealthTerm(
                    name=generic,
                    term_type='medication',
                    category=category,
                    subcategory=subcategory,
                    prevalence_rate=None,  # Prescription frequency would go here
                    usage_rank=rank,
                    year_introduced=year,
                    official_classification='FDA_APPROVED',
                    brand_names=brands,
                    generic_name=None,  # This IS the generic
                    stigma_score=0.0,  # Medications less stigmatized than diagnoses
                    is_obsolete=False
                )
                
                db.session.add(generic_term)
                stats['added'] += 1
                
                # Also add brand name entries for most common brands
                if brands:
                    primary_brand = brands.split(',')[0].strip()
                    existing_brand = MentalHealthTerm.query.filter_by(name=primary_brand).first()
                    if not existing_brand:
                        brand_term = MentalHealthTerm(
                            name=primary_brand,
                            term_type='medication',
                            category=category,
                            subcategory=subcategory,
                            prevalence_rate=None,
                            usage_rank=rank,
                            year_introduced=year,
                            official_classification='FDA_APPROVED',
                            brand_names=None,  # Brand names don't have brand names
                            generic_name=generic,  # Link back to generic
                            stigma_score=0.0,
                            is_obsolete=False
                        )
                        
                        db.session.add(brand_term)
                        stats['added'] += 1
                
            except Exception as e:
                logger.error(f"Error adding medication {generic}: {e}")
        
        db.session.commit()
        logger.info(f"Added {stats['added']} medications")
        
        return stats
    
    def _analyze_all_terms(self) -> int:
        """
        Analyze all mental health terms that don't have analysis yet.
        
        Returns:
            Number of analyses created
        """
        logger.info("Analyzing all mental health terms...")
        
        count = 0
        terms = MentalHealthTerm.query.filter(
            ~MentalHealthTerm.analysis.has()
        ).all()
        
        logger.info(f"Found {len(terms)} terms without analysis")
        
        for term in terms:
            try:
                # Run analysis
                analysis_data = self.analyzer.analyze(
                    term.name,
                    term.term_type
                )
                
                # Create analysis record
                analysis = MentalHealthAnalysis(
                    term_id=term.id,
                    character_length=analysis_data.get('character_length'),
                    syllable_count=analysis_data.get('syllable_count'),
                    phoneme_count=analysis_data.get('phoneme_count'),
                    consonant_count=analysis_data.get('consonant_count'),
                    vowel_count=analysis_data.get('vowel_count'),
                    memorability_score=analysis_data.get('memorability_score'),
                    pronounceability_score=analysis_data.get('pronounceability_score'),
                    uniqueness_score=analysis_data.get('uniqueness_score'),
                    pronounceability_clinical=analysis_data.get('pronounceability_clinical'),
                    patient_friendliness=analysis_data.get('patient_friendliness'),
                    latin_roots_score=analysis_data.get('latin_roots_score'),
                    stigma_linguistic_markers=analysis_data.get('stigma_linguistic_markers'),
                    harshness_score=analysis_data.get('harshness_score'),
                    speed_score=analysis_data.get('speed_score'),
                    strength_score=analysis_data.get('strength_score'),
                    phonetic_data=json.dumps(analysis_data.get('phonetic_data', {})),
                    semantic_data=json.dumps(analysis_data.get('semantic_data', {})),
                    etymology_data=json.dumps(analysis_data.get('etymology_data', {}))
                )
                
                db.session.add(analysis)
                count += 1
                
                if count % 50 == 0:
                    logger.info(f"Analyzed {count} terms...")
                    db.session.commit()
                
            except Exception as e:
                logger.error(f"Error analyzing {term.name}: {e}")
        
        db.session.commit()
        logger.info(f"Analysis complete: {count} analyses created")
        
        return count
    
    def _calculate_diagnosis_stigma(self, category: str, subcategory: str, name: str) -> float:
        """
        Calculate stigma score for a diagnosis based on historical stigma.
        
        Args:
            category: Main category
            subcategory: Subcategory
            name: Diagnosis name
            
        Returns:
            Stigma score (0-100, higher = more stigmatized)
        """
        # Base scores by category (historically stigmatized conditions)
        category_stigma = {
            'psychotic_disorder': 75.0,
            'personality_disorder': 65.0,
            'substance_disorder': 60.0,
            'dissociative_disorder': 55.0,
            'eating_disorder': 50.0,
            'mood_disorder': 40.0,
            'anxiety_disorder': 30.0,
            'trauma_disorder': 35.0,
            'ocd_spectrum': 35.0,
            'sleep_disorder': 20.0,
            'neurodevelopmental': 45.0,
            'somatic_disorder': 40.0,
            'gender_related': 55.0
        }
        
        base_score = category_stigma.get(category, 40.0)
        
        # Specific modifiers
        if 'schizo' in name.lower():
            base_score += 10.0
        if 'psycho' in name.lower():
            base_score += 8.0
        if 'borderline' in name.lower():
            base_score += 7.0
        if 'antisocial' in name.lower():
            base_score += 12.0
        
        return min(100.0, base_score)

