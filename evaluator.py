"""
evaluator.py — Final Interview Evaluation Generator

After all questions are answered, this module synthesises a comprehensive
evaluation report including:
  - Overall score (weighted average, out of 100)
  - Hire recommendation (4 tiers)
  - Technical & communication assessment
  - Top strengths and key gaps
  - Executive summary paragraph
  - Suggested next steps
"""

import os
import json
import logging
import re

logger = logging.getLogger(__name__)

EVAL_SYSTEM_PROMPT = """You are a senior hiring manager writing a post-interview evaluation report.
Be specific, honest, and constructive. Base your assessment strictly on the interview data provided.
Return ONLY valid JSON — no markdown, no preamble, no extra text."""

# Category weights for overall score calculation
CATEGORY_WEIGHTS = {
    "Technical":    0.40,
    "Behavioral":   0.25,
    "Situational":  0.20,
    "Motivation":   0.15,
}


def generate_evaluation(role: str, skills: list[str], qa_results: list[dict], client) -> dict:
    """
    Generate a comprehensive final evaluation.

    Args:
        role:       Job role title.
        skills:     Required skills list.
        qa_results: List of scored Q&A dicts from answer_scorer.
        client:     Initialized Groq client.

    Returns:
        Evaluation dict with keys:
          overall_score, recommendation, technical_assessment,
          communication_assessment, strengths, gaps, summary, next_steps
    """
    weighted_score = _compute_weighted_score(qa_results)

    # Build the Q&A summary for the LLM
    qa_lines = []
    for r in qa_results:
        snippet = r["answer"][:250] + ("..." if len(r["answer"]) > 250 else "")
        qa_lines.append(
            f"Q{r['question_id']} [{r['category']}] — {r['question']}\n"
            f"  Score: {r['score']}/10 | Answer: {snippet}"
        )
    qa_text = "\n\n".join(qa_lines)

    user_prompt = f"""Write a post-interview evaluation for a "{role}" candidate.
Required skills: {", ".join(skills)}
Computed overall score: {weighted_score:.1f}/100

Full interview transcript:
{qa_text}

Return ONLY this JSON (no markdown):
{{
  "overall_score":             {weighted_score:.0f},
  "recommendation":            "STRONGLY RECOMMEND" | "RECOMMEND" | "BORDERLINE" | "DO NOT RECOMMEND",
  "technical_assessment":      "<2–3 sentences on technical knowledge and skill depth>",
  "communication_assessment":  "<1–2 sentences on clarity, structure, and communication quality>",
  "strengths": [
    "<specific strength 1 with evidence from the interview>",
    "<specific strength 2>",
    "<specific strength 3>"
  ],
  "gaps": [
    "<specific gap 1 with evidence>",
    "<specific gap 2>"
  ],
  "summary":    "<3–4 sentence executive summary of the candidate>",
  "next_steps": "<1–2 sentences of clear, actionable next steps e.g. 'Reject application and archive candidate profile for future openings', or 'Schedule follow-up System Design interview'>"
}}"""

    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        messages=[
            {"role": "system", "content": EVAL_SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=1000,
    )

    content    = response.choices[0].message.content.strip()
    evaluation = _parse_json_response(content)

    # Always use our computed score (don't let LLM override it)
    evaluation["overall_score"] = round(weighted_score, 1)

    logger.info(
        f"Evaluation complete. Score: {evaluation['overall_score']}/100 | "
        f"Recommendation: {evaluation.get('recommendation', 'N/A')}"
    )
    return evaluation


def _compute_weighted_score(qa_results: list[dict]) -> float:
    """
    Compute the weighted overall score (out of 100).

    Each category is averaged separately, then combined with weights.
    Falls back to a simple average if a category has no questions.
    """
    category_scores: dict[str, list[float]] = {}
    for r in qa_results:
        cat = r.get("category", "Technical")
        category_scores.setdefault(cat, []).append(r["score"])

    if not category_scores:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0
    for cat, weight in CATEGORY_WEIGHTS.items():
        if cat in category_scores:
            avg = sum(category_scores[cat]) / len(category_scores[cat])
            weighted_sum += avg * weight
            total_weight  += weight

    if total_weight == 0:
        # Fallback: simple average
        all_scores = [r["score"] for r in qa_results]
        return (sum(all_scores) / len(all_scores)) * 10

    # Normalise to 100-point scale
    return (weighted_sum / total_weight) * 10


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
        logger.error(f"Evaluation JSON parse error: {e}\nRaw:\n{content[:500]}")
        return {
            "overall_score":            50,
            "recommendation":           "BORDERLINE",
            "technical_assessment":     "Could not generate assessment.",
            "communication_assessment": "Could not generate assessment.",
            "strengths":                ["Completed the interview"],
            "gaps":                     ["Assessment unavailable"],
            "summary":                  "Evaluation could not be generated due to a parsing error.",
            "next_steps":               "Manual review recommended.",
        }
