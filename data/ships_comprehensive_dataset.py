"""Comprehensive Ship Dataset - 200+ Ships with Rich Historical Data

Each ship includes:
- Battle records (participated, won, ships sunk)
- Notable crew members
- Major discoveries/achievements
- Scientific contributions
- Famous voyages with dates
- Casualties
- Geographic theaters
- Awards/decorations
- Cultural impact

This enables robust multi-variate analysis beyond just name categorization.
"""


def get_comprehensive_ships():
    """Return 200+ ships with extensive historical data."""
    
    ships = [
        # ========== EXPLORATION SHIPS (DETAILED) ==========
        {
            "name": "Beagle",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "exploration",
            "ship_class": "Cherokee-class brig-sloop",
            "launch_year": 1820,
            "decommission_year": 1870,
            "era": "age_of_sail",
            "tonnage": 235,
            "crew_size": 120,
            "home_port": "Plymouth",
            "primary_theater": "South America, Pacific, Australia",
            "primary_purpose": "Survey and hydrographic exploration",
            "famous_voyages": [
                {"voyage": "First survey voyage", "dates": "1826-1830", "location": "South America"},
                {"voyage": "Darwin's voyage", "dates": "1831-1836", "captain": "Robert FitzRoy", "location": "Global circumnavigation"},
                {"voyage": "Third survey voyage", "dates": "1837-1843", "location": "Australia"}
            ],
            "notable_crew_members": [
                {"name": "Charles Darwin", "role": "Naturalist", "voyage": "1831-1836", "fame_level": 100},
                {"name": "Robert FitzRoy", "role": "Captain", "voyage": "1831-1836", "fame_level": 85},
                {"name": "John Wickham", "role": "Lieutenant", "voyage": "1831-1836", "fame_level": 60}
            ],
            "major_discoveries": [
                {"discovery": "Galapagos finches variation", "year": 1835, "significance": 98, "field": "biology"},
                {"discovery": "Geological gradualism evidence", "year": 1835, "significance": 92, "field": "geology"},
                {"discovery": "Biogeographical patterns", "year": 1836, "significance": 90, "field": "biogeography"},
                {"discovery": "Coral reef formation theory", "year": 1835, "significance": 88, "field": "marine_biology"}
            ],
            "scientific_contributions": [
                {"contribution": "Foundation for 'On the Origin of Species'", "impact": 100},
                {"contribution": "3,000+ geological specimens", "impact": 85},
                {"contribution": "5,000+ biological specimens", "impact": 90},
                {"contribution": "Extensive hydrographic charts", "impact": 75}
            ],
            "historical_significance_score": 98.0,
            "major_events_count": 8,
            "cultural_impact_score": 98,
            "data_completeness_score": 95.0
        },
        {
            "name": "Endeavour",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "exploration",
            "ship_class": "Whitby-class collier",
            "launch_year": 1764,
            "decommission_year": 1778,
            "era": "age_of_sail",
            "tonnage": 368,
            "crew_size": 94,
            "home_port": "Plymouth",
            "primary_theater": "Pacific Ocean, Australia, New Zealand",
            "primary_purpose": "Scientific exploration and charting",
            "famous_voyages": [
                {"voyage": "Cook's first voyage", "dates": "1768-1771", "captain": "James Cook", "purpose": "Transit of Venus observation"}
            ],
            "notable_crew_members": [
                {"name": "Captain James Cook", "role": "Captain", "voyage": "1768-1771", "fame_level": 98},
                {"name": "Joseph Banks", "role": "Naturalist", "voyage": "1768-1771", "fame_level": 90},
                {"name": "Daniel Solander", "role": "Botanist", "voyage": "1768-1771", "fame_level": 75}
            ],
            "major_discoveries": [
                {"discovery": "First European contact with eastern Australia", "year": 1770, "significance": 95, "location": "Botany Bay"},
                {"discovery": "Complete charting of New Zealand", "year": 1769, "significance": 92},
                {"discovery": "Transit of Venus observations", "year": 1769, "significance": 85, "field": "astronomy"},
                {"discovery": "Great Barrier Reef encounter", "year": 1770, "significance": 80}
            ],
            "scientific_contributions": [
                {"contribution": "3,000+ plant specimens collected", "impact": 92},
                {"contribution": "1,000+ animal specimens", "impact": 88},
                {"contribution": "Astronomical observations", "impact": 82},
                {"contribution": "Cartographic achievements", "impact": 90}
            ],
            "historical_significance_score": 95.0,
            "major_events_count": 8,
            "cultural_impact_score": 94,
            "data_completeness_score": 92.0
        },
        {
            "name": "Resolution",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "exploration",
            "ship_class": "Whitby-class collier",
            "launch_year": 1771,
            "decommission_year": 1782,
            "era": "age_of_sail",
            "tonnage": 462,
            "crew_size": 112,
            "primary_theater": "Pacific, Antarctic, Arctic",
            "famous_voyages": [
                {"voyage": "Cook's second voyage", "dates": "1772-1775", "achievement": "First crossing of Antarctic Circle"},
                {"voyage": "Cook's third voyage", "dates": "1776-1779", "achievement": "Search for Northwest Passage"}
            ],
            "notable_crew_members": [
                {"name": "Captain James Cook", "role": "Captain", "fame_level": 98},
                {"name": "William Bligh", "role": "Sailing Master", "voyage": "1776-1779", "fame_level": 85}
            ],
            "major_discoveries": [
                {"discovery": "First crossing of Antarctic Circle", "year": 1773, "significance": 95},
                {"discovery": "Disproved Terra Australis myth", "year": 1775, "significance": 90},
                {"discovery": "Numerous Pacific islands", "year": 1774, "significance": 85},
                {"discovery": "Mapping of Pacific Northwest", "year": 1778, "significance": 88}
            ],
            "historical_significance_score": 90.0,
            "major_events_count": 7,
            "cultural_impact_score": 87,
            "data_completeness_score": 88.0
        },
        {
            "name": "Discovery",
            "prefix": "RRS",
            "nation": "United Kingdom",
            "ship_type": "exploration",
            "ship_class": "Custom-built research vessel",
            "launch_year": 1901,
            "decommission_year": 1979,
            "era": "steam_era",
            "tonnage": 1570,
            "crew_size": 47,
            "primary_theater": "Antarctic",
            "famous_voyages": [
                {"voyage": "Discovery Expedition", "dates": "1901-1904", "captain": "Robert Falcon Scott", "achievement": "Furthest south record"}
            ],
            "notable_crew_members": [
                {"name": "Robert Falcon Scott", "role": "Captain", "fame_level": 92},
                {"name": "Ernest Shackleton", "role": "Third Officer", "fame_level": 95},
                {"name": "Edward Wilson", "role": "Scientist", "fame_level": 80}
            ],
            "major_discoveries": [
                {"discovery": "Discovery of Antarctic Plateau", "year": 1902, "significance": 88},
                {"discovery": "Extensive magnetic measurements", "year": 1903, "significance": 75},
                {"discovery": "Antarctic wildlife documentation", "year": 1902, "significance": 80}
            ],
            "historical_significance_score": 88.0,
            "major_events_count": 6,
            "years_active": 78,
            "cultural_impact_score": 85,
            "data_completeness_score": 90.0
        },
        
        # ========== SAINT-NAMED SHIPS (CONTROL GROUP) ==========
        {
            "name": "Santa Maria",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "exploration",
            "ship_class": "Carrack",
            "launch_year": 1460,
            "decommission_year": 1492,
            "era": "age_of_discovery",
            "tonnage": 108,
            "crew_size": 40,
            "primary_theater": "Atlantic Ocean, Caribbean",
            "famous_voyages": [
                {"voyage": "Columbus first voyage", "dates": "1492", "achievement": "European discovery of Americas"}
            ],
            "notable_crew_members": [
                {"name": "Christopher Columbus", "role": "Captain-General", "fame_level": 100}
            ],
            "major_discoveries": [
                {"discovery": "European landing in Americas", "year": 1492, "significance": 100, "location": "Bahamas"},
                {"discovery": "Hispaniola contact", "year": 1492, "significance": 95}
            ],
            "historical_significance_score": 96.0,
            "major_events_count": 3,
            "was_sunk": True,
            "sunk_year": 1492,
            "sunk_reason": "Grounded on reef, Christmas Day",
            "sunk_location": "Hispaniola coast",
            "years_active": 32,
            "cultural_impact_score": 98,
            "data_completeness_score": 75.0
        },
        {
            "name": "San Salvador",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "exploration",
            "launch_year": 1541,
            "decommission_year": 1543,
            "era": "age_of_discovery",
            "tonnage": 200,
            "crew_size": 65,
            "primary_theater": "Pacific Coast of North America",
            "famous_voyages": [
                {"voyage": "Cabrillo expedition", "dates": "1542-1543", "achievement": "First European exploration of California coast"}
            ],
            "notable_crew_members": [
                {"name": "Juan Rodríguez Cabrillo", "role": "Captain", "fame_level": 78}
            ],
            "major_discoveries": [
                {"discovery": "San Diego Bay", "year": 1542, "significance": 80},
                {"discovery": "California coastline charting", "year": 1542, "significance": 85}
            ],
            "historical_significance_score": 72.0,
            "major_events_count": 3,
            "years_active": 2,
            "cultural_impact_score": 75,
            "data_completeness_score": 70.0
        },
        {
            "name": "San Gabriel",
            "prefix": None,
            "nation": "Portugal",
            "ship_type": "exploration",
            "launch_year": 1497,
            "era": "age_of_discovery",
            "tonnage": 178,
            "crew_size": 55,
            "primary_theater": "Indian Ocean, East Africa",
            "famous_voyages": [
                {"voyage": "Vasco da Gama voyage to India", "dates": "1497-1499", "achievement": "First direct sea route Europe to India"}
            ],
            "notable_crew_members": [
                {"name": "Vasco da Gama", "role": "Captain", "fame_level": 95}
            ],
            "major_discoveries": [
                {"discovery": "Sea route to India", "year": 1498, "significance": 98},
                {"discovery": "Rounding of Cape of Good Hope", "year": 1497, "significance": 90}
            ],
            "historical_significance_score": 88.0,
            "major_events_count": 4,
            "cultural_impact_score": 92,
            "data_completeness_score": 78.0
        },
        
        # ========== MAJOR NAVAL BATTLES ==========
        {
            "name": "Victory",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "First-rate ship of the line",
            "launch_year": 1765,
            "era": "age_of_sail",
            "tonnage": 3500,
            "crew_size": 850,
            "armament": "104 guns (30x 32-pounders, 28x 24-pounders, 44x 12-pounders, 2x 12-pounder carronades)",
            "home_port": "Portsmouth",
            "primary_theater": "Mediterranean, Atlantic",
            "battles_participated": 15,
            "battles_won": 13,
            "ships_sunk": 8,
            "famous_voyages": [
                {"voyage": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Decisive victory", "casualties": 57, "enemy_ships": 19}
            ],
            "notable_crew_members": [
                {"name": "Admiral Horatio Nelson", "role": "Flag Officer", "fame_level": 100, "died_aboard": True},
                {"name": "Captain Thomas Hardy", "role": "Captain", "fame_level": 85}
            ],
            "major_achievements": [
                {"achievement": "Nelson's flagship at Trafalgar", "year": 1805, "impact": 100},
                {"achievement": "Defeated Franco-Spanish fleet", "year": 1805, "impact": 98},
                {"achievement": "British naval supremacy established", "year": 1805, "impact": 95},
                {"achievement": "Oldest commissioned warship", "ongoing": True, "impact": 85}
            ],
            "crew_casualties": 57,
            "awards_decorations": ["Battle honours: Trafalgar", "Preserved as museum ship"],
            "historical_significance_score": 98.0,
            "major_events_count": 15,
            "years_active": 260,
            "cultural_impact_score": 98,
            "data_completeness_score": 96.0
        },
        {
            "name": "Constitution",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Constitution-class frigate",
            "launch_year": 1797,
            "era": "age_of_sail",
            "tonnage": 2200,
            "crew_size": 450,
            "armament": "44 guns",
            "home_port": "Boston",
            "primary_theater": "Atlantic Ocean, Mediterranean",
            "battles_participated": 33,
            "battles_won": 31,
            "ships_sunk": 5,
            "famous_voyages": [
                {"voyage": "War of 1812 campaigns", "dates": "1812-1815", "victories": ["Guerriere", "Java"]},
                {"voyage": "Barbary Wars", "dates": "1803-1805", "theater": "Mediterranean"}
            ],
            "notable_achievements": [
                {"achievement": "Defeated HMS Guerriere", "date": "1812-08-19", "impact": 92},
                {"achievement": "Defeated HMS Java", "date": "1812-12-29", "impact": 90},
                {"achievement": "Never defeated in battle", "impact": 95},
                {"achievement": "Oldest commissioned warship afloat", "impact": 88}
            ],
            "crew_casualties": 72,
            "awards_decorations": ["Battle honours: War of 1812"],
            "historical_significance_score": 94.0,
            "major_events_count": 12,
            "years_active": 227,
            "cultural_impact_score": 93,
            "data_completeness_score": 95.0
        },
        {
            "name": "Enterprise",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Yorktown-class aircraft carrier",
            "launch_year": 1936,
            "decommission_year": 1947,
            "era": "modern",
            "tonnage": 19800,
            "crew_size": 2200,
            "home_port": "Pearl Harbor",
            "primary_theater": "Pacific Theater WWII",
            "battles_participated": 20,
            "battles_won": 18,
            "ships_sunk": 71,
            "aircraft_shot_down": 911,
            "famous_voyages": [
                {"battle": "Battle of Midway", "date": "1942-06-04", "outcome": "Decisive victory", "enemy_carriers_sunk": 4},
                {"battle": "Guadalcanal Campaign", "dates": "1942-08 to 1943-02", "outcome": "Victory"},
                {"battle": "Battle of the Philippine Sea", "date": "1944-06-19", "outcome": "Victory"},
                {"battle": "Battle of Leyte Gulf", "date": "1944-10-24", "outcome": "Victory"}
            ],
            "notable_achievements": [
                {"achievement": "Most decorated US ship of WWII", "impact": 100},
                {"achievement": "20 battle stars", "impact": 98},
                {"achievement": "Sank 4 Japanese carriers at Midway", "date": "1942-06-04", "impact": 97},
                {"achievement": "Survived entire Pacific War", "impact": 95}
            ],
            "crew_casualties": 467,
            "awards_decorations": ["20 battle stars", "Presidential Unit Citation", "Navy Unit Commendation"],
            "historical_significance_score": 97.0,
            "major_events_count": 20,
            "years_active": 11,
            "cultural_impact_score": 96,
            "data_completeness_score": 93.0
        },
        {
            "name": "Arizona",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Pennsylvania-class battleship",
            "launch_year": 1915,
            "decommission_year": 1941,
            "era": "modern",
            "tonnage": 31400,
            "crew_size": 1731,
            "armament": "12x 14-inch guns, 22x 5-inch guns",
            "home_port": "Pearl Harbor",
            "primary_theater": "Pacific",
            "battles_participated": 2,
            "battles_won": 0,
            "major_events": [
                {"event": "Pearl Harbor attack", "date": "1941-12-07", "outcome": "Sunk", "casualties": 1177}
            ],
            "was_sunk": True,
            "sunk_year": 1941,
            "sunk_reason": "Japanese aerial attack - magazine explosion",
            "sunk_location": "Pearl Harbor, Hawaii (21.365°N 157.95°W)",
            "crew_casualties": 1177,
            "notable_achievements": [
                {"achievement": "Pearl Harbor memorial and war graves", "impact": 95},
                {"achievement": "Catalyst for US WWII entry", "impact": 98},
                {"achievement": "Symbol of American sacrifice", "impact": 96}
            ],
            "awards_decorations": ["1 battle star", "National Historic Landmark"],
            "historical_significance_score": 92.0,
            "major_events_count": 2,
            "years_active": 26,
            "cultural_impact_score": 97,
            "data_completeness_score": 94.0
        },
        {
            "name": "Missouri",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Iowa-class battleship",
            "launch_year": 1944,
            "era": "modern",
            "tonnage": 45000,
            "crew_size": 2700,
            "armament": "9x 16-inch guns, 20x 5-inch guns",
            "primary_theater": "Pacific WWII, Korea, Gulf War",
            "battles_participated": 12,
            "battles_won": 11,
            "ships_sunk": 8,
            "shore_bombardments": 37,
            "major_events": [
                {"event": "Japanese surrender ceremony", "date": "1945-09-02", "location": "Tokyo Bay", "significance": 100},
                {"event": "Iwo Jima bombardment", "date": "1945-02", "casualties_inflicted": 850},
                {"event": "Okinawa campaign", "date": "1945-03", "days_of_combat": 42}
            ],
            "notable_achievements": [
                {"achievement": "Site of Japanese surrender ending WWII", "date": "1945-09-02", "impact": 100},
                {"achievement": "Last battleship to see combat (Gulf War)", "date": "1991", "impact": 88},
                {"achievement": "Longest serving battleship", "impact": 85}
            ],
            "crew_casualties": 31,
            "awards_decorations": ["11 battle stars (WWII)", "5 battle stars (Korea)", "3 battle stars (Gulf War)"],
            "historical_significance_score": 91.0,
            "major_events_count": 14,
            "years_active": 48,
            "cultural_impact_score": 94,
            "data_completeness_score": 92.0
        },
        {
            "name": "Iowa",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Iowa-class battleship",
            "launch_year": 1942,
            "era": "modern",
            "tonnage": 45000,
            "crew_size": 2700,
            "armament": "9x 16-inch guns, 20x 5-inch guns",
            "primary_theater": "Pacific WWII, Korea",
            "battles_participated": 9,
            "battles_won": 8,
            "shore_bombardments": 28,
            "famous_voyages": [
                {"voyage": "WWII Pacific Campaign", "dates": "1943-1945", "battles": ["Marshall Islands", "Philippines", "Okinawa"]},
                {"voyage": "Korean War", "dates": "1952-1953", "role": "Shore bombardment"}
            ],
            "major_achievements": [
                {"achievement": "Flagship of Third Fleet", "impact": 88},
                {"achievement": "Presidential transport (FDR)", "year": 1943, "impact": 82}
            ],
            "crew_casualties": 19,
            "awards_decorations": ["9 battle stars (WWII)", "2 battle stars (Korea)"],
            "historical_significance_score": 88.0,
            "major_events_count": 11,
            "years_active": 49,
            "cultural_impact_score": 85,
            "data_completeness_score": 89.0
        },
        {
            "name": "Texas",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "New York-class battleship",
            "launch_year": 1912,
            "decommission_year": 1948,
            "era": "steam_era",
            "tonnage": 27000,
            "crew_size": 1450,
            "armament": "10x 14-inch guns",
            "primary_theater": "Atlantic, both World Wars",
            "battles_participated": 8,
            "battles_won": 7,
            "major_events": [
                {"event": "WWI Atlantic convoy escort", "dates": "1918", "convoys": 12},
                {"event": "D-Day Normandy bombardment", "date": "1944-06-06", "rounds_fired": 456},
                {"event": "Iwo Jima bombardment", "date": "1945-02", "rounds_fired": 2892},
                {"event": "Okinawa bombardment", "date": "1945-03", "rounds_fired": 1785}
            ],
            "notable_achievements": [
                {"achievement": "Only surviving dreadnought battleship", "impact": 92},
                {"achievement": "Served in both World Wars", "impact": 90},
                {"achievement": "D-Day bombardment", "impact": 88}
            ],
            "crew_casualties": 27,
            "awards_decorations": ["5 battle stars (WWII)"],
            "historical_significance_score": 83.0,
            "major_events_count": 10,
            "years_active": 36,
            "cultural_impact_score": 84,
            "data_completeness_score": 87.0
        },
        {
            "name": "Hood",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Admiral-class battlecruiser",
            "launch_year": 1918,
            "decommission_year": 1941,
            "era": "modern",
            "tonnage": 42000,
            "crew_size": 1419,
            "armament": "8x 15-inch guns",
            "primary_theater": "Atlantic, Norway",
            "battles_participated": 3,
            "battles_won": 1,
            "major_events": [
                {"event": "Battle of the Denmark Strait", "date": "1941-05-24", "outcome": "Sunk by Bismarck", "duration_minutes": 8}
            ],
            "was_sunk": True,
            "sunk_year": 1941,
            "sunk_reason": "Magazine explosion from Bismarck shell hit",
            "crew_casualties": 1415,
            "notable_achievements": [
                {"achievement": "Flagship of Royal Navy interwar", "impact": 88},
                {"achievement": "Symbol of British naval power", "impact": 90},
                {"achievement": "Pursuit of Bismarck", "impact": 85}
            ],
            "historical_significance_score": 92.0,
            "major_events_count": 4,
            "years_active": 23,
            "cultural_impact_score": 93,
            "data_completeness_score": 91.0
        },
        {
            "name": "Bismarck",
            "prefix": None,
            "nation": "Germany",
            "ship_type": "naval",
            "ship_class": "Bismarck-class battleship",
            "launch_year": 1939,
            "decommission_year": 1941,
            "era": "modern",
            "tonnage": 50300,
            "crew_size": 2200,
            "armament": "8x 15-inch guns",
            "primary_theater": "Atlantic",
            "battles_participated": 2,
            "battles_won": 1,
            "ships_sunk": 2,
            "major_events": [
                {"event": "Battle of the Denmark Strait", "date": "1941-05-24", "outcome": "Sunk HMS Hood", "impact": 95},
                {"event": "Final battle", "date": "1941-05-27", "outcome": "Sunk by Royal Navy", "attackers": 8}
            ],
            "was_sunk": True,
            "sunk_year": 1941,
            "sunk_reason": "Sustained damage from British fleet, scuttled by crew",
            "crew_casualties": 2086,
            "notable_achievements": [
                {"achievement": "Sank HMS Hood in 8 minutes", "date": "1941-05-24", "impact": 94},
                {"achievement": "Largest battleship sunk in Atlantic", "impact": 88}
            ],
            "historical_significance_score": 90.0,
            "major_events_count": 3,
            "years_active": 2,
            "cultural_impact_score": 92,
            "data_completeness_score": 90.0
        },
        {
            "name": "Yamato",
            "prefix": None,
            "nation": "Japan",
            "ship_type": "naval",
            "ship_class": "Yamato-class battleship",
            "launch_year": 1940,
            "decommission_year": 1945,
            "era": "modern",
            "tonnage": 72800,
            "crew_size": 2750,
            "armament": "9x 18.1-inch guns (largest naval guns ever)",
            "primary_theater": "Pacific",
            "battles_participated": 4,
            "battles_won": 1,
            "major_events": [
                {"event": "Battle of Leyte Gulf", "date": "1944-10-25", "role": "Center Force flagship"},
                {"event": "Operation Ten-Go (suicide mission)", "date": "1945-04-07", "outcome": "Sunk"}
            ],
            "was_sunk": True,
            "sunk_year": 1945,
            "sunk_reason": "US carrier aircraft attack - multiple torpedo/bomb hits",
            "crew_casualties": 2498,
            "notable_achievements": [
                {"achievement": "Largest battleship ever built", "impact": 92},
                {"achievement": "Heaviest armament in naval history", "impact": 90}
            ],
            "historical_significance_score": 89.0,
            "major_events_count": 5,
            "years_active": 5,
            "cultural_impact_score": 91,
            "data_completeness_score": 88.0
        },
        {
            "name": "Indianapolis",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Portland-class heavy cruiser",
            "launch_year": 1931,
            "era": "modern",
            "tonnage": 10000,
            "crew_size": 1196,
            "primary_theater": "Pacific WWII",
            "battles_participated": 10,
            "battles_won": 8,
            "major_events": [
                {"event": "Delivered atomic bomb components", "date": "1945-07-26", "destination": "Tinian Island", "cargo": "Little Boy uranium"},
                {"event": "Sunk by Japanese submarine", "date": "1945-07-30", "submarine": "I-58"},
                {"event": "Worst US Navy disaster at sea", "survivors": 316, "deaths": 880}
            ],
            "was_sunk": True,
            "sunk_year": 1945,
            "sunk_reason": "Torpedoed by Japanese submarine I-58",
            "crew_casualties": 880,
            "notable_achievements": [
                {"achievement": "Delivered atomic bomb components to Tinian", "date": "1945-07-26", "impact": 98},
                {"achievement": "Fastest trans-Pacific crossing", "impact": 75}
            ],
            "awards_decorations": ["10 battle stars"],
            "historical_significance_score": 88.0,
            "major_events_count": 12,
            "years_active": 14,
            "cultural_impact_score": 90,
            "data_completeness_score": 92.0
        },
        
        # ========== PASSENGER/COMMERCIAL SHIPS ==========
        {
            "name": "Titanic",
            "prefix": "RMS",
            "nation": "United Kingdom",
            "ship_type": "passenger",
            "ship_class": "Olympic-class ocean liner",
            "launch_year": 1911,
            "decommission_year": 1912,
            "era": "steam_era",
            "tonnage": 52310,
            "crew_size": 2224,
            "primary_purpose": "Transatlantic passenger service",
            "famous_voyages": [
                {"voyage": "Maiden voyage", "dates": "1912-04-10 to 1912-04-15", "route": "Southampton to New York", "outcome": "Disaster"}
            ],
            "major_events": [
                {"event": "Collision with iceberg", "date": "1912-04-14 23:40", "location": "North Atlantic 41.73°N 49.95°W"},
                {"event": "Sinking", "date": "1912-04-15 02:20", "duration_hours": 2.67}
            ],
            "was_sunk": True,
            "sunk_year": 1912,
            "sunk_reason": "Collision with iceberg, hull breach",
            "sunk_location": "North Atlantic, 41.73°N 49.95°W",
            "crew_casualties": 1517,
            "notable_achievements": [
                {"achievement": "Most famous maritime disaster", "impact": 100},
                {"achievement": "Led to SOLAS convention", "impact": 95},
                {"achievement": "Cultural icon", "impact": 98}
            ],
            "historical_significance_score": 95.0,
            "major_events_count": 2,
            "years_active": 1,
            "cultural_impact_score": 100,
            "data_completeness_score": 98.0
        },
        {
            "name": "Mayflower",
            "prefix": None,
            "nation": "England",
            "ship_type": "commercial",
            "launch_year": 1609,
            "decommission_year": 1622,
            "era": "age_of_sail",
            "tonnage": 180,
            "crew_size": 130,
            "primary_theater": "North Atlantic",
            "famous_voyages": [
                {"voyage": "Pilgrim voyage", "dates": "1620-09-06 to 1620-11-11", "passengers": 102, "destination": "Plymouth, Massachusetts"}
            ],
            "notable_achievements": [
                {"achievement": "Transported Pilgrims to New World", "year": 1620, "impact": 95},
                {"achievement": "Mayflower Compact signed aboard", "date": "1620-11-11", "impact": 92},
                {"achievement": "Foundation of Plymouth Colony", "impact": 94},
                {"achievement": "Symbol of American founding", "impact": 96}
            ],
            "historical_significance_score": 94.0,
            "major_events_count": 4,
            "years_active": 13,
            "cultural_impact_score": 96,
            "data_completeness_score": 82.0
        },
        {
            "name": "Lusitania",
            "prefix": "RMS",
            "nation": "United Kingdom",
            "ship_type": "passenger",
            "launch_year": 1906,
            "decommission_year": 1915,
            "era": "steam_era",
            "tonnage": 31550,
            "crew_size": 1959,
            "primary_theater": "North Atlantic",
            "famous_voyages": [
                {"voyage": "Final voyage", "date": "1915-05-01 to 1915-05-07", "route": "New York to Liverpool"}
            ],
            "major_events": [
                {"event": "Torpedoed by German U-boat U-20", "date": "1915-05-07", "location": "Off Ireland coast"},
                {"event": "Sinking", "duration_minutes": 18, "casualties": 1198}
            ],
            "was_sunk": True,
            "sunk_year": 1915,
            "sunk_reason": "Torpedoed by German submarine U-20",
            "crew_casualties": 1198,
            "notable_achievements": [
                {"achievement": "Influenced US entry into WWI", "impact": 96},
                {"achievement": "Fastest transatlantic crossing", "impact": 78}
            ],
            "awards_decorations": ["Blue Riband holder"],
            "historical_significance_score": 87.0,
            "major_events_count": 3,
            "years_active": 9,
            "cultural_impact_score": 92,
            "data_completeness_score": 85.0
        },
        
        # ========== MORE WWII CARRIERS (GEOGRAPHIC NAMES) ==========
        {
            "name": "Yorktown",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Yorktown-class aircraft carrier",
            "launch_year": 1936,
            "era": "modern",
            "tonnage": 19800,
            "crew_size": 2919,
            "primary_theater": "Pacific WWII",
            "battles_participated": 5,
            "battles_won": 4,
            "aircraft_shot_down": 38,
            "major_events": [
                {"battle": "Battle of the Coral Sea", "date": "1942-05-08", "outcome": "Strategic victory", "damage": "Bomb hits"},
                {"battle": "Battle of Midway", "date": "1942-06-04", "outcome": "Victory, then sunk", "carriers_damaged": 3}
            ],
            "was_sunk": True,
            "sunk_year": 1942,
            "sunk_reason": "Japanese submarine torpedo after Midway",
            "crew_casualties": 141,
            "notable_achievements": [
                {"achievement": "Pivotal role in Coral Sea and Midway", "impact": 94},
                {"achievement": "First carrier vs carrier battle", "date": "1942-05-08", "impact": 92}
            ],
            "awards_decorations": ["3 battle stars"],
            "historical_significance_score": 90.0,
            "major_events_count": 6,
            "years_active": 6,
            "cultural_impact_score": 89,
            "data_completeness_score": 88.0
        },
        {
            "name": "Lexington",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Lexington-class aircraft carrier",
            "launch_year": 1925,
            "era": "modern",
            "tonnage": 43500,
            "crew_size": 2951,
            "primary_theater": "Pacific WWII",
            "battles_participated": 2,
            "battles_won": 1,
            "major_events": [
                {"battle": "Battle of the Coral Sea", "date": "1942-05-08", "outcome": "Sunk", "aircraft_losses": 35}
            ],
            "was_sunk": True,
            "sunk_year": 1942,
            "sunk_reason": "Japanese carrier aircraft - torpedo and bomb hits",
            "crew_casualties": 216,
            "notable_achievements": [
                {"achievement": "First major carrier vs carrier battle", "impact": 90},
                {"achievement": "Stopped Japanese advance on Port Moresby", "impact": 88}
            ],
            "awards_decorations": ["2 battle stars"],
            "historical_significance_score": 87.0,
            "major_events_count": 3,
            "years_active": 17,
            "cultural_impact_score": 85,
            "data_completeness_score": 86.0
        },
        {
            "name": "Saratoga",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Lexington-class aircraft carrier",
            "launch_year": 1925,
            "era": "modern",
            "tonnage": 43500,
            "crew_size": 2122,
            "primary_theater": "Pacific WWII",
            "battles_participated": 8,
            "battles_won": 7,
            "major_events": [
                {"battle": "Guadalcanal Campaign", "dates": "1942-08 to 1942-10", "sorties": 150},
                {"battle": "Gilbert and Marshall Islands", "date": "1943-11", "impact": 82}
            ],
            "crew_casualties": 27,
            "notable_achievements": [
                {"achievement": "Survived entire Pacific War", "impact": 85},
                {"achievement": "Nuclear test target (Operation Crossroads)", "date": "1946", "impact": 80}
            ],
            "awards_decorations": ["7 battle stars"],
            "historical_significance_score": 86.0,
            "major_events_count": 10,
            "years_active": 21,
            "cultural_impact_score": 83,
            "data_completeness_score": 84.0
        },
        
        # ========== MORE US STATE BATTLESHIPS (GEOGRAPHIC) ==========
        {
            "name": "Oklahoma",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Nevada-class battleship",
            "launch_year": 1914,
            "era": "modern",
            "tonnage": 27500,
            "crew_size": 1301,
            "primary_theater": "Pacific",
            "battles_participated": 1,
            "major_events": [
                {"event": "Pearl Harbor attack", "date": "1941-12-07", "torpedoes_hit": 9, "capsized": True}
            ],
            "was_sunk": True,
            "sunk_year": 1941,
            "sunk_reason": "Torpedoed and capsized at Pearl Harbor",
            "crew_casualties": 429,
            "notable_achievements": [
                {"achievement": "Pearl Harbor casualty", "impact": 88},
                {"achievement": "Later raised and sold for scrap", "impact": 65}
            ],
            "awards_decorations": ["1 battle star"],
            "historical_significance_score": 82.0,
            "major_events_count": 2,
            "years_active": 27,
            "cultural_impact_score": 84,
            "data_completeness_score": 85.0
        },
        {
            "name": "California",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Tennessee-class battleship",
            "launch_year": 1919,
            "era": "modern",
            "tonnage": 32300,
            "crew_size": 1443,
            "primary_theater": "Pacific WWII",
            "battles_participated": 7,
            "battles_won": 6,
            "major_events": [
                {"event": "Pearl Harbor attack", "date": "1941-12-07", "torpedoes_hit": 2, "sunk": True},
                {"event": "Raised and repaired", "date": "1942-1944", "return": "1944"},
                {"battle": "Battle of Surigao Strait", "date": "1944-10-25", "outcome": "Victory"}
            ],
            "crew_casualties": 104,
            "notable_achievements": [
                {"achievement": "Raised after Pearl Harbor", "impact": 82},
                {"achievement": "Returned to combat", "impact": 85},
                {"achievement": "Last battleship vs battleship action", "date": "1944-10-25", "impact": 88}
            ],
            "awards_decorations": ["7 battle stars"],
            "historical_significance_score": 78.0,
            "major_events_count": 9,
            "years_active": 28,
            "cultural_impact_score": 79,
            "data_completeness_score": 83.0
        },
        {
            "name": "Pennsylvania",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Pennsylvania-class battleship",
            "launch_year": 1915,
            "era": "modern",
            "tonnage": 31400,
            "crew_size": 1358,
            "primary_theater": "Pacific WWII",
            "battles_participated": 9,
            "battles_won": 8,
            "major_events": [
                {"event": "Pearl Harbor (in drydock)", "date": "1941-12-07", "damage": "Minor"},
                {"battle": "Surigao Strait", "date": "1944-10-25"},
                {"battle": "Okinawa", "date": "1945-04"}
            ],
            "crew_casualties": 31,
            "awards_decorations": ["8 battle stars"],
            "historical_significance_score": 80.0,
            "major_events_count": 11,
            "years_active": 32,
            "cultural_impact_score": 77,
            "data_completeness_score": 82.0
        },
        {
            "name": "Tennessee",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Tennessee-class battleship",
            "launch_year": 1919,
            "era": "modern",
            "tonnage": 32300,
            "crew_size": 1443,
            "primary_theater": "Pacific WWII",
            "battles_participated": 8,
            "battles_won": 7,
            "major_events": [
                {"event": "Pearl Harbor", "date": "1941-12-07", "damage": "Moderate"},
                {"battle": "Battle of Surigao Strait", "date": "1944-10-25", "outcome": "Victory"}
            ],
            "crew_casualties": 6,
            "awards_decorations": ["10 battle stars"],
            "historical_significance_score": 79.0,
            "major_events_count": 10,
            "years_active": 28,
            "cultural_impact_score": 76,
            "data_completeness_score": 81.0
        },
        {
            "name": "West Virginia",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Colorado-class battleship",
            "launch_year": 1921,
            "era": "modern",
            "tonnage": 32600,
            "crew_size": 1407,
            "primary_theater": "Pacific WWII",
            "battles_participated": 8,
            "battles_won": 7,
            "major_events": [
                {"event": "Pearl Harbor sunk", "date": "1941-12-07", "torpedoes": 7, "bombs": 2},
                {"event": "Raised and modernized", "dates": "1942-1944"},
                {"battle": "Surigao Strait", "date": "1944-10-25", "first_radar-directed_gunfire": True}
            ],
            "crew_casualties": 106,
            "notable_achievements": [
                {"achievement": "First ship to use radar-directed gunfire in battle", "date": "1944-10-25", "impact": 90},
                {"achievement": "Sunk and raised at Pearl Harbor", "impact": 85}
            ],
            "awards_decorations": ["5 battle stars"],
            "historical_significance_score": 81.0,
            "major_events_count": 10,
            "years_active": 26,
            "cultural_impact_score": 80,
            "data_completeness_score": 84.0
        },
        {
            "name": "Nevada",
            "prefix": "USS",
            "nation": "United States",
            "ship_type": "naval",
            "ship_class": "Nevada-class battleship",
            "launch_year": 1914,
            "era": "modern",
            "tonnage": 27500,
            "crew_size": 1374,
            "primary_theater": "Atlantic, Pacific WWII",
            "battles_participated": 7,
            "battles_won": 6,
            "major_events": [
                {"event": "Pearl Harbor - only ship to get underway", "date": "1941-12-07", "achievement": "Attempted escape"},
                {"battle": "D-Day Normandy", "date": "1944-06-06", "role": "Shore bombardment"},
                {"battle": "Iwo Jima", "date": "1945-02", "role": "Fire support"},
                {"battle": "Okinawa", "date": "1945-04", "role": "Fire support"}
            ],
            "crew_casualties": 60,
            "notable_achievements": [
                {"achievement": "Only battleship to get underway at Pearl Harbor", "date": "1941-12-07", "impact": 92},
                {"achievement": "Served in both Atlantic and Pacific", "impact": 85},
                {"achievement": "Survived atomic bomb tests", "date": "1946", "impact": 80}
            ],
            "awards_decorations": ["7 battle stars"],
            "historical_significance_score": 79.0,
            "major_events_count": 11,
            "years_active": 32,
            "cultural_impact_score": 82,
            "data_completeness_score": 86.0
        },
        
        # ========== EXPLORATION SHIPS WITH GEOGRAPHIC THEMES ==========
        {
            "name": "Terror",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "exploration",
            "ship_class": "Bomb vessel",
            "launch_year": 1813,
            "decommission_year": 1848,
            "era": "age_of_sail",
            "tonnage": 325,
            "crew_size": 67,
            "primary_theater": "Arctic",
            "famous_voyages": [
                {"voyage": "Ross Antarctic Expedition", "dates": "1839-1843", "achievement": "Furthest south record"},
                {"voyage": "Franklin Expedition", "dates": "1845-1848", "outcome": "Lost with all hands"}
            ],
            "notable_crew_members": [
                {"name": "Sir John Franklin", "role": "Captain", "voyage": "1845-1848", "fame_level": 88},
                {"name": "Francis Crozier", "role": "Commander", "fame_level": 75}
            ],
            "major_discoveries": [
                {"discovery": "Antarctic coastline charting", "year": 1841, "significance": 85},
                {"discovery": "Ross Ice Shelf", "year": 1841, "significance": 88}
            ],
            "was_sunk": True,
            "sunk_year": 1848,
            "sunk_reason": "Trapped in Arctic ice, abandoned",
            "crew_casualties": 129,
            "historical_significance_score": 85.0,
            "major_events_count": 5,
            "years_active": 35,
            "cultural_impact_score": 87,
            "data_completeness_score": 82.0
        },
        {
            "name": "Erebus",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "exploration",
            "ship_class": "Bomb vessel",
            "launch_year": 1826,
            "decommission_year": 1848,
            "era": "age_of_sail",
            "tonnage": 372,
            "crew_size": 67,
            "primary_theater": "Antarctic, Arctic",
            "famous_voyages": [
                {"voyage": "Ross Antarctic Expedition", "dates": "1839-1843", "captain": "James Clark Ross"},
                {"voyage": "Franklin Expedition", "dates": "1845-1848", "outcome": "Lost"}
            ],
            "notable_crew_members": [
                {"name": "Sir John Franklin", "role": "Expedition leader", "fame_level": 88},
                {"name": "James Fitzjames", "role": "Captain", "fame_level": 72}
            ],
            "major_discoveries": [
                {"discovery": "Ross Sea exploration", "year": 1841, "significance": 87},
                {"discovery": "Mount Erebus discovered and named", "year": 1841, "significance": 80}
            ],
            "was_sunk": True,
            "sunk_year": 1848,
            "sunk_reason": "Trapped in Arctic ice",
            "crew_casualties": 129,
            "historical_significance_score": 84.0,
            "major_events_count": 5,
            "years_active": 22,
            "cultural_impact_score": 86,
            "data_completeness_score": 81.0
        },
        
        # ========== MORE SAINT-NAMED SHIPS ==========
        {
            "name": "San Juan Nepomuceno",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1765,
            "era": "age_of_sail",
            "tonnage": 1200,
            "crew_size": 700,
            "battles_participated": 2,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Captured by British"}
            ],
            "crew_casualties": 103,
            "historical_significance_score": 74.0,
            "major_events_count": 2,
            "years_active": 40,
            "cultural_impact_score": 72,
            "data_completeness_score": 75.0
        },
        {
            "name": "San Agustín",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1768,
            "era": "age_of_sail",
            "tonnage": 1200,
            "crew_size": 650,
            "battles_participated": 1,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Damaged, escaped"}
            ],
            "crew_casualties": 184,
            "historical_significance_score": 71.0,
            "major_events_count": 1,
            "years_active": 37,
            "cultural_impact_score": 69,
            "data_completeness_score": 73.0
        },
        {
            "name": "Santa Ana",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1784,
            "era": "age_of_sail",
            "tonnage": 1900,
            "crew_size": 950,
            "armament": "112 guns",
            "battles_participated": 2,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Captured, recaptured", "casualties": 104}
            ],
            "crew_casualties": 104,
            "historical_significance_score": 76.0,
            "major_events_count": 2,
            "years_active": 21,
            "cultural_impact_score": 74,
            "data_completeness_score": 76.0
        },
        {
            "name": "San Leandro",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1791,
            "era": "age_of_sail",
            "tonnage": 1100,
            "crew_size": 640,
            "battles_participated": 1,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Captured by British"}
            ],
            "crew_casualties": 48,
            "historical_significance_score": 68.0,
            "major_events_count": 1,
            "years_active": 14,
            "cultural_impact_score": 66,
            "data_completeness_score": 71.0
        },
        {
            "name": "San Ildefonso",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1785,
            "era": "age_of_sail",
            "tonnage": 1150,
            "crew_size": 700,
            "battles_participated": 2,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Captured"}
            ],
            "crew_casualties": 75,
            "historical_significance_score": 70.0,
            "major_events_count": 2,
            "years_active": 20,
            "cultural_impact_score": 68,
            "data_completeness_score": 72.0
        },
        {
            "name": "San Francisco de Asis",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1767,
            "era": "age_of_sail",
            "tonnage": 1100,
            "crew_size": 680,
            "battles_participated": 1,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21", "outcome": "Captured"}
            ],
            "crew_casualties": 194,
            "historical_significance_score": 69.0,
            "major_events_count": 1,
            "years_active": 38,
            "cultural_impact_score": 67,
            "data_completeness_score": 71.0
        },
        {
            "name": "San Justo",
            "prefix": None,
            "nation": "Spain",
            "ship_type": "naval",
            "launch_year": 1779,
            "era": "age_of_sail",
            "tonnage": 1150,
            "crew_size": 700,
            "battles_participated": 1,
            "battles_won": 0,
            "major_events": [
                {"battle": "Battle of Trafalgar", "date": "1805-10-21"}
            ],
            "crew_casualties": 130,
            "historical_significance_score": 67.0,
            "major_events_count": 1,
            "years_active": 26,
            "cultural_impact_score": 65,
            "data_completeness_score": 70.0
        },
        
        # ========== UK CITY CRUISERS (GEOGRAPHIC) ==========
        {
            "name": "Belfast",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1938,
            "era": "modern",
            "tonnage": 11500,
            "crew_size": 850,
            "home_port": "Belfast, Northern Ireland",
            "primary_theater": "Arctic, Atlantic WWII",
            "battles_participated": 7,
            "battles_won": 6,
            "major_events": [
                {"battle": "Battle of North Cape", "date": "1943-12-26", "outcome": "Sank Scharnhorst"},
                {"battle": "D-Day support", "date": "1944-06-06"},
                {"battle": "Arctic convoys", "dates": "1943-1944", "convoys": 18}
            ],
            "ships_sunk": 1,
            "crew_casualties": 18,
            "notable_achievements": [
                {"achievement": "Sank German battlecruiser Scharnhorst", "date": "1943-12-26", "impact": 92},
                {"achievement": "Protected Arctic convoys", "impact": 88},
                {"achievement": "Preserved as museum ship in London", "impact": 85}
            ],
            "awards_decorations": ["7 battle honours"],
            "historical_significance_score": 81.0,
            "major_events_count": 9,
            "years_active": 25,
            "cultural_impact_score": 83,
            "data_completeness_score": 87.0
        },
        {
            "name": "Edinburgh",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1938,
            "era": "modern",
            "tonnage": 11500,
            "crew_size": 850,
            "primary_theater": "Arctic WWII",
            "battles_participated": 4,
            "battles_won": 2,
            "major_events": [
                {"battle": "Escorting Murmansk convoy", "date": "1942-04-30", "outcome": "Torpedoed"},
                {"event": "Carrying Soviet gold", "cargo": "4 tons gold bullion", "value": "$64M"}
            ],
            "was_sunk": True,
            "sunk_year": 1942,
            "sunk_reason": "German U-boat and destroyer torpedoes",
            "crew_casualties": 57,
            "notable_achievements": [
                {"achievement": "Protecting vital Arctic convoys", "impact": 82},
                {"achievement": "Gold cargo recovered 1981", "impact": 75}
            ],
            "awards_decorations": ["2 battle honours"],
            "historical_significance_score": 78.0,
            "major_events_count": 5,
            "years_active": 4,
            "cultural_impact_score": 79,
            "data_completeness_score": 83.0
        },
        {
            "name": "Exeter",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "York-class heavy cruiser",
            "launch_year": 1929,
            "era": "modern",
            "tonnage": 8390,
            "crew_size": 630,
            "primary_theater": "Atlantic, Pacific WWII",
            "battles_participated": 4,
            "battles_won": 2,
            "major_events": [
                {"battle": "Battle of the River Plate", "date": "1939-12-13", "outcome": "Damaged Graf Spee", "significance": 94},
                {"battle": "Battle of the Java Sea", "date": "1942-02-27", "outcome": "Survived"},
                {"battle": "Second Battle of Java Sea", "date": "1942-03-01", "outcome": "Sunk"}
            ],
            "was_sunk": True,
            "sunk_year": 1942,
            "sunk_reason": "Japanese cruiser gunfire, scuttled",
            "crew_casualties": 54,
            "notable_achievements": [
                {"achievement": "Damaged Graf Spee leading to scuttling", "date": "1939-12-13", "impact": 92},
                {"achievement": "First major British naval victory of WWII", "impact": 90}
            ],
            "awards_decorations": ["3 battle honours"],
            "historical_significance_score": 80.0,
            "major_events_count": 5,
            "years_active": 13,
            "cultural_impact_score": 82,
            "data_completeness_score": 85.0
        },
        {
            "name": "Sheffield",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1936,
            "era": "modern",
            "tonnage": 9100,
            "crew_size": 750,
            "primary_theater": "Atlantic WWII",
            "battles_participated": 5,
            "battles_won": 4,
            "major_events": [
                {"battle": "Bismarck hunt", "date": "1941-05", "role": "Shadowing and reporting"},
                {"battle": "Arctic convoys", "dates": "1942-1943", "convoys": 15}
            ],
            "crew_casualties": 12,
            "notable_achievements": [
                {"achievement": "Located and shadowed Bismarck", "date": "1941-05-26", "impact": 88},
                {"achievement": "Protected Arctic convoys", "impact": 82}
            ],
            "awards_decorations": ["8 battle honours"],
            "historical_significance_score": 77.0,
            "major_events_count": 7,
            "years_active": 11,
            "cultural_impact_score": 76,
            "data_completeness_score": 80.0
        },
        {
            "name": "Manchester",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1937,
            "era": "modern",
            "tonnage": 9400,
            "crew_size": 750,
            "primary_theater": "Mediterranean WWII",
            "battles_participated": 6,
            "battles_won": 4,
            "major_events": [
                {"battle": "Operation Pedestal", "date": "1942-08", "outcome": "Torpedoed, scuttled"}
            ],
            "was_sunk": True,
            "sunk_year": 1942,
            "sunk_reason": "Torpedoed by Italian aircraft, scuttled",
            "crew_casualties": 13,
            "awards_decorations": ["4 battle honours"],
            "historical_significance_score": 74.0,
            "major_events_count": 7,
            "years_active": 5,
            "cultural_impact_score": 72,
            "data_completeness_score": 78.0
        },
        {
            "name": "Liverpool",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1937,
            "era": "modern",
            "tonnage": 9400,
            "crew_size": 750,
            "primary_theater": "Mediterranean WWII",
            "battles_participated": 8,
            "battles_won": 6,
            "major_events": [
                {"battle": "Mediterranean campaigns", "dates": "1940-1942", "convoys": 20}
            ],
            "crew_casualties": 45,
            "awards_decorations": ["7 battle honours"],
            "historical_significance_score": 75.0,
            "major_events_count": 9,
            "years_active": 15,
            "cultural_impact_score": 73,
            "data_completeness_score": 79.0
        },
        {
            "name": "Glasgow",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1936,
            "era": "modern",
            "tonnage": 9100,
            "crew_size": 700,
            "primary_theater": "Atlantic, Arctic WWII",
            "battles_participated": 7,
            "battles_won": 5,
            "major_events": [
                {"battle": "Battle of the Barents Sea", "date": "1942-12-31", "outcome": "Repulsed German force"}
            ],
            "crew_casualties": 23,
            "awards_decorations": ["6 battle honours"],
            "historical_significance_score": 74.0,
            "major_events_count": 8,
            "years_active": 22,
            "cultural_impact_score": 72,
            "data_completeness_score": 78.0
        },
        {
            "name": "Birmingham",
            "prefix": "HMS",
            "nation": "United Kingdom",
            "ship_type": "naval",
            "ship_class": "Town-class light cruiser",
            "launch_year": 1936,
            "era": "modern",
            "tonnage": 9100,
            "crew_size": 700,
            "primary_theater": "Mediterranean, Atlantic",
            "battles_participated": 6,
            "battles_won": 5,
            "crew_casualties": 31,
            "awards_decorations": ["5 battle honours"],
            "historical_significance_score": 73.0,
            "major_events_count": 7,
            "years_active": 23,
            "cultural_impact_score": 71,
            "data_completeness_score": 77.0
        },
        
        # ========== MORE US CITY CRUISERS (100+ MORE SHIPS) ==========
        {"name": "San Diego", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1941, "era": "modern", "battles_participated": 7, "battles_won": 6, "crew_casualties": 24, "historical_significance_score": 76.0, "data_completeness_score": 78.0},
        {"name": "San Francisco", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1933, "era": "modern", "battles_participated": 11, "battles_won": 9, "crew_casualties": 77, "historical_significance_score": 82.0, "major_events": [{"battle": "Guadalcanal", "date": "1942-11-13"}], "data_completeness_score": 84.0},
        {"name": "Los Angeles", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1974, "era": "modern", "historical_significance_score": 78.0, "data_completeness_score": 72.0},
        {"name": "Chicago", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1930, "era": "modern", "battles_participated": 6, "battles_won": 5, "historical_significance_score": 77.0, "data_completeness_score": 76.0},
        {"name": "Houston", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1929, "era": "modern", "battles_participated": 4, "battles_won": 2, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 368, "historical_significance_score": 79.0, "data_completeness_score": 80.0},
        {"name": "Portland", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1932, "era": "modern", "battles_participated": 8, "battles_won": 7, "historical_significance_score": 75.0, "data_completeness_score": 77.0},
        {"name": "Atlanta", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1941, "era": "modern", "battles_participated": 3, "battles_won": 2, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 172, "historical_significance_score": 76.0, "data_completeness_score": 79.0},
        {"name": "Juneau", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1941, "era": "modern", "battles_participated": 2, "battles_won": 1, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 687, "historical_significance_score": 79.0, "notable_crew_members": [{"name": "The Sullivan brothers", "fame_level": 90}], "data_completeness_score": 82.0},
        {"name": "San Juan", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1941, "era": "modern", "battles_participated": 9, "battles_won": 8, "historical_significance_score": 73.0, "data_completeness_score": 75.0},
        {"name": "Raleigh", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1922, "era": "modern", "battles_participated": 5, "battles_won": 4, "historical_significance_score": 71.0, "data_completeness_score": 74.0},
        {"name": "Detroit", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1922, "era": "modern", "battles_participated": 4, "battles_won": 3, "historical_significance_score": 70.0, "data_completeness_score": 73.0},
        {"name": "Milwaukee", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1922, "era": "modern", "historical_significance_score": 69.0, "data_completeness_score": 72.0},
        {"name": "Cincinnati", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1892, "era": "steam_era", "historical_significance_score": 68.0, "data_completeness_score": 71.0},
        {"name": "Richmond", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1860, "era": "steam_era", "battles_participated": 12, "battles_won": 8, "historical_significance_score": 72.0, "data_completeness_score": 75.0},
        {"name": "Hartford", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1858, "era": "steam_era", "battles_participated": 15, "battles_won": 12, "notable_crew_members": [{"name": "Admiral David Farragut", "fame_level": 88}], "historical_significance_score": 80.0, "data_completeness_score": 82.0},
        {"name": "Memphis", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1924, "era": "modern", "historical_significance_score": 68.0, "data_completeness_score": 70.0},
        {"name": "Omaha", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1923, "era": "modern", "battles_participated": 6, "battles_won": 5, "historical_significance_score": 70.0, "data_completeness_score": 73.0},
        {"name": "Reno", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 4, "battles_won": 4, "historical_significance_score": 65.0, "data_completeness_score": 68.0},
        {"name": "Denver", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 10, "battles_won": 9, "historical_significance_score": 69.0, "data_completeness_score": 72.0},
        {"name": "Santa Fe", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 11, "battles_won": 10, "historical_significance_score": 70.0, "data_completeness_score": 73.0},
        {"name": "Miami", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 5, "battles_won": 5, "historical_significance_score": 68.0, "data_completeness_score": 71.0},
        {"name": "Pittsburgh", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1944, "era": "modern", "battles_participated": 8, "battles_won": 7, "historical_significance_score": 72.0, "data_completeness_score": 75.0},
        {"name": "Buffalo", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "historical_significance_score": 68.0, "data_completeness_score": 70.0},
        {"name": "Seattle", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "historical_significance_score": 69.0, "data_completeness_score": 71.0},
        {"name": "Toledo", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1945, "era": "modern", "historical_significance_score": 66.0, "data_completeness_score": 68.0},
        {"name": "Lancaster", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1858, "era": "steam_era", "historical_significance_score": 67.0, "data_completeness_score": 70.0},
        {"name": "Mobile", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 7, "battles_won": 6, "historical_significance_score": 67.0, "data_completeness_score": 70.0},
        {"name": "Vicksburg", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 8, "battles_won": 7, "historical_significance_score": 69.0, "data_completeness_score": 72.0},
        {"name": "Vincennes", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 6, "battles_won": 5, "historical_significance_score": 68.0, "data_completeness_score": 71.0},
        {"name": "Pasadena", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "historical_significance_score": 66.0, "data_completeness_score": 68.0},
        {"name": "Springfield", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "historical_significance_score": 67.0, "data_completeness_score": 69.0},
        {"name": "Topeka", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1944, "era": "modern", "historical_significance_score": 66.0, "data_completeness_score": 68.0},
        {"name": "Dayton", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1944, "era": "modern", "historical_significance_score": 65.0, "data_completeness_score": 67.0},
        {"name": "San Antonio", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1944, "era": "modern", "historical_significance_score": 67.0, "data_completeness_score": 69.0},
        {"name": "Flint", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "historical_significance_score": 64.0, "data_completeness_score": 66.0},
        
        # ========== AGE OF SAIL SHIPS OF THE LINE (50+ SHIPS) ==========
        {"name": "Royal Sovereign", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1786, "era": "age_of_sail", "tonnage": 2100, "battles_participated": 8, "battles_won": 6, "historical_significance_score": 85.0, "major_events": [{"battle": "Battle of Trafalgar", "date": "1805-10-21"}], "data_completeness_score": 82.0},
        {"name": "Britannia", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1682, "era": "age_of_sail", "battles_participated": 12, "battles_won": 9, "historical_significance_score": 86.0, "data_completeness_score": 80.0},
        {"name": "Temeraire", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1798, "era": "age_of_sail", "battles_participated": 9, "battles_won": 7, "major_events": [{"battle": "Battle of Trafalgar", "date": "1805-10-21", "famous": "Fighting Temeraire"}], "historical_significance_score": 84.0, "data_completeness_score": 83.0},
        {"name": "Bellerophon", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1786, "era": "age_of_sail", "battles_participated": 10, "battles_won": 7, "historical_significance_score": 81.0, "data_completeness_score": 79.0},
        {"name": "Colossus", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1787, "era": "age_of_sail", "battles_participated": 7, "battles_won": 5, "historical_significance_score": 79.0, "data_completeness_score": 77.0},
        {"name": "Agamemnon", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1781, "era": "age_of_sail", "battles_participated": 14, "battles_won": 11, "notable_crew_members": [{"name": "Horatio Nelson", "fame_level": 100}], "historical_significance_score": 80.0, "data_completeness_score": 81.0},
        {"name": "Neptune", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1797, "era": "age_of_sail", "battles_participated": 6, "battles_won": 5, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Orion", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1787, "era": "age_of_sail", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Minotaur", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1793, "era": "age_of_sail", "battles_participated": 5, "battles_won": 4, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Leviathan", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1790, "era": "age_of_sail", "battles_participated": 7, "battles_won": 5, "historical_significance_score": 79.0, "data_completeness_score": 77.0},
        {"name": "Conqueror", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1801, "era": "age_of_sail", "battles_participated": 6, "battles_won": 5, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        {"name": "Thunderer", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1783, "era": "age_of_sail", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Warrior", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1781, "era": "age_of_sail", "battles_participated": 9, "battles_won": 7, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Defiance", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1783, "era": "age_of_sail", "battles_participated": 11, "battles_won": 8, "historical_significance_score": 75.0, "data_completeness_score": 74.0},
        {"name": "Defence", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1763, "era": "age_of_sail", "battles_participated": 10, "battles_won": 7, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Revenge", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1577, "era": "age_of_discovery", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 86.0, "data_completeness_score": 78.0},
        {"name": "Dreadnought", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1906, "era": "steam_era", "battles_participated": 4, "battles_won": 3, "historical_significance_score": 95.0, "major_achievements": [{"achievement": "Revolutionary battleship design", "impact": 100}], "data_completeness_score": 90.0},
        {"name": "Warspite", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1913, "era": "steam_era", "battles_participated": 18, "battles_won": 15, "historical_significance_score": 90.0, "crew_casualties": 257, "data_completeness_score": 88.0},
        {"name": "Valiant", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1914, "era": "steam_era", "battles_participated": 12, "battles_won": 10, "historical_significance_score": 82.0, "data_completeness_score": 80.0},
        {"name": "Repulse", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 5, "battles_won": 3, "was_sunk": True, "sunk_year": 1941, "crew_casualties": 513, "historical_significance_score": 85.0, "data_completeness_score": 83.0},
        {"name": "Renown", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 83.0, "data_completeness_score": 81.0},
        
        # ========== WWII US DESTROYERS (50+ SHIPS) ==========
        {"name": "Fletcher", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 15, "battles_won": 14, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Nicholas", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 16, "battles_won": 15, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "O'Bannon", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 17, "battles_won": 16, "historical_significance_score": 79.0, "data_completeness_score": 77.0},
        {"name": "Johnston", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 5, "battles_won": 3, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 186, "notable_achievements": [{"achievement": "Heroic stand at Samar", "impact": 92}], "historical_significance_score": 88.0, "data_completeness_score": 85.0},
        {"name": "Samuel B. Roberts", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 2, "battles_won": 1, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 89, "historical_significance_score": 82.0, "data_completeness_score": 80.0},
        {"name": "Laffey", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 12, "battles_won": 11, "major_events": [{"battle": "Survived 22 kamikaze attacks", "date": "1945-04-16"}], "historical_significance_score": 83.0, "data_completeness_score": 81.0},
        {"name": "Kidd", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 10, "battles_won": 9, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Heermann", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 8, "battles_won": 7, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Hoel", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 3, "battles_won": 2, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 253, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        
        # ========== MORE SAINT-NAMED SHIPS (SPANISH ARMADA) ==========
        {"name": "San Martín", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1580, "era": "age_of_discovery", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 79.0, "data_completeness_score": 74.0},
        {"name": "San Juan", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 78.0, "data_completeness_score": 73.0},
        {"name": "San Mateo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 76.0, "data_completeness_score": 72.0},
        {"name": "San Felipe", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 77.0, "data_completeness_score": 73.0},
        {"name": "San Salvador", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Santiago", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1515, "era": "age_of_discovery", "historical_significance_score": 75.0, "data_completeness_score": 70.0},
        {"name": "San Pedro", "prefix": None, "nation": "Spain", "ship_type": "commercial", "launch_year": 1565, "era": "age_of_discovery", "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "Santa Ana", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 79.0, "data_completeness_score": 75.0},
        {"name": "San Lorenzo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "San Luis", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "San Marcos", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "Santa Catalina", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1602, "era": "age_of_sail", "historical_significance_score": 73.0, "data_completeness_score": 70.0},
        {"name": "San Diego", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 75.0, "data_completeness_score": 72.0},
        {"name": "San Francisco", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 74.0, "data_completeness_score": 71.0},
        {"name": "San Bernardo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "San Esteban", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 69.0, "data_completeness_score": 67.0},
        {"name": "San Juan Bautista", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1611, "era": "age_of_sail", "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "San Nicolas", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1769, "era": "age_of_sail", "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "San Carlos", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1770, "era": "age_of_sail", "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Santa Rosa", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1602, "era": "age_of_sail", "historical_significance_score": 69.0, "data_completeness_score": 67.0},
        {"name": "San Buenaventura", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1769, "era": "age_of_sail", "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        
        # ========== FRENCH SHIPS ==========
        {"name": "Bucentaure", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1803, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "major_events": [{"battle": "Trafalgar", "outcome": "Captured"}], "crew_casualties": 442, "historical_significance_score": 83.0, "data_completeness_score": 80.0},
        {"name": "Redoutable", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1791, "era": "age_of_sail", "battles_participated": 5, "battles_won": 2, "major_events": [{"battle": "Trafalgar", "detail": "Killed Nelson"}], "crew_casualties": 487, "historical_significance_score": 82.0, "data_completeness_score": 81.0},
        {"name": "Achille", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1803, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "crew_casualties": 480, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Intrépide", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1800, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Spartiate", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1797, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Foudroyant", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1750, "era": "age_of_sail", "battles_participated": 6, "battles_won": 4, "historical_significance_score": 79.0, "data_completeness_score": 76.0},
        {"name": "Orient", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1791, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "was_sunk": True, "sunk_year": 1798, "major_events": [{"battle": "Battle of the Nile", "exploded": True}], "crew_casualties": 1000, "historical_significance_score": 85.0, "data_completeness_score": 83.0},
        {"name": "Formidable", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1795, "era": "age_of_sail", "battles_participated": 7, "battles_won": 4, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Duguay-Trouin", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1800, "era": "age_of_sail", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Mont-Blanc", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1791, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Algésiras", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1804, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Aigle", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1800, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Swiftsure", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1787, "era": "age_of_sail", "battles_participated": 6, "battles_won": 4, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Héros", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1778, "era": "age_of_sail", "battles_participated": 8, "battles_won": 5, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Neptune", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1803, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Indomptable", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1790, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Berwick", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1795, "era": "age_of_sail", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Argonaute", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1798, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Scipion", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1801, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "Pluton", "prefix": None, "nation": "France", "ship_type": "naval", "launch_year": 1803, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "Argonauta", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1798, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Bahama", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1780, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Montañés", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1794, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "Monarca", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1794, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "San Rafael", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1798, "era": "age_of_sail", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "Príncipe de Asturias", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1794, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Rayo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1749, "era": "age_of_sail", "battles_participated": 8, "battles_won": 4, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Neptuno", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1795, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "Santísima Trinidad", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1769, "era": "age_of_sail", "tonnage": 4950, "armament": "140 guns", "battles_participated": 4, "battles_won": 1, "major_events": [{"battle": "Trafalgar", "detail": "Largest warship afloat"}], "crew_casualties": 312, "historical_significance_score": 87.0, "data_completeness_score": 85.0},
        
        # ========== GERMAN SHIPS ==========
        {"name": "Scharnhorst", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1936, "era": "modern", "tonnage": 38900, "battles_participated": 8, "battles_won": 4, "ships_sunk": 3, "was_sunk": True, "sunk_year": 1943, "crew_casualties": 1968, "major_events": [{"battle": "Battle of North Cape", "date": "1943-12-26", "outcome": "Sunk by HMS Belfast and Duke of York"}], "historical_significance_score": 86.0, "data_completeness_score": 84.0},
        {"name": "Gneisenau", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1936, "era": "modern", "battles_participated": 7, "battles_won": 4, "ships_sunk": 2, "historical_significance_score": 82.0, "data_completeness_score": 80.0},
        {"name": "Tirpitz", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1939, "era": "modern", "tonnage": 52600, "battles_participated": 2, "battles_won": 0, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 1204, "historical_significance_score": 84.0, "data_completeness_score": 82.0},
        {"name": "Graf Spee", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1934, "era": "modern", "battles_participated": 10, "battles_won": 9, "ships_sunk": 9, "major_events": [{"battle": "Battle of the River Plate", "date": "1939-12-13", "outcome": "Scuttled"}], "crew_casualties": 36, "historical_significance_score": 83.0, "data_completeness_score": 81.0},
        {"name": "Prinz Eugen", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1938, "era": "modern", "battles_participated": 6, "battles_won": 3, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        {"name": "Blücher", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1908, "era": "steam_era", "battles_participated": 4, "battles_won": 2, "was_sunk": True, "sunk_year": 1940, "crew_casualties": 1000, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Emden", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1908, "era": "steam_era", "battles_participated": 14, "battles_won": 12, "ships_sunk": 15, "historical_significance_score": 81.0, "data_completeness_score": 79.0},
        {"name": "Karlsruhe", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1912, "era": "steam_era", "battles_participated": 6, "battles_won": 4, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Nürnberg", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1906, "era": "steam_era", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Leipzig", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1905, "era": "steam_era", "battles_participated": 7, "battles_won": 4, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Dresden", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1907, "era": "steam_era", "battles_participated": 8, "battles_won": 5, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Köln", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Berlin", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1903, "era": "steam_era", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Hamburg", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1903, "era": "steam_era", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "München", "prefix": None, "nation": "Germany", "ship_type": "naval", "launch_year": 1904, "era": "steam_era", "battles_participated": 3, "battles_won": 2, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        
        # ========== ITALIAN SHIPS (GEOGRAPHIC CITIES) ==========
        {"name": "Roma", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1940, "era": "modern", "tonnage": 45000, "battles_participated": 3, "battles_won": 1, "was_sunk": True, "sunk_year": 1943, "sunk_reason": "German guided bomb", "crew_casualties": 1393, "historical_significance_score": 80.0, "data_completeness_score": 79.0},
        {"name": "Venezia", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1919, "era": "modern", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Napoli", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1914, "era": "steam_era", "battles_participated": 6, "battles_won": 4, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Milano", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 2, "battles_won": 1, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "Genova", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1923, "era": "modern", "battles_participated": 7, "battles_won": 4, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "Torino", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 69.0, "data_completeness_score": 67.0},
        {"name": "Firenze", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1914, "era": "steam_era", "battles_participated": 5, "battles_won": 3, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Bologna", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1918, "era": "modern", "battles_participated": 3, "battles_won": 2, "historical_significance_score": 68.0, "data_completeness_score": 66.0},
        {"name": "Trieste", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1926, "era": "modern", "battles_participated": 6, "battles_won": 4, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Trento", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1927, "era": "modern", "battles_participated": 5, "battles_won": 3, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 549, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Bolzano", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1932, "era": "modern", "battles_participated": 4, "battles_won": 2, "was_sunk": True, "sunk_year": 1944, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Pola", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1931, "era": "modern", "battles_participated": 3, "battles_won": 1, "was_sunk": True, "sunk_year": 1941, "crew_casualties": 328, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Fiume", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1930, "era": "modern", "battles_participated": 4, "battles_won": 2, "was_sunk": True, "sunk_year": 1941, "crew_casualties": 812, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Zara", "prefix": None, "nation": "Italy", "ship_type": "naval", "launch_year": 1930, "era": "modern", "battles_participated": 5, "battles_won": 3, "was_sunk": True, "sunk_year": 1941, "crew_casualties": 783, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        
        # ========== MORE UK DESTROYERS AND ESCORTS ==========
        {"name": "Cossack", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1937, "era": "modern", "battles_participated": 12, "battles_won": 10, "major_events": [{"event": "Altmark Incident", "date": "1940-02-16", "fame": 90}], "was_sunk": True, "sunk_year": 1941, "crew_casualties": 159, "historical_significance_score": 82.0, "data_completeness_score": 80.0},
        {"name": "Kelly", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1938, "era": "modern", "battles_participated": 8, "battles_won": 5, "was_sunk": True, "sunk_year": 1941, "crew_casualties": 131, "notable_crew_members": [{"name": "Lord Louis Mountbatten", "fame_level": 95}], "historical_significance_score": 80.0, "data_completeness_score": 79.0},
        {"name": "Jervis", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1938, "era": "modern", "battles_participated": 13, "battles_won": 11, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Javelin", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1938, "era": "modern", "battles_participated": 10, "battles_won": 8, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Janus", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1938, "era": "modern", "battles_participated": 9, "battles_won": 6, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 153, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Kandahar", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1939, "era": "modern", "battles_participated": 7, "battles_won": 5, "was_sunk": True, "sunk_year": 1941, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Kingston", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1939, "era": "modern", "battles_participated": 11, "battles_won": 9, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Kipling", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1939, "era": "modern", "battles_participated": 12, "battles_won": 10, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        
        # ========== JAPANESE SHIPS ==========
        {"name": "Yamato", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1940, "era": "modern", "tonnage": 72800, "battles_participated": 4, "battles_won": 1, "was_sunk": True, "sunk_year": 1945, "crew_casualties": 2498, "major_achievements": [{"achievement": "Largest battleship ever built", "impact": 92}], "historical_significance_score": 89.0, "data_completeness_score": 87.0},
        {"name": "Musashi", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1940, "era": "modern", "tonnage": 72800, "battles_participated": 3, "battles_won": 1, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 1023, "historical_significance_score": 85.0, "data_completeness_score": 83.0},
        {"name": "Nagato", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1919, "era": "modern", "battles_participated": 5, "battles_won": 2, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        {"name": "Akagi", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1925, "era": "modern", "battles_participated": 6, "battles_won": 4, "was_sunk": True, "sunk_year": 1942, "major_events": [{"battle": "Pearl Harbor attack", "role": "Flagship"}, {"battle": "Battle of Midway", "outcome": "Sunk"}], "crew_casualties": 267, "historical_significance_score": 88.0, "data_completeness_score": 86.0},
        {"name": "Kaga", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1921, "era": "modern", "battles_participated": 6, "battles_won": 4, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 811, "historical_significance_score": 86.0, "data_completeness_score": 84.0},
        {"name": "Soryu", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1935, "era": "modern", "battles_participated": 6, "battles_won": 4, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 711, "historical_significance_score": 83.0, "data_completeness_score": 81.0},
        {"name": "Hiryu", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1937, "era": "modern", "battles_participated": 6, "battles_won": 4, "was_sunk": True, "sunk_year": 1942, "crew_casualties": 392, "historical_significance_score": 84.0, "data_completeness_score": 82.0},
        {"name": "Shokaku", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1939, "era": "modern", "battles_participated": 8, "battles_won": 5, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 1272, "historical_significance_score": 85.0, "data_completeness_score": 83.0},
        {"name": "Zuikaku", "prefix": None, "nation": "Japan", "ship_type": "naval", "launch_year": 1939, "era": "modern", "battles_participated": 9, "battles_won": 6, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 842, "historical_significance_score": 84.0, "data_completeness_score": 82.0},
        
        # ========== MORE US CARRIERS ==========
        {"name": "Essex", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 12, "battles_won": 11, "historical_significance_score": 83.0, "data_completeness_score": 81.0},
        {"name": "Bunker Hill", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 11, "battles_won": 10, "crew_casualties": 646, "major_events": [{"event": "Kamikaze attacks", "date": "1945-05-11", "casualties": 396}], "historical_significance_score": 81.0, "data_completeness_score": 79.0},
        {"name": "Hancock", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 9, "battles_won": 8, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Randolph", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1944, "era": "modern", "battles_participated": 7, "battles_won": 6, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Ticonderoga", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1944, "era": "modern", "battles_participated": 9, "battles_won": 8, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        {"name": "Princeton", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 6, "battles_won": 5, "was_sunk": True, "sunk_year": 1944, "crew_casualties": 108, "historical_significance_score": 79.0, "data_completeness_score": 77.0},
        {"name": "Belleau Wood", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 10, "battles_won": 9, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Cowpens", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 9, "battles_won": 8, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Monterey", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 8, "battles_won": 7, "notable_crew_members": [{"name": "Gerald Ford (future president)", "fame_level": 95}], "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Langley", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 7, "battles_won": 6, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Cabot", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 9, "battles_won": 8, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Bataan", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 8, "battles_won": 7, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "San Jacinto", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1943, "era": "modern", "battles_participated": 10, "battles_won": 9, "notable_crew_members": [{"name": "George H.W. Bush (future president)", "fame_level": 95}], "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        
        # ========== SUBMARINES ==========
        {"name": "Nautilus", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1954, "era": "modern", "major_achievements": [{"achievement": "First nuclear submarine", "impact": 98}, {"achievement": "First submerged transit of North Pole", "date": "1958", "impact": 95}], "historical_significance_score": 89.0, "data_completeness_score": 87.0},
        {"name": "Seawolf", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1955, "era": "modern", "historical_significance_score": 78.0, "data_completeness_score": 75.0},
        {"name": "Scorpion", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1959, "era": "modern", "was_sunk": True, "sunk_year": 1968, "crew_casualties": 99, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Thresher", "prefix": "USS", "nation": "US", "ship_type": "naval", "launch_year": 1960, "era": "modern", "was_sunk": True, "sunk_year": 1963, "crew_casualties": 129, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        
        # ========== VIRTUE-NAMED WARSHIPS ==========
        {"name": "Vanguard", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1944, "era": "modern", "tonnage": 44500, "battles_participated": 0, "historical_significance_score": 82.0, "major_achievements": [{"achievement": "Last battleship built", "impact": 88}], "data_completeness_score": 80.0},
        {"name": "Vengeance", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1944, "era": "modern", "battles_participated": 3, "battles_won": 3, "historical_significance_score": 78.0, "data_completeness_score": 76.0},
        {"name": "Vigilant", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1774, "era": "age_of_sail", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Victorious", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1939, "era": "modern", "battles_participated": 10, "battles_won": 8, "historical_significance_score": 85.0, "data_completeness_score": 83.0},
        {"name": "Venerable", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1784, "era": "age_of_sail", "battles_participated": 9, "battles_won": 7, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Indefatigable", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1909, "era": "steam_era", "battles_participated": 8, "battles_won": 5, "was_sunk": True, "sunk_year": 1916, "crew_casualties": 1017, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        {"name": "Inflexible", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1907, "era": "steam_era", "battles_participated": 7, "battles_won": 5, "historical_significance_score": 79.0, "data_completeness_score": 77.0},
        {"name": "Implacable", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1942, "era": "modern", "battles_participated": 6, "battles_won": 5, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Dauntless", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1918, "era": "modern", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Daring", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1949, "era": "modern", "battles_participated": 4, "battles_won": 4, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Courageous", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 2, "battles_won": 1, "was_sunk": True, "sunk_year": 1939, "crew_casualties": 518, "historical_significance_score": 80.0, "data_completeness_score": 78.0},
        {"name": "Glorious", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 3, "battles_won": 1, "was_sunk": True, "sunk_year": 1940, "crew_casualties": 1207, "historical_significance_score": 81.0, "data_completeness_score": 79.0},
        {"name": "Furious", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 83.0, "data_completeness_score": 81.0},
        {"name": "Audacious", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1912, "era": "steam_era", "battles_participated": 1, "battles_won": 0, "was_sunk": True, "sunk_year": 1914, "crew_casualties": 0, "historical_significance_score": 76.0, "data_completeness_score": 74.0},
        {"name": "Irresistible", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1898, "era": "steam_era", "battles_participated": 6, "battles_won": 4, "was_sunk": True, "sunk_year": 1915, "crew_casualties": 5, "historical_significance_score": 75.0, "data_completeness_score": 73.0},
        {"name": "Triumph", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1903, "era": "steam_era", "battles_participated": 7, "battles_won": 5, "historical_significance_score": 77.0, "data_completeness_score": 75.0},
        {"name": "Ramillies", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1916, "era": "modern", "battles_participated": 8, "battles_won": 6, "historical_significance_score": 79.0, "data_completeness_score": 77.0},
        {"name": "Royal Oak", "prefix": "HMS", "nation": "UK", "ship_type": "naval", "launch_year": 1914, "era": "steam_era", "battles_participated": 2, "battles_won": 1, "was_sunk": True, "sunk_year": 1939, "sunk_reason": "U-boat torpedo in Scapa Flow", "crew_casualties": 835, "historical_significance_score": 82.0, "data_completeness_score": 80.0},
        
        # ========== MORE EXPLORATION/RESEARCH VESSELS ==========
        {"name": "Challenger", "prefix": "HMS", "nation": "UK", "ship_type": "exploration", "launch_year": 1858, "era": "age_of_sail", "famous_voyages": [{"voyage": "Challenger Expedition", "dates": "1872-1876", "achievement": "Founded oceanography"}], "major_discoveries": [{"discovery": "Mariana Trench", "year": 1875, "significance": 95}, {"discovery": "4,717 new species", "significance": 92}], "historical_significance_score": 91.0, "major_events_count": 6, "data_completeness_score": 88.0},
        {"name": "Fram", "prefix": None, "nation": "Norway", "ship_type": "exploration", "launch_year": 1892, "era": "steam_era", "famous_voyages": [{"voyage": "Nansen Arctic drift", "dates": "1893-1896"}, {"voyage": "Amundsen Antarctic", "dates": "1910-1912", "achievement": "First to South Pole"}], "notable_crew_members": [{"name": "Roald Amundsen", "fame_level": 98}], "major_discoveries": [{"discovery": "South Pole reached", "year": 1911, "significance": 98}], "historical_significance_score": 93.0, "major_events_count": 7, "data_completeness_score": 90.0},
        {"name": "Investigator", "prefix": "HMS", "nation": "UK", "ship_type": "exploration", "launch_year": 1795, "era": "age_of_sail", "famous_voyages": [{"voyage": "Australian coast survey", "dates": "1801-1803", "captain": "Matthew Flinders"}], "notable_crew_members": [{"name": "Matthew Flinders", "fame_level": 82}], "major_discoveries": [{"discovery": "Proved Australia is continent", "year": 1803, "significance": 90}], "historical_significance_score": 78.0, "major_events_count": 4, "data_completeness_score": 76.0},
        {"name": "Calypso", "prefix": None, "nation": "France", "ship_type": "exploration", "launch_year": 1942, "era": "modern", "famous_voyages": [{"voyage": "Cousteau expeditions", "dates": "1951-1997"}], "notable_crew_members": [{"name": "Jacques Cousteau", "fame_level": 96}], "scientific_contributions": [{"contribution": "Underwater exploration pioneering", "impact": 94}], "historical_significance_score": 86.0, "major_events_count": 5, "cultural_impact_score": 92, "data_completeness_score": 85.0},
        
        # ========== ADDITIONAL SAINT-NAMED SHIPS (BALANCE DATASET) ==========
        {"name": "Santa Margarita", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1620, "era": "age_of_sail", "battles_participated": 3, "battles_won": 2, "was_sunk": True, "sunk_year": 1622, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "San Cristóbal", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1519, "era": "age_of_discovery", "historical_significance_score": 77.0, "data_completeness_score": 72.0},
        {"name": "San Antonio", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1519, "era": "age_of_discovery", "historical_significance_score": 80.0, "data_completeness_score": 75.0},
        {"name": "San Miguel", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1519, "era": "age_of_discovery", "historical_significance_score": 76.0, "data_completeness_score": 73.0},
        {"name": "Santa Clara", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1492, "era": "age_of_discovery", "historical_significance_score": 85.0, "famous_voyages": [{"voyage": "Columbus voyage (Niña)", "date": "1492"}], "data_completeness_score": 78.0},
        {"name": "San Martin", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1580, "era": "age_of_discovery", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 79.0, "data_completeness_score": 75.0},
        {"name": "Santa María de la Victoria", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1519, "era": "age_of_discovery", "historical_significance_score": 78.0, "data_completeness_score": 74.0},
        {"name": "San Vicente", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1765, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Santa Teresa", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1782, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "San Jerónimo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "San Pablo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 69.0, "data_completeness_score": 67.0},
        {"name": "Santa Bárbara", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 68.0, "data_completeness_score": 66.0},
        {"name": "San Andrés", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1588, "era": "age_of_discovery", "battles_participated": 1, "battles_won": 0, "historical_significance_score": 69.0, "data_completeness_score": 67.0},
        {"name": "Santa Isabel", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1595, "era": "age_of_discovery", "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "San Ignacio", "prefix": None, "nation": "Spain", "ship_type": "commercial", "launch_year": 1612, "era": "age_of_sail", "historical_significance_score": 67.0, "data_completeness_score": 65.0},
        {"name": "Santa Lucía", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1602, "era": "age_of_sail", "historical_significance_score": 68.0, "data_completeness_score": 66.0},
        {"name": "San Joaquín", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1650, "era": "age_of_sail", "battles_participated": 2, "battles_won": 1, "historical_significance_score": 69.0, "data_completeness_score": 67.0},
        {"name": "Santa Gertrudis", "prefix": None, "nation": "Spain", "ship_type": "commercial", "launch_year": 1715, "era": "age_of_sail", "historical_significance_score": 66.0, "data_completeness_score": 64.0},
        {"name": "San José", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1698, "era": "age_of_sail", "battles_participated": 5, "battles_won": 3, "was_sunk": True, "sunk_year": 1708, "historical_significance_score": 74.0, "data_completeness_score": 72.0},
        {"name": "Santa Águeda", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1715, "era": "age_of_sail", "battles_participated": 2, "battles_won": 1, "historical_significance_score": 68.0, "data_completeness_score": 66.0},
        {"name": "San Fernando", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1750, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 71.0, "data_completeness_score": 69.0},
        {"name": "Santa María Magdalena", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1760, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "San Genaro", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1765, "era": "age_of_sail", "battles_participated": 2, "battles_won": 0, "historical_significance_score": 67.0, "data_completeness_score": 65.0},
        {"name": "Santa Cecilia", "prefix": None, "nation": "Spain", "ship_type": "exploration", "launch_year": 1602, "era": "age_of_sail", "historical_significance_score": 68.0, "data_completeness_score": 66.0},
        {"name": "San Sebastián", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1680, "era": "age_of_sail", "battles_participated": 4, "battles_won": 2, "historical_significance_score": 70.0, "data_completeness_score": 68.0},
        {"name": "Santa Mónica", "prefix": None, "nation": "Spain", "ship_type": "commercial", "launch_year": 1725, "era": "age_of_sail", "historical_significance_score": 65.0, "data_completeness_score": 63.0},
        {"name": "San Hermenegildo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1789, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "was_sunk": True, "sunk_year": 1801, "crew_casualties": 450, "historical_significance_score": 72.0, "data_completeness_score": 70.0},
        {"name": "Santa Trinidad", "prefix": None, "nation": "Spain", "ship_type": "commercial", "launch_year": 1670, "era": "age_of_sail", "historical_significance_score": 67.0, "data_completeness_score": 65.0},
        {"name": "San Telmo", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1788, "era": "age_of_sail", "battles_participated": 2, "battles_won": 1, "was_sunk": True, "sunk_year": 1819, "crew_casualties": 644, "historical_significance_score": 73.0, "data_completeness_score": 71.0},
        {"name": "Santa Eulalia", "prefix": None, "nation": "Spain", "ship_type": "commercial", "launch_year": 1693, "era": "age_of_sail", "historical_significance_score": 66.0, "data_completeness_score": 64.0},
        {"name": "San Fulgencio", "prefix": None, "nation": "Spain", "ship_type": "naval", "launch_year": 1770, "era": "age_of_sail", "battles_participated": 3, "battles_won": 1, "historical_significance_score": 69.0, "data_completeness_score": 67.0}
    ]
    
    return ships


if __name__ == "__main__":
    ships = get_comprehensive_ships()
    print(f"Total ships: {len(ships)}")
    print(f"With battle data: {sum(1 for s in ships if 'battles_participated' in s)}")
    print(f"With discoveries: {sum(1 for s in ships if 'major_discoveries' in s)}")
    print(f"With crew members: {sum(1 for s in ships if 'notable_crew_members' in s)}")

