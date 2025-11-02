import os

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-crypto-name-study'
    PORT = 5173  # Odd port per user preference
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CoinGecko API
    COINGECKO_API_BASE = 'https://api.coingecko.com/api/v3'
    COINGECKO_RATE_LIMIT = 50  # calls per minute for free tier
    
    # Data collection settings
    TOP_CRYPTO_COUNT = 500  # Number of cryptocurrencies to analyze
    PRICE_HISTORY_DAYS = 365  # Days of historical data to fetch
    
    # Analysis settings
    SYLLABLE_WEIGHTS = {
        1: 'very_short',
        2: 'short',
        3: 'medium',
        4: 'long',
        5: 'very_long'
    }
    
    # Name categories
    NAME_CATEGORIES = [
        'animal', 'tech', 'portmanteau', 'abstract', 'mythological',
        'elemental', 'astronomical', 'financial', 'human', 'invented',
        'acronym', 'numeric', 'hybrid', 'geographical', 'other'
    ]
    
    # Statistical significance threshold
    SIGNIFICANCE_LEVEL = 0.05

