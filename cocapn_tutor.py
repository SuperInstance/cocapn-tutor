"""cocapn_tutor — Minimal TUTOR interpreter for fleet agent pedagogy.

Implements the core pedagogical primitives from the TUTOR spec:
  unit, lesson, exercise, assess, reference, trial
Plus fleet primitives:
  connect, move, look, interact, submit, spawn

Each primitive is a Python function. An 'atunit' is a function decorated
with @unit that the interpreter can execute step by step.

Usage:
    @unit("MUD Exploration", level="Sailor")
    def mud_exploration():
        lesson("Harbor layout")
        exercise("List all exits from Harbor")
        submit("/submit/tile", {"domain": "mud", "content": "..."})
        assess(success=True, xp=500)

    run(mud_exploration)
"""
import json
import inspect
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any
from datetime import datetime, timezone

_current_unit: "Unit" = None
_current_agent: str = "unknown"
_log: List[Dict] = []


@dataclass
class Unit:
    """A pedagogical unit — like a quest or mission."""
    title: str
    level: str = "Recruit"
    steps: List[Dict] = field(default_factory=list)
    completed: bool = False
    xp_earned: int = 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def unit(title: str, level: str = "Recruit"):
    """Decorator to mark a function as a TUTOR unit."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            global _current_unit
            _current_unit = Unit(title=title, level=level)
            _log.append({"type": "unit_start", "title": title, "level": level, "at": _now()})
            try:
                result = func(*args, **kwargs)
                _current_unit.completed = True
                _log.append({"type": "unit_complete", "title": title, "xp": _current_unit.xp_earned, "at": _now()})
                return result
            except Exception as e:
                _log.append({"type": "unit_fail", "title": title, "error": str(e), "at": _now()})
                raise
            finally:
                _current_unit = None
        wrapper._tutor_unit = True
        wrapper._title = title
        wrapper._level = level
        return wrapper
    return decorator


def lesson(text: str):
    """Present a lesson (informational step)."""
    step = {"type": "lesson", "text": text, "at": _now()}
    _current_unit.steps.append(step)
    _log.append(step)
    print(f"  [lesson] {text}")


def exercise(prompt: str, expected: Any = None):
    """Present an exercise (agent must produce answer)."""
    step = {"type": "exercise", "prompt": prompt, "expected": expected, "at": _now()}
    _current_unit.steps.append(step)
    _log.append(step)
    print(f"  [exercise] {prompt}")


def assess(success: bool, xp: int = 0, feedback: str = ""):
    """Assess performance and award XP."""
    step = {"type": "assess", "success": success, "xp": xp, "feedback": feedback, "at": _now()}
    if _current_unit:
        _current_unit.xp_earned += xp
    _current_unit.steps.append(step)
    _log.append(step)
    status = "✓" if success else "✗"
    print(f"  [assess] {status} {xp}xp — {feedback}")


def reference(topic: str, url: str = ""):
    """Reference material (link to docs, paper, example)."""
    step = {"type": "reference", "topic": topic, "url": url, "at": _now()}
    _current_unit.steps.append(step)
    _log.append(step)
    print(f"  [ref] {topic} {'→ ' + url if url else ''}")


def trial(task: str, success: bool, error: str = "", tokens: int = 0):
    """Record a trial (negative example for learning)."""
    step = {"type": "trial", "task": task, "success": success, "error": error, "tokens": tokens, "at": _now()}
    _current_unit.steps.append(step)
    _log.append(step)
    status = "✓" if success else "✗"
    print(f"  [trial] {status} {task} ({tokens} tokens)")


# --- Fleet primitives ---

def connect(service: str):
    """Connect to a fleet service."""
    print(f"  [connect] → {service}")
    _log.append({"type": "connect", "service": service, "at": _now()})


def move(room: str):
    """Move to a MUD room."""
    print(f"  [move] → {room}")
    _log.append({"type": "move", "room": room, "at": _now()})


def look(target: str = ""):
    """Look at current room or specific target."""
    print(f"  [look] {target or 'around'}")
    _log.append({"type": "look", "target": target, "at": _now()})


def interact(entity: str, action: str = ""):
    """Interact with an entity (NPC, object)."""
    print(f"  [interact] {action} {entity}")
    _log.append({"type": "interact", "entity": entity, "action": action, "at": _now()})


def submit(endpoint: str, payload: Dict):
    """Submit data to PLATO or another endpoint."""
    print(f"  [submit] → {endpoint} ({len(json.dumps(payload))} bytes)")
    _log.append({"type": "submit", "endpoint": endpoint, "payload_size": len(json.dumps(payload)), "at": _now()})


def spawn(agent_name: str, mission: str = ""):
    """Spawn a subagent."""
    print(f"  [spawn] {agent_name} — {mission}")
    _log.append({"type": "spawn", "agent": agent_name, "mission": mission, "at": _now()})


# --- Execution ---

def run(unit_func: Callable) -> Unit:
    """Execute a TUTOR unit and return its record."""
    global _log
    _log = []
    unit_func()
    # _current_unit is cleared in wrapper's finally, so we capture from log
    for entry in reversed(_log):
        if entry.get("type") == "unit_complete":
            return Unit(title=entry["title"], completed=True, xp_earned=entry.get("xp", 0))
        if entry.get("type") == "unit_fail":
            return Unit(title=entry["title"], completed=False)
    return Unit(title="unknown")


def transcript() -> List[Dict]:
    """Full execution transcript."""
    return _log.copy()


def export_json(path: str = "tutor_transcript.json"):
    """Save transcript to JSON."""
    with open(path, "w") as f:
        json.dump(_log, f, indent=2, default=str)
    return path


# --- Demo ---

@unit("First MUD Exploration", level="Recruit")
def first_mud_exploration():
    lesson("The Harbor is the fleet's central hub. It has exits to every lab.")
    reference("MUD Protocol", "https://cocapn.ai/docs/mud")
    connect("MUD v3")
    move("harbor")
    look()
    exercise("List at least 3 exits from Harbor")
    assess(success=True, xp=100, feedback="Correct — Harbor has 18 exits.")


@unit("Submit First Tile", level="Recruit")
def submit_first_tile():
    lesson("PLATO tiles are the fleet's knowledge unit. Each tile has a domain, agent, and payload.")
    connect("PLATO Gate")
    exercise("Construct a tile with domain='tutorial', agent='you', payload='hello fleet'")
    submit("/submit/tile", {"domain": "tutorial", "agent": "recruit", "payload": "hello fleet"})
    trial(task="tile formatting", success=False, error="missing agent field", tokens=1200)
    trial(task="tile formatting", success=True, error="", tokens=800)
    assess(success=True, xp=200, feedback="Tile accepted by gate.")


if __name__ == "__main__":
    print("=== First MUD Exploration ===")
    u1 = run(first_mud_exploration)
    print(f"Completed: {u1.completed} | XP: {u1.xp_earned}\n")

    print("=== Submit First Tile ===")
    u2 = run(submit_first_tile)
    print(f"Completed: {u2.completed} | XP: {u2.xp_earned}\n")

    print(f"Total steps logged: {len(transcript())}")
    export_json()
    print("Transcript saved to tutor_transcript.json")
