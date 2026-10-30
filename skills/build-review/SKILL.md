---
name: build-review
description: Use when /implementar starts it after the last task of a feature, or when the user invokes /build-review, $build-review or @build-review, to review a finished feature of `.specs/features/<feature>/` before it goes live. Not for building nor for planning.
license: TLC-derived material under CC-BY-4.0; Matt Pocock-derived material under MIT. See LICENSE and Credits and licenses.
---

# Build Review

This skill runs the feature-level validation of the Spec-Driven Development flow, once, at the end of the feature, for a feature built with the `/implementar` skill. Specify, Design and Tasks run in the `/spec-plan` skill; Execute runs in the `/implementar` skill. Never fix code here.

## How this skill runs the review

1. **When.** It starts on its own after the last task of the feature, and again after each fix round. It reviews the whole feature from where the feature branch left main.Follow “Project vocabulary” in the /spec-plan skill to locate the relevant glossary. Require the Verifier and Spec reviewer to read it and report behavior that conflicts with its approved definitions.
2. **Language.** Write every message to the user in the user's language, in plain words; put each technical question in lay terms. Keep `.specs/` files in English.
3. **Tests and reviewers.** The Verifier, a fresh sub-agent (author ≠ verifier), runs [validate.md](references/validate.md) steps 1 to 6, then 6b, 9 and 10: it writes `validation.md` (`validate_state.py` waits for item 6), distills the lessons and returns its report. Once all tasks are complete, run [code-review.md](references/code-review.md) on the feature branch. The verdict is the Verifier's; the Standards and Spec reports stay separate and only report.
4. **Screen photos.** For a feature with a screen, the Verifier runs step 6b of `validate.md` only after the tests pass, never at the same time. If the tests fail, say the photos come in the next round. The photos come back with the Verifier's report, and the orchestrator shows them to the user with the review result, every time, even when the guided test does not run.
   - Log in with the project's own test account, from its example or seed files. If there is none, ask the user once and record it in the project.
   - If the app does not open, the result is "Não deu para revisar as telas", with the reason, and the PR is not marked ready until the user decides.
5. **Guided test with the user.** Then run step 7 of `validate.md` (Interactive UAT) when it applies, with the photos.
6. **Final verdict.** Add the photo and guided-test results to `validation.md`. If either found an issue, change the `**Verdict**:` line to FAIL (the gate reads only that line; also update `**Overall**`). Only then run `python3 <skill-dir>/scripts/validate_state.py <feature>` (`validate.md`, step 9).
7. **One fix plan.** Every issue from the Verifier, the photos, the guided test and the Standards and Spec reports goes into one fix plan, in the "Fix Plans" section of `validation.md` with the round number (`validate.md`, step 8). Each item names where it came from (Verifier, photos, guided test, Standards or Spec), and items are not reranked across those sources. The user approves it item by item, even when the Verifier's verdict is PASS. An item the user refuses is recorded there with the user's words and no longer counts toward FAIL. With the yes, hand the approved fix tasks to the `/implementar` skill; it builds them from that section, marks each one done there, and starts this skill again. After 3 rounds with gaps left, stop and ask the user.
8. **Could not review.** When the review stops before the reviewers run, the verdict is neither PASS nor FAIL: it is "Não deu para revisar", with what was missing and how to get it.
9. **On PASS, with no approved fix task left.** The draft PR already exists: mark it ready for review only with the user's yes. Ask one question: commit `validation.md` and the lessons files, push, and mark the PR ready. That yes covers the three actions.

## Critical Rules (read before acting)

**Loading this skill's files.** Reference files live under `references/` in this skill's own directory (where this `SKILL.md` resides). Resolve them relative to the skill directory - never the workspace root - and load them through the active skill by name; never assume a fixed install path. When a step tells you to read a reference, **read it completely (to EOF)** before acting - never act on a partial/truncated read.

**Running this skill's scripts.** Every `scripts/*.py` shipped with this skill lives under that same skill directory. Resolve the skill directory first, then invoke `python3 <skill-dir>/scripts/<name>.py ...`. Never run `python3 scripts/...` from the consuming project root - that looks for a project-local `scripts/` tree that is not this skill. Project data under `.specs/` is still read/written relative to the project root (pass `--root` when the cwd is elsewhere). Below, `<skill-dir>` means the directory that contains this `SKILL.md`.

**Execution contract - every task, non-negotiable (holds even if you do not open the reference files):**

1. Tests derive from the spec's acceptance criteria and assert spec-defined outcomes - they never mirror the implementation.
2. The gate must pass (tests pass) before a task is done - the test runner decides, not self-assessment.
3. One atomic commit per task. Mark the task complete in `tasks.md` (and update spec traceability when used) **before** that commit, and include those updates in the same commit. Never batch tasks; never weaken, skip, or delete tests to make them pass.
4. After the LAST task, a fresh **Verifier always runs automatically** (author ≠ verifier) - spec-anchored outcome check + discrimination sensor. It is never optional and never prompted. See the Verifier Sub-Agent in [sub-agents.md](references/sub-agents.md).
5. **Blast radius:** approving a spec or tasks authorizes local implementation and local commits only. `git push`, force-push, deploy, production DB changes, and other remote / externally visible / destructive operations require an explicit go-ahead for that action.

**Deterministic gates run before human review - not from memory.** The structural gates for the spec and tasks are enforced by scripts in this skill's `scripts/` directory, so they cannot silently drift when the model forgets a step:

- Before confirming a spec, in the `/spec-plan` skill: `python3 <skill-dir>/scripts/validate_spec.py <spec-path-or-feature>` (closure gate: EARS-shaped ACs, filled assumptions, well-formed requirement IDs, required sections).
- Before presenting tasks for approval, in the `/spec-plan` skill: `python3 <skill-dir>/scripts/validate_tasks.py <tasks-path-or-feature>` (granularity smell, diagram-vs-`Depends on` parity within a phase, no forward-phase dependency, every task carries `Tests` + `Gate`).
- On each commit: `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"` (Conventional Commits). Optionally wire it as a git `commit-msg` guard (git only, no agent dependency) - see `references/implement.md` in the `/implementar` skill, which ships `check_commit.py`.
- Before declaring a feature done: `python3 <skill-dir>/scripts/validate_state.py <feature>` (completion gate: the Verifier's `validation.md` exists, its verdict is filled to PASS, and it cites `file:line` evidence - a missing, FAIL, placeholder, or evidence-free report fails). The closing step of Execute runs this automatically, the same way the lessons layer runs at distillation; it is not a manual step.

A non-zero exit means STOP and fix before proceeding. Skip a script only when no code-execution tool is available; then perform the same checks by reading the artifact.

**Before Execute** (the `/implementar` skill does this step, not this skill): read `references/implement.md` of the `/implementar` skill completely and run `<skill-dir>/scripts/validate_tasks.py`; if a formal `tasks.md` packs into more than one task-budgeted batch (> ~8 tasks), present the sub-agent offer first (see Sub-Agent Delegation in the `/implementar` skill).

## Credits and licenses

This skill adapts **tlc-spec-driven v3.3.0**, authored by **Felipe Rodrigues ([felipfr](https://github.com/felipfr))**, from **Tech Leads Club**, under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). [Original source](https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/%28development%29/tlc-spec-driven).

It also incorporates material from **Matt Pocock's** skills (code-review and implement-spec) in [mattpocock/skills](https://github.com/mattpocock/skills), under the **MIT License**, Copyright (c) 2026 Matt Pocock.

Changes from the sources: the TLC workflow was split into `spec-plan`, `implementar` and `build-review`; instructions and cross-references were adapted to connect the three skills; Matt Pocock's material was integrated into the corresponding stages. This adapted skill is not an unchanged upstream copy.

See [LICENSE](LICENSE) for attribution and license notices for both sources.
