"""
HealthGuide PyTorch Dataset
Tokenizes symptom text on-demand to avoid upfront RAM spike.
"""

import torch
from torch.utils.data import Dataset
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from healthguide.config import MAX_LEN, LABEL2ID


class TriageDataset(Dataset):
    """
    Wraps a DataFrame of (text, urgency_label) pairs.
    Tokenizes with the provided tokenizer on __getitem__.

    Args:
        df: DataFrame with columns [text, urgency_label]
        tokenizer: HuggingFace tokenizer (AutoTokenizer)
        label2id: dict mapping label string -> int
    """

    def __init__(self, df: pd.DataFrame, tokenizer, label2id: dict = LABEL2ID):
        self.texts = df["text"].tolist()
        self.labels = [label2id[lbl] for lbl in df["urgency_label"]]
        self.tokenizer = tokenizer
        self.max_len = MAX_LEN

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),       # (max_len,)
            "attention_mask": encoding["attention_mask"].squeeze(0),  # (max_len,)
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }
