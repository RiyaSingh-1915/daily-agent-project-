import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from logging_setup import configure_logging
logger = configure_logging()
logger.info("Starting AI Daily Task Agent demo")

print("DEBUG: Project root added to sys.path:", os.path.dirname(os.path.abspath(__file__)))

# main.py
import sys
from datetime import date
from memory.session_memory import SessionMemory
from memory.memory_bank import MemoryBank
from agents.intake_agent import IntakeAgent
from agents.prioritization_agent import prioritize
from agents.scheduler_agent import SchedulerAgent
from agents.summary_agent import SummaryAgent

def demo_flow():
    print("Running demo flow...")  # Debug print

    session = SessionMemory()
    memory = MemoryBank()
    intake = IntakeAgent(session, memory)
    summary_agent = SummaryAgent()
    scheduler = SchedulerAgent()

    print("Adding demo tasks...")
    intake.handle("Finish ML assignment tomorrow 3 hours")
    intake.handle("Buy groceries today 30min")

    tasks = memory.get_tasks()
    print(f"Loaded {len(tasks)} tasks from memory")

    ordered = prioritize(tasks)
    print(f"Found {len(ordered)} tasks after prioritization")

    sched = scheduler.create_daily_schedule(date.today(), ordered)
    print("Schedule:")
    for s in sched["scheduled"]:
        print(s)

    print("Unscheduled tasks:")
    for u in sched["unscheduled"]:
        print(u.get("title"))

    summary = summary_agent.generate_end_of_day_summary(tasks)
    print("Summary text:\n", summary["text"])

if __name__ == "__main__":
    print("MAIN.PY STARTED")   # Very important debug print
    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if cmd == "demo":
        demo_flow()
    else:
        print("Available: demo")

