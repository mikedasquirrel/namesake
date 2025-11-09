#!/usr/bin/env python3
"""Add adult film domain #18 to Silence artwork"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load current data
with open('data/nail_artwork_data.json', 'r') as f:
    data = json.load(f)

# Add adult film domain
adult_film = {
    'id': 18,
    'name': 'Adult Film (Visual)',
    'category': 'social_artistic',
    'effect_size_r': 0.22,  # Genre×Name interaction R²
    'p_value': 0.001,
    'sample_size': 1012,
    'key_metric': 'Genre×Name interactions: MILF 2.12 syl (-41%)',
    'primary_names': ['Lisa Ann', 'Brandi Love', 'Riley Reid', 'Mia Malkova', 'Angela White'],
    'mechanism': 'Domain-specific formula: Genre×Syllables cohort effects',
    'nail_position': 'heart_complex_fracture',
    'violence_type': 'cohort_differentiation'
}

data['domains'].append(adult_film)
data['metadata']['domains_count'] = 18
data['metadata']['total_entities'] = 847293 + 1012
data['metadata']['generated_date'] = '2025-11-08'

# Save
with open('data/nail_artwork_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print('✅ Domain #18 Added: Adult Film (Visual Entertainment)')
print(f'   Sample: {adult_film["sample_size"]:,} performers')
print(f'   Effect: {adult_film["mechanism"]}')
print(f'   Total entities: 848,305')
print()
print('Regenerating artwork...')

# Regenerate
from utils.nail_generator import generate_all_outputs
generate_all_outputs()

print('\n✅ Artwork updated with Domain #18')

