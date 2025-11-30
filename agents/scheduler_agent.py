# agents/scheduler_agent.py
from datetime import datetime, timedelta, time
from typing import List, Dict
import logging

log = logging.getLogger(__name__)


class SchedulerAgent:
    """
    Simple greedy scheduler:
    Schedules tasks between work_start and work_end.
    Inserts short buffer after each task.
    """

    def __init__(self, work_start: time = time(9, 0), work_end: time = time(18, 0)):
        self.work_start = work_start
        self.work_end = work_end

    def _to_dt(self, date_obj, t: time) -> datetime:
        return datetime.combine(date_obj, t)

    def create_daily_schedule(self, date_obj, tasks: List[Dict]) -> Dict:
        """
        tasks: list of dicts, prioritized already
        Return:
            {
              "scheduled": [ ... ],
              "unscheduled": [ ... ]
            }
        """
        cursor = self._to_dt(date_obj, self.work_start)
        end_dt = self._to_dt(date_obj, self.work_end)

        scheduled = []
        unscheduled = []

        for t in tasks:
            try:
                dur = int(t.get("duration_minutes") or 30)
            except Exception:
                dur = 30

            slot_end = cursor + timedelta(minutes=dur)

            if slot_end <= end_dt:
                # schedule task
                scheduled.append({
                    "task_id": t.get("id"),
                    "title": t.get("title"),
                    "start": cursor.isoformat(),
                    "end": slot_end.isoformat(),
                })

                # buffer 5 minutes
                cursor = slot_end + timedelta(minutes=5)

                # insert break if long task ≥ 90 minutes
                if dur >= 90:
                    break_end = cursor + timedelta(minutes=15)
                    if break_end <= end_dt:
                        scheduled.append({
                            "task_id": None,
                            "title": "Short break",
                            "start": cursor.isoformat(),
                            "end": break_end.isoformat(),
                        })
                        cursor = break_end

            else:
                unscheduled.append(t)

        # logging
        try:
            log.info(
                "Schedule created for %s: %d scheduled, %d unscheduled",
                date_obj.isoformat(), len(scheduled), len(unscheduled)
            )

            if scheduled:
                first = scheduled[0]
                last = scheduled[-1]
                log.info("First task: %s %s -> %s", first["title"], first["start"], first["end"])
                log.info("Last task: %s %s -> %s", last["title"], last["start"], last["end"])
        except Exception:
            log.exception("Failed to log scheduler summary")

        return {"scheduled": scheduled, "unscheduled": unscheduled}
