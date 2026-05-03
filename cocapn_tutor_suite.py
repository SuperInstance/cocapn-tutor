"""cocapn_tutor_suite.py — Unified FLUX v3.0 Agent Lifecycle Demo.

Shows all 4 tutor repos working together:
  1. cocapn-shells  → Spawn agent shell (register file + capabilities)
  2. cocapn-curriculum → Load competency DAG (bytecode modules)
  3. cocapn-tutor    → Execute lesson via bytecode VM
  4. cocapn-lessons  → Record trial, compile hot path

This is the "Hello World" of the FLUX v3.0 ecosystem.
"""
import sys
sys.path.insert(0, '/tmp/fleet-repos/cocapn-shells')
sys.path.insert(0, '/tmp/fleet-repos/cocapn-curriculum')
sys.path.insert(0, '/tmp/fleet-repos/cocapn-tutor')
sys.path.insert(0, '/tmp/fleet-repos/cocapn-lessons')

from cocapn_shells_flux import FluxShell
from cocapn_curriculum_flux import FluxCurriculum
from cocapn_tutor_flux import unit, TutorCompiler
from cocapn_lessons_flux import FluxLessonLibrary


def main():
    print("=" * 60)
    print("FLUX v3.0 Unified Agent Lifecycle")
    print("=" * 60)
    
    # ── Phase 1: Spawn Shell (cocapn-shells) ────────────────────────────
    print("\n[1] SPAWN SHELL")
    shell = FluxShell.spawn("scout-001", class_="MUD Explorer")
    shell.add_quest("Map 5 MUD rooms", bytecode=b"\x2b\x00\x05\x00")
    shell.gain_xp(600, quest="probe attempt", tags=["mud", "network"])
    print(f"  Shell: {shell.name} | Level: {shell.level} | XP: {shell.xp}")
    print(f"  PM: {hex(shell.capabilities)} | RP: {shell.regs[14]}")
    
    # ── Phase 2: Load Curriculum (cocapn-curriculum) ────────────────────
    print("\n[2] LOAD CURRICULUM")
    cv = FluxCurriculum.fleet_default()
    available = cv.available_to(shell)
    print(f"  Competencies: {len(cv.competencies)}")
    print(f"  Available to {shell.level}: {len(available)}")
    for c in available[:3]:
        print(f"    - {c.name} ({c.id})")
    
    # Get personalized bytecode for this shell
    personal = cv.shell_bytecode(shell)
    print(f"  Personalized bytecode: {len(personal)} bytes")
    
    # ── Phase 3: Execute Lesson (cocapn-tutor) ──────────────────────────
    print("\n[3] EXECUTE LESSON")
    comp = TutorCompiler()
    
    @unit("MUD Room Mapping", level="Recruit")
    def mud_lesson(a):
        a.lesson("MUD rooms are identified by unique IDs. Use 'look' to inspect.")
        a.reference("MUD Protocol", "https://cocapn.ai/docs/mud")
        a.exercise("List the 3 core rooms in the Harbor")
        a.assess("harbor, forge, tide-pool")
    
    result = mud_lesson()
    print(f"  Unit: {result.get('name')}")
    print(f"  Bytecode: {result.get('bytecode_size')} bytes, {result.get('cycles')} cycles")
    print(f"  R4 (answer): {result.get('registers', {}).get('R4', 'N/A')}")
    print(f"  Completed: {result.get('completed', False)}")
    
    # ── Phase 4: Record Trial (cocapn-lessons) ────────────────────────────
    print("\n[4] RECORD TRIAL")
    lib = FluxLessonLibrary()
    lesson = lib.get_or_create("MUD Room Mapping")
    lesson.description = "Navigate MUD rooms and identify core locations."
    
    # Simulate trial outcomes
    lesson.record_trial(
        agent="scout-001",
        success=True,
        technique="direct_mud_look",
        tokens_used=450,
        tags=["mud", "explore"],
        bytecode_hash=personal.hex()[:16]
    )
    lesson.record_trial(
        agent="scout-002",
        success=False,
        error="Connection timeout to port 4042",
        technique="direct_mud_look",
        tokens_used=1200,
        tags=["mud", "network"],
        bytecode_hash="deadbeef"
    )
    lesson.record_trial(
        agent="scout-003",
        success=True,
        technique="direct_mud_look",
        tokens_used=380,
        tags=["mud", "explore"],
        bytecode_hash=personal.hex()[:16]
    )
    
    print(f"  Trials: {lesson.total_attempts}")
    print(f"  Success rate: {lesson.success_rate:.0%}")
    print(f"  JIT stats: {lesson.jit_stats()}")
    print(f"  Predicted failure rate (10 agents): {lesson.predict_failure_rate(10):.0%}")
    print(f"\n  {lesson.advice_for_new_agent()}")
    
    # ── Phase 5: Shell evolves ───────────────────────────────────────────
    print("\n[5] SHELL EVOLUTION")
    # Award XP for completing the lesson
    leveled_up = shell.gain_xp(lesson.total_attempts * 100, quest="MUD Room Mapping")
    print(f"  XP gained: {lesson.total_attempts * 100}")
    print(f"  Level up: {leveled_up}")
    print(f"  New level: {shell.level} | PM: {hex(shell.capabilities)}")
    
    # Re-check available competencies with new level
    available_now = cv.available_to(shell)
    new_comps = [c.name for c in available_now if c.id not in [x.id for x in available]]
    if new_comps:
        print(f"  Newly available: {', '.join(new_comps)}")
    
    # ── Phase 6: Snapshot for edge transfer ──────────────────────────────
    print("\n[6] SNAPSHOT")
    snap = shell.snapshot()
    print(f"  Snapshot size: {len(snap)} bytes")
    restored = FluxShell.restore(snap)
    print(f"  Restored: {restored.name} | level={restored.level} | PM={hex(restored.capabilities)}")
    
    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("LIFECYCLE COMPLETE")
    print("=" * 60)
    print(f"Fleet stats: {lib.fleet_stats()}")
    print(f"Curriculum: {len(cv.competencies)} competencies, {len(cv.global_bytecode)} bytes global")
    print(f"Shell: {shell.name} | {shell.level} | {shell.xp} XP | {len(shell.snapshots)} snapshots")
    print(f"\nAll 4 repos integrated: shells → curriculum → tutor → lessons")
    print(f"FLUX v3.0 ABI: RP=R14, PM=R15, PULSE, POLL, FORK, WITNESS")


if __name__ == "__main__":
    main()
