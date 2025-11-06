"""Quick check of available hurricanes in database"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from core.models import Hurricane

with app.app_context():
    count = Hurricane.query.count()
    print(f"\nTotal hurricanes in database: {count}")
    
    if count > 0:
        print("\nMost recent 10 hurricanes:")
        recent = Hurricane.query.order_by(Hurricane.year.desc()).limit(10).all()
        for h in recent:
            print(f"  {h.id} - {h.name} ({h.year})")
    else:
        print("\n⚠️  No hurricanes in database!")
        print("\nYou need to collect hurricane data first. Run:")
        print("  python3 -c \"from app import app; from collectors.hurricane_collector import HurricaneCollector; ")
        print("  collector = HurricaneCollector(); ")
        print("  with app.app_context(): collector.collect_all_hurricanes()\"")

