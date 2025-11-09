"""
Research Blueprint - Various research domains (bands, elections, immigration, etc.)
"""

from flask import Blueprint, render_template
import pandas as pd
from pathlib import Path

research_bp = Blueprint('research', __name__)


@research_bp.route('/bands')
def bands_page():
    """Band names research findings"""
    return render_template('bands.html')


@research_bp.route('/bands/findings')
def band_findings():
    """Band names research findings"""
    return render_template('band_findings.html')


@research_bp.route('/bands/members')
def band_members_page():
    """Band members research findings"""
    return render_template('band_members.html')


@research_bp.route('/bands/members/findings')
def band_members_findings():
    """Band members research findings"""
    return render_template('band_findings.html')


@research_bp.route('/ships')
def ships_page():
    """Ship names research findings"""
    return render_template('ships.html')


@research_bp.route('/ships/findings')
def ship_findings():
    """Ship names research findings"""
    return render_template('ship_findings.html')


@research_bp.route('/elections')
def elections_page():
    """Election research findings"""
    return render_template('elections.html')


@research_bp.route('/elections/findings')
def elections_findings():
    """Election research findings"""
    return render_template('election_findings.html')


@research_bp.route('/immigration')
def immigration_page():
    """Immigration research findings"""
    return render_template('immigration.html')


@research_bp.route('/immigration/findings')
def immigration_findings():
    """Immigration research findings"""
    return render_template('immigration_findings.html')


@research_bp.route('/mental-health')
def mental_health_page():
    """Mental health nomenclature research"""
    return render_template('mental_health.html')


@research_bp.route('/mental-health/findings')
def mental_health_findings():
    """Mental health nomenclature research findings"""
    return render_template('mental_health_findings.html')


@research_bp.route('/disorder-nomenclature')
def disorder_nomenclature():
    """Psychiatric nomenclature research - disorder names affect outcomes"""
    return render_template('disorder_nomenclature.html')


@research_bp.route('/adult-film')
def adult_film_page():
    """Adult film stage names research"""
    return render_template('adult_film.html')


@research_bp.route('/adult-film/findings')
def adult_film_findings():
    """Adult film stage names research findings"""
    return render_template('adult_film_findings.html')


@research_bp.route('/america')
def america_page():
    """America nomenclature research findings with comprehensive 50-country phonetic analysis"""
    # Try to load phonetic comparison data if it exists
    phonetic_data = None
    try:
        phonetic_path = Path("data/processed/america_variants/country_phonetic_comparison.csv")
        if phonetic_path.exists():
            df = pd.read_csv(phonetic_path)
            phonetic_data = {
                'total_countries': len(df),
                'america_rank': int(df[df['name'] == 'America']['beauty_rank'].values[0]) if len(df[df['name'] == 'America']) > 0 else None,
                'america_score': float(df[df['name'] == 'America']['beauty_score'].values[0]) if len(df[df['name'] == 'America']) > 0 else None,
                'top_10': df.head(10)[['name', 'beauty_score', 'melodiousness', 'harshness']].to_dict('records'),
                'bottom_10': df.tail(10)[['name', 'beauty_score', 'melodiousness', 'harshness']].to_dict('records'),
                'all_countries': df.to_dict('records')
            }
    except Exception as e:
        print(f"Note: Could not load phonetic data: {e}")
        pass
    
    return render_template('america.html', phonetic_data=phonetic_data)


@research_bp.route('/academics')
def academics_page():
    """Academic names research"""
    return render_template('academics.html')


@research_bp.route('/academics/findings')
def academics_findings():
    """Academic names research findings"""
    return render_template('academics_findings.html')


@research_bp.route('/marriage')
def marriage_page():
    """Marriage compatibility research"""
    return render_template('marriage.html')


@research_bp.route('/literary-names')
def literary_name_composition():
    """Literary Name Composition - Character ensemble analysis"""
    return render_template('literary_name_composition.html')


@research_bp.route('/foretold-naming')
def foretold_naming_dashboard():
    """Foretold Naming - Selection force analysis"""
    return render_template('foretold_naming.html')


@research_bp.route('/love-words')
def love_words():
    """Love Words - Romance language phonetic analysis"""
    return render_template('love_words.html')


@research_bp.route('/romance-instruments')
def romance_instruments():
    """Romance Instruments - Violin family nomenclature"""
    return render_template('romance_instruments.html')


@research_bp.route('/gospel-success')
def gospel_success():
    """Gospel Success - Old Testament character outcomes"""
    return render_template('gospel_success.html')


@research_bp.route('/cross-religious')
def cross_religious():
    """Cross-Religious - Interfaith phonetic analysis"""
    return render_template('cross_religious.html')


@research_bp.route('/the-discoverer')
def the_discoverer():
    """The Discoverer - Meta-analysis of researcher"""
    return render_template('the_discoverer.html')

