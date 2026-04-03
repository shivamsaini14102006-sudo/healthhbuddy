"""
Healthcare OS — Scoring Engine
Computes Risk, Urgency, and Adherence scores from patient data.
"""

# ─── Symptom Severity Map ───────────────────────────────────────────────────────
SYMPTOM_SEVERITY = {
    # Critical (0.85–1.0)
    "chest pain": 0.95, "seizure": 0.95, "severe bleeding": 0.95,
    "unconsciousness": 1.0, "difficulty breathing": 0.92,
    "shortness of breath": 0.90, "stroke symptoms": 0.95,
    "heart attack": 1.0, "cardiac arrest": 1.0,
    "severe allergic reaction": 0.90, "anaphylaxis": 0.95,

    # High (0.60–0.84)
    "high fever": 0.75, "persistent vomiting": 0.70,
    "severe headache": 0.65, "dizziness": 0.60,
    "fainting": 0.75, "blood in stool": 0.80, "blood in urine": 0.78,
    "severe abdominal pain": 0.80, "confusion": 0.72,
    "numbness": 0.65, "vision changes": 0.68,
    "palpitations": 0.62, "swelling": 0.55,

    # Moderate (0.30–0.59)
    "fever": 0.45, "nausea": 0.35, "vomiting": 0.50,
    "diarrhea": 0.40, "headache": 0.40, "back pain": 0.45,
    "joint pain": 0.42, "muscle pain": 0.38, "fatigue": 0.35,
    "abdominal pain": 0.50, "rash": 0.30, "anxiety": 0.35,
    "insomnia": 0.30, "weight loss": 0.40,

    # Low (0.05–0.29)
    "cough": 0.25, "mild fever": 0.20, "sore throat": 0.20,
    "runny nose": 0.10, "sneezing": 0.08, "mild headache": 0.15,
    "cold": 0.15, "body ache": 0.20, "mild fatigue": 0.15,
}

# ─── History Risk Map ───────────────────────────────────────────────────────────
HISTORY_RISK = {
    "heart attack": 0.40, "previous heart attack": 0.40,
    "stroke": 0.38, "cancer": 0.35, "heart disease": 0.35,
    "coronary artery disease": 0.35, "heart failure": 0.38,
    "hypertension": 0.25, "diabetes": 0.25, "type 2 diabetes": 0.25,
    "type 1 diabetes": 0.28, "asthma": 0.18, "copd": 0.28,
    "kidney disease": 0.30, "liver disease": 0.30,
    "obesity": 0.20, "high cholesterol": 0.18,
    "thyroid disorder": 0.12, "arthritis": 0.10,
    "depression": 0.12, "anxiety disorder": 0.10,
}

# ─── Vital Ranges ──────────────────────────────────────────────────────────────
VITAL_RANGES = {
    "heart_rate":              {"low": 60, "high": 100, "crit_low": 40, "crit_high": 150},
    "blood_pressure_systolic": {"low": 90, "high": 140, "crit_low": 70, "crit_high": 200},
    "blood_pressure_diastolic":{"low": 60, "high": 90,  "crit_low": 40, "crit_high": 120},
    "temperature":             {"low": 97.0, "high": 99.5, "crit_low": 95.0, "crit_high": 104.0},
    "spo2":                    {"low": 95, "high": 100, "crit_low": 85, "crit_high": 101},
}

# ─── Duration Urgency Map ──────────────────────────────────────────────────────
DURATION_URGENCY = {
    "minutes": 1.0, "minute": 1.0,
    "hours": 0.7, "hour": 0.7,
    "days": 0.4, "day": 0.4,
    "weeks": 0.2, "week": 0.2,
    "months": 0.1, "month": 0.1,
    "years": 0.05, "year": 0.05,
}


def _parse_list(text):
    """Parse comma-separated string into cleaned lowercase list."""
    if not text or not text.strip():
        return []
    return [item.strip().lower() for item in text.split(",") if item.strip()]


def _compute_vital_deviation(value, vital_name):
    """Compute how far a vital is from normal range, normalized to 0–1."""
    if vital_name not in VITAL_RANGES:
        return 0.0

    r = VITAL_RANGES[vital_name]

    if r["low"] <= value <= r["high"]:
        return 0.0

    if value < r["low"]:
        # Below normal
        range_span = r["low"] - r["crit_low"]
        if range_span == 0:
            return 1.0
        deviation = (r["low"] - value) / range_span
    else:
        # Above normal
        if vital_name == "spo2":
            return 0.0  # SpO2 above 100 is not dangerous
        range_span = r["crit_high"] - r["high"]
        if range_span == 0:
            return 1.0
        deviation = (value - r["high"]) / range_span

    return min(max(deviation, 0.0), 1.0)


def compute_risk_score(symptoms, vitals, medical_history, age):
    """
    Compute risk score (0.0–1.0).
    Weights: symptom_severity=0.35, vital_abnormality=0.35, history=0.20, age=0.10
    """
    # Symptom severity
    symptom_list = _parse_list(symptoms)
    if symptom_list:
        severities = [SYMPTOM_SEVERITY.get(s, 0.35) for s in symptom_list]
        symptom_score = sum(severities) / len(severities)
    else:
        symptom_score = 0.0

    # Vital abnormality
    vital_scores = []
    for vital_name, value in vitals.items():
        if value is not None:
            vital_scores.append(_compute_vital_deviation(value, vital_name))
    vital_score = sum(vital_scores) / len(vital_scores) if vital_scores else 0.0

    # History risk
    history_list = _parse_list(medical_history)
    history_score = sum(HISTORY_RISK.get(h, 0.1) for h in history_list)
    history_score = min(history_score, 1.0)

    # Age factor
    age_score = min(max(age / 100.0, 0.0), 1.0) if age else 0.0

    risk = (0.35 * symptom_score +
            0.35 * vital_score +
            0.20 * history_score +
            0.10 * age_score)

    return round(min(max(risk, 0.0), 1.0), 2)


def compute_urgency_score(symptoms, vitals, symptom_duration):
    """
    Compute urgency score (0.0–1.0).
    Weights: symptom_severity=0.40, vital_abnormality=0.45, duration=0.15
    """
    # Symptom severity
    symptom_list = _parse_list(symptoms)
    if symptom_list:
        severities = [SYMPTOM_SEVERITY.get(s, 0.35) for s in symptom_list]
        symptom_score = sum(severities) / len(severities)
    else:
        symptom_score = 0.0

    # Vital abnormality
    vital_scores = []
    for vital_name, value in vitals.items():
        if value is not None:
            vital_scores.append(_compute_vital_deviation(value, vital_name))
    vital_score = sum(vital_scores) / len(vital_scores) if vital_scores else 0.0

    # Duration urgency
    duration_score = 0.5  # default
    if symptom_duration:
        duration_lower = symptom_duration.lower().strip()
        for keyword, score in DURATION_URGENCY.items():
            if keyword in duration_lower:
                duration_score = score
                break

    urgency = (0.40 * symptom_score +
               0.45 * vital_score +
               0.15 * duration_score)

    return round(min(max(urgency, 0.0), 1.0), 2)


def compute_adherence_score(adherence_info):
    """
    Compute adherence score (0.0–1.0).
    Equal weight of: medication, appointments, diet, exercise.
    """
    if not adherence_info:
        return 0.5  # default neutral

    # Medication adherence
    missed_meds = adherence_info.get("missed_medications_per_week", 0)
    med_score = max(1 - (missed_meds / 7.0), 0.0)

    # Appointment attendance
    missed_appts = adherence_info.get("missed_appointments_last_6months", 0)
    appt_score = max(1 - (missed_appts / 6.0), 0.0)

    # Diet compliance
    diet_score = 1.0 if adherence_info.get("follows_diet_plan", False) else 0.0

    # Exercise compliance
    exercise_score = 1.0 if adherence_info.get("exercises_regularly", False) else 0.0

    adherence = (med_score + appt_score + diet_score + exercise_score) / 4.0

    return round(min(max(adherence, 0.0), 1.0), 2)
