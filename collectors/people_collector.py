"""
People Name Collector
Collects names of successful people for nominative determinism analysis
"""

import logging

logger = logging.getLogger(__name__)


class PeopleCollector:
    """Collect successful people's names"""
    
    def get_bootstrap_data(self):
        """Well-known successful people (real data from Forbes, public sources)"""
        
        # Forbes Billionaires, Fortune 500 CEOs, Notable Achievers
        # All real people with verifiable success metrics
        successful_people = [
            # Tech Billionaires
            {'first_name': 'Elon', 'last_name': 'Musk', 'full_name': 'Elon Musk', 'net_worth': 230000000000, 'field': 'Tech/Auto', 'achievement': 'Tesla/SpaceX CEO'},
            {'first_name': 'Jeff', 'last_name': 'Bezos', 'full_name': 'Jeff Bezos', 'net_worth': 160000000000, 'field': 'Tech/E-commerce', 'achievement': 'Amazon Founder'},
            {'first_name': 'Bernard', 'last_name': 'Arnault', 'full_name': 'Bernard Arnault', 'net_worth': 210000000000, 'field': 'Luxury', 'achievement': 'LVMH CEO'},
            {'first_name': 'Bill', 'last_name': 'Gates', 'full_name': 'Bill Gates', 'net_worth': 120000000000, 'field': 'Tech', 'achievement': 'Microsoft Founder'},
            {'first_name': 'Warren', 'last_name': 'Buffett', 'full_name': 'Warren Buffett', 'net_worth': 115000000000, 'field': 'Investing', 'achievement': 'Berkshire Hathaway CEO'},
            {'first_name': 'Larry', 'last_name': 'Page', 'full_name': 'Larry Page', 'net_worth': 110000000000, 'field': 'Tech', 'achievement': 'Google Founder'},
            {'first_name': 'Sergey', 'last_name': 'Brin', 'full_name': 'Sergey Brin', 'net_worth': 105000000000, 'field': 'Tech', 'achievement': 'Google Founder'},
            {'first_name': 'Mark', 'last_name': 'Zuckerberg', 'full_name': 'Mark Zuckerberg', 'net_worth': 100000000000, 'field': 'Tech/Social', 'achievement': 'Meta/Facebook Founder'},
            {'first_name': 'Steve', 'last_name': 'Ballmer', 'full_name': 'Steve Ballmer', 'net_worth': 95000000000, 'field': 'Tech', 'achievement': 'Microsoft CEO'},
            {'first_name': 'Larry', 'last_name': 'Ellison', 'full_name': 'Larry Ellison', 'net_worth': 120000000000, 'field': 'Tech', 'achievement': 'Oracle Founder'},
            
            # Fortune 500 CEOs
            {'first_name': 'Tim', 'last_name': 'Cook', 'full_name': 'Tim Cook', 'net_worth': 2000000000, 'field': 'Tech', 'achievement': 'Apple CEO'},
            {'first_name': 'Satya', 'last_name': 'Nadella', 'full_name': 'Satya Nadella', 'net_worth': 800000000, 'field': 'Tech', 'achievement': 'Microsoft CEO'},
            {'first_name': 'Sundar', 'last_name': 'Pichai', 'full_name': 'Sundar Pichai', 'net_worth': 600000000, 'field': 'Tech', 'achievement': 'Google CEO'},
            {'first_name': 'Jensen', 'last_name': 'Huang', 'full_name': 'Jensen Huang', 'net_worth': 15000000000, 'field': 'Tech', 'achievement': 'NVIDIA CEO'},
            {'first_name': 'Lisa', 'last_name': 'Su', 'full_name': 'Lisa Su', 'net_worth': 1000000000, 'field': 'Tech', 'achievement': 'AMD CEO'},
            {'first_name': 'Marc', 'last_name': 'Benioff', 'full_name': 'Marc Benioff', 'net_worth': 8000000000, 'field': 'Tech', 'achievement': 'Salesforce CEO'},
            {'first_name': 'Reed', 'last_name': 'Hastings', 'full_name': 'Reed Hastings', 'net_worth': 3500000000, 'field': 'Tech/Media', 'achievement': 'Netflix CEO'},
            
            # Entrepreneurs
            {'first_name': 'Jack', 'last_name': 'Dorsey', 'full_name': 'Jack Dorsey', 'net_worth': 5000000000, 'field': 'Tech/Fintech', 'achievement': 'Twitter/Square Founder'},
            {'first_name': 'Brian', 'last_name': 'Armstrong', 'full_name': 'Brian Armstrong', 'net_worth': 2500000000, 'field': 'Crypto', 'achievement': 'Coinbase CEO'},
            {'first_name': 'Sam', 'last_name': 'Altman', 'full_name': 'Sam Altman', 'net_worth': 500000000, 'field': 'AI', 'achievement': 'OpenAI CEO'},
            {'first_name': 'Travis', 'last_name': 'Kalanick', 'full_name': 'Travis Kalanick', 'net_worth': 3000000000, 'field': 'Tech', 'achievement': 'Uber Founder'},
            {'first_name': 'Drew', 'last_name': 'Houston', 'full_name': 'Drew Houston', 'net_worth': 2000000000, 'field': 'Tech', 'achievement': 'Dropbox CEO'},
            
            # Investors/Finance
            {'first_name': 'Ray', 'last_name': 'Dalio', 'full_name': 'Ray Dalio', 'net_worth': 15000000000, 'field': 'Finance', 'achievement': 'Bridgewater Founder'},
            {'first_name': 'Carl', 'last_name': 'Icahn', 'full_name': 'Carl Icahn', 'net_worth': 24000000000, 'field': 'Investing', 'achievement': 'Activist Investor'},
            {'first_name': 'George', 'last_name': 'Soros', 'full_name': 'George Soros', 'net_worth': 8500000000, 'field': 'Finance', 'achievement': 'Soros Fund'},
            {'first_name': 'Ken', 'last_name': 'Griffin', 'full_name': 'Ken Griffin', 'net_worth': 35000000000, 'field': 'Finance', 'achievement': 'Citadel CEO'},
            
            # More entrepreneurs
            {'first_name': 'Peter', 'last_name': 'Thiel', 'full_name': 'Peter Thiel', 'net_worth': 7000000000, 'field': 'Tech/VC', 'achievement': 'PayPal/Palantir'},
            {'first_name': 'Reid', 'last_name': 'Hoffman', 'full_name': 'Reid Hoffman', 'net_worth': 3000000000, 'field': 'Tech/VC', 'achievement': 'LinkedIn Founder'},
            {'first_name': 'Daniel', 'last_name': 'Ek', 'full_name': 'Daniel Ek', 'net_worth': 4000000000, 'field': 'Tech/Music', 'achievement': 'Spotify CEO'},
            {'first_name': 'Patrick', 'last_name': 'Collison', 'full_name': 'Patrick Collison', 'net_worth': 11000000000, 'field': 'Fintech', 'achievement': 'Stripe CEO'},
            {'first_name': 'John', 'last_name': 'Collison', 'full_name': 'John Collison', 'net_worth': 11000000000, 'field': 'Fintech', 'achievement': 'Stripe Co-Founder'},
            
            # Short first names
            {'first_name': 'Satya', 'last_name': 'Nadella', 'full_name': 'Satya Nadella', 'net_worth': 800000000, 'field': 'Tech', 'achievement': 'Microsoft CEO'},
            {'first_name': 'Sundar', 'last_name': 'Pichai', 'full_name': 'Sundar Pichai', 'net_worth': 600000000, 'field': 'Tech', 'achievement': 'Google CEO'},
            {'first_name': 'Evan', 'last_name': 'Spiegel', 'full_name': 'Evan Spiegel', 'net_worth': 3000000000, 'field': 'Tech/Social', 'achievement': 'Snap CEO'},
            {'first_name': 'Bobby', 'last_name': 'Murphy', 'full_name': 'Bobby Murphy', 'net_worth': 3000000000, 'field': 'Tech/Social', 'achievement': 'Snap Co-Founder'},
            
            # Various name patterns
            {'first_name': 'Jamie', 'last_name': 'Dimon', 'full_name': 'Jamie Dimon', 'net_worth': 2000000000, 'field': 'Finance', 'achievement': 'JPMorgan CEO'},
            {'first_name': 'Mary', 'last_name': 'Barra', 'full_name': 'Mary Barra', 'net_worth': 100000000, 'field': 'Auto', 'achievement': 'GM CEO'},
            {'first_name': 'Ginni', 'last_name': 'Rometty', 'full_name': 'Ginni Rometty', 'net_worth': 100000000, 'field': 'Tech', 'achievement': 'IBM CEO'},
            {'first_name': 'Safra', 'last_name': 'Catz', 'full_name': 'Safra Catz', 'net_worth': 1200000000, 'field': 'Tech', 'achievement': 'Oracle CEO'},
            {'first_name': 'Susan', 'last_name': 'Wojcicki', 'full_name': 'Susan Wojcicki', 'net_worth': 800000000, 'field': 'Tech', 'achievement': 'YouTube CEO'},
            {'first_name': 'Sheryl', 'last_name': 'Sandberg', 'full_name': 'Sheryl Sandberg', 'net_worth': 1700000000, 'field': 'Tech', 'achievement': 'Meta COO'}
        ]
        
        return successful_people

