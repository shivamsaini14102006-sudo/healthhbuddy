# Healthcare OS — API Contracts

## Base URL

```
http://localhost:5000
```

---

## `GET /api/health`

Health check endpoint.

**Response** `200 OK`
```json
{
  "status": "healthy",
  "service": "healthcare-os",
  "version": "1.0.0"
}
```

---

## `POST /api/assess`

Submit patient data for full clinical assessment.

### Request

**Content-Type**: `application/json`

```json
{
  "name": "Rajesh Kumar",
  "age": 58,
  "gender": "male",
  "symptoms": "chest pain, shortness of breath, dizziness",
  "symptom_duration": "2 hours",
  "medical_history": "hypertension, diabetes, previous heart attack",
  "current_medications": "metformin, atenolol, aspirin",
  "vitals": {
    "heart_rate": 110,
    "blood_pressure_systolic": 180,
    "blood_pressure_diastolic": 110,
    "temperature": 99.1,
    "spo2": 91
  },
  "adherence_info": {
    "missed_medications_per_week": 0,
    "missed_appointments_last_6months": 1,
    "follows_diet_plan": true,
    "exercises_regularly": false
  }
}
```

### Response `200 OK`

```json
{
  "patient_context": {
    "name": "Rajesh Kumar",
    "age": 58,
    "gender": "male",
    "symptoms_list": ["chest pain", "shortness of breath", "dizziness"],
    "vitals_summary": "HR: 110 bpm | BP: 180/110 mmHg | Temp: 99.1°F | SpO2: 91%"
  },
  "scores": {
    "risk": 0.92,
    "urgency": 0.88,
    "adherence": 0.75
  },
  "classification": "CRITICAL",
  "doctor_summary": {
    "key_issues": [
      "Acute chest pain with cardiac history",
      "Tachycardia (HR 110) with hypertensive crisis (180/110)",
      "Hypoxia (SpO2 91%)"
    ],
    "risk_level": "CRITICAL — Immediate attention required",
    "recommended_actions": [
      "Immediate cardiac evaluation",
      "12-lead ECG and troponin levels",
      "Continuous monitoring in emergency department"
    ]
  },
  "patient_instructions": {
    "steps": [
      "Stay calm and rest — do not exert yourself",
      "You need to see a doctor immediately",
      "If pain worsens, call emergency services (112)"
    ],
    "warnings": [
      "Do not drive yourself to the hospital",
      "Do not take any new medication without doctor approval"
    ]
  },
  "workflow_actions": {
    "appointments": ["Emergency department visit — IMMEDIATE"],
    "alerts": ["CRITICAL: Cardiac emergency — escalate to on-call cardiologist"],
    "follow_ups": ["Cardiology follow-up within 48 hours post-discharge"]
  }
}
```

### Error Response `400 Bad Request`

```json
{
  "error": "Missing required field: symptoms"
}
```
