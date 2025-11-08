#!/usr/bin/env python3
"""
Formula Analysis Scheduler

Manages automated scheduling of formula analysis tasks using APScheduler.
Integrates with Flask app for background execution.

Usage:
    # Import in app.py:
    from scripts.scheduler import scheduler, initialize_scheduler
    
    # In app initialization:
    initialize_scheduler(app)
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import yaml
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def load_config(config_path: str = 'config/auto_analysis.yaml') -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def job_listener(event):
    """Listen for job execution events"""
    if event.exception:
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} completed successfully")


def run_daily_analysis():
    """Job function for daily analysis"""
    from scripts.auto_analyze_formulas import AutoFormulaAnalyzer
    
    logger.info("Starting scheduled daily analysis...")
    
    try:
        analyzer = AutoFormulaAnalyzer()
        results = analyzer.run_daily_analysis()
        
        if results.get('success'):
            logger.info("Daily analysis completed successfully")
        else:
            logger.warning(f"Daily analysis completed with {len(results.get('errors', []))} errors")
    
    except Exception as e:
        logger.error(f"Daily analysis failed: {e}", exc_info=True)


def run_weekly_deep_dive():
    """Job function for weekly deep dive"""
    from scripts.auto_analyze_formulas import AutoFormulaAnalyzer
    
    logger.info("Starting scheduled weekly deep dive...")
    
    try:
        analyzer = AutoFormulaAnalyzer()
        results = analyzer.run_weekly_deep_dive()
        
        if results.get('success'):
            logger.info("Weekly deep dive completed successfully")
        else:
            logger.warning(f"Weekly deep dive completed with {len(results.get('errors', []))} errors")
    
    except Exception as e:
        logger.error(f"Weekly deep dive failed: {e}", exc_info=True)


def initialize_scheduler(app=None, config_path: str = 'config/auto_analysis.yaml'):
    """
    Initialize and start the scheduler
    
    Args:
        app: Flask app instance (for app context)
        config_path: Path to configuration file
    """
    config = load_config(config_path)
    
    if not config:
        logger.warning("No configuration loaded - scheduler not initialized")
        return False
    
    # Add event listener
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    
    # Configure daily analysis
    daily_config = config.get('schedule', {}).get('daily_analysis', {})
    if daily_config.get('enabled', True):
        time_parts = daily_config.get('time', '02:00').split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        scheduler.add_job(
            func=run_daily_analysis,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='daily_analysis',
            name='Daily Formula Analysis',
            replace_existing=True,
            misfire_grace_time=3600  # 1 hour grace period
        )
        
        logger.info(f"Scheduled daily analysis for {hour:02d}:{minute:02d}")
    
    # Configure weekly deep dive
    weekly_config = config.get('schedule', {}).get('weekly_deep_dive', {})
    if weekly_config.get('enabled', True):
        day = weekly_config.get('day', 'Sunday')
        time_parts = weekly_config.get('time', '03:00').split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # Map day name to number (0 = Monday)
        day_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        day_of_week = day_map.get(day, 6)
        
        scheduler.add_job(
            func=run_weekly_deep_dive,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            id='weekly_deep_dive',
            name='Weekly Formula Deep Dive',
            replace_existing=True,
            misfire_grace_time=7200  # 2 hour grace period
        )
        
        logger.info(f"Scheduled weekly deep dive for {day} at {hour:02d}:{minute:02d}")
    
    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info("Formula analysis scheduler started")
    
    return True


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Formula analysis scheduler shutdown")


def get_scheduler_status() -> dict:
    """Get current scheduler status and job information"""
    if not scheduler.running:
        return {
            'running': False,
            'jobs': []
        }
    
    jobs = []
    for job in scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': next_run.isoformat() if next_run else None,
            'trigger': str(job.trigger)
        })
    
    return {
        'running': True,
        'jobs': jobs,
        'job_count': len(jobs)
    }


def trigger_job_now(job_id: str) -> bool:
    """Manually trigger a scheduled job immediately"""
    try:
        job = scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Triggered job: {job_id}")
            return True
        else:
            logger.warning(f"Job not found: {job_id}")
            return False
    except Exception as e:
        logger.error(f"Failed to trigger job {job_id}: {e}")
        return False


def pause_job(job_id: str) -> bool:
    """Pause a scheduled job"""
    try:
        scheduler.pause_job(job_id)
        logger.info(f"Paused job: {job_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to pause job {job_id}: {e}")
        return False


def resume_job(job_id: str) -> bool:
    """Resume a paused job"""
    try:
        scheduler.resume_job(job_id)
        logger.info(f"Resumed job: {job_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to resume job {job_id}: {e}")
        return False


# CLI for testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Formula Analysis Scheduler')
    parser.add_argument('action', choices=['start', 'status', 'trigger'], 
                       help='Action to perform')
    parser.add_argument('--job', help='Job ID for trigger action')
    parser.add_argument('--config', default='config/auto_analysis.yaml',
                       help='Config file path')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        print("Starting scheduler...")
        initialize_scheduler(config_path=args.config)
        print("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            # Keep running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            shutdown_scheduler()
    
    elif args.action == 'status':
        initialize_scheduler(config_path=args.config)
        status = get_scheduler_status()
        
        print(f"\nScheduler Status: {'Running' if status['running'] else 'Stopped'}")
        print(f"Jobs: {status['job_count']}\n")
        
        for job in status['jobs']:
            print(f"  [{job['id']}] {job['name']}")
            print(f"    Next run: {job['next_run']}")
            print(f"    Trigger: {job['trigger']}\n")
        
        shutdown_scheduler()
    
    elif args.action == 'trigger':
        if not args.job:
            print("Error: --job required for trigger action")
            sys.exit(1)
        
        initialize_scheduler(config_path=args.config)
        
        if trigger_job_now(args.job):
            print(f"Triggered job: {args.job}")
        else:
            print(f"Failed to trigger job: {args.job}")
        
        shutdown_scheduler()

