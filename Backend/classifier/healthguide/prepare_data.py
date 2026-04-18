"""
HealthGuide Data Preparation
Loads both datasets, unifies labels, combines, balances, and saves processed CSVs.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

# Allow running as script or import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from healthguide.config import (
    LABEL2ID, SPECIALTY_URGENCY_MAP,
    DATA_PROCESSED_DIR, MTSAMPLES_PATH,
    TRAIN_CSV, VAL_CSV, SEED
)


def load_huggingface_dataset() -> pd.DataFrame:
    """
    Downloads sweatSmile/medical-symptom-triage from HuggingFace.
    Returns DataFrame with columns: [text, urgency_label, split].
    """
    print("Loading HuggingFace dataset: sweatSmile/medical-symptom-triage ...")
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Run: pip install datasets")

    ds = load_dataset("sweatSmile/medical-symptom-triage")

    rows = []
    for split_name in ds.keys():
        for example in ds[split_name]:
            text = example.get("input") or example.get("text") or example.get("symptoms") or ""
            urgency = example.get("urgency") or example.get("label") or ""
            if not text or not urgency:
                continue
            # Normalize label
            urgency = urgency.strip()
            if urgency == "Routine":
                urgency = "Non-Urgent"
            if urgency not in LABEL2ID:
                continue
            rows.append({
                "text": text.strip(),
                "urgency_label": urgency,
                "split": "train" if split_name == "train" else "val",
            })

    df = pd.DataFrame(rows)
    print(f"  HuggingFace dataset: {len(df)} examples loaded")
    print(f"  Label distribution:\n{df['urgency_label'].value_counts().to_string()}")
    return df


def load_mtsamples(csv_path: str) -> pd.DataFrame:
    """
    Reads mtsamples.csv and maps medical_specialty -> urgency using SPECIALTY_URGENCY_MAP.
    Returns DataFrame with columns: [text, urgency_label, split].
    All rows assigned to 'train' only — no MTSamples leakage into validation.
    """
    if not os.path.exists(csv_path):
        print(f"\n[WARNING] mtsamples.csv not found at: {csv_path}")
        print("  To include this dataset:")
        print("  1. Go to: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions")
        print("  2. Download mtsamples.csv")
        print(f"  3. Place it at: {csv_path}")
        print("  Continuing with HuggingFace dataset only.\n")
        return pd.DataFrame(columns=["text", "urgency_label", "split"])

    print(f"Loading MTSamples from {csv_path} ...")
    df = pd.read_csv(csv_path)

    # Identify columns (Kaggle version uses these names)
    text_col = None
    for candidate in ["transcription", "description", "sample_name"]:
        if candidate in df.columns:
            text_col = candidate
            break
    specialty_col = None
    for candidate in ["medical_specialty", "specialty"]:
        if candidate in df.columns:
            specialty_col = candidate
            break

    if text_col is None or specialty_col is None:
        print(f"  [WARNING] Could not find expected columns in mtsamples.csv. Columns found: {list(df.columns)}")
        print("  Skipping MTSamples.")
        return pd.DataFrame(columns=["text", "urgency_label", "split"])

    df = df[[text_col, specialty_col]].dropna()
    df.columns = ["raw_text", "specialty"]
    df["specialty"] = df["specialty"].str.strip()

    # Map specialty -> urgency
    df["urgency_label"] = df["specialty"].map(SPECIALTY_URGENCY_MAP)
    df = df.dropna(subset=["urgency_label"])

    # Truncate long transcriptions to first 800 characters
    # (Chief complaint and assessment are at the top — most triage-relevant)
    df["text"] = df["raw_text"].str[:800].str.strip()
    df = df[df["text"].str.len() > 20]  # drop near-empty rows

    df = df[["text", "urgency_label"]].copy()
    df["split"] = "train"

    print(f"  MTSamples: {len(df)} examples loaded (after specialty mapping)")
    print(f"  Label distribution:\n{df['urgency_label'].value_counts().to_string()}")
    return df


def combine_and_balance(
    df_hf: pd.DataFrame,
    df_mt: pd.DataFrame
) -> tuple:
    """
    Combines both DataFrames. Computes class weights to handle imbalance.
    Returns (train_df, val_df, class_weights_tensor).
    """
    import torch

    # Separate HF validation set (keep it pure — no MTSamples in val)
    hf_train = df_hf[df_hf["split"] == "train"].copy()
    hf_val = df_hf[df_hf["split"] == "val"].copy()

    # If HF dataset doesn't have a pre-defined val split, create one
    if len(hf_val) == 0:
        hf_train, hf_val = train_test_split(
            hf_train, test_size=0.15, stratify=hf_train["urgency_label"], random_state=SEED
        )

    # Combine train sets
    train_df = pd.concat([hf_train, df_mt], ignore_index=True)
    val_df = hf_val.copy()

    # Shuffle train
    train_df = train_df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)

    # Compute class weights from training labels
    labels_array = train_df["urgency_label"].map({"Emergency": 0, "Urgent": 1, "Non-Urgent": 2}).values
    classes = np.array([0, 1, 2])
    weights = compute_class_weight("balanced", classes=classes, y=labels_array)
    class_weights = torch.tensor(weights, dtype=torch.float)

    print(f"\nCombined dataset:")
    print(f"  Train: {len(train_df)} examples")
    print(f"  Val:   {len(val_df)} examples")
    print(f"  Train label distribution:\n{train_df['urgency_label'].value_counts().to_string()}")
    print(f"  Class weights (Emergency/Urgent/Non-Urgent): {class_weights.numpy().round(3)}")

    return train_df, val_df, class_weights


def main():
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)

    df_hf = load_huggingface_dataset()
    df_mt = load_mtsamples(MTSAMPLES_PATH)

    train_df, val_df, class_weights = combine_and_balance(df_hf, df_mt)

    train_df[["text", "urgency_label"]].to_csv(TRAIN_CSV, index=False)
    val_df[["text", "urgency_label"]].to_csv(VAL_CSV, index=False)

    print(f"\nSaved processed data:")
    print(f"  {TRAIN_CSV}")
    print(f"  {VAL_CSV}")


if __name__ == "__main__":
    main()
