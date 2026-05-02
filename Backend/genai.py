"""
Gemini integration via plain HTTP (requests).
Works on Python 3.8+ with no Gemini SDK required.
"""
import sys
import json
import re
import requests

# ── Load Gemini API key ────────────────────────────────────────────────────────
try:
    with open('secrets.json', 'r', encoding='utf-8') as f:
        _config = json.load(f)
    gemini_api_key = _config['gemini_api_key']
except FileNotFoundError:
    print("[ERROR] secrets.json not found. Create Backend/secrets.json with {\"gemini_api_key\": \"YOUR_KEY\"}")
    sys.exit(1)
except KeyError:
    print("[ERROR] secrets.json must contain a 'gemini_api_key' field.")
    sys.exit(1)

GEMINI_MODEL = "gemini-flash-lite-latest"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
).format(model=GEMINI_MODEL, key=gemini_api_key)


def _call_gemini(prompt):
    """Send a prompt to Gemini and return the response text. Retries on 429."""
    import time
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    for attempt in range(3):
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        if resp.status_code == 429:
            wait = 20 * (attempt + 1)   # 20s, 40s, 60s
            print("[WARN] Rate limited by Gemini, retrying in {}s...".format(wait))
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    resp.raise_for_status()  # raise after all retries exhausted


# ── Optionally load DistilBERT classifier (RAG enhancement) ────────────────────
_classifier = None
_tokenizer = None
_device = None
_classifier_available = False

def _try_load_classifier():
    global _classifier, _tokenizer, _device, _classifier_available
    try:
        import torch
        from classifier.healthguide.config import MODEL_SAVE_PATH
        from classifier.healthguide.demo import load_model_and_tokenizer
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _classifier, _tokenizer = load_model_and_tokenizer(MODEL_SAVE_PATH)
        _classifier = _classifier.to(_device)
        _classifier_available = True
        print("[INFO] DistilBERT classifier loaded – RAG mode enabled.")
    except Exception as e:
        print("[WARNING] Classifier unavailable ({}). Running Gemini-only mode.".format(e))

_try_load_classifier()


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze_patient(name, symptoms):
    """
    Analyse patient symptoms with Gemini REST API.
    Returns a dict with urgency, summary, department,
    and optionally classifier_urgency + classifier_confidence.
    """
    classifier_context = ""
    classifier_urgency = None
    classifier_confidence = None

    if _classifier_available:
        try:
            from classifier.healthguide.demo import predict
            clf_result = predict(symptoms, _classifier, _tokenizer, _device)
            classifier_urgency = clf_result.get("urgency")
            classifier_confidence = clf_result.get("confidence")
            classifier_context = (
                "Classifier pre-assessment: urgency={}, confidence={:.1%}\n\n"
            ).format(classifier_urgency, classifier_confidence)
        except Exception as e:
            print("[WARNING] Classifier prediction failed: {}".format(e))

    prompt = (
        "You are a concise medical triage assistant for an emergency department.\n\n"
        "{context}"
        "Patient name: {name}\n"
        "Patient-reported symptoms: {symptoms}\n\n"
        "Task: Provide a structured triage assessment. "
        "Respond with ONLY valid JSON – no markdown fences, no extra text.\n\n"
        "For the department field, you MUST choose exactly one from this list:\n"
        "Emergency, Cardiology, Neurology, Orthopedics, Gastroenterology, "
        "Pulmonology, Psychiatry, General Medicine, Urgent Care, Pediatrics, "
        "Trauma, Dermatology, Urology, Oncology, Obstetrics\n\n"
        "{{\n"
        '  "urgency": "Emergency" | "Urgent" | "Non-Urgent",\n'
        '  "summary": "<1-2 sentence clinical summary for hospital staff>",\n'
        '  "department": "<one department from the list above>"\n'
        "}}"
    ).format(context=classifier_context, name=name, symptoms=symptoms)

    try:
        raw = _call_gemini(prompt).strip()
        print("[DEBUG] Gemini raw response: {}".format(raw[:500]))

        # Strip markdown code fences if Gemini included them
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            urgency = parsed.get("urgency", "Non-Urgent")
            if urgency not in ("Emergency", "Urgent", "Non-Urgent"):
                urgency = "Non-Urgent"

            # Use Gemini's department if it's from the allowed list, else fall
            # back to the classifier's urgency-based routing description
            allowed_depts = {
                "Emergency", "Cardiology", "Neurology", "Orthopedics",
                "Gastroenterology", "Pulmonology", "Psychiatry",
                "General Medicine", "Urgent Care", "Pediatrics",
                "Trauma", "Dermatology", "Urology", "Oncology", "Obstetrics"
            }
            gemini_dept = parsed.get("department", "")
            if gemini_dept in allowed_depts:
                department = gemini_dept
            else:
                try:
                    from classifier.healthguide.config import URGENCY_TO_DEPARTMENT
                    department = URGENCY_TO_DEPARTMENT.get(urgency, "General Medicine")
                except Exception:
                    department = "General Medicine"

            # Routing instruction from classifier config (patient-friendly)
            try:
                from classifier.healthguide.config import URGENCY_TO_DEPARTMENT
                routing = URGENCY_TO_DEPARTMENT.get(urgency, "")
            except Exception:
                routing = ""

            result = {
                "urgency": urgency,
                "summary": parsed.get("summary", raw[:300]),
                "department": department,
                "routing": routing,
            }
            if classifier_urgency:
                result["classifier_urgency"] = classifier_urgency
                result["classifier_confidence"] = round(classifier_confidence * 100, 1)
            return result
        else:
            print("[ERROR] No JSON object found in Gemini response: {}".format(raw))
    except Exception as e:
        print("[ERROR] Gemini call failed: {} — {}".format(type(e).__name__, e))

    return {
        "urgency": "Non-Urgent",
        "summary": "Unable to generate summary. Please consult clinical staff.",
        "department": "General Medicine",
    }


# ── Legacy helper kept for backward-compatibility with tests ──────────────────

def summarize_patient_sheet(content, preprompt="", rag=True):
    """Original function used in test_gen.py – preserved for compatibility."""
    prompt = ""
    if preprompt:
        prompt += preprompt + "\n\nQ:"
    if rag and _classifier_available:
        try:
            from classifier.healthguide.demo import predict
            prompt += str(predict(content, _classifier, _tokenizer, _device))
        except Exception:
            pass
    prompt += "\n" + content
    return (prompt, _call_gemini(prompt))
