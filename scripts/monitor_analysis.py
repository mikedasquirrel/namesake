#!/usr/bin/env python3
"""
Monitor Running Formula Analysis

Shows real-time progress of formula analysis jobs.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import json
from datetime import datetime

def monitor():
    """Monitor analysis progress"""
    output_dir = Path('analysis_outputs/auto_analysis')
    
    print("\n" + "=" * 60)
    print("FORMULA ANALYSIS MONITOR")
    print("=" * 60)
    print("\nPress Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            # Check for latest results
            latest_daily = output_dir / 'daily_analysis_latest.json'
            latest_weekly = output_dir / 'weekly_analysis_latest.json'
            
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] ", end='')
            
            if latest_daily.exists():
                with open(latest_daily) as f:
                    data = json.load(f)
                start = data.get('start_time', '')
                validations = len(data.get('validations', {}))
                evolutions = len(data.get('evolutions', {}))
                errors = len(data.get('errors', []))
                
                print(f"Daily: {validations} validations, {evolutions} evolutions, {errors} errors | ", end='')
            else:
                print("Daily: No results yet | ", end='')
            
            # Check scheduler status
            import subprocess
            try:
                result = subprocess.run(
                    ['python3', 'scripts/formula_cli.py', 'scheduler', 'status'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if 'RUNNING' in result.stdout:
                    print("Scheduler: ✓ Running", end='')
                else:
                    print("Scheduler: ⚠ Stopped", end='')
            except:
                print("Scheduler: ? Unknown", end='')
            
            sys.stdout.flush()
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

if __name__ == '__main__':
    monitor()

