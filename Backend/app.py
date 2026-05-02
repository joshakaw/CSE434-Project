import uuid
from datetime import datetime

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

app = Flask(
    __name__,
    static_folder="../Frontend/dist/Frontend/browser",
    static_url_path="",
)
CORS(app)  # Allow Angular dev server (port 4200) to reach the API

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# ── In-memory patient store ────────────────────────────────────────────────────
# Each entry: { id, name, symptoms, urgency, summary, department, timestamp }
patients = []


# ── Static / Angular app ───────────────────────────────────────────────────────

@app.route("/")
def serve_angular_app():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    # Don't catch API routes – let Flask handle them as 404 if not defined
    if path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, path)


# ── Patient API ────────────────────────────────────────────────────────────────

@app.route("/api/patients", methods=["GET"])
def get_patients():
    """Return the full in-memory patient list."""
    return jsonify(patients)


@app.route("/api/submit", methods=["POST"])
def submit_patient():
    """
    Accept a patient submission, call Gemini for triage, and store the result.

    Expected JSON body:
        { "name": "John Doe", "symptoms": "I have chest pain..." }
    """
    body = request.get_json(force=True, silent=True) or {}
    name = (body.get("name") or "Anonymous").strip()
    symptoms = (body.get("symptoms") or "").strip()

    if not symptoms:
        return jsonify({"error": "symptoms field is required"}), 400

    try:
        from genai import analyze_patient
        result = analyze_patient(name, symptoms)
    except Exception as exc:
        return jsonify({"error": f"AI analysis failed: {exc}"}), 500

    patient = {
        "id": str(uuid.uuid4()),
        "name": name,
        "symptoms": symptoms,
        "urgency": result.get("urgency", "Non-Urgent"),
        "summary": result.get("summary", ""),
        "department": result.get("department", "General Medicine"),
        "routing": result.get("routing", ""),
        "classifier_urgency": result.get("classifier_urgency", None),
        "classifier_confidence": result.get("classifier_confidence", None),
        "models_disagree": (
            result.get("classifier_urgency") is not None and
            result.get("classifier_urgency") != result.get("urgency")
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    patients.append(patient)
    return jsonify(patient), 201


# ── Legacy test endpoint ───────────────────────────────────────────────────────

@app.route("/api/data")
def get_data():
    return jsonify({"message": "Hello from Flask API"})


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)  # reloader=False avoids double-loading genai
