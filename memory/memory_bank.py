# memory/memory_bank.py
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
import tempfile
import os

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
if not DATA_PATH.exists():
    DATA_PATH.write_text("[]")

class MemoryBank:
    def __init__(self, path: str = None):
        self.path = Path(path) if path else DATA_PATH

    def _read(self) -> List[Dict]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
        except FileNotFoundError:
            return []

    def _write(self, items: List[Dict]):
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(self.path.parent))
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, default=str)
            os.replace(tmp_path, self.path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def save_task(self, task: Dict) -> Dict:
        items = self._read()
        task_id = task.get("id") or str(uuid.uuid4())
        task.update({
            "id": task_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": task.get("status", "todo")
        })
        items.append(task)
        self._write(items)
        return task

    def get_tasks(self, filters: Dict = None) -> List[Dict]:
        items = self._read()
        if not filters:
            return items
        out = items
        if "status" in filters:
            out = [t for t in out if t.get("status") == filters["status"]]
        if "tag" in filters:
            out = [t for t in out if filters["tag"] in (t.get("tags") or [])]
        return out

    def update_task(self, task_id: str, updates: Dict) -> Optional[Dict]:
        items = self._read()
        for t in items:
            if t.get("id") == task_id:
                t.update(updates)
                self._write(items)
                return t
        return None

    def delete_task(self, task_id: str) -> bool:
        items = self._read()
        new = [t for t in items if t.get("id") != task_id]
        if len(new) == len(items):
            return False
        self._write(new)
        return True
