"""Name Diversity Causal Analysis - Discovery Science Approach

Core question: Does name diversity cause economic prosperity, or vice versa?

Weber hypothesis: Protestant individualism → diverse names → economic dynamism
Reverse causality: Economic prosperity → parental choice → diverse names
Confounds: Education, literacy, urbanization independent of both

Analyses:
1. County-level U.S. regressions (diversity × GDP/entrepreneurship)
2. Germany temporal analysis (1945-2025 middle name adoption)
3. Immigration cohort analysis (generational assimilation patterns)
4. Quasi-experimental designs (policy changes, natural experiments)

Discovery orientation: Test competing causal stories
"""

import logging
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List
import warnings

warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NameDiversityCausalAnalysis:
    """Causal inference for name diversity and economic outcomes."""
    
    def __init__(self):
        self.results = {}
        
    def run_all_analyses(self) -> Dict[str, Any]:
        """Execute full causal analysis suite."""
        
        logger.info("="*70)
        logger.info("NAME DIVERSITY CAUSAL ANALYSIS - DISCOVERY MODE")
        logger.info("="*70)
        logger.info("Testing Weber hypothesis: Names → Economics vs Economics → Names")
        logger.info("="*70)
        
        # NOTE: This analysis requires data we don't have yet
        # Creating framework for when data becomes available
        
        self.results['framework'] = self._establish_causal_framework()
        self.results['county_analysis_design'] = self._design_county_analysis()
        self.results['germany_temporal_design'] = self._design_germany_analysis()
        self.results['immigration_design'] = self._design_immigration_analysis()
        self.results['quasi_experimental_opportunities'] = self._identify_natural_experiments()
        self.results['data_requirements'] = self._specify_data_needs()
        
        # Save
        self._save_results()
        self._generate_research_plan()
        
        return self.results
    
    def _establish_causal_framework(self) -> Dict[str, Any]:
        """Establish competing causal models."""
        
        return {
            'hypothesis_1_weber': {
                'direction': 'Names → Economics',
                'mechanism': 'Protestant individualism → name diversity → entrepreneurial culture → prosperity',
                'testable_predictions': [
                    'Name diversity precedes economic growth temporally',
                    'Protestant regions show both high diversity and high growth',
                    'Diversity predicts entrepreneurship rates',
                    'Cultural tightness/looseness mediates relationship'
                ],
                'required_data': [
                    'Historical name diversity (county-level, 1880-2020)',
                    'GDP growth rates',
                    'Business formation rates',
                    'Religious composition',
                    'Cultural values surveys'
                ]
            },
            
            'hypothesis_2_reverse_causality': {
                'direction': 'Economics → Names',
                'mechanism': 'Prosperity → education → individualism → parents choose rare names',
                'testable_predictions': [
                    'Economic growth precedes diversity increases',
                    'Wealth correlates with rare name selection',
                    'Education level predicts diversity',
                    'Naming diversity lags economic booms'
                ],
                'required_data': [
                    'Income trajectories',
                    'Education levels over time',
                    'Individual-level naming choices + SES',
                    'Temporal lag structures'
                ]
            },
            
            'hypothesis_3_common_cause': {
                'direction': 'Confound → Both',
                'mechanism': 'Literacy/urbanization → diversity AND prosperity independently',
                'testable_predictions': [
                    'Controlling for literacy eliminates correlation',
                    'Urbanization explains both',
                    'Immigration patterns account for relationship',
                    'Historical accidents (universities, ports) predict both'
                ],
                'required_data': [
                    'Literacy rates (historical)',
                    'Urbanization metrics',
                    'Immigration flows',
                    'Geographic/institutional variables'
                ]
            },
            
            'hypothesis_4_feedback_loop': {
                'direction': 'Bidirectional',
                'mechanism': 'Protestant culture → initial diversity → prosperity → reinforces diversity',
                'testable_predictions': [
                    'Granger causality in both directions',
                    'Effects strengthen over time',
                    'Catholic regions show weaker loops',
                    'Structural break tests identify loop initiation'
                ],
                'required_data': [
                    'Panel data (multiple time points)',
                    'Vector autoregression data',
                    'Regime change indicators'
                ]
            },
            
            'strongest_tests': {
                'regression_discontinuity': 'Geographic borders (Catholic/Protestant split)',
                'difference_in_differences': 'Germany 1945-1990 (East/West divide)',
                'instrumental_variables': 'Historical Protestant missionary activity',
                'panel_fixed_effects': 'Within-county changes over decades'
            }
        }
    
    def _design_county_analysis(self) -> Dict[str, Any]:
        """Design county-level U.S. economic outcome analysis."""
        
        return {
            'objective': 'Test whether name diversity predicts economic outcomes within U.S.',
            
            'data_sources': {
                'name_diversity': {
                    'source': 'SSA baby names by state (have this)',
                    'need': 'County-level SSA data (requires FOIA request or purchase)',
                    'alternative': 'Aggregate to state-level (weaker but feasible)',
                    'metrics': ['Shannon entropy', 'HHI', 'Gini', 'Top-10 concentration']
                },
                'economic_outcomes': {
                    'source': 'Bureau of Economic Analysis, Census Bureau',
                    'variables': [
                        'GDP per capita',
                        'Personal income',
                        'Business formation rate (new employer firms per 1000 pop)',
                        'Patent rates (USPTO)',
                        'Employment growth',
                        'Income inequality (Gini)'
                    ]
                },
                'controls': {
                    'demographic': ['Population', 'Age structure', 'Race/ethnicity', 'Immigration rate'],
                    'educational': ['College degree %', 'High school %', 'School quality'],
                    'geographic': ['Urbanization', 'Coastal', 'Climate', 'Natural resources'],
                    'institutional': ['Tax rates', 'Regulation indexes', 'University presence'],
                    'cultural': ['Religious composition', 'Political lean', 'Social capital indexes']
                }
            },
            
            'regression_specifications': {
                'baseline': 'GDP_pc ~ name_diversity + controls',
                'lagged': 'GDP_pc_2020 ~ name_diversity_1990 + controls_1990',
                'growth': 'GDP_growth_2010_2020 ~ name_diversity_2010 + controls',
                'fixed_effects': 'GDP_pc ~ name_diversity + county_FE + year_FE',
                'instrumental_variable': 'name_diversity ~ historical_protestant_share; GDP_pc ~ predicted_diversity'
            },
            
            'expected_results': {
                'if_weber_correct': 'Positive coefficient, robust to controls, precedence in lagged models',
                'if_reverse_causality': 'Insignificant when lagged, income predicts diversity better',
                'if_confounded': 'Coefficient disappears with education/urbanization controls'
            },
            
            'feasibility': {
                'state_level': 'FEASIBLE NOW - have SSA state data',
                'county_level': 'REQUIRES DATA PURCHASE (~$500-2000)',
                'individual_level': 'REQUIRES CENSUS MICRODATA (restricted access)'
            }
        }
    
    def _design_germany_analysis(self) -> Dict[str, Any]:
        """Design Germany temporal analysis (middle name adoption 1945-2025)."""
        
        return {
            'objective': 'Test whether middle name adoption tracks liberalization/Americanization',
            
            'natural_experiment': {
                'treatment': 'West Germany (Allied occupation, market economy)',
                'control': 'East Germany (Soviet occupation, planned economy)',
                'pre_period': '1930-1945',
                'post_period': '1945-1990',
                'reunification': '1990-2025'
            },
            
            'hypothesis': {
                'prediction': 'West Germany adopts middle names faster than East (1945-1990)',
                'mechanism': 'American cultural influence + economic liberalization → individualism → middle names',
                'alternative': 'Middle names driven by wealth, not culture'
            },
            
            'data_sources': {
                'birth_records': {
                    'source': 'German Federal Statistical Office (Destatis)',
                    'availability': 'Public aggregated data available',
                    'cost': 'Free for researcher access',
                    'variables': ['Middle name prevalence by year', 'By region (Länder)']
                },
                'economic_indicators': {
                    'source': 'World Bank, OECD',
                    'variables': ['GDP per capita (West vs East)', 'Income', 'Trade openness']
                },
                'cultural_indicators': {
                    'source': 'World Values Survey, European Values Study',
                    'variables': ['Individualism scores', 'Self-expression values', 'Secular values']
                }
            },
            
            'analysis_plan': {
                'difference_in_differences': {
                    'formula': 'middle_name_rate ~ post_1945 × west_germany + year + region',
                    'interpretation': 'DiD coefficient = treatment effect of Western influence'
                },
                'interrupted_time_series': {
                    'breakpoints': [1945, 1990],
                    'test': 'Slope change at breakpoints'
                },
                'synthetic_control': {
                    'treated_unit': 'West Germany',
                    'donor_pool': ['Austria', 'Switzerland', 'Netherlands', 'Belgium'],
                    'outcome': 'Middle name adoption rate',
                    'treatment': '1945 occupation'
                }
            },
            
            'expected_patterns': {
                'if_cultural_influence': 'West diverges from East 1945-1990, convergence post-1990',
                'if_wealth_driven': 'Both West and East track GDP, no cultural effect',
                'if_secular_modernization': 'Both adopt middle names, no East/West gap'
            },
            
            'feasibility': 'HIGH - German data is well-documented and accessible'
        }
    
    def _design_immigration_analysis(self) -> Dict[str, Any]:
        """Design immigration cohort analysis (generational assimilation)."""
        
        return {
            'objective': 'Test naming assimilation patterns across immigrant generations',
            
            'hypothesis': {
                'prediction': 'Each generation adopts U.S. naming patterns (diversity, rare names, middle names)',
                'mechanism': 'Cultural assimilation → naming Americanization',
                'alternative': 'SES, not generation, drives naming patterns'
            },
            
            'data_sources': {
                'census_microdata': {
                    'source': 'IPUMS (Integrated Public Use Microdata Series)',
                    'access': 'Free for researchers',
                    'variables': [
                        'Name (in recent censuses)',
                        'Nativity (1st gen, 2nd gen, 3rd+ gen)',
                        'Parents nativity',
                        'Country of origin',
                        'Year of immigration',
                        'Income, education, occupation',
                        'Language spoken at home'
                    ]
                },
                'name_diversity_metrics': {
                    'by_generation': ['1st gen', '2nd gen', '3rd+ gen'],
                    'by_origin': ['Mexico', 'China', 'India', 'Philippines', 'Vietnam', etc.],
                    'metrics': ['Rare name rate', 'American name rate', 'Middle name rate', 'Diversity entropy']
                }
            },
            
            'analysis_plan': {
                'cross_generational_regression': {
                    'formula': 'name_diversity ~ generation + origin + income + education + year',
                    'test': 'Generation coefficient positive and significant'
                },
                'within_family_analysis': {
                    'design': 'Compare siblings naming patterns within families',
                    'test': 'Later children more assimilated names than earlier'
                },
                'origin_heterogeneity': {
                    'test': 'Do all origin groups assimilate at same rate?',
                    'prediction': 'European groups faster, Asian groups slower (language barriers)'
                }
            },
            
            'expected_patterns': {
                '1st_generation': 'Maintain home country naming patterns',
                '2nd_generation': 'Hybrid - some assimilation, retain ethnic markers',
                '3rd_generation': 'Fully Americanized - indistinguishable from natives'
            },
            
            'feasibility': 'MEDIUM - Requires IPUMS data access (free but application process)'
        }
    
    def _identify_natural_experiments(self) -> Dict[str, Any]:
        """Identify natural experiments for causal inference."""
        
        return {
            'experiment_1_protestant_reformation_borders': {
                'design': 'Regression discontinuity at Catholic/Protestant historical borders',
                'geography': 'Germany/Austria border, Swiss cantons, Netherlands/Belgium',
                'treatment': 'Protestant influence (exogenous due to historical accident)',
                'outcome': 'Modern name diversity',
                'assumption': 'Cultural practices persist across centuries',
                'feasibility': 'HIGH - good geographic data available'
            },
            
            'experiment_2_communist_regimes': {
                'design': 'Difference-in-differences for communist periods',
                'treatment_group': 'East Germany 1945-1990, Czech Republic 1948-1989',
                'control_group': 'West Germany, Austria',
                'hypothesis': 'Communist suppression of individualism → lower name diversity',
                'test': 'DiD on diversity before/during/after communism',
                'feasibility': 'MEDIUM - requires historical Eastern European data'
            },
            
            'experiment_3_immigrant_waves': {
                'design': 'Instrumental variable using immigrant settlement patterns',
                'instrument': 'Historical railroad/port locations predict immigrant density',
                'first_stage': 'Railroad → immigrant settlement',
                'second_stage': 'Immigrant settlement → name diversity',
                'exclusion': 'Railroads affect diversity only through immigration',
                'feasibility': 'MEDIUM - good historical data, questionable exclusion restriction'
            },
            
            'experiment_4_education_policy_shocks': {
                'design': 'Compulsory education law changes as shock',
                'treatment': 'States that raised mandatory schooling years',
                'timing': 'Progressive era (1900-1920) state-by-state variation',
                'hypothesis': 'Education → literacy → name diversity',
                'test': 'Event study around policy adoption',
                'feasibility': 'MEDIUM - education policy data available, name data sparse pre-1920'
            },
            
            'experiment_5_social_security_act_1935': {
                'design': 'Interrupted time series around SSA 1935',
                'hypothesis': 'SSA required formal name registration → diversity increase',
                'alternative': 'No effect - names already formalized',
                'test': 'Structural break test at 1935',
                'feasibility': 'HIGH - we have data 1880-2024'
            }
        }
    
    def _specify_data_needs(self) -> Dict[str, Any]:
        """Specify exact data requirements for causal analysis."""
        
        return {
            'tier_1_critical': {
                'county_level_names': {
                    'source': 'SSA FOIA request or commercial data',
                    'cost': '$500-2000',
                    'urgency': 'HIGH',
                    'unlocks': 'County-level economic regressions'
                },
                'census_microdata': {
                    'source': 'IPUMS',
                    'cost': 'Free (application)',
                    'urgency': 'HIGH',
                    'unlocks': 'Immigration cohort analysis'
                },
                'german_birth_records': {
                    'source': 'Destatis',
                    'cost': 'Free for researchers',
                    'urgency': 'MEDIUM',
                    'unlocks': 'Germany temporal analysis'
                }
            },
            
            'tier_2_important': {
                'county_economic_data': {
                    'source': 'BEA, Census Bureau',
                    'cost': 'Free (public data)',
                    'urgency': 'MEDIUM',
                    'status': 'Can download now'
                },
                'world_values_survey': {
                    'source': 'WVS website',
                    'cost': 'Free',
                    'urgency': 'MEDIUM',
                    'status': 'Can download now'
                },
                'religious_congregation_data': {
                    'source': 'ARDA (Association of Religion Data Archives)',
                    'cost': 'Free',
                    'urgency': 'LOW',
                    'status': 'Available'
                }
            },
            
            'tier_3_nice_to_have': {
                'european_names_panel': {
                    'countries': ['Austria', 'Netherlands', 'Belgium', 'Switzerland'],
                    'cost': 'Varies by country',
                    'urgency': 'LOW',
                    'unlocks': 'Protestant border analysis'
                },
                'patent_data': {
                    'source': 'USPTO',
                    'cost': 'Free',
                    'urgency': 'LOW',
                    'unlocks': 'Innovation outcome measure'
                }
            },
            
            'immediate_action_items': [
                '1. Submit IPUMS data application (immigration analysis)',
                '2. Download county economic data from BEA (free)',
                '3. Request SSA county-level data quote',
                '4. Contact Destatis for German data access',
                '5. Aggregate existing state-level SSA to test methods'
            ]
        }
    
    def _save_results(self):
        """Save results."""
        
        output_dir = Path(__file__).parent.parent / 'analysis_outputs' / 'name_diversity_causal'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'causal_framework_{timestamp}.json'
        
        with output_file.open('w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ Causal framework saved to: {output_file}")
        logger.info(f"{'='*70}")
    
    def _generate_research_plan(self):
        """Generate research execution plan."""
        
        print("\n" + "="*70)
        print("NAME DIVERSITY CAUSAL ANALYSIS - RESEARCH PLAN")
        print("="*70)
        
        print("\nCOMPETING HYPOTHESES:")
        print("  1. Weber: Names → Economics (Protestant individualism)")
        print("  2. Reverse: Economics → Names (prosperity enables choice)")
        print("  3. Confound: Education/Urbanization → Both")
        print("  4. Feedback: Bidirectional reinforcing loop")
        
        print("\nSTRONGEST TESTS:")
        framework = self.results.get('framework', {})
        if 'strongest_tests' in framework:
            for test, description in framework['strongest_tests'].items():
                print(f"  - {test}: {description}")
        
        print("\nIMMEDIATE ACTIONS:")
        data_needs = self.results.get('data_requirements', {})
        if 'immediate_action_items' in data_needs:
            for action in data_needs['immediate_action_items']:
                print(f"  {action}")
        
        print("\nFEASIBILITY ASSESSMENT:")
        print("  - State-level analysis: CAN DO NOW (have data)")
        print("  - County-level: Requires data purchase ($500-2000)")
        print("  - Immigration: Requires IPUMS application (free, 2-4 weeks)")
        print("  - Germany: Requires international data request (2-8 weeks)")
        
        print("\nEXPECTED TIMELINE:")
        print("  - Month 1: State-level preliminary analyses")
        print("  - Month 2: Data acquisition (IPUMS, county data)")
        print("  - Month 3: County-level regressions")
        print("  - Month 4: Immigration cohort analysis")
        print("  - Month 5: Germany temporal analysis")
        print("  - Month 6: Synthesis and manuscript writing")
        
        print("\n" + "="*70)
        print("CONCLUSION:")
        print("  Causal framework established.")
        print("  Multiple competing explanations testable.")
        print("  Natural experiments identified.")
        print("  Data requirements specified.")
        print("  Ready to execute when data acquired.")
        print("="*70 + "\n")


def main():
    """Run name diversity causal analysis framework."""
    
    analyzer = NameDiversityCausalAnalysis()
    results = analyzer.run_all_analyses()
    
    return results


if __name__ == '__main__':
    main()

