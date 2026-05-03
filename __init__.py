"""cocapn_tutor — FLUX v3.0 Tutor Personality Module.

This package provides two API levels:

1. **Python-native API** (`cocapn_tutor`):
   - TUTOR interpreter with `@unit` decorator
   - 12 pedagogical primitives (lesson, exercise, assess, spawn, etc.)
   - Zero-dependency, stdlib only

2. **FLUX v3.0 Bytecode API** (`cocapn_tutor_flux`):
   - Same `@unit` decorator, compiles to FLUX bytecode internally
   - Executes on 16-register VM with PULSE/POLL/FORK opcodes
   - R14=RP (Resource Pointer), R15=PM (Permission Mask)
   - Endian-independent SNAPSHOT/RESTORE

Import either:
  >>> from cocapn_tutor import unit, TUTOR      # Python-native
  >>> from cocapn_tutor_flux import unit, TutorVM  # FLUX bytecode

Or run:
  $ python3 -m cocapn_tutor          # Runs FLUX v3.0 demo by default
  $ python3 cocapn_tutor_suite.py    # Full lifecycle integration demo
"""

# Re-export the FLUX v3.0 API as the default
from cocapn_tutor_flux import (
    unit, TutorCompiler, TutorVM, Assembler, Op,
    main as run_demo
)

# Also expose the Python-native API for backwards compatibility
try:
    from cocapn_tutor import TUTOR, Mission
except ImportError:
    TUTOR = None
    Mission = None

__version__ = "3.0.0"
__all__ = ["unit", "TutorCompiler", "TutorVM", "Assembler", "Op", "run_demo"]
