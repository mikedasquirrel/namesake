#!/bin/bash

# Organization script for 290+ markdown files
# Creates clean hierarchical structure

echo "📚 Organizing Documentation..."

# Create full structure
mkdir -p docs_organized/{01_START_HERE,02_DISCOVERIES,03_DOMAINS,04_THEORY,05_SESSIONS,06_ARTWORK,07_IMPLEMENTATION,08_ANALYSIS_OUTPUTS,09_ARCHIVE}
mkdir -p docs_organized/03_DOMAINS/{Crypto,Hurricanes,Elections,NBA,NFL,MLB,Ships,Mental_Health,Adult_Film,Board_Games,Bands,Immigration,Investment,MTG,FEMA,Earthquakes}
mkdir -p docs_organized/06_ARTWORK/{The_Nail,The_Heart}

# 01_START_HERE - Entry points
echo "→ Organizing START_HERE..."
mv START_HERE.md docs_organized/01_START_HERE/ 2>/dev/null || true
mv PROJECT_INDEX.md docs_organized/01_START_HERE/ 2>/dev/null || true
mv README_NAVIGATION.md docs_organized/01_START_HERE/ 2>/dev/null || true
mv COMMANDS_CHEAT_SHEET.md docs_organized/01_START_HERE/ 2>/dev/null || true
mv CURRENT_STATUS.md docs_organized/01_START_HERE/ 2>/dev/null || true
mv QUICK_START.md docs_organized/01_START_HERE/ 2>/dev/null || true
mv docs/guides/QUICK_START.md docs_organized/01_START_HERE/QUICK_START_GUIDE.md 2>/dev/null || true

# 02_DISCOVERIES - Major findings
echo "→ Organizing DISCOVERIES..."
mv CONSTANTS_SIMPLE_EXPLANATION.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv CONSTANTS_AS_GRAVITY.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv COMPREHENSIVE_DOMAIN_RANKING.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv THE_DISCOVERER_STATISTICAL_PROOF.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv MICHAEL_SMERCONISH_COMPLETE_ANALYSIS.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv DISCOVERER_SIGNATURE_VALIDATED.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv PREDICTED_DISCOVERER_PROFILE.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv THE_PATTERN_RECOGNITION.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv COMPLETE_NOMINATIVE_PROFILE_TEST.md docs_organized/02_DISCOVERIES/ 2>/dev/null || true

# 03_DOMAINS - Domain analyses
echo "→ Organizing DOMAINS..."
# Adult Film
mv ADULT_FILM_*.md docs_organized/03_DOMAINS/Adult_Film/ 2>/dev/null || true
mv docs/20_ADULT_FILM_ANALYSIS/* docs_organized/03_DOMAINS/Adult_Film/ 2>/dev/null || true

# MLB
mv MLB_*.md docs_organized/03_DOMAINS/MLB/ 2>/dev/null || true
mv docs/19_MLB_ANALYSIS/* docs_organized/03_DOMAINS/MLB/ 2>/dev/null || true
mv docs/20_MLB_TEAMS_ANALYSIS/* docs_organized/03_DOMAINS/MLB/ 2>/dev/null || true

# Board Games
mv docs/18_BOARD_GAMES_ANALYSIS/* docs_organized/03_DOMAINS/Board_Games/ 2>/dev/null || true

# Elections
mv docs/12_ELECTION_ANALYSIS/* docs_organized/03_DOMAINS/Elections/ 2>/dev/null || true

# Band Members
mv docs/14_BAND_MEMBERS_ANALYSIS/* docs_organized/03_DOMAINS/Bands/ 2>/dev/null || true

# Immigration
mv docs/10_IMMIGRATION_ANALYSIS/* docs_organized/03_DOMAINS/Immigration/ 2>/dev/null || true

# Investment
mv docs/17_INVESTMENT_INTELLIGENCE/* docs_organized/03_DOMAINS/Investment/ 2>/dev/null || true
mv INVESTMENT_*.md docs_organized/03_DOMAINS/Investment/ 2>/dev/null || true
mv COMPREHENSIVE_INVESTMENT_INTELLIGENCE_ANALYSIS.md docs_organized/03_DOMAINS/Investment/ 2>/dev/null || true

# MTG
mv docs/03_MTG_ANALYSIS/* docs_organized/03_DOMAINS/MTG/ 2>/dev/null || true

# 04_THEORY - Theoretical frameworks
echo "→ Organizing THEORY..."
mv docs/theory/* docs_organized/04_THEORY/ 2>/dev/null || true
mv docs/NAME_ECONOMY_FRAMEWORK.md docs_organized/04_THEORY/ 2>/dev/null || true
mv docs/PHONETIC_METHODS_HANDBOOK.md docs_organized/04_THEORY/ 2>/dev/null || true

# 05_SESSIONS - Session logs
echo "→ Organizing SESSIONS..."
mv SESSION_*.md docs_organized/05_SESSIONS/ 2>/dev/null || true
mv COMPLETE_SESSION_*.md docs_organized/05_SESSIONS/ 2>/dev/null || true

# 06_ARTWORK - Visual works
echo "→ Organizing ARTWORK..."
mv THE_NAIL_*.md docs_organized/06_ARTWORK/The_Nail/ 2>/dev/null || true
mv START_HERE_THE_NAIL.md docs_organized/06_ARTWORK/The_Nail/ 2>/dev/null || true
mv figures/the_nail/*.md docs_organized/06_ARTWORK/The_Nail/ 2>/dev/null || true
mv THE_HEART_*.md docs_organized/06_ARTWORK/The_Heart/ 2>/dev/null || true
mv VISUAL_INTEGRATION_COMPLETE.md docs_organized/06_ARTWORK/ 2>/dev/null || true

# 07_IMPLEMENTATION - Technical docs
echo "→ Organizing IMPLEMENTATION..."
mv FORMULA_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv docs/core/FORMULA_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv DOMAIN_EXPANSION_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv DOMAIN_SPECIFIC_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv DOMAIN_EXTENSIONS_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv docs/implementation/* docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv docs/core/SYSTEM_OPERATIONAL.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv docs/16_FRAMEWORK/* docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true

# Status files
mv FINAL_COMPLETE_SYSTEM.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv COMPLETE_IMPLEMENTATION_SUMMARY.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv IMPLEMENTATION_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv LAUNCH_READY.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv PRESENTATION_COMPLETE.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv READY_FOR_PRESENTATION.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true

# Shocking domains
mv SHOCKING_DOMAINS_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv MASTER_SHOCKING_DOMAINS_LIST.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true

# Testing
mv RIGOROUS_TESTING_*.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv FINAL_RIGOROUS_TEST.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true

# Polish/deployment
mv README_FORMULA_POLISH.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv PYTHONANYWHERE_DEPLOYMENT.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv PAGE_CONTENT_CHECKLIST.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true

# 08_ANALYSIS_OUTPUTS
echo "→ Organizing ANALYSIS_OUTPUTS..."
mv analysis_outputs/africa_funding/*.md docs_organized/08_ANALYSIS_OUTPUTS/ 2>/dev/null || true

# 09_ARCHIVE - Old/deprecated
echo "→ Organizing ARCHIVE..."
mv docs/archive/* docs_organized/09_ARCHIVE/ 2>/dev/null || true
mv docs/study_designs/* docs_organized/09_ARCHIVE/study_designs/ 2>/dev/null || true
mv DATA_COLLECTION_QUESTIONNAIRE.md docs_organized/09_ARCHIVE/ 2>/dev/null || true
mv DOCUMENTATION_INDEX.md docs_organized/09_ARCHIVE/ 2>/dev/null || true

# Misc docs
mv docs/COMPLETE_DOMAIN_COVERAGE_VERIFICATION.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv docs/core/WHAT_DATA_IS_COLLECTED.md docs_organized/07_IMPLEMENTATION/ 2>/dev/null || true
mv docs/discoveries/* docs_organized/02_DISCOVERIES/ 2>/dev/null || true
mv docs/warnings/* docs_organized/01_START_HERE/ 2>/dev/null || true

echo "✅ Documentation organized!"
echo ""
echo "Structure:"
echo "  docs_organized/"
echo "    01_START_HERE/     - Entry points & navigation"
echo "    02_DISCOVERIES/    - Major findings & constants"
echo "    03_DOMAINS/        - Domain-specific analyses"
echo "    04_THEORY/         - Theoretical frameworks"
echo "    05_SESSIONS/       - Research progress logs"
echo "    06_ARTWORK/        - Visual & artistic works"
echo "    07_IMPLEMENTATION/ - Technical documentation"
echo "    08_ANALYSIS_OUTPUTS/ - Reports & results"
echo "    09_ARCHIVE/        - Historical documents"
echo ""
echo "📚 See MASTER_DOCUMENTATION_INDEX.md for complete guide"
