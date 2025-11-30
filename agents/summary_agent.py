# agents/summary_agent.py
from typing import List, Dict

class SummaryAgent:
    """
    Minimal summary agent:
    - produces a small JSON summary with completed/pending and a human-friendly paragraph.
    - works without an LLM (deterministic).
    """
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def generate_end_of_day_summary(self, tasks: List[Dict]) -> Dict:
        completed = [t for t in tasks if t.get("status") == "done"]
        pending = [t for t in tasks if t.get("status") != "done"]
        suggestions = [p.get("title") for p in pending[:3]]
        paragraph = (
            f"Today you completed {len(completed)} task(s). "
            f"{len(pending)} task(s) remain. Suggested focus for tomorrow: "
            + (", ".join(suggestions) if suggestions else "no pending tasks.")
        )
        return {"completed": completed, "pending": pending, "suggestions": suggestions, "text": paragraph}
