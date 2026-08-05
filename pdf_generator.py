"""
pdf_generator.py — Styled PDF Report Generator for Interview Agent
===================================================================
Generates a downloadable, professional PDF evaluation report using fpdf2.
"""

from datetime import datetime
from fpdf import FPDF
from session import InterviewSession


def clean_text(s: str) -> str:
    """Sanitize unicode characters for Latin-1 encoding in standard FPDF fonts."""
    if not s:
        return ""
    replacements = {
        "\u2014": " - ",
        "\u2013": " - ",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2022": "*",
        "\u2713": "v",
        "\u2717": "x",
        "…": "...",
    }
    for orig, repl in replacements.items():
        s = s.replace(orig, repl)
    return s.encode("latin-1", "replace").decode("latin-1")


class InterviewReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 150, 220)  # Cyan/Blue
        self.cell(0, 10, clean_text("EVALORA AI INTERVIEW AGENT"), border=False, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, clean_text("AI-Powered Candidate Evaluation Report"), border=False, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_draw_color(0, 150, 220)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, clean_text(f"Page {self.page_no()} | Confidential Candidate Evaluation | Evalora AI System"), align="C")


def generate_pdf_report(session: InterviewSession) -> bytes:
    """
    Generate a full styled PDF evaluation report for an InterviewSession.

    Args:
        session: Completed InterviewSession object.

    Returns:
        Raw PDF file bytes ready for download.
    """
    pdf = InterviewReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    evaluation = session.evaluation or {}
    qa_results = session.qa_results or []

    # ── Candidate Summary Box ──────────────────────────────────────────
    pdf.set_fill_color(240, 246, 252)  # Light blue background
    pdf.set_draw_color(200, 220, 240)
    pdf.rect(10, pdf.get_y(), 190, 36, style="FD")
    
    y_start = pdf.get_y() + 3
    pdf.set_y(y_start)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 30, 50)
    pdf.cell(95, 6, clean_text(f"Candidate: {session.candidate_name}"), new_x="RIGHT", new_y="TOP")
    
    # Overall Score & Recommendation
    score_val = evaluation.get("overall_score", round(session.average_score * 10, 1))
    rec_val = evaluation.get("recommendation", "N/A")
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 120, 200)
    pdf.cell(95, 6, clean_text(f"Overall Score: {score_val} / 100"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(95, 6, clean_text(f"Role: {session.role}"), new_x="RIGHT", new_y="TOP")
    
    # Recommendation status color
    if "STRONGLY" in rec_val:
        pdf.set_text_color(35, 134, 54)   # Green
    elif "RECOMMEND" in rec_val:
        pdf.set_text_color(31, 107, 235)  # Blue
    elif "BORDERLINE" in rec_val:
        pdf.set_text_color(158, 106, 3)   # Yellow/Brown
    else:
        pdf.set_text_color(218, 54, 51)   # Red
        
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 6, clean_text(f"Recommendation: {rec_val}"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(95, 6, clean_text(f"Skills: {', '.join(session.skills)}"), new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 6, clean_text(f"Date: {datetime.now().strftime('%d %b %Y, %H:%M')}"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(8)

    # ── Assessments Section ───────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 100, 180)
    pdf.set_x(10)
    pdf.cell(0, 6, clean_text("1. CANDIDATE ASSESSMENTS"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    tech = evaluation.get("technical_assessment", "")
    if tech:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(10)
        pdf.cell(0, 5, clean_text("Technical Assessment:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(50, 50, 50)
        pdf.set_x(10)
        pdf.multi_cell(190, 5, clean_text(tech))
        pdf.ln(2)

    comm = evaluation.get("communication_assessment", "")
    if comm:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(10)
        pdf.cell(0, 5, clean_text("Communication & Soft Skills:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(50, 50, 50)
        pdf.set_x(10)
        pdf.multi_cell(190, 5, clean_text(comm))
        pdf.ln(4)

    # ── Strengths & Gaps ───────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 100, 180)
    pdf.set_x(10)
    pdf.cell(0, 6, clean_text("2. STRENGTHS & AREAS FOR IMPROVEMENT"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    strengths = evaluation.get("strengths", [])
    if strengths:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(35, 134, 54)  # Green
        pdf.set_x(10)
        pdf.cell(0, 5, clean_text("Key Strengths:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(40, 40, 40)
        for s in strengths:
            pdf.set_x(10)
            pdf.multi_cell(190, 5, clean_text(f"  +  {s}"))
        pdf.ln(2)

    gaps = evaluation.get("gaps", [])
    if gaps:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(218, 54, 51)  # Red
        pdf.set_x(10)
        pdf.cell(0, 5, clean_text("Areas for Improvement:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(40, 40, 40)
        for g in gaps:
            pdf.set_x(10)
            pdf.multi_cell(190, 5, clean_text(f"  -  {g}"))
        pdf.ln(4)

    # ── Summary & Next Steps ──────────────────────────────────────────
    summary = evaluation.get("summary", "")
    if summary:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 100, 180)
        pdf.set_x(10)
        pdf.cell(0, 6, clean_text("3. EXECUTIVE SUMMARY & NEXT STEPS"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(40, 40, 40)
        pdf.set_x(10)
        pdf.multi_cell(190, 5, clean_text(summary))
        pdf.ln(2)

    next_steps = evaluation.get("next_steps", "")
    if next_steps:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(10)
        pdf.cell(0, 5, clean_text("Recommended Next Steps:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 9.5)
        pdf.set_text_color(0, 100, 180)
        pdf.set_x(10)
        pdf.multi_cell(190, 5, clean_text(next_steps))
        pdf.ln(6)

    # ── Per-Question Scores Breakdown Table ───────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 100, 180)
    pdf.set_x(10)
    pdf.cell(0, 6, clean_text("4. QUESTION-BY-QUESTION EVALUATION BREAKDOWN"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    for r in qa_results:
        q_id = r.get("question_id", "")
        cat = r.get("category", "")
        score = r.get("score", 0)
        question_text = r.get("question", "")
        answer_text = r.get("answer", "")
        feedback = r.get("feedback", "")
        strength = r.get("strengths", "")
        improvement = r.get("improvement", "")

        # Question header line
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(140, 6, clean_text(f"Q{q_id} [{cat}] - Focus: {r.get('focus', '')}"), new_x="RIGHT", new_y="TOP")
        
        # Score tag
        pdf.set_font("Helvetica", "B", 10)
        if score >= 8:
            pdf.set_text_color(35, 134, 54)
        elif score >= 6:
            pdf.set_text_color(210, 153, 34)
        else:
            pdf.set_text_color(218, 54, 51)
        pdf.cell(50, 6, clean_text(f"Score: {score}/10"), new_x="LMARGIN", new_y="NEXT", align="R")

        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(190, 5, clean_text(f"Question: {question_text}"))

        pdf.set_x(10)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(80, 80, 80)
        snippet = answer_text[:300] + ("..." if len(answer_text) > 300 else "")
        pdf.multi_cell(190, 4.5, clean_text(f'Candidate Answer: "{snippet}"'))

        pdf.set_x(10)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(190, 4.5, clean_text(f"Feedback: {feedback}"))

        if strength:
            pdf.set_x(10)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(35, 134, 54)
            pdf.multi_cell(190, 4.5, clean_text(f"Strength: {strength}"))

        if improvement:
            pdf.set_x(10)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(210, 153, 34)
            pdf.multi_cell(190, 4.5, clean_text(f"Improvement: {improvement}"))

        pdf.ln(4)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    return bytes(pdf.output())
