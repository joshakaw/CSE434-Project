"""
HealthGuide Configuration
All hyperparameters and constants in one place.
"""

import os

# --- Model ---
MODEL_NAME = "distilbert-base-uncased"
MAX_LEN = 256
NUM_LABELS = 3

# --- Labels ---
LABEL2ID = {"Emergency": 0, "Urgent": 1, "Non-Urgent": 2}
ID2LABEL = {0: "Emergency", 1: "Urgent", 2: "Non-Urgent"}

# --- Training ---
BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 2e-5
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01
EARLY_STOPPING_PATIENCE = 2
GRAD_CLIP = 1.0
SEED = 42

# Emergency recall threshold — prints warning if below this during training
EMERGENCY_RECALL_THRESHOLD = 0.85

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models", "healthguide_model")
MTSAMPLES_PATH = os.path.join(DATA_RAW_DIR, "mtsamples.csv")
TRAIN_CSV = os.path.join(DATA_PROCESSED_DIR, "combined_train.csv")
VAL_CSV = os.path.join(DATA_PROCESSED_DIR, "combined_val.csv")

# --- Department lookup (post-inference) ---
URGENCY_TO_DEPARTMENT = {
    "Emergency": "Emergency Department — seek immediate care or call 911",
    "Urgent": "Urgent Care Clinic or same-day physician appointment",
    "Non-Urgent": "Primary Care Physician or scheduled outpatient visit",
}

# --- MTSamples specialty -> urgency mapping ---
# These transcriptions describe completed encounters, not incoming triage.
# The mapping is a domain-approximate heuristic, not clinically validated.
SPECIALTY_URGENCY_MAP = {
    # Emergency
    "Emergency Room Reports": "Emergency",
    "Cardiovascular / Pulmonary": "Emergency",
    # Urgent
    "Neurology": "Urgent",
    "Neurosurgery": "Urgent",
    "Hematology - Oncology": "Urgent",
    "Nephrology": "Urgent",
    "Obstetrics / Gynecology": "Urgent",
    "Pediatrics - Neonatal": "Urgent",
    "Endocrinology": "Urgent",
    "Gastroenterology": "Urgent",
    "ENT - Otolaryngology": "Urgent",
    "Urology": "Urgent",
    "Surgery": "Urgent",
    # Non-Urgent
    "Orthopedic": "Non-Urgent",
    "Dermatology": "Non-Urgent",
    "Ophthalmology": "Non-Urgent",
    "Psychiatry / Psychology": "Non-Urgent",
    "Physical Medicine - Rehab": "Non-Urgent",
    "Pain Management": "Non-Urgent",
    "Radiology": "Non-Urgent",
    "Allergy / Immunology": "Non-Urgent",
    "Rheumatology": "Non-Urgent",
    "Sleep Medicine": "Non-Urgent",
    "Chiropractic": "Non-Urgent",
    "Podiatry": "Non-Urgent",
    "Speech - Language": "Non-Urgent",
    "Dentistry": "Non-Urgent",
    "Cosmetic / Plastic Surgery": "Non-Urgent",
    "Bariatrics": "Non-Urgent",
    "Diets and Nutritions": "Non-Urgent",
    "Office Notes": "Non-Urgent",
    "SOAP / Chart / Progress Notes": "Non-Urgent",
    "Consult - History and Phy.": "Non-Urgent",
    "Discharge Summary": "Non-Urgent",
    "General Medicine": "Non-Urgent",
    "Letters": "Non-Urgent",
    "IME-QME-Work Comp etc.": "Non-Urgent",
    "Lab Medicine - Pathology": "Non-Urgent",
    "Hospice - Palliative Care": "Non-Urgent",
    "Autopsy": "Non-Urgent",
}
