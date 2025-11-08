#!/usr/bin/env python3
"""
List All Available Domains

Shows what domains you have data for and how much data in each.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from core.unified_domain_model_extended import ExtendedDomainInterface
from tabulate import tabulate

print("\n" + "=" * 80)
print("AVAILABLE DOMAINS FOR FORMULA ANALYSIS")
print("=" * 80)

interface = ExtendedDomainInterface()

with app.app_context():
    info = interface.get_domain_info()
    
    # Separate available from unavailable
    available = []
    unavailable = []
    
    for domain_name, domain_info in sorted(info.items()):
        if domain_info.get('available'):
            available.append([
                domain_name,
                domain_info.get('count', 0),
                domain_info.get('with_analysis', 0),
                domain_info.get('with_outcome', 0),
                domain_info.get('outcome_metric', 'N/A')
            ])
        else:
            unavailable.append([
                domain_name,
                domain_info.get('error', 'Unknown')[:50]
            ])
    
    if available:
        print("\n✅ AVAILABLE DOMAINS:")
        print(tabulate(available,
                      headers=['Domain', 'Total', 'With Analysis', 'With Outcome', 'Outcome Metric'],
                      tablefmt='grid'))
        
        # Summary
        total_entities = sum(row[1] for row in available)
        total_analyzed = sum(row[2] for row in available)
        
        print(f"\nTOTAL: {len(available)} domains, {total_entities:,} entities, {total_analyzed:,} analyzed")
    
    if unavailable:
        print("\n⚠️  UNAVAILABLE DOMAINS:")
        print(tabulate(unavailable,
                      headers=['Domain', 'Issue'],
                      tablefmt='grid'))

print("\n" + "=" * 80)
print("Use these domains in your analysis configuration")
print("Edit: config/auto_analysis.yaml")
print("=" * 80)

