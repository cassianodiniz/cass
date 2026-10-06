# Phase 2 — Spec, issues and handoff

Use only the decisions confirmed in Phase 1. Do not reopen closed choices; if a gap appears that changes scope, behavior or a test seam, go back to the user before finishing the draft.

Write everything the user may read in the user's language: the approval message, the parent spec and the issues. The user opens the plan files to read them.

## 1. Write the parent spec

Produce a single view of the plan with:

- **Problem:** the user's situation and the desired outcome.
- **Solution:** the proposed behavior, without turning the spec into code.
- **Stories and scenarios:** numbered needs and Given/When/Then scenarios for the relevant flows, failures, permissions and transitions.
- **Implementation decisions:** affected modules or interfaces, contracts, schema and integrations; avoid file paths and snippets that go stale, unless a prototype recorded a decision better than prose.
- **Test decisions:** approved seams, existing precedents and real commands already known.
- **Out of scope:** explicit exclusions.
- **Notes:** risks, migration, rollout and points still `UNKNOWN` that do not block slicing.

Use the domain vocabulary and respect the project's ADRs.

## 2. Slice into executable issues

Break the spec into vertical tracer bullets:

- each issue delivers one complete, verifiable behavior through the layers it needs;
- each issue fits in one fresh context session;
- each issue declares its real blockers;
- issues with no blockers form the frontier available for parallel implementation;
- necessary pre-refactoring comes first;
- a broad refactor uses expand → migrate in green batches → contract, with explicit dependencies.

Each issue must be self-contained. Someone who receives only its file needs to know what to build, why, how to observe that it is done, which decisions are already made and what is not authorized.

When reconciling a draft, read every issue in full, including the implementation/test sections retained by reference. During that reading, build a temporary completion map. Give every original acceptance checkbox its own entry, including unchanged ones; do not group criteria or use “all criteria”. Use its source ID and a short label, keeping the original text in the source file; do not copy the whole source into the map. Map each nested action, observation point and failure separately. Also inspect binding implementation/test passages. For each clause record: source criterion/clause | required suppliers and availability | structural repair | separate functional gap. Classify each supplier as existing, completed predecessor, self, later or UNKNOWN, with its concrete capability and the approved proof seam. Save that map in the temporary draft before editing; when writing is unavailable, include the map in the response before the edits. A claim that the audit was done does not replace its entries. An edge proof may be available before a gesture; shared files alone do not create a blocker.

Repair each later supplier now, without waiting for an independent functional choice in the same criterion. Apply the TLC check: "If code can't be tested in the task that creates it, the task boundaries are wrong." Move the complete obligation to an issue with all suppliers, bring the capability earlier, or merge only when separate delivery cannot be verified. Preserve every action, result, observation point, permission, failure and proof. For a displayed state after an action, the final criterion must explicitly preserve every original observation point after that action.

Reconstruct the original plus literal before/after edits. For every edited criterion, build a final coverage map: each original clause | exact final clause and owner | suppliers available at completion. Map each action × observation point separately; a predecessor's initial display does not prove the state after a later action. Repair any unmapped clause before returning. An unresolved or UNKNOWN clause remains literal in its final owner's criterion, including every action × observation combination; a note or an initial observation elsewhere does not replace that obligation. Record its open functional decision without dropping it. Reconcile every final supplier with the issue's blockers and the parent graph; do not declare issues parallel when one consumes the other's result. Recheck inherited implementation/test references, exclusions and conflicting passages; keep explicit boundaries and green refactoring batches. Unverified file/interface overlap stays UNKNOWN. Move only affected entries into the parent Notes, with their complete original/final text and owners; the temporary map is working material, not extra approval-message content.

Keep Status: draft and conflicting functional passages literal. Record their unresolved decision separately in Notes and return to Phase 1 before approval, while retaining the independent structural repairs already made. Resolve technical slicing choices from the supplied material and explain them; the approval message asks the user about them (section 3). Preserve the existing approval-message format.

Use this format (keep the section titles as written; `$implementar` finds `Varredura (decidida na entrevista)` by name):

```markdown
# <issue-key> — <título>

**Status:** draft | approved | published
**Plano-pai:** <caminho do index.md>
**Tracker:** <URL/ID ou "não publicado">
**Bloqueada por:** <issue-keys ou "nenhuma">

## Resultado
<comportamento completo entregue por esta fatia>

## Cenários e critérios de aceite
- [ ] <resultado observável e concreto>

## Decisões de implementação
- <contrato ou decisão já aprovada>

## Contrato de teste
- Seams aprovados: <interfaces públicas>
- Provas conhecidas: <comandos reais ou UNKNOWN>

## Varredura (decidida na entrevista)
- <cada um dos 9 que toca esta issue>: <critério de aceite acima | já existe em … | fora de escopo porque …>

## Fora de escopo
- <limite desta issue>
```

## 3. Approval before any effect

Decide where the plan lives before writing the message; it lives in one place only. If `docs/agents/issue-tracker.md` exists, follow it. Otherwise, as Matt Pocock's `setup-matt-pocock-skills` puts it: "If a `git remote` points at GitHub, propose that." Without a GitHub remote, the plan lives in local files (section 4).

Write the parent spec and every issue in full, with `Status: draft`, to a temporary directory outside the repository, using the same layout as section 4 (`index.md` + `issues/`). The draft is what the implementer reads. The user approves from the approval message below.

Write the approval message in the user's language, in plain words, for a reader who does not program: they need to understand how the plan works in order to decide well. Tell the plan once, as a story in steps: each fact appears in one place, the step where it happens. How each step is built lives in the draft; the message says what changes for the people involved. Aim for 300 to 500 words. It is, in this order:

1. **The ask, and how it works when it is done** — open with "I need your yes for this plan" and, on the same opening line, "I divided it into N parts (issues)" or "This is a single delivery". Explain that each part is built and checked separately. Say that the whole plan becomes one PR, as Matt Pocock's `implement-spec` puts it: "the entire spec implemented on a single integration branch"; then state the execution arrangement. A part is never a separate PR or deployment. Then three or four sentences describing the finished result from the user's side: what happens, to whom, in what order.
2. **How I get there, in N steps** — one numbered step per issue, in dependency order: one sentence of about 20 words, in the words the people involved would use, stating what that step does to money, data, people's work or what keeps running, when it does — "Postmark, US$ 15 a month", "the old column is deleted for good", "the 212 members start receiving it". Walk through the Phase 1 decisions one by one; a Phase 1 decision that appears in no issue is a gap: fix the draft before showing the message. When work is delegated to subagents, the step says what they do, what they cannot touch, and what their check does not see.
3. **Where I deviated from what you asked, and why** — one line per deviation, quoting the user's words; then one line per assumption that changes what the user gets, with what to tell me if it is wrong. Or "nothing".
4. **Cost and time** — one line: an estimate, or "I don't know" and why.
5. **What the plan does not cover, and what is still open** — one line each.
6. **Size of the parts** — the three questions from Matt Pocock's `to-tickets`, each in plain words with your recommended answer and why:
   - Does the granularity feel right? (too coarse / too fine)
   - Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
   - Should any tickets be merged or split further?
7. **Full text** — the draft path, and "ask 'open step N' and I will explain that issue here".
8. **Close** — "Approve?" and where a yes saves the plan: on GitHub, "a yes creates in `<owner/repo>` 1 plan issue + N issues, with the labels `<…>`", naming the labels it will create because they do not exist yet; in files, the repository path.

The message asks once. Treat the user's yes as approval of the spec content, the issue granularity, the dependencies, the test seams, and permission to save or publish them to the destination shown.

Iterate until the user approves. Before approval, write no files in the repository, create no issues and apply no labels. After approval, save the plan to the destination shown (section 4).

## 4. Persistence without collisions

Never use a `PLAN.md` at the root. Detect the repository's existing convention first; when there is none, use:

```text
docs/plans/<plan-id>/index.md
docs/plans/<plan-id>/issues/<issue-key>-<slug>.md
```

The `<plan-id>` must be unique and stable:

- with a real parent issue: `<tracker>-<id>-<feature-slug>`;
- without one: `<YYYYMMDDTHHMMSSZ>-<feature-slug>`.

Give the plan a short name (2 to 4 words, lowercase, hyphens), unique among the plans in the repository, on the first line of `index.md`: `Plan name: <plan-name>`. The directory keeps the `plan-id`.

`index.md` holds the parent spec, the dependency graph and links to the issues. It is context, not an implementation unit.

Each file in `issues/` holds exactly one issue. Use as `<issue-key>` a stable local key (`01`, `02`, `03`) in dependency order; record the tracker's real ID inside the file, without renaming it after publication. Do not reuse another session's directory and do not overwrite an existing artifact; on collision, generate another `plan-id`.

On GitHub, write no plan files; use the commands in `references/github.md`. Publish the parent spec first, as one issue titled with the plan name; it is the parent of every issue. Then, from Matt Pocock's `to-tickets`: "publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues. Apply the `ready-for-agent` triage label unless instructed otherwise; the tickets are agent-grabbable by construction." An issue only the user can do (for example, going live) gets `ready-for-human` instead: "Requires human implementation". If `docs/agents/triage-labels.md` exists, use its label names; create the labels that do not exist. Each issue's header keeps only `Plano-pai: #<plan>` and `Bloqueada por: #n`; GitHub holds the status.

"Do NOT close or modify any parent issue." (`to-tickets`)

## 5. Handoff to build the plan

After the user approves, offer to build the whole plan with one more yes: one session builds every part, in dependency order, on the plan's branch, as Matt Pocock's `implement-spec` puts it: "the entire spec implemented on a single integration branch". It stops and calls the user at a part only the user can do. Do not ask the user to choose a part. Offer the two builders, one line each, pointing to the plan, and let the user pick:

```text
$implementar #<plan-issue>   (the agent in this session builds: Claude, Codex or any other)
$gpt-implementar #<plan-issue>   (Claude orchestrates, GPT subagents in Codex build)
```

Without GitHub, use `<plan-name>` in place of `#<plan-issue>`. Call the builder the user picks only when the user says yes.
