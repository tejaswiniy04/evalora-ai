# 🎯 Evalora AI
### AI-Powered Structured Interview & Candidate Evaluation Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://evalora-ai.streamlit.app)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![LLM Engine](https://img.shields.io/badge/LLM-Groq%20Llama--3.1--8B-purple.svg)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Evalora AI** is an end-to-end autonomous interview system designed for modern recruiting. It generates role-tailored questions, records voice/text responses, scores each answer in real-time, builds structured glassmorphic candidate evaluations, and emails publication-ready PDF reports directly to hiring managers.

🌐 **Live Web Application:** [evalora-ai.streamlit.app](https://evalora-ai.streamlit.app)

---

## ✨ Features at a Glance

| Feature | Description |
|---|---|
| 🔐 **User Authentication** | Sign In & Sign Up system with persistent user state (`auth.py` + `users.json`) |
| 💻 **Glassmorphic Web App** | Modern Streamlit UI (`app.py`) featuring glass cards, top accent strips, and animated feedback |
| 🎙️ **Voice & Text Answering** | Dual-mode response: Speech-to-Text powered by **Groq Whisper (`whisper-large-v3`)** or typed text |
| 🎯 **7-Question Structure** | Role-tailored question set: **Technical ×3, Behavioral ×2, Situational ×1, Motivation ×1** |
| ⚡ **Real-Time Answer Scoring** | Immediate 1–10 score with animated feedback card detailing **Strengths** and **Areas to Improve** |
| 📊 **Weighted Evaluation** | Final Score = `40% Technical + 25% Behavioral + 20% Situational + 15% Motivation` |
| 🏆 **4-Tier Recommendation** | `STRONGLY RECOMMEND` • `RECOMMEND` • `BORDERLINE` • `DO NOT RECOMMEND` |
| 📄 **PDF Evaluation Export** | Styled 2-page candidate evaluation report generated via `fpdf2` (`pdf_generator.py`) |
| 📧 **Auto-Email Notifications** | Background Gmail SMTP engine (`email_notifier.py`) sends result summaries + PDF attachments |
| 🧠 **10 Predefined Roles + Custom** | Select from top tech roles or type custom titles to generate AI-suggested skill sets |
| 🖥️ **Dual Interface (Web + CLI)** | Run interactively in browser (`app.py`) or as a rich terminal application (`agent.py`) |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed on your machine
- A free [Groq API key](https://console.groq.com) *(takes ~1 minute)*
- *(Optional)* Gmail App Password for sending email notifications

### 2. Installation & Setup

```bash
# Clone repository
git clone https://github.com/tejaswiniy04/evalora-ai.git
cd evalora-ai

# Create & activate virtual environment
# Windows:
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables Configuration

Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and fill in your keys:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
ADMIN_EMAIL=admin@yourdomain.com
```

### 4. Launch Web Application

```bash
streamlit run app.py
```
*Access the app in your browser at `http://localhost:8501`.*

---

## 🌐 Cloud Deployment Options

### Option 1: Streamlit Community Cloud (Free 1-Click Host)
1. Push repository to **GitHub**.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → **New app**.
3. Select repo, branch (`main`), and set Main file path to `app.py`.
4. In **Advanced Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxx"
   GMAIL_USER = "your_email@gmail.com"
   GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
   ADMIN_EMAIL = "admin@yourdomain.com"
   ```
5. Click **Deploy!**

### Option 2: Hugging Face Spaces / Render / Docker
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## 🖥️ Terminal Mode (CLI Agent)

Evalora AI can also be run entirely from the command line:

```powershell
# Interactive Live CLI Session
$env:PYTHONUTF8=1; python agent.py

# Pre-filled Role & Name via Flags
python agent.py --role "Data Scientist" --skills "Python,SQL,ML" --name "Alice"

# Demo Mode (Replay sample transcript without API key)
python agent.py --demo
```

---

## 📁 System Architecture & Directory Structure

```
evalora-ai/
├── app.py                     # Streamlit Web App — Main interactive UI & dashboard
├── agent.py                   # CLI Orchestrator — Rich terminal interview application
├── answer_scorer.py           # Real-Time Scorer — Evaluates individual Q&A (1–10)
├── auth.py                    # User Auth Engine — Sign In / Sign Up logic with users.json
├── email_notifier.py          # SMTP Email Engine — Dispatches candidate PDF results
├── evaluator.py               # Final Evaluation Engine — Generates weighted assessment
├── pdf_generator.py           # PDF Engine — Builds styled 2-page PDF report (fpdf2)
├── question_generator.py      # Question Engine — Generates 7 role-specific questions
├── session.py                 # Session State — Holds candidate data & JSON transcripts
├── transcriber.py             # Voice Engine — Groq Whisper audio transcription
├── requirements.txt           # Dependency requirements manifest
├── .env.example               # Environment variables template file
├── users.json                 # User accounts database (auto-managed)
├── sample_transcripts/
│   └── sample_interview.json  # Pre-computed demo transcript (Junior ML Engineer)
└── transcripts/               # Saved live session JSON transcripts
```

---

## 📊 Scoring & Evaluation Formula

### 1. Per-Answer Category Weights

Each question is tagged with a category and scored on a 1–10 scale:

| Category | Questions | Evaluation Criteria |
|---|---|---|
| **Technical** (40%) | Q1, Q2, Q3 | Accuracy, depth of knowledge, problem solving |
| **Behavioral** (25%) | Q4, Q5 | STAR structure, impact, team collaboration |
| **Situational** (20%) | Q6 | Logical reasoning, decision-making under constraints |
| **Motivation** (15%) | Q7 | Role alignment, growth mindset, enthusiasm |

### 2. Weighted Overall Score (out of 100)

$$\text{Final Score} = \left( \overline{S}_{\text{Tech}} \times 0.40 + \overline{S}_{\text{Behav}} \times 0.25 + \overline{S}_{\text{Sit}} \times 0.20 + \overline{S}_{\text{Motiv}} \times 0.15 \right) \times 10$$

### 3. Recommendation Tiers

| Score Range | Tier | Status Pill |
|---|---|---|
| **80 – 100** | **STRONGLY RECOMMEND** | 🟢 Green Pill |
| **65 – 79** | **RECOMMEND** | 🟢 Emerald Pill |
| **50 – 64** | **BORDERLINE** | 🟡 Amber Pill |
| **0 – 49** | **DO NOT RECOMMEND** | 🔴 Red Pill |

---

## 🧠 Predefined Job Roles

1. **Software Engineer** — *Python, Java, Data Structures, System Design*
2. **Frontend Developer** — *JavaScript, React, HTML/CSS, TypeScript*
3. **Backend Engineer** — *Python, FastAPI, PostgreSQL, Redis, Docker*
4. **Full Stack Developer** — *JavaScript, Node.js, React, MongoDB*
5. **Data Scientist** — *Python, SQL, Machine Learning, Pandas, Statistics*
6. **Machine Learning Engineer** — *Python, PyTorch, Deep Learning, MLOps, NLP*
7. **Data Engineer** — *Python, SQL, Apache Spark, Airflow, BigQuery*
8. **DevOps / Cloud Engineer** — *Docker, Kubernetes, AWS, CI/CD, Terraform*
9. **Cybersecurity Analyst** — *Network Security, Python, Penetration Testing, SIEM*
10. **Product Manager** — *Product Strategy, Agile, User Research, Data Analytics*
11. **Custom Role** — *Enter any title & auto-suggest skills via AI*

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.30.0 | Web application dashboard framework |
| `groq` | 1.6.0 | Groq LLM API client + Whisper transcription |
| `fpdf2` | ≥ 2.7.8 | Styled PDF document generator |
| `python-dotenv` | 1.0.1 | Environment `.env` file reader |
| `rich` | 13.7.1 | Terminal color and table layout (CLI mode) |

---

## 📄 License & Attribution

© 2026 **Evalora AI**. All rights reserved.  
Designed and built for structured, unbiased, AI-powered hiring.
