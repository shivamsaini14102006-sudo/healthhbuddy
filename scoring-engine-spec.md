# Healthcare OS — Scoring Engine Specification

## Overview

Three independent scores are computed from patient data. Each score is a float in the range **[0.0, 1.0]** where higher values indicate greater severity (for Risk/Urgency) or better compliance (for Adherence).

---

## 1. Risk Score

Measures the overall clinical risk based on symptoms, vitals, and medical history.

### Components (weighted)

| Factor | Weight | Logic |
|--------|--------|-------|
| **Symptom severity** | 0.35 | Each symptom mapped to a severity value (0–1). Average of all symptom severities. |
| **Vital abnormality** | 0.35 | Each vital compared against normal ranges. Deviation normalized to 0–1. Average across all vitals. |
| **History risk factors** | 0.20 | Known conditions mapped to risk values. Sum capped at 1.0. |
| **Age factor** | 0.10 | Linear scaling: 0.0 at age 0, 1.0 at age 100. |

### Symptom Severity Map (examples)

| Symptom | Severity |
|---------|----------|
| chest pain | 0.95 |
| shortness of breath | 0.90 |
| seizure | 0.95 |
| severe bleeding | 0.95 |
| dizziness | 0.60 |
| headache | 0.40 |
| cough | 0.25 |
| mild fever | 0.20 |

### Vital Normal Ranges

| Vital | Normal Range | Critical Low | Critical High |
|-------|-------------|-------------|--------------|
| Heart Rate | 60–100 bpm | <40 | >150 |
| Systolic BP | 90–140 mmHg | <70 | >200 |
| Diastolic BP | 60–90 mmHg | <40 | >120 |
| Temperature | 97.0–99.5 °F | <95.0 | >104.0 |
| SpO2 | 95–100% | <85 | N/A |

---

## 2. Urgency Score

Measures how quickly intervention is needed.

### Components (weighted)

| Factor | Weight | Logic |
|--------|--------|-------|
| **Symptom severity** | 0.40 | Same mapping as Risk, but weighted more heavily |
| **Vital abnormality** | 0.45 | Same calculation as Risk, weighted more |
| **Duration factor** | 0.15 | Shorter duration = higher urgency. "minutes" → 1.0, "hours" → 0.7, "days" → 0.4, "weeks" → 0.2 |

---

## 3. Adherence Score

Measures patient compliance with prescribed care plan.

### Components (equal weight)

| Factor | Score | Logic |
|--------|-------|-------|
| **Medication adherence** | 0–1 | `1 - (missed_per_week / 7)`, capped at [0, 1] |
| **Appointment attendance** | 0–1 | `1 - (missed_6months / 6)`, capped at [0, 1] |
| **Diet compliance** | 0 or 1 | Boolean: follows_diet_plan |
| **Exercise compliance** | 0 or 1 | Boolean: exercises_regularly |

**Final**: Average of all four factors.

---

## Score Interpretation

| Score Range | Risk/Urgency Interpretation | Adherence Interpretation |
|------------|---------------------------|------------------------|
| 0.0 – 0.3 | Low | Poor |
| 0.3 – 0.6 | Moderate | Fair |
| 0.6 – 0.8 | High | Good |
| 0.8 – 1.0 | Critical | Excellent |
