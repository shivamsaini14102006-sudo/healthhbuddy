"""
Healthcare OS — Decision Engine
Classifies patients and generates recommendations based on computed scores.
"""


def classify_patient(risk_score, urgency_score, adherence_score):
    """
    Apply decision logic:
      IF Risk > 0.8 AND Urgency > 0.7 → CRITICAL
      ELSE IF Adherence < 0.4 → LOW_ADHERENCE
      ELSE → NORMAL

    Returns dict with classification and recommended actions.
    """

    if risk_score > 0.8 and urgency_score > 0.7:
        return _critical_classification(risk_score, urgency_score, adherence_score)
    elif adherence_score < 0.4:
        return _low_adherence_classification(risk_score, urgency_score, adherence_score)
    else:
        return _normal_classification(risk_score, urgency_score, adherence_score)


def _critical_classification(risk, urgency, adherence):
    """Generate CRITICAL classification response."""
    return {
        "classification": "CRITICAL",
        "severity_label": "Immediate Attention Required",
        "color": "#ef4444",
        "recommendations": {
            "immediate_actions": [
                "Escalate to emergency department immediately",
                "Initiate continuous vital sign monitoring",
                "Prepare for urgent diagnostic workup",
                "Notify on-call specialist",
            ],
            "diagnostic_orders": [
                "Complete blood panel (CBC, BMP, cardiac enzymes)",
                "12-lead ECG",
                "Chest X-ray if respiratory symptoms present",
                "CT/MRI as clinically indicated",
            ],
            "monitoring": [
                "Continuous cardiac and SpO2 monitoring",
                "Vital signs every 15 minutes",
                "Neurological checks if altered consciousness",
            ],
        },
        "escalation_level": "EMERGENCY",
        "follow_up_timeline": "Within 24–48 hours post-stabilization",
    }


def _low_adherence_classification(risk, urgency, adherence):
    """Generate LOW_ADHERENCE classification response."""

    engagement_strategies = [
        "Schedule medication counseling session",
        "Simplify medication regimen where possible",
        "Set up automated medication reminders",
        "Discuss barriers to adherence with patient",
    ]

    if adherence < 0.2:
        engagement_strategies.extend([
            "Assign dedicated care coordinator",
            "Consider directly observed therapy if appropriate",
            "Evaluate social determinants of health",
        ])

    return {
        "classification": "LOW_ADHERENCE",
        "severity_label": "Engagement Intervention Needed",
        "color": "#f59e0b",
        "recommendations": {
            "immediate_actions": engagement_strategies,
            "care_adjustments": [
                "Review and simplify treatment plan",
                "Evaluate medication side effects",
                "Consider alternative delivery methods",
                "Assess financial barriers to medication access",
            ],
            "monitoring": [
                "Weekly check-in calls for 4 weeks",
                "Medication adherence tracking",
                "Bi-weekly vitals check",
            ],
        },
        "escalation_level": "MODERATE",
        "follow_up_timeline": "Within 1 week",
    }


def _normal_classification(risk, urgency, adherence):
    """Generate NORMAL classification response."""

    # Determine appropriate follow-up based on risk level
    if risk > 0.6:
        follow_up = "Within 2 weeks"
        monitoring = [
            "Monthly vitals check",
            "Lab work in 2 weeks",
            "Symptom diary maintenance",
        ]
    elif risk > 0.3:
        follow_up = "Within 1 month"
        monitoring = [
            "Quarterly vitals check",
            "Annual comprehensive review",
            "Self-monitoring of symptoms",
        ]
    else:
        follow_up = "Within 3 months"
        monitoring = [
            "Annual wellness checkup",
            "Standard preventive care schedule",
        ]

    return {
        "classification": "NORMAL",
        "severity_label": "Standard Care",
        "color": "#10b981",
        "recommendations": {
            "immediate_actions": [
                "Continue current treatment plan",
                "Reinforce healthy lifestyle habits",
                "Address any patient concerns",
            ],
            "preventive_care": [
                "Age-appropriate screenings",
                "Immunization updates",
                "Lifestyle counseling (diet, exercise, stress management)",
            ],
            "monitoring": monitoring,
        },
        "escalation_level": "LOW",
        "follow_up_timeline": follow_up,
    }
