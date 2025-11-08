"""
Progress Reporter - Live Analysis Updates

Provides real-time progress reporting during analysis with:
- Time elapsed and ETA
- Current step and progress percentage
- Immediate highlighting of interesting findings
- Color-coded severity levels
- Summary of discoveries

This transforms silent batch jobs into live discovery streams.
"""

import time
from typing import List, Optional
from datetime import datetime, timedelta
import sys


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'  # 🟢 Normal
    YELLOW = '\033[93m'  # 🟡 Interesting
    ORANGE = '\033[38;5;214m'  # 🟠 Strong
    RED = '\033[91m'  # 🔴 Exceptional
    FIRE = '\033[38;5;196m'  # 🔥 Revolutionary
    CYAN = '\033[96m'  # Info
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ProgressReporter:
    """Real-time progress reporting for analysis"""
    
    def __init__(self, total_steps: int, job_name: str = "Analysis"):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.interesting_findings = []
        self.job_name = job_name
        self.last_update_time = time.time()
        
    def update(self, message: str, is_interesting: bool = False, 
              severity: str = "normal"):
        """
        Update progress
        
        Args:
            message: Progress message
            is_interesting: If True, highlights as interesting finding
            severity: normal/interesting/strong/exceptional/revolutionary
        """
        self.current_step += 1
        elapsed = time.time() - self.start_time
        
        # Calculate progress
        progress_pct = (self.current_step / self.total_steps) * 100
        
        # Calculate ETA
        if self.current_step > 0:
            rate = elapsed / self.current_step
            remaining_steps = self.total_steps - self.current_step
            eta_seconds = rate * remaining_steps
            eta_str = self._format_time(eta_seconds)
        else:
            eta_str = "calculating..."
        
        # Color code by severity
        emoji, color = self._get_severity_display(severity)
        
        # Format output
        time_str = self._format_time(elapsed)
        output = f"{color}[{time_str}] [{self.current_step}/{self.total_steps} {progress_pct:.0f}%] {emoji} {message}{Colors.RESET}"
        
        print(output)
        sys.stdout.flush()
        
        # If interesting, add to list
        if is_interesting:
            finding = {
                'time': elapsed,
                'step': self.current_step,
                'message': message,
                'severity': severity
            }
            self.interesting_findings.append(finding)
            
            # Extra highlight
            if severity in ['exceptional', 'revolutionary']:
                print(f"{Colors.FIRE}  {'🔥' * 3} SIGNIFICANT FINDING {'🔥' * 3}{Colors.RESET}")
        
        self.last_update_time = time.time()
    
    def report_finding(self, finding_type: str, value: any, context: str, 
                      severity: str = "interesting"):
        """
        Report an interesting finding immediately with full formatting
        
        Args:
            finding_type: Type of finding (e.g., "Golden Ratio Detected")
            value: The value found
            context: Context explanation
            severity: interesting/strong/exceptional/revolutionary
        """
        emoji, color = self._get_severity_display(severity)
        
        print(f"\n{color}{'=' * 70}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{emoji} FINDING: {finding_type}{Colors.RESET}")
        print(f"{color}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.CYAN}Value:{Colors.RESET} {value}")
        print(f"{Colors.CYAN}Context:{Colors.RESET} {context}")
        print(f"{color}{'=' * 70}{Colors.RESET}\n")
        sys.stdout.flush()
        
        # Add to findings
        self.interesting_findings.append({
            'type': finding_type,
            'value': str(value),
            'context': context,
            'severity': severity,
            'time': time.time() - self.start_time
        })
    
    def report_correlation(self, formula: str, domain: str, property_name: str,
                          correlation: float, p_value: float):
        """Report a correlation result with appropriate severity"""
        
        abs_corr = abs(correlation)
        
        # Determine severity
        if abs_corr < 0.20:
            severity = "normal"
        elif abs_corr < 0.30:
            severity = "interesting"
        elif abs_corr < 0.40:
            severity = "strong"
        elif abs_corr < 0.50:
            severity = "exceptional"
        else:
            severity = "revolutionary"
        
        # Report if interesting
        if abs_corr >= 0.25:
            self.report_finding(
                f"Correlation: {formula} in {domain}",
                f"r = {correlation:.3f} (p = {p_value:.4f})",
                f"Property '{property_name}' shows {'strong' if abs_corr > 0.30 else 'moderate'} correlation",
                severity=severity
            )
    
    def report_golden_ratio(self, entity1: str, entity2: str, ratio: float):
        """Report golden ratio discovery"""
        self.report_finding(
            "Golden Ratio Detected",
            f"{entity1}/{entity2} = {ratio:.4f} ≈ φ (1.618)",
            "Formula relationship shows golden ratio!",
            severity="revolutionary"
        )
    
    def report_novel_pattern(self, pattern_type: str, pattern_value: float, 
                           description: str):
        """Report discovery of novel mathematical pattern"""
        self.report_finding(
            f"Novel Pattern: {pattern_type}",
            f"Constant = {pattern_value:.6f}",
            description,
            severity="exceptional"
        )
    
    def report_convergence(self, formula: str, generation: int, fitness: float):
        """Report evolution convergence"""
        self.update(
            f"{formula} converged at generation {generation} (fitness={fitness:.3f})",
            is_interesting=True,
            severity="interesting"
        )
    
    def print_summary(self):
        """Print summary of interesting findings"""
        elapsed = time.time() - self.start_time
        
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}ANALYSIS COMPLETE - {self.job_name}{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        print(f"\nDuration: {self._format_time(elapsed)}")
        print(f"Steps Completed: {self.current_step}/{self.total_steps}")
        print(f"Interesting Findings: {len(self.interesting_findings)}")
        
        if self.interesting_findings:
            print(f"\n{Colors.BOLD}DISCOVERIES:{Colors.RESET}")
            print("-" * 70)
            
            for i, finding in enumerate(self.interesting_findings, 1):
                time_str = self._format_time(finding['time'])
                emoji, color = self._get_severity_display(finding.get('severity', 'interesting'))
                
                if 'type' in finding:
                    # Full finding report
                    print(f"{i}. [{time_str}] {emoji} {finding['type']}")
                    print(f"   {finding['value']}")
                else:
                    # Simple message
                    print(f"{i}. [{time_str}] {emoji} {finding['message']}")
            
            print("-" * 70)
        
        print(f"\n{Colors.GREEN}✓ Complete{Colors.RESET}\n")
    
    def _get_severity_display(self, severity: str) -> tuple:
        """Get emoji and color for severity level"""
        severity_map = {
            'normal': ('🟢', Colors.GREEN),
            'interesting': ('🟡', Colors.YELLOW),
            'strong': ('🟠', Colors.ORANGE),
            'exceptional': ('🔴', Colors.RED),
            'revolutionary': ('🔥', Colors.FIRE),
        }
        return severity_map.get(severity, ('🟢', Colors.GREEN))
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as human-readable time"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            mins = seconds / 60
            return f"{mins:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def checkpoint(self, message: str):
        """Print a major checkpoint"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'▶' * 35}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{message}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'▶' * 35}{Colors.RESET}\n")
        sys.stdout.flush()

