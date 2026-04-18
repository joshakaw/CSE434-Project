"""
HealthGuide Model
Thin wrapper around DistilBERT for sequence classification.
"""

import torch.nn as nn
from transformers import AutoModelForSequenceClassification

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from healthguide.config import MODEL_NAME, NUM_LABELS, ID2LABEL, LABEL2ID


class HealthGuideClassifier(nn.Module):
    """
    DistilBERT-based triage classifier.

    The HuggingFace AutoModelForSequenceClassification already adds:
      - pre-classifier linear layer  (768 -> 768)
      - dropout
      - classifier linear layer      (768 -> num_labels)

    Forward pass returns a SequenceClassifierOutput with:
      .loss   (when labels provided)
      .logits (batch_size, num_labels)
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        num_labels: int = NUM_LABELS,
    ):
        super().__init__()
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels,
            id2label=ID2LABEL,
            label2id=LABEL2ID,
        )

    def forward(self, input_ids, attention_mask, labels=None):
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )

    def save(self, path: str):
        self.model.save_pretrained(path)

    @classmethod
    def load(cls, path: str):
        instance = cls.__new__(cls)
        nn.Module.__init__(instance)
        instance.model = AutoModelForSequenceClassification.from_pretrained(path)
        return instance
