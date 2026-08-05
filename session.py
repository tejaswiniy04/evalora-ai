"""
session.py — Interview Session State & Transcript Management

Manages all state for a single interview session and persists it
to a structured JSON transcript file for later review.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class InterviewSession:
    """
    Holds all state for one interview session.

    Attributes:
        role:           Job role being interviewed for.
        skills:         Required skills list.
        candidate_name: Candidate's name (defaults to "Anonymous").
        session_id:     Unique ID based on start timestamp.
        started_at:     ISO timestamp when the session was created.
        questions:      List of generated question dicts.
        qa_results:     List of scored Q&A result dicts.
        evaluation:     Final evaluation dict (populated at the end).
    """

    role:           str
    skills:         list[str]
    candidate_name: str        = "Anonymous"
    session_id:     str        = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    started_at:     str        = field(default_factory=lambda: datetime.now().isoformat())
    questions:      list[dict] = field(default_factory=list)
    qa_results:     list[dict] = field(default_factory=list)
    evaluation:     dict       = field(default_factory=dict)

    # ── Mutators ──────────────────────────────────────────────────────────

    def add_result(self, result: dict) -> None:
        """Append a scored Q&A result to the session."""
        self.qa_results.append(result)

    # ── Computed Properties ───────────────────────────────────────────────

    @property
    def average_score(self) -> float:
        """Raw average score across all answered questions (out of 10)."""
        if not self.qa_results:
            return 0.0
        return sum(r["score"] for r in self.qa_results) / len(self.qa_results)

    @property
    def questions_answered(self) -> int:
        return len(self.qa_results)

    # ── Persistence ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise the session to a plain dict."""
        return {
            "session_id":        self.session_id,
            "candidate_name":    self.candidate_name,
            "role":              self.role,
            "skills":            self.skills,
            "started_at":        self.started_at,
            "completed_at":      datetime.now().isoformat(),
            "questions_count":   len(self.questions),
            "average_score_10":  round(self.average_score, 2),
            "overall_score_100": round(self.evaluation.get("overall_score", 0), 1),
            "recommendation":    self.evaluation.get("recommendation", ""),
            "questions":         self.questions,
            "qa_results":        self.qa_results,
            "evaluation":        self.evaluation,
        }

    def save(self, output_dir: str = "transcripts") -> str:
        """
        Save the full session transcript to a JSON file.

        Args:
            output_dir: Directory to write the transcript (created if needed).

        Returns:
            The path of the saved file.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        safe_role = self.role.replace(" ", "_").replace("/", "-")
        filename  = f"{output_dir}/interview_{self.session_id}_{safe_role}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Transcript saved → {filename}")
        return filename

    # ── Display Helpers ───────────────────────────────────────────────────

    def score_summary(self) -> list[dict]:
        """Return a lightweight per-question score summary."""
        return [
            {
                "Q":          r["question_id"],
                "category":   r["category"],
                "score":      r["score"],
                "question":   r["question"][:60] + ("..." if len(r["question"]) > 60 else ""),
            }
            for r in self.qa_results
        ]
