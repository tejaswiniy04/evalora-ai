"""
question_generator.py — Role-Specific Interview Question Generator

Generates 7 structured questions per session:
  - 3 Technical  (skill-specific knowledge & problem-solving)
  - 2 Behavioral (STAR-format real-experience questions)
  - 1 Situational (hypothetical scenario)
  - 1 Motivation  (career fit & goals)
"""

import os
import json
import logging
import re
import time

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior technical interviewer at a top tech company.
Your job is to generate structured, role-specific interview questions.
You must return ONLY valid JSON — no markdown, no explanation, no extra text."""


def generate_questions(role: str, skills: list[str], client) -> list[dict]:
    """
    Generate 7 role-specific interview questions using the LLM.

    Args:
        role:   The job title (e.g. "Junior ML Engineer").
        skills: List of required skills (e.g. ["Python", "NLP", "SQL"]).
        client: Initialized Groq client.

    Returns:
        List of 7 question dicts, each with keys:
          id, category, question, focus
    """
    skills_str = ", ".join(skills)

    user_prompt = f"""Generate exactly 7 interview questions for a "{role}" position.
Required skills: {skills_str}

Return a JSON array of exactly 7 objects. Each object must have:
  "id"       : integer 1–7
  "category" : one of "Technical", "Behavioral", "Situational", "Motivation"
  "question" : the full interview question text
  "focus"    : the skill or competency being tested (short phrase)

Rules:
  - Questions 1–3: Technical (test {skills_str} specifically)
  - Questions 4–5: Behavioral (STAR format — "Tell me about a time...")
  - Question  6:   Situational ("Imagine you are..." — a realistic problem scenario)
  - Question  7:   Motivation ("Why..." — career goals and role fit)
  - Each question must be unique, clear, and appropriate for the role level.

Return ONLY the JSON array. No markdown fences, no explanation."""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            content = response.choices[0].message.content.strip()
            break
        except Exception as e:
            logger.warning(f"Groq API call attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(
                    "Connection error to Groq API. Please check your internet connection or API Key and try again."
                ) from e
            time.sleep(1)

    questions = _parse_json_response(content)

    # Validate structure
    validated = []
    for i, q in enumerate(questions[:7], 1):
        validated.append({
            "id":       q.get("id", i),
            "category": q.get("category", "Technical"),
            "question": q.get("question", ""),
            "focus":    q.get("focus", ""),
        })

    logger.info(f"Generated {len(validated)} questions for role: {role}")
    return validated


def _parse_json_response(content: str) -> list:
    """Robustly extract a JSON array from LLM output."""
    # Strip common markdown fences
    content = re.sub(r"```(?:json)?", "", content).strip()
    content = content.strip("`").strip()

    # Find the first '[' and last ']'
    start = content.find("[")
    end   = content.rfind("]")
    if start != -1 and end != -1:
        content = content[start : end + 1]

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw content:\n{content[:500]}")
        raise ValueError(
            "The LLM returned malformed JSON. Try running again or switch to a larger model."
        ) from e
