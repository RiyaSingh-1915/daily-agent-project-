# memory/session_memory.py
from collections import deque
from typing import List, Dict

class SessionMemory:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self._deque = deque(maxlen=capacity)

    def add_message(self, role: str, text: str):
        """Add a message dict with role and text."""
        self._deque.append({"role": role, "text": text})

    def get_recent(self, n: int = 10) -> List[Dict]:
        """Return the last n messages as a list (oldest first)."""
        return list(self._deque)[-n:]

    def clear(self):
        """Clear the session memory."""
        self._deque.clear()
