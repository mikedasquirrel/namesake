"""
Earthquake Data Collector - USGS Earthquake Catalog Integration

Collects earthquake data from USGS API, including:
- Seismological parameters (magnitude, depth, location)
- Geographic naming (location names for phonetic analysis)
- Temporal data (date, time, day of week)

Extends hurricane analysis framework to earthquake nomenclature.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import json
import os

class EarthquakeCollector:
    """Collects earthquake data from USGS Earthquake API."""
    
    def __init__(self, db_path: str = 'instance/database.db'):
        self.base_url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
        self.db_path = db_path
        
    def collect_significant_earthquakes(self, 
                                       start_date: str = '1900-01-01',
                                       end_date: str = None,
                                       min_magnitude: float = 6.0,
                                       limit: int = 1000) -> pd.DataFrame:
        """
        Collect significant earthquakes from USGS catalog.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today
            min_magnitude: Minimum magnitude threshold
            limit: Maximum number of events to retrieve
            
        Returns:
            DataFrame with earthquake records
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'format': 'geojson',
            'starttime': start_date,
            'endtime': end_date,
            'minmagnitude': min_magnitude,
            'orderby': 'magnitude',
            'limit': limit
        }
        
        print(f"Collecting earthquakes from {start_date} to {end_date}, M≥{min_magnitude}...")
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            earthquakes = []
            for feature in data['features']:
                props = feature['properties']
                geom = feature['geometry']
                
                # Extract location name (primary naming source)
                location_name = props.get('place', '').strip()
                
                # Parse location name components
                location_parts = self._parse_location_name(location_name)
                
                earthquake = {
                    'event_id': feature.get('id'),
                    'magnitude': props.get('mag'),
                    'magnitude_type': props.get('magType'),
                    'location_name': location_name,
                    'location_primary': location_parts['primary'],
                    'location_secondary': location_parts['secondary'],
                    'location_region': location_parts['region'],
                    'longitude': geom['coordinates'][0],
                    'latitude': geom['coordinates'][1],
                    'depth_km': geom['coordinates'][2],
                    'timestamp': props.get('time'),
                    'date': self._timestamp_to_date(props.get('time')),
                    'day_of_week': self._get_day_of_week(props.get('time')),
                    'tsunami': props.get('tsunami', 0),
                    'felt_reports': props.get('felt'),
                    'cdi': props.get('cdi'),  # Community Decimal Intensity
                    'mmi': props.get('mmi'),  # Modified Mercalli Intensity
                    'alert_level': props.get('alert'),
                    'significance': props.get('sig'),
                    'gap': props.get('gap'),
                    'rms': props.get('rms'),
                    'collected_at': datetime.now().isoformat()
                }
                
                earthquakes.append(earthquake)
                
            df = pd.DataFrame(earthquakes)
            print(f"✓ Collected {len(df)} earthquakes")
            return df
            
        except Exception as e:
            print(f"Error collecting earthquakes: {e}")
            return pd.DataFrame()
    
    def _parse_location_name(self, location_str: str) -> Dict[str, str]:
        """
        Parse USGS location string into components.
        
        USGS format: "5 km NW of City, Region" or "offshore Region"
        
        Returns:
            Dict with primary, secondary, region components
        """
        if not location_str:
            return {'primary': '', 'secondary': '', 'region': ''}
        
        # Remove distance/direction prefix (e.g., "5 km NW of")
        parts = location_str.split(' of ')
        if len(parts) > 1:
            location_str = parts[1]
        
        # Split by comma
        components = [c.strip() for c in location_str.split(',')]
        
        return {
            'primary': components[0] if len(components) > 0 else '',
            'secondary': components[1] if len(components) > 1 else '',
            'region': components[-1] if len(components) > 0 else ''
        }
    
    def _timestamp_to_date(self, timestamp_ms: Optional[int]) -> Optional[str]:
        """Convert USGS timestamp (milliseconds) to date string."""
        if timestamp_ms is None:
            return None
        try:
            return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')
        except:
            return None
    
    def _get_day_of_week(self, timestamp_ms: Optional[int]) -> Optional[str]:
        """Get day of week from timestamp."""
        if timestamp_ms is None:
            return None
        try:
            return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%A')
        except:
            return None
    
    def collect_major_us_earthquakes(self) -> pd.DataFrame:
        """
        Collect major US earthquakes with high damage/casualty potential.
        
        Focus on well-documented US events for primary analysis.
        """
        # Define major US earthquakes manually for high-quality outcome data
        major_us_events = [
            # California
            {'name': '1906 San Francisco', 'year': 1906, 'magnitude': 7.9, 'state': 'CA'},
            {'name': '1989 Loma Prieta', 'year': 1989, 'magnitude': 6.9, 'state': 'CA'},
            {'name': '1994 Northridge', 'year': 1994, 'magnitude': 6.7, 'state': 'CA'},
            {'name': '1971 San Fernando', 'year': 1971, 'magnitude': 6.6, 'state': 'CA'},
            {'name': '1992 Landers', 'year': 1992, 'magnitude': 7.3, 'state': 'CA'},
            {'name': '1999 Hector Mine', 'year': 1999, 'magnitude': 7.1, 'state': 'CA'},
            {'name': '2014 South Napa', 'year': 2014, 'magnitude': 6.0, 'state': 'CA'},
            {'name': '2019 Ridgecrest', 'year': 2019, 'magnitude': 7.1, 'state': 'CA'},
            
            # Alaska
            {'name': '1964 Alaska', 'year': 1964, 'magnitude': 9.2, 'state': 'AK'},
            {'name': '2002 Denali', 'year': 2002, 'magnitude': 7.9, 'state': 'AK'},
            {'name': '2018 Anchorage', 'year': 2018, 'magnitude': 7.1, 'state': 'AK'},
            
            # Others
            {'name': '2001 Nisqually (Seattle)', 'year': 2001, 'magnitude': 6.8, 'state': 'WA'},
            {'name': '2011 Virginia', 'year': 2011, 'magnitude': 5.8, 'state': 'VA'},
        ]
        
        return pd.DataFrame(major_us_events)
    
    def collect_international_major_earthquakes(self) -> pd.DataFrame:
        """
        Collect major international earthquakes for cross-cultural validation.
        """
        major_international = [
            # Japan
            {'name': '2011 Tohoku', 'year': 2011, 'magnitude': 9.1, 'country': 'Japan', 'deaths': 15894},
            {'name': '1995 Kobe', 'year': 1995, 'magnitude': 6.9, 'country': 'Japan', 'deaths': 6434},
            {'name': '2016 Kumamoto', 'year': 2016, 'magnitude': 7.0, 'country': 'Japan', 'deaths': 273},
            
            # China
            {'name': '2008 Sichuan', 'year': 2008, 'magnitude': 7.9, 'country': 'China', 'deaths': 87587},
            {'name': '1976 Tangshan', 'year': 1976, 'magnitude': 7.6, 'country': 'China', 'deaths': 242769},
            
            # Haiti/Caribbean
            {'name': '2010 Haiti', 'year': 2010, 'magnitude': 7.0, 'country': 'Haiti', 'deaths': 316000},
            
            # Nepal
            {'name': '2015 Nepal', 'year': 2015, 'magnitude': 7.8, 'country': 'Nepal', 'deaths': 8964},
            
            # Chile
            {'name': '2010 Chile', 'year': 2010, 'magnitude': 8.8, 'country': 'Chile', 'deaths': 525},
            {'name': '1960 Valdivia', 'year': 1960, 'magnitude': 9.5, 'country': 'Chile', 'deaths': 1655},
            
            # Turkey
            {'name': '1999 Izmit', 'year': 1999, 'magnitude': 7.6, 'country': 'Turkey', 'deaths': 17127},
            {'name': '2023 Turkey-Syria', 'year': 2023, 'magnitude': 7.8, 'country': 'Turkey', 'deaths': 59259},
            
            # Indonesia
            {'name': '2004 Sumatra', 'year': 2004, 'magnitude': 9.1, 'country': 'Indonesia', 'deaths': 227898},
            {'name': '2018 Sulawesi', 'year': 2018, 'magnitude': 7.5, 'country': 'Indonesia', 'deaths': 4340},
            
            # Pakistan
            {'name': '2005 Kashmir', 'year': 2005, 'magnitude': 7.6, 'country': 'Pakistan', 'deaths': 86000},
            
            # Italy
            {'name': '2009 L\'Aquila', 'year': 2009, 'magnitude': 6.3, 'country': 'Italy', 'deaths': 309},
            {'name': '2016 Amatrice', 'year': 2016, 'magnitude': 6.2, 'country': 'Italy', 'deaths': 299},
            
            # Mexico
            {'name': '2017 Puebla', 'year': 2017, 'magnitude': 7.1, 'country': 'Mexico', 'deaths': 370},
            {'name': '1985 Mexico City', 'year': 1985, 'magnitude': 8.0, 'country': 'Mexico', 'deaths': 10000},
            
            # Iran
            {'name': '2003 Bam', 'year': 2003, 'magnitude': 6.6, 'country': 'Iran', 'deaths': 26271},
            
            # New Zealand
            {'name': '2011 Christchurch', 'year': 2011, 'magnitude': 6.3, 'country': 'New Zealand', 'deaths': 185},
        ]
        
        return pd.DataFrame(major_international)
    
    def enrich_with_outcomes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich earthquake data with outcome variables.
        
        For now, returns skeleton with manual enrichment fields.
        Full implementation would integrate NOAA NGDC and EM-DAT APIs.
        """
        # Add outcome columns for manual enrichment
        outcome_cols = {
            'deaths_total': None,
            'deaths_direct': None,
            'deaths_indirect': None,
            'injuries': None,
            'displaced': None,
            'damage_usd_millions': None,
            'damage_usd_2024': None,  # Inflation adjusted
            'buildings_destroyed': None,
            'buildings_damaged': None,
            'fema_declaration': None,
            'international_aid_usd': None,
            'recovery_years': None,
            'has_casualties': None
        }
        
        for col, default in outcome_cols.items():
            if col not in df.columns:
                df[col] = default
        
        # Calculate binary outcome if deaths available
        if 'deaths_total' in df.columns:
            df['has_casualties'] = df['deaths_total'].notna() & (df['deaths_total'] > 0)
        
        return df
    
    def save_to_database(self, df: pd.DataFrame, table_name: str = 'earthquakes'):
        """Save earthquake data to SQLite database."""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"✓ Saved {len(df)} earthquakes to {table_name} table")
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = 'data/processed/earthquakes_dataset.csv'):
        """Export earthquake data to CSV."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"✓ Exported to {filename}")


def main():
    """Collect comprehensive earthquake dataset."""
    collector = EarthquakeCollector()
    
    print("=" * 60)
    print("EARTHQUAKE DATA COLLECTION")
    print("=" * 60)
    
    # Collect US earthquakes (better outcome data)
    print("\n1. Collecting major US earthquakes...")
    us_quakes = collector.collect_major_us_earthquakes()
    print(f"   ✓ {len(us_quakes)} US earthquakes")
    
    # Collect international major earthquakes
    print("\n2. Collecting major international earthquakes...")
    intl_quakes = collector.collect_international_major_earthquakes()
    print(f"   ✓ {len(intl_quakes)} international earthquakes")
    
    # Combine
    all_quakes = pd.concat([us_quakes, intl_quakes], ignore_index=True)
    
    # Enrich with outcome structure
    print("\n3. Enriching with outcome variables...")
    all_quakes = collector.enrich_with_outcomes(all_quakes)
    
    # Save
    print("\n4. Saving data...")
    collector.save_to_database(all_quakes)
    collector.export_to_csv(all_quakes)
    
    print("\n" + "=" * 60)
    print(f"COLLECTION COMPLETE: {len(all_quakes)} earthquakes")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Manual enrichment of outcome data (deaths, damage)")
    print("2. Run phonetic analysis on location names")
    print("3. Statistical validation with controls")
    
    return all_quakes


if __name__ == '__main__':
    df = main()
    print(f"\nDataset shape: {df.shape}")
    print(f"\nSample locations:\n{df[['name', 'magnitude', 'deaths_total']].head(10)}")

