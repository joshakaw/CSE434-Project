"""
HealthGuide CLI Demo
Interactive symptom triage assistant. Type symptoms to get urgency level + department.
"""

import os
import sys
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from healthguide.config import (
    MODEL_SAVE_PATH, MAX_LEN, ID2LABEL, LABEL2ID, URGENCY_TO_DEPARTMENT
)
from healthguide.model import HealthGuideClassifier


BANNER = """
============================================================
  HealthGuide — Medical Symptom Triage Assistant
  (NOT a substitute for professional medical advice)
============================================================
"""

DISCLAIMER = """
DISCLAIMER: This tool provides general guidance only.
            It is NOT a diagnosis and does NOT replace
            a licensed medical professional. In an emergency
            call 911 immediately.
------------------------------------------------------------"""


def load_model_and_tokenizer(model_path: str):
    """Loads saved model and tokenizer from MODEL_SAVE_PATH."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No saved model found at: {model_path}\n"
            "Run training first: python healthguide/train.py"
        )
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = HealthGuideClassifier.load(model_path)
    model.eval()
    return model, tokenizer


def predict(text: str, model, tokenizer, device) -> dict:
    """
    Runs inference on symptom text.

    Returns:
        {
            "urgency": str,
            "confidence": float,
            "department": str,
            "probabilities": dict[str, float]
        }
    """
    encoding = tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = F.softmax(outputs.logits, dim=-1).squeeze(0)

    pred_idx = int(torch.argmax(probs).item())
    urgency = ID2LABEL[pred_idx]
    confidence = float(probs[pred_idx].item())

    return {
        "urgency": urgency,
        "confidence": confidence,
        "department": URGENCY_TO_DEPARTMENT[urgency],
        "probabilities": {
            ID2LABEL[i]: float(probs[i].item()) for i in range(len(probs))
        },
    }


def _bar(probability: float, width: int = 20) -> str:
    filled = int(round(probability * width))
    return "█" * filled + " " * (width - filled)


def print_result(result: dict):
    urgency = result["urgency"]
    conf = result["confidence"]
    dept = result["department"]
    probs = result["probabilities"]

    print(f"\n--- Triage Assessment ---")
    print(f"Urgency Level  : {urgency.upper()}")
    print(f"Confidence     : {conf * 100:.1f}%")
    print(f"Recommended    : {dept}")
    print(f"\nProbability breakdown:")
    for label, p in sorted(probs.items(), key=lambda x: -x[1]):
        print(f"  {label:<12} {_bar(p)}  {p * 100:5.1f}%")
    print(DISCLAIMER)


def run_cli():
    print(BANNER)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Loading model...")
    try:
        model, tokenizer = load_model_and_tokenizer(MODEL_SAVE_PATH)
        model = model.to(device)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    print("Model loaded. Ready.\n")

    while True:
        print("Describe your symptoms (or type 'quit' to exit):")
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not user_input:
            print("Please enter a symptom description.\n")
            continue

        result = predict(user_input, model, tokenizer, device)
        print_result(result)
        print()


if __name__ == "__main__":
    run_cli()
