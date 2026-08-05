"""
agent.py — Interview Agent  |  Rooman AI 24-Hour Challenge
============================================================
Conducts AI-powered structured interviews: generates role-specific questions,
scores each answer live, and produces a final evaluation report.

Usage:
    python agent.py                                          # Interactive
    python agent.py --demo                                   # Replay sample
    python agent.py --role "Data Scientist" --skills "Python,SQL,Statistics"
    python agent.py --role "ML Engineer" --skills "Python,PyTorch,NLP" --name "Jane Doe"
"""

import argparse
import json
import logging
import os
import sys
import time

# ── Windows UTF-8 fix (must happen before any output) ──────────────────────
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from answer_scorer import score_answer
from email_notifier import send_interview_result_notification
from evaluator import generate_evaluation
from question_generator import generate_questions
from session import InterviewSession

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

# ── Setup ──────────────────────────────────────────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
console = Console()


# ── Color helpers ──────────────────────────────────────────────────────────
def score_color(score: int) -> str:
    if score >= 8:  return "bright_green"
    if score >= 6:  return "yellow"
    if score >= 4:  return "orange3"
    return "red"


def score_label(score: int) -> str:
    if score >= 9:  return "Exceptional"
    if score >= 7:  return "Strong"
    if score >= 5:  return "Adequate"
    if score >= 3:  return "Weak"
    return "Inadequate"


def rec_color(rec: str) -> str:
    return {
        "STRONGLY RECOMMEND": "bright_green",
        "RECOMMEND":          "green",
        "BORDERLINE":         "yellow",
        "DO NOT RECOMMEND":   "red",
    }.get(rec, "white")


def category_color(cat: str) -> str:
    return {
        "Technical":   "cyan",
        "Behavioral":  "magenta",
        "Situational": "yellow",
        "Motivation":  "blue",
    }.get(cat, "white")


# ── UI components ──────────────────────────────────────────────────────────
def print_banner() -> None:
    t = Text(justify="center")
    t.append("[*] INTERVIEW AGENT\n", style="bold cyan")
    t.append("AI-Powered Structured Interview System", style="dim")
    console.print(Panel(Align.center(t), border_style="cyan", padding=(1, 6)))
    console.print()


def select_job_role() -> tuple[str, list[str]]:
    """Display a menu of job roles for the user to select by typing an option number."""
    console.print()
    table = Table(title="Available Job Roles", box=box.ROUNDED, border_style="cyan", show_header=True)
    table.add_column("Option", justify="center", style="bold yellow", width=8)
    table.add_column("Job Role", style="bold white", width=28)
    table.add_column("Default Skills", style="dim cyan")

    for idx, item in enumerate(PREDEFINED_ROLES, 1):
        table.add_row(str(idx), item["role"], ", ".join(item["skills"]))
    custom_idx = len(PREDEFINED_ROLES) + 1
    table.add_row(str(custom_idx), "Custom Role", "Enter custom role and skills")

    console.print(table)
    console.print()

    choices = [str(i) for i in range(1, custom_idx + 1)]
    choice_str = Prompt.ask(
        f"  [bold]Select Job Role Option (1-{custom_idx})[/bold]",
        choices=choices,
        default="1",
    )

    choice = int(choice_str)
    if choice <= len(PREDEFINED_ROLES):
        selected = PREDEFINED_ROLES[choice - 1]
        role = selected["role"]
        default_skills_str = ", ".join(selected["skills"])
        raw_skills = Prompt.ask(
            "  [bold]Required Skills[/bold] [dim](press Enter to use default)[/dim]",
            default=default_skills_str,
        )
        skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
        return role, skills
    else:
        role = Prompt.ask("  [bold]Role / Position[/bold]", default="Junior ML Engineer")
        raw_skills = Prompt.ask(
            "  [bold]Required Skills[/bold] [dim](comma-separated)[/dim]",
            default="Python, Machine Learning, NLP",
        )
        skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
        return role, skills



def print_question(q: dict, num: int, total: int) -> None:
    cat   = q.get("category", "General")
    color = category_color(cat)
    console.print()
    console.print(Rule(f"[bold]Question {num} / {total}[/bold]", style="dim"))
    console.print(
        f"  [dim]Category:[/dim] [{color}]{cat}[/{color}]"
        f"   [dim]Tests:[/dim] [italic]{q.get('focus', '')}[/italic]"
    )
    console.print()
    console.print(Panel(
        f"[bold white]{q['question']}[/bold white]",
        border_style=color,
        padding=(1, 2),
    ))


def get_multiline_answer(demo_answer: str = None) -> str:
    """Accept a multi-line answer; returns empty string on EOF."""
    if demo_answer is not None:
        return demo_answer

    console.print("[dim]  Type your answer. Press Enter twice when done.[/dim]\n")
    lines = []
    try:
        while True:
            line = input("  > ")
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    return "\n".join(lines).strip()


def print_score(result: dict) -> None:
    s     = result["score"]
    color = score_color(s)
    bar   = "█" * s + "░" * (10 - s)

    console.print()
    score_txt = Text()
    score_txt.append("  Score: ", style="bold")
    score_txt.append(f"{s}/10  ", style=f"bold {color}")
    score_txt.append(f"[{color}]{bar}[/{color}]  ", style="")
    score_txt.append(score_label(s), style=f"italic {color}")
    console.print(score_txt)
    console.print()
    console.print(f"  [bold]Feedback:[/bold]    {result['feedback']}")
    if result.get("strengths"):
        console.print(f"  [green]✓ Strength:[/green]  {result['strengths']}")
    if result.get("improvement"):
        console.print(f"  [yellow]→ Improve:[/yellow]   {result['improvement']}")


def print_progress_table(qa_results: list[dict]) -> None:
    t = Table(title="Progress So Far", box=box.ROUNDED, border_style="dim", show_header=True)
    t.add_column("Q",        justify="center", width=3)
    t.add_column("Category", width=14)
    t.add_column("Score",    justify="center", width=8)
    t.add_column("Rating",   width=12)
    for r in qa_results:
        s = r["score"]
        c = score_color(s)
        t.add_row(
            str(r["question_id"]),
            r["category"],
            f"[{c}]{s}/10[/{c}]",
            f"[{c}]{score_label(s)}[/{c}]",
        )
    console.print(t)


def print_evaluation(evaluation: dict, session: InterviewSession) -> None:
    rec   = evaluation.get("recommendation", "BORDERLINE")
    rc    = rec_color(rec)
    ovr   = evaluation.get("overall_score", 0)
    oc    = score_color(int(ovr / 10))

    console.print()
    console.print(Rule("[bold cyan]FINAL EVALUATION REPORT[/bold cyan]", style="cyan"))
    console.print()

    # ── Header info table ──────────────────────────────────────────────
    hdr = Table.grid(padding=(0, 2))
    hdr.add_column(style="dim",  width=20)
    hdr.add_column(style="bold")
    hdr.add_row("Candidate",     session.candidate_name)
    hdr.add_row("Role",          session.role)
    hdr.add_row("Skills",        ", ".join(session.skills))
    hdr.add_row("Date",          datetime.now().strftime("%d %b %Y  %H:%M"))
    hdr.add_row("Overall Score", f"[{oc}]{ovr}/100[/{oc}]")
    hdr.add_row("Recommendation", f"[bold {rc}]{rec}[/bold {rc}]")
    console.print(Panel(hdr, title="[bold]Summary[/bold]", border_style="cyan", padding=(1, 2)))
    console.print()

    # ── Assessment ─────────────────────────────────────────────────────
    tech = evaluation.get("technical_assessment", "")
    comm = evaluation.get("communication_assessment", "")
    if tech or comm:
        body = ""
        if tech: body += f"[bold]Technical:[/bold] {tech}\n\n"
        if comm: body += f"[bold]Communication:[/bold] {comm}"
        console.print(Panel(body.strip(), title="[bold]Assessment[/bold]", border_style="blue", padding=(1, 2)))
        console.print()

    # ── Strengths & Gaps ───────────────────────────────────────────────
    strengths = evaluation.get("strengths", [])
    gaps      = evaluation.get("gaps", [])
    str_body  = "\n".join(f"  [green]✓[/green]  {s}" for s in strengths) or "  (none noted)"
    gap_body  = "\n".join(f"  [red]✗[/red]  {g}" for g in gaps)         or "  (none noted)"
    console.print(Panel(str_body, title="[bold green]Strengths[/bold green]",               border_style="green", padding=(1, 1)))
    console.print(Panel(gap_body, title="[bold red]Areas for Improvement[/bold red]", border_style="red",   padding=(1, 1)))
    console.print()

    # ── Summary ────────────────────────────────────────────────────────
    summary = evaluation.get("summary", "")
    if summary:
        console.print(Panel(summary, title="[bold]Overall Summary[/bold]", border_style="dim", padding=(1, 2)))
        console.print()

    # ── Next steps ─────────────────────────────────────────────────────
    next_steps = evaluation.get("next_steps", "")
    if next_steps:
        console.print(f"  [bold]Next Steps:[/bold] {next_steps}")
        console.print()


# ── Core interview flow ────────────────────────────────────────────────────
def run_interview(
    role:   str  = None,
    skills: list = None,
    name:   str  = None,
    demo:   bool = False,
) -> None:
    print_banner()

    if demo:
        _run_demo()
        return

    # ── Validate API key ──────────────────────────────────────────────
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        console.print(Panel(
            "[bold red]GROQ_API_KEY not configured.[/bold red]\n\n"
            "1. Copy [bold].env.example[/bold] → [bold].env[/bold]\n"
            "2. Add your key from [link=https://console.groq.com]https://console.groq.com[/link]\n"
            "3. Run the agent again.\n\n"
            "[dim]No account yet? It's free and takes 2 minutes.[/dim]",
            title="[bold]Setup Required[/bold]",
            border_style="red",
        ))
        sys.exit(1)

    from groq import Groq
    client = Groq(api_key=api_key)

    # ── Collect inputs ────────────────────────────────────────────────
    console.print("[bold cyan]Interview Setup[/bold cyan]")
    console.print()

    candidate_name = name or Prompt.ask("  [bold]Candidate Name[/bold]", default="Anonymous")

    if not role:
        role, selected_skills = select_job_role()
        if not skills:
            skills = selected_skills
    elif not skills:
        raw = Prompt.ask(
            "  [bold]Required Skills[/bold] [dim](comma-separated)[/dim]",
            default="Python, Machine Learning, NLP",
        )
        skills = [s.strip() for s in raw.split(",") if s.strip()]

    console.print()
    console.print(
        f"  [dim]Role:[/dim] [bold]{role}[/bold]   "
        f"[dim]Skills:[/dim] {', '.join(skills)}"
    )
    console.print()

    # ── Initialise session ────────────────────────────────────────────
    session = InterviewSession(role=role, skills=skills, candidate_name=candidate_name)

    # ── Generate questions ────────────────────────────────────────────
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Generating interview questions…"),
        console=console, transient=True
    ) as prog:
        prog.add_task("")
        questions = generate_questions(role, skills, client)

    session.questions = questions
    console.print(f"  [green]✓[/green] {len(questions)} questions generated for [bold]{role}[/bold].")
    console.print()
    console.print(Rule("[dim]Interview Begins[/dim]", style="dim"))
    console.print("[dim]  Answer each question thoroughly. Press Enter twice to submit.[/dim]")

    # ── Interview loop ────────────────────────────────────────────────
    for i, question in enumerate(questions, 1):
        print_question(question, i, len(questions))
        answer = get_multiline_answer()
        if not answer:
            answer = "(No answer provided)"

        with Progress(
            SpinnerColumn(),
            TextColumn("[dim]Evaluating answer…"),
            console=console, transient=True
        ) as prog:
            prog.add_task("")
            result = score_answer(question, answer, role, client)

        session.add_result(result)
        print_score(result)

        if i % 3 == 0 and i < len(questions):
            console.print()
            print_progress_table(session.qa_results)

    # ── Post-interview summary ────────────────────────────────────────
    console.print()
    console.print(Rule("[dim]All Questions Complete[/dim]", style="dim"))
    console.print()
    print_progress_table(session.qa_results)

    # ── Final evaluation ──────────────────────────────────────────────
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Generating final evaluation…"),
        console=console, transient=True
    ) as prog:
        prog.add_task("")
        evaluation = generate_evaluation(role, skills, session.qa_results, client)

    session.evaluation = evaluation
    print_evaluation(evaluation, session)

    # ── Save transcript & Notify Admin ────────────────────────────────
    path = session.save()
    console.print(f"  [green]✓[/green] Transcript saved → [bold]{path}[/bold]")

    try:
        send_interview_result_notification(session)
    except Exception as e:
        logger.warning(f"Could not send interview result email: {e}")

    console.print()
    console.print(Rule(style="dim"))
    console.print("[dim]  Interview complete. Thank you![/dim]")
    console.print()


# ── Demo mode ──────────────────────────────────────────────────────────────
def _run_demo() -> None:
    demo_path = Path("sample_transcripts") / "sample_interview.json"
    if not demo_path.exists():
        console.print(f"[red]Demo file not found:[/red] {demo_path}")
        sys.exit(1)

    with open(demo_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    console.print(Panel(
        "[cyan bold]DEMO MODE[/cyan bold] — Replaying a pre-run sample transcript\n"
        "[dim]No API key required. All answers and scores are pre-computed.[/dim]",
        border_style="yellow",
    ))
    console.print()

    session = InterviewSession(
        role=data["role"],
        skills=data["skills"],
        candidate_name=data["candidate_name"],
    )
    session.questions  = data["questions"]
    session.qa_results = data["qa_results"]
    session.evaluation = data["evaluation"]

    for i, (q, r) in enumerate(zip(data["questions"], data["qa_results"]), 1):
        print_question(q, i, len(data["questions"]))
        snippet = r["answer"][:350] + ("…" if len(r["answer"]) > 350 else "")
        console.print(f"  [dim italic]{snippet}[/dim italic]")
        print_score(r)
        time.sleep(0.4)

    console.print()
    print_progress_table(session.qa_results)
    print_evaluation(session.evaluation, session)
    console.print()
    console.print("[dim]  Demo complete. Run [bold]python agent.py[/bold] for a live interactive interview.[/dim]")
    console.print()


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Interview Agent — AI-powered structured interview system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py
  python agent.py --demo
  python agent.py --role "Data Scientist" --skills "Python,SQL,Statistics" --name "Alice"
  python agent.py --role "Backend Engineer" --skills "Python,Django,PostgreSQL,Docker"
        """,
    )
    parser.add_argument("--demo",   action="store_true", help="Replay pre-run sample transcript (no API key needed)")
    parser.add_argument("--role",   type=str, help="Job role title")
    parser.add_argument("--skills", type=str, help="Comma-separated required skills")
    parser.add_argument("--name",   type=str, help="Candidate name")
    args = parser.parse_args()

    skills_list = [s.strip() for s in args.skills.split(",")] if args.skills else None

    run_interview(role=args.role, skills=skills_list, name=args.name, demo=args.demo)
