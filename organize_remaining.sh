#!/bin/bash

echo "📚 Organizing remaining documentation..."

# Move remaining domain folders
mv docs/01_CRYPTO_ANALYSIS/* docs_organized/03_DOMAINS/Crypto/ 2>/dev/null || true
mv docs/06_NBA_ANALYSIS/* docs_organized/03_DOMAINS/NBA/ 2>/dev/null || true
mv docs/07_ACADEMIC_ANALYSIS/* docs_organized/03_DOMAINS/Academics/ 2>/dev/null || true
mv docs/08_SHIP_ANALYSIS/* docs_organized/03_DOMAINS/Ships/ 2>/dev/null || true
mv docs/11_NFL_ANALYSIS/* docs_organized/03_DOMAINS/NFL/ 2>/dev/null || true
mv docs/15_MENTAL_HEALTH_ANALYSIS/* docs_organized/03_DOMAINS/Mental_Health/ 2>/dev/null || true

# Africa funding
mv docs/AFRICA_FUNDING_LINGUISTICS_COMPLETE.md docs_organized/03_DOMAINS/Investment/ 2>/dev/null || true

# Cross-sphere theory
mv docs/04_CROSS_SPHERE_THEORY/* docs_organized/04_THEORY/ 2>/dev/null || true

# Hurricane analysis
mv docs/02_HURRICANE_ANALYSIS/* docs_organized/03_DOMAINS/Hurricanes/ 2>/dev/null || true

# Earthquakes
mv docs/09_EARTHQUAKE_ANALYSIS/* docs_organized/03_DOMAINS/Earthquakes/ 2>/dev/null || true

# FEMA
mv docs/13_FEMA_ANALYSIS/* docs_organized/03_DOMAINS/FEMA/ 2>/dev/null || true

# Film analysis
mv docs/05_FILM_ANALYSIS/* docs_organized/03_DOMAINS/Films/ 2>/dev/null || true

# Read me first
mv docs/00_READ_ME_FIRST.md docs_organized/01_START_HERE/ 2>/dev/null || true

# Any remaining papers
mv papers/* docs_organized/04_THEORY/papers/ 2>/dev/null || true

# Project status - keep in root but copy to START_HERE
cp PROJECT_STATUS.md docs_organized/01_START_HERE/ 2>/dev/null || true

# README.md - keep in root

# Create directory structure report
mkdir -p docs_organized/03_DOMAINS/Academics

echo "✅ Remaining files organized!"
