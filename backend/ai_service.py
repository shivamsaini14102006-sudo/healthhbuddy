"""
Healthcare OS — AI Service
Generates structured summaries for doctors and patients based on scoring and classification results.
Uses rule-based template generation (no external API dependency).
"""


def generate_summary(patient_data, scores, classification_result):
    """
    Generate a complete assessment summary including:
    - Patient context
    - Doctor summary
    - Patient instructions
    - Workflow actions

    Returns a dict ready for JSON serialization.
    """

    patient_context = _build_patient_context(patient_data)
    doctor_summary = _generate_doctor_summary(patient_data, scores, classification_result)
    patient_instructions = _generate_patient_instructions(scores, classification_result)
    workflow_actions = _generate_workflow_actions(scores, classification_result, patient_data)

    return {
        "patient_context": patient_context,
        "scores": scores,
        "classification": classification_result["classification"],
        "classification_detail": {
            "label": classification_result["severity_label"],
            "color": classification_result["color"],
            "escalation_level": classification_result["escalation_level"],
        },
        "doctor_summary": doctor_summary,
        "patient_instructions": patient_instructions,
        "workflow_actions": workflow_actions,
        "recommendations": classification_result["recommendations"],
    }


def _build_patient_context(data):
    """Build structured patient context from raw input."""
    vitals = data.get("vitals", {})

    vitals_parts = []
    if vitals.get("heart_rate") is not None:
        vitals_parts.append(f"HR: {vitals['heart_rate']} bpm")
    if vitals.get("blood_pressure_systolic") is not None:
        sys_val = vitals["blood_pressure_systolic"]
        dia_val = vitals.get("blood_pressure_diastolic", "?")
        vitals_parts.append(f"BP: {sys_val}/{dia_val} mmHg")
    if vitals.get("temperature") is not None:
        vitals_parts.append(f"Temp: {vitals['temperature']}°F")
    if vitals.get("spo2") is not None:
        vitals_parts.append(f"SpO2: {vitals['spo2']}%")

    symptoms_text = data.get("symptoms", "")
    symptoms_list = [s.strip() for s in symptoms_text.split(",") if s.strip()] if symptoms_text else []

    return {
        "name": data.get("name", "Unknown"),
        "age": data.get("age", 0),
        "gender": data.get("gender", "unspecified"),
        "symptoms_list": symptoms_list,
        "symptom_duration": data.get("symptom_duration", "unspecified"),
        "medical_history": data.get("medical_history", "none reported"),
        "current_medications": data.get("current_medications", "none reported"),
        "vitals_summary": " | ".join(vitals_parts) if vitals_parts else "No vitals recorded",
    }


def _generate_doctor_summary(patient_data, scores, classification):
    """Generate structured summary for the attending doctor."""
    key_issues = []
    recommended_actions = []
    symptoms_text = patient_data.get("symptoms", "")
    vitals = patient_data.get("vitals", {})
    history = patient_data.get("medical_history", "")

    # Build key issues from symptoms
    if symptoms_text:
        symptoms = [s.strip() for s in symptoms_text.split(",") if s.strip()]
        primary = symptoms[0] if symptoms else "unspecified symptoms"

        if history and history.strip():
            key_issues.append(f"Presenting with {primary} — relevant history: {history}")
        else:
            key_issues.append(f"Presenting with {primary}")

        if len(symptoms) > 1:
            key_issues.append(f"Additional symptoms: {', '.join(symptoms[1:])}")

    # Flag abnormal vitals
    hr = vitals.get("heart_rate")
    if hr is not None:
        if hr > 100:
            key_issues.append(f"Tachycardia (HR {hr} bpm)")
        elif hr < 60:
            key_issues.append(f"Bradycardia (HR {hr} bpm)")

    sys_bp = vitals.get("blood_pressure_systolic")
    dia_bp = vitals.get("blood_pressure_diastolic")
    if sys_bp is not None:
        if sys_bp >= 180 or (dia_bp is not None and dia_bp >= 120):
            key_issues.append(f"Hypertensive crisis (BP {sys_bp}/{dia_bp} mmHg)")
        elif sys_bp >= 140 or (dia_bp is not None and dia_bp >= 90):
            key_issues.append(f"Elevated blood pressure (BP {sys_bp}/{dia_bp} mmHg)")
        elif sys_bp < 90:
            key_issues.append(f"Hypotension (BP {sys_bp}/{dia_bp} mmHg)")

    temp = vitals.get("temperature")
    if temp is not None:
        if temp >= 103:
            key_issues.append(f"High fever ({temp}°F)")
        elif temp >= 100.4:
            key_issues.append(f"Fever ({temp}°F)")
        elif temp < 96:
            key_issues.append(f"Hypothermia ({temp}°F)")

    spo2 = vitals.get("spo2")
    if spo2 is not None and spo2 < 95:
        key_issues.append(f"Hypoxia (SpO2 {spo2}%)")

    # Determine risk level text
    cls = classification["classification"]
    if cls == "CRITICAL":
        risk_text = "CRITICAL — Immediate attention required"
    elif cls == "LOW_ADHERENCE":
        risk_text = "MODERATE — Patient adherence intervention needed"
    elif scores["risk"] > 0.6:
        risk_text = "ELEVATED — Close monitoring recommended"
    else:
        risk_text = "LOW — Standard care appropriate"

    # Recommended actions based on classification
    rec_data = classification.get("recommendations", {})
    recommended_actions = rec_data.get("immediate_actions", [])[:4]

    if not key_issues:
        key_issues.append("No acute findings — routine assessment")

    return {
        "key_issues": key_issues,
        "risk_level": risk_text,
        "recommended_actions": recommended_actions,
    }


def _generate_patient_instructions(scores, classification):
    """Generate clear, simple instructions for the patient."""
    cls = classification["classification"]

    if cls == "CRITICAL":
        steps = [
            "🚨 You need to see a doctor right away — this is urgent",
            "Stay calm and rest — do not move around or exert yourself",
            "Have someone take you to the nearest emergency room",
            "If pain gets worse or you feel faint, call emergency services (112 / 911)",
            "Bring your current medications list to the hospital",
        ]
        warnings = [
            "Do NOT drive yourself to the hospital",
            "Do NOT take any new medication without a doctor's approval",
            "Do NOT ignore these symptoms — seek help immediately",
        ]
    elif cls == "LOW_ADHERENCE":
        steps = [
            "📋 Your health plan needs some adjustments — let's work on this together",
            "Take your medications at the same time every day — set a phone alarm",
            "Keep all scheduled appointments — they help track your progress",
            "Write down any side effects you experience and share them with your doctor",
            "Eat balanced meals and try to stay active for at least 30 minutes daily",
        ]
        warnings = [
            "Do NOT stop medications without talking to your doctor first",
            "Missing medications can make your condition worse",
            "If cost is an issue, ask your doctor about alternatives",
        ]
    else:
        steps = [
            "✅ Your health looks stable — keep up the good work!",
            "Continue taking your medications as prescribed",
            "Maintain a balanced diet with fruits, vegetables, and whole grains",
            "Aim for 30 minutes of moderate exercise most days",
            "Get enough sleep (7–9 hours) and manage stress",
        ]
        warnings = [
            "Watch for any new or worsening symptoms",
            "Contact your doctor if you feel something is not right",
        ]

    return {
        "steps": steps,
        "warnings": warnings,
    }


def _generate_workflow_actions(scores, classification, patient_data):
    """Generate workflow actions: appointments, alerts, follow-ups."""
    cls = classification["classification"]
    name = patient_data.get("name", "Patient")

    if cls == "CRITICAL":
        appointments = [
            "Emergency department visit — IMMEDIATE",
            "Specialist consultation within 24 hours",
        ]
        alerts = [
            f"🔴 CRITICAL ALERT: {name} requires immediate medical attention",
            "Notify on-call physician and specialist team",
            "Prepare emergency intervention protocols",
        ]
        follow_ups = [
            "Post-stabilization review within 24–48 hours",
            "Specialist follow-up within 1 week",
            "Primary care follow-up within 2 weeks",
        ]
    elif cls == "LOW_ADHERENCE":
        appointments = [
            "Medication counseling session — within 1 week",
            "Care coordinator meeting — within 2 weeks",
        ]
        alerts = [
            f"🟡 ADHERENCE ALERT: {name} — adherence score below threshold",
            "Assign care coordinator for follow-up",
        ]
        follow_ups = [
            "Weekly phone check-ins for 4 weeks",
            "Medication adherence review in 2 weeks",
            "Comprehensive care plan review in 1 month",
        ]
    else:
        timeline = classification.get("follow_up_timeline", "Within 3 months")
        appointments = [
            f"Routine follow-up — {timeline}",
        ]
        alerts = []
        follow_ups = [
            f"Standard follow-up — {timeline}",
            "Annual comprehensive health review",
        ]

    return {
        "appointments": appointments,
        "alerts": alerts,
        "follow_ups": follow_ups,
    }
