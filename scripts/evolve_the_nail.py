"""
Evolution System for The Nail Artwork
Automatically regenerates the artwork when new domains are added
Maintains version history showing how the nail sharpens over time
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.nail_generator import NailGenerator


class NailEvolutionSystem:
    """Manages evolution of The Nail artwork across research milestones"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_path = self.project_root / "data" / "nail_artwork_data.json"
        self.output_dir = self.project_root / "figures" / "the_nail"
        self.archive_dir = self.output_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Load current state
        with open(self.data_path, 'r') as f:
            self.data = json.load(f)
    
    def add_domain(self, domain_data: dict):
        """
        Add a new domain to the artwork data
        
        Args:
            domain_data: Dict with keys:
                - name: str
                - category: str  
                - effect_size_r: float
                - p_value: float
                - sample_size: int
                - key_metric: str
                - primary_names: list[str]
                - mechanism: str
                - nail_position: str (e.g., "horizontal_right", "vertical_mid")
                - violence_type: str
        """
        
        # Get next ID
        max_id = max(d['id'] for d in self.data['domains'])
        domain_data['id'] = max_id + 1
        
        # Add to domains list
        self.data['domains'].append(domain_data)
        
        # Update metadata
        self.data['metadata']['domains_count'] = len(self.data['domains'])
        self.data['metadata']['generated_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Update version
        current_count = len(self.data['domains'])
        self.data['evolution_parameters']['current_version'] = f"{current_count}_domains"
        
        # Save updated data
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        print(f"Added domain: {domain_data['name']}")
        print(f"Total domains: {current_count}")
        
        return current_count
    
    def check_milestone(self, domain_count: int) -> bool:
        """Check if we've hit a milestone requiring new physical painting"""
        milestones = self.data['evolution_parameters']['next_milestones']
        return domain_count in milestones
    
    def archive_current_version(self):
        """Archive the current version before regenerating"""
        
        domain_count = len(self.data['domains'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_name = f"v{domain_count:03d}_{timestamp}"
        
        version_dir = self.archive_dir / version_name
        version_dir.mkdir(exist_ok=True)
        
        # Copy current outputs to archive
        for file in self.output_dir.glob('*.svg'):
            shutil.copy(file, version_dir / file.name)
        
        for file in self.output_dir.glob('*.json'):
            shutil.copy(file, version_dir / file.name)
        
        for file in self.output_dir.glob('*.md'):
            shutil.copy(file, version_dir / file.name)
        
        # Save version metadata
        version_meta = {
            "version": version_name,
            "domain_count": domain_count,
            "timestamp": timestamp,
            "domains": [d['name'] for d in self.data['domains']],
            "milestone": self.check_milestone(domain_count)
        }
        
        with open(version_dir / "version_metadata.json", 'w') as f:
            json.dump(version_meta, f, indent=2)
        
        print(f"Archived version: {version_name}")
        return version_dir
    
    def regenerate(self):
        """Regenerate all outputs with current data"""
        
        print(f"\nRegenerating The Nail with {len(self.data['domains'])} domains...")
        
        # Create generator
        generator = NailGenerator(str(self.data_path))
        
        # Generate all outputs
        normal_svg = self.output_dir / "the_nail_normal_view.svg"
        nail_svg = self.output_dir / "the_nail_from_angle.svg"
        web_data = self.output_dir / "nail_web_data.json"
        instructions = self.output_dir / "painting_instructions.md"
        
        generator.export_svg(str(normal_svg), viewing_angle=0, size_inches=(6, 4))
        generator.export_svg(str(nail_svg), viewing_angle=30, size_inches=(6, 4))
        generator.export_data_for_web(str(web_data))
        generator.generate_painting_instructions(str(instructions))
        
        # Copy web data to static folder
        static_dir = self.project_root / "static"
        shutil.copy(web_data, static_dir / "nail_web_data.json")
        
        print(f"Generated all outputs")
        print(f"  - Normal view: {normal_svg.name}")
        print(f"  - Nail view: {nail_svg.name}")
        print(f"  - Web data: {web_data.name}")
        print(f"  - Instructions: {instructions.name}")
        
        return True
    
    def evolve(self, domain_data: dict = None, archive: bool = True):
        """
        Complete evolution cycle: add domain, archive, regenerate
        
        Args:
            domain_data: New domain to add (None = just regenerate existing)
            archive: Whether to archive current version first
        """
        
        print("=" * 70)
        print("THE NAIL - EVOLUTION CYCLE")
        print("=" * 70)
        print()
        
        # Archive current if requested
        if archive and self.output_dir.exists():
            self.archive_current_version()
            print()
        
        # Add new domain if provided
        if domain_data:
            domain_count = self.add_domain(domain_data)
            print()
            
            # Check milestone
            if self.check_milestone(domain_count):
                print(f"🎯 MILESTONE REACHED: {domain_count} domains")
                print("   → Physical painting recommended")
                print()
        
        # Regenerate
        self.regenerate()
        
        print()
        print("=" * 70)
        print("EVOLUTION COMPLETE")
        print("=" * 70)
        print()
        print(f"Current state: {len(self.data['domains'])} domains")
        print("The nail sharpens. The beauty deepens.")
        print()
    
    def get_version_history(self):
        """Get history of all archived versions"""
        versions = []
        
        for version_dir in sorted(self.archive_dir.glob("v*")):
            meta_file = version_dir / "version_metadata.json"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    versions.append(json.load(f))
        
        return versions
    
    def compare_versions(self, version1: str, version2: str):
        """Compare two versions to see how composition changed"""
        
        v1_dir = self.archive_dir / version1
        v2_dir = self.archive_dir / version2
        
        v1_data = json.load(open(v1_dir / "nail_web_data.json"))
        v2_data = json.load(open(v2_dir / "nail_web_data.json"))
        
        # Compare domain counts
        v1_domains = set(d['name'] for d in v1_data['normal_view'])
        v2_domains = set(d['name'] for d in v2_data['normal_view'])
        
        added = v2_domains - v1_domains
        
        print(f"Version Comparison: {version1} → {version2}")
        print(f"Domains added: {', '.join(added)}")
        print(f"Total domains: {len(v1_domains)} → {len(v2_domains)}")
        
        return {
            "added_domains": list(added),
            "v1_count": len(v1_domains),
            "v2_count": len(v2_domains)
        }


def add_new_domain_interactive():
    """Interactive CLI for adding a new domain"""
    
    print("\n" + "=" * 70)
    print("ADD NEW DOMAIN TO THE NAIL")
    print("=" * 70)
    print()
    
    domain_data = {}
    
    domain_data['name'] = input("Domain name (e.g., 'Political Candidates'): ")
    
    print("\nCategory options:")
    print("  - social_financial, social_identity, social_artistic")
    print("  - psychological_violence, natural_violence")
    print("  - geopolitical, historical_martial, institutional")
    domain_data['category'] = input("Category: ")
    
    domain_data['effect_size_r'] = float(input("\nEffect size (r-value, e.g., 0.25): "))
    domain_data['p_value'] = float(input("P-value (e.g., 0.001): "))
    domain_data['sample_size'] = int(input("Sample size (e.g., 5000): "))
    
    domain_data['key_metric'] = input("\nKey finding (e.g., '+25% for short names'): ")
    
    names_input = input("Primary names (comma-separated): ")
    domain_data['primary_names'] = [n.strip() for n in names_input.split(',')]
    
    domain_data['mechanism'] = input("Mechanism (brief description): ")
    
    print("\nNail position options:")
    print("  - vertical_shaft_top, vertical_mid, vertical_lower")
    print("  - horizontal_left, horizontal_mid_left, horizontal_right")
    print("  - intersection_nail_head")
    print("  - diagonal_upper_right, spiral_right")
    domain_data['nail_position'] = input("Nail position: ")
    
    domain_data['violence_type'] = input("Violence type (e.g., 'identity_fixation'): ")
    
    print("\n" + "-" * 70)
    print("Domain to be added:")
    print(json.dumps(domain_data, indent=2))
    print("-" * 70)
    
    confirm = input("\nAdd this domain? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        evo = NailEvolutionSystem()
        evo.evolve(domain_data, archive=True)
        return True
    else:
        print("Cancelled.")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evolve The Nail artwork")
    parser.add_argument('--add', action='store_true', help="Add new domain interactively")
    parser.add_argument('--regenerate', action='store_true', help="Regenerate with existing data")
    parser.add_argument('--history', action='store_true', help="Show version history")
    parser.add_argument('--compare', nargs=2, metavar=('V1', 'V2'), help="Compare two versions")
    
    args = parser.parse_args()
    
    evo = NailEvolutionSystem()
    
    if args.add:
        add_new_domain_interactive()
    
    elif args.regenerate:
        evo.evolve(domain_data=None, archive=True)
    
    elif args.history:
        versions = evo.get_version_history()
        print("\nVersion History:")
        print("=" * 70)
        for v in versions:
            milestone = " 🎯 MILESTONE" if v['milestone'] else ""
            print(f"{v['version']}: {v['domain_count']} domains{milestone}")
        print()
    
    elif args.compare:
        evo.compare_versions(args.compare[0], args.compare[1])
    
    else:
        print("The Nail Evolution System")
        print()
        print("Usage:")
        print("  python scripts/evolve_the_nail.py --add          # Add new domain interactively")
        print("  python scripts/evolve_the_nail.py --regenerate   # Regenerate with existing data")
        print("  python scripts/evolve_the_nail.py --history      # Show version history")
        print("  python scripts/evolve_the_nail.py --compare V1 V2  # Compare two versions")
        print()
        print(f"Current state: {len(evo.data['domains'])} domains")
        print()

