# agents/prioritization_agent.py
from datetime import datetime
from typing import List, Dict
import logging

log = logging.getLogger(__name__)


def _days_left_iso(iso_str: str) -> float:
    if not iso_str:
        return 9999.0  # treat no due date as very far
    try:
        dt = datetime.fromisoformat(iso_str)
        delta = dt - datetime.utcnow()
        return max(delta.days + delta.seconds / 86400.0, 0.0)
    except Exception:
        return 9999.0


def score_task(task: Dict) -> float:
    days = _days_left_iso(task.get("due_date"))

    urgency = 1.0 / (days + 0.5)

    importance_map = {"high": 1.0, "medium": 0.6, "low": 0.2}
    importance = importance_map.get(task.get("priority_hint"), 0.5)

    duration = (task.get("duration_minutes") or 30)
    duration_penalty = min(duration / 120.0, 1.0)

    score = 0.6 * urgency + 0.4 * importance - 0.1 * duration_penalty
    return float(score)


def prioritize(tasks: List[Dict]) -> List[Dict]:
    """Attach a _score to each task and return sorted by score descending."""
    for t in tasks:
        try:
            t["_score"] = score_task(t)
        except Exception:
            t["_score"] = 0.0

    ordered = sorted(tasks, key=lambda x: x.get("_score", 0.0), reverse=True)

    # Logging: number of tasks and top 3
    try:
        log.info("Prioritized %d tasks", len(ordered))

        top3 = ordered[:3]
        if top3:
            summary = ", ".join([f"{t.get('title')}({t.get('_score'):.2f})" for t in top3])
            log.info("Top tasks: %s", summary)
        else:
            log.info("Top tasks: none")

    except Exception:
        log.exception("Failed to log prioritization summary")

    return ordered


