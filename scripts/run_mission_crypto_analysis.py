#!/usr/bin/env python3
"""Mission-aligned cryptocurrency analysis pipeline.

This script bootstraps the Flask application, loads the fully assembled
cryptocurrency dataset, enriches it with mission-centric derived fields,
and runs a multi-method statistical analytics suite. It persists structured
outputs (CSV + JSON) for downstream reporting.

Usage::

    python scripts/run_mission_crypto_analysis.py

Outputs are written to ``analysis_outputs/mission_run_<timestamp>/``.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Set

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Bootstrap application context
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app as flask_app, stats_analyzer  # noqa: E402
from utils.advanced_statistics import AdvancedStatisticalAnalyzer  # noqa: E402


logger = logging.getLogger("mission_crypto_analysis")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_output_dir() -> Path:
    """Create a timestamped output directory for the current run."""

    root_dir = PROJECT_ROOT / "analysis_outputs"
    root_dir.mkdir(parents=True, exist_ok=True)

    run_dir = root_dir / f"mission_run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def enrich_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Add mission-relevant derived features to the base dataset."""

    enriched = df.copy()

    # Normalize numeric fields and protect against missing data
    numeric_cols = [
        "price_1yr_change",
        "price_90d_change",
        "price_30d_change",
        "market_cap",
        "memorability_score",
        "pronounceability_score",
        "uniqueness_score",
        "phonetic_score",
        "vowel_ratio",
        "syllable_count",
        "character_length",
    ]
    for col in numeric_cols:
        if col in enriched.columns:
            enriched[col] = pd.to_numeric(enriched[col], errors="coerce")

    enriched["price_1yr_change"].fillna(0, inplace=True)

    # Composite linguistic strength (aligned with nominative determinism mission)
    enriched["linguistic_composite"] = (
        enriched[[
            "memorability_score",
            "pronounceability_score",
            "uniqueness_score",
            "phonetic_score",
        ]]
        .mean(axis=1, skipna=True)
        .fillna(0)
    )

    # Performance tiers
    enriched["is_mission_positive"] = enriched["price_1yr_change"] > 0
    enriched["is_high_performer"] = enriched["price_1yr_change"] >= 150
    enriched["is_breakout"] = enriched["price_1yr_change"] >= 300

    # Rank-based tiers reflecting market position
    def rank_tier(rank: Any) -> str:
        if pd.isna(rank):
            return "unranked"
        rank = int(rank)
        if rank <= 50:
            return "vanguard"
        if rank <= 200:
            return "established"
        if rank <= 500:
            return "mid_cap"
        if rank <= 1000:
            return "emergent"
        return "long_tail"

    enriched["rank_tier"] = enriched["rank"].apply(rank_tier)

    # Linguistic sweet spot flag based on validated patterns (2-3 syllables, optimal length)
    enriched["in_linguistic_sweet_spot"] = (
        enriched["syllable_count"].between(2, 3, inclusive="both")
        & enriched["character_length"].between(5, 10, inclusive="both")
    )

    # Mission resonance score (scaled 0-100)
    comp = enriched["linguistic_composite"].clip(lower=0)
    enriched["mission_resonance_score"] = (
        0.5 * comp.rank(pct=True) * 100
        + 0.3 * enriched["price_1yr_change"].rank(pct=True) * 100
        + 0.2 * (~pd.isna(enriched["name_type"])).astype(int) * 100
    ).round(2)

    return enriched


def compute_descriptive_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate executive-level descriptive statistics."""

    coverage = df["rank_tier"].value_counts(dropna=False).to_dict()
    performance = {
        "avg_return": round(float(df["price_1yr_change"].mean()), 2),
        "median_return": round(float(df["price_1yr_change"].median()), 2),
        "high_performer_rate": round(float(df["is_high_performer"].mean() * 100), 1),
        "breakout_rate": round(float(df["is_breakout"].mean() * 100), 1),
        "positive_return_rate": round(float(df["is_mission_positive"].mean() * 100), 1),
    }

    sweet_spot = df[df["in_linguistic_sweet_spot"]]
    sweet_spot_perf = (
        sweet_spot["price_1yr_change"].mean() if not sweet_spot.empty else np.nan
    )

    linguistic = {
        "composite_mean": round(float(df["linguistic_composite"].mean()), 2),
        "composite_std": round(float(df["linguistic_composite"].std()), 2),
        "sweet_spot_avg_return": None
        if np.isnan(sweet_spot_perf)
        else round(float(sweet_spot_perf), 2),
        "sweet_spot_size": int(len(sweet_spot)),
    }

    mission_corr = df[["linguistic_composite", "price_1yr_change"]].dropna()
    corr_value = (
        float(mission_corr.corr().iloc[0, 1])
        if not mission_corr.empty
        else 0.0
    )

    return {
        "sample_size": int(len(df)),
        "rank_tier_distribution": coverage,
        "performance": performance,
        "linguistic": linguistic,
        "linguistic_performance_correlation": round(corr_value, 4),
    }


def run_multi_method_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute the advanced analytics suite."""

    analyzer = AdvancedStatisticalAnalyzer()

    interaction_effects = analyzer.find_interaction_effects(df)
    non_linear_patterns = analyzer.detect_nonlinear_patterns(df)
    clustering = analyzer.cluster_analysis(df)

    causal_features = []
    for feature in ["memorability_score", "uniqueness_score", "phonetic_score"]:
        result = analyzer.causal_analysis(df, treatment_feature=feature)
        if "error" not in result:
            causal_features.append(result)

    comprehensive_report = analyzer.generate_comprehensive_report(df)
    slim_report = {
        "generated_at": comprehensive_report.get("generated_at"),
        "sample_size": comprehensive_report.get("sample_size"),
        "executive_summary": comprehensive_report.get("executive_summary"),
    }

    return {
        "interaction_effects": interaction_effects,
        "non_linear_patterns": non_linear_patterns,
        "clustering": clustering,
        "causal_effects": causal_features,
        "comprehensive_report": slim_report,
    }


def collect_classic_statistics() -> Dict[str, Any]:
    """Run baseline statistical routines from the core analyzer."""

    with flask_app.app_context():
        return {
            "correlations": stats_analyzer.correlation_analysis("price_1yr_change"),
            "regression": stats_analyzer.regression_analysis("price_1yr_change"),
            "name_type_comparison": stats_analyzer.name_type_comparison("price_1yr_change"),
            "syllable_analysis": stats_analyzer.syllable_analysis("price_1yr_change"),
            "length_analysis": stats_analyzer.length_analysis("price_1yr_change"),
        }


def to_serializable(obj: Any) -> Any:
    """Safely convert NumPy / pandas objects to plain Python types for JSON."""

    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    return obj


def sanitize_for_json(obj: Any, _visited: Set[int] | None = None) -> Any:
    """Deep-convert objects to JSON-safe structures while avoiding cycles."""

    if _visited is None:
        _visited = set()

    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    obj_id = id(obj)
    if obj_id in _visited:
        return "<circular>"
    _visited.add(obj_id)

    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v, _visited) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v, _visited) for v in obj]
    if isinstance(obj, pd.DataFrame):
        return sanitize_for_json(obj.to_dict(orient="records"), _visited)
    if isinstance(obj, (pd.Series, pd.Index)):
        return sanitize_for_json(obj.tolist(), _visited)
    if isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist(), _visited)

    return to_serializable(obj)


def main() -> None:
    configure_logging()
    logger.info("Starting mission-aligned crypto analytics run")

    with flask_app.app_context():
        base_df = stats_analyzer.get_dataset()

    if base_df.empty:
        logger.error("Dataset is empty. Aborting analysis run.")
        sys.exit(1)

    logger.info("Dataset loaded: %s rows", len(base_df))
    enriched_df = enrich_dataset(base_df)
    logger.info("Dataset enriched with mission features")

    descriptive = compute_descriptive_summary(enriched_df)
    logger.info("Descriptive summary computed")

    classic_stats = sanitize_for_json(collect_classic_statistics())
    logger.info("Baseline statistical routines completed")

    advanced_stats = sanitize_for_json(run_multi_method_analytics(enriched_df))
    logger.info("Advanced statistical suite completed")

    output_dir = ensure_output_dir()

    dataset_path = output_dir / "mission_dataset_enriched.csv"
    enriched_df.to_csv(dataset_path, index=False)
    logger.info("Enriched dataset exported to %s", dataset_path)

    results = {
        "generated_at": datetime.utcnow().isoformat(),
        "descriptive_summary": descriptive,
        "classic_statistics": classic_stats,
        "advanced_statistics": advanced_stats,
    }

    # Validate JSON serialization per section to surface issues early
    for section, payload in results.items():
        try:
            json.dumps(payload, default=to_serializable)
        except Exception as exc:  # pragma: no cover - diagnostics
            logger.error("Serialization failed for section '%s': %s", section, exc)
            raise

    results_path = output_dir / "mission_analysis_results.json"
    with results_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, default=to_serializable)
    logger.info("Structured mission analytics saved to %s", results_path)

    logger.info("Mission-aligned crypto analytics run complete")


if __name__ == "__main__":
    main()


