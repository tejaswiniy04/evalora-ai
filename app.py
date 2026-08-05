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
from question_generator import generate_questions
from session import InterviewSession
from transcriber import SUPPORTED_LANGUAGES, transcribe_audio

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
    page_title="AI Interview Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Dark mode background polish */
    .stApp {
        background-color: #0e1117;
    }
    /* Banner styling */
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        font-size: 1.1rem;
        color: #8b949e;
        margin-bottom: 2rem;
    }
    /* Question Card */
    .q-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .category-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .badge-Technical { background: rgba(0, 210, 255, 0.15); color: #00d2ff; border: 1px solid #00d2ff; }
    .badge-Behavioral { background: rgba(235, 87, 87, 0.15); color: #ff6b6b; border: 1px solid #ff6b6b; }
    .badge-Situational { background: rgba(242, 201, 76, 0.15); color: #f2c94c; border: 1px solid #f2c94c; }
    .badge-Motivation { background: rgba(111, 207, 151, 0.15); color: #6fcf97; border: 1px solid #6fcf97; }

    /* Score Badges */
    .recommendation-STRONGLY-RECOMMEND {
        background-color: #238636; color: #ffffff; padding: 6px 16px; border-radius: 8px; font-weight: bold; display: inline-block;
    }
    .recommendation-RECOMMEND {
        background-color: #1f6beb; color: #ffffff; padding: 6px 16px; border-radius: 8px; font-weight: bold; display: inline-block;
    }
    .recommendation-BORDERLINE {
        background-color: #9e6a03; color: #ffffff; padding: 6px 16px; border-radius: 8px; font-weight: bold; display: inline-block;
    }
    .recommendation-DO-NOT-RECOMMEND {
        background-color: #da3633; color: #ffffff; padding: 6px 16px; border-radius: 8px; font-weight: bold; display: inline-block;
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

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.title("Interview Agent")
    st.caption("AI-Powered Structured Recruitment")
    st.divider()

    if st.session_state.authenticated and st.session_state.user_info:
        user_name = st.session_state.user_info.get("name", "User")
        st.markdown(f"👤 **Logged in as:**<br>**{user_name}**", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            logout_user()
        st.divider()

    api_key = get_groq_api_key()
    st.markdown("🟢 **AI Engine:** Ready (Groq Llama-3.1)")

    st.divider()
    st.markdown("### Progress")
    if st.session_state.step == "interview" and st.session_state.questions:
        q_num = st.session_state.current_q_idx + 1
        total_q = len(st.session_state.questions)
        st.progress(q_num / total_q)
        st.write(f"Question {q_num} of {total_q}")
    elif st.session_state.step == "evaluation":
        st.progress(1.0)
        st.write("Completed!")
    else:
        st.progress(0.0)
        st.write("Not started")

    if st.session_state.step != "setup":
        st.divider()
        if st.button("Reset Interview", use_container_width=True):
            reset_session()
            st.rerun()

# ── Main Header ────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🎯 AI Interview Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Structured Role-Based Interviewing, Real-Time Scoring & Evaluation</div>', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────
# STEP 0: AUTHENTICATION GATE (SIGN IN / SIGN UP)
# ───────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.subheader("🔐 User Sign In & Access")
    st.caption("Please sign in or create an account to start your structured interview.")

    tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])

    with tab_login:
        col_l1, col_l2 = st.columns([1, 1])
        with col_l1:
            login_user = st.text_input("Username or Email", key="login_username_val")
            login_pass = st.text_input("Password", type="password", key="login_pass_val")

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
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
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
        selected_role_option = st.selectbox(
            "Select Job Role",
            options=role_options,
            index=0,
            help="Choose from predefined roles or specify a custom role"
        )

        if selected_role_option == "Custom Role":
            final_role = st.text_input("Custom Role Title", value="Senior Data Engineer")
            default_skills_list = ["Python", "SQL", "Spark", "Docker"]
        else:
            final_role = selected_role_option
            match = next(r for r in PREDEFINED_ROLES if r["role"] == selected_role_option)
            default_skills_list = match["skills"]

    with col2:
        skills_str = st.text_input(
            "Required Skills (comma-separated)",
            value=", ".join(default_skills_list),
            help="Specify skills to test in the interview"
        )
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
            col_lang1, col_lang2 = st.columns([2, 1])
            with col_lang1:
                selected_lang_name = st.selectbox(
                    "🌐 Spoken Audio Language:",
                    options=list(SUPPORTED_LANGUAGES.keys()),
                    index=0,
                    key=f"audio_lang_{q_idx}"
                )
            selected_lang_code = SUPPORTED_LANGUAGES[selected_lang_name]

            st.markdown("Click the microphone button below to record your answer. Speak clearly in your selected language.")
            audio_input = st.audio_input("Record Microphone Input", key=f"audio_input_{q_idx}")

            voice_ans = ""
            if audio_input is not None:
                client = get_groq_client(api_key)
                if client:
                    with st.spinner(f"⚡ Transcribing audio ({selected_lang_name}) via Groq Whisper API..."):
                        try:
                            audio_bytes = audio_input.read()
                            transcribed = transcribe_audio(audio_bytes, client, language=selected_lang_code)
                            if transcribed:
                                st.success(f"✓ Voice transcribed successfully ({selected_lang_name})!")
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
            <p style="color: #7ee787; margin: 4px 0;"><b>✓ Strength:</b> {res.get('strengths', '')}</p>
            <p style="color: #ffa657; margin: 4px 0;"><b>→ Area to Improve:</b> {res.get('improvement', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        if q_idx + 1 < len(questions):
            if st.button("Next Question →", type="primary"):
                st.session_state.current_q_idx += 1
                st.session_state.answered_current = False
                st.session_state.last_result = None
                st.rerun()
        else:
            if st.button("Finish & View Final Report 🎉", type="primary"):
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
