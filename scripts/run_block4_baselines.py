#!/usr/bin/env python
"""Block 4: External baselines — direct-risk-score + CAAFE comparison.

Part A: Direct-risk-score baseline
  - LLM directly predicts class probability per row (no feature engineering)
  - This tests "can the LLM just classify directly without DASEF?"
  - Uses DeepSeek R1 (cheap, same model as judgment filler for fair comparison)

Part B: Raw ML baselines (re-run with matching CV config for consistency)

Part C: CAAFE-style automated feature engineering (if available/feasible)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


# --- Configuration ---
DATASETS = ["blood_transfusion", "pima_diabetes", "credit_g", "qsar_biodegradation"]
TARGET_CLASSES = {
    "blood_transfusion": "1",  # donated
    "pima_diabetes": "tested_positive",
    "credit_g": "bad",
    "qsar_biodegradation": "1",  # ready biodegradable
}
DOWNSTREAM_MODELS = "xgboost,random_forest,logistic_regression,knn"
N_SPLITS = 5
N_REPEATS = 2
SEED = 42

# Use deepseek-chat (V3) for direct risk — R1 (reasoner) puts answers in
# reasoning chain, leaving content field empty which breaks JSON parsing.
FILLER_MODEL = "deepseek-chat"
FILLER_PROVIDER = "deepseek"

OUT_DIR_RISK = Path("results/block4_direct_risk")
OUT_DIR_RAW = Path("results/block4_raw_baselines")


def run_command(cmd: list[str], label: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  CMD: {' '.join(cmd)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ FAILED (rc={result.returncode})")
        print(f"  STDERR: {result.stderr[:500]}")
        return False
    print(f"  ✓ OK")
    if result.stdout:
        # Print last 5 lines of stdout
        lines = result.stdout.strip().split("\n")
        for line in lines[-5:]:
            print(f"    {line}")
    return True


def main() -> None:
    OUT_DIR_RISK.mkdir(parents=True, exist_ok=True)
    OUT_DIR_RAW.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print(" BLOCK 4A: Direct Risk Score Baselines")
    print("=" * 60)

    for ds in DATASETS:
        target_class = TARGET_CLASSES[ds]
        out_dir = OUT_DIR_RISK / ds
        if (out_dir / "results.json").exists():
            print(f"\n  SKIP (already done): {ds}")
            continue

        run_command(
            [
                "dasef", "run-direct-risk-control",
                ds,
                "--target-class", target_class,
                "--filler-model", FILLER_MODEL,
                "--filler-provider", FILLER_PROVIDER,
                "--downstream-models", DOWNSTREAM_MODELS,
                "--n-splits", str(N_SPLITS),
                "--n-repeats", str(N_REPEATS),
                "--seed", str(SEED),
                "--out-dir", str(out_dir),
            ],
            label=f"Direct risk: {ds} (target={target_class})",
        )

    print("\n" + "=" * 60)
    print(" BLOCK 4B: Raw ML Baselines (consistent CV)")
    print("=" * 60)

    for ds in DATASETS:
        out_dir = OUT_DIR_RAW / ds
        if (out_dir / "results.json").exists():
            print(f"\n  SKIP (already done): {ds}")
            continue

        run_command(
            [
                "dasef", "run-raw-baselines",
                ds,
                "--downstream-models", DOWNSTREAM_MODELS,
                "--n-splits", str(N_SPLITS),
                "--n-repeats", str(N_REPEATS),
                "--seed", str(SEED),
                "--out-dir", str(out_dir),
            ],
            label=f"Raw baseline: {ds}",
        )

    print("\n" + "=" * 60)
    print(" BLOCK 4 COMPLETE")
    print("=" * 60)
    print(f"  Direct risk results: {OUT_DIR_RISK}")
    print(f"  Raw baselines: {OUT_DIR_RAW}")


if __name__ == "__main__":
    main()
