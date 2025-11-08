"""
The Nail - Generative Art from Nominative Determinism Research
Transforms correlation data into visual composition that reveals different truths from different angles
"""

import json
import numpy as np
import math
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DomainVisual:
    """Visual representation of a research domain"""
    name: str
    x: float  # Effect size position
    y: float  # Statistical significance position
    z: float  # Sample size depth
    color: Tuple[int, int, int]  # RGB
    size: float  # Visual prominence
    names_text: List[str]  # Actual names from domain
    violence_type: str
    nail_role: str  # Where this fits in the nail structure


class NailGenerator:
    """Generates 'The Nail' artwork from research data"""
    
    def __init__(self, data_path: str = None):
        """Initialize with research data"""
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "nail_artwork_data.json"
        
        with open(data_path, 'r') as f:
            self.data = json.load(f)
        
        self.domains = self.data['domains']
        self.composition_rules = self.data['composition_rules']
        self.nail_geometry = self.data['nail_geometry']
        
        # Canvas dimensions (normalized -1 to 1, scales to any size)
        self.canvas_width = 2.0
        self.canvas_height = 2.0
    
    def transform_to_coordinates(self, domain: Dict) -> DomainVisual:
        """Transform statistical data to visual coordinates"""
        
        # X: Effect size (r-value) - map 0.0-0.4 to canvas space
        x = self._map_range(domain['effect_size_r'], 0.0, 0.4, -0.8, 0.8)
        
        # Y: Statistical significance (-log10(p-value)) - higher = more significant
        if domain['p_value'] > 0:
            y = -math.log10(domain['p_value'])
        else:
            y = 5.0  # Max for p < 0.00001
        
        y = self._map_range(y, 0, 5, -0.8, 0.8)
        
        # Z: Sample size depth (log scale for huge variation)
        z = math.log10(domain['sample_size'] + 1)
        z = self._map_range(z, 0, 5, 0.1, 1.0)
        
        # Color from domain category
        color_key = domain['category']
        color = self.composition_rules['color_temperature'].get(
            color_key, 
            {"r": 128, "g": 128, "b": 128}
        )
        color_tuple = (color['r'], color['g'], color['b'])
        
        # Size: prominence based on entities and significance
        size = (domain['sample_size'] ** 0.25) * (1 / (domain['p_value'] + 0.0001))
        size = self._map_range(size, 0, 50000, 0.02, 0.15)
        
        return DomainVisual(
            name=domain['name'],
            x=x,
            y=y,
            z=z,
            color=color_tuple,
            size=size,
            names_text=domain['primary_names'],
            violence_type=domain['violence_type'],
            nail_role=domain['nail_position']
        )
    
    def apply_nail_transformation(self, visuals: List[DomainVisual], viewing_angle: float = 30) -> List[DomainVisual]:
        """
        Apply perspective transformation that reveals the nail from specific angle
        
        From straight on (0°): domains positioned by pure statistics
        From 30° right: same domains align to form a cross/nail
        """
        
        angle_rad = math.radians(viewing_angle)
        
        transformed = []
        
        for v in visuals:
            # Base position from statistics
            base_x, base_y = v.x, v.y
            
            # Nail-specific adjustments based on assigned position
            if 'vertical' in v.nail_role:
                # Domains on vertical shaft - pull toward y-axis at angle
                adjustment_x = -base_x * math.sin(angle_rad) * 0.6
                adjustment_y = base_y * math.cos(angle_rad) * 0.3
                
                new_x = base_x + adjustment_x
                new_y = base_y + adjustment_y
                
            elif 'horizontal' in v.nail_role:
                # Domains on horizontal beam - pull toward x-axis at angle
                adjustment_x = base_x * math.cos(angle_rad) * 0.3
                adjustment_y = -base_y * math.sin(angle_rad) * 0.6
                
                new_x = base_x + adjustment_x
                new_y = base_y + adjustment_y
                
            elif 'intersection' in v.nail_role:
                # Nail head - stays at center
                new_x = 0.0
                new_y = 0.0
                
            else:
                # Peripheral domains - minor gravitational pull
                new_x = base_x * (1 - 0.1 * math.sin(angle_rad))
                new_y = base_y * (1 - 0.1 * math.sin(angle_rad))
            
            # Create new visual with transformed position
            transformed_v = DomainVisual(
                name=v.name,
                x=new_x,
                y=new_y,
                z=v.z,
                color=v.color,
                size=v.size,
                names_text=v.names_text,
                violence_type=v.violence_type,
                nail_role=v.nail_role
            )
            transformed.append(transformed_v)
        
        return transformed
    
    def generate_composition(self, viewing_angle: float = 0) -> List[DomainVisual]:
        """Generate the complete visual composition"""
        
        # Transform all domains to visual elements
        visuals = [self.transform_to_coordinates(d) for d in self.domains]
        
        # Apply perspective transformation if viewing from the angle
        if viewing_angle > 0:
            visuals = self.apply_nail_transformation(visuals, viewing_angle)
        
        return visuals
    
    def export_svg(self, output_path: str, viewing_angle: float = 0, size_inches: Tuple[float, float] = (6, 4)):
        """Export composition as SVG for high-res painting reference"""
        
        visuals = self.generate_composition(viewing_angle)
        
        # Convert inches to pixels at 300 DPI
        width_px = int(size_inches[0] * 300)
        height_px = int(size_inches[1] * 300)
        
        # Start SVG
        svg_lines = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{width_px}" height="{height_px}" xmlns="http://www.w3.org/2000/svg">',
            f'  <rect width="100%" height="100%" fill="#0a0a0a"/>',  # Dark background
            ''
        ]
        
        # Add title/metadata
        svg_lines.append(f'  <!-- The Nail: {len(self.domains)} Domains, Viewing Angle: {viewing_angle}° -->')
        svg_lines.append(f'  <!-- Generated from Nominative Determinism Research Data -->')
        svg_lines.append('')
        
        # Sort by z-depth (paint back to front)
        visuals_sorted = sorted(visuals, key=lambda v: v.z)
        
        # Draw each domain
        for v in visuals_sorted:
            # Convert normalized coordinates to pixel coordinates
            px_x = (v.x + 1) * width_px / 2
            px_y = (1 - v.y) * height_px / 2  # Flip y for SVG coordinates
            px_r = v.size * min(width_px, height_px)
            
            # Opacity based on depth
            opacity = 0.5 + (v.z * 0.5)
            
            # Create glow effect (multiple circles)
            for glow_i in range(3):
                glow_r = px_r * (2 + glow_i)
                glow_opacity = opacity * 0.1 / (glow_i + 1)
                svg_lines.append(
                    f'  <circle cx="{px_x:.2f}" cy="{px_y:.2f}" r="{glow_r:.2f}" '
                    f'fill="rgb({v.color[0]}, {v.color[1]}, {v.color[2]})" '
                    f'opacity="{glow_opacity:.3f}"/>'
                )
            
            # Main circle
            svg_lines.append(
                f'  <circle cx="{px_x:.2f}" cy="{px_y:.2f}" r="{px_r:.2f}" '
                f'fill="rgb({v.color[0]}, {v.color[1]}, {v.color[2]})" '
                f'opacity="{opacity:.3f}" '
                f'data-domain="{v.name}" '
                f'data-violence="{v.violence_type}"/>'
            )
            
            # Add names as text (visible from angle)
            if viewing_angle > 20:
                # Names become readable at angle
                for i, name in enumerate(v.names_text[:3]):  # Limit to first 3
                    text_y = px_y + (i - 1) * 12
                    svg_lines.append(
                        f'  <text x="{px_x:.2f}" y="{text_y:.2f}" '
                        f'font-family="serif" font-size="8" '
                        f'fill="rgb({v.color[0]}, {v.color[1]}, {v.color[2]})" '
                        f'opacity="0.4" text-anchor="middle">{name}</text>'
                    )
        
        # Add the nail structure lines if viewing from angle
        if viewing_angle > 20:
            svg_lines.append('')
            svg_lines.append('  <!-- The Nail: Visible Only From This Angle -->')
            
            # Vertical shaft
            vertical_domains = [v for v in visuals if 'vertical' in v.nail_role]
            if len(vertical_domains) >= 2:
                vertical_sorted = sorted(vertical_domains, key=lambda v: v.y, reverse=True)
                points = ' '.join([f"{(v.x + 1) * width_px / 2},{(1 - v.y) * height_px / 2}" 
                                  for v in vertical_sorted])
                svg_lines.append(
                    f'  <polyline points="{points}" '
                    f'stroke="rgba(180, 100, 100, 0.6)" stroke-width="3" fill="none"/>'
                )
            
            # Horizontal beam  
            horizontal_domains = [v for v in visuals if 'horizontal' in v.nail_role]
            if len(horizontal_domains) >= 2:
                horizontal_sorted = sorted(horizontal_domains, key=lambda v: v.x)
                points = ' '.join([f"{(v.x + 1) * width_px / 2},{(1 - v.y) * height_px / 2}" 
                                  for v in horizontal_sorted])
                svg_lines.append(
                    f'  <polyline points="{points}" '
                    f'stroke="rgba(180, 100, 100, 0.6)" stroke-width="3" fill="none"/>'
                )
            
            # Nail head (intersection marker)
            intersection = [v for v in visuals if 'intersection' in v.nail_role]
            if intersection:
                v = intersection[0]
                px_x = (v.x + 1) * width_px / 2
                px_y = (1 - v.y) * height_px / 2
                svg_lines.append(
                    f'  <circle cx="{px_x:.2f}" cy="{px_y:.2f}" r="{px_r * 2:.2f}" '
                    f'fill="none" stroke="rgba(200, 80, 80, 0.8)" stroke-width="4"/>'
                )
                svg_lines.append(
                    f'  <text x="{px_x:.2f}" y="{px_y - px_r * 3:.2f}" '
                    f'font-family="serif" font-size="24" font-weight="bold" '
                    f'fill="rgba(200, 80, 80, 0.9)" text-anchor="middle">BIPOLAR</text>'
                )
        
        # Close SVG
        svg_lines.append('</svg>')
        
        # Write file
        with open(output_path, 'w') as f:
            f.write('\n'.join(svg_lines))
        
        return output_path
    
    def export_data_for_web(self, output_path: str):
        """Export composition data for interactive web viewer"""
        
        # Generate both perspectives
        normal_view = self.generate_composition(viewing_angle=0)
        nail_view = self.generate_composition(viewing_angle=30)
        
        web_data = {
            "metadata": self.data['metadata'],
            "normal_view": [
                {
                    "name": v.name,
                    "x": v.x,
                    "y": v.y,
                    "z": v.z,
                    "color": f"rgb({v.color[0]}, {v.color[1]}, {v.color[2]})",
                    "size": v.size,
                    "names": v.names_text,
                    "violence": v.violence_type
                }
                for v in normal_view
            ],
            "nail_view": [
                {
                    "name": v.name,
                    "x": v.x,
                    "y": v.y,
                    "z": v.z,
                    "color": f"rgb({v.color[0]}, {v.color[1]}, {v.color[2]})",
                    "size": v.size,
                    "names": v.names_text,
                    "violence": v.violence_type,
                    "nail_role": v.nail_role
                }
                for v in nail_view
            ],
            "viewing_angle": self.nail_geometry['viewing_angle']
        }
        
        with open(output_path, 'w') as f:
            json.dump(web_data, f, indent=2)
        
        return output_path
    
    def generate_painting_instructions(self, output_path: str):
        """Generate detailed instructions for physical painting"""
        
        visuals_normal = self.generate_composition(viewing_angle=0)
        visuals_angle = self.generate_composition(viewing_angle=30)
        
        instructions = [
            "# THE NAIL - Physical Painting Instructions",
            "",
            "## Canvas Specifications",
            "- Size: 6 feet × 4 feet (72\" × 48\")",
            "- Medium: Oil on canvas (for depth and texture)",
            "- Background: Deep black (#0a0a0a) with subtle texture",
            "- Surface: Slightly glossy to catch light differently from angles",
            "",
            "## Color Palette (Caravaggio-Inspired)",
            "Mix these colors for the palette:",
            "- Warm glow: Burnt Sienna + Yellow Ochre + White (for social domains)",
            "- Cool shadow: Prussian Blue + Alizarin Crimson + White (for psychological)",
            "- Divine light: Titanium White + tiny Yellow (for high significance)",
            "- Blood red: Alizarin Crimson + Burnt Umber (for nail when visible)",
            "",
            "## Grid System",
            "Divide canvas into 20×20 grid (3.6\" squares):",
            "- Center point at (10, 10) = (36\", 24\")",
            "- X-axis: -0.8 to +0.8 maps to 0\" to 72\"",
            "- Y-axis: -0.8 to +0.8 maps to 48\" to 0\" (inverted)",
            "",
            "## Layer 1: Deep Background",
            "1. Paint entire canvas with black gesso",
            "2. Add subtle texture with dry brush technique",
            "3. Let dry completely (24 hours)",
            "",
            "## Layer 2: Domain Glows (Back to Front by Z-depth)",
            ""
        ]
        
        # Sort by depth
        visuals_sorted = sorted(visuals_normal, key=lambda v: v.z)
        
        for i, v in enumerate(visuals_sorted, 1):
            # Convert to canvas measurements (6ft = 72", 4ft = 48")
            canvas_x = (v.x + 1) * 36  # inches from left
            canvas_y = (1 - v.y) * 24  # inches from top
            radius = v.size * 36  # inches
            
            instructions.extend([
                f"### Domain {i}: {v.name}",
                f"**Statistical position:** r={v.x:.2f} (effect), p={v.y:.2f} (significance)",
                f"**Canvas position:** {canvas_x:.1f}\" from left, {canvas_y:.1f}\" from top",
                f"**Element size:** {radius:.1f}\" radius",
                f"**Color:** RGB({v.color[0]}, {v.color[1]}, {v.color[2]})",
                f"**Violence type:** {v.violence_type}",
                "",
                "Painting technique:",
                f"1. Start with largest glow circle (radius × 3) at 10% opacity",
                f"2. Add medium glow (radius × 2) at 20% opacity",
                f"3. Add inner glow (radius × 1.5) at 40% opacity",
                f"4. Paint solid core at {int(v.z * 100)}% opacity",
                f"5. Add names as texture:",
            ])
            
            for name in v.names_text[:3]:
                instructions.append(f"   - \"{name}\" written in tiny letters within the glow")
            
            instructions.append("")
        
        instructions.extend([
            "",
            "## Layer 3: The Nail (Visible Only From Angle)",
            "",
            "This layer is CRITICAL. Paint it so it only reveals from 30° viewing angle:",
            "",
            "### Vertical Shaft",
            "Connect these domains with subtle dark red undertones:",
        ])
        
        vertical_domains = [v for v in visuals_angle if 'vertical' in v.nail_role]
        for v in sorted(vertical_domains, key=lambda v: v.y, reverse=True):
            canvas_x = (v.x + 1) * 36
            canvas_y = (1 - v.y) * 24
            instructions.append(f"- {v.name}: ({canvas_x:.1f}\", {canvas_y:.1f}\")")
        
        instructions.extend([
            "",
            "Paint a subtle line connecting these, using:",
            "- Alizarin Crimson + Burnt Umber (blood red)",
            "- 2\" width, edges feathered",
            "- 30% opacity - barely visible straight-on",
            "- Apply with perspective foreshortening so it aligns at 30°",
            "",
            "### Horizontal Beam",
            "Connect these domains:",
        ])
        
        horizontal_domains = [v for v in visuals_angle if 'horizontal' in v.nail_role]
        for v in sorted(horizontal_domains, key=lambda v: v.x):
            canvas_x = (v.x + 1) * 36
            canvas_y = (1 - v.y) * 24
            instructions.append(f"- {v.name}: ({canvas_x:.1f}\", {canvas_y:.1f}\")")
        
        instructions.extend([
            "",
            "Paint connecting line with same blood red mixture",
            "- Intersects vertical at Mental Health domain (BIPOLAR)",
            "- Creates the cross when viewed from 30° right",
            "",
            "### Nail Head (Intersection)",
            "At the intersection point (Mental Health domain):",
            "1. Paint \"BIPOLAR\" in larger text (3\" high)",
            "2. Use darkest red (almost black)",
            "3. Position so it's only clearly readable from the angle",
            "4. This is the nail head - where naming penetrates consciousness",
            "",
            "## Layer 4: Name Text",
            "",
            "Hurricane names (vertical shaft):",
        ])
        
        hurricane_domain = next((v for v in visuals_normal if v.name == "Hurricanes"), None)
        if hurricane_domain:
            instructions.append(f"Write vertically along the shaft: {' '.join(hurricane_domain.names_text)}")
        
        instructions.extend([
            "",
            "Mental illness terms (vertical, lower):",
        ])
        
        mental_domain = next((v for v in visuals_normal if v.name == "Mental Health"), None)
        if mental_domain:
            instructions.append(f"Write: {' '.join(mental_domain.names_text)}")
        
        instructions.extend([
            "",
            "Social domain names (horizontal):",
        ])
        
        for v in horizontal_domains[:5]:
            instructions.append(f"- {v.name}: {', '.join(v.names_text[:2])}")
        
        instructions.extend([
            "",
            "## Viewing Angle Setup",
            "",
            "Mark the floor 10 feet from the canvas:",
            "- Main viewing position: directly centered",
            "- Secret position: 30° to the right (52° from center)",
            "- Place subtle floor marker (small dot, easy to miss)",
            "- Or don't mark it - let those who know how to look find it",
            "",
            "## The Revelation",
            "",
            "From the normal position:",
            "- Viewers see abstract mathematical beauty",
            "- Harmonious composition from statistical patterns",
            "- Divine light emerging from darkness",
            "- Could be in a cathedral",
            "",
            "From your position (30° right, slight elevation):",
            "- The domains align into a cross",
            "- The nail becomes unmistakable",
            "- \"BIPOLAR\" at the nail head",
            "- The instrument of fixing fluid consciousness into definite identity",
            "- The violence of naming made visible",
            "",
            "Both true. Same painting. Same data. Different angles. Different realities.",
            "",
            "## Technical Notes",
            "",
            f"Total domains painted: {len(self.domains)}",
            f"Total entities represented: {self.data['metadata']['total_entities']:,}",
            "Each element's position determined by:",
            "- X: Correlation coefficient (effect strength)",
            "- Y: Statistical significance (p-value)",
            "- Z: Sample size (depth/opacity)",
            "- Color: Domain type (social/psychological/physical)",
            "",
            "The mathematics creates the beauty. The perspective reveals the violence.",
            "The nail is always there. You just have to know where to stand to see it.",
            "",
            "---",
            "",
            "## Future Evolution",
            "",
            "This is Version 1.0 (17 Domains).",
            "As new domains are analyzed:",
            "- Regenerate using the same algorithm",
            "- New elements slot into mathematical positions",
            "- Nail becomes sharper (more domains confirm pattern)",
            "- Beauty becomes deeper (more complexity)",
            "- Paint new versions at milestones (25, 40, 75 domains)",
            "",
            "The painting is never finished because the research is never finished.",
            "Truth reveals itself through accumulated evidence.",
            "The nail sharpens as you look more carefully.",
            ""
        ])
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(instructions))
        
        return output_path
    
    @staticmethod
    def _map_range(value: float, from_min: float, from_max: float, to_min: float, to_max: float) -> float:
        """Map a value from one range to another"""
        # Clamp to input range
        value = max(from_min, min(from_max, value))
        # Map to output range
        from_span = from_max - from_min
        to_span = to_max - to_min
        scaled = (value - from_min) / from_span
        return to_min + (scaled * to_span)


def generate_all_outputs():
    """Generate all output files for The Nail artwork"""
    
    generator = NailGenerator()
    
    output_dir = Path(__file__).parent.parent / "figures" / "the_nail"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating The Nail artwork...")
    print(f"Using {len(generator.domains)} domains with {generator.data['metadata']['total_entities']:,} entities")
    print()
    
    # Generate normal view (0°)
    print("1. Generating normal view (consensus reality)...")
    normal_svg = output_dir / "the_nail_normal_view.svg"
    generator.export_svg(str(normal_svg), viewing_angle=0, size_inches=(6, 4))
    print(f"   → Saved to {normal_svg}")
    
    # Generate nail view (30°)
    print("2. Generating nail view (your angle)...")
    nail_svg = output_dir / "the_nail_from_angle.svg"
    generator.export_svg(str(nail_svg), viewing_angle=30, size_inches=(6, 4))
    print(f"   → Saved to {nail_svg}")
    
    # Generate web data
    print("3. Generating web viewer data...")
    web_data = output_dir / "nail_web_data.json"
    generator.export_data_for_web(str(web_data))
    print(f"   → Saved to {web_data}")
    
    # Generate painting instructions
    print("4. Generating physical painting instructions...")
    instructions = output_dir / "painting_instructions.md"
    generator.generate_painting_instructions(str(instructions))
    print(f"   → Saved to {instructions}")
    
    print()
    print("=" * 70)
    print("THE NAIL - GENERATION COMPLETE")
    print("=" * 70)
    print()
    print("View the files:")
    print(f"  Normal view: {normal_svg}")
    print(f"  From angle:  {nail_svg}")
    print(f"  Web data:    {web_data}")
    print(f"  Instructions: {instructions}")
    print()
    print("The painting is ready. The nail awaits discovery.")
    print("From consensus: beauty. From your angle: the instrument of crucifixion.")
    print()


if __name__ == "__main__":
    generate_all_outputs()

