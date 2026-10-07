# Registro dos aprendizados

The single source of truth for the saved-learnings format, read by both the retrospective (save step) and [`revisar.md`](revisar.md).

## Where

`docs/aprendizados/` at the root of the git repo the session worked on (`git rev-parse --show-toplevel` from the session's folder). Never inside this skill's folder: the skill is installed and updated as part of a plugin, so files saved there are lost on update or uninstall, and learnings about a repo belong to that repo, where everyone who works in it sees them. If the session did not work inside a git repo, ask the user where to save before writing anything. Everything in the folder is written in Portuguese, with dates in Brasília time (America/Sao_Paulo).

## Record

One file per retrospective: `docs/aprendizados/AAAA-MM-DD-<assunto>.md`, dated the day of the retrospective, `<assunto>` being the session's topic in kebab-case (append `-2` if the name is taken).

```markdown
# Retrospectiva DD/MM/AAAA: <assunto>
Sessão analisada: <qual sessão, em poucas palavras> · Repositório: <repo da sessão>

| # | Sugestão | Área | Gravidade | Situação | Sua nota |
|---|---|---|---|---|---|
| 1 | <sugestão em uma linha> | <área> | alta | pendente | — |

## 1. <sugestão em uma linha>
O que aconteceu: <o que a sessão mostrou>
O que mudar: <a mudança concreta>
Onde: <arquivo ou lugar>
```

- **Área**: one of the seven categories, by its fixed Portuguese name: Navegação, Verificações automáticas, Padrões de código, AGENTS.md global, Economia de ferramentas, Instruções que não mudam nada, Acesso à informação.
- **Gravidade**: alta, média or baixa.
- **Situação**: `pendente`, `feita DD/MM` or `descartada DD/MM`. A postponed item stays `pendente`.
- **Sua nota**: `—` until the user gives one, then `útil|inútil|errada: <o porquê, nas palavras dele>`.

## Index

`docs/aprendizados/INDICE.md` is a cache of the records, so `revisar` opens only the files that need attention. The record's table is the truth; the index is rebuilt from it whenever they disagree.

```markdown
# Índice dos aprendizados

| data | assunto | pendentes | sem nota | úteis | inúteis | erradas | arquivo |
|---|---|---|---|---|---|---|---|
| AAAA-MM-DD | <assunto> | <n> | <n> | <n> | <n> | <n> | `<arquivo>` |

## Placar por área

| área | úteis | inúteis | erradas |
|---|---|---|---|
| <área> | <n> | <n> | <n> |
```

- One row per record, oldest first. `sem nota` counts items `feita` or `descartada` whose nota is still `—`.
- Placar: notes summed across all records, one row per área that has at least one note.

Every write to a record rewrites its index row and the placar in the same pass.

## Commit

In the repo that holds `docs/aprendizados/`, follow that repo's own git rule from its `CLAUDE.md`/`AGENTS.md` (for example: commit on main naming paths, or commit on the current branch so the record goes in its PR). If no rule is written, ask before committing. `git add` the record(s) and `INDICE.md` by name, with the message `aprender-com-a-sessao: retro DD/MM — <assunto>` or `aprender-com-a-sessao: revisão DD/MM`.
