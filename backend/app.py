"""
Healthcare OS — Flask API Server
REST API with CORS, static file serving, and patient assessment endpoint.
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from scoring_engine import compute_risk_score, compute_urgency_score, compute_adherence_score
from decision_engine import classify_patient
from ai_service import generate_summary

# ─── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")


# ─── Static File Serving ────────────────────────────────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ─── Health Check ───────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "healthcare-os",
        "version": "1.0.0"
    })


# ─── Patient Assessment ────────────────────────────────────────────────────────
@app.route("/api/assess", methods=["POST"])
def assess_patient():
    """
    Accept patient data, compute scores, classify, and return structured assessment.
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON in request body"}), 400

    # Validate required fields
    required_fields = ["symptoms"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Extract data
    symptoms = data.get("symptoms", "")
    vitals = data.get("vitals", {})
    medical_history = data.get("medical_history", "")
    age = data.get("age", 30)
    symptom_duration = data.get("symptom_duration", "")
    adherence_info = data.get("adherence_info", {})

    # Compute scores
    risk_score = compute_risk_score(symptoms, vitals, medical_history, age)
    urgency_score = compute_urgency_score(symptoms, vitals, symptom_duration)
    adherence_score = compute_adherence_score(adherence_info)

    scores = {
        "risk": risk_score,
        "urgency": urgency_score,
        "adherence": adherence_score,
    }

    # Classify patient
    classification_result = classify_patient(risk_score, urgency_score, adherence_score)

    # Generate summary
    result = generate_summary(data, scores, classification_result)

    return jsonify(result)


# ─── Run Server ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🏥 Healthcare OS Server Starting...")
    print("   URL: http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
