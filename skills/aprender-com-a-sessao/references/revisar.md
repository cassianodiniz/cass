# Revisar

Run when the user asks to review saved learnings. Read [`registro.md`](registro.md) first: it holds the folder, the format and the commit rule.

1. Read `docs/aprendizados/INDICE.md` in the repo the session is working on. If the folder or the index does not exist, tell the user no retrospective has been saved yet and stop, creating nothing.
2. Open every record whose index row shows `pendentes` or `sem nota` above zero. For each one, compare its table with its index row: when they disagree, the record wins. Rewrite the row and the placar from the record. This is bookkeeping, not a decision, so do it even when the user decides nothing today, and say so in one line.
3. Show the user: the pending items (date, #, sugestão, gravidade), the done items still without a nota, and the placar por área.
4. Apply the user's decisions, item by item:
   - **aprova**: apply it (see "Aplicar"), mark `feita DD/MM`, record the nota they give.
   - **descarta**: mark `descartada DD/MM`, record the nota they give.
   - **nota** for an item already done: record it.
   - Anything the user did not mention stays as it is.
5. Write the records and the index, then commit (see `registro.md`). Done when every decision is in its record, the index matches the records, and both are committed.

## Aplicar

- Make the change the item describes in "O que mudar" and "Onde", in the repo where it lands, which may differ from the skill's repo.
- Follow that repo's own git rule from its `CLAUDE.md`/`AGENTS.md` (for example: commit on main naming paths, or branch and PR with no merge before the user's OK). If no rule is written, ask before committing.
- If the item no longer applies (the file is gone, the change already exists), tell the user and ask whether to mark it `descartada`.
