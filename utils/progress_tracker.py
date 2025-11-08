"""Progress Tracker - Reusable Progress Tracking with Intermittent Printing

Provides clean, informative progress updates for long-running background tasks.

Features:
- Intermittent printing (avoid spam, show meaningful updates)
- ETA calculation based on running average
- Timestamps for all updates
- Custom messages per update
- Completion summary with total time

Usage:
    tracker = ProgressTracker(total_steps=1000, print_interval=50)
    for i in range(1000):
        # Do work
        tracker.update(1, message=f"Processing record {i}")
    tracker.complete("All records processed successfully")

Author: Michael Smerconish
Date: November 2025
"""

import time
from datetime import datetime, timedelta
from typing import Optional
import sys


class ProgressTracker:
    """Track and display progress for long-running tasks"""
    
    def __init__(self, total_steps: int, print_interval: int = 10, 
                 task_name: str = "Processing", show_eta: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            total_steps: Total number of steps to complete
            print_interval: Print update every N steps (default: 10)
            task_name: Name of the task being tracked
            show_eta: Whether to show estimated time to completion
        """
        self.total_steps = total_steps
        self.print_interval = print_interval
        self.task_name = task_name
        self.show_eta = show_eta
        
        self.current_step = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.completed = False
        
        # For ETA calculation (running average of time per step)
        self.times_per_step = []
        self.max_history = 100  # Keep last 100 samples for ETA
        
        self._print_start()
    
    def _print_start(self):
        """Print task start message"""
        print("\n" + "=" * 80)
        print(f"{self.task_name.upper()}")
        print("=" * 80)
        print(f"Started: {self._format_timestamp()}")
        print(f"Total Steps: {self.total_steps:,}")
        print(f"Progress Updates: Every {self.print_interval} steps")
        print("=" * 80 + "\n")
        sys.stdout.flush()
    
    def update(self, steps: int = 1, message: Optional[str] = None):
        """
        Update progress by N steps.
        
        Args:
            steps: Number of steps completed (default: 1)
            message: Optional custom message to display
        """
        if self.completed:
            return
        
        self.current_step += steps
        
        # Calculate time for these steps
        current_time = time.time()
        time_for_steps = current_time - self.last_update_time
        if steps > 0:
            self.times_per_step.append(time_for_steps / steps)
            if len(self.times_per_step) > self.max_history:
                self.times_per_step.pop(0)
        self.last_update_time = current_time
        
        # Print update if interval reached or completed
        if (self.current_step % self.print_interval == 0 or 
            self.current_step >= self.total_steps):
            self._print_update(message)
    
    def _print_update(self, message: Optional[str] = None):
        """Print progress update"""
        timestamp = self._format_timestamp()
        progress_pct = (self.current_step / self.total_steps) * 100
        
        # Build progress line
        parts = [
            f"[{timestamp}]",
            f"Progress: {self.current_step:,}/{self.total_steps:,}",
            f"({progress_pct:.1f}%)"
        ]
        
        # Add ETA if enabled and we have timing data
        if self.show_eta and len(self.times_per_step) > 0 and self.current_step < self.total_steps:
            eta_seconds = self._calculate_eta()
            parts.append(f"| ETA: {self._format_duration(eta_seconds)}")
        
        # Add elapsed time
        elapsed = time.time() - self.start_time
        parts.append(f"| Elapsed: {self._format_duration(elapsed)}")
        
        # Add custom message
        if message:
            parts.append(f"| {message}")
        
        print(" ".join(parts))
        sys.stdout.flush()
    
    def _calculate_eta(self) -> float:
        """Calculate estimated time to completion (seconds)"""
        if not self.times_per_step:
            return 0.0
        
        # Use median of recent samples for robustness
        recent_times = sorted(self.times_per_step)
        median_time = recent_times[len(recent_times) // 2]
        
        remaining_steps = self.total_steps - self.current_step
        return remaining_steps * median_time
    
    def complete(self, message: Optional[str] = None):
        """Mark task as complete and print summary"""
        if self.completed:
            return
        
        self.completed = True
        self.current_step = self.total_steps
        
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print(f"{self.task_name.upper()} - COMPLETE")
        print("=" * 80)
        print(f"Completed: {self._format_timestamp()}")
        print(f"Total Steps: {self.total_steps:,}")
        print(f"Total Time: {self._format_duration(total_time)}")
        
        if self.total_steps > 0:
            avg_time = total_time / self.total_steps
            print(f"Average Time/Step: {avg_time*1000:.2f}ms")
        
        if message:
            print(f"\n{message}")
        
        print("=" * 80 + "\n")
        sys.stdout.flush()
    
    def error(self, error_message: str):
        """Mark task as failed and print error"""
        if self.completed:
            return
        
        self.completed = True
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print(f"{self.task_name.upper()} - ERROR")
        print("=" * 80)
        print(f"Failed at: {self._format_timestamp()}")
        print(f"Completed Steps: {self.current_step:,}/{self.total_steps:,}")
        print(f"Time Before Error: {self._format_duration(total_time)}")
        print(f"\nError: {error_message}")
        print("=" * 80 + "\n")
        sys.stdout.flush()
    
    def set_total_steps(self, new_total: int):
        """Update total steps (useful when actual count differs from estimate)"""
        self.total_steps = new_total
    
    def _format_timestamp(self) -> str:
        """Format current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    @property
    def percentage(self) -> float:
        """Get current completion percentage"""
        return (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0.0
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete"""
        return self.completed


class MultiTaskProgressTracker:
    """Track progress across multiple concurrent or sequential tasks"""
    
    def __init__(self, task_names: list, task_weights: Optional[list] = None):
        """
        Initialize multi-task tracker.
        
        Args:
            task_names: List of task names
            task_weights: Optional list of weights (default: equal weight)
        """
        self.task_names = task_names
        self.num_tasks = len(task_names)
        
        if task_weights is None:
            self.task_weights = [1.0 / self.num_tasks] * self.num_tasks
        else:
            total = sum(task_weights)
            self.task_weights = [w / total for w in task_weights]
        
        self.task_progress = [0.0] * self.num_tasks
        self.start_time = time.time()
        self.completed_tasks = set()
        
        self._print_start()
    
    def _print_start(self):
        """Print multi-task start message"""
        print("\n" + "=" * 80)
        print("MULTI-TASK PROCESSING")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tasks: {self.num_tasks}")
        print("\nTasks:")
        for i, (name, weight) in enumerate(zip(self.task_names, self.task_weights)):
            print(f"  {i+1}. {name} (weight: {weight:.1%})")
        print("=" * 80 + "\n")
        sys.stdout.flush()
    
    def update_task(self, task_index: int, progress_pct: float, message: Optional[str] = None):
        """
        Update progress for a specific task.
        
        Args:
            task_index: Index of the task (0-based)
            progress_pct: Progress percentage (0-100)
            message: Optional status message
        """
        if task_index < 0 or task_index >= self.num_tasks:
            return
        
        self.task_progress[task_index] = min(100.0, max(0.0, progress_pct))
        
        if progress_pct >= 100.0:
            self.completed_tasks.add(task_index)
        
        self._print_update(task_index, message)
    
    def _print_update(self, task_index: int, message: Optional[str] = None):
        """Print multi-task progress update"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        task_name = self.task_names[task_index]
        task_pct = self.task_progress[task_index]
        
        overall_pct = sum(p * w for p, w in zip(self.task_progress, self.task_weights))
        
        parts = [
            f"[{timestamp}]",
            f"Task {task_index+1}/{self.num_tasks}:",
            f"{task_name}",
            f"({task_pct:.1f}%)",
            f"| Overall: {overall_pct:.1f}%"
        ]
        
        if message:
            parts.append(f"| {message}")
        
        print(" ".join(parts))
        sys.stdout.flush()
    
    def complete(self):
        """Mark all tasks as complete"""
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("MULTI-TASK PROCESSING - COMPLETE")
        print("=" * 80)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tasks: {self.num_tasks}")
        print(f"Total Time: {self._format_duration(total_time)}")
        print("\nTask Summary:")
        for i, name in enumerate(self.task_names):
            status = "✓" if i in self.completed_tasks else "✗"
            print(f"  {status} {name}: {self.task_progress[i]:.1f}%")
        print("=" * 80 + "\n")
        sys.stdout.flush()
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

