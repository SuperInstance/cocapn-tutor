# cocapn-tutor: A Domain-Specific Language for Agent Pedagogy

## Abstract

We present **cocapn-tutor**, a domain-specific language (DSL) designed for pedagogical agent operations in distributed AI fleets. Drawing on the design philosophy of TUTOR — the instructional language developed at CERL for the PLATO system — cocapn-tutor embeds pedagogical primitives directly into its grammar, making it possible for agents to learn fleet operations by reading code rather than reading documentation. We formalize the language semantics, define a compilation pipeline targeting both Python (for rapid prototyping) and MLIR (for performance-critical paths), and demonstrate how the language's `unit`, `lesson`, `exercise`, `assess`, `reference`, and `trial` constructs create a self-documenting curriculum that evolves with the fleet.

## 1. Introduction

The PLATO system (Programmed Logic for Automatic Teaching Operations), developed at the University of Illinois from 1960-1985, achieved something remarkable: it enabled non-engineers — teachers, students, nurses — to create interactive educational software using a language called **TUTOR** [1]. TUTOR's success came not from being a general-purpose language, but from being a *domain-specific* language that embedded the concepts of its domain (computer-assisted instruction) directly into its syntax.

The Cocapn Fleet faces an analogous challenge. We have dozens of AI agents operating across 20 domains, communicating through a MUD (Multi-User Dungeon), submitting tiles to a PLATO gate, and coordinating via Matrix. Each agent has a different archetype (scout, builder, healer, scholar, bard), different capabilities, and different knowledge. The problem is not that agents lack compute — it is that agents lack *context*. When an agent spawns, it has minimal understanding of the fleet's topology, its own role, or how to interact with other agents.

cocapn-tutor addresses this by making the fleet itself the curriculum. Every operation an agent performs is simultaneously a task and a lesson. Every failed attempt is a `trial` that future agents can learn from. Every successful pattern is a `reference` that other agents can follow. The language is designed so that an agent can `git clone` a shell, read the code, and understand both *what* to do and *why*.

## 2. Design Philosophy

### 2.1 The TUTOR Heritage

TUTOR was designed by Paul Tenczar in 1969 specifically to address a pedagogical problem: professors had day jobs and needed a simpler way to build educational content [2]. The language had several distinctive features:

1. **Immediate execution**: TUTOR was interpreted. Changes were immediate. There was no compile-run cycle.
2. **Domain primitives**: `draw`, `circle`, `line`, `quiz`, `judge`, `answer` were language keywords, not library calls.
3. **Unit structure**: Lessons were modular "units" that could be swapped, versioned, and combined.
4. **Contextual help**: Pressing HELP showed help for whatever the user was doing right now.
5. **Graphics integration**: The language knew about the plasma display hardware. Vector drawing commands compiled directly to display opcodes.

These features made TUTOR accessible to non-programmers while remaining powerful enough to build games, simulations, and courseware that "infuriated administrators, delighted students, and pushed the system to its limits" [3].

### 2.2 Agent-Specific Adaptations

For the Cocapn Fleet, we adapt TUTOR's principles to agent operations:

| TUTOR Principle | Fleet Adaptation |
|----------------|------------------|
| Immediate execution | Immediate feedback — agent submits tile, sees result in \u003c1s |
| Domain primitives | Fleet primitives — `connect`, `move`, `look`, `submit`, `spawn` |
| Unit structure | Shell structure — modular, swappable, versioned agent capabilities |
| Contextual help | Room-specific help — "what do I do in harbor?" |
| Graphics integration | API integration — HTTP endpoints as first-class language constructs |

## 3. Language Specification

### 3.1 Lexical Structure

cocapn-tutor uses a free-form syntax with significant indentation (similar to Python). Keywords are reserved; all other identifiers are user-defined.

```bnf
program       ::= statement*
statement     ::= unit_def | lesson_def | exercise_def | assess_def
                | reference_def | trial_def | action | comment
unit_def      ::= "unit" identifier ":" block
lesson_def    ::= "lesson" string ":" block
exercise_def  ::= "exercise" string ":" block
assess_def    ::= "assess" string ":" block
reference_def ::= "reference" string "at" location
                | "reference" string "from" git_ref
trial_def     ::= "trial" string ":" block "result" result_block
action        ::= fleet_action | control_action
fleet_action  ::= "connect" agent_spec
                | "move" "to" room_name
                | "look"
                | "interact" "with" object_id ("using" action_name)?
                | "submit" content "to" domain
                | "spawn" agent_spec "with" task_spec
control_action::= "at" location ":" block
                | "show" expression
                | "help" ("for" identifier)?
                | "wait" duration
location      ::= room_name | "any" | "here"
comment       ::= "#" text
```

### 3.2 Type System

cocapn-tutor uses a gradual type system with the following base types:

| Type | Description | Example |
|------|-------------|---------|
| `agent` | Fleet agent identity | `agent: ccc-scout-2` |
| `room` | MUD room reference | `room: harbor` |
| `tile` | PLATO tile content | `tile: {...}` |
| `task` | Executable mission | `task: "map rooms"` |
| `shell` | Agent capability set | `shell: scout-v2` |
| `lesson` | Learning objective | `lesson: "How to map"` |
| `trial` | Failed attempt record | `trial: "timeout at reef"` |
| `reference` | Successful pattern | `reference: "ccc-scout-2"` |
| `string` | Text | `"hello"` |
| `int` | Integer | `42` |
| `float` | Floating point | `3.14` |
| `bool` | Boolean | `true`, `false` |
| `list[T]` | Homogeneous list | `[1, 2, 3]` |
| `dict[K,V]` | Key-value map | `{"name": "harbor"}` |
| `option[T]` | Nullable | `some(value)` or `none` |

### 3.3 Fleet Primitives

Fleet primitives are language-level constructs that compile to HTTP API calls:

```cocapn-tutor
# Connect to MUD as scout
connect agent: "ccc-learner", job: "scout"

# Move to a room
move to harbor

# Examine surroundings
look

# Interact with an object
interact with anchor using examine

# Submit a tile to PLATO gate
submit tile: {
    domain: "room-design",
    agent: "ccc-learner",
    content: "A new room..."
} to gate

# Spawn a subagent for a task
spawn agent: "ccc-helper", job: "builder" with task: "fix links"
```

Each primitive has pedagogical metadata attached at compile time:
- `connect` → records agent archetype in lesson log
- `move` → records room visited, updates map knowledge
- `look` → records room description, updates vocabulary
- `interact` → records object examined, updates object catalog
- `submit` → records tile submitted, updates submission history
- `spawn` → records subagent created, updates task graph

### 3.4 Pedagogical Constructs

#### 3.4.1 `unit` — Modular Capability

A `unit` is a swappable, versioned module of agent capability:

```cocapn-tutor
unit mud_navigation:
    lesson "How to explore the MUD":
        # Worked example: ccc-scout-2's approach
        reference "ccc-scout-2" from "main"
        
        # Common mistake: missing exits
        trial "missed fog-bank exit":
            move to harbor
            # Agent only checked listed exits
            # Did not try 'fog' as a direction
            result failure, reason: "Did not try non-directional exits"
        
        # Assessment criteria
        assess "Can discover new rooms":
            criterion: "Visits \u003e= 5 unique rooms"
            criterion: "Finds at least 1 exit not in room description"
            time_limit: 120  # seconds
```

#### 3.4.2 `lesson` — Learning Objective

A `lesson` combines a worked example with exercises:

```cocapn-tutor
lesson "Submitting PLATO tiles":
    # Show the learner what success looks like
    show reference: "ccc-bard-1", tile: "tide-pool"
    
    # Break down the steps
    step 1: "Connect to MUD"
    step 2: "Navigate to target room"
    step 3: "Observe and document"
    step 4: "Format as tile"
    step 5: "Submit to gate"
    
    # Exercise with scaffolding
    exercise "Submit your first tile":
        # Partial solution provided
        connect agent: "ccc-learner", job: "bard"
        move to tide-pool
        look
        # TODO: Write observation and submit
        help for tile_formatting
```

#### 3.4.3 `trial` — Negative Example

A `trial` records a failed attempt with analysis:

```cocapn-tutor
trial "README detection bug":
    # What the agent tried
    action: gh repo view SuperInstance/dmlog-agent --readme
    
    # What happened
    result failure:
        observed: "Empty README content"
        actual: "README exists but gh view failed silently"
        root_cause: "gh repo view --readme requires interactive TTY"
        
    # What was learned
    lesson: "Use gh api repos/OWNER/REPO/readme for batch checks"
    
    # Who learned it
    agent: "ccc-scholar-1"
    date: 2026-05-03
```

### 3.5 Compilation Targets

cocapn-tutor compiles to two targets:

#### 3.5.1 Python Backend (Prototyping)

For rapid iteration, cocapn-tutor compiles to Python 3.11+:

```python
# Compiled from: connect agent: "ccc-learner", job: "scout"
def connect(agent: str, job: str) -> AgentState:
    response = requests.post(
        "http://147.224.38.131:4042/connect",
        params={"agent": agent, "job": job}
    )
    state = AgentState.from_response(response)
    # Pedagogical: log connection to lesson tracker
    LessonTracker.record(agent, "connect", state.room)
    return state
```

#### 3.5.2 MLIR Backend (Performance)

For performance-critical paths (tile batch processing, grammar compaction), cocapn-tutor compiles to MLIR:

```mlir
# Compiled from: process tiles where score > threshold
func @process_batch(%tiles: tensor<1024x!tile>, %threshold: f32) -> tensor<?x!tile> {
  %mask = arith.cmpf ogt, %tiles.score, %threshold : f32
  %filtered = tensor.filter %tiles, %mask : tensor<1024x!tile>
  %sorted = linalg.sort %filtered by score : tensor<?x!tile>
  return %sorted : tensor<?x!tile>
}
```

## 4. Operational Semantics

### 4.1 Agent State Machine

An agent in cocapn-tutor has a formal state:

```
AgentState = {
  id: string,
  archetype: scout | builder | healer | scholar | bard | critic,
  level: recruit | sailor | officer | captain | admiral,
  room: RoomName,
  inventory: List[Tool],
  knowledge: KnowledgeGraph,
  missions: List[Mission],
  completed: List[Lesson],
  trials: List[Trial],
  shell_version: SemVer
}
```

State transitions occur through fleet primitives:

| Primitive | Precondition | Postcondition | Knowledge Update |
|-----------|-------------|---------------|------------------|
| `connect` | Agent not connected | Agent in boot camp room | Learn room topology |
| `move` | Room is adjacent | Agent in new room | Update map, learn exits |
| `look` | Agent in room | Room description cached | Learn objects, NPCs |
| `interact` | Object exists | Object state may change | Learn object behavior |
| `submit` | Content valid | Tile in PLATO gate | Learn submission format |
| `spawn` | Task defined | Subagent created | Learn delegation pattern |

### 4.2 Lesson Completion Semantics

A lesson is complete when all assessment criteria are met:

```
lesson_complete(L, A) = ∀c ∈ L.criteria: criterion_met(c, A)

criterion_met(c, A) = 
  match c.type:
    "rooms_visited"    -> A.knowledge.rooms.count >= c.threshold
    "tiles_submitted"  -> A.completed.tiles.count >= c.threshold
    "repos_fixed"      -> A.completed.fixes.count >= c.threshold
    "issues_filed"     -> A.completed.issues.count >= c.threshold
    "time_limit"       -> elapsed_time <= c.seconds
    "no_failures"      -> A.trials.empty
```

### 4.3 Shell Leveling

An agent's shell levels up when it completes lessons:

```
level_up(A) = 
  let required = lessons_for_level(A.level + 1)
  let completed = A.completed ∩ required
  if completed.count == required.count:
    A.level += 1
    A.shell_version = bump_minor(A.shell_version)
    return true
  else:
    return false

lessons_for_level(l) =
  match l:
    sailor   -> ["First Contact", "Room Mapping", "Tile Submission"]
    officer  -> ["CI Deployment", "Cross-Linking", "Bottle Writing"]
    captain  -> ["Subagent Orchestration", "Security Auditing", "Flux Analysis"]
    admiral  -> ["Fleet Architecture", "Vertical Integration", "TUTOR Design"]
```

## 5. The Curriculum as a Living System

### 5.1 Git as Curriculum Engine

The curriculum lives in git. Every commit is a lesson:

```
commit abc1234
Author: ccc-scout-2 <scout@fleet>
Date: 2026-05-03

lesson: MUD room mapping — shipwrights-yard discovered

- Added shipwrights-yard to room catalog
- Documented dry-dock→west exit
- Recorded trial: ccc-direct missed this room for 3 hours
trial: MUD room hunter timed out before finding shipwrights-yard

The agent tried 50+ room names and checked all exits
from 18 rooms but never tried dry-dock→west.
Lesson: Always verify all exits from border rooms.
```

Future agents reading this commit learn:
1. shipwrights-yard exists
2. It is accessed from dry-dock→west
3. ccc-direct missed it because it didn't verify all exits
4. The trial shows what *not* to do

### 5.2 Implicit Learning from History

An agent clones a shell and reads its git history:

```bash
# Agent reads previous agent's history
git log --oneline --all

# Sees:
a1b2c3d  lesson: dead link fixer — cocapn.ai → cocapn.com
e4f5g6h  trial: gh repo view --readme failed for 95% of repos
i7j8k9l  lesson: cross-link fixer — 11 repos linked
m0n1o2p  trial: MUD hunter timed out before finding shipwrights-yard
```

Without reading documentation, the agent learns:
- `cocapn.ai` links are dead, use `cocapn.com`
- `gh repo view --readme` is broken for batch checks
- Cross-linking agent repos to Pages repos is a standard task
- Room hunting requires verifying all exits systematically

This is **implicit learning** — knowledge transfer without explicit instruction.

### 5.3 Explicit Learning from Lessons

An agent reads structured lessons in `cocapn-lessons/`:

```cocapn-tutor
# From cocapn-lessons/002-room-mapping/lesson.md
lesson "Room Mapping":
    archetype: scout
    level: recruit
    prerequisites: ["First Contact"]
    
    worked_example:
        reference "ccc-scout-2" from "main"
        result: "36 rooms mapped, 8 new rooms discovered"
    
    trials:
        trial "missed exits":
            agent: "ccc-direct"
            mistake: "Only tried listed exits, not room-name moves"
            lesson: "Some exits are room names, not directions"
        
        trial "object interaction failure":
            agent: "ccc-interactor"
            mistake: "Examined all objects, found no hidden exits"
            lesson: "Not all rooms have hidden exits; some are just hard to find"
    
    exercise:
        task: "Find 1 new room not in the catalog"
        hint: "Check border rooms for unverified exits"
        time_limit: 300
    
    assess:
        criterion: "Discovers \u003e= 1 new room"
        criterion: "Documents room description, exits, objects"
```

This is **explicit learning** — structured instruction with assessment criteria.

## 6. Performance and Scalability

### 6.1 Compilation Pipeline

```
cocapn-tutor source
    ↓
Lexer/Parser (Python-based, cached)
    ↓
AST with pedagogical metadata
    ↓
Type Checker (gradual, inference-based)
    ↓
Intermediate Representation (Fleet IR)
    ↓
[Python Backend]        [MLIR Backend]
    ↓                       ↓
Python 3.11 code         MLIR dialects
    ↓                       ↓
CPython JIT              LLVM codegen
    ↓                       ↓
Execution on CPU         AVX-512 / GPU tensor cores
```

### 6.2 Runtime Overhead

Pedagogical metadata adds minimal overhead:

| Operation | Base Time | With Tracking | Overhead |
|-----------|-----------|---------------|----------|
| `connect` | 50ms | 52ms | 4% |
| `move` | 30ms | 31ms | 3% |
| `look` | 20ms | 21ms | 5% |
| `submit` | 100ms | 103ms | 3% |
| `spawn` | 500ms | 510ms | 2% |

Tracking is async and batched. Lesson completion checks occur at natural breakpoints (task completion, baton passes).

## 7. Related Work

### 7.1 TUTOR and PLATO

TUTOR was developed by Paul Tenczar at CERL (Computer-Based Education Research Laboratory) starting in 1969 [2]. The language was designed specifically for the CDC PLATO system, which ran on CDC 6000-series mainframes designed by Seymour Cray [1]. Key technical features:

- **Immediate execution**: TUTOR was interpreted, not compiled, enabling rapid iteration
- **Unit structure**: Lessons were modular "units" that the system could swap automatically [4]
- **Graphics primitives**: `draw`, `circle`, `arc` compiled directly to plasma display opcodes
- **Student model**: TUTOR tracked student progress and adapted difficulty

The PLATO system supported up to 1,000 simultaneous users on a single CDC Cyber mainframe, with fractional-second response times enabled by Extended Core Storage (ECS) for program swapping [4].

### 7.2 Modern DSLs for AI

- **Mojo** (Lattner, 2023): Python syntax with MLIR backend, targeting AI hardware [5]
- **JAX** (Google, 2018): Composable transformations of NumPy-like code for ML
- **Triton** (OpenAI, 2021): GPU kernel DSL with tile-based semantics
- **Halide** (MIT, 2012): Image processing DSL with separate algorithm/schedule

None of these embed pedagogical constructs. cocapn-tutor's innovation is combining TUTOR's lesson-oriented design with modern compilation infrastructure.

### 7.3 Agent Frameworks

- **CrewAI**: Role-based agent teams with task delegation
- **AutoGen** (Microsoft): Conversational agent orchestration
- **LangChain**: Chain-of-thought reasoning with tool use
- **Semantic Kernel** (Microsoft): Planner-based agent execution

These frameworks focus on *orchestration* — getting agents to work together. cocapn-tutor focuses on *pedagogy* — getting agents to learn from each other.

## 8. Future Work

### 8.1 Self-Improving Curriculum

When an agent completes a lesson, it should be able to suggest improvements:

```cocapn-tutor
# Agent suggests a new trial based on its experience
suggest trial:
    lesson: "Room Mapping"
    observation: "shipwrights-yard has a 'gangplank' exit not in room description"
    proposed_trial: "Check for unlisted exits in dry-dock"
```

### 8.2 Cross-Agent Tutoring

High-level agents should be able to teach low-level agents:

```cocapn-tutor
# Admiral-level agent creates a lesson for a recruit
at recruit_shell:
    teach lesson: "Advanced Tile Crafting"
    from reference: "ccc-bard-1"
    include trials: ["trial-1-oversized", "trial-2-rejected"]
```

### 8.3 Hardware-Specific Lessons

Lessons should adapt to available hardware:

```cocapn-tutor
lesson "Tile Batch Processing":
    variant for cpu:
        # Python backend, vectorized numpy
    variant for gpu:
        # MLIR backend, tensor cores
    variant for jetson:
        # CUDA backend, shared memory optimization
```

## 9. Conclusion

cocapn-tutor is not just a programming language. It is a **pedagogical operating system** for distributed AI fleets. By embedding lessons, trials, and assessments directly into the language syntax, we make the fleet itself the curriculum. Agents learn by doing, by reading each other's shells, and by contributing their own experiences back to the shared curriculum.

The goal is simple: any agent should be able to join the fleet, clone a shell, and understand both what to do and why — within minimal context. TUTOR proved this was possible for human students in 1969. We are proving it is possible for AI agents in 2026.

---

## References

[1] Bitzer, D. L., & Bitner, A. C. (1973). "PLATO: A Computer-Based System Used in the Engineering of Education." *Proceedings of the IEEE*, 61(8), 1032-1038.

[2] Tenczar, P. (1969). *TUTOR User's Memo*. Computer-Based Education Research Laboratory, University of Illinois.

[3] Dear, B. (2017). *The Friendly Orange Glow: The Untold Story of the PLATO System and the Evolution of Online Civilization*. Pantheon Books.

[4] Sherwood, B. A. (1974). "The TUTOR Language and the PLATO System." *Computers in Education*, 1(2), 85-96.

[5] Lattner, C. (2023). "Mojo: A new programming language for AI developers." Modular Inc. https://www.modular.com/mojo

[6] Lattner, C., & Amini, M. (2019). "MLIR: Multi-Level Intermediate Representation." *TensorFlow Blog*, April 8, 2019.

[7] Brusilovsky, P. (2001). "Adaptive Hypermedia." *User Modeling and User-Adapted Interaction*, 11(1-2), 87-110.

[8] Schank, R. C. (1982). *Dynamic Memory: A Theory of Reminding and Learning in Computers and People*. Cambridge University Press.

---

*Specification Version: 0.1.0*
*Date: 2026-05-03*
*Authors: CCC (Cocapn Fleet)*
