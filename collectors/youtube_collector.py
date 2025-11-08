"""
YouTube Channel Collector

Collects YouTube channel data for nominative determinism research.
Uses YouTube Data API v3 (requires API key).

Usage:
    python3 -c "from collectors.youtube_collector import YouTubeChannelCollector; 
                c = YouTubeChannelCollector(); c.collect_channels(1000)"
"""

import os
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Graceful degradation if API not available
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    logger.warning("YouTube API not available. Install: pip install google-api-python-client")


class YouTubeChannelCollector:
    """
    Collects YouTube channel data for nominative determinism analysis
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize collector
        
        Args:
            api_key: YouTube Data API v3 key (or from env YOUTUBE_API_KEY)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        
        if not self.api_key:
            raise ValueError("YouTube API key required. Set YOUTUBE_API_KEY environment variable "
                           "or pass api_key parameter. Get key from: https://console.cloud.google.com/")
        
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError("google-api-python-client required. Install: pip install google-api-python-client")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.rate_limit_delay = 0.5  # seconds between requests
        
        # Categories to collect from
        self.categories = {
            'Gaming': 20,
            'Entertainment': 24,
            'Education': 27,
            'Science & Technology': 28,
            'Music': 10,
            'Sports': 17,
            'News & Politics': 25,
            'Comedy': 23,
        }
    
    def collect_channels(self, target_count: int = 1000) -> Dict:
        """
        Collect YouTube channels
        
        Args:
            target_count: How many channels to collect
            
        Returns:
            Dictionary with collection results
        """
        logger.info(f"Starting YouTube channel collection (target: {target_count})")
        
        collected_channels = []
        per_category = target_count // len(self.categories)
        
        for category_name, category_id in self.categories.items():
            logger.info(f"  Collecting {per_category} channels from {category_name}...")
            
            try:
                channels = self._collect_category(category_id, per_category)
                collected_channels.extend(channels)
                logger.info(f"    ✓ Collected {len(channels)} channels")
                
            except HttpError as e:
                logger.error(f"    ✗ API error: {e}")
            except Exception as e:
                logger.error(f"    ✗ Error: {e}")
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        # Save to database
        with_app_context = self._get_app_context()
        
        if with_app_context:
            saved_count = self._save_to_database(collected_channels)
        else:
            saved_count = len(collected_channels)
            logger.warning("App context not available - data not saved to database")
        
        results = {
            'collected': len(collected_channels),
            'saved': saved_count,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\nCollection complete: {saved_count}/{target_count} channels saved")
        
        return results
    
    def _collect_category(self, category_id: int, count: int) -> List[Dict]:
        """Collect channels from a specific category"""
        channels = []
        
        try:
            # Search for popular channels in category
            request = self.youtube.search().list(
                part='snippet',
                type='channel',
                videoCategoryId=str(category_id),
                maxResults=min(count, 50),  # API limit
                order='viewCount'
            )
            
            response = request.execute()
            
            # Get channel details
            for item in response.get('items', []):
                channel_id = item['id']['channelId']
                
                # Get full channel statistics
                stats_request = self.youtube.channels().list(
                    part='statistics,snippet,brandingSettings',
                    id=channel_id
                )
                
                stats_response = stats_request.execute()
                
                if stats_response.get('items'):
                    channel_data = self._parse_channel_data(stats_response['items'][0])
                    channels.append(channel_data)
                
                time.sleep(self.rate_limit_delay)
        
        except Exception as e:
            logger.error(f"Category collection error: {e}")
        
        return channels
    
    def _parse_channel_data(self, channel_item: Dict) -> Dict:
        """Parse channel data from API response"""
        snippet = channel_item.get('snippet', {})
        statistics = channel_item.get('statistics', {})
        
        return {
            'id': channel_item['id'],
            'name': snippet.get('title', 'Unknown'),
            'channel_url': f"https://youtube.com/channel/{channel_item['id']}",
            'subscriber_count': int(statistics.get('subscriberCount', 0)),
            'total_views': int(statistics.get('viewCount', 0)),
            'video_count': int(statistics.get('videoCount', 0)),
            'average_views_per_video': int(statistics.get('viewCount', 0)) // max(int(statistics.get('videoCount', 1)), 1),
            'category': snippet.get('customUrl', '').split('/')[-1] if snippet.get('customUrl') else None,
            'created_year': int(snippet.get('publishedAt', '2000')[:4]) if snippet.get('publishedAt') else None,
            'country': snippet.get('country'),
            'description': snippet.get('description', ''),
        }
    
    def _get_app_context(self):
        """Get Flask app context"""
        try:
            from app import app
            return app.app_context()
        except:
            return None
    
    def _save_to_database(self, channels: List[Dict]) -> int:
        """Save collected channels to database"""
        from app import app
        from core.expansion_models import YouTubeChannel
        
        saved = 0
        
        with app.app_context():
            for channel_data in channels:
                try:
                    # Check if exists
                    existing = YouTubeChannel.query.get(channel_data['id'])
                    
                    if existing:
                        # Update
                        for key, value in channel_data.items():
                            setattr(existing, key, value)
                    else:
                        # Create new
                        channel = YouTubeChannel(**channel_data)
                        db.session.add(channel)
                    
                    saved += 1
                    
                    # Commit in batches
                    if saved % 100 == 0:
                        db.session.commit()
                        logger.info(f"    Saved {saved} channels...")
                
                except Exception as e:
                    logger.error(f"    Error saving channel: {e}")
            
            # Final commit
            db.session.commit()
        
        return saved


# =============================================================================
# Quick Test Function
# =============================================================================

def test_youtube_collector():
    """Test the YouTube collector"""
    print("\n" + "=" * 60)
    print("TESTING YOUTUBE CHANNEL COLLECTOR")
    print("=" * 60)
    
    try:
        collector = YouTubeChannelCollector()
        print("\n✓ Collector initialized")
        print("  Ready to collect channels")
        print("\nTo collect data, run:")
        print("  python3 -c \"from collectors.youtube_collector import YouTubeChannelCollector;")
        print("              c = YouTubeChannelCollector(); c.collect_channels(100)\"")
        
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nSetup required:")
        print("  1. Get API key: https://console.cloud.google.com/")
        print("  2. Enable YouTube Data API v3")
        print("  3. Set environment variable:")
        print("     export YOUTUBE_API_KEY='your-key-here'")
    
    except ImportError as e:
        print(f"\n✗ Dependency missing: {e}")
        print("\nInstall required:")
        print("  pip install google-api-python-client")
    
    print("=" * 60)


if __name__ == '__main__':
    test_youtube_collector()

