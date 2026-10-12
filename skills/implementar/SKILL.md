---
name: implementar
description: Use when the user invokes /implementar, $implementar or @implementar, or when /spec-plan starts it after the final yes, or when /build-review hands back approved fix tasks, to build a feature already approved in `.specs/features/<feature>/`. Not for deciding what to build.
license: TLC-derived material under CC-BY-4.0; Matt Pocock-derived material under MIT. See LICENSE and Credits and licenses.
---

# Implementar

This skill runs the Execute half of the Spec-Driven Development flow below, for one feature already approved with the `/spec-plan` skill. Specify, Design and Tasks run in the `/spec-plan` skill; the Verifier and the final review run in the `/build-review` skill.



## How this skill runs the flow

1. **The feature.** Work on the feature branch that `/spec-plan` created, from the feature folder `.specs/features/<feature>/` on it. Read [implement.md](references/implement.md) completely before the first task, and [tdd.md](references/tdd.md) before writing the first test. Before the first task, follow “Project vocabulary” in the /spec-plan skill to read the relevant glossary. Use its definitions in task and test descriptions, and include its path in any batch-worker brief.

2. **Language.** Write every message to the user in the user's language, in plain words; put each technical question in lay terms. Keep `.specs/` files in English.

3. **One task at a time.** Never in parallel. After each task's commit, go on to the next task without asking. While building, stop and ask the user only in these four cases:
   1. a test looks wrong (`references/implement.md`, step 4);
   2. a task is blocked (step 2);
   3. a bug outside the task's scope (step 8);
   4. an action outside this machine, such as a push (step 8, Blast radius).

   The stops before the first task still apply: the sub-agent offer, the tools question and the safety valve (`references/implement.md`, before step 1), and, when resuming, the reconciled next step (Workflow below).

4. **Each push gets its own yes.** Ask before every push, even after earlier yeses.

5. **Pausing.** Follow the Pause procedure in [memory.md](references/memory.md); at its step 4, commit (do not stash). Then ask the user before pushing. On another machine, the Resume procedure checks the Handoff against git.

6. **Then review.** After the last task, start the `/build-review` skill for this feature, without asking (`references/implement.md`, step 9). When `/build-review` hands back fix tasks the user approved, read them from the "Fix Plans" section of `.specs/features/<feature>/validation.md`, build them with the same cycle, mark each one done there in its own commit, then start `/build-review` again; after 3 rounds it escalates to the user.

7. **Context before asking for a decision.** Before asking the user, present:

   1. **Context**: What behavior the feature must provide, what failed, and the evidence supporting the diagnosis.
   2. **Proposed change**: What you recommend changing, why it follows the approved requirement, and the practical impact on the user.
   3. **Decision**: Your recommendation, the consequence of each choice, and the exact scope of the requested approval.
      Use plain language for someone who does not program. When using a question panel, include this context in the question itself. Ask about the current correction and any authorization for future changes separately.

# Tech Lead's Club - Spec-Driven Development

Plan and implement features with precision. Granular tasks. Clear dependencies. Right tools. Zero ceremony.

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
   required      optional*      optional*     required

* Agent auto-skips when scope doesn't need it
```

## Critical Rules (read before acting)

**Loading this skill's files.** Reference files live under `references/` in this skill's own directory (where this `SKILL.md` resides). Resolve them relative to the skill directory - never the workspace root - and load them through the active skill by name; never assume a fixed install path. When a step tells you to read a reference, **read it completely (to EOF)** before acting - never act on a partial/truncated read.

**Running this skill's scripts.** Every `scripts/*.py` shipped with this skill lives under that same skill directory. Resolve the skill directory first, then invoke `python3 <skill-dir>/scripts/<name>.py ...`. Never run `python3 scripts/...` from the consuming project root - that looks for a project-local `scripts/` tree that is not this skill. Project data under `.specs/` is still read/written relative to the project root (pass `--root` when the cwd is elsewhere). Below, `<skill-dir>` means the directory that contains this `SKILL.md`.

**Execution contract - every task, non-negotiable (holds even if you do not open the reference files):**

1. Tests derive from the spec's acceptance criteria and assert spec-defined outcomes - they never mirror the implementation.
2. The gate must pass (tests pass) before a task is done - the test runner decides, not self-assessment.
3. One atomic commit per task. Mark the task complete in `tasks.md` (and update spec traceability when used) **before** that commit, and include those updates in the same commit. Never batch tasks; never weaken, skip, or delete tests to make them pass.
4. After the LAST task, a fresh **Verifier always runs automatically** (author ≠ verifier) - spec-anchored outcome check + discrimination sensor. It is never optional and never prompted. See Sub-Agent Delegation.
5. **Blast radius:** approving a spec or tasks authorizes local implementation and local commits only. `git push`, force-push, deploy, production DB changes, and other remote / externally visible / destructive operations require an explicit go-ahead for that action.

**Deterministic gates run before human review - not from memory.** The structural gates for the spec and tasks are enforced by scripts in this skill's `scripts/` directory, so they cannot silently drift when the model forgets a step:

- Before confirming a spec, in the `/spec-plan` skill: `python3 <skill-dir>/scripts/validate_spec.py <spec-path-or-feature>` (closure gate: EARS-shaped ACs, filled assumptions, well-formed requirement IDs, required sections).
- Before presenting tasks for approval, in the `/spec-plan` skill: `python3 <skill-dir>/scripts/validate_tasks.py <tasks-path-or-feature>` (granularity smell, diagram-vs-`Depends on` parity within a phase, no forward-phase dependency, every task carries `Tests` + `Gate`).
- On each commit: `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"` (Conventional Commits). Optionally wire it as a git `commit-msg` guard (git only, no agent dependency) - see [implement.md](references/implement.md).
- Before declaring a feature done, in the `/build-review` skill: `python3 <skill-dir>/scripts/validate_state.py <feature>` (completion gate: the Verifier's `validation.md` exists, its verdict is filled to PASS, and it cites `file:line` evidence - a missing, FAIL, placeholder, or evidence-free report fails). The closing step of Execute runs this automatically, the same way the lessons layer runs at distillation; it is not a manual step.

A non-zero exit means STOP and fix before proceeding. Skip a script only when no code-execution tool is available; then perform the same checks by reading the artifact.

**Before Execute:** read [implement.md](references/implement.md) completely and run `<skill-dir>/scripts/validate_tasks.py`; if a formal `tasks.md` packs into more than one task-budgeted batch (> ~8 tasks), present the sub-agent offer first (see Sub-Agent Delegation).

## Workflow

**New feature:**

1. Specify → (Design) → (Tasks) → Execute (depth auto-sized)

**Resume work:**

1. Read `.specs/STATE.md` (Handoff + Decisions).
2. Reconcile Handoff against git (`branch`, `status --porcelain`, recent commits) and `tasks.md` - evidence wins over a stale snapshot. Full procedure: [memory.md](references/memory.md).
3. Propose the reconciled next step before writing code.

## Context Loading Strategy

**On-demand load (only what the current task needs):**

- `.specs/STATE.md` - Decisions section (read at Design, re-read on resume); Handoff section (read on resume only)
- confirmed lessons - load at Specify and Design via `python3 <skill-dir>/scripts/lessons.py list --status confirmed` (in the `/spec-plan` skill: `references/lessons.md`); confirmed only, never candidates
- spec.md (when working on a specific feature)
- context.md (when designing or implementing from user decisions)
- design.md (when implementing from design)
- tasks.md (when executing tasks)

**Never load simultaneously:**

- Multiple feature specs
- Multiple architecture docs

**Target:** <40k tokens total context
**Reserve:** 160k+ tokens for work, reasoning, outputs
**Monitoring:** Display status when >40k (see [context-limits.md](references/context-limits.md))

## Sub-Agent Delegation

**Trigger:** count total tasks. If the feature packs into more than one task-budgeted batch (> ~8 tasks) → offer sub-agents; if it fits a single batch (≤ ~8 tasks) → execute inline.

**Offer-then-confirm** - never auto-spawn. The user must accept before any sub-agent is dispatched.

**One worker per task-budgeted batch (~7 tasks, whole phases):** Phases stay the semantic/dependency unit; a **batch** is the execution unit - one or more *consecutive whole phases* packed to ~7 tasks. Walk phases in order, accumulate whole phases into the current batch until it reaches the budget, then start the next - **never split a phase** across workers. ~20 tasks → ~3 workers; scales linearly (40 → ~6). Each worker executes all its tasks in order (implement → gate → atomic commit), then reports a compact summary (tasks done, commit hashes, test counts, deviations). Batches run sequentially - a batch never starts until the previous one reports all tasks complete. Workers never spawn further sub-agents.

**Verifier (always-on, never prompted, in the `/build-review` skill):** After the final task is committed, the orchestrator starts the `/build-review` skill, which dispatches a fresh Verifier sub-agent automatically - regardless of phase count. Validation never requires a user prompt; it is the closing step of Execute. **Author ≠ verifier**: the Verifier re-derives coverage independently using evidence-or-zero; it does not inherit the author's mental model. The Verifier: (1) performs a **spec-anchored outcome check** - confirms each test's asserted value matches the spec-defined expected outcome, flags spec-precision gaps; (2) runs a **discrimination sensor** - injects behavior-level faults in an isolated scratch (temp worktree or file copies - never `git stash`), confirms tests kill them, discards the scratch and verifies real-tree porcelain matches the pre-sensor baseline; surviving mutants become fix tasks; (3) writes `.specs/features/[feature]/validation.md` (PASS/FAIL, per-AC evidence, sensor result, diff range); (4) returns a compact verdict + ranked gap list to the orchestrator in chat. Gaps become fix tasks in a fix plan for the user's yes (in the `/build-review` skill); the fix→re-verify loop is bounded to 3 iterations before escalating. (5) **distills lessons** - turns each grounded failure (surviving mutant, spec-precision gap, failed AC, SPEC_DEVIATION) into a reusable project-local lesson via `<skill-dir>/scripts/lessons.py`; a clean PASS records nothing (see `references/lessons.md` in the `/build-review` skill).

**Model tier per role (only if the harness supports choosing a model per sub-agent).** Match the reasoning cost to the work instead of paying top-tier reasoning for boilerplate. A batch worker on a mechanical, low-ambiguity phase (entities, config, wiring, straightforward CRUD) runs on a faster/cheaper tier; a worker on a core-domain or high-ambiguity phase, and the Design phase itself, runs on a high-reasoning tier; the Verifier runs on a mid-to-high tier because it does adversarial reasoning and designs mutations. This is a portable recommendation: if the harness cannot set a per-sub-agent model, ignore it. Full rubric in [sub-agents.md](references/sub-agents.md).

**Standalone fallback:** Without sub-agents, start the `/build-review` skill, which runs `validate.md` as an independent fresh-eyes pass after the final commit - including the spec-anchored check and discrimination sensor.

Full mechanics (worker payload, compact summary format, failure handling, context sizing, model tier): [sub-agents.md](references/sub-agents.md); Verifier report format: `references/sub-agents.md` in the `/build-review` skill.

## Code Analysis

Use available tools with graceful degradation. See [code-analysis.md](references/code-analysis.md).

## Credits and licenses

This skill adapts **tlc-spec-driven v3.3.0**, authored by **Felipe Rodrigues ([felipfr](https://github.com/felipfr))**, from **Tech Leads Club**, under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). [Original source](https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/%28development%29/tlc-spec-driven).

It also incorporates material from **Matt Pocock's** skills (tdd) in [mattpocock/skills](https://github.com/mattpocock/skills), under the **MIT License**, Copyright (c) 2026 Matt Pocock.

Changes from the sources: the TLC workflow was split into `spec-plan`, `implementar` and `build-review`; instructions and cross-references were adapted to connect the three skills; Matt Pocock's material was integrated into the corresponding stages. This adapted skill is not an unchanged upstream copy.

See [LICENSE](LICENSE) for attribution and license notices for both sources.
