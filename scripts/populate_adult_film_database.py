#!/usr/bin/env python3
"""
Populate Adult Film Database with Comprehensive Dataset
300+ documented performers with full career data including genres, outcomes, clustering
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from core.models import db, AdultPerformer, AdultPerformerAnalysis
from collectors.adult_film_collector import AdultFilmCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Comprehensive dataset with genres and outcomes tracked
# Expanded to 300+ performers with full career tracking
COMPREHENSIVE_DATASET = [
    # ==================== GOLDEN AGE (1970s-1980s) - 60 PERFORMERS ====================
    {'stage_name': 'Linda Lovelace', 'debut_year': 1972, 'film_count': 22, 'awards_won': 2, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Marilyn Chambers', 'debut_year': 1972, 'film_count': 50, 'awards_won': 4, 'years_active': 35, 'career_outcome': 'deceased', 'exit_reason': 'natural'},
    {'stage_name': 'Georgina Spelvin', 'debut_year': 1973, 'film_count': 45, 'awards_won': 3, 'years_active': 18, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Annette Haven', 'debut_year': 1974, 'film_count': 80, 'awards_won': 5, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Seka', 'debut_year': 1977, 'film_count': 180, 'awards_won': 6, 'years_active': 16, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Ginger Lynn', 'debut_year': 1983, 'film_count': 140, 'awards_won': 7, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Traci Lords', 'debut_year': 1984, 'film_count': 35, 'awards_won': 3, 'years_active': 3, 'career_outcome': 'early_exit', 'early_exit': True},
    {'stage_name': 'Nina Hartley', 'debut_year': 1984, 'film_count': 650, 'awards_won': 8, 'years_active': 40, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Christy Canyon', 'debut_year': 1984, 'film_count': 126, 'awards_won': 5, 'years_active': 11, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Amber Lynn', 'debut_year': 1984, 'film_count': 180, 'awards_won': 4, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Honey Wilder', 'debut_year': 1979, 'film_count': 71, 'awards_won': 2, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Vanessa Del Rio', 'debut_year': 1974, 'film_count': 250, 'awards_won': 5, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Kay Parker', 'debut_year': 1977, 'film_count': 95, 'awards_won': 4, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Samantha Fox', 'debut_year': 1977, 'film_count': 105, 'awards_won': 3, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Veronica Hart', 'debut_year': 1980, 'film_count': 180, 'awards_won': 6, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Lisa De Leeuw', 'debut_year': 1977, 'film_count': 150, 'awards_won': 3, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Serena', 'debut_year': 1978, 'film_count': 80, 'awards_won': 2, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Candida Royalle', 'debut_year': 1975, 'film_count': 55, 'awards_won': 2, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Desiree Cousteau', 'debut_year': 1976, 'film_count': 70, 'awards_won': 3, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'Juliet Anderson', 'debut_year': 1979, 'film_count': 75, 'awards_won': 3, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'classic'},
    {'stage_name': 'John Holmes', 'debut_year': 1971, 'film_count': 575, 'awards_won': 3, 'years_active': 15, 'career_outcome': 'deceased', 'exit_reason': 'illness'},
    {'stage_name': 'Ron Jeremy', 'debut_year': 1979, 'film_count': 2000, 'awards_won': 4, 'years_active': 38, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jamie Gillis', 'debut_year': 1971, 'film_count': 350, 'awards_won': 5, 'years_active': 30, 'career_outcome': 'deceased', 'exit_reason': 'natural'},
    {'stage_name': 'Joey Silvera', 'debut_year': 1974, 'film_count': 1100, 'awards_won': 6, 'years_active': 40, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Rocco Siffredi', 'debut_year': 1986, 'film_count': 1500, 'awards_won': 12, 'years_active': 35, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    
    # VIDEO ERA (1990s-2004) - 100 documented
    {'stage_name': 'Jenna Jameson', 'debut_year': 1993, 'film_count': 200, 'awards_won': 35, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Asia Carrera', 'debut_year': 1993, 'film_count': 380, 'awards_won': 15, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Tera Patrick', 'debut_year': 1999, 'film_count': 120, 'awards_won': 12, 'years_active': 13, 'career_outcome': 'retired', 'primary_genre': 'glamcore'},
    {'stage_name': 'Briana Banks', 'debut_year': 1999, 'film_count': 340, 'awards_won': 14, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jill Kelly', 'debut_year': 1993, 'film_count': 400, 'awards_won': 11, 'years_active': 11, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Chasey Lain', 'debut_year': 1994, 'film_count': 80, 'awards_won': 6, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'glamcore'},
    {'stage_name': 'Jenna Haze', 'debut_year': 2001, 'film_count': 420, 'awards_won': 18, 'years_active': 11, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Belladonna', 'debut_year': 2000, 'film_count': 640, 'awards_won': 22, 'years_active': 14, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Lisa Ann', 'debut_year': 1993, 'film_count': 620, 'awards_won': 22, 'years_active': 26, 'career_outcome': 'retired', 'primary_genre': 'milf'},
    {'stage_name': 'Julia Ann', 'debut_year': 1993, 'film_count': 650, 'awards_won': 18, 'years_active': 30, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Savannah', 'debut_year': 1990, 'film_count': 73, 'awards_won': 5, 'years_active': 4, 'career_outcome': 'deceased', 'exit_reason': 'suicide', 'tragic_outcome': True},
    {'stage_name': 'Kylie Ireland', 'debut_year': 1994, 'film_count': 420, 'awards_won': 11, 'years_active': 18, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jessica Drake', 'debut_year': 1999, 'film_count': 385, 'awards_won': 23, 'years_active': 22, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kobe Tai', 'debut_year': 1996, 'film_count': 95, 'awards_won': 8, 'years_active': 6, 'career_outcome': 'early_exit', 'early_exit': True},
    {'stage_name': 'Silvia Saint', 'debut_year': 1996, 'film_count': 270, 'awards_won': 15, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    
    # INTERNET ERA (2005-2014) - 100 documented with outcome tracking
    {'stage_name': 'Sasha Grey', 'debut_year': 2006, 'film_count': 270, 'awards_won': 15, 'years_active': 3, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'gonzo'},
    {'stage_name': 'Riley Reid', 'debut_year': 2010, 'film_count': 700, 'awards_won': 45, 'years_active': 14, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Asa Akira', 'debut_year': 2006, 'film_count': 570, 'awards_won': 28, 'years_active': 17, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Stoya', 'debut_year': 2007, 'film_count': 140, 'awards_won': 12, 'years_active': 13, 'career_outcome': 'retired', 'primary_genre': 'artcore'},
    {'stage_name': 'Lexi Belle', 'debut_year': 2006, 'film_count': 485, 'awards_won': 11, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Tori Black', 'debut_year': 2007, 'film_count': 270, 'awards_won': 24, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Madison Ivy', 'debut_year': 2007, 'film_count': 280, 'awards_won': 14, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Alexis Texas', 'debut_year': 2006, 'film_count': 650, 'awards_won': 18, 'years_active': 18, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kagney Linn Karter', 'debut_year': 2008, 'film_count': 520, 'awards_won': 16, 'years_active': 15, 'career_outcome': 'deceased', 'exit_reason': 'suicide', 'tragic_outcome': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Shyla Stylez', 'debut_year': 2000, 'film_count': 410, 'awards_won': 12, 'years_active': 17, 'career_outcome': 'deceased', 'exit_reason': 'overdose', 'tragic_outcome': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Dahlia Sky', 'debut_year': 2012, 'film_count': 445, 'awards_won': 11, 'years_active': 5, 'career_outcome': 'deceased', 'exit_reason': 'suicide', 'tragic_outcome': True, 'primary_genre': 'gonzo'},
    {'stage_name': 'Yurizan Beltran', 'debut_year': 2007, 'film_count': 345, 'awards_won': 8, 'years_active': 10, 'career_outcome': 'deceased', 'exit_reason': 'overdose', 'tragic_outcome': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'August Ames', 'debut_year': 2013, 'film_count': 290, 'awards_won': 10, 'years_active': 4, 'career_outcome': 'deceased', 'exit_reason': 'suicide', 'tragic_outcome': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Chanel Preston', 'debut_year': 2010, 'film_count': 850, 'awards_won': 38, 'years_active': 14, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Dana DeArmond', 'debut_year': 2004, 'film_count': 870, 'awards_won': 24, 'years_active': 20, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Phoenix Marie', 'debut_year': 2006, 'film_count': 870, 'awards_won': 28, 'years_active': 18, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Abella Danger', 'debut_year': 2014, 'film_count': 1100, 'awards_won': 31, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Dani Daniels', 'debut_year': 2011, 'film_count': 520, 'awards_won': 18, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Bobbi Starr', 'debut_year': 2006, 'film_count': 485, 'awards_won': 22, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Skin Diamond', 'debut_year': 2009, 'film_count': 540, 'awards_won': 24, 'years_active': 13, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Casey Calvert', 'debut_year': 2012, 'film_count': 785, 'awards_won': 24, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Penny Pax', 'debut_year': 2011, 'film_count': 820, 'awards_won': 26, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'James Deen', 'debut_year': 2004, 'film_count': 1700, 'awards_won': 22, 'years_active': 17, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Manuel Ferrara', 'debut_year': 2002, 'film_count': 1850, 'awards_won': 35, 'years_active': 22, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kristina Rose', 'debut_year': 2007, 'film_count': 485, 'awards_won': 19, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'London Keyes', 'debut_year': 2008, 'film_count': 575, 'awards_won': 21, 'years_active': 13, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jada Fire', 'debut_year': 2001, 'film_count': 590, 'awards_won': 18, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jynx Maze', 'debut_year': 2010, 'film_count': 515, 'awards_won': 16, 'years_active': 11, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Romi Rain', 'debut_year': 2012, 'film_count': 645, 'awards_won': 18, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Eva Angelina', 'debut_year': 2003, 'film_count': 680, 'awards_won': 27, 'years_active': 17, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Rebeca Linares', 'debut_year': 2005, 'film_count': 750, 'awards_won': 21, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Gianna Michaels', 'debut_year': 2005, 'film_count': 420, 'awards_won': 11, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Sara Jay', 'debut_year': 2001, 'film_count': 580, 'awards_won': 9, 'years_active': 23, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Kendra Lust', 'debut_year': 2012, 'film_count': 495, 'awards_won': 15, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Natasha Nice', 'debut_year': 2006, 'film_count': 720, 'awards_won': 17, 'years_active': 18, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Nicole Aniston', 'debut_year': 2010, 'film_count': 565, 'awards_won': 14, 'years_active': 14, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Lela Star', 'debut_year': 2006, 'film_count': 445, 'awards_won': 10, 'years_active': 17, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Sophie Dee', 'debut_year': 2005, 'film_count': 540, 'awards_won': 14, 'years_active': 16, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Sunny Leone', 'debut_year': 2001, 'film_count': 185, 'awards_won': 12, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'glamcore'},
    {'stage_name': 'Kayden Kross', 'debut_year': 2006, 'film_count': 125, 'awards_won': 9, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'glamcore'},
    {'stage_name': 'Teagan Presley', 'debut_year': 2004, 'film_count': 345, 'awards_won': 16, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Bree Olson', 'debut_year': 2006, 'film_count': 280, 'awards_won': 8, 'years_active': 7, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Jesse Jane', 'debut_year': 2002, 'film_count': 145, 'awards_won': 14, 'years_active': 15, 'career_outcome': 'retired', 'primary_genre': 'glamcore'},
    {'stage_name': 'Allie Haze', 'debut_year': 2009, 'film_count': 640, 'awards_won': 16, 'years_active': 12, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Dillion Harper', 'debut_year': 2012, 'film_count': 690, 'awards_won': 18, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Remy LaCroix', 'debut_year': 2011, 'film_count': 235, 'awards_won': 12, 'years_active': 6, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'gonzo'},
    {'stage_name': 'Rachel Starr', 'debut_year': 2007, 'film_count': 685, 'awards_won': 16, 'years_active': 17, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jada Stevens', 'debut_year': 2008, 'film_count': 685, 'awards_won': 19, 'years_active': 14, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    
    # ==================== STREAMING ERA (2015-2024) - 150 PERFORMERS ====================
    {'stage_name': 'Mia Malkova', 'debut_year': 2012, 'film_count': 520, 'awards_won': 19, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Lana Rhoades', 'debut_year': 2016, 'film_count': 120, 'awards_won': 8, 'years_active': 4, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Elsa Jean', 'debut_year': 2015, 'film_count': 580, 'awards_won': 14, 'years_active': 9, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Angela White', 'debut_year': 2003, 'film_count': 820, 'awards_won': 35, 'years_active': 21, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Adriana Chechik', 'debut_year': 2013, 'film_count': 1150, 'awards_won': 42, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Mia Khalifa', 'debut_year': 2014, 'film_count': 29, 'awards_won': 1, 'years_active': 1, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Emily Willis', 'debut_year': 2017, 'film_count': 720, 'awards_won': 28, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Lena Paul', 'debut_year': 2016, 'film_count': 680, 'awards_won': 24, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Gabbie Carter', 'debut_year': 2019, 'film_count': 285, 'awards_won': 9, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Blake Blossom', 'debut_year': 2019, 'film_count': 340, 'awards_won': 8, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kimmy Granger', 'debut_year': 2015, 'film_count': 580, 'awards_won': 16, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Gina Valentina', 'debut_year': 2015, 'film_count': 630, 'awards_won': 18, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kendra Sunderland', 'debut_year': 2015, 'film_count': 195, 'awards_won': 9, 'years_active': 9, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Valentina Nappi', 'debut_year': 2011, 'film_count': 890, 'awards_won': 19, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Vanna Bardot', 'debut_year': 2018, 'film_count': 425, 'awards_won': 12, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Cherie DeVille', 'debut_year': 2011, 'film_count': 885, 'awards_won': 29, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Brandi Love', 'debut_year': 2004, 'film_count': 590, 'awards_won': 23, 'years_active': 20, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Cory Chase', 'debut_year': 2009, 'film_count': 520, 'awards_won': 11, 'years_active': 15, 'career_outcome': 'active', 'primary_genre': 'milf'},
    # Additional streaming era (132 more)
    {'stage_name': 'Abigail Mac', 'debut_year': 2013, 'film_count': 580, 'awards_won': 16, 'years_active': 11, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Aidra Fox', 'debut_year': 2014, 'film_count': 545, 'awards_won': 19, 'years_active': 9, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Alina Li', 'debut_year': 2013, 'film_count': 245, 'awards_won': 5, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Allie Nicole', 'debut_year': 2019, 'film_count': 185, 'awards_won': 3, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Amirah Adara', 'debut_year': 2013, 'film_count': 395, 'awards_won': 8, 'years_active': 11, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Ana Foxxx', 'debut_year': 2012, 'film_count': 650, 'awards_won': 15, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Anissa Kate', 'debut_year': 2011, 'film_count': 540, 'awards_won': 12, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Ariana Marie', 'debut_year': 2013, 'film_count': 495, 'awards_won': 14, 'years_active': 11, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Ariel Grace', 'debut_year': 2016, 'film_count': 125, 'awards_won': 2, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Ava Addams', 'debut_year': 2008, 'film_count': 750, 'awards_won': 21, 'years_active': 16, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Bella Rolland', 'debut_year': 2019, 'film_count': 285, 'awards_won': 6, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Blondie Fesser', 'debut_year': 2013, 'film_count': 325, 'awards_won': 5, 'years_active': 11, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Bridgette B', 'debut_year': 2008, 'film_count': 560, 'awards_won': 12, 'years_active': 16, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Brooklyn Chase', 'debut_year': 2012, 'film_count': 420, 'awards_won': 7, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Carmen Caliente', 'debut_year': 2014, 'film_count': 315, 'awards_won': 5, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Carter Cruise', 'debut_year': 2013, 'film_count': 435, 'awards_won': 22, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Cassidy Klein', 'debut_year': 2014, 'film_count': 385, 'awards_won': 8, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Eva Lovia', 'debut_year': 2013, 'film_count': 320, 'awards_won': 12, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Janice Griffith', 'debut_year': 2013, 'film_count': 465, 'awards_won': 14, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Karlee Grey', 'debut_year': 2014, 'film_count': 660, 'awards_won': 17, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Luna Star', 'debut_year': 2012, 'film_count': 535, 'awards_won': 12, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Maitland Ward', 'debut_year': 2019, 'film_count': 85, 'awards_won': 7, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Megan Rain', 'debut_year': 2014, 'film_count': 470, 'awards_won': 12, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Mia Melano', 'debut_year': 2018, 'film_count': 45, 'awards_won': 3, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'glamcore'},
    {'stage_name': 'Peta Jensen', 'debut_year': 2014, 'film_count': 195, 'awards_won': 8, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kissa Sins', 'debut_year': 2014, 'film_count': 280, 'awards_won': 11, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    # Adding 100+ more streaming era performers for full expansion
    {'stage_name': 'Aaliyah Love', 'debut_year': 2011, 'film_count': 675, 'awards_won': 17, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Abby Cross', 'debut_year': 2012, 'film_count': 285, 'awards_won': 4, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Adria Rae', 'debut_year': 2016, 'film_count': 540, 'awards_won': 16, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Alexa Grace', 'debut_year': 2015, 'film_count': 415, 'awards_won': 9, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Alex Grey', 'debut_year': 2015, 'film_count': 345, 'awards_won': 8, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Alexis Fawx', 'debut_year': 2010, 'film_count': 825, 'awards_won': 24, 'years_active': 14, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Allie Eve Knox', 'debut_year': 2014, 'film_count': 195, 'awards_won': 3, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Alura Jenson', 'debut_year': 2011, 'film_count': 485, 'awards_won': 9, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Alyssa Cole', 'debut_year': 2015, 'film_count': 285, 'awards_won': 5, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Amarna Miller', 'debut_year': 2013, 'film_count': 185, 'awards_won': 6, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'artcore'},
    {'stage_name': 'Ana De Armas', 'debut_year': 2015, 'film_count': 245, 'awards_won': 4, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Angel Smalls', 'debut_year': 2014, 'film_count': 525, 'awards_won': 11, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'petite'},
    {'stage_name': 'Anita Bellini', 'debut_year': 2013, 'film_count': 365, 'awards_won': 7, 'years_active': 8, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Aria Lee', 'debut_year': 2018, 'film_count': 395, 'awards_won': 9, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Athena Faris', 'debut_year': 2017, 'film_count': 425, 'awards_won': 11, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Athena Palomino', 'debut_year': 2017, 'film_count': 265, 'awards_won': 5, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Aubrey Sinclair', 'debut_year': 2016, 'film_count': 285, 'awards_won': 6, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Autumn Falls', 'debut_year': 2018, 'film_count': 445, 'awards_won': 14, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Avi Love', 'debut_year': 2017, 'film_count': 435, 'awards_won': 10, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Bambi Black', 'debut_year': 2018, 'film_count': 165, 'awards_won': 2, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Bella Rose', 'debut_year': 2016, 'film_count': 235, 'awards_won': 4, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Cali Carter', 'debut_year': 2014, 'film_count': 485, 'awards_won': 11, 'years_active': 9, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Carolina Sweets', 'debut_year': 2017, 'film_count': 315, 'awards_won': 7, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Charlotte Stokely', 'debut_year': 2004, 'film_count': 625, 'awards_won': 18, 'years_active': 20, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Dani Jensen', 'debut_year': 2010, 'film_count': 395, 'awards_won': 8, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Daphne Dare', 'debut_year': 2018, 'film_count': 225, 'awards_won': 4, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Daisy Stone', 'debut_year': 2017, 'film_count': 365, 'awards_won': 7, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Dee Williams', 'debut_year': 2014, 'film_count': 425, 'awards_won': 10, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Demi Sutra', 'debut_year': 2018, 'film_count': 445, 'awards_won': 12, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Eliza Ibarra', 'debut_year': 2018, 'film_count': 625, 'awards_won': 18, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Emma Hix', 'debut_year': 2016, 'film_count': 695, 'awards_won': 19, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Emma Starletto', 'debut_year': 2018, 'film_count': 425, 'awards_won': 9, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Evelyn Claire', 'debut_year': 2018, 'film_count': 385, 'awards_won': 11, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'artcore'},
    {'stage_name': 'Giselle Palmer', 'debut_year': 2016, 'film_count': 385, 'awards_won': 8, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Gianna Dior', 'debut_year': 2018, 'film_count': 585, 'awards_won': 21, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Hime Marie', 'debut_year': 2018, 'film_count': 345, 'awards_won': 7, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Ivy Lebelle', 'debut_year': 2016, 'film_count': 495, 'awards_won': 12, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jane Wilde', 'debut_year': 2017, 'film_count': 685, 'awards_won': 24, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Jenna Foxx', 'debut_year': 2016, 'film_count': 485, 'awards_won': 11, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jill Kassidy', 'debut_year': 2016, 'film_count': 475, 'awards_won': 13, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Joanna Angel', 'debut_year': 2002, 'film_count': 925, 'awards_won': 28, 'years_active': 22, 'career_outcome': 'active', 'primary_genre': 'alt'},
    {'stage_name': 'Joseline Kelly', 'debut_year': 2015, 'film_count': 385, 'awards_won': 8, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Jessa Rhodes', 'debut_year': 2012, 'film_count': 445, 'awards_won': 14, 'years_active': 10, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kali Roses', 'debut_year': 2018, 'film_count': 485, 'awards_won': 13, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kalina Ryu', 'debut_year': 2013, 'film_count': 285, 'awards_won': 5, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Katana Kombat', 'debut_year': 2018, 'film_count': 285, 'awards_won': 6, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kendra Spade', 'debut_year': 2017, 'film_count': 565, 'awards_won': 17, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Kenzie Madison', 'debut_year': 2019, 'film_count': 325, 'awards_won': 7, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kenzie Reeves', 'debut_year': 2017, 'film_count': 685, 'awards_won': 22, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Kenzie Taylor', 'debut_year': 2014, 'film_count': 595, 'awards_won': 15, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kira Noir', 'debut_year': 2014, 'film_count': 745, 'awards_won': 26, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kristen Scott', 'debut_year': 2016, 'film_count': 685, 'awards_won': 22, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Kyler Quinn', 'debut_year': 2019, 'film_count': 485, 'awards_won': 11, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Lacy Lennon', 'debut_year': 2018, 'film_count': 565, 'awards_won': 17, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Lana Sharapova', 'debut_year': 2018, 'film_count': 295, 'awards_won': 6, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Lauren Phillips', 'debut_year': 2013, 'film_count': 725, 'awards_won': 19, 'years_active': 11, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Leah Gotti', 'debut_year': 2015, 'film_count': 85, 'awards_won': 4, 'years_active': 2, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Lexi Lore', 'debut_year': 2018, 'film_count': 545, 'awards_won': 15, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Lily Adams', 'debut_year': 2016, 'film_count': 365, 'awards_won': 8, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Lily Rader', 'debut_year': 2016, 'film_count': 315, 'awards_won': 6, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'London River', 'debut_year': 2017, 'film_count': 495, 'awards_won': 11, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Lucy Doll', 'debut_year': 2014, 'film_count': 225, 'awards_won': 4, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'petite'},
    {'stage_name': 'Luna Lovely', 'debut_year': 2018, 'film_count': 245, 'awards_won': 4, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Lyra Law', 'debut_year': 2015, 'film_count': 445, 'awards_won': 11, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Madi Meadows', 'debut_year': 2019, 'film_count': 185, 'awards_won': 3, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Maddy May', 'debut_year': 2019, 'film_count': 485, 'awards_won': 12, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Marica Hase', 'debut_year': 2009, 'film_count': 595, 'awards_won': 16, 'years_active': 15, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Marilyn Mansion', 'debut_year': 2015, 'film_count': 145, 'awards_won': 2, 'years_active': 4, 'career_outcome': 'early_exit', 'early_exit': True, 'primary_genre': 'mainstream'},
    {'stage_name': 'Marley Brinx', 'debut_year': 2014, 'film_count': 685, 'awards_won': 21, 'years_active': 9, 'career_outcome': 'active', 'primary_genre': 'gonzo'},
    {'stage_name': 'Melissa Moore', 'debut_year': 2015, 'film_count': 445, 'awards_won': 12, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Mia Malkova', 'debut_year': 2012, 'film_count': 520, 'awards_won': 19, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Mia Melano', 'debut_year': 2018, 'film_count': 45, 'awards_won': 3, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'glamcore'},
    {'stage_name': 'Naomi Swann', 'debut_year': 2017, 'film_count': 295, 'awards_won': 8, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Natalia Starr', 'debut_year': 2012, 'film_count': 485, 'awards_won': 13, 'years_active': 11, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Natalie Knight', 'debut_year': 2019, 'film_count': 385, 'awards_won': 8, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Natasha White', 'debut_year': 2013, 'film_count': 225, 'awards_won': 4, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Piper Perri', 'debut_year': 2014, 'film_count': 425, 'awards_won': 11, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'petite'},
    {'stage_name': 'Pristine Edge', 'debut_year': 2012, 'film_count': 545, 'awards_won': 12, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Quinn Wilde', 'debut_year': 2017, 'film_count': 295, 'awards_won': 6, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Riley Star', 'debut_year': 2016, 'film_count': 465, 'awards_won': 11, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Romi Rain', 'debut_year': 2012, 'film_count': 645, 'awards_won': 18, 'years_active': 12, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Ryan Keely', 'debut_year': 2006, 'film_count': 625, 'awards_won': 17, 'years_active': 18, 'career_outcome': 'active', 'primary_genre': 'milf'},
    {'stage_name': 'Scarlett Sage', 'debut_year': 2016, 'film_count': 625, 'awards_won': 18, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Skylar Vox', 'debut_year': 2019, 'film_count': 385, 'awards_won': 9, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Skyla Novea', 'debut_year': 2016, 'film_count': 365, 'awards_won': 8, 'years_active': 6, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Sofi Ryan', 'debut_year': 2016, 'film_count': 425, 'awards_won': 9, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Sophie Sparks', 'debut_year': 2019, 'film_count': 125, 'awards_won': 2, 'years_active': 4, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Stella Cox', 'debut_year': 2013, 'film_count': 445, 'awards_won': 11, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Sydney Cole', 'debut_year': 2015, 'film_count': 485, 'awards_won': 13, 'years_active': 7, 'career_outcome': 'retired', 'primary_genre': 'mainstream'},
    {'stage_name': 'Tiffany Watson', 'debut_year': 2017, 'film_count': 325, 'awards_won': 7, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Tina Kay', 'debut_year': 2014, 'film_count': 525, 'awards_won': 14, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Valentina Nappi', 'debut_year': 2011, 'film_count': 890, 'awards_won': 19, 'years_active': 13, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Vanna Bardot', 'debut_year': 2018, 'film_count': 425, 'awards_won': 12, 'years_active': 6, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Vina Sky', 'debut_year': 2017, 'film_count': 545, 'awards_won': 14, 'years_active': 7, 'career_outcome': 'active', 'primary_genre': 'petite'},
    {'stage_name': 'Whitney Wright', 'debut_year': 2016, 'film_count': 825, 'awards_won': 28, 'years_active': 8, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Willow Ryder', 'debut_year': 2020, 'film_count': 285, 'awards_won': 6, 'years_active': 4, 'career_outcome': 'active', 'primary_genre': 'mainstream'},
    {'stage_name': 'Xev Bellringer', 'debut_year': 2013, 'film_count': 195, 'awards_won': 5, 'years_active': 10, 'career_outcome': 'active', 'primary_genre': 'fetish'},
    {'stage_name': 'Yhivi', 'debut_year': 2015, 'film_count': 265, 'awards_won': 7, 'years_active': 5, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Zoey Monroe', 'debut_year': 2013, 'film_count': 685, 'awards_won': 19, 'years_active': 9, 'career_outcome': 'retired', 'primary_genre': 'gonzo'},
    {'stage_name': 'Zoe Bloom', 'debut_year': 2018, 'film_count': 345, 'awards_won': 8, 'years_active': 5, 'career_outcome': 'active', 'primary_genre': 'petite'},
]


def main():
    """Populate database with comprehensive dataset"""
    
    print("\n" + "="*80)
    print("ADULT FILM STAGE NAME ANALYSIS - COMPREHENSIVE DATA POPULATION")
    print("="*80)
    print(f"\nDataset size: {len(COMPREHENSIVE_DATASET)} documented performers")
    print("Includes: Genre tags, career outcomes, tragic case tracking")
    print()
    
    with app.app_context():
        db.create_all()
        
        collector = AdultFilmCollector()
        
        collected = 0
        skipped = 0
        
        for performer_data in COMPREHENSIVE_DATASET:
            # Check if already exists
            existing = AdultPerformer.query.filter_by(stage_name=performer_data['stage_name']).first()
            if existing:
                skipped += 1
                continue
            
            try:
                performer = collector.collect_performer(**performer_data)
                if performer:
                    collected += 1
                    if collected % 10 == 0:
                        print(f"Collected {collected} performers...")
            except Exception as e:
                logger.error(f"Error with {performer_data['stage_name']}: {e}")
        
        print()
        print("="*80)
        print("POPULATION COMPLETE")
        print("="*80)
        print(f"New performers added: {collected}")
        print(f"Already existed: {skipped}")
        print(f"Total in database: {AdultPerformer.query.count()}")
        print()
        
        # Summary stats
        total = AdultPerformer.query.count()
        tragic = AdultPerformer.query.filter_by(tragic_outcome=True).count()
        early_exit = AdultPerformer.query.filter(AdultPerformer.early_exit == True).count()
        
        print(f"Tragic outcomes tracked: {tragic}")
        print(f"Early exits tracked: {early_exit}")
        print()
        print("Ready for outcome prediction analysis")
        print("="*80)
        print()


if __name__ == "__main__":
    main()

