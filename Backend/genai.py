import string

import torch
from classifier.healthguide.config import MODEL_SAVE_PATH
from classifier.healthguide.demo import load_model_and_tokenizer, predict
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
import random, numpy as np, re, evaluate
import time

# ===================== STUDENT TODO START =====================
# Replace YOUR_API_KEY_HERE with your actual Gemini API key
genai.configure(api_key="AIzaSyD2WBX1Xr_LC1sxPSuUBfoC_IKS0q9spjQ")
# ===================== STUDENT TODO START =====================

# Initialize Gemini 2.5 Flash Lite model
gemini_model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    model, tokenizer = load_model_and_tokenizer(MODEL_SAVE_PATH)
    model = model.to(device)
except FileNotFoundError as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)


def summarize_patient_sheet(content: string) -> string:
    prompt = ""
    
    # Get relevant information from classifier
    prompt += str(predict(content, model, tokenizer, device))

    prompt += "\n"

    # Add the patient sheet content
    prompt += content

    response = gemini_model.generate_content(prompt)

    return (prompt,response)