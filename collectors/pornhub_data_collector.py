"""
Pornhub Data Collector for Nominative Determinism Research

Collects publicly available performer data from Pornhub including:
- Performer names (stage names)
- View counts (popularity metric)
- Video counts (productivity metric)
- Subscriber counts (fan loyalty metric)
- Rank/popularity metrics
- Genre/category associations

All data from public performer pages and rankings
Respectful rate limiting and terms of service compliance
Research purpose: Analyzing stage name patterns and career outcomes
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PornhubDataCollector:
    """
    Collects public performer data from Pornhub for research
    
    Focus: Stage names, view counts, video counts, subscribers
    Method: Public pages only, respectful rate limiting
    Purpose: Nominative determinism research
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Research/Nominative Study',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        self.base_url = 'https://www.pornhub.com'
        self.request_delay = 3.0  # 3 seconds between requests (respectful)
        self.last_request_time = 0
        
        self.collected_data = []
    
    def _rate_limit(self):
        """Respectful rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def collect_top_performers(self, limit: int = 500) -> List[Dict]:
        """
        Collect data from Pornhub's public performer rankings
        
        Args:
            limit: Number of performers to collect (default 500)
        
        Returns:
            List of performer data dictionaries
        """
        
        logger.info(f"Collecting top {limit} performers from Pornhub rankings...")
        
        performers = []
        page = 1
        performers_per_page = 20  # Typical pagination
        
        while len(performers) < limit:
            try:
                logger.info(f"Fetching page {page}...")
                
                # Pornhub rankings URL (public page)
                url = f"{self.base_url}/pornstars?page={page}"
                
                self._rate_limit()
                response = self.session.get(url, timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"Got status {response.status_code}, stopping")
                    break
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find performer cards/listings
                # Note: This is simplified - actual implementation would need
                # to match Pornhub's current HTML structure
                performer_elements = soup.select('.pornstars-list .pornstarCard, .modelCard, .performerCard')
                
                if not performer_elements:
                    logger.warning("No performer elements found, structure may have changed")
                    break
                
                for element in performer_elements:
                    if len(performers) >= limit:
                        break
                    
                    performer_data = self._parse_performer_element(element)
                    if performer_data:
                        performers.append(performer_data)
                        logger.info(f"Collected: {performer_data['stage_name']}")
                
                page += 1
                
                # Safety limit
                if page > 50:
                    logger.warning("Reached page limit")
                    break
                
            except Exception as e:
                logger.error(f"Error on page {page}: {str(e)}")
                break
        
        logger.info(f"Collected {len(performers)} performers")
        self.collected_data = performers
        return performers
    
    def _parse_performer_element(self, element) -> Optional[Dict]:
        """
        Parse a performer card/element for data
        
        Extracts:
        - Stage name
        - View count
        - Video count
        - Subscriber count (if available)
        - Rank/popularity
        """
        
        try:
            # Find name (various possible selectors)
            name_elem = element.select_one('.pornstarName, .modelName, .performerName, a.title')
            if not name_elem:
                return None
            
            stage_name = name_elem.get_text(strip=True)
            
            # Find metrics
            views = 0
            videos = 0
            subscribers = 0
            rank = 0
            
            # Views (look for view count text)
            view_elem = element.select_one('.views, .videoViews, [class*="view"]')
            if view_elem:
                view_text = view_elem.get_text(strip=True)
                views = self._parse_number(view_text)
            
            # Videos
            video_elem = element.select_one('.videosNumber, .videoCount, [class*="video"]')
            if video_elem:
                video_text = video_elem.get_text(strip=True)
                videos = self._parse_number(video_text)
            
            # Subscribers
            sub_elem = element.select_one('.subscribers, .fans, [class*="subscriber"]')
            if sub_elem:
                sub_text = sub_elem.get_text(strip=True)
                subscribers = self._parse_number(sub_text)
            
            # Rank (from position or explicit rank)
            rank_elem = element.select_one('.rank, .ranking, [class*="rank"]')
            if rank_elem:
                rank_text = rank_elem.get_text(strip=True)
                rank = self._parse_number(rank_text)
            
            return {
                'stage_name': stage_name,
                'source': 'pornhub',
                'total_views': views,
                'video_count': videos,
                'pornhub_subscribers': subscribers,
                'rank': rank,
                'collected_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing performer element: {str(e)}")
            return None
    
    def _parse_number(self, text: str) -> int:
        """
        Parse numbers from text like '1.5M', '234K', '1,234'
        
        Returns integer value
        """
        if not text:
            return 0
        
        # Remove non-numeric except M, K, B
        text = re.sub(r'[^\d.MKB]', '', text.upper())
        
        multipliers = {
            'K': 1000,
            'M': 1000000,
            'B': 1000000000
        }
        
        for suffix, mult in multipliers.items():
            if suffix in text:
                number = float(text.replace(suffix, ''))
                return int(number * mult)
        
        # Regular number
        try:
            return int(float(text))
        except:
            return 0
    
    def save_to_json(self, filepath: str):
        """Save collected data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.collected_data, f, indent=2)
        logger.info(f"Saved {len(self.collected_data)} performers to {filepath}")
    
    def integrate_with_database(self):
        """
        Integrate collected Pornhub data with existing database
        
        Matches by stage name, adds metrics
        """
        from core.models import db, AdultPerformer, AdultPerformerAnalysis
        from collectors.adult_film_collector import AdultFilmCollector
        
        collector = AdultFilmCollector()
        
        integrated = 0
        new_added = 0
        
        for performer_data in self.collected_data:
            stage_name = performer_data['stage_name']
            
            # Check if exists
            existing = AdultPerformer.query.filter_by(stage_name=stage_name).first()
            
            if existing:
                # Update with Pornhub metrics
                if performer_data.get('total_views'):
                    existing.total_views = performer_data['total_views']
                if performer_data.get('video_count'):
                    existing.video_count = performer_data['video_count']
                if performer_data.get('pornhub_subscribers'):
                    existing.pornhub_subscribers = performer_data['pornhub_subscribers']
                
                integrated += 1
                db.session.commit()
                
            else:
                # New performer - add to database
                performer = collector.collect_performer(
                    stage_name=stage_name,
                    source='pornhub',
                    total_views=performer_data.get('total_views', 0),
                    video_count=performer_data.get('video_count', 0),
                    pornhub_subscribers=performer_data.get('pornhub_subscribers', 0)
                )
                
                if performer:
                    new_added += 1
        
        logger.info(f"Integrated: {integrated} existing, {new_added} new performers")
        return integrated, new_added


def collect_and_save(limit: int = 500):
    """Convenience function to collect and save data"""
    
    collector = PornhubDataCollector()
    
    print("\n" + "="*80)
    print("PORNHUB DATA COLLECTION FOR NOMINATIVE DETERMINISM RESEARCH")
    print("="*80)
    print(f"\nTarget: {limit} performers")
    print("Collecting from public rankings...")
    print()
    
    performers = collector.collect_top_performers(limit=limit)
    
    print("\n" + "="*80)
    print(f"COLLECTION COMPLETE: {len(performers)} performers")
    print("="*80)
    
    # Save to file
    output_file = 'data/pornhub_performers.json'
    collector.save_to_json(output_file)
    
    print(f"\nData saved to: {output_file}")
    print("\nTo integrate with database, run:")
    print("  from collectors.pornhub_data_collector import PornhubDataCollector")
    print("  collector = PornhubDataCollector()")
    print("  collector.collected_data = json.load(open('data/pornhub_performers.json'))")
    print("  collector.integrate_with_database()")
    print()
    
    return performers


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect Pornhub performer data")
    parser.add_argument('--limit', type=int, default=500, help="Number of performers to collect")
    parser.add_argument('--integrate', action='store_true', help="Integrate with database after collection")
    
    args = parser.parse_args()
    
    performers = collect_and_save(limit=args.limit)
    
    if args.integrate:
        print("\nIntegrating with database...")
        from app import app
        with app.app_context():
            collector = PornhubDataCollector()
            collector.collected_data = performers
            integrated, new_added = collector.integrate_with_database()
            print(f"\nIntegration complete:")
            print(f"  Updated existing: {integrated}")
            print(f"  Added new: {new_added}")

