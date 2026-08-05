"""
email_notifier.py — Admin Email Notification & Database Exporter
=================================================================
Dispatches automated email notifications for:
  1. User account registration & user database details
  2. Candidate interview results & attached PDF evaluation reports (<username>.pdf)
to recipient: ayushhmane@gmail.com with subject: TEST ALERT: Evalora AI
"""

import logging
import os
import re
import smtplib
import threading
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logger = logging.getLogger(__name__)

# Default Admin Email Target
DEFAULT_ADMIN_EMAIL = "ayushhmane@gmail.com"
DEFAULT_SUBJECT = "TEST ALERT: Evalora AI"


def _send_email_thread(subject: str, body_text: str, recipient_email: str, attachment_path: str = None, custom_filename: str = None):
    """
    Internal function to send an email via SMTP in a background thread.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SMTP_USER", "tejaswini.y2004teju@gmail.com")
    sender_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()

    if not sender_password or sender_password in ("your_gmail_app_password_here", "your_password"):
        logger.warning(
            f"[EMAIL NOTICE] SMTP_PASSWORD is not set in .env! Email alert to {recipient_email} was skipped.\n"
            f"To receive emails at {recipient_email}, set your Gmail App Password in .env:\n"
            f"SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx"
        )
        print(f"\n[!] Notice: To receive live emails at {recipient_email}, add your Gmail App Password to .env (SMTP_PASSWORD=...)")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # Attach file if provided and exists
        if attachment_path and Path(attachment_path).exists():
            file_path = Path(attachment_path)
            attach_name = custom_filename or file_path.name
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=attach_name)
            part["Content-Disposition"] = f'attachment; filename="{attach_name}"'
            msg.attach(part)

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Successfully sent admin notification email to {recipient_email} with subject: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email notification to {recipient_email}: {e}")


def send_registration_notification(user_info: dict, admin_email: str = None, user_db_path: str = "users.json"):
    """
    Asynchronously send an email notification when a new user registers.

    Args:
        user_info: Dict with keys 'name', 'username'.
        admin_email: Target admin email address.
        user_db_path: Path to users.json database file.
    """
    target_email = admin_email or os.getenv("ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)
    subject = DEFAULT_SUBJECT

    body = (
        f"TEST ALERT: Evalora AI — New User Registered\n\n"
        f"Hello Admin,\n\n"
        f"A new user account has registered on Evalora AI:\n\n"
        f"  • Full Name: {user_info.get('name')}\n"
        f"  • Username / Email: {user_info.get('username')}\n\n"
        f"User Details & Database attached.\n\n"
        f"Best regards,\n"
        f"Evalora AI System"
    )

    thread = threading.Thread(
        target=_send_email_thread,
        args=(subject, body, target_email, user_db_path, "users.json"),
        daemon=True
    )
    thread.start()
    logger.info(f"Triggered async registration email: {user_info.get('username')} -> {target_email}")


def _send_interview_result_thread(subject: str, body_text: str, recipient_email: str, session):
    """
    Generate PDF report (<username>.pdf) and send interview result email in background.
    """
    try:
        from pdf_generator import generate_pdf_report
        pdf_bytes = generate_pdf_report(session)

        # Sanitize username for PDF filename (e.g. ayush.pdf or candidate_name.pdf)
        safe_username = re.sub(r"[^\w\-]", "_", session.candidate_name.lower().replace(" ", "_"))
        if not safe_username:
            safe_username = "usersname"
        pdf_filename = f"{safe_username}.pdf"

        # Save PDF report to transcripts directory
        pdf_path = Path("transcripts") / pdf_filename
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        _send_email_thread(subject, body_text, recipient_email, str(pdf_path), pdf_filename)
    except Exception as e:
        logger.error(f"Failed to generate/email candidate interview report: {e}")


def send_interview_result_notification(session, admin_email: str = None):
    """
    Asynchronously send candidate interview evaluation results and attached PDF report (<username>.pdf).

    Args:
        session: Completed InterviewSession object.
        admin_email: Target admin email address.
    """
    target_email = admin_email or os.getenv("ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)
    eval_data = session.evaluation or {}
    score = eval_data.get("overall_score", round(session.average_score * 10, 1))
    rec = eval_data.get("recommendation", "N/A")

    subject = DEFAULT_SUBJECT

    # Build comprehensive user and result details body
    body = (
        f"TEST ALERT: Evalora AI — Candidate Interview Results\n\n"
        f"USER & CANDIDATE DETAILS:\n"
        f"  • Candidate Name: {session.candidate_name}\n"
        f"  • Job Role: {session.role}\n"
        f"  • Required Skills Tested: {', '.join(session.skills)}\n"
        f"  • Session ID: {session.session_id}\n\n"
        f"RESULT DETAILS:\n"
        f"  • Overall Score: {score} / 100\n"
        f"  • Hire Recommendation: {rec}\n\n"
        f"TECHNICAL ASSESSMENT:\n"
        f"{eval_data.get('technical_assessment', 'N/A')}\n\n"
        f"COMMUNICATION ASSESSMENT:\n"
        f"{eval_data.get('communication_assessment', 'N/A')}\n\n"
        f"EXECUTIVE SUMMARY:\n"
        f"{eval_data.get('summary', 'N/A')}\n\n"
        f"RECOMMENDED NEXT STEPS:\n"
        f"{eval_data.get('next_steps', 'N/A')}\n\n"
        f"Attached PDF Report: {re.sub(r'[^\w\-]', '_', session.candidate_name.lower().replace(' ', '_'))}.pdf\n\n"
        f"Best regards,\n"
        f"Evalora AI System"
    )

    thread = threading.Thread(
        target=_send_interview_result_thread,
        args=(subject, body, target_email, session),
        daemon=True
    )
    thread.start()
    logger.info(f"Triggered async interview result email for {session.candidate_name} -> {target_email}")
