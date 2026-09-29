---
name: gpt-implementar
description: "Use when the user invokes /gpt-implementar (old name /gpt-builder) or wants OpenAI Codex, not Claude, to build work that is already decided — a /spec-plan issue, a locked plan, or a work-order task such as a refactor, mechanical migration, bug fix with a known repro, or test writing (\"have codex build this\", \"hand the plan to codex\", \"delegate the build to codex\"). Not for edits under ~20 lines, for work whose spec still needs decisions (/spec-plan first), for reviewing existing code (/build-review), or for tasks that need Claude-session tools (MCP, secrets, browser)."
---

# gpt-implementar — Codex digita, Claude coordena

Siga a skill `/implementar` inteira (`../implementar/SKILL.md`): árvore limpa, commit-marco, checklist antes do código, "sim" por issue, relatório final. Esta skill muda uma coisa só: **quem digita o código é o Codex**, numa sessão separada. A sessão delega a construção e continua dona das provas e dos commits.

Seu papel é coordenar, não reconstruir. O contexto desta sessão é o recurso caro; o que o Codex e o fiscal leem não pesa aqui. Por isso você confere pelo resultado dos testes, não lendo o código que o Codex escreveu.

## Largada

Uma mensagem só: qual issue, modelo `gpt-6-sol` com esforço `medium`, e o comando de prova (da spec; se ela não tiver, do manifesto/CI do repo). Espere o sim.

## Contrato pro Codex (um só, pra entrega inteira)

Escreva num arquivo temporário (`P=$(mktemp)`), nesta ordem:

- **OBJETIVO:** pronto quando cada item de `<CHECKLIST>` tem sua prova verde (liste os itens).
- **SPEC:** `<SPEC_FILE>`. Outras issues do plano estão fora. Passo impossível como escrito → pare e reporte, não redesenhe.
- **COMO:** leia `<caminho absoluto de ../implementar/SKILL.md>` e `<caminho absoluto de ../implementar/references/tdd/tdd.md>` e siga como se fosse você: TDD, nunca enfraquecer nem apagar teste, porta nova registrada em `Landing` antes do código, falha real de cada teste na linha `Red:` do checklist. No checklist, mexa só em `Red:` e `Landing`. Não faça commit, push nem branch.
- **LIMITES:** arquivos que pode tocar; o que não pode; fora de escopo.
- **RELATÓRIO:** no máximo 30 linhas — arquivos mudados (uma linha cada), código de saída de cada prova, decisões que a spec não fixava, desvios. Não cole saída de teste.

## Comandos (não mude)

```bash
OUT=/tmp/gpt-implementar-<nome do checklist>.txt
codex exec --model gpt-6-sol -c model_reasoning_effort="medium" --yolo --json -o "$OUT" - <"$P" 2>/dev/null | grep '"type":"thread.started"'
# correção, na MESMA sessão do Codex:
codex exec resume "<thread_id>" --model gpt-6-sol -c model_reasoning_effort="medium" --dangerously-bypass-approvals-and-sandbox --json -o "$OUT" - <"$P2" 2>/dev/null >/dev/null
```

- Guarde o `thread_id` da linha `thread.started`. Nunca `--last`: pega a conversa errada, e um id errado cai na última conversa sem dar erro.
- O pedido vai por `-` (arquivo na entrada); sem isso o Codex trava esperando. A resposta dele é o arquivo `$OUT`.
- Modelo e esforço sempre explícitos: sem eles o Codex usa o `~/.codex/config.toml`, que o app reescreve sozinho. Variantes `-codex` dão erro 400 em conta ChatGPT.
- Rode da raiz do repo. No Bash, `timeout: 600000`; entrega grande → `run_in_background: true`, e quando terminar a primeira linha pro usuário é `🔔 CODEX TERMINOU — verificando`.
- Sem linha `thread.started` ou sem `$OUT`, ou permissão recusada → pare e conte ao usuário citando o erro. Não troque flags nem construa você.
- Requisito: `codex --version` ≥ 0.156, já logado.

## Conferir cada rodada

1. `git status --porcelain` e `git diff --stat <marco>`: arquivo fora dos limites, commit feito pelo Codex ou arquivo solto → entra na lista de correção.
2. Rode você as provas nomeadas do checklist e a suíte, em modo quieto (`-q`). O relato do Codex não conta como prova.
3. Commit do que chegou, arquivo por arquivo pelo nome.
4. Algo vermelho → correção. Tudo verde → fiscal: um subagente (`model: sonnet`) com o briefing de `../implementar/references/fiscal.md`. É ele quem abre o código e confere cada asserção; você lê só o veredito. FAIL do fiscal → correção.

Abra código só quando precisar montar uma correção que o teste vermelho não explica, e só o trecho.

## Correção: no máximo 2 rodadas

Mande ao Codex (resume) a lista exata: problema, arquivo, prova esperada. Depois da 2ª rodada ainda vermelho: **pare**. Não conserte você, nem com pressa do usuário, nem sendo uma linha: o combinado é que o Codex digita, e um conserto seu esconde que ele não entregou. Faça commit do que existe e diga ao usuário o que falta, oferecendo: nova sessão do Codex, você consertar (só com o aval dele), ou seguir pro `/build-review`.

## Fim

Relatório de `../implementar/references/relatorio.md`, mais as rodadas usadas e os desvios da spec. Fluxo: `/spec-plan` → **`/gpt-implementar`** → `/build-review`.
