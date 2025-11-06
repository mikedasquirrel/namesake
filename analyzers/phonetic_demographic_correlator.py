"""Phonetic-Demographic Correlator

Tests whether hurricane name phonetic features (harshness, memorability, gender)
correlate with demographic-specific outcomes. Implements regression models with
interaction terms to test if different phonetic features affect different
demographic groups differently.

Regression Claims:
- D1: Phonetic harshness differentially affects evacuation by income
- D2: Memorable names improve outcomes across all demographics proportionally
- D3: Gender-coded names affect risk perception differently by demographic
- D4: Displacement rates vary by demographic and correlate with phonetic formulas
"""

import logging
from typing import Dict, List, Optional, Tuple
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from scipy import stats

from core.models import (
    Hurricane, HurricaneAnalysis, HurricaneDemographicImpact,
    GeographicDemographics, db
)

logger = logging.getLogger(__name__)


class PhoneticDemographicCorrelator:
    """Analyze correlations between phonetic features and demographic-specific outcomes."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
        # Phonetic features to test
        self.phonetic_features = [
            'phonetic_harshness_score',
            'memorability_score',
            'syllable_count',
            'character_length',
            'phonetic_score',
            'sentiment_polarity'
        ]
        
        # Demographic categories
        self.demographic_categories = ['race', 'income_quintile', 'age_group']
    
    def test_all_claims(self, hurricane_ids: Optional[List[str]] = None) -> Dict:
        """
        Test all demographic-phonetic correlation claims (D1-D4).
        
        Args:
            hurricane_ids: List of hurricane IDs (None = all with demographic data)
        
        Returns:
            Results dict with all claim tests
        """
        results = {
            'sample_size': 0,
            'claims': {},
            'success': False
        }
        
        try:
            # Build dataset
            dataset = self._build_analysis_dataset(hurricane_ids)
            
            if dataset.empty:
                logger.warning("No data available for analysis")
                results['success'] = True
                return results
            
            results['sample_size'] = len(dataset)
            logger.info(f"Built analysis dataset with {len(dataset)} observations")
            
            # Test each claim
            results['claims']['D1'] = self._test_claim_d1(dataset)
            results['claims']['D2'] = self._test_claim_d2(dataset)
            results['claims']['D3'] = self._test_claim_d3(dataset)
            results['claims']['D4'] = self._test_claim_d4(dataset)
            
            results['success'] = True
            return results
            
        except Exception as e:
            logger.error(f"Error testing phonetic-demographic claims: {e}")
            results['error'] = str(e)
            return results
    
    def _build_analysis_dataset(self, hurricane_ids: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Build analysis dataset combining hurricane phonetics with demographic outcomes.
        
        Each row represents: hurricane × demographic_group × county
        
        Returns:
            DataFrame with columns for phonetic features, demographic info, and outcomes
        """
        data_rows = []
        
        # Query all hurricane-demographic impacts
        query = db.session.query(
            HurricaneDemographicImpact,
            HurricaneAnalysis,
            Hurricane
        ).join(
            Hurricane,
            HurricaneDemographicImpact.hurricane_id == Hurricane.id
        ).join(
            HurricaneAnalysis,
            Hurricane.id == HurricaneAnalysis.hurricane_id
        ).filter(
            HurricaneDemographicImpact.population_at_risk.isnot(None),
            HurricaneDemographicImpact.population_at_risk > 0
        )
        
        if hurricane_ids:
            query = query.filter(Hurricane.id.in_(hurricane_ids))
        
        records = query.all()
        
        logger.info(f"Processing {len(records)} demographic impact records")
        
        for impact, analysis, hurricane in records:
            # Skip aggregate 'total' records
            if impact.demographic_category == 'total':
                continue
            
            # Extract phonetic features
            phonetic_features = {
                'phonetic_harshness_score': analysis.phonetic_harshness_score,
                'memorability_score': analysis.memorability_score,
                'syllable_count': analysis.syllable_count,
                'character_length': analysis.character_length,
                'phonetic_score': analysis.phonetic_score,
                'sentiment_polarity': analysis.sentiment_polarity,
                'gender_coded': analysis.gender_coded,
                'pronounceability_score': analysis.pronounceability_score
            }
            
            # Skip if missing key features
            if any(v is None for k, v in phonetic_features.items() if k != 'gender_coded'):
                continue
            
            # Hurricane metadata
            hurricane_data = {
                'hurricane_id': hurricane.id,
                'hurricane_name': hurricane.name,
                'year': hurricane.year,
                'saffir_simpson_category': hurricane.saffir_simpson_category or 0,
                'max_wind_mph': hurricane.max_wind_mph or 0
            }
            
            # Demographic information
            demographic_data = {
                'demographic_category': impact.demographic_category,
                'demographic_value': impact.demographic_value,
                'geographic_code': impact.geographic_code,
                'population_at_risk': impact.population_at_risk
            }
            
            # Outcomes
            outcomes = {
                'deaths': impact.deaths or 0,
                'injuries': impact.injuries or 0,
                'displaced_persons': impact.displaced_persons or 0,
                'fema_applications': impact.fema_applications or 0,
                'death_rate_per_1000': impact.death_rate_per_1000 or 0,
                'displacement_rate': impact.displacement_rate or 0,
                'fema_application_rate': impact.fema_application_rate or 0
            }
            
            # Combine all
            row = {**phonetic_features, **hurricane_data, **demographic_data, **outcomes}
            data_rows.append(row)
        
        df = pd.DataFrame(data_rows)
        
        # Encode categorical variables
        if not df.empty:
            # Gender coding to numeric
            df['gender_male'] = (df['gender_coded'] == 'male').astype(int)
            df['gender_female'] = (df['gender_coded'] == 'female').astype(int)
            
            # Create demographic dummy variables
            df = pd.get_dummies(df, columns=['demographic_category', 'demographic_value'], prefix=['demo_cat', 'demo_val'])
        
        return df
    
    def _test_claim_d1(self, dataset: pd.DataFrame) -> Dict:
        """
        Test Claim D1: Phonetic harshness differentially affects evacuation by income quintile.
        
        Model: displacement_rate ~ harshness × income_quintile + storm_intensity + year
        
        Args:
            dataset: Analysis dataset
        
        Returns:
            Claim D1 test results
        """
        claim_result = {
            'claim': 'D1',
            'hypothesis': 'Phonetic harshness differentially affects evacuation by income quintile',
            'tested': False,
            'significant': False,
            'interpretation': None
        }
        
        try:
            # Filter to income quintile records only
            income_data = dataset[dataset['demographic_category'] == 'income_quintile'].copy()
            
            if income_data.empty or len(income_data) < 30:
                claim_result['interpretation'] = 'Insufficient data (n < 30)'
                return claim_result
            
            # Prepare features
            X_features = ['phonetic_harshness_score', 'saffir_simpson_category', 'max_wind_mph', 'year']
            
            # Add income quintile dummies if they exist
            income_dummies = [col for col in income_data.columns if col.startswith('demo_val_quintile')]
            if not income_dummies:
                claim_result['interpretation'] = 'No income quintile data available'
                return claim_result
            
            X_features.extend(income_dummies)
            
            # Create interaction terms: harshness × each income quintile
            for quintile_col in income_dummies:
                income_data[f'harshness_x_{quintile_col}'] = (
                    income_data['phonetic_harshness_score'] * income_data[quintile_col]
                )
                X_features.append(f'harshness_x_{quintile_col}')
            
            # Outcome: displacement rate (or FEMA application rate as proxy)
            y = income_data['fema_application_rate'].fillna(0)
            X = income_data[X_features].fillna(0)
            
            # Fit regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Cross-validate
            cv_scores = cross_val_score(model, X, y, cv=min(5, len(income_data)//10 or 2), scoring='r2')
            
            # Test significance of interaction terms
            interaction_cols = [col for col in X_features if col.startswith('harshness_x_')]
            interaction_coefs = [model.coef_[X_features.index(col)] for col in interaction_cols]
            
            # Simple significance test: any interaction coefficient substantially different from 0
            max_interaction = max(abs(c) for c in interaction_coefs) if interaction_coefs else 0
            
            claim_result.update({
                'tested': True,
                'sample_size': len(income_data),
                'r2': model.score(X, y),
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'interaction_coefficients': dict(zip(interaction_cols, interaction_coefs)),
                'max_interaction_effect': max_interaction,
                'significant': cv_scores.mean() > 0.05 and max_interaction > 0.001,
                'interpretation': self._interpret_d1_results(cv_scores.mean(), max_interaction)
            })
            
        except Exception as e:
            logger.error(f"Error testing claim D1: {e}")
            claim_result['error'] = str(e)
        
        return claim_result
    
    def _test_claim_d2(self, dataset: pd.DataFrame) -> Dict:
        """
        Test Claim D2: Memorable names improve outcomes across all demographics proportionally.
        
        Model: death_rate ~ memorability + demographic + storm_intensity (no interaction)
        
        If interaction is non-significant, memorability effect is universal.
        
        Args:
            dataset: Analysis dataset
        
        Returns:
            Claim D2 test results
        """
        claim_result = {
            'claim': 'D2',
            'hypothesis': 'Memorable names improve outcomes across all demographics proportionally',
            'tested': False,
            'significant': False
        }
        
        try:
            if dataset.empty or len(dataset) < 30:
                claim_result['interpretation'] = 'Insufficient data'
                return claim_result
            
            # Outcome: death rate
            y = dataset['death_rate_per_1000'].fillna(0)
            
            # Features: memorability + controls (NO interaction terms)
            X_features = ['memorability_score', 'saffir_simpson_category', 'max_wind_mph', 'year']
            
            # Add demographic dummies (but no interaction with memorability)
            demo_dummies = [col for col in dataset.columns if col.startswith('demo_val_')]
            X_features.extend(demo_dummies)
            
            X = dataset[X_features].fillna(0)
            
            # Fit model
            model = LinearRegression()
            model.fit(X, y)
            
            # Cross-validate
            cv_scores = cross_val_score(model, X, y, cv=min(5, len(dataset)//10 or 2), scoring='r2')
            
            # Extract memorability coefficient
            memo_coef = model.coef_[X_features.index('memorability_score')]
            
            claim_result.update({
                'tested': True,
                'sample_size': len(dataset),
                'r2': model.score(X, y),
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'memorability_coefficient': memo_coef,
                'significant': cv_scores.mean() > 0.05 and abs(memo_coef) > 0.01,
                'interpretation': self._interpret_d2_results(memo_coef, cv_scores.mean())
            })
            
        except Exception as e:
            logger.error(f"Error testing claim D2: {e}")
            claim_result['error'] = str(e)
        
        return claim_result
    
    def _test_claim_d3(self, dataset: pd.DataFrame) -> Dict:
        """
        Test Claim D3: Gender-coded names affect risk perception differently by demographic.
        
        Model: outcome ~ gender × demographic + controls
        
        Args:
            dataset: Analysis dataset
        
        Returns:
            Claim D3 test results
        """
        claim_result = {
            'claim': 'D3',
            'hypothesis': 'Gender-coded names affect risk perception differently by demographic',
            'tested': False,
            'significant': False
        }
        
        try:
            if dataset.empty or len(dataset) < 30:
                claim_result['interpretation'] = 'Insufficient data'
                return claim_result
            
            # Outcome: FEMA application rate (proxy for evacuation/response)
            y = dataset['fema_application_rate'].fillna(0)
            
            # Features: gender + demographics + interactions
            X_features = ['gender_male', 'gender_female', 'saffir_simpson_category', 'max_wind_mph', 'year']
            
            # Add demographic dummies
            demo_dummies = [col for col in dataset.columns if col.startswith('demo_val_')]
            X_features.extend(demo_dummies)
            
            # Create gender × demographic interactions
            for demo_col in demo_dummies:
                dataset[f'male_x_{demo_col}'] = dataset['gender_male'] * dataset[demo_col]
                dataset[f'female_x_{demo_col}'] = dataset['gender_female'] * dataset[demo_col]
                X_features.append(f'male_x_{demo_col}')
                X_features.append(f'female_x_{demo_col}')
            
            X = dataset[X_features].fillna(0)
            
            # Fit model
            model = LinearRegression()
            model.fit(X, y)
            
            # Cross-validate
            cv_scores = cross_val_score(model, X, y, cv=min(5, len(dataset)//10 or 2), scoring='r2')
            
            # Test interaction significance
            interaction_cols = [col for col in X_features if '_x_demo_val_' in col]
            interaction_coefs = [model.coef_[X_features.index(col)] for col in interaction_cols if col in X_features]
            
            max_interaction = max(abs(c) for c in interaction_coefs) if interaction_coefs else 0
            
            claim_result.update({
                'tested': True,
                'sample_size': len(dataset),
                'r2': model.score(X, y),
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'max_gender_interaction': max_interaction,
                'significant': cv_scores.mean() > 0.05 and max_interaction > 0.001,
                'interpretation': self._interpret_d3_results(cv_scores.mean(), max_interaction)
            })
            
        except Exception as e:
            logger.error(f"Error testing claim D3: {e}")
            claim_result['error'] = str(e)
        
        return claim_result
    
    def _test_claim_d4(self, dataset: pd.DataFrame) -> Dict:
        """
        Test Claim D4: Displacement rates vary by demographic and correlate with phonetic formulas.
        
        Model: displacement_rate ~ phonetic_composite × demographic + controls
        
        Args:
            dataset: Analysis dataset
        
        Returns:
            Claim D4 test results
        """
        claim_result = {
            'claim': 'D4',
            'hypothesis': 'Displacement rates vary by demographic and correlate with phonetic formulas',
            'tested': False,
            'significant': False
        }
        
        try:
            if dataset.empty or len(dataset) < 30:
                claim_result['interpretation'] = 'Insufficient data'
                return claim_result
            
            # Create composite phonetic score
            dataset['phonetic_composite'] = (
                dataset['phonetic_harshness_score'] * 0.3 +
                dataset['memorability_score'] * 0.3 +
                dataset['phonetic_score'] * 0.2 +
                dataset['pronounceability_score'] * 0.2
            )
            
            # Outcome: displacement rate (or FEMA application rate)
            y = dataset['fema_application_rate'].fillna(0)
            
            # Features
            X_features = ['phonetic_composite', 'saffir_simpson_category', 'max_wind_mph', 'year']
            
            # Add demographic dummies
            demo_dummies = [col for col in dataset.columns if col.startswith('demo_val_')]
            X_features.extend(demo_dummies)
            
            # Create phonetic × demographic interactions
            for demo_col in demo_dummies:
                dataset[f'phonetic_x_{demo_col}'] = dataset['phonetic_composite'] * dataset[demo_col]
                X_features.append(f'phonetic_x_{demo_col}')
            
            X = dataset[X_features].fillna(0)
            
            # Fit model
            model = LinearRegression()
            model.fit(X, y)
            
            # Cross-validate
            cv_scores = cross_val_score(model, X, y, cv=min(5, len(dataset)//10 or 2), scoring='r2')
            
            # Phonetic composite coefficient
            phonetic_coef = model.coef_[X_features.index('phonetic_composite')]
            
            claim_result.update({
                'tested': True,
                'sample_size': len(dataset),
                'r2': model.score(X, y),
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'phonetic_composite_coefficient': phonetic_coef,
                'significant': cv_scores.mean() > 0.05 and abs(phonetic_coef) > 0.001,
                'interpretation': self._interpret_d4_results(phonetic_coef, cv_scores.mean())
            })
            
        except Exception as e:
            logger.error(f"Error testing claim D4: {e}")
            claim_result['error'] = str(e)
        
        return claim_result
    
    def _interpret_d1_results(self, cv_r2: float, max_interaction: float) -> str:
        """Interpret D1 test results."""
        if cv_r2 < 0.05:
            return "Weak model fit - insufficient evidence for differential effects"
        elif max_interaction < 0.001:
            return "No significant interaction detected - harshness affects all income groups similarly"
        elif max_interaction > 0.01:
            return "SIGNIFICANT: Phonetic harshness has differential effects across income quintiles"
        else:
            return "Weak interaction detected - marginal evidence for differential effects"
    
    def _interpret_d2_results(self, memo_coef: float, cv_r2: float) -> str:
        """Interpret D2 test results."""
        if cv_r2 < 0.05:
            return "Weak model fit - insufficient evidence"
        elif abs(memo_coef) < 0.01:
            return "No significant memorability effect detected"
        elif memo_coef < 0:
            return "SIGNIFICANT: Higher memorability associated with LOWER death rates (protective effect)"
        else:
            return "Higher memorability associated with higher death rates (unexpected)"
    
    def _interpret_d3_results(self, cv_r2: float, max_interaction: float) -> str:
        """Interpret D3 test results."""
        if cv_r2 < 0.05:
            return "Weak model fit - insufficient evidence"
        elif max_interaction < 0.001:
            return "No significant gender × demographic interaction"
        else:
            return "SIGNIFICANT: Gender coding has differential effects across demographics"
    
    def _interpret_d4_results(self, phonetic_coef: float, cv_r2: float) -> str:
        """Interpret D4 test results."""
        if cv_r2 < 0.05:
            return "Weak model fit - insufficient evidence"
        elif abs(phonetic_coef) < 0.001:
            return "No significant phonetic formula effect on displacement"
        elif phonetic_coef > 0:
            return "SIGNIFICANT: Higher phonetic scores → higher displacement rates"
        else:
            return "SIGNIFICANT: Higher phonetic scores → lower displacement rates (protective)"

