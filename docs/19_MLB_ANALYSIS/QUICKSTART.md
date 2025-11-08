# MLB Analysis - Quick Start

## Step 1: Bootstrap Data

```bash
python3 scripts/bootstrap_mlb.py
```

This populates 50-60 famous players for immediate visualization.

## Step 2: View Dashboard

Navigate to: http://localhost:5000/mlb

## Step 3: View Findings

Navigate to: http://localhost:5000/mlb/findings

## Step 4: Access APIs

```bash
curl http://localhost:5000/api/mlb/stats
curl http://localhost:5000/api/mlb/position-analysis
curl http://localhost:5000/api/mlb/pitcher-analysis
curl http://localhost:5000/api/mlb/power-analysis
```

---

## For Full Collection (2,500+ players)

Create and run comprehensive collection script when Baseball Reference access is available.

---

**Estimated Time:** 5 minutes for bootstrap, instant for viewing

