## Local feature routing

This copy is shared by the local entry points. Before choosing a phase, read only [Feature contract](../SKILL.md#feature-contract). Reading that section does not start Plan. Do not reuse approval for a different plan. Enter verification through [Build Review](../../build-review/SKILL.md), which preserves the existing local reviewers, photos, UAT and correction/release decisions around the shared Verify round. On return from review, including a resumed Build, apply that entry's [local safeguards](../../implementar/references/local-review.md) before correcting any review finding: the user approves or refuses each item first. This local rule governs review corrections even where the shared Build/Verify text says to fix findings within the approved scope.

# Shared core

Freeze the obligations. Free the plan. Prove it with someone who did not build it. Derived from tlc-spec-driven 3.3.0 (Felipe Rodrigues), tlc-plan, and tlc-implement.

```
┌──────┐   ┌────────┐   ┌────────┐   ┌───────┐   ┌───────┐   ┌────────┐
│ PLAN │ → │ DESIGN │ → │ CHECKS │ → │ TASKS │ → │ BUILD │ → │ VERIFY │
└──────┘   └────────┘   └────────┘   └───────┘   └───────┘   └────────┘
 yes 1      how          obligations  yes 2       one task    always
```

The common failure of a coding agent is a requirement that never became an active obligation, followed by a completion claim. What works against it is a small, frozen, external obligation set and a verifier that is not the author, so the budget goes there and not into choreographing the model. A human confirms what must be true and how it is being built in one document; only then does it become obligations with proofs. What is hard to reverse gets a one-way door with its literal shape in the plan. After the plan's yes, design.md names the components and tasks.md breaks the work into tasks; the user approves the tasks before code.

## Rules

These hold even if no reference file is read. Each one lives here; the references point back.

1. Every check is one observable claim with a concrete value plus the proof that settles it: a test or command whose exit code decides, or, for a state a capture draws, the Verifier's photo of it compared with the capture (rule 9).
2. Tests assert what the checks say, not what the code happens to do. Do not write a test by reading the implementation. Where the approved proof is a test, work one criterion at a time: write its test, run it and see it fail, implement it and see it pass, then move to the next criterion. The red result must show the intended missing behavior before production changes; an import or environment error does not.
3. A test changes only with the claim it proves, and leaves with the code it proves, in the same commit. Changing a test to make a suite pass hides the failure it exists to show: a wrong check is a stop-and-ask.
4. Checks are fixed once `validate_checks.py` passes; a check may be appended when the walk or the Verifier finds a missing obligation. In the plan, `Landing`, `Surface` and the stored shape are additive; the path and `Changes underneath` are kept true in the commit that changes them.
5. The Verifier is a fresh sub-agent, never the author, and it always runs at feature completion and again after each fix that changes code. There are at most three code fix-to-review iterations after the initial review; remaining failures go to the user ([verify.md](../../implementar/references/verify.md)). `check_proofs.py` settles the mechanical part - every proof run and passing at `HEAD`, the build, the walk - and the Verifier spends its time on judgement: it runs the complete battery, traces every criterion to `file:line` + assertion, opens the test each check's proof selects and says whether that test would fail if the claim were false, tries examples nobody named, runs the discrimination sensor, and takes and judges the screen photos. The work is done when every finding is closed by a commit or explicitly refused in the user's actual words, and `proofs.md` is green at `HEAD`.
6. A proof is the project's own test command; the skill knows no test runner. Tests that run together go on one `Run <name>: <command>` line, run once, and each check that reads it writes `Proof: run <name> | <the line the run prints when its test passes>`, pass marker included, so a filter that selects nothing reads `no test ran` instead of a green exit code. Name the full test identity, not words from it; reporter timing/progress metadata is ignored. A command run alone is judged by its exit code. The checks are the floor; an edge case or guard no check names is still the work.
7. The completion gate is a script: `validate_verification.py` exits 0. The final report opens with its last line; a red gate is said first, never left for the reader to find.
8. An approved spec authorizes local edits and local commits. `git push`, deploy and production data changes need an explicit go-ahead for that action.
9. **A state a capture draws is one photo, taken and judged by the Verifier.** The Verifier reaches that state and photographs it from a browser window at the capture's size - its pixel size over its scale: a wider window lays the page out differently, and resizing the image afterwards hides it ([verify.md](../../implementar/references/verify.md), step 6b). It matches the capture except for what `## Differences from the source` lists; each difference is a finding. A state no capture draws, and an existing screen the feature does not change, are proven by a test or a `walk` proof.
10. The prototype's photos, approved with the plan, are the binding source; a capture, frame or live site that comes with the request is a reference the prototype follows ([prototype.md](prototype.md)). A binding source is changed only by the user. Removing, renaming or departing from something it draws is asked, recorded as a decision in `.specs/STATE.md`, and listed in the plan's `## Differences from the source` with `Confirmed: y - AD-NNN`.
11. **The files hold the run; the chat does not survive a compaction.** The user's approval is written as `**Approved**: <date> - user: "<their words>"` in plan.md, or in checks.md when there is no plan, and in tasks.md when it exists - never one the user did not give. Before code, confirm the actual authorization is recorded; an authorization already given is not asked again. Each answer goes into its file in the turn it arrives. Each sub-agent goes on the `**Dispatched:**` line of `checks.md` `## Handoff` before it is sent. After a compaction or in a new session, re-read this file and the current phase's reference, then resume from the files ([memory.md](memory.md)).
12. **A finding is a fact its reviewer reproduced.** Each finding carries the steps that show it, the source it contradicts and the reviewer's own proof. An item without a source is a question for the user, not a finding: it stays open and blocks done until the user answers. Why: the executor fixes what the finding says, so a finding without proof becomes a wrong change. How to write it: [verify.md](../../implementar/references/verify.md), step "Create fix item".

## Who checks what

| Part | Runs | Cannot catch |
| --- | --- | --- |
| `check_proofs.py` (always) | every `Run` group and lone proof once at `HEAD`, one at a time, each check's line found in its run's output, the build and walk checked | a test that passes for the wrong reason |
| The Verifier (always) | the complete battery and test count, each criterion traced to `file:line` + assertion, each check's test read against its criterion, edge cases and two examples nobody named, the discrimination sensor, code quality, photos at 375/768/1280 and at each capture's size ([verify.md](../../implementar/references/verify.md)) | a wrong rule whose test reads as right |

## Artifacts

```
.specs/
├── STATE.md                    # Decisions log (AD-NNN)
├── LESSONS.md                  # rendered by scripts/lessons.py - do not hand-edit
├── lessons.json                # machine-owned
└── features/<feature>/
    ├── plan.md                 # problem, shape, surface, doors, criteria
    ├── design.md               # architecture, components, reuse, error handling, risks
    ├── checks.md               # claims + proofs, the coverage join, swept, handoff
    ├── tasks.md                # atomic tasks, phases, the test coverage matrix
    ├── prototype/              # <screen>.html and its stylesheet, approved with the plan
    ├── references/             # what the user sent: captures, frames, prints - they do not bind
    ├── captures/               # the prototype's photos (binding), <capture>.running.png pictures, and the Verifier's review-*.png photos
    ├── screens.md              # the Verifier's inventory and verdict, per picture
    ├── proofs.md               # written by check_proofs.py: every proof at HEAD, and each run's output
    └── verification.md         # the Verifier's judgement of each check, and its findings closed by commits
```

For a change under roughly three files, with no one-way door and no prototype ([prototype.md](prototype.md)), write only `checks.md` with an `## Intent` paragraph and skip `plan.md`. Record the user's actual authorization there before code; if none was given, present the checks and stop for approval.

## Phases

| Phase | What it produces | Reference |
| --- | --- | --- |
| Plan | problem, shape, surface, doors, criteria; the first stop for a human | [plan.md](plan.md) |
| Design | architecture, components, reuse, error handling, risks | [design.md](design.md) |
| Checks | claims with proofs, every set joined member by member, the nine dimensions swept | [checks.md](checks.md) |
| Tasks | atomic tasks in phases, each with its files, reuse and checks; the second stop for a human | [tasks.md](tasks.md) |
| Build | one task at a time: tests from the checks, the code, a commit, the screens walked | [build.md](../../implementar/references/build.md) |
| Verify | rule 5 | [verify.md](../../implementar/references/verify.md) |

Decisions and lessons: [memory.md](memory.md).

## Scripts

Resolve `<spec-plan>`, `<implementar>` and `<build-review>` as the directories of those skills, side by side in the same skills folder. `check_commit.py` lives in `<implementar>/scripts/`, `validate_verification.py` in `<build-review>/scripts/`, and every other script in `<spec-plan>/scripts/`; run `python3 <that directory>/scripts/<name>.py`. Pass `--root` when cwd is not the project root. A non-zero exit means stop and fix.

Run a script rather than read it: its messages say what to change. On Windows, where `python3` may be the Microsoft Store alias, run `python` or `py -3`.

| When | Command |
| --- | --- |
| Before presenting the plan | `validate_plan.py <feature>` |
| Before presenting the tasks | `validate_tasks.py <feature>` |
| Before starting to build | `validate_checks.py <feature> --execute` - it also requires the plan's `**Approved**:` line, and runs the `Build:` line once: red before any change stops; then `validate_tasks.py <feature> --execute` when tasks.md exists - it requires the tasks' `**Approved**:` line |
| Before each commit | `check_commit.py --message "<msg>"` - it also prints what follows the last commit |
| Before dispatching the Verifier, and after the fix | `check_proofs.py <feature>` |
| Before declaring done | `validate_verification.py <feature>` |
| At distillation | `lessons.py add ...` |
| After editing a validator or template | `selftest.py` |

`selftest.py` mutates the fixtures in `scripts/fixtures/` once per gate rule and requires every mutant to be killed; the fixtures are also a worked example of a passing artifact set.

## Requires

| Needs | For | Without it |
| --- | --- | --- |
| Python 3.8+ (standard library only) | every script | the gates do not run; the phases still apply |
| git | `check_proofs.py` (HEAD, clean tree) | no HEAD check: say so in the report |
| Git for Windows (on Windows) | `check_proofs.py` runs proofs in its bash, because proofs are POSIX shell | proofs run in `cmd.exe` and the script warns |
| sub-agents | the Verifier | run its file in a new session and write `self-verified`; the gate warns |
| a browser the agent can drive | the Verifier's photos and the walk | record the blocker; hand the steps to the user |

Test runners: none is built in. `check_proofs.py` runs the commands `checks.md` names as the project runs them, one at a time, with no timeout; a run's own parallelism is whatever the project configured ([checks.md](checks.md)).

## Output

Produce the artifact; do not narrate the phase. Lead with the verdict and state decisions plainly. Section headings stay in English; prose follows the project; identifiers are never translated.
