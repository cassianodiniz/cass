# Investigate

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

## Order

1. **The problem.** Ask what is wrong today, who it affects and what changes for them when this ships, in a round of its own. When the request already says all three, skip to 2.
2. **The code.** Before the next round:
   - Load confirmed lessons: `python3 <spec-plan>/scripts/lessons.py --root <project> list --status confirmed` (add `--scope` or `--query` for the area). Confirmed only. No store yet: skip.
   - Read `.specs/STATE.md` `## Decisions`. Every `active` `AD-NNN` constrains the shape: conform, or append an entry that supersedes it and say why.
   - Open every reference the user sent in full - every capture, frame and state.
   - You must read [improve-codebase-architecture](skills/improve-codebase-architecture/SKILL.md) and follow its guidance to dispatch the explorer sub-agent, with the problem as the direction, even when the project looks small. Save its reuse list, with full paths, in the plan under `## Investigation`.
   - Check the open pull requests and issues for work that touches this area. When one does, tell the user in the next round.
   - Read [seguranca.md](seguranca.md) and follow its `No plano` section.
   - When the feature reads or changes data a screen shows and the project uses TanStack Query, read [tanstack-query-best-practices](skills/tanstack-query-best-practices/SKILL.md). Each rule of it that is the user's decision goes into the next round as a question.
   - Read [coding principles](coding-principles.md) §Before Coding: state every assumption, present every interpretation instead of picking one silently.
3. **The decisions.** Ask the gray areas below in rounds, with what the code showed beside each question. Walk the surfaces of [plan.md](plan.md) now, not at the end.
4. **The yes.** Ask for it only when no question is left and no line of [the ledger](#the-ledger) is empty. A question that surfaces while you write the plan - a screen element with no piece, a value the manual lacks, a guarantee with no mechanism - goes into one more round first.

## Gray areas

A gray area is a decision that is the user's, has more than one defensible answer, and is not settled by the code. Anything else is an assumption you state and move on from.

Ask every gray area before presenting the plan, until the requirements leave no product decision to the builder. A gray area does not become an `Assumptions` row to save a question. This includes the nine below and the surface rows of [plan.md](plan.md).

- "You decide" is an answer: record it in `Assumptions` with `Confirmed? y` and rationale `user delegated`. Write `user delegated` only when the user said it in the conversation.
- Asking clarifies how, not whether to add a capability. A new capability that surfaces goes in `Out of scope` with its reason.
- Removing, renaming or changing something a binding source draws is the user's call. Ask it as a `blocks` question with your recommendation, even when the system lacks the concept. It is never resolved by an `Out of scope` row alone. The answer becomes an `AD-NNN` in `.specs/STATE.md` whose rationale quotes the question and the option chosen; each departure it approves lands in `## Differences from the source` citing that id.
- A screen element with no existing piece in the design manual is a new piece. Ask it as a `blocks` question with concrete options, your recommendation first with one line of why. The answer becomes an `AD-NNN` in `.specs/STATE.md`.

An assumption lands in `## Assumptions` with your default, the rationale and `Confirmed? n`. `y` means a human said so.

Each answer goes into the plan in the turn it arrives - a criterion, an `Assumptions` row with `y`, or an `AD-NNN` - not at the end of the conversation: a compaction keeps the file, not the chat.

## Simplicity

1. When considering solutions, prefer the simplest one that fully satisfies the agreed behavior:
2. Avoid speculative functionality, abstractions, and scaffolding.
3. Reuse existing code, patterns, platform capabilities, and installed dependencies when appropriate.
4. Introduce new architecture or dependencies only when simpler existing options do not satisfy the requirements.
5. For bug fixes, address the root cause rather than only the reported symptom.
6. Challenge unnecessary complexity when it appears, but leave decisions to the user.

Simplicity must never remove required behavior, input validation at trust boundaries, error handling needed to prevent data loss, security requirements, accessibility basics, or anything explicitly agreed with the user.

## Format a round like so:

📝 **1** - Quer que eu transforme isso num plano pronto pra implementar? a) Sim, pode gerar o plano b) Antes disso, quero ajustar alguns pontos c) Quero só revisar o entendimento comigo primeiro

✅ (recommend 1 only if nothing is pending; otherwise recommend 2 and say what is pending)

📝**2** - Exemplo de pergunta nova.

a) Exemplo de resposta 1 b) Exemplo de resposta 2 c) Exemplo de resposta 3 ✅ (recommend 1 only if nothing is pending; otherwise recommend 2 and say what is pending)

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a later round, not this one.

Finding facts is your job, never the user's. When a frontier question needs a fact from the environment, repository, tools, or other available sources, find it yourself; don't ask the user for anything you could look up once access is available. Don't block on it: an unresolved fact is an unsettled prerequisite, so only the questions downstream of it wait; ask the rest of the frontier now. The decisions are the user's: put each to them and wait.

## The nine nobody writes down

In the first round of decisions, together with the gray areas, cover the requirements that never make it into a request. For each of the nine, say where it lands: a decision already settled above, a new question in this round with your recommended answer, or "out of scope because X" for the user to confirm. All three are complete answers; passing over one in silence is not.

1. input validation
2. failure modes (what happens when it goes wrong)
3. idempotency and retry (repeating the same action does not duplicate)
4. authorization (who may)
5. concurrency and ordering
6. data lifecycle (creation, retention, removal)
7. external dependency failure
8. state transitions
9. observability (log, metric)

Raising one is always free; growing the scope is the user's call. Asking now, while the user is in the conversation, is what keeps the build from stopping later to ask.

The design investigation is done when every branch required to define the agreed scope has been visited, all required decisions are settled, and each of the nine has landed.

If the user said the planning depends on an existing repository, any branch that depends on repository facts must also be resolved before the investigation is complete. If the user said the planning does not depend on a repository, repository access is not required to complete the investigation.

## The ledger

The plan holds `## Investigation`: one line per step. Create it when step 2 starts. Fill each line when its step ends. With no plan.md, it goes in checks.md after `## Intent`.

A line is complete with one of:
- `done - <the file and line, command or agent that shows it>`
- `asked - round <n>, question <n>`
- `n/a - <why>`

Any other value is an empty line. `done` names what you opened or ran. A step you did not do is not `n/a`: do it now. Each of the nine has its own line and its own reason.

Before each round and before the yes, read the table. An empty line is a step to do now. Write `asked` only after the code did not settle it.
