"""
Data Acquisition Module
Downloads and caches name datasets from official sources across countries.
"""

import os
import json
import pandas as pd
import requests
from pathlib import Path
from typing import Dict, List, Optional
import time
from datetime import datetime
import zipfile
import io

class NameDataAcquisition:
    """Handles downloading and caching of name datasets from multiple countries."""
    
    def __init__(self, cache_dir: str = "data/raw"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = {}
        self.metadata_file = self.cache_dir / "acquisition_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load acquisition metadata if it exists."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
    
    def _save_metadata(self):
        """Save acquisition metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def download_usa_ssa_names(self, force_refresh: bool = False) -> Path:
        """
        Download U.S. Social Security Administration baby names data.
        Covers 1880-present for given names.
        Returns path to cached data.
        """
        cache_path = self.cache_dir / "usa_ssa_names"
        cache_path.mkdir(exist_ok=True)
        
        if not force_refresh and (cache_path / "names_complete.csv").exists():
            print("✓ U.S. SSA data already cached")
            return cache_path
        
        print("Downloading U.S. SSA baby names data...")
        url = "https://www.ssa.gov/oact/babynames/names.zip"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=60, headers=headers)
            response.raise_for_status()
            
            # Extract zip file
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(cache_path)
            
            # Consolidate all yearly files
            all_data = []
            for year_file in sorted(cache_path.glob("yob*.txt")):
                year = int(year_file.stem.replace("yob", ""))
                df = pd.read_csv(year_file, names=["name", "sex", "count"])
                df["year"] = year
                all_data.append(df)
            
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(cache_path / "names_complete.csv", index=False)
            
            self.metadata["usa_ssa"] = {
                "source": "U.S. Social Security Administration",
                "url": url,
                "downloaded": datetime.now().isoformat(),
                "years": f"{combined['year'].min()}-{combined['year'].max()}",
                "records": len(combined)
            }
            self._save_metadata()
            
            print(f"✓ Downloaded {len(combined):,} U.S. name records")
            return cache_path
            
        except Exception as e:
            print(f"✗ Error downloading U.S. SSA data: {e}")
            print("  Creating manual download instructions...")
            
            instructions = pd.DataFrame({
                "source": ["U.S. Social Security Administration"],
                "url": [url],
                "format": ["ZIP file containing yearly text files (yobYYYY.txt)"],
                "manual_steps": ["Download names.zip, extract to this folder, rerun script"]
            })
            instructions.to_csv(cache_path / "download_instructions.csv", index=False)
            
            self.metadata["usa_ssa"] = {
                "source": "U.S. Social Security Administration",
                "url": url,
                "status": "manual_download_required"
            }
            self._save_metadata()
            
            return cache_path
    
    def download_uk_ons_names(self, force_refresh: bool = False) -> Path:
        """
        Download UK Office for National Statistics baby names.
        Coverage: England & Wales, 1996-present.
        """
        cache_path = self.cache_dir / "uk_ons_names"
        cache_path.mkdir(exist_ok=True)
        
        if not force_refresh and (cache_path / "uk_names.csv").exists():
            print("✓ UK ONS data already cached")
            return cache_path
        
        print("Downloading UK ONS baby names data...")
        # Note: UK data requires manual construction from multiple sources
        # For now, create a placeholder structure
        
        # Primary source URLs (these change yearly, so we create a flexible loader)
        base_urls = {
            "england_wales": "https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/babynamesenglandandwalesbabynamesstatisticsgirls"
        }
        
        # Create placeholder with instructions
        instructions = pd.DataFrame({
            "note": ["UK data requires manual download from ONS website"],
            "url": [base_urls["england_wales"]],
            "years_available": ["1996-2023"],
            "format": ["Excel files, multiple sheets"]
        })
        instructions.to_csv(cache_path / "download_instructions.csv", index=False)
        
        self.metadata["uk_ons"] = {
            "source": "UK Office for National Statistics",
            "status": "manual_download_required",
            "base_url": base_urls["england_wales"],
            "expected_years": "1996-2023"
        }
        self._save_metadata()
        
        print("✓ UK data structure created (manual download required)")
        return cache_path
    
    def download_canada_names(self, force_refresh: bool = False) -> Path:
        """
        Download Canadian baby names from provincial sources.
        Primary source: Statistics Canada
        """
        cache_path = self.cache_dir / "canada_names"
        cache_path.mkdir(exist_ok=True)
        
        if not force_refresh and (cache_path / "canada_names.csv").exists():
            print("✓ Canada data already cached")
            return cache_path
        
        print("Downloading Canadian baby names data...")
        
        # Create structure for manual curation
        instructions = pd.DataFrame({
            "province": ["Ontario", "Quebec", "British Columbia", "Alberta"],
            "data_source": [
                "ServiceOntario",
                "Retraite Québec",
                "BC Vital Statistics",
                "Alberta Vital Statistics"
            ],
            "years_available": ["1917-present", "1980-present", "2000-present", "1980-present"]
        })
        instructions.to_csv(cache_path / "provincial_sources.csv", index=False)
        
        self.metadata["canada"] = {
            "source": "Provincial vital statistics agencies",
            "status": "manual_aggregation_required",
            "coverage": "varies by province"
        }
        self._save_metadata()
        
        print("✓ Canada data structure created (manual aggregation required)")
        return cache_path
    
    def create_mexico_structure(self) -> Path:
        """
        Create structure for Mexican name data.
        Mexico uses compound names and double surnames - requires special handling.
        """
        cache_path = self.cache_dir / "mexico_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating Mexico name data structure...")
        
        metadata = pd.DataFrame({
            "aspect": ["given_names", "surnames", "source", "note"],
            "description": [
                "Compound given names common (e.g., María José, Juan Carlos)",
                "Double surnames: paternal + maternal",
                "INEGI (Instituto Nacional de Estadística y Geografía)",
                "Naming structure differs significantly from Anglo naming"
            ]
        })
        metadata.to_csv(cache_path / "naming_conventions.csv", index=False)
        
        self.metadata["mexico"] = {
            "source": "INEGI",
            "naming_structure": "compound_given_double_surname",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ Mexico naming convention structure created")
        return cache_path
    
    def create_spain_structure(self) -> Path:
        """
        Create structure for Spanish name data.
        Spain: similar double surname system to Mexico, INE source.
        """
        cache_path = self.cache_dir / "spain_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating Spain name data structure...")
        
        metadata = pd.DataFrame({
            "aspect": ["surname_system", "source", "availability"],
            "description": [
                "Double surnames: primer apellido padre, primer apellido madre",
                "INE - Instituto Nacional de Estadística",
                "Data available from 1980s-present"
            ]
        })
        metadata.to_csv(cache_path / "naming_conventions.csv", index=False)
        
        self.metadata["spain"] = {
            "source": "INE Spain",
            "naming_structure": "double_surname",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ Spain naming convention structure created")
        return cache_path
    
    def create_brazil_structure(self) -> Path:
        """
        Create structure for Brazilian name data.
        Portuguese naming conventions, IBGE source.
        """
        cache_path = self.cache_dir / "brazil_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating Brazil name data structure...")
        
        metadata = pd.DataFrame({
            "aspect": ["given_names", "surnames", "source", "note"],
            "description": [
                "Multiple given names very common (Maria/João + additional names)",
                "Multiple surnames from both parents, flexible order",
                "IBGE - Instituto Brasileiro de Geografia e Estatística",
                "High diversity in compound name structures"
            ]
        })
        metadata.to_csv(cache_path / "naming_conventions.csv", index=False)
        
        self.metadata["brazil"] = {
            "source": "IBGE",
            "naming_structure": "compound_flexible",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ Brazil naming convention structure created")
        return cache_path
    
    def create_germany_structure(self) -> Path:
        """
        Create structure for German name data.
        Single surname, middle names less common historically.
        """
        cache_path = self.cache_dir / "germany_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating Germany name data structure...")
        
        metadata = pd.DataFrame({
            "aspect": ["historical_pattern", "modern_trend", "source", "note"],
            "description": [
                "Traditional: single given name, single surname",
                "Post-1950: middle names increasingly common (American influence)",
                "Statistisches Bundesamt (Destatis) / Gesellschaft für deutsche Sprache",
                "Key comparison for middle name adoption over time"
            ]
        })
        metadata.to_csv(cache_path / "naming_conventions.csv", index=False)
        
        self.metadata["germany"] = {
            "source": "Destatis / GfdS",
            "naming_structure": "single_surname_optional_middle",
            "middle_name_trend": "increasing_post_1950",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ Germany naming convention structure created")
        return cache_path
    
    def create_china_structure(self) -> Path:
        """
        Create structure for Chinese name data.
        Family name first, given name second (usually 1-2 characters).
        """
        cache_path = self.cache_dir / "china_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating China name data structure...")
        
        metadata = pd.DataFrame({
            "aspect": ["name_order", "structure", "source", "concentration", "note"],
            "description": [
                "Family name (姓) + given name (名) - surname FIRST",
                "Surname: 1-2 characters; Given name: 1-2 characters",
                "National Bureau of Statistics / Ministry of Public Security",
                "Top 3 surnames (Wang, Li, Zhang) cover ~20% of population",
                "Top 100 surnames cover ~85% - extreme concentration"
            ]
        })
        metadata.to_csv(cache_path / "naming_conventions.csv", index=False)
        
        # Create placeholder for common surnames with their prevalence
        common_surnames = pd.DataFrame({
            "surname_pinyin": ["Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", "Zhou"],
            "surname_chinese": ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周"],
            "approx_percentage": [7.25, 7.19, 6.83, 5.38, 4.53, 3.08, 2.23, 2.29, 2.05, 2.10],
            "rank": list(range(1, 11))
        })
        common_surnames.to_csv(cache_path / "top_surnames.csv", index=False)
        
        self.metadata["china"] = {
            "source": "NBS China / MPS",
            "naming_structure": "surname_first_given_second",
            "surname_concentration": "extreme_top_100_covers_85pct",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ China naming convention structure created")
        return cache_path
    
    def create_india_structure(self) -> Path:
        """
        Create structure for Indian name data.
        Extremely diverse: regional, religious, caste-based naming systems.
        """
        cache_path = self.cache_dir / "india_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating India name data structure...")
        
        metadata = pd.DataFrame({
            "system": ["North_India", "South_India", "Muslim", "Sikh", "Christian"],
            "pattern": [
                "Given + family name",
                "Initial(s) + given name + village/family",
                "Arabic names - Muhammad variants common",
                "Given + Singh (M) / Kaur (F)",
                "Western-style given + surname"
            ],
            "diversity": ["Medium", "High", "Low (concentrated)", "Low (Singh/Kaur)", "Medium-High"]
        })
        metadata.to_csv(cache_path / "naming_systems.csv", index=False)
        
        # Muhammad prevalence estimate
        muslim_names = pd.DataFrame({
            "name": ["Muhammad/Mohammed variants"],
            "estimated_muslim_population_pct": ["~15-20%"],
            "national_male_population_pct": ["~2-3% (Muslims ~14% of population)"],
            "note": ["Extremely common within Muslim community"]
        })
        muslim_names.to_csv(cache_path / "dominant_names.csv", index=False)
        
        self.metadata["india"] = {
            "source": "Census of India",
            "naming_structure": "highly_regional_religious_variation",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ India naming convention structure created")
        return cache_path
    
    def create_egypt_structure(self) -> Path:
        """
        Create structure for Egyptian name data.
        Arabic naming: given + father's + grandfather's + family name.
        """
        cache_path = self.cache_dir / "egypt_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating Egypt name data structure...")
        
        metadata = pd.DataFrame({
            "aspect": ["structure", "dominant_name", "source", "muhammad_prevalence"],
            "description": [
                "Given + father's + grandfather's + family name (patronymic chain)",
                "Muhammad (محمد) extremely prevalent",
                "CAPMAS - Egyptian Central Agency for Public Mobilization and Statistics",
                "Estimated 20-25% of males have Muhammad as given or part of name"
            ]
        })
        metadata.to_csv(cache_path / "naming_conventions.csv", index=False)
        
        dominant_names = pd.DataFrame({
            "name_arabic": ["محمد", "أحمد", "علي", "إبراهيم", "فاطمة", "عائشة"],
            "name_romanized": ["Muhammad", "Ahmad", "Ali", "Ibrahim", "Fatima", "Aisha"],
            "sex": ["M", "M", "M", "M", "F", "F"],
            "estimated_prevalence_pct": [20, 8, 7, 5, 12, 6]
        })
        dominant_names.to_csv(cache_path / "dominant_names.csv", index=False)
        
        # Add note file
        note_df = pd.DataFrame({
            "note": ["These are rough estimates; official comprehensive data limited"]
        })
        note_df.to_csv(cache_path / "data_notes.csv", index=False)
        
        self.metadata["egypt"] = {
            "source": "CAPMAS Egypt",
            "naming_structure": "patronymic_chain",
            "muhammad_dominance": "very_high_20_25_pct",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ Egypt naming convention structure created")
        return cache_path
    
    def create_nigeria_structure(self) -> Path:
        """
        Create structure for Nigerian name data.
        Highly diverse: ethnic/tribal names (Yoruba, Igbo, Hausa) + Muslim/Christian.
        """
        cache_path = self.cache_dir / "nigeria_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating Nigeria name data structure...")
        
        metadata = pd.DataFrame({
            "ethnic_group": ["Yoruba", "Igbo", "Hausa", "Christian", "Traditional"],
            "naming_pattern": [
                "Meaning-based (e.g., Oluwaseun = God has done this)",
                "Circumstantial/day names (e.g., Chukwuemeka)",
                "Muslim/Arabic names (Muhammad common)",
                "Biblical/Western names",
                "Multiple naming ceremonies, high diversity"
            ],
            "diversity_level": ["Very High", "Very High", "Low (Muhammad concentrated)", "Medium", "Very High"]
        })
        metadata.to_csv(cache_path / "naming_systems.csv", index=False)
        
        regional_patterns = pd.DataFrame({
            "region": ["North (Hausa-Fulani)", "Southwest (Yoruba)", "Southeast (Igbo)"],
            "dominant_religion": ["Islam", "Christianity/Traditional", "Christianity"],
            "naming_pattern": [
                "Arabic/Muslim names, Muhammad very common",
                "Meaning-based Yoruba names, high diversity",
                "Igbo names + Christian names, high diversity"
            ],
            "estimated_muhammad_prevalence": ["15-20% in region", "<1%", "<1%"]
        })
        regional_patterns.to_csv(cache_path / "regional_patterns.csv", index=False)
        
        self.metadata["nigeria"] = {
            "source": "National Population Commission Nigeria",
            "naming_structure": "ethnic_regional_religious_variation",
            "diversity": "very_high_except_muslim_north",
            "status": "structure_created"
        }
        self._save_metadata()
        
        print("✓ Nigeria naming convention structure created")
        return cache_path
    
    def create_country_names_dataset(self) -> Path:
        """
        Create dataset of country names, exonyms, endonyms, and pronunciations.
        """
        cache_path = self.cache_dir / "country_names"
        cache_path.mkdir(exist_ok=True)
        
        print("Creating country names dataset...")
        
        # Key examples for initial analysis
        country_names = pd.DataFrame({
            "country_code": ["USA", "CHN", "MEX", "DEU", "BRA", "IND", "EGY", "NGA", "GBR", "CAN", "ESP"],
            "endonym": ["United States of America", "中国 (Zhōngguó)", "México", "Deutschland", "Brasil", 
                       "भारत (Bhārat) / India", "مصر (Miṣr)", "Nigeria", "United Kingdom", "Canada", "España"],
            "common_english": ["America / the States", "China", "Mexico", "Germany", "Brazil", 
                             "India", "Egypt", "Nigeria", "Britain / UK", "Canada", "Spain"],
            "abbreviation_english": ["USA / US", "PRC", "MEX", "GER / DE", "BRA", "IND", "EGY", "NGA / NGR", "UK", "CAN", "ESP"],
            "abbreviation_local": ["USA", "中国", "MX", "DE", "BR", "IND / भारत", "مصر", "NGR", "UK", "CA", "ES"],
            "spanish_name": ["Estados Unidos / EEUU", "China", "México", "Alemania", "Brasil", 
                           "India", "Egipto", "Nigeria", "Reino Unido", "Canadá", "España"],
            "phonetic_beauty_note": [
                "America = subjectively beautiful (user hypothesis)",
                "China = harsh plosive (Trump pronunciation emphasis)",
                "Smooth flow",
                "Harsh consonants",
                "Soft sibilants",
                "Short, simple",
                "Smooth",
                "Soft beginning, hard ending",
                "Formal/stiff",
                "Simple, open",
                "Palatalized"
            ]
        })
        country_names.to_csv(cache_path / "country_names_core.csv", index=False)
        
        # Create phonetic analysis template
        phonetic_template = pd.DataFrame({
            "name": ["America", "China", "Deutschland", "Brasil", "India"],
            "syllables": [4, 2, 2, 2, 3],
            "plosives": [1, 2, 2, 1, 1],  # hard consonants
            "sibilants": [0, 1, 2, 2, 1],
            "liquids_nasals": [2, 1, 2, 2, 3],  # l, r, m, n
            "open_vowels": [4, 1, 2, 2, 3],
            "phonetic_harshness_score": [20, 75, 70, 45, 35],  # 0-100 scale
            "subjective_beauty_rating": [95, 30, 40, 70, 60]  # user rating for America=95
        })
        phonetic_template.to_csv(cache_path / "phonetic_analysis_template.csv", index=False)
        
        self.metadata["country_names"] = {
            "source": "compiled from ISO 3166, native sources",
            "purpose": "exonym/endonym aesthetic analysis",
            "status": "initial_dataset_created"
        }
        self._save_metadata()
        
        print("✓ Country names dataset created")
        return cache_path
    
    def acquire_all_data(self, force_refresh: bool = False):
        """Run full acquisition pipeline for all countries."""
        print("\n" + "="*60)
        print("GLOBAL NAME DIVERSITY DATA ACQUISITION")
        print("="*60 + "\n")
        
        results = {}
        
        # Real downloadable data
        print("\n--- DOWNLOADABLE DATASETS ---")
        results["usa"] = self.download_usa_ssa_names(force_refresh)
        
        # Structure creation for manual/complex sources
        print("\n--- COMPLEX DATA STRUCTURES ---")
        results["uk"] = self.download_uk_ons_names(force_refresh)
        results["canada"] = self.download_canada_names(force_refresh)
        results["mexico"] = self.create_mexico_structure()
        results["spain"] = self.create_spain_structure()
        results["brazil"] = self.create_brazil_structure()
        results["germany"] = self.create_germany_structure()
        results["china"] = self.create_china_structure()
        results["india"] = self.create_india_structure()
        results["egypt"] = self.create_egypt_structure()
        results["nigeria"] = self.create_nigeria_structure()
        
        print("\n--- COUNTRY NAMES ---")
        results["country_names"] = self.create_country_names_dataset()
        
        print("\n" + "="*60)
        print("ACQUISITION SUMMARY")
        print("="*60)
        print(f"✓ Created structures for {len(results)} country datasets")
        print(f"✓ Metadata saved to {self.metadata_file}")
        print("\nNext steps:")
        print("1. Manual data download for UK, Canada (instructions in respective folders)")
        print("2. Curate representative samples for countries without public APIs")
        print("3. Run processing.py to harmonize and compute metrics")
        
        return results


if __name__ == "__main__":
    acquirer = NameDataAcquisition()
    acquirer.acquire_all_data(force_refresh=False)

