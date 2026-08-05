"""
answer_scorer.py — Per-Answer Scoring Engine

Scores each candidate answer on a 1–10 scale using the LLM.
Scoring dimensions:
  - Accuracy / Correctness  (for technical questions)
  - Depth & Specificity     (how detailed and substantive)
  - Clarity & Communication (how well articulated)
  - Relevance               (does it actually answer the question?)
"""

import os
import json
import logging
import re

logger = logging.getLogger(__name__)

SCORING_SYSTEM_PROMPT = """You are a senior technical interviewer evaluating a candidate's interview answers.
Score objectively and fairly. Be constructive, not harsh.
Return ONLY valid JSON — no markdown, no explanation, no extra text."""


def score_answer(question: dict, answer: str, role: str, client) -> dict:
    """
    Score a single candidate answer using the LLM.

    Args:
        question: Dict with keys: id, category, question, focus.
        answer:   The candidate's answer text.
        role:     Job role being interviewed for.
        client:   Initialized Groq client.

    Returns:
        Dict with keys:
          question_id, question, category, answer,
          score (int 1-10), feedback, strengths, improvement
    """
    category = question.get("category", "Technical")
    focus    = question.get("focus", "general competency")

    # Scoring criteria differ by question type
    if category == "Technical":
        criteria = "technical accuracy, depth of knowledge, and correctness of the explanation"
    elif category == "Behavioral":
        criteria = "use of STAR structure (Situation, Task, Action, Result), specificity, and impact"
    elif category == "Situational":
        criteria = "logical reasoning, problem-solving approach, and practical thinking"
    else:  # Motivation
        criteria = "authenticity, alignment with the role, and clarity of career goals"

    user_prompt = f"""Evaluate this answer for a "{role}" position interview.

Question Type: {category}
Tests: {focus}
Question: {question['question']}

Candidate's Answer:
\"\"\"{answer}\"\"\"

Score the answer from 1 to 10 based on: {criteria}

Score guide:
  9-10 = Exceptional — exceeds expectations
  7-8  = Strong — meets expectations well
  5-6  = Adequate — meets basic expectations
  3-4  = Weak — below expectations
  1-2  = Inadequate — significantly lacking

Return ONLY this JSON (no markdown, no extra text):
{{
  "score": <integer 1-10>,
  "feedback": "<2–3 sentence overall evaluation>",
  "strengths": "<what was done well in the answer>",
  "improvement": "<one specific thing that would make this answer stronger>"
}}"""

    import time
    max_retries = 3
    content = ""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
                messages=[
                    {"role": "system", "content": SCORING_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=600,
            )
            content = response.choices[0].message.content.strip()
            break
        except Exception as e:
            logger.warning(f"Answer scoring API call attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                return {
                    "question_id":  question["id"],
                    "question":     question["question"],
                    "category":     question["category"],
                    "focus":        question.get("focus", ""),
                    "answer":       answer,
                    "score":        5,
                    "feedback":     f"Network connection error to AI scorer ({e}). Default score recorded.",
                    "strengths":    "Answer recorded.",
                    "improvement":  "Please verify connection.",
                }
            time.sleep(1)
    result  = _parse_json_response(content)

    # Clamp score to valid range
    result["score"] = max(1, min(10, int(result.get("score", 5))))

    return {
        "question_id":  question["id"],
        "question":     question["question"],
        "category":     question["category"],
        "focus":        question.get("focus", ""),
        "answer":       answer,
        "score":        result["score"],
        "feedback":     result.get("feedback", ""),
        "strengths":    result.get("strengths", ""),
        "improvement":  result.get("improvement", ""),
    }


def _parse_json_response(content: str) -> dict:
    """Robustly extract a JSON object from LLM output."""
    content = re.sub(r"```(?:json)?", "", content).strip()
    content = content.strip("`").strip()

    start = content.find("{")
    end   = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start : end + 1]

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Score JSON parse error: {e}\nRaw:\n{content[:300]}")
        # Return a safe fallback rather than crashing the interview
        return {
            "score":       5,
            "feedback":    "Could not parse LLM response. Score defaulted to 5.",
            "strengths":   "N/A",
            "improvement": "N/A",
        }
