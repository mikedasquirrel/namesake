#!/usr/bin/env python3
"""
Master Bootstrap Script
Populates ALL 6 spheres with real data
Run once, data persists forever
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from core.config import Config
from core.models import db, Cryptocurrency, Domain, Stock, Film, Book, Person
from core.models import StockAnalysis, FilmAnalysis, BookAnalysis, PersonAnalysis
from collectors.stock_collector import StockCollector
from collectors.film_collector import FilmCollector  
from collectors.book_collector import BookCollector
from collectors.people_collector import PeopleCollector
from analyzers.name_analyzer import NameAnalyzer
import json


def populate_stocks():
    """Load stock data"""
    print("\n📊 Loading Stocks...")
    
    # Check if stock JSON exists from background collection
    stock_file = 'instance/stocks_data.json'
    if os.path.exists(stock_file):
        with open(stock_file, 'r') as f:
            stocks_data = json.load(f)
        print(f"   Found {len(stocks_data)} stocks from file")
    else:
        collector = StockCollector()
        stocks_data = collector.collect_all_stocks()
    
    analyzer = NameAnalyzer()
    all_names = [s['company_name'] for s in stocks_data]
    
    count = 0
    for stock_data in stocks_data:
        existing = Stock.query.filter_by(ticker=stock_data['ticker']).first()
        if existing:
            continue
        
        stock = Stock(
            ticker=stock_data['ticker'],
            company_name=stock_data['company_name'],
            sector=stock_data.get('sector'),
            industry=stock_data.get('industry'),
            market_cap=stock_data.get('market_cap'),
            current_price=stock_data.get('current_price'),
            return_1yr=stock_data.get('return_1yr'),
            return_5yr=stock_data.get('return_5yr'),
            founded_year=stock_data.get('founded_year')
        )
        
        db.session.add(stock)
        db.session.flush()
        
        # Analyze company name
        analysis_results = analyzer.analyze_name(stock_data['company_name'], all_names)
        
        stock_analysis = StockAnalysis(
            stock_id=stock.id,
            syllable_count=analysis_results.get('syllable_count'),
            character_length=analysis_results.get('character_length'),
            memorability_score=analysis_results.get('memorability_score'),
            uniqueness_score=analysis_results.get('uniqueness_score'),
            name_type=analysis_results.get('name_type'),
            ticker_length=len(stock_data['ticker'])
        )
        
        db.session.add(stock_analysis)
        count += 1
        
        if count % 50 == 0:
            db.session.commit()
    
    db.session.commit()
    print(f"   ✅ Loaded {count} stocks")
    return count


def populate_films():
    """Load film data"""
    print("\n🎬 Loading Films...")
    
    collector = FilmCollector()
    films_data = collector.get_bootstrap_data()
    
    analyzer = NameAnalyzer()
    all_names = [f['title'] for f in films_data]
    
    count = 0
    for film_data in films_data:
        film = Film(
            title=film_data['title'],
            year=film_data['year'],
            revenue=film_data['revenue'],
            budget=film_data['budget'],
            roi=film_data['roi'],
            rating=film_data.get('rating'),
            genre=film_data.get('genres', ['Unknown'])[0] if isinstance(film_data.get('genres'), list) else film_data.get('genre', 'Unknown')
        )
        
        db.session.add(film)
        db.session.flush()
        
        # Analyze title
        analysis_results = analyzer.analyze_name(film_data['title'], all_names)
        
        film_analysis = FilmAnalysis(
            film_id=film.id,
            syllable_count=analysis_results.get('syllable_count'),
            character_length=analysis_results.get('character_length'),
            word_count=analysis_results.get('word_count'),
            memorability_score=analysis_results.get('memorability_score'),
            uniqueness_score=analysis_results.get('uniqueness_score'),
            name_type=analysis_results.get('name_type')
        )
        
        db.session.add(film_analysis)
        count += 1
    
    db.session.commit()
    print(f"   ✅ Loaded {count} films")
    return count


def populate_books():
    """Load book data"""
    print("\n📚 Loading Books...")
    
    collector = BookCollector()
    books_data = collector.get_bootstrap_data()
    
    analyzer = NameAnalyzer()
    all_names = [b['title'] for b in books_data]
    
    count = 0
    for book_data in books_data:
        book = Book(
            title=book_data['title'],
            author=book_data.get('author'),
            year=book_data['year'],
            sales_estimate=book_data['sales'],
            weeks_on_list=book_data['weeks_on_list'],
            genre=book_data['genre'],
            performance_score=book_data.get('performance_score')
        )
        
        db.session.add(book)
        db.session.flush()
        
        # Analyze title
        analysis_results = analyzer.analyze_name(book_data['title'], all_names)
        
        book_analysis = BookAnalysis(
            book_id=book.id,
            syllable_count=analysis_results.get('syllable_count'),
            character_length=analysis_results.get('character_length'),
            word_count=analysis_results.get('word_count'),
            memorability_score=analysis_results.get('memorability_score'),
            uniqueness_score=analysis_results.get('uniqueness_score'),
            name_type=analysis_results.get('name_type')
        )
        
        db.session.add(book_analysis)
        count += 1
    
    db.session.commit()
    print(f"   ✅ Loaded {count} books")
    return count


def populate_people():
    """Load people data"""
    print("\n👤 Loading People...")
    
    collector = PeopleCollector()
    people_data = collector.get_bootstrap_data()
    
    analyzer = NameAnalyzer()
    all_first = [p['first_name'] for p in people_data]
    all_last = [p['last_name'] for p in people_data]
    
    count = 0
    for person_data in people_data:
        person = Person(
            full_name=person_data['full_name'],
            first_name=person_data['first_name'],
            last_name=person_data['last_name'],
            net_worth=person_data['net_worth'],
            field=person_data['field'],
            achievement=person_data['achievement']
        )
        
        db.session.add(person)
        db.session.flush()
        
        # Analyze first name
        first_analysis = analyzer.analyze_name(person_data['first_name'], all_first)
        last_analysis = analyzer.analyze_name(person_data['last_name'], all_last)
        full_analysis = analyzer.analyze_name(person_data['full_name'], [p['full_name'] for p in people_data])
        
        person_analysis = PersonAnalysis(
            person_id=person.id,
            first_syllables=first_analysis.get('syllable_count'),
            first_length=len(person_data['first_name']),
            first_memorability=first_analysis.get('memorability_score'),
            last_syllables=last_analysis.get('syllable_count'),
            last_length=len(person_data['last_name']),
            last_memorability=last_analysis.get('memorability_score'),
            total_syllables=full_analysis.get('syllable_count'),
            total_length=full_analysis.get('character_length'),
            memorability_score=full_analysis.get('memorability_score'),
            uniqueness_score=full_analysis.get('uniqueness_score')
        )
        
        db.session.add(person_analysis)
        count += 1
    
    db.session.commit()
    print(f"   ✅ Loaded {count} people")
    return count


def main():
    """Bootstrap all spheres"""
    print("="*70)
    print("BOOTSTRAPPING ALL 6 SPHERES")
    print("="*70)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Check current status
        cryptos = Cryptocurrency.query.count()
        domains = Domain.query.count()
        stocks = Stock.query.count()
        films = Film.query.count()
        books = Book.query.count()
        people = Person.query.count()
        
        print(f"\nCurrent Database:")
        print(f"  Crypto: {cryptos}")
        print(f"  Domains: {domains}")
        print(f"  Stocks: {stocks}")
        print(f"  Films: {films}")
        print(f"  Books: {books}")
        print(f"  People: {people}")
        print(f"  TOTAL: {cryptos + domains + stocks + films + books + people}")
        
        # Populate what's missing
        if stocks == 0:
            populate_stocks()
        if films == 0:
            populate_films()
        if books == 0:
            populate_books()
        if people == 0:
            populate_people()
        
        # Final status
        total = (Cryptocurrency.query.count() + Domain.query.count() + 
                 Stock.query.count() + Film.query.count() + 
                 Book.query.count() + Person.query.count())
        
        print("\n" + "="*70)
        print("BOOTSTRAP COMPLETE")
        print("="*70)
        print(f"\nTotal Assets: {total}")
        print(f"  Cryptocurrencies: {Cryptocurrency.query.count()}")
        print(f"  Domains: {Domain.query.count()}")
        print(f"  Stocks: {Stock.query.count()}")
        print(f"  Films: {Film.query.count()}")
        print(f"  Books: {Book.query.count()}")
        print(f"  People: {Person.query.count()}")
        print("\n" + "="*70)
        print("DATABASE READY FOR MULTI-SPHERE ANALYSIS")
        print("="*70)


if __name__ == '__main__':
    main()

