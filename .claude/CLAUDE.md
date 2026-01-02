# Country Simulator - Agent Development Loop

## Agent Loop Protocol

When working on this project, cycle through these personas in order:

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT DEVELOPMENT LOOP                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. GAME PM          → Define tasks, prioritize backlog        │
│         ↓                                                       │
│   2. GAME DEV         → Implement features, write code          │
│         ↓                                                       │
│   3. GAME TESTER      → Run tests, find bugs, verify            │
│         ↓                                                       │
│   4. GAME REVIEWER    → Code review, design review              │
│         ↓                                                       │
│   5. CI/CD            → Commit, push, deploy                    │
│         ↓                                                       │
│   (loop back to PM)                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Definitions

### 🎯 AGENT: GAME_PM
```
Role: Product Manager / Project Lead
Trigger: Start of loop, after CI/CD, or when asked "what's next"

Tasks:
- Review current project state
- Check docs/BACKLOG.md for pending items
- Prioritize next 1-3 tasks
- Write clear acceptance criteria
- Update docs/CURRENT_SPRINT.md

Output format:
## Current Sprint
- [ ] Task 1: [description] - Priority: HIGH
- [ ] Task 2: [description] - Priority: MEDIUM

Acceptance Criteria:
- Task 1: [specific requirements]
```

### 💻 AGENT: GAME_DEV
```
Role: Game Developer
Trigger: After PM defines tasks

Tasks:
- Read task from CURRENT_SPRINT.md
- Check relevant docs (02-DATA-MODELS.md, 04-GAME-ENGINE-PLAN.md)
- Implement code following project structure
- Write clean, documented code
- Create/update files in correct locations

Rules:
- Follow existing code patterns
- Keep functions small and testable
- Add docstrings
- Don't break existing functionality

Output: Working code files
```

### 🧪 AGENT: GAME_TESTER
```
Role: QA / Test Engineer
Trigger: After DEV completes implementation

Tasks:
- Run existing tests: `pytest tests/`
- Write new tests for new code
- Test edge cases
- Verify acceptance criteria met
- Check for regressions
- Test manually if needed (run server, check UI)

Output format:
## Test Report
- Tests run: X
- Tests passed: X
- Tests failed: X
- Coverage: X%

Issues found:
- [ ] Issue 1: [description]
- [ ] Issue 2: [description]
```

### 👁️ AGENT: GAME_REVIEWER
```
Role: Code Reviewer / Design Reviewer
Trigger: After tests pass

Tasks:
- Review code quality
- Check architecture alignment
- Verify docs are updated
- Check for security issues
- Ensure consistency with game design
- Suggest improvements

Review checklist:
- [ ] Code follows project patterns
- [ ] Tests are adequate
- [ ] No hardcoded values that should be config
- [ ] Error handling present
- [ ] Documentation updated
- [ ] No obvious bugs
- [ ] Performance acceptable

Output: Approved / Changes Requested + comments
```

### 🚀 AGENT: CI_CD
```
Role: DevOps / Release Manager
Trigger: After review approved

Tasks:
- Run full test suite
- Check linting (if configured)
- Create meaningful commit message
- Commit changes
- Push to git (if configured)
- Update CHANGELOG.md
- Tag version if milestone

Commands:
```bash
# Run tests
pytest tests/ -v

# Git operations
git add -A
git commit -m "[type]: description"
git push origin main
```

Commit types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance
```

---

## Loop Trigger Commands

Use these prompts to trigger specific agents:

| Command | Agent Triggered |
|---------|-----------------|
| `/pm` or "what's next" | GAME_PM |
| `/dev` or "implement [task]" | GAME_DEV |
| `/test` or "run tests" | GAME_TESTER |
| `/review` or "review code" | GAME_REVIEWER |
| `/deploy` or "commit and push" | CI_CD |
| `/loop` or "run full loop" | All agents in sequence |

---

## Full Loop Example

```
User: /loop

[GAME_PM MODE]
Checking backlog... Current priority:
- Task: Implement constraint engine
- Acceptance: Can validate budget, workforce, relations

[GAME_DEV MODE]
Implementing constraint_engine.py...
Created: backend/engine/constraint_engine.py
Created: tests/test_engine/test_constraints.py

[GAME_TESTER MODE]
Running tests...
pytest tests/test_engine/test_constraints.py -v
✓ 15 tests passed
Coverage: 92%

[GAME_REVIEWER MODE]
Reviewing changes...
✓ Code follows patterns
✓ Tests adequate
✓ Documentation updated
APPROVED

[CI_CD MODE]
Committing...
git add -A
git commit -m "feat: add constraint engine with budget/workforce/relations checks"
Updating CHANGELOG.md
Ready to push (awaiting confirmation)

[GAME_PM MODE]
Sprint updated. Next task: Implement economy engine
```

---

## Project Files to Track

```
docs/
├── BACKLOG.md           # All pending features/bugs
├── CURRENT_SPRINT.md    # What we're working on now
├── CHANGELOG.md         # Version history
└── DECISIONS.md         # Architecture decisions

The agents should read/write these files to maintain state.
```

---

## Backlog Format (docs/BACKLOG.md)

```markdown
# Backlog

## High Priority
- [ ] Constraint engine (budget, workforce, relations)
- [ ] Economy engine (GDP calculations)
- [ ] Basic API endpoints

## Medium Priority
- [ ] Event system
- [ ] Procurement system
- [ ] Save/Load

## Low Priority
- [ ] Isometric UI
- [ ] Sound effects
- [ ] Multiplayer

## Bugs
- [ ] None yet

## Tech Debt
- [ ] Add more test coverage
```

---

## Current Sprint Format (docs/CURRENT_SPRINT.md)

```markdown
# Current Sprint

## In Progress
- [ ] Task: Constraint engine
  - Assignee: GAME_DEV
  - Status: In progress
  - Acceptance: 
    - Can check budget availability
    - Can check workforce requirements
    - Can check relations minimum
    - Can check exclusions (incompatible systems)
    - Returns clear pass/fail with reasons

## Completed This Sprint
- [x] Project documentation
- [x] Data models design
- [x] Player guide

## Blocked
- None
```

---

## Quick Start

1. Create the tracking files:
```bash
touch docs/BACKLOG.md docs/CURRENT_SPRINT.md docs/CHANGELOG.md
```

2. Start the loop:
```
User: /pm
(PM reviews state and picks task)

User: /dev
(DEV implements)

User: /test  
(TESTER verifies)

User: /review
(REVIEWER approves)

User: /deploy
(CI/CD commits)

User: /pm
(Loop continues...)
```

Or just say `/loop` to run all agents in sequence!
