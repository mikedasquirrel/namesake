"""Run default regressively proven claims and persist results.

This script bootstraps the Flask application context, executes the configured
claims via the ``RegressiveProofEngine``, and stores structured outputs inside
``analysis_outputs/regressive_proof/<timestamp>``.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on the import path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app  # noqa: E402,F401  # Import ensures Flask context availability
from analyzers.regressive_proof import DEFAULT_CLAIMS, RegressiveProofEngine


def main() -> None:
    engine = RegressiveProofEngine()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_dir = engine.base_output_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    with app.app_context():
        for claim in DEFAULT_CLAIMS:
            result = engine.run_claim(claim, persist=True, output_dir=output_dir)
            summary.append(
                {
                    "claim_id": result["claim"]["claim_id"],
                    "status": result["status"],
                    "sample_size": result["sample_size"],
                    "primary_metric": result["model_summary"].get("primary_metric"),
                    "model_metrics": {
                        "r_squared": result["model_summary"].get("r_squared"),
                        "pseudo_r_squared": result["model_summary"].get("pseudo_r_squared"),
                        "accuracy": result["model_summary"].get("accuracy"),
                        "cross_validation": result["model_summary"].get("cross_validation"),
                    },
                    "warnings": result.get("warnings", []),
                }
            )

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Regressive proof run complete. Results stored in {output_dir.resolve()}")


if __name__ == "__main__":
    main()
