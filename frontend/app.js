/**
 * Healthcare OS — Client Application
 * Handles form submission, API calls, view navigation, and dashboard rendering.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// DOM References
// ═══════════════════════════════════════════════════════════════════════════════
const $ = (id) => document.getElementById(id);

const DOM = {
    // Navigation
    navIntake:    $('navIntake'),
    navDashboard: $('navDashboard'),
    intakeView:   $('intakeView'),
    dashboardView:$('dashboardView'),
    dashboardContent: $('dashboardContent'),

    // Buttons
    btnAssess: $('btnAssess'),
    btnReset:  $('btnReset'),

    // Loading
    loadingOverlay: $('loadingOverlay'),

    // Patient Info
    patientName:   $('patientName'),
    patientAge:    $('patientAge'),
    patientGender: $('patientGender'),

    // Symptoms
    symptoms:        $('symptoms'),
    symptomDuration: $('symptomDuration'),

    // Vitals
    heartRate:    $('heartRate'),
    bpSystolic:   $('bpSystolic'),
    bpDiastolic:  $('bpDiastolic'),
    temperature:  $('temperature'),
    spo2:         $('spo2'),

    // History
    medicalHistory: $('medicalHistory'),
    currentMeds:    $('currentMeds'),

    // Adherence
    missedMeds:         $('missedMeds'),
    missedAppts:        $('missedAppts'),
    followsDiet:        $('followsDiet'),
    exercisesRegularly: $('exercisesRegularly'),
};

// ═══════════════════════════════════════════════════════════════════════════════
// Navigation
// ═══════════════════════════════════════════════════════════════════════════════
function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

    if (viewName === 'dashboard') {
        DOM.dashboardView.classList.add('active');
        DOM.navDashboard.classList.add('active');
    } else {
        DOM.intakeView.classList.add('active');
        DOM.navIntake.classList.add('active');
    }
}

DOM.navIntake.addEventListener('click', () => switchView('intake'));
DOM.navDashboard.addEventListener('click', () => switchView('dashboard'));

// ═══════════════════════════════════════════════════════════════════════════════
// Form Data Collection
// ═══════════════════════════════════════════════════════════════════════════════
function collectFormData() {
    return {
        name:              DOM.patientName.value.trim() || 'Anonymous Patient',
        age:               parseInt(DOM.patientAge.value) || 30,
        gender:            DOM.patientGender.value || 'unspecified',
        symptoms:          DOM.symptoms.value.trim(),
        symptom_duration:  DOM.symptomDuration.value || '',
        medical_history:   DOM.medicalHistory.value.trim(),
        current_medications: DOM.currentMeds.value.trim(),
        vitals: {
            heart_rate:              DOM.heartRate.value ? parseInt(DOM.heartRate.value) : null,
            blood_pressure_systolic: DOM.bpSystolic.value ? parseInt(DOM.bpSystolic.value) : null,
            blood_pressure_diastolic:DOM.bpDiastolic.value ? parseInt(DOM.bpDiastolic.value) : null,
            temperature:             DOM.temperature.value ? parseFloat(DOM.temperature.value) : null,
            spo2:                    DOM.spo2.value ? parseInt(DOM.spo2.value) : null,
        },
        adherence_info: {
            missed_medications_per_week:      parseInt(DOM.missedMeds.value) || 0,
            missed_appointments_last_6months: parseInt(DOM.missedAppts.value) || 0,
            follows_diet_plan:                DOM.followsDiet.checked,
            exercises_regularly:              DOM.exercisesRegularly.checked,
        },
    };
}

// ═══════════════════════════════════════════════════════════════════════════════
// API Call
// ═══════════════════════════════════════════════════════════════════════════════
async function submitAssessment(data) {
    const response = await fetch('/api/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || `Server error: ${response.status}`);
    }

    return response.json();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Assessment Handler
// ═══════════════════════════════════════════════════════════════════════════════
DOM.btnAssess.addEventListener('click', async () => {
    // Validate
    if (!DOM.symptoms.value.trim()) {
        DOM.symptoms.style.borderColor = 'var(--accent-rose)';
        DOM.symptoms.focus();
        DOM.symptoms.setAttribute('placeholder', '⚠️ Please enter at least one symptom');
        setTimeout(() => {
            DOM.symptoms.style.borderColor = '';
            DOM.symptoms.setAttribute('placeholder', 'e.g. chest pain, shortness of breath, dizziness');
        }, 3000);
        return;
    }

    // Show loading
    DOM.loadingOverlay.classList.add('active');
    DOM.btnAssess.disabled = true;

    try {
        const data = collectFormData();
        const result = await submitAssessment(data);
        renderDashboard(result);
        switchView('dashboard');
    } catch (err) {
        alert('Assessment failed: ' + err.message);
    } finally {
        DOM.loadingOverlay.classList.remove('active');
        DOM.btnAssess.disabled = false;
    }
});

// ═══════════════════════════════════════════════════════════════════════════════
// Reset Handler
// ═══════════════════════════════════════════════════════════════════════════════
DOM.btnReset.addEventListener('click', () => {
    DOM.patientName.value = '';
    DOM.patientAge.value = '';
    DOM.patientGender.value = '';
    DOM.symptoms.value = '';
    DOM.symptomDuration.value = '';
    DOM.heartRate.value = '';
    DOM.bpSystolic.value = '';
    DOM.bpDiastolic.value = '';
    DOM.temperature.value = '';
    DOM.spo2.value = '';
    DOM.medicalHistory.value = '';
    DOM.currentMeds.value = '';
    DOM.missedMeds.value = '0';
    DOM.missedAppts.value = '0';
    DOM.followsDiet.checked = false;
    DOM.exercisesRegularly.checked = false;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Dashboard Rendering
// ═══════════════════════════════════════════════════════════════════════════════
function renderDashboard(data) {
    const cls = data.classification;
    const clsLower = cls === 'LOW_ADHERENCE' ? 'low-adherence' : cls.toLowerCase();
    const scores = data.scores;
    const detail = data.classification_detail;
    const ctx = data.patient_context;
    const doc = data.doctor_summary;
    const inst = data.patient_instructions;
    const wf = data.workflow_actions;

    // Classification icon
    const clsIcon = cls === 'CRITICAL' ? '🚨' : cls === 'LOW_ADHERENCE' ? '⚠️' : '✅';

    // Score colors
    const riskColor = getScoreColor(scores.risk, false);
    const urgencyColor = getScoreColor(scores.urgency, false);
    const adherenceColor = getScoreColor(scores.adherence, true);

    DOM.dashboardContent.innerHTML = `
        <!-- Classification Banner -->
        <div class="classification-banner ${clsLower} animate-in delay-1">
            <div class="classification-icon">${clsIcon}</div>
            <div class="classification-info">
                <div class="classification-label">${detail.escalation_level} Priority</div>
                <div class="classification-title">${formatClassification(cls)}</div>
                <div class="classification-subtitle">${detail.label}</div>
            </div>
        </div>

        <!-- Patient Context Bar -->
        <div class="patient-context-bar animate-in delay-1">
            <div class="context-chip">
                <span class="chip-icon">👤</span>
                <strong>${escHtml(ctx.name)}</strong>
            </div>
            <div class="context-chip">
                <span class="chip-icon">🎂</span>
                ${ctx.age} years, ${ctx.gender}
            </div>
            <div class="context-chip">
                <span class="chip-icon">⏱️</span>
                Duration: ${escHtml(ctx.symptom_duration)}
            </div>
            <div class="context-chip">
                <span class="chip-icon">💊</span>
                ${escHtml(ctx.current_medications || 'No medications reported')}
            </div>
        </div>

        <!-- Score Gauges -->
        <div class="scores-grid animate-in delay-2">
            ${renderScoreCard('Risk Score', scores.risk, riskColor, 'Likelihood of adverse outcome')}
            ${renderScoreCard('Urgency', scores.urgency, urgencyColor, 'How quickly intervention is needed')}
            ${renderScoreCard('Adherence', scores.adherence, adherenceColor, 'Patient compliance with care plan')}
        </div>

        <!-- Dashboard Content -->
        <div class="dashboard-grid">
            <!-- Doctor Summary: Key Issues -->
            <div class="card animate-in delay-3">
                <div class="card-header">
                    <div class="card-icon rose">⚕️</div>
                    <div>
                        <div class="card-title">Key Issues</div>
                        <div class="card-subtitle">${doc.risk_level}</div>
                    </div>
                </div>
                <ul class="info-list">
                    ${doc.key_issues.map(i => `<li><span class="list-icon">•</span>${escHtml(i)}</li>`).join('')}
                </ul>
            </div>

            <!-- Doctor Summary: Recommended Actions -->
            <div class="card animate-in delay-3">
                <div class="card-header">
                    <div class="card-icon indigo">📋</div>
                    <div>
                        <div class="card-title">Recommended Actions</div>
                        <div class="card-subtitle">Clinical recommendations</div>
                    </div>
                </div>
                <ul class="info-list">
                    ${doc.recommended_actions.map(a => `<li><span class="list-icon">→</span>${escHtml(a)}</li>`).join('')}
                </ul>
            </div>

            <!-- Patient Instructions -->
            <div class="card animate-in delay-4">
                <div class="card-header">
                    <div class="card-icon emerald">💬</div>
                    <div>
                        <div class="card-title">Patient Instructions</div>
                        <div class="card-subtitle">Simple guidance for the patient</div>
                    </div>
                </div>
                <ul class="info-list">
                    ${inst.steps.map(s => `<li><span class="list-icon">✦</span>${escHtml(s)}</li>`).join('')}
                </ul>
                ${inst.warnings.length ? `
                <ul class="warning-list">
                    ${inst.warnings.map(w => `<li><span class="list-icon">⚠️</span>${escHtml(w)}</li>`).join('')}
                </ul>` : ''}
            </div>

            <!-- Workflow Actions -->
            <div class="card animate-in delay-4">
                <div class="card-header">
                    <div class="card-icon cyan">⚡</div>
                    <div>
                        <div class="card-title">Workflow Actions</div>
                        <div class="card-subtitle">Scheduling, alerts, and follow-ups</div>
                    </div>
                </div>

                ${wf.appointments.length ? `
                <div style="margin-bottom: 12px;">
                    <div style="font-size:0.78rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">📅 Appointments</div>
                    ${wf.appointments.map(a => `<div class="alert-item info-alert"><span>📅</span>${escHtml(a)}</div>`).join('')}
                </div>` : ''}

                ${wf.alerts.length ? `
                <div style="margin-bottom: 12px;">
                    <div style="font-size:0.78rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">🔔 Alerts</div>
                    ${wf.alerts.map(a => {
                        const alertClass = a.includes('CRITICAL') ? 'critical-alert' : 'warning-alert';
                        return `<div class="alert-item ${alertClass}"><span>🔔</span>${escHtml(a)}</div>`;
                    }).join('')}
                </div>` : ''}

                ${wf.follow_ups.length ? `
                <div>
                    <div style="font-size:0.78rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">🔄 Follow-ups</div>
                    ${wf.follow_ups.map(f => `<div class="alert-item info-alert"><span>🔄</span>${escHtml(f)}</div>`).join('')}
                </div>` : ''}
            </div>

            <!-- Vitals Summary -->
            <div class="card full-width animate-in delay-5">
                <div class="card-header">
                    <div class="card-icon amber">📊</div>
                    <div>
                        <div class="card-title">Vitals Summary</div>
                        <div class="card-subtitle">${escHtml(ctx.vitals_summary)}</div>
                    </div>
                </div>
                <div class="info-list" style="display:flex; flex-wrap:wrap; gap:12px;">
                    ${ctx.symptoms_list.map(s => `
                        <span class="context-chip" style="background:rgba(244,63,94,0.08); border-color:rgba(244,63,94,0.15); color:#fda4af;">
                            🩺 ${escHtml(s)}
                        </span>
                    `).join('')}
                </div>
            </div>
        </div>

        <!-- New Assessment Button -->
        <div class="form-actions animate-in delay-6" style="margin-top:32px;">
            <button class="btn btn-secondary btn-lg" onclick="switchView('intake')">
                ← New Assessment
            </button>
        </div>
    `;

    // Animate gauges after render
    requestAnimationFrame(() => {
        setTimeout(animateGauges, 100);
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Gauge Rendering & Animation
// ═══════════════════════════════════════════════════════════════════════════════
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 45; // radius=45

function renderScoreCard(label, value, color, description) {
    const percentage = Math.round(value * 100);
    const offset = GAUGE_CIRCUMFERENCE * (1 - value);

    return `
        <div class="score-card">
            <div class="gauge-container">
                <svg class="gauge-svg" viewBox="0 0 100 100">
                    <circle class="gauge-bg" cx="50" cy="50" r="45"/>
                    <circle class="gauge-fill" cx="50" cy="50" r="45"
                        stroke="${color}"
                        stroke-dasharray="${GAUGE_CIRCUMFERENCE}"
                        stroke-dashoffset="${GAUGE_CIRCUMFERENCE}"
                        data-target-offset="${offset}"/>
                </svg>
                <div class="gauge-value" style="color:${color}">${percentage}%</div>
            </div>
            <div class="score-label">${label}</div>
            <div class="score-description">${description}</div>
        </div>
    `;
}

function animateGauges() {
    document.querySelectorAll('.gauge-fill').forEach(circle => {
        const targetOffset = circle.getAttribute('data-target-offset');
        circle.style.strokeDashoffset = targetOffset;
    });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════════
function getScoreColor(value, isAdherence) {
    if (isAdherence) {
        // For adherence: high = good (green), low = bad (red)
        if (value >= 0.7) return '#10b981';
        if (value >= 0.4) return '#f59e0b';
        return '#ef4444';
    } else {
        // For risk/urgency: high = bad (red), low = good (green)
        if (value >= 0.8) return '#ef4444';
        if (value >= 0.6) return '#f59e0b';
        if (value >= 0.3) return '#06b6d4';
        return '#10b981';
    }
}

function formatClassification(cls) {
    switch (cls) {
        case 'CRITICAL':       return 'Critical — Immediate Escalation';
        case 'LOW_ADHERENCE':  return 'Low Adherence — Engagement Required';
        case 'NORMAL':         return 'Normal — Standard Care';
        default:               return cls;
    }
}

function escHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
