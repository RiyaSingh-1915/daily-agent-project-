# agents/intake_agent.py
import re
import json
import logging
from typing import Dict
from pydantic import BaseModel, Field

from memory.session_memory import SessionMemory
from memory.memory_bank import MemoryBank
from tools.save_task_tool import SaveTaskTool

log = logging.getLogger(__name__)


class TaskModel(BaseModel):
    title: str
    description: str = None
    due_date: str = None
    duration_minutes: int = None
    tags: list = Field(default_factory=list)
    priority_hint: str = None


class IntakeAgent:
    """
    IntakeAgent: Parses user text into structured task data.
    Supports optional LLM parser and naive fallback parser.
    """

    def __init__(self, session: SessionMemory, memory: MemoryBank, llm_client=None):
        self.session = session
        self.memory = memory
        self.save_tool = SaveTaskTool(memory)
        self.llm_client = llm_client

    # -------------------------------------
    # NAIVE PARSER (fallback logic)
    # -------------------------------------
    def _naive_parse(self, user_text: str) -> Dict:
        title = user_text.strip()
        duration = None

        # detect hours
        m = re.search(r"(\d+)\s*(hour|hours|hr)", user_text, re.I)
        if m:
            duration = int(m.group(1)) * 60

        # detect minutes
        m2 = re.search(r"(\d+)\s*(min|minute|minutes)", user_text, re.I)
        if m2 and not duration:
            duration = int(m2.group(1))

        tags = []
        if "meeting" in user_text.lower():
            tags.append("meeting")

        return {
            "title": title,
            "description": user_text,
            "duration_minutes": duration,
            "tags": tags
        }

    # -------------------------------------
    # OPTIONAL LLM PARSER (JSON)
    # -------------------------------------
    def _llm_parse_to_json(self, user_text: str) -> Dict:
        if self.llm_client:
            prompt = f"""
Convert this user text into JSON with keys:
title, description, due_date, duration_minutes, tags, priority_hint.
Return only JSON.

User text: {user_text}
"""
            try:
                resp = self.llm_client.generate(prompt=prompt, max_tokens=300)
                text = getattr(resp, "text", "") or ""
                j = re.search(r"\{.*\}", text, re.S)
                if j:
                    return json.loads(j.group(0))
            except Exception:
                log.warning("LLM parsing failed, using naive fallback.")

        # fallback parser
        return self._naive_parse(user_text)

    # -------------------------------------
    # MAIN HANDLE FUNCTION
    # -------------------------------------
    def handle(self, user_text: str) -> Dict:
        self.session.add_message("user", user_text)

        parsed = self._llm_parse_to_json(user_text)
        task = TaskModel(**parsed).dict()

        # --------------------------
        # DEDUPE CHECK
        # --------------------------
        existing = self.memory.get_tasks()
        titles = [t.get("title", "").strip().lower() for t in existing]

        if task["title"].strip().lower() in titles:
            log.info("Duplicate task detected, not saving: %s", task["title"])
            return {"success": False, "error": "Duplicate task"}

        # Save task
        saved = self.save_tool.run(task)

        if saved.get("success"):
            log.info(
                "Saved task id=%s title=%s",
                saved["task"].get("id"),
                saved["task"].get("title")
            )
            self.session.add_message("assistant", f"Saved task: {task['title']}")
            return {"success": True, "task": saved["task"]}

        log.warning("Failed to save task: %s", saved.get("error"))
        return {"success": False, "error": saved.get("error")}
