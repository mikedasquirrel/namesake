"""Debug NFL Scraping - See What's Being Found

Quick script to test scraping without full collection.
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

base_url = "https://www.pro-football-reference.com"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Test QB passing stats for 2023
year = 2023
stat_type = 'passing'
url = f"{base_url}/years/{year}/{stat_type}.htm"

print(f"\nFetching: {url}\n")

response = requests.get(url, headers=headers, timeout=15)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')

# Find the stats table
print("Looking for table...")
table = soup.find('table', {'id': stat_type})
if not table:
    table = soup.find('table', {'class': 'stats_table'})

if not table:
    print("❌ No table found!")
    
    # Show all tables
    all_tables = soup.find_all('table')
    print(f"\nFound {len(all_tables)} tables total:")
    for t in all_tables[:5]:
        print(f"  - ID: {t.get('id')}, Classes: {t.get('class')}")
    sys.exit(1)

print(f"✓ Found table with ID: {table.get('id')}")

tbody = table.find('tbody')
if not tbody:
    print("❌ No tbody found!")
    sys.exit(1)

rows = tbody.find_all('tr')
print(f"✓ Found {len(rows)} rows")

# Check first 5 rows
print("\nFirst 20 rows (debugging):")
count = 0
for i, row in enumerate(rows[:20]):
    # Skip header rows
    if row.get('class') and 'thead' in row.get('class'):
        print(f"{i+1}. [HEADER ROW - skipping]")
        continue
    
    # Show all cells in first few rows
    cells = row.find_all(['td', 'th'])
    print(f"\n{i+1}. Row has {len(cells)} cells:")
    for cell in cells[:3]:
        data_stat = cell.get('data-stat', 'no-data-stat')
        text = cell.get_text(strip=True)[:30]
        has_link = 'YES' if cell.find('a') else 'NO'
        print(f"     - data-stat='{data_stat}', text='{text}', has_link={has_link}")
    
    # Get player link
    player_link = row.find('td', {'data-stat': 'name_display'})
    if not player_link:
        player_link = row.find('td', {'data-stat': 'player'})
    if not player_link:
        player_link = row.find('th', {'data-stat': 'player'})
    
    if not player_link:
        print(f"     ❌ No player cell found!")
        continue
    
    a_tag = player_link.find('a')
    if not a_tag or not a_tag.get('href'):
        continue
    
    player_href = a_tag['href']
    
    if '/players/' not in player_href:
        continue
    
    player_name = a_tag.get_text(strip=True)
    player_id = player_href.split('/')[-1].replace('.htm', '')
    
    # Get position
    pos_cell = row.find('td', {'data-stat': 'pos'})
    position = pos_cell.get_text(strip=True) if pos_cell else 'N/A'
    
    # Get team
    team_cell = row.find('td', {'data-stat': 'team'})
    team = team_cell.get_text(strip=True) if team_cell else 'N/A'
    
    # Get stats
    att_cell = row.find('td', {'data-stat': 'pass_att'})
    attempts = att_cell.get_text(strip=True) if att_cell else 'N/A'
    
    print(f"{count+1}. {player_name} ({player_id})")
    print(f"   Position: {position}, Team: {team}, Attempts: {attempts}")
    print(f"   URL: {base_url}{player_href}\n")
    
    count += 1
    if count >= 5:
        break

print(f"✓ Successfully found {count} QBs from {year}")

