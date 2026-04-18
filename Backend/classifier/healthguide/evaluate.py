"""
HealthGuide Evaluation Utilities
Computes macro F1, per-class metrics, confusion matrix.
"""

import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
    recall_score,
)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from healthguide.config import ID2LABEL, EMERGENCY_RECALL_THRESHOLD


def compute_metrics(preds: np.ndarray, labels: np.ndarray) -> dict:
    """
    Computes classification metrics.

    Args:
        preds:  1-D array of predicted class indices
        labels: 1-D array of ground-truth class indices

    Returns:
        dict with keys: accuracy, macro_f1, emergency_recall, per_class_f1
    """
    accuracy = accuracy_score(labels, preds)
    macro_f1 = f1_score(labels, preds, average="macro", zero_division=0)

    # Per-class recall; index 0 = Emergency
    per_class_recall = recall_score(labels, preds, average=None, zero_division=0, labels=[0, 1, 2])
    emergency_recall = float(per_class_recall[0]) if len(per_class_recall) > 0 else 0.0

    per_class_f1 = f1_score(labels, preds, average=None, zero_division=0, labels=[0, 1, 2])

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "emergency_recall": emergency_recall,
        "per_class_f1": {ID2LABEL[i]: float(per_class_f1[i]) for i in range(len(per_class_f1))},
    }


def print_classification_report(preds: np.ndarray, labels: np.ndarray):
    """Prints a formatted classification report with class names."""
    target_names = [ID2LABEL[i] for i in sorted(ID2LABEL.keys())]
    report = classification_report(
        labels, preds, target_names=target_names, zero_division=0
    )
    cm = confusion_matrix(labels, preds, labels=list(sorted(ID2LABEL.keys())))

    print("\n--- Classification Report ---")
    print(report)

    print("--- Confusion Matrix ---")
    print(f"{'':>12}", end="")
    for name in target_names:
        print(f"{name:>12}", end="")
    print()
    for i, name in enumerate(target_names):
        print(f"{name:>12}", end="")
        for val in cm[i]:
            print(f"{val:>12}", end="")
        print()

    metrics = compute_metrics(preds, labels)
    if metrics["emergency_recall"] < EMERGENCY_RECALL_THRESHOLD:
        print(
            f"\n[WARNING] Emergency recall = {metrics['emergency_recall']:.3f} "
            f"(below threshold {EMERGENCY_RECALL_THRESHOLD}). "
            "Consider adjusting class weights or training longer."
        )
