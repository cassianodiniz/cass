# PR body

Adapted from Matt Pocock's `pr` (MIT), crediting Dex Horthy / Humanlayer's `show-me`: https://github.com/mattpocock/skills/tree/main/skills/engineering/pr. Keep the smallest useful visual, before/after evidence and merge danger. Write brief prose in the user's language and project vocabulary; give each fact once.

The body lives in the feature folder as `pr.md`, so it survives a compaction; the PR on GitHub is a copy refreshed at each authorized publication.

## Read the sources

| PR information | Sources |
| --- | --- |
| Task, original plan and decisions | plan.md (checks.md `## Intent` when there is no plan) and the decisions in `.specs/STATE.md`. |
| Stage and progress | The slices in plan.md `## Criteria`, the completion marks and `## Handoff` in checks.md, and current evidence. |
| Before | Merge-base code and earlier tests, output or screenshots. |
| Delivery and route taken | Current diff/code/commits compared with the approved plan. |
| Proof and measured gains | proofs.md, verification.md, the review photos and measurements for the reviewed code. |
| Risks, pending work and testing | Unmet criteria, reproduction steps, verification.md findings and accepted or refused fixes. |

Read originals. Decisions and checked slices do not prove delivery. Match evidence to the tested code and subsequent changes; separate recorded results from a new run. Support history claims with Git/API evidence. Name missing/conflicting information.

## Body

Open with **Feature**, **Plano** (link to the approved plan, or identify the available source) and **Andamento** (actual stage, including already merged). One feature remains one PR. Show a compact `Fatia | Estado | Falta` table with the plan's slices, the current slice and supported counts. Keep implementation progress separate from final feature verification. Small changes need only the overall stage; show only recorded divisions/totals.

### Tarefa
Explain the problem, who it affects, the conditions that trigger it and its practical impact. Distinguish ordinary use from a specific combination when the sources establish that. Give frequencies, thresholds or timing only when documented; otherwise say what is unknown.

### O que muda
One row per meaningful behavior:

| Situação | Antes | Depois | Estado |
| --- | --- | --- | --- |

Situação is the action/condition; Antes is the baseline; Depois is the agreed result. Estado shows **Não iniciado**, **Em construção**, **Bloqueado** (reason), **Implementado — verificação pendente**, or **Verificado** (proof scope). Missing evidence is **Não confirmado**. Keep unfinished promises visible.

Place fenced Mermaid beside the table: use the plan's `## Shape` drawing, the smallest clear view of the plan. Use only behaviors already documented in the plan/PR. Code/evidence confirms progress; update the changed steps as work advances, preserving the distinction between planned and proven outcomes. Every label/arrow expresses existing information, without rebuilding internal execution. Omit prose explaining what the diagram/table summarizes. Use clear arrowheads and short conditions. Check the local render; distinguish a GitHub check.

### Entrega e provas
Briefly compare the approved plan with actual delivery: what changed direction, why and what remains. Link concrete before/after tests, output, screenshots or measurements and what they establish. Measured gains include their scenario; identify missing/outdated proof once. Before implementation, say work has not started.

### Como testar antes de mergear
A numbered list, one item per line, with actions and observable expected results. Put a blank line before the list so GitHub renders it correctly. Identify checks already run, pending or dependent on merge/deploy.

### Riscos e pendências
For each relevant issue: trigger, affected people/workflow, consequence, evidence/uncertainty and next action. Preserve accepted limitations and declined fixes. End with **Reversão do código:** how to undo it; **Efeitos já produzidos:** what reversal cannot recover, or what remains unconfirmed.

Once the branch is on GitHub, use verified links at the reviewed commit; before that, link the feature folder on the branch, preserving the original approved-plan reference when explaining a change of direction. End with **Registros da feature:** folder link or “pasta não localizada/não confirmada”; then `Closes #N` only when the feature started from an existing issue. Preserve user notes and publication approvals. If publication fails, keep the local draft and report the pending action.
