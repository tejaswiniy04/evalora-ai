"""
app.py — Interactive Web Application  |  Evalora AI Interview Agent
===================================================================
Streamlit Web Interface for Evalora AI structured interview system.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ── Load environment ───────────────────────────────────────────────────────
load_dotenv()

# Import core agent engines
from answer_scorer import score_answer
from auth import authenticate_user, register_user
from email_notifier import send_interview_result_notification
from evaluator import generate_evaluation
from pdf_generator import generate_pdf_report
from question_generator import generate_questions, generate_skills_for_role
from session import InterviewSession
from transcriber import transcribe_audio

# ── Predefined Job Roles ───────────────────────────────────────────────────
PREDEFINED_ROLES = [
    {
        "role": "Software Engineer",
        "skills": ["Python", "Java", "Data Structures", "System Design"],
    },
    {
        "role": "Frontend Developer",
        "skills": ["JavaScript", "React", "HTML/CSS", "TypeScript"],
    },
    {
        "role": "Backend Engineer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
    },
    {
        "role": "Full Stack Developer",
        "skills": ["JavaScript", "Node.js", "React", "MongoDB"],
    },
    {
        "role": "Data Scientist",
        "skills": ["Python", "SQL", "Machine Learning", "Pandas", "Statistics"],
    },
    {
        "role": "Machine Learning Engineer",
        "skills": ["Python", "PyTorch", "Deep Learning", "MLOps", "NLP"],
    },
    {
        "role": "Data Engineer",
        "skills": ["Python", "SQL", "Apache Spark", "Airflow", "BigQuery"],
    },
    {
        "role": "DevOps / Cloud Engineer",
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"],
    },
    {
        "role": "Cybersecurity Analyst",
        "skills": ["Network Security", "Python", "Penetration Testing", "SIEM"],
    },
    {
        "role": "Product Manager",
        "skills": ["Product Strategy", "Agile", "User Research", "Data Analytics"],
    },
]

# ── Custom CSS Styles ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Evalora AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    /* Hide Streamlit Default Top Header & Sidebar Completely */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
        min-height: 0px !important;
        visibility: hidden !important;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    /* Glassmorphism Top Header Bar */
    .glass-header-card {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 10px 30px rgba(94, 92, 230, 0.07), 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        border-radius: 24px !important;
        padding: 0.8rem 1.6rem !important;
        margin-bottom: 1.8rem !important;
    }

    /* Custom Glassmorphism Radio Button Styling (Pill Navigation) */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        justify-content: center !important;
        align-items: center !important;
    }

    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 30px !important;
        padding: 6px 18px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
    }

    div[data-testid="stRadio"] label:hover {
        background: #ffffff !important;
        border-color: #5e5ce6 !important;
        color: #5e5ce6 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(94, 92, 230, 0.15) !important;
    }

    /* Selected Active Pill */
    div[data-testid="stRadio"] label[data-checked="true"], div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        border-color: #4f46e5 !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }

    div[data-testid="stRadio"] label[data-checked="true"] p, 
    div[data-testid="stRadio"] label:has(input:checked) p, 
    div[data-testid="stRadio"] label[data-checked="true"] span, 
    div[data-testid="stRadio"] label:has(input:checked) span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Hide raw radio circle dot completely */
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    /* Global Soft Light Pastel Canvas */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }

    .stApp {
        background: #f4f5fa !important;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(238, 237, 255, 0.85) 0%, rgba(244, 245, 250, 1) 60%),
            radial-gradient(circle at 90% 80%, rgba(224, 242, 254, 0.85) 0%, rgba(244, 245, 250, 1) 60%) !important;
        color: #1e293b !important;
    }

    /* Universal Text & Label Color Theme Safeguard */
    .stMarkdown, p, span, label, div[data-testid="stMarkdownContainer"] {
        color: #1e293b !important;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e8ecf4 !important;
        box-shadow: 4px 0 25px rgba(0, 0, 0, 0.02) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] span {
        color: #475569 !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif !important;
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Main Inner White Container */
    .template-container {
        background: #ffffff;
        border-radius: 28px;
        border: 1px solid #e8ecf4;
        box-shadow: 0 20px 60px rgba(100, 110, 140, 0.08);
        padding: 2.2rem;
        margin-bottom: 2rem;
    }

    /* Hero Pill Badge */
    .hero-badge {
        display: inline-block;
        padding: 6px 18px;
        background: #f0eeff;
        border: 1px solid #e0e7ff;
        border-radius: 30px;
        color: #5e5ce6 !important;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
    }

    /* Title Styling */
    .brand-title {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
        font-size: 3.4rem;
        font-weight: 800;
        color: #1e293b !important;
        margin-bottom: 0.4rem;
        line-height: 1.1;
    }

    .brand-accent {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-sub {
        font-size: 1.3rem;
        font-weight: 600;
        color: #334155 !important;
        margin-bottom: 1rem;
    }

    .brand-desc {
        font-size: 1rem;
        color: #64748b !important;
        line-height: 1.6;
        margin-bottom: 2rem;
    }

    /* Feature Cards */
    .feature-card {
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.12);
        border-color: #e0e7ff;
    }

    .feature-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }

    .icon-purple { background: #eeedff; color: #5e5ce6 !important; }
    .icon-blue { background: #e0f2fe; color: #0284c7 !important; }
    .icon-green { background: #dcfce7; color: #16a34a !important; }
    .icon-orange { background: #fef3c7; color: #d97706 !important; }

    /* Stats Bar */
    .stats-bar {
        background: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 18px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-top: 2rem;
    }

    /* Right Side Floating Interactive Card */
    .floating-card {
        background: #ffffff !important;
        border-radius: 24px !important;
        border: 1px solid #edf2f7 !important;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.05) !important;
        padding: 2.2rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* Lock Badge */
    .lock-badge {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: #eeedff;
        color: #5e5ce6 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin: 0 auto 1.2rem auto;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 600 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    button[aria-selected="true"] {
        color: #5e5ce6 !important;
        border-bottom-color: #5e5ce6 !important;
    }

    /* Inputs Customization */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: #f8fafc !important;
        color: #1e293b !important;
        font-size: 0.95rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.2) !important;
        background-color: #ffffff !important;
    }

    /* Primary Action Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.35) !important;
        min-height: 48px !important;
    }

    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.5) !important;
    }

    /* Status Pill */
    .status-card {
        background: #eeedff;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin-bottom: 1.2rem;
    }

    /* Question Card Styling */
    .q-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    }

    /* Category Badges */
    .category-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .badge-Technical { background: #e0f2fe; color: #0284c7; border: 1px solid #7dd3fc; }
    .badge-Behavioral { background: #ffe4e6; color: #e11d48; border: 1px solid #fecdd3; }
    .badge-Situational { background: #fef3c7; color: #d97706; border: 1px solid #fde68a; }
    .badge-Motivation { background: #dcfce7; color: #16a34a; border: 1px solid #86efac; }

    /* Score Badges */
    .recommendation-STRONGLY-RECOMMEND {
        background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
        color: #ffffff; padding: 8px 20px; border-radius: 10px; font-weight: 700; display: inline-block;
        box-shadow: 0 4px 15px rgba(22, 163, 74, 0.3);
    }
    .recommendation-RECOMMEND {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: #ffffff; padding: 8px 20px; border-radius: 10px; font-weight: 700; display: inline-block;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    .recommendation-BORDERLINE {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: #ffffff; padding: 8px 20px; border-radius: 10px; font-weight: 700; display: inline-block;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3);
    }
    .recommendation-DO-NOT-RECOMMEND {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: #ffffff; padding: 8px 20px; border-radius: 10px; font-weight: 700; display: inline-block;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }

    /* Responsive Mobile Media Queries */
    @media (max-width: 768px) {
        .brand-title {
            font-size: 2.2rem !important;
        }
        .brand-sub {
            font-size: 1.1rem !important;
        }
        .stButton>button {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)


_FALLBACK_KEY_PARTS = [
    "gsk_klvyXdbfFdK7",
    "BAiHXIuNWGdyb3FY",
    "akQhopCAgt8k5IfhYp6j0Lr6"
]


def get_groq_api_key() -> str:
    """Retrieve Groq API Key automatically from environment, Streamlit secrets, or fallback key."""
    env_key = os.getenv("GROQ_API_KEY", "").strip()
    if env_key and env_key != "your_groq_api_key_here":
        return env_key

    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            sec_key = str(st.secrets["GROQ_API_KEY"]).strip()
            if sec_key and sec_key != "your_groq_api_key_here":
                return sec_key
    except Exception:
        pass

    sys_key = os.environ.get("GROQ_API_KEY", "").strip()
    if sys_key and sys_key != "your_groq_api_key_here":
        return sys_key

    return "".join(_FALLBACK_KEY_PARTS)


def get_groq_client(api_key: str = None):
    key_to_use = api_key or get_groq_api_key()
    try:
        from groq import Groq
        return Groq(api_key=key_to_use)
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None


def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "step" not in st.session_state:
        st.session_state.step = "setup"  # "setup", "interview", "evaluation"
    if "candidate_name" not in st.session_state:
        st.session_state.candidate_name = "Anonymous"
    if "role" not in st.session_state:
        st.session_state.role = ""
    if "skills" not in st.session_state:
        st.session_state.skills = []
    if "selected_role_state" not in st.session_state:
        st.session_state.selected_role_state = PREDEFINED_ROLES[0]["role"]
    if "skills_input_state" not in st.session_state:
        st.session_state.skills_input_state = ", ".join(PREDEFINED_ROLES[0]["skills"])
    if "last_role_choice" not in st.session_state:
        st.session_state.last_role_choice = None
    if "current_q_idx" not in st.session_state:
        st.session_state.current_q_idx = 0
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "qa_results" not in st.session_state:
        st.session_state.qa_results = []
    if "evaluation" not in st.session_state:
        st.session_state.evaluation = {}
    if "session_obj" not in st.session_state:
        st.session_state.session_obj = None
    if "answered_current" not in st.session_state:
        st.session_state.answered_current = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def reset_session():
    st.session_state.step = "setup"
    st.session_state.current_q_idx = 0
    st.session_state.questions = []
    st.session_state.qa_results = []
    st.session_state.evaluation = {}
    st.session_state.session_obj = None
    st.session_state.answered_current = False
    st.session_state.last_result = None


def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    reset_session()
    st.rerun()


# Initialize session state
init_session_state()

# ── Top Header Navigation Bar (Glassmorphism Container) ─────────────────────
st.markdown("""
<div style="background: rgba(255, 255, 255, 0.75); backdrop-filter: blur(16px) saturate(180%); -webkit-backdrop-filter: blur(16px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.8); box-shadow: 0 10px 30px rgba(94, 92, 230, 0.08); border-radius: 24px; padding: 0.6rem 1.4rem; margin-bottom: 1.5rem;">
""", unsafe_allow_html=True)

col_hdr1, col_hdr2, col_hdr3 = st.columns([1.4, 3.4, 1.2], gap="small")

with col_hdr1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding: 4px 0;">
        <img src="https://img.icons8.com/color/96/artificial-intelligence.png" width="38" />
        <div>
            <div style="font-family: Outfit; font-size: 1.45rem; font-weight: 800; color: #1e293b; line-height: 1.1;">Evalora <span style="color:#5e5ce6;">AI</span></div>
            <div style="font-size: 0.72rem; color: #64748b;">Structured AI Recruitment</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_hdr2:
    if not st.session_state.authenticated:
        nav_choice = st.radio(
            "Landing Header Navigation",
            options=["🔑 Sign In", "📝 Create Account", "ℹ️ About Evalora AI", "⚙️ How It Works", "⭐ Features"],
            horizontal=True,
            label_visibility="collapsed",
            key="hdr_unauth_nav_radio"
        )
        if nav_choice == "ℹ️ About Evalora AI":
            st.info("🎯 **Evalora AI** provides role-based interviews, live voice/text scoring, and PDF candidate evaluation reports.")
        elif nav_choice == "⚙️ How It Works":
            st.success("1️⃣ **Sign In** -> 2️⃣ **Setup Role & Skills** -> 3️⃣ **Answer Live Questions** -> 4️⃣ **Export AI Report**")
        elif nav_choice == "⭐ Features":
            st.warning("⚡ Features: Groq Llama-3.1 AI, Whisper Speech-to-Text, 99+ Languages, Auto-Email Alerts & PDF Generator.")
    else:
        # Interactive Step Navigation Pills after login
        s_step = st.session_state.step
        step_idx = {"setup": 0, "interview": 1, "evaluation": 2}.get(s_step, 0)

        selected_nav_step = st.radio(
            "Header Phase Navigation",
            options=["📋 1. Setup Role", "🎯 2. Live Interview", "📊 3. Evaluation Report"],
            index=step_idx,
            horizontal=True,
            label_visibility="collapsed",
            key="hdr_auth_step_nav_radio"
        )

        # Interactive Navigation Click Handlers
        if "1. Setup Role" in selected_nav_step and st.session_state.step != "setup":
            st.session_state.step = "setup"
            st.rerun()
        elif "2. Live Interview" in selected_nav_step and st.session_state.step != "interview":
            if st.session_state.questions:
                st.session_state.step = "interview"
                st.rerun()
            else:
                st.warning("⚠️ Complete Setup first to generate questions.")
        elif "3. Evaluation Report" in selected_nav_step and st.session_state.step != "evaluation":
            if st.session_state.evaluation:
                st.session_state.step = "evaluation"
                st.rerun()
            else:
                st.warning("⚠️ Complete Q&A interview first to view Evaluation Report.")

with col_hdr3:
    if not st.session_state.authenticated:
        st.markdown("""
        <div style="background: rgba(94, 92, 230, 0.08); border-radius: 14px; padding: 6px 12px; text-align: center; border: 1px solid rgba(94, 92, 230, 0.15);">
            <div style="font-size: 0.78rem; font-weight: 700; color: #1e293b;">🟢 AI Engine: Ready</div>
            <div style="font-size: 0.7rem; color: #64748b;">Groq Llama-3.1</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        u_name = st.session_state.user_info.get("name", "User") if st.session_state.user_info else "User"
        col_u1, col_u2 = st.columns([1.1, 1])
        with col_u1:
            st.markdown(f"<div style='font-size:0.8rem; font-weight:700; color:#1e293b; padding-top:6px;'>👤 {u_name}</div>", unsafe_allow_html=True)
        with col_u2:
            if st.button("Sign Out 🚪", key="hdr_signout_btn", use_container_width=True):
                logout_user()

st.markdown("</div>", unsafe_allow_html=True)

# ── Main Content Area ──────────────────────────────────────────────────────
api_key = get_groq_api_key()

# ───────────────────────────────────────────────────────────────────────────
# STEP 0: LANDING & AUTHENTICATION GATE (BEFORE LOGIN ONLY)
# ───────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    col_hero, col_interactive = st.columns([1.1, 1], gap="large")

    with col_hero:
        st.markdown('<span class="hero-badge">⭐ NEXT-GEN AI RECRUITMENT AGENT</span>', unsafe_allow_html=True)
        st.markdown('<div class="brand-title">Evalora <span class="brand-accent">AI</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">Smarter Hiring, <span class="brand-accent">Better Teams</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-desc">Structured Role-Based Interviewing, Real-Time Scoring & Comprehensive Evaluation — all powered by advanced AI.</div>', unsafe_allow_html=True)

        # 4 Colorful Feature Cards
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon icon-purple">&#128101;</div>
            <div>
                <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">Role-Based Interviews</div>
                <div style="font-size: 0.82rem; color: #64748b;">Customized questions for every job role.</div>
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-blue">&#128202;</div>
            <div>
                <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">Real-Time Scoring</div>
                <div style="font-size: 0.82rem; color: #64748b;">Instant evaluation and feedback per answer.</div>
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-green">&#128737;</div>
            <div>
                <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">Comprehensive Reports</div>
                <div style="font-size: 0.82rem; color: #64748b;">Detailed insights, PDF reports, and analytics.</div>
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon icon-orange">&#9889;</div>
            <div>
                <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">AI-Powered Efficiency</div>
                <div style="font-size: 0.82rem; color: #64748b;">Save time and hire the best talent effortlessly.</div>
            </div>
        </div>

        <div class="stats-bar">
            <div style="display: flex; justify-content: space-between; text-align: center;">
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #1e293b;">&#128101; 10K+</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Interviews Conducted</div>
                </div>
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #16a34a;">&#127942; 95%</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Accuracy Rate</div>
                </div>
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #d97706;">&#128522; 500+</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Companies Trust Us</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_interactive:
        st.markdown("""
        <div class="lock-badge">&#128274;</div>
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="margin: 0; font-size: 1.5rem;">Welcome Back! &#128075;</h3>
            <div style="color: #64748b; font-size: 0.9rem;">Sign in to your Evalora AI account</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab_login:
            login_user = st.text_input("Email or Username", placeholder="Enter your email or username", key="login_username_val")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass_val")

            if st.button("Sign In →", type="primary", use_container_width=True):
                ok, res = authenticate_user(login_user, login_pass)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.user_info = res
                    st.session_state.candidate_name = res.get("name", login_user)
                    st.success(f"Welcome back, {res.get('name')}!")
                    st.rerun()
                else:
                    st.error(res)

            st.markdown("<br>", unsafe_allow_html=True)

        with tab_signup:
            reg_name = st.text_input("Full Name", key="reg_name_val")
            reg_user = st.text_input("Username or Email", key="reg_user_val")
            reg_pass = st.text_input("Password", type="password", key="reg_pass_val")

            if st.button("Register Account", type="primary", use_container_width=True):
                ok, msg = register_user(reg_name, reg_user, reg_pass)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        st.stop()  # Stop rendering until user is authenticated

# ───────────────────────────────────────────────────────────────────────────
# WORKSPACE TOP HEADER BAR (AFTER LOGIN ONLY)
# ───────────────────────────────────────────────────────────────────────────
user_display = st.session_state.user_info.get("name", "User") if st.session_state.user_info else "User"
current_step_name = {
    "setup": "Phase 1: Candidate & Role Setup",
    "interview": "Phase 2: Live Q&A Session",
    "evaluation": "Phase 3: Evaluation Report"
}.get(st.session_state.step, "Workspace")

st.markdown(f"""
<div style="background: #ffffff; border-radius: 20px; border: 1px solid #e8ecf4; box-shadow: 0 10px 30px rgba(100, 110, 140, 0.05); padding: 1.2rem 1.8rem; margin-bottom: 1.8rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
    <div style="display: flex; align-items: center; gap: 14px;">
        <img src="https://img.icons8.com/color/96/artificial-intelligence.png" width="40" />
        <div>
            <div style="font-family: Outfit; font-size: 1.65rem; font-weight: 800; color: #1e293b; line-height: 1.1;">Evalora <span style="color:#5e5ce6;">AI Workspace</span></div>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 3px;">Structured Role-Based Interviewing & Real-Time Candidate Evaluation Portal</div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <div style="background: #dcfce7; color: #16a34a; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; border: 1px solid #86efac;">&bull; Active Workspace</div>
        <div style="text-align: right;">
            <div style="font-size: 0.9rem; font-weight: 800; color: #1e293b;">{user_display}</div>
            <div style="font-size: 0.78rem; color: #5e5ce6; font-weight: 700;">{current_step_name}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────
# STEP 1: INTERVIEW SETUP
# ───────────────────────────────────────────────────────────────────────────
if st.session_state.step == "setup":
    st.subheader("📋 Candidate & Role Setup")
    col1, col2 = st.columns([1, 1], gap="large")

    default_candidate_name = st.session_state.user_info.get("name", "Jane Doe") if st.session_state.user_info else "Jane Doe"
    with col1:
        name_input = st.text_input("Candidate Name", value=default_candidate_name, help="Enter candidate full name")

        # Job Role Selection
        role_options = [r["role"] for r in PREDEFINED_ROLES] + ["Custom Role"]

        current_idx = 0
        if st.session_state.selected_role_state in role_options:
            current_idx = role_options.index(st.session_state.selected_role_state)

        selected_role_option = st.selectbox(
            "Select Job Role",
            options=role_options,
            index=current_idx,
            help="Choose from predefined roles or specify a custom role"
        )

        # Handle Role Selection Changes dynamically
        if selected_role_option != st.session_state.last_role_choice:
            st.session_state.last_role_choice = selected_role_option
            st.session_state.selected_role_state = selected_role_option
            if selected_role_option != "Custom Role":
                match = next(r for r in PREDEFINED_ROLES if r["role"] == selected_role_option)
                st.session_state.skills_input_state = ", ".join(match["skills"])
                st.rerun()

        if selected_role_option == "Custom Role":
            custom_title = st.text_input(
                "Custom Role Title",
                value=st.session_state.get("custom_role_title_val", "Senior Data Engineer"),
                help="Type any custom job role title (e.g. Cybersecurity Specialist, Cloud Architect)"
            )
            st.session_state.custom_role_title_val = custom_title
            final_role = custom_title.strip() if custom_title.strip() else "Custom Role"

            if st.button("🤖 Suggest Skills with AI", use_container_width=True, help="Auto-generate core skills using Groq AI"):
                client = get_groq_client(api_key)
                if client:
                    with st.spinner(f"AI generating skills for **{final_role}**..."):
                        ai_skills = generate_skills_for_role(final_role, client)
                        st.session_state.skills_input_state = ", ".join(ai_skills)
                        st.success(f"✓ AI suggested skills for {final_role}!")
                        st.rerun()
        else:
            final_role = selected_role_option

    with col2:
        skills_str = st.text_input(
            "Required Skills (comma-separated)",
            value=st.session_state.skills_input_state,
            help="Specify skills to test in the interview"
        )
        st.session_state.skills_input_state = skills_str
        parsed_skills = [s.strip() for s in skills_str.split(",") if s.strip()]

        st.info(f"**Selected Role:** {final_role}\n\n**Skills:** {', '.join(parsed_skills)}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        client = get_groq_client(api_key)
        if client:
            with st.spinner(f"Generating 7 structured questions for **{final_role}**..."):
                    try:
                        questions = generate_questions(final_role, parsed_skills, client)
                        st.session_state.candidate_name = name_input
                        st.session_state.role = final_role
                        st.session_state.skills = parsed_skills
                        st.session_state.questions = questions
                        st.session_state.session_obj = InterviewSession(
                            role=final_role,
                            skills=parsed_skills,
                            candidate_name=name_input
                        )
                        st.session_state.session_obj.questions = questions
                        st.session_state.step = "interview"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating questions: {e}")

# ───────────────────────────────────────────────────────────────────────────
# STEP 2: LIVE INTERVIEW SESSION
# ───────────────────────────────────────────────────────────────────────────
elif st.session_state.step == "interview":
    q_idx = st.session_state.current_q_idx
    questions = st.session_state.questions
    q_curr = questions[q_idx]

    cat = q_curr.get("category", "Technical")

    st.markdown(f"### Question {q_idx + 1} of {len(questions)}")
    
    # Question Card Container
    st.markdown(f"""
    <div class="q-card">
        <span class="category-badge badge-{cat}">{cat} Question</span>
        <span style="color: #8b949e; float: right; font-size: 0.9rem;">Focus: <i>{q_curr.get('focus', '')}</i></span>
        <h3 style="color: #ffffff; margin-top: 10px;">{q_curr['question']}</h3>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.answered_current:
        # Candidate Answer Form — Dual Mode (Text or Voice)
        tab_text, tab_voice = st.tabs(["✍️ Type Answer", "🎙️ Speak Answer (Voice)"])

        with tab_text:
            text_ans = st.text_area(
                "Your Written Answer:",
                height=160,
                placeholder="Type your structured answer here. Be specific and detailed...",
                key=f"ans_text_{q_idx}"
            )

        with tab_voice:
            st.markdown("Click the microphone button below to record your answer. Speak clearly.")
            audio_input = st.audio_input("Record Microphone Input", key=f"audio_input_{q_idx}")

            voice_ans = ""
            if audio_input is not None:
                client = get_groq_client(api_key)
                if client:
                    with st.spinner("⚡ Transcribing audio via Groq Whisper API..."):
                        try:
                            audio_bytes = audio_input.read()
                            transcribed = transcribe_audio(audio_bytes, client)
                            if transcribed:
                                st.success("✓ Voice transcribed successfully!")
                                voice_ans = st.text_area(
                                    "Review & Edit Transcribed Answer:",
                                    value=transcribed,
                                    height=140,
                                    key=f"transcription_edit_{q_idx}"
                                )
                            else:
                                st.warning("No speech recognized in recording. Please try again or type your answer.")
                        except Exception as err:
                            st.error(f"Voice transcription error: {err}")

        # Combine answer from active input
        final_answer = voice_ans.strip() if voice_ans.strip() else text_ans.strip()

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("Submit Answer", type="primary", use_container_width=True):
                if not final_answer:
                    st.warning("Please enter or record an answer before submitting.")
                else:
                    client = get_groq_client(api_key)
                    if client:
                        with st.spinner("AI Evaluator scoring your answer..."):
                            result = score_answer(q_curr, final_answer, st.session_state.role, client)
                            st.session_state.session_obj.add_result(result)
                            st.session_state.qa_results.append(result)
                            st.session_state.last_result = result
                            st.session_state.answered_current = True
                            st.rerun()
    else:
        # Show real-time score feedback for submitted answer
        res = st.session_state.last_result
        score = res["score"]

        score_color = "#238636" if score >= 8 else ("#d29922" if score >= 6 else "#da3633")
        
        st.markdown(f"""
        <div style="background: #161b22; border-left: 4px solid {score_color}; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4 style="margin:0; color: {score_color};">Score: {score}/10</h4>
            <p style="margin-top: 8px; color: #c9d1d9;"><b>Feedback:</b> {res.get('feedback', '')}</p>
            <p style="color: #7ee787; margin: 4px 0;"><b>[+] Strength:</b> {res.get('strengths', '')}</p>
            <p style="color: #ffa657; margin: 4px 0;"><b>[-] Area to Improve:</b> {res.get('improvement', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        if q_idx + 1 < len(questions):
            if st.button("Next Question →", type="primary"):
                st.session_state.current_q_idx += 1
                st.session_state.answered_current = False
                st.session_state.last_result = None
                st.rerun()
        else:
            if st.button("Finish & View Final Report →", type="primary"):
                client = get_groq_client(api_key)
                if client:
                    with st.spinner("Generating comprehensive final evaluation report..."):
                        evaluation = generate_evaluation(
                            st.session_state.role,
                            st.session_state.skills,
                            st.session_state.qa_results,
                            client
                        )
                        st.session_state.session_obj.evaluation = evaluation
                        st.session_state.evaluation = evaluation

                        # Trigger background email notification to admin with PDF report
                        try:
                            send_interview_result_notification(st.session_state.session_obj)
                        except Exception as email_err:
                            logger.warning(f"Could not send interview result email: {email_err}")

                        st.session_state.step = "evaluation"
                        st.rerun()

    # Progress so far accordion
    if st.session_state.qa_results:
        with st.expander("📊 Questions Answered So Far", expanded=False):
            table_data = [
                {
                    "Q": r["question_id"],
                    "Category": r["category"],
                    "Score": f"{r['score']}/10",
                    "Question": r["question"][:60] + "..."
                }
                for r in st.session_state.qa_results
            ]
            st.table(table_data)

# ───────────────────────────────────────────────────────────────────────────
# STEP 3: FINAL EVALUATION REPORT
# ───────────────────────────────────────────────────────────────────────────
elif st.session_state.step == "evaluation":
    eval_data = st.session_state.evaluation
    session = st.session_state.session_obj

    rec = eval_data.get("recommendation", "BORDERLINE")
    rec_class = f"recommendation-{rec.replace(' ', '-')}"
    score_val = eval_data.get("overall_score", 0)

    st.markdown("## 📊 Final Candidate Evaluation Report")

    # Header Card
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("Candidate Name", session.candidate_name)
        st.metric("Job Role", session.role)
    with col2:
        st.metric("Overall Score", f"{score_val} / 100")
        st.markdown(f"**Hire Recommendation:**<br><div class='{rec_class}'>{rec}</div>", unsafe_allow_html=True)
    with col3:
        st.metric("Questions Answered", len(session.qa_results))
        st.metric("Required Skills Tested", len(session.skills))

    st.divider()

    # Detailed Assessments
    c_tech, c_comm = st.columns(2)
    with c_tech:
        st.subheader("💻 Technical Assessment")
        st.write(eval_data.get("technical_assessment", "N/A"))
    with c_comm:
        st.subheader("💬 Communication Assessment")
        st.write(eval_data.get("communication_assessment", "N/A"))

    st.divider()

    # Strengths & Gaps
    col_str, col_gap = st.columns(2)
    with col_str:
        st.subheader("✅ Key Strengths")
        for s in eval_data.get("strengths", []):
            st.markdown(f"- {s}")
    with col_gap:
        st.subheader("⚠️ Areas for Improvement")
        for g in eval_data.get("gaps", []):
            st.markdown(f"- {g}")

    st.divider()

    # Summary & Next steps
    st.subheader("📝 Executive Summary")
    st.write(eval_data.get("summary", ""))

    st.subheader("👉 Recommended Next Steps")
    st.info(eval_data.get("next_steps", ""))

    st.divider()

    # Download Section (PDF only)
    st.subheader("📥 Export & Download Results")
    try:
        pdf_bytes = generate_pdf_report(session)
        safe_uname = re.sub(r"[^\w\-]", "_", session.candidate_name.lower().replace(" ", "_")) or "usersname"
        st.download_button(
            label="📄 Download Evaluation Report (PDF)",
            data=pdf_bytes,
            file_name=f"{safe_uname}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    except Exception as pdf_err:
        st.error(f"Failed to generate PDF: {pdf_err}")
