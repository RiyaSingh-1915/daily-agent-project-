# tools/save_task_tool.py
from typing import Dict
from memory.memory_bank import MemoryBank

class SaveTaskTool:
    def __init__(self, memory: MemoryBank):
        self.memory = memory

    def run(self, task: Dict) -> Dict:
        # Basic validation
        if not task.get("title") or not str(task.get("title")).strip():
            return {"success": False, "error": "Task must have a non-empty title"}
        # Normalize tags
        task['tags'] = task.get('tags') or []
        if isinstance(task['tags'], str):
            task['tags'] = [t.strip() for t in task['tags'].split(',') if t.strip()]
        saved = self.memory.save_task(task)
        return {"success": True, "task": saved}
