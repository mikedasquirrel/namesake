"""Debug Player Page Parsing"""

import requests
from bs4 import BeautifulSoup

url = "https://www.pro-football-reference.com/players/T/TagoTu00.htm"
headers = {'User-Agent': 'Mozilla/5.0'}

print(f"Fetching: {url}\n")

response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

# Name
print("=== NAME ===")
h1 = soup.find('h1')
if h1:
    print(f"H1 found: {h1.get_text(strip=True)}")
    for span in h1.find_all('span'):
        print(f"  Span: {span.get_text(strip=True)}")
else:
    print("No H1 found")

# Meta div
print("\n=== META DIV ===")
meta = soup.find('div', {'id': 'meta'})
if meta:
    print("Meta div found")
    paragraphs = meta.find_all('p')
    for i, p in enumerate(paragraphs[:5]):
        print(f"P{i+1}: {p.get_text(strip=True)[:100]}")
else:
    print("No meta div found")

# Stats table
print("\n=== STATS TABLE ===")
stats_table = soup.find('table', {'id': 'stats'})
if stats_table:
    print(f"Stats table found with ID: {stats_table.get('id')}")
    tfoot = stats_table.find('tfoot')
    if tfoot:
        print("Found tfoot (career totals)")
        career_row = tfoot.find('tr')
        if career_row:
            cells = career_row.find_all(['td', 'th'])
            print(f"Career row has {len(cells)} cells")
            for cell in cells[:10]:
                data_stat = cell.get('data-stat', 'no-stat')
                text = cell.get_text(strip=True)
                print(f"  {data_stat}: {text}")
    else:
        print("No tfoot found")
else:
    print("No stats table found")
    # Try to find any tables
    all_tables = soup.find_all('table')
    print(f"\nFound {len(all_tables)} tables:")
    for t in all_tables[:5]:
        print(f"  ID: {t.get('id')}, Classes: {t.get('class')}")

