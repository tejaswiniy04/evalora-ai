# 🎯 Interview Agent
### Rooman AI 24-Hour Challenge — CATEGORY 1: HR & Recruitment

An AI-powered structured interview system that generates role-specific questions,
scores each answer in real time, and produces a comprehensive evaluation report
with strengths, gaps, and a hire recommendation.

---

## Demo (no API key needed)

**Windows (PowerShell):**
```powershell
$env:PYTHONUTF8=1; python agent.py --demo
```

**macOS / Linux:**
```bash
python agent.py --demo
```

This replays a pre-run interview transcript of a Junior ML Engineer candidate
with all scores and the final evaluation — no setup required.

---

## Features

| Feature | Details |
|---|---|
| User Authentication | Secure Sign In & Sign Up system (`auth.py`) with persistent accounts (`users.json`) |
| Web Application | Modern Streamlit Web Dashboard UI (`app.py`) for browser-based interviews |
| Voice Answering | Speech-to-Text microphone recording using Groq Whisper API (`whisper-large-v3`) |
| PDF Export | Styled 2-page candidate evaluation PDF report generator (`pdf_generator.py`) |
| Question generation | 7 role-specific questions (Technical × 3, Behavioral × 2, Situational × 1, Motivation × 1) |
| Live answer scoring | Each answer scored 1–10 with feedback immediately after submission |
| Weighted evaluation | Final score = 40% Technical + 25% Behavioral + 20% Situational + 15% Motivation |
| Recommendation tier | STRONGLY RECOMMEND / RECOMMEND / BORDERLINE / DO NOT RECOMMEND |
| Output | PDF Evaluation Report download directly from Web UI |
| UI | Streamlit Web App & Rich terminal — colour-coded scores, progress tables |
| Demo mode | Replay pre-run transcript without any API key |

---

## 🌐 Web Application & Deployment

### Run Web App Locally
```bash
streamlit run app.py
```
*(Or on Windows, simply double-click `run.bat` or run `run.bat --web`)*

This opens the interactive Web Dashboard in your browser at `http://localhost:8501`.

### 🚀 Deploying to Cloud (Streamlit Community Cloud / Hugging Face / Render)

#### Option 1: Streamlit Community Cloud (Free 1-Click Deployment)
1. Push your repository to **GitHub**.
2. Visit **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
3. Click **New app**, select your repository, branch (`main`), and set Main file path to `app.py`.
4. Under **Advanced Settings**, add your environment secret:
   ```env
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
   ```
5. Click **Deploy!** Your app will be live on a public URL in seconds.

#### Option 2: Hugging Face Spaces (Free Docker/Streamlit Host)
1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces).
2. Choose **Streamlit** SDK.
3. Upload `app.py`, `requirements.txt`, and modules, or link to your Git repository.
4. Add `GROQ_API_KEY` under **Repository Secrets**.

#### Option 3: Render / Railway / Docker
Use standard Python command:
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## Setup

### 1. Prerequisites
- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com) *(takes ~2 minutes to get)*

### 2. Clone or download
```bash
git clone https://github.com/YOUR_USERNAME/rooman-interview-agent.git
cd rooman-interview-agent
```

### 3. Create a virtual environment
```bash
# Windows — create venv using the Python found in your system
"D:\Projects\GenAI- Pricing Simulator\python_version\.venv\Scripts\python.exe" -m venv venv

# macOS / Linux
python3 -m venv venv
```

> **Windows tip:** If `python` is not found, use the full path to any Python 3.10+ exe you have.
> On this machine the correct command is shown above.

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure your API key
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and replace `your_groq_api_key_here` with your actual Groq key:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

---

### Easiest — use the batch launcher (Windows only)
```bat
run.bat --demo    # demo mode, no API key needed
run.bat --live    # interactive interview
```

### Interactive interview (fully live)
```powershell
# Windows (PowerShell)
$env:PYTHONUTF8=1; .\venv\Scripts\python.exe agent.py

# macOS / Linux
python agent.py
```
You will be prompted for:
- Candidate name
- Role selection (Pick from 10 pre-configured job roles by typing option number `1–10`, or option `11` for a custom role)
- Required skills (Pre-populated default skills for each role; press Enter to accept or customize)

Then answer each of the 7 questions. Press **Enter twice** to submit each answer.

### Pre-fill role and skills via flags
```powershell
# Windows
$env:PYTHONUTF8=1; .\venv\Scripts\python.exe agent.py --role "Data Scientist" --skills "Python,SQL,Statistics" --name "Alice"

# macOS / Linux
python agent.py --role "Data Scientist" --skills "Python,SQL,Statistics" --name "Alice"
```

### Demo mode (no API key, no typing)
```bash
python agent.py --demo
```
Replays `sample_transcripts/sample_interview.json` — a realistic Junior ML Engineer
interview with all answers, scores, and final evaluation pre-computed.

---

## Sample Inputs & Outputs

### Example 1 — Junior ML Engineer (interactive)
```
Role:   Junior ML Engineer
Skills: Python, Machine Learning, NLP, PyTorch, SQL
```

**Sample question generated:**
> *"What is the vanishing gradient problem in deep neural networks, and how can it be mitigated?"*

**Sample answer:**
> *"The vanishing gradient problem happens when gradients become very small as they are backpropagated through many layers…"*

**Score output:**
```
Score: 8/10  ████████░░  Strong

Feedback:    Strong answer demonstrating solid deep learning fundamentals.
✓ Strength:  Covered three distinct solutions with clear explanations.
→ Improve:   Mentioning gradient clipping would have made it more complete.
```

### Final Evaluation (excerpt from sample transcript)
```
╭──────────────────────────────────────────╮
│ Candidate   Priya Sharma                 │
│ Role        Junior ML Engineer           │
│ Score       72 / 100                     │
│ Decision    ✅ RECOMMEND                  │
╰──────────────────────────────────────────╯

Strengths:
  ✓ Strong grasp of supervised vs. unsupervised learning
  ✓ Systematic debugging mindset
  ✓ Awareness of full ML lifecycle

Gaps:
  ✗ Limited experience with multi-label classification
  ✗ Behavioral answers lacked explicit lessons-learned
```

Full transcript: [`sample_transcripts/sample_interview.json`](sample_transcripts/sample_interview.json)

---

## Project Structure

```
rooman-interview-agent/
├── agent.py                         # Entry point — orchestrates the full interview
├── question_generator.py            # LLM-powered question generation (7 per session)
├── answer_scorer.py                 # LLM-based per-answer scoring (1–10)
├── evaluator.py                     # Final evaluation report generator
├── session.py                       # Session state + JSON transcript persistence
├── requirements.txt                 # Pinned dependencies
├── .env.example                     # Environment variable template
├── sample_transcripts/
│   └── sample_interview.json        # Pre-run demo transcript
└── transcripts/                     # Auto-created — live session transcripts saved here
```

---

## Scoring Method

### Per-Answer Score (1–10)

Each answer is scored by the LLM on criteria appropriate to its category:

| Category | Scoring Criteria |
|---|---|
| Technical | Accuracy, depth of knowledge, correctness |
| Behavioral | STAR structure, specificity, demonstrated impact |
| Situational | Logical reasoning, practical approach |
| Motivation | Authenticity, alignment with role |

**Score bands:**

| Score | Label |
|---|---|
| 9–10 | Exceptional |
| 7–8  | Strong |
| 5–6  | Adequate |
| 3–4  | Weak |
| 1–2  | Inadequate |

### Final Score (out of 100)

```
Final = (avg_Technical × 0.40)
      + (avg_Behavioral × 0.25)
      + (avg_Situational × 0.20)
      + (avg_Motivation × 0.15)
      × 10
```

Technical questions are weighted highest because they directly assess the core
skills required for the role. Motivation is weighted least — it provides signal
but is not a strong predictor of performance.

### Recommendation Tiers

| Score | Recommendation |
|---|---|
| 80–100 | STRONGLY RECOMMEND |
| 65–79  | RECOMMEND |
| 50–64  | BORDERLINE |
| 0–49   | DO NOT RECOMMEND |

---

## Design Tradeoffs & Limitations

### What I chose and why

**LLM: Groq (`llama-3.1-8b-instant`)**
- Free tier, no credit card required — reviewers can run immediately
- Fast inference (~1–2 seconds per call), so the interview feels responsive
- Tradeoff: smaller model occasionally produces less nuanced scoring than GPT-4. Switching to `llama-3.3-70b-versatile` (also free on Groq) gives noticeably better evaluation depth.

**Question generation via LLM (vs. template bank)**
- Fully dynamic — works for any role or skill set without pre-coding questions
- Tradeoff: occasional JSON parse errors with very unusual roles. Mitigated with a robust `_parse_json_response()` fallback in every module.

**Scoring by LLM (vs. embedding similarity)**
- Embedding similarity can't evaluate reasoning quality or STAR structure
- LLM scoring is more holistic but is subjective — two runs may differ slightly
- Temperature is set to 0.3 for scoring (near-deterministic) to minimise variance

**Weighted category scoring**
- More honest than a flat average — a candidate who aces behavioural but fails technical shouldn't score the same as one who's strong across the board
- Weights are opinionated; in a production system they'd be configurable per role

**CLI-only (no web UI)**
- Keeps setup friction near zero (one `pip install`, one `python agent.py`)
- Tradeoff: less visual than a web UI; Rich library provides a reasonable terminal experience

### Known limitations

1. **No speech input** — answers must be typed. Adding `openai-whisper` or `groq/whisper-large-v3` would enable voice interviews.
2. **Single-round only** — does not support follow-up questions or adaptive branching based on candidate answers.
3. **No persistent candidate database** — each session is saved to a standalone JSON file; a real system would use a database with search.
4. **English only** — the system prompt does not specify language; multilingual use is untested.
5. **LLM dependency** — all intelligence depends on the Groq API being available. An Ollama (local) fallback would improve resilience.

### What I'd improve with more time

- Add a `--compare` mode to rank multiple transcripts against each other
- Adaptive follow-up questions when a score is below 5
- Web UI with a simple FastAPI backend + React frontend
- SQLite database to persist candidates and enable search/filtering
- Whisper integration for voice answers

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `groq` | 0.11.0 | Groq LLM API client |
| `python-dotenv` | 1.0.1 | Load `.env` variables |
| `rich` | 13.7.1 | Beautiful terminal UI |

---

## Reproducibility Checklist

| Step | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Copy env | `cp .env.example .env` (macOS/Linux) or `copy .env.example .env` (Windows) |
| Add key | Edit `.env` → set `GROQ_API_KEY` |
| Demo — Windows | `$env:PYTHONUTF8=1; python agent.py --demo` |
| Demo — Mac/Linux | `python agent.py --demo` |
| Live interview | `python agent.py` |
| Custom role | `python agent.py --role "..." --skills "..."` |
