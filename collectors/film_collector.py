"""
Film Data Collector
Collects top-grossing films for title analysis
"""

import requests
import time
import logging

logger = logging.getLogger(__name__)


class FilmCollector:
    """Collect film data from TMDB"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "8265bd1679663a7ea12ac168da84d2e8"  # Free public key
        self.base_url = "https://api.themoviedb.org/3"
    
    def collect_top_films(self, limit=500):
        """Collect top-grossing films"""
        logger.info(f"Collecting top {limit} films from TMDB...")
        
        films = []
        page = 1
        
        while len(films) < limit:
            try:
                url = f"{self.base_url}/discover/movie"
                params = {
                    'api_key': self.api_key,
                    'sort_by': 'revenue.desc',
                    'page': page
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                
                for movie in data.get('results', []):
                    if len(films) >= limit:
                        break
                    
                    # Get details
                    movie_id = movie['id']
                    details = self._get_movie_details(movie_id)
                    
                    if details and details.get('revenue', 0) > 0:
                        films.append(details)
                    
                    time.sleep(0.05)  # Rate limiting
                
                page += 1
                time.sleep(0.25)
                
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                break
        
        logger.info(f"Collected {len(films)} films")
        return films
    
    def _get_movie_details(self, movie_id):
        """Get detailed movie information"""
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {'api_key': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                revenue = data.get('revenue', 0)
                budget = data.get('budget', 0)
                roi = ((revenue - budget) / budget * 100) if budget > 0 else 0
                
                return {
                    'title': data.get('title'),
                    'original_title': data.get('original_title'),
                    'year': int(data.get('release_date', '2000')[:4]) if data.get('release_date') else 2000,
                    'revenue': revenue,
                    'budget': budget,
                    'roi': roi,
                    'rating': data.get('vote_average', 0),
                    'votes': data.get('vote_count', 0),
                    'genres': [g['name'] for g in data.get('genres', [])],
                    'runtime': data.get('runtime', 0)
                }
        except:
            return None
    
    def get_bootstrap_data(self):
        """Get well-known film data without API (for instant bootstrap)"""
        # Top-grossing films (real data from Box Office Mojo)
        known_films = [
            {'title': 'Avatar', 'year': 2009, 'revenue': 2923706026, 'budget': 237000000},
            {'title': 'Avengers: Endgame', 'year': 2019, 'revenue': 2799439100, 'budget': 356000000},
            {'title': 'Avatar: The Way of Water', 'year': 2022, 'revenue': 2320250281, 'budget': 350000000},
            {'title': 'Titanic', 'year': 1997, 'revenue': 2257844554, 'budget': 200000000},
            {'title': 'Star Wars: The Force Awakens', 'year': 2015, 'revenue': 2068223624, 'budget': 245000000},
            {'title': 'Avengers: Infinity War', 'year': 2018, 'revenue': 2048359754, 'budget': 321000000},
            {'title': 'Spider-Man: No Way Home', 'year': 2021, 'revenue': 1921847111, 'budget': 200000000},
            {'title': 'Jurassic World', 'year': 2015, 'revenue': 1671537444, 'budget': 150000000},
            {'title': 'The Lion King', 'year': 2019, 'revenue': 1663075401, 'budget': 260000000},
            {'title': 'The Avengers', 'year': 2012, 'revenue': 1518815515, 'budget': 220000000},
            {'title': 'Furious 7', 'year': 2015, 'revenue': 1515341399, 'budget': 190000000},
            {'title': 'Frozen II', 'year': 2019, 'revenue': 1453683476, 'budget': 150000000},
            {'title': 'Avengers: Age of Ultron', 'year': 2015, 'revenue': 1405403694, 'budget': 365000000},
            {'title': 'Black Panther', 'year': 2018, 'revenue': 1347597973, 'budget': 200000000},
            {'title': 'Harry Potter and the Deathly Hallows: Part 2', 'year': 2011, 'revenue': 1342025430, 'budget': 125000000},
            {'title': 'Star Wars: The Last Jedi', 'year': 2017, 'revenue': 1332698830, 'budget': 200000000},
            {'title': 'Jurassic World: Fallen Kingdom', 'year': 2018, 'revenue': 1310466296, 'budget': 170000000},
            {'title': 'Frozen', 'year': 2013, 'revenue': 1290000000, 'budget': 150000000},
            {'title': 'Beauty and the Beast', 'year': 2017, 'revenue': 1273545945, 'budget': 160000000},
            {'title': 'Incredibles 2', 'year': 2018, 'revenue': 1243089244, 'budget': 200000000},
            
            # One-word titles
            {'title': 'Joker', 'year': 2019, 'revenue': 1074251311, 'budget': 55000000},
            {'title': 'Aladdin', 'year': 2019, 'revenue': 1050693953, 'budget': 183000000},
            {'title': 'Bohemian Rhapsody', 'year': 2018, 'revenue': 911809762, 'budget': 52000000},
            {'title': 'Aquaman', 'year': 2018, 'revenue': 1148485886, 'budget': 160000000},
            {'title': 'Venom', 'year': 2018, 'revenue': 856085151, 'budget': 100000000},
            {'title': 'Skyfall', 'year': 2012, 'revenue': 1108561013, 'budget': 200000000},
            {'title': 'Spectre', 'year': 2015, 'revenue': 880674609, 'budget': 245000000},
            {'title': 'Coco', 'year': 2017, 'revenue': 814043976, 'budget': 175000000},
            {'title': 'Zootopia', 'year': 2016, 'revenue': 1024505882, 'budget': 150000000},
            {'title': 'Sing', 'year': 2016, 'revenue': 634151679, 'budget': 75000000},
            
            # Franchise names
            {'title': 'Iron Man 3', 'year': 2013, 'revenue': 1214811252, 'budget': 200000000},
            {'title': 'Captain America: Civil War', 'year': 2016, 'revenue': 1153337496, 'budget': 250000000},
            {'title': 'Spider-Man: Far From Home', 'year': 2019, 'revenue': 1131927996, 'budget': 160000000},
            {'title': 'Thor: Ragnarok', 'year': 2017, 'revenue': 855301806, 'budget': 180000000},
            {'title': 'Black Widow', 'year': 2021, 'revenue': 379751655, 'budget': 200000000},
            {'title': 'Doctor Strange', 'year': 2016, 'revenue': 677796076, 'budget': 165000000},
            {'title': 'Guardians of the Galaxy', 'year': 2014, 'revenue': 772789935, 'budget': 170000000},
            {'title': 'Ant-Man', 'year': 2015, 'revenue': 519311965, 'budget': 130000000},
            
            # Memorable short titles
            {'title': 'Up', 'year': 2009, 'revenue': 735099082, 'budget': 175000000},
            {'title': 'Her', 'year': 2013, 'revenue': 48274445, 'budget': 23000000},
            {'title': 'It', 'year': 2017, 'revenue': 701796228, 'budget': 35000000},
            {'title': 'Us', 'year': 2019, 'revenue': 255041895, 'budget': 20000000},
            {'title': 'Get Out', 'year': 2017, 'revenue': 255407969, 'budget': 4500000},
            {'title': 'Jaws', 'year': 1975, 'revenue': 476000000, 'budget': 9000000},
            {'title': 'Alien', 'year': 1979, 'revenue': 184000000, 'budget': 11000000},
            {'title': 'Rocky', 'year': 1976, 'revenue': 225000000, 'budget': 1000000}
        ]
        
        # Calculate ROI
        for film in known_films:
            rev = film['revenue']
            bud = film['budget']
            film['roi'] = ((rev - bud) / bud * 100) if bud > 0 else 0
            film['rating'] = 8.0  # Estimate
            film['votes'] = 10000  # Estimate
            film['genres'] = ['Action']  # Simplified
            film['runtime'] = 120  # Estimate
        
        return known_films

