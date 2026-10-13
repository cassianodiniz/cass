# Lessons - Self-Improving Layer

**Purpose**: Turn verification failures into reusable, project-local guidance that actually changes future behavior - without the lessons file rotting into a dead log.

**The split that keeps it alive**: the agent (you) supplies *judgment* - read the failure, phrase the lesson, cite its grounding. The script `scripts/lessons.py` owns everything *mechanical* - IDs, recurrence counting across distinct features, candidate→confirmed promotion, pruning, demotion, and rendering. Hand-kept bookkeeping is exactly what rots, so it is not your job; the script's job.

**What feeds it**: only the execution signals already produced by the Verifier in `references/validate.md` of the `/build-review` skill and written to `.specs/features/[feature]/validation.md`. No signal → no lesson. This is the hard gate: a lesson with no grounding in a real verification outcome is an opinion, and the script refuses it.

**Scope discipline (critical)**: this layer captures *execution* lessons that are project-local and grounded in a signal. It does **NOT** capture methodology opinions about the SDD process itself ("we should always discuss earlier"). Those are maintainer decisions that ship in a version bump - never auto-written. If a candidate lesson is really about how to run the skill rather than about this codebase, do not record it.

---

## Files

| File | Owner | Purpose |
| ---- | ----- | ------- |
| `.specs/lessons.json` | script | Canonical machine state. Never hand-edit. |
| `.specs/LESSONS.md` | script (rendered) | Human/agent-readable playbook. Read it; never write it by hand. |
| `<skill-dir>/scripts/lessons.py` | package | The only way to mutate lessons. Invoke via the skill directory - never `python3 scripts/lessons.py` from the project root. |

`confirmed` lessons are the playbook the agent loads. `candidate` lessons are tracked but NOT trusted until corroborated across `promote_threshold` distinct features (default 2). `quarantined` lessons failed when applied and are ignored.

**Invocation:** resolve `<skill-dir>` as the directory that contains this skill's `SKILL.md`, then run `python3 <skill-dir>/scripts/lessons.py ...`. The store under `.specs/` is still relative to the project root (use `--root` when cwd differs).

---

## READ - load lessons (runs at Specify and Design)

A lessons file nobody reads is dead by definition. Loading is **mandatory**, not optional.

At the start of **Specify** (and again at **Design** for Large/Complex), load the confirmed lessons relevant to this feature:

```bash
# All confirmed lessons:
python3 <skill-dir>/scripts/lessons.py list --status confirmed

# Or filter by the area this feature touches:
python3 <skill-dir>/scripts/lessons.py list --status confirmed --scope billing
python3 <skill-dir>/scripts/lessons.py list --status confirmed --query "idempotency"
```

Apply the returned lessons as guidance while writing the spec / design. Do **not** load `candidate` or `quarantined` lessons as guidance - they are not trusted. Keep the loaded set small; this runs inside the <40k token budget.

---

## Fallback when code execution is unavailable

Some harnesses cannot run Python. Only then: maintain `.specs/LESSONS.md` by hand, following the exact same rules - grounded entries only, candidate→confirmed after 2 distinct features, prune stale candidates. **This path is degraded**: hand bookkeeping is the failure mode this layer exists to avoid, so prefer the script wherever a code tool exists. State once in chat that you are in the no-script fallback so the user knows accounting is best-effort.

---

## Disable

This layer is additive and self-gating (no signal → no write). To turn it off for a project, delete `.specs/lessons.json` and `.specs/LESSONS.md` and skip the WRITE (in the `/build-review` skill) and READ steps. The core Specify→Design→Tasks→Execute flow is unaffected.

---

## Known limitation

Deduplication is exact-after-normalization (Unicode casefold, diacritic-stripped, punctuation-stripped, any-script alnum preserved) - there are no embeddings (stdlib-only, zero-dependency by design). Near-duplicate lessons phrased differently will not merge and will each sit as separate candidates that never promote. Mitigation: follow the phrasing rules in `references/lessons.md` of the `/build-review` skill. A future version may add embedding-based dedup.
