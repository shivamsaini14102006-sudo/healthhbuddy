# 🏥 Healthcare Operating System

An intelligent, real-time clinical decision support system that computes patient risk scores, classifies urgency levels, and generates structured summaries for doctors and patients.

## Features

- **Patient Intake Form** — Collect symptoms, vitals, medical history, and adherence data
- **Scoring Engine** — Compute Risk, Urgency, and Adherence scores (0–1)
- **Decision Engine** — Classify patients as CRITICAL, LOW ADHERENCE, or NORMAL
- **AI Summary Service** — Generate structured Doctor Summaries, Patient Instructions, and Workflow Actions
- **Doctor Dashboard** — Visualize scores with animated gauges, view prioritized insights

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
cd "health care"
pip install flask flask-cors
```

### Run

```bash
python backend/app.py
```

Open **http://localhost:5000** in your browser.

## Project Structure

```
healthcare-os/
├── frontend/
│   ├── index.html          # Patient intake + Doctor dashboard
│   ├── index.css           # Design system (dark mode, glassmorphism)
│   └── app.js              # Client-side logic and API calls
├── backend/
│   ├── app.py              # Flask API server
│   ├── scoring_engine.py   # Risk, Urgency, Adherence computation
│   ├── decision_engine.py  # Classification and recommendations
│   └── ai_service.py       # Summary generation
├── architecture.md
├── systemDesign.md
├── api-contracts.md
├── scoring-engine-spec.md
├── prompt.txt
└── README.md
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/assess` | POST | Submit patient data, receive full assessment |

See [api-contracts.md](api-contracts.md) for full request/response schemas.

## How It Works

1. Patient enters symptoms, vitals, and history via the web form
2. Backend computes three scores using rule-based algorithms
3. Decision engine classifies the patient and generates recommendations
4. AI service creates structured summaries for doctors and patients
5. Doctor dashboard displays the complete assessment with visual gauges

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **No external dependencies** — runs fully offline
