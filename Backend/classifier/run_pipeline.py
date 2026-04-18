"""
HealthGuide Pipeline Entry Point
Runs data preparation -> training -> optional demo in sequence.

Usage:
    python run_pipeline.py                  # full pipeline
    python run_pipeline.py --skip-data-prep # skip to training
    python run_pipeline.py --demo-only      # inference only (model must exist)
    python run_pipeline.py --data-only      # data prep only
"""

import argparse
import os
import sys

# Ensure the package is importable when run from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from healthguide.config import TRAIN_CSV, VAL_CSV, MODEL_SAVE_PATH, MTSAMPLES_PATH


def check_mtsamples():
    if not os.path.exists(MTSAMPLES_PATH):
        print(
            "\n[INFO] mtsamples.csv not found at:\n"
            f"  {MTSAMPLES_PATH}\n\n"
            "To add the MTSamples dataset (optional, improves training):\n"
            "  1. Go to: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions\n"
            "  2. Download mtsamples.csv\n"
            f"  3. Place it at: {MTSAMPLES_PATH}\n\n"
            "Continuing with HuggingFace dataset only.\n"
        )


def run_data_prep():
    print("\n" + "=" * 60)
    print("STAGE 1: Data Preparation")
    print("=" * 60)
    check_mtsamples()
    from healthguide.prepare_data import main as prep_main
    prep_main()


def run_training():
    print("\n" + "=" * 60)
    print("STAGE 2: Training")
    print("=" * 60)
    from healthguide.train import main as train_main
    train_main()


def run_demo():
    print("\n" + "=" * 60)
    print("STAGE 3: Demo")
    print("=" * 60)
    from healthguide.demo import run_cli
    run_cli()


def main():
    parser = argparse.ArgumentParser(
        description="HealthGuide — Medical Symptom Triage Classifier Pipeline"
    )
    parser.add_argument(
        "--skip-data-prep",
        action="store_true",
        help="Skip data preparation (processed CSVs must already exist)",
    )
    parser.add_argument(
        "--demo-only",
        action="store_true",
        help="Skip training and go directly to the CLI demo (model must be saved)",
    )
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="Run data preparation only, then exit",
    )
    parser.add_argument(
        "--no-demo",
        action="store_true",
        help="Run data prep and training but skip the interactive demo",
    )
    args = parser.parse_args()

    if args.demo_only:
        run_demo()
        return

    if not args.skip_data_prep:
        run_data_prep()

    if args.data_only:
        return

    run_training()

    if not args.no_demo:
        print("\nTraining complete. Launching interactive demo...")
        print("(Press Ctrl+C or type 'quit' to exit the demo)\n")
        try:
            run_demo()
        except KeyboardInterrupt:
            print("\nDemo exited.")


if __name__ == "__main__":
    main()
