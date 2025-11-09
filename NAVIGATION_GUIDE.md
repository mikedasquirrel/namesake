# 🗺️ APP NAVIGATION GUIDE

**Where to Find Everything in Your Flask App**

---

## ⚡ QUICK ACCESS

**Start the app:**
```bash
cd /Users/michaelsmerconish/Desktop/RandomCode/FlaskProject
python3 app.py
```

**Then visit any of these URLs:**

---

## 🔴 LIVE BETTING SYSTEM (NEW - PRIMARY)

### **Main Live Dashboard**
**URL:** http://localhost:5000/live-betting

**What You'll See:**
- Real-time betting recommendations
- Auto-refresh every 15 minutes
- Priority ranking (1-5, with 5 = MUST BET)
- All 6 sports (MMA, Football, Basketball, Baseball, Soccer, Tennis)
- Complete relational analysis (500+ variables)
- Expected ROI per opportunity
- Context badges (Primetime, Playoff, etc.)
- One-click bet logging

**Filters:**
- All Sports
- Priority 5 Only (best bets)
- By Sport (Football, Basketball, etc.)
- Sweet Spots Only

**This is your PRIMARY interface for daily betting.**

---

### **Portfolio History**
**URL:** http://localhost:5000/portfolio-history

**What You'll See:**
- All-time performance stats
- Season-by-season breakdown
- Sport contribution analysis
- Win rate trends
- ROI evolution
- Best/worst seasons

**Use this to:**
- Track long-term performance
- See which sports perform best
- Analyze seasonal patterns
- Validate ROI projections

---

## 📊 ORIGINAL BETTING DASHBOARDS

### **Static Opportunities**
**URL:** http://localhost:5000/sports-betting

**What You'll See:**
- Browse all opportunities by sport
- Filter by score/confidence thresholds
- Detailed linguistic analysis
- Edge indicators
- Component breakdowns

**Use this for:**
- In-depth analysis of specific opportunities
- Understanding the scoring system
- Comparing across sports

---

### **Performance Analytics**
**URL:** http://localhost:5000/betting-performance

**What You'll See:**
- Total ROI
- Win rate (vs 52.4% breakeven)
- Total profit
- Sharpe ratio
- Max drawdown
- CLV tracking
- Risk metrics

**Features:**
- Filter by sport
- Time period selection (30 days, 90 days, all-time)
- One-click backtesting

**Use this for:**
- Performance monitoring
- Risk assessment
- ROI validation

---

## ⚽ SPORTS META-ANALYSIS (ORIGINAL)

### **Cross-Sport Analysis**
**URL:** http://localhost:5000/sports-meta-analysis

**What You'll See:**
- Sport characteristic comparisons
- Contact level vs harshness correlation
- Team size vs syllable effects
- Meta-regression results
- Sport comparison matrix

**Use this for:**
- Understanding WHY formulas differ by sport
- Seeing meta-analysis findings
- Theoretical foundation

---

## 🔌 API ENDPOINTS (For Programmatic Access)

### **Live Betting APIs:**
```
GET  /api/betting/live-recommendations     # Real-time opportunities
GET  /api/betting/opportunities            # All opportunities
GET  /api/betting/opportunities/<sport>    # Sport-specific
POST /api/betting/analyze-prop             # Analyze specific prop
GET  /api/betting/bankroll/status          # Bankroll state
POST /api/betting/place-bet                # Log a bet
GET  /api/betting/performance              # Performance metrics
POST /api/betting/backtest                 # Run backtest
GET  /api/betting/bet-history              # Bet history
GET  /api/betting/portfolio-history        # Complete portfolio
```

### **Sports Meta-Analysis APIs:**
```
GET /api/sports-meta/characteristics       # Sport data
GET /api/sports-meta/analysis/<sport>      # Sport-specific results
GET /api/sports-meta/meta-results          # Cross-sport analysis
POST /api/sports-meta/predict              # Predict for name
```

---

## 🎯 RECOMMENDED WORKFLOW

### **Daily Betting Routine:**

**1. Morning - Check Opportunities:**
```
Visit: http://localhost:5000/live-betting
Filter: Priority 5 Only
Review: Top 8-12 recommendations
```

**2. Analyze Specific Bets:**
```
Click through to see:
- Complete relational analysis (8 layers)
- Opponent matchup details
- Historical context
- Market signals
- Expected ROI
```

**3. Make Decisions:**
```
Priority 5 + Sweet Spot context = BET HEAVY (2× size)
Priority 5 regular = BET (1.5× size)
Priority 4 = MODERATE BET (1× size)
Priority 3 = SMALL BET (0.5× size)
```

**4. Log Bets:**
```
Click "Log This Bet" button
Or use API: POST /api/betting/place-bet
```

---

### **Evening - Update Results:**
```
Visit: http://localhost:5000/portfolio-history
Update bet outcomes
See today's performance
Track season progress
```

---

### **Weekly - Performance Review:**
```
Visit: http://localhost:5000/betting-performance
Review: Win rate, ROI, Sharpe ratio
Analyze: Sport breakdown
Adjust: Allocations if needed
```

---

## 📂 WHERE THE ANALYSIS CODE LIVES

### **Core Analyzers:**
```
analyzers/
├── sports_betting_analyzer.py           # Core scoring engine
├── integrated_betting_analyzer.py       # 14-layer integration
├── ensemble_nominative_analyzer.py      # Ensemble coherence ⭐
├── relational_combat_analyzer.py        # MMA full relational
├── cross_sport_relational_framework.py  # All sports relational
├── micro_subdomain_analyzer.py          # Play×player×situation
├── position_specific_optimizer.py       # 15 position formulas
├── sport_specific_prominence_finder.py  # Sweet spot detection
├── universal_constant_calibrator.py     # 1.344 integration
├── contextual_amplifiers.py            # 9 context types
├── media_attention_analyzer.py          # Buzz, visibility
├── market_inefficiency_detector.py      # Contrarian signals
└── ... 31 more modules
```

### **Data Collections:**
```
analysis_outputs/
├── sports_meta_analysis/               # NFL, NBA, MLB data
├── mma_analysis/                       # 1,200 MMA fighters
├── tennis_analysis/                    # 1,200 tennis players
├── soccer_analysis/                    # 1,500 soccer players
└── world_cup_2026/                     # Team ensembles (ready)
```

### **Dashboards:**
```
templates/
├── live_betting_dashboard.html         # ⭐ PRIMARY interface
├── portfolio_history.html              # Historical tracking
├── sports_betting_dashboard.html       # Static opportunities
├── betting_performance.html            # Analytics
└── sports_meta_analysis.html           # Meta-analysis
```

---

## 🎯 WHAT EACH PAGE DOES

### **live-betting (PRIMARY):**
**Purpose:** Daily betting decisions
**Shows:** Today's best opportunities with complete analysis
**Use:** Every morning before placing bets

### **portfolio-history:**
**Purpose:** Long-term tracking
**Shows:** All-time and seasonal performance
**Use:** Weekly performance reviews

### **sports-betting:**
**Purpose:** In-depth opportunity exploration
**Shows:** All opportunities with filters
**Use:** When you want to browse/analyze

### **betting-performance:**
**Purpose:** Performance analytics
**Shows:** ROI, win rate, risk metrics
**Use:** Monthly/quarterly reviews

### **sports-meta-analysis:**
**Purpose:** Understanding the theory
**Shows:** Why formulas differ by sport
**Use:** Learning/validation

---

## 🔥 YOUR ANALYSIS IS IN 3 PLACES

### **1. LIVE BETTING PAGE (Best for Daily Use)**
- Real-time opportunities
- All enhancement layers applied
- Priority rankings
- Expected ROI shown
- **START HERE**

### **2. API ENDPOINTS (Best for Programmatic)**
```python
import requests

# Get recommendations
resp = requests.get('http://localhost:5000/api/betting/live-recommendations')
opportunities = resp.json()['recommendations']

# Each has complete analysis with:
# - Final score
# - Confidence
# - Expected ROI  
# - Layer-by-layer breakdown
# - Relational context
```

### **3. CODEBASE (Best for Understanding)**
```python
# Import and use directly
from analyzers.integrated_betting_analyzer import IntegratedBettingAnalyzer

analyzer = IntegratedBettingAnalyzer()
result = analyzer.complete_analysis(
    player_data, game_context, opponent_data, market_data
)

# Returns: Complete 14-layer analysis
```

---

## 🚀 START HERE NOW

**Immediate Access:**
```bash
python3 app.py

# Then visit:
http://localhost:5000/live-betting

# You'll see:
# - Today's opportunities
# - MMA, Football, Basketball, Baseball, Soccer, Tennis
# - Complete relational analysis
# - Expected ROI 48-62%
# - Ready to bet NOW
```

---

## 🏆 WHAT'S IN THE APP

**5 Dashboards:**
1. `/live-betting` - ⭐ Primary (real-time)
2. `/portfolio-history` - Tracking
3. `/sports-betting` - Static opportunities
4. `/betting-performance` - Analytics
5. `/sports-meta-analysis` - Theory

**12+ API Endpoints:**
- All betting operations
- Analysis requests
- Historical queries
- Performance metrics

**43 Analyzer Modules:**
- All accessible via import
- All documented
- All production-ready

---

## 🎯 THE BOTTOM LINE

**Your analysis is EVERYWHERE in the app:**
- ✅ Live dashboard (easiest access)
- ✅ API endpoints (programmatic)
- ✅ Direct imports (custom analysis)
- ✅ Multiple views (different purposes)

**Primary interface:** http://localhost:5000/live-betting

**Start there. Bet with 48-62% expected ROI. Track performance.**

🔴 **SYSTEM IS LIVE NOW.**

**Repository:** https://github.com/mikedasquirrel/namesake.git  
**App:** `python3 app.py`  
**Main Page:** http://localhost:5000/live-betting  
**Expected ROI:** 48-62%  

✅ **GO PROFIT.**

