# 🎯 Evalora AI
### AI-Powered Structured Interview & Evaluation Agent

**Evalora AI** is an end-to-end AI interview platform that generates role-specific questions,
scores each answer in real time, produces a comprehensive PDF evaluation report,
and automatically emails results — all through a sleek Streamlit web interface.

---

## ✨ Features

| Feature | Details |
|---|---|
| **User Authentication** | Secure Sign In & Sign Up with persistent accounts stored in `users.json` |
| **Web Application** | Premium light-themed Streamlit dashboard (`app.py`) with glassmorphism header |
| **Voice Answering** | Speech-to-Text microphone recording via Groq **Whisper (`whisper-large-v3`)** |
| **PDF Export** | Styled 2-page candidate evaluation PDF report via `fpdf2` |
| **Email Notifications** | Auto-email interview results to both the admin and the candidate via Gmail SMTP |
| **Question Generation** | 7 role-specific questions: Technical × 3, Behavioral × 2, Situational × 1, Motivation × 1 |
| **Live Answer Scoring** | Each answer scored 1–10 with instant feedback card (strengths + improvement) |
| **Animated Score Card** | Score feedback card with entrance animations, score pill, and two-column grid |
| **Weighted Final Score** | `40% Technical + 25% Behavioral + 20% Situational + 15% Motivation` |
| **Recommendation Tier** | STRONGLY RECOMMEND / RECOMMEND / BORDERLINE / DO NOT RECOMMEND |
| **10 Predefined Roles** | Software Engineer, ML Engineer, Data Scientist, DevOps, Product Manager, and more |
| **Custom Role Support** | Enter any job title + skills to generate a fully tailored interview |
| **Transcript Saving** | Each session auto-saved as a JSON transcript in `transcripts/` |
| **Demo Mode** | Replay a pre-run Junior ML Engineer transcript — no API key required |

---

## 🌐 Web Application

### Run Locally
```bash
# Activate virtual environment first
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # macOS / Linux

# Then start the app
streamlit run app.py
```

Opens at **http://localhost:8501** (or the port shown in the terminal).

### 🚀 Deploy to Cloud

#### Option 1 — Streamlit Community Cloud (Recommended, Free)
1. Push this repo to **GitHub**.
2. Visit [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch `main`, and set **Main file path** to `app.py`.
4. Under **Advanced Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"
   GMAIL_USER = "your_sender@gmail.com"
   GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
   ADMIN_EMAIL = "admin@yourdomain.com"
   ```
5. Click **Deploy!** — your app is live in seconds.

#### Option 2 — Hugging Face Spaces
1. Create a new Space → choose **Streamlit** SDK.
2. Upload all project files or connect your GitHub repo.
3. Add secrets under **Repository Secrets**.

#### Option 3 — Render / Railway / Docker
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## ⚙️ Setup

### Prerequisites
- Python **3.10+**
- A free [Groq API key](https://console.groq.com) *(~2 min to get)*
- Gmail account with an [App Password](https://myaccount.google.com/apppasswords) *(for email notifications)*

### 1. Clone the repository
```bash
git clone https://github.com/tejaswiniy04/evalora-ai.git
cd evalora-ai
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and fill in your values:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GMAIL_USER=your_sender@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
ADMIN_EMAIL=admin@yourdomain.com
```

---

## 🖥️ CLI Usage (Terminal Mode)

### Interactive interview
```powershell
# Windows (PowerShell)
$env:PYTHONUTF8=1; .\venv\Scripts\python.exe agent.py

# macOS / Linux
python agent.py
```

You will be prompted for candidate name, role (1–10 from predefined list or option 11 for custom), and skills.
Answer each of the 7 questions. Press **Enter twice** to submit each answer.

### Pre-fill via flags
```bash
python agent.py --role "Data Scientist" --skills "Python,SQL,Statistics" --name "Alice"
```

### Demo mode (no API key needed)
```powershell
# Windows
$env:PYTHONUTF8=1; python agent.py --demo

# macOS / Linux
python agent.py --demo
```
Replays `sample_transcripts/sample_interview.json` — a realistic Junior ML Engineer interview with scores and evaluation.

---

## 📁 Project Structure

```
evalora-ai/
├── app.py                     # Streamlit Web Application — main entry point
├── agent.py                   # CLI entry point — terminal interview orchestrator
├── answer_scorer.py           # LLM-based per-answer scoring (1–10 + feedback)
├── auth.py                    # User authentication (sign up / sign in)
├── email_notifier.py          # Gmail SMTP email notifications (admin + candidate)
├── evaluator.py               # Final weighted evaluation report generator
├── pdf_generator.py           # Styled 2-page PDF report builder (fpdf2)
├── question_generator.py      # LLM-powered question generation (7 per session)
├── session.py                 # Session state + JSON transcript persistence
├── transcriber.py             # Groq Whisper audio transcription (voice answers)
├── run.bat                    # Windows batch launcher (--demo / --live / --web)
├── requirements.txt           # Pinned Python dependencies
├── .env.example               # Environment variable template
├── users.json                 # Persistent user account store (auto-created)
├── sample_transcripts/
│   └── sample_interview.json  # Pre-run demo transcript (Junior ML Engineer)
└── transcripts/               # Auto-created — live session transcripts saved here
```

---

## 🧠 Predefined Job Roles

| # | Role | Key Skills |
|---|---|---|
| 1 | Software Engineer | Python, Java, Data Structures, System Design |
| 2 | Frontend Developer | JavaScript, React, HTML/CSS, TypeScript |
| 3 | Backend Engineer | Python, FastAPI, PostgreSQL, Redis, Docker |
| 4 | Full Stack Developer | JavaScript, Node.js, React, MongoDB |
| 5 | Data Scientist | Python, SQL, Machine Learning, Pandas, Statistics |
| 6 | Machine Learning Engineer | Python, PyTorch, Deep Learning, MLOps, NLP |
| 7 | Data Engineer | Python, SQL, Apache Spark, Airflow, BigQuery |
| 8 | DevOps / Cloud Engineer | Docker, Kubernetes, AWS, CI/CD, Terraform |
| 9 | Cybersecurity Analyst | Network Security, Python, Penetration Testing, SIEM |
| 10 | Product Manager | Product Strategy, Agile, User Research, Data Analytics |

Or type any custom role + skills for a fully tailored interview.

---

## 📊 Scoring Method

### Per-Answer Score (1–10)

| Category | Scoring Criteria |
|---|---|
| Technical | Accuracy, depth of knowledge, correctness |
| Behavioral | STAR structure, specificity, demonstrated impact |
| Situational | Logical reasoning, practical approach |
| Motivation | Authenticity, alignment with role |

**Score bands:**

| Score | Label | Card Color |
|---|---|---|
| 8–10 | Excellent | 🟢 Green |
| 6–7 | Good | 🟡 Amber |
| 1–5 | Needs Work | 🔴 Red |

### Final Score (out of 100)

```
Final = (avg_Technical  × 0.40
       + avg_Behavioral × 0.25
       + avg_Situational × 0.20
       + avg_Motivation  × 0.15) × 10
```

### Recommendation Tiers

| Score | Recommendation |
|---|---|
| 80–100 | ✅ STRONGLY RECOMMEND |
| 65–79  | ✅ RECOMMEND |
| 50–64  | ⚠️ BORDERLINE |
| 0–49   | ❌ DO NOT RECOMMEND |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `groq` | 1.6.0 | Groq LLM API + Whisper transcription |
| `python-dotenv` | 1.0.1 | Load `.env` variables |
| `rich` | 13.7.1 | Terminal UI (CLI mode) |
| `streamlit` | ≥ 1.30.0 | Web application framework |
| `starlette` | < 0.40.0 | Streamlit compatibility pin |
| `fpdf2` | ≥ 2.7.8 | PDF report generation |

---

## 🔁 Quick-Start Checklist

| Step | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Copy env | `cp .env.example .env` (macOS/Linux) / `copy .env.example .env` (Windows) |
| Add Groq key | Edit `.env` → set `GROQ_API_KEY` |
| Add email creds | Edit `.env` → set `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `ADMIN_EMAIL` |
| Run Web App | `streamlit run app.py` |
| Demo (Windows) | `$env:PYTHONUTF8=1; python agent.py --demo` |
| Demo (Mac/Linux) | `python agent.py --demo` |
| Live CLI interview | `python agent.py` |

---

## ⚖️ Design Decisions & Tradeoffs

**LLM: Groq (`llama-3.1-8b-instant`)**
Free tier, no credit card required. ~1–2 s inference keeps the interview responsive.
For better evaluation depth, switch to `llama-3.3-70b-versatile` (also free on Groq).

**Dynamic question generation**
Works for any role/skill set without pre-coded question banks. Mitigated JSON parse errors with robust fallback parsing in every module.

**LLM scoring (vs. embedding similarity)**
Embeddings cannot evaluate reasoning quality or STAR structure. Temperature set to 0.3 for near-deterministic scoring.

**Weighted category scoring**
More honest than a flat average — a strong behavioural score does not mask weak technical answers.

---

## Known Limitations

1. **Single-round only** — no adaptive follow-up questions based on score.
2. **English only** — multilingual interviews are untested.
3. **No candidate database** — sessions are saved as standalone JSON files.
4. **LLM dependency** — requires Groq API availability.

---

## 📄 License

© 2025 Evalora AI. All rights reserved.
