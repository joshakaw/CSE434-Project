"""
HealthGuide Training Loop
AdamW optimizer, linear warmup/decay scheduler, class-weighted loss, early stopping.
"""

import os
import sys
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from tqdm import tqdm
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from healthguide.config import (
    MODEL_NAME, BATCH_SIZE, EPOCHS, LEARNING_RATE,
    WARMUP_RATIO, WEIGHT_DECAY, GRAD_CLIP,
    EARLY_STOPPING_PATIENCE, MODEL_SAVE_PATH,
    TRAIN_CSV, VAL_CSV, LABEL2ID, SEED
)
from healthguide.dataset import TriageDataset
from healthguide.model import HealthGuideClassifier
from healthguide.evaluate import compute_metrics, print_classification_report


def set_seed(seed: int):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_optimizer_and_scheduler(model, num_training_steps: int):
    """
    AdamW with weight decay on non-bias/LayerNorm params only.
    Linear warmup then linear decay.
    """
    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_params = [
        {
            "params": [
                p for n, p in model.named_parameters()
                if not any(nd in n for nd in no_decay)
            ],
            "weight_decay": WEIGHT_DECAY,
        },
        {
            "params": [
                p for n, p in model.named_parameters()
                if any(nd in n for nd in no_decay)
            ],
            "weight_decay": 0.0,
        },
    ]
    optimizer = torch.optim.AdamW(optimizer_grouped_params, lr=LEARNING_RATE)
    num_warmup_steps = int(WARMUP_RATIO * num_training_steps)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=num_warmup_steps,
        num_training_steps=num_training_steps,
    )
    return optimizer, scheduler


def train_epoch(model, loader, optimizer, scheduler, device, loss_fn):
    model.train()
    total_loss = 0.0

    for batch in tqdm(loader, desc="  Training", leave=False):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

        loss = loss_fn(logits, labels)
        loss.backward()

        nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()

    return total_loss / len(loader)


def eval_epoch(model, loader, device, loss_fn):
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in tqdm(loader, desc="  Validation", leave=False):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits

            loss = loss_fn(logits, labels)
            total_loss += loss.item()

            preds = torch.argmax(logits, dim=-1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    return (
        total_loss / len(loader),
        np.array(all_preds),
        np.array(all_labels),
    )


def main():
    set_seed(SEED)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # --- Load data ---
    if not os.path.exists(TRAIN_CSV) or not os.path.exists(VAL_CSV):
        print("Processed data not found. Running prepare_data.py first...")
        from healthguide.prepare_data import main as prep_main
        prep_main()

    train_df = pd.read_csv(TRAIN_CSV)
    val_df = pd.read_csv(VAL_CSV)
    print(f"Train: {len(train_df)} | Val: {len(val_df)}")

    # --- Tokenizer ---
    print(f"Loading tokenizer: {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # --- Datasets & DataLoaders ---
    train_dataset = TriageDataset(train_df, tokenizer, LABEL2ID)
    val_dataset = TriageDataset(val_df, tokenizer, LABEL2ID)

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0
    )

    # --- Class weights from training label distribution ---
    from sklearn.utils.class_weight import compute_class_weight
    label_ints = train_df["urgency_label"].map(LABEL2ID).values
    weights = compute_class_weight("balanced", classes=np.array([0, 1, 2]), y=label_ints)
    class_weights = torch.tensor(weights, dtype=torch.float).to(device)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights)

    # --- Model ---
    print(f"Loading model: {MODEL_NAME} ...")
    model = HealthGuideClassifier().to(device)

    # --- Optimizer & Scheduler ---
    num_training_steps = EPOCHS * len(train_loader)
    optimizer, scheduler = get_optimizer_and_scheduler(model, num_training_steps)

    # --- Training loop ---
    best_macro_f1 = 0.0
    patience_counter = 0

    print(f"\nStarting training ({EPOCHS} epochs, patience={EARLY_STOPPING_PATIENCE})")
    print("=" * 60)

    for epoch in range(1, EPOCHS + 1):
        print(f"\nEpoch {epoch}/{EPOCHS}")

        train_loss = train_epoch(model, train_loader, optimizer, scheduler, device, loss_fn)
        val_loss, preds, labels = eval_epoch(model, val_loader, device, loss_fn)
        metrics = compute_metrics(preds, labels)

        print(
            f"  Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Macro F1: {metrics['macro_f1']:.4f} | "
            f"Acc: {metrics['accuracy']:.4f} | "
            f"Emergency Recall: {metrics['emergency_recall']:.4f}"
        )

        if metrics["macro_f1"] > best_macro_f1:
            best_macro_f1 = metrics["macro_f1"]
            os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
            model.save(MODEL_SAVE_PATH)
            tokenizer.save_pretrained(MODEL_SAVE_PATH)
            print(f"  [Checkpoint saved] Best macro F1: {best_macro_f1:.4f}")
            patience_counter = 0
        else:
            patience_counter += 1
            print(f"  No improvement. Patience: {patience_counter}/{EARLY_STOPPING_PATIENCE}")
            if patience_counter >= EARLY_STOPPING_PATIENCE:
                print("  Early stopping triggered.")
                break

    print("\n" + "=" * 60)
    print(f"Training complete. Best Macro F1: {best_macro_f1:.4f}")
    print(f"Model saved to: {MODEL_SAVE_PATH}")

    # Final evaluation on validation set using best checkpoint
    print("\nFinal evaluation (best checkpoint):")
    best_model = HealthGuideClassifier.load(MODEL_SAVE_PATH).to(device)
    _, final_preds, final_labels = eval_epoch(best_model, val_loader, device, loss_fn)
    print_classification_report(final_preds, final_labels)


if __name__ == "__main__":
    main()
