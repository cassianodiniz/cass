---
name: gpt-implementar
description: "Use when the user invokes /gpt-implementar (old name /gpt-builder), or answers the final yes of /spec-plan with \"sim, codex\", to build a feature already approved in `.specs/features/<feature>/` with OpenAI Codex writing the code instead of Claude. Not for work whose spec still needs decisions (/spec-plan first), for reviewing a finished feature (/build-review), or for tasks that need Claude-session tools (MCP, secrets, browser)."
---

# gpt-implementar — a /implementar com o Codex construindo

Siga a skill `/implementar` inteira (`../implementar/SKILL.md` e os arquivos que ela manda ler), com uma troca só: **quem constrói cada lote é o Codex**, sempre. Esta sessão coordena: monta o pedido de cada lote, confere o resultado rodando os testes ela mesma, faz as perguntas ao usuário e, no fim, inicia a `/build-review` como a `/implementar` manda.

O contexto desta sessão é o recurso caro; o que o Codex lê não pesa aqui. Por isso você confere pelo resultado dos testes e pelo git, não lendo o código que o Codex escreveu.

## O que muda na /implementar (vale por cima dela)

1. **Sempre delega, sem oferecer.** Não valem aqui a construção na própria sessão até ~8 tarefas nem a oferta de ajudantes acima disso (`Sub-Agent Delegation` no SKILL.md da `/implementar`; "Before implementing: assess sub-agent delegation" em `references/implement.md`): o usuário escolheu o Codex ao chamar esta skill. Monte os lotes como em `references/sub-agents.md` da `/implementar` (fases inteiras, ~7 tarefas; obra de até ~8 tarefas é um lote só) e entregue cada lote ao Codex, um depois do outro. Não peça sim antes do primeiro lote.
2. **O ajudante de lote é o Codex.** Ele recebe o que `references/sub-agents.md` lista em "What a batch worker receives" e faz o que está em "What a batch worker does": cada tarefa no ciclo de `references/implement.md` (teste antes, gate, `tasks.md` marcado e um commit por tarefa) e, no fim, o resumo curto.
3. **Parada vira relato.** O Codex não fala com o usuário. Nos casos em que a `/implementar` manda parar e perguntar (teste que parece errado, tarefa bloqueada, bug fora do escopo, ação fora da máquina), o Codex para e relata; você leva a pergunta ao usuário no formato do item 7 do SKILL.md da `/implementar` e, com a resposta, retoma a mesma sessão do Codex.
4. **Conserto da /build-review.** As tarefas de conserto que o usuário aprovou na `/build-review` também vão para o Codex, do mesmo jeito.

O resto da `/implementar` vale como está: a branch da feature, a retomada, o sim antes de cada push e a `/build-review` depois da última tarefa.

## Antes do primeiro lote

Rode `codex --version` (precisa ser ≥ 0.156) e `codex login status`. Se o Codex não estiver instalado ou não estiver logado, pare e avise o usuário citando o erro, sem começar a obra. Não construa você no lugar dele.

## Pedido de cada lote

Escreva num arquivo temporário (`P=$(mktemp)`), nesta ordem:

- **PAPEL:** você é o ajudante de lote da skill implementar. Leia e siga, para cada tarefa, `<caminho absoluto de ../implementar/references/implement.md>`, `tdd.md`, `tests.md`, `mocking.md` e `coding-principles.md` da mesma pasta. Mensagem de commit conferida com `python3 <caminho absoluto de ../implementar/scripts/check_commit.py> --message "<msg>"`.
- **LOTE:** os ids das tarefas, nesta ordem, e o caminho de `tasks.md`; nele estão a Test Coverage Matrix e os Gate Check Commands. Também `spec.md` e, se existir, `design.md` da feature.
- **LIMITES:** arquivos que pode tocar (o `Where` de cada tarefa, mais `tasks.md`); o que não pode; fora de escopo. Sem push, branch nova nem escrita fora desta máquina.
- **PARE E RELATE:** teste que parece errado, tarefa bloqueada, bug fora do escopo ou ação fora da máquina: pare nessa tarefa e relate, sem contornar. Nunca enfraqueça, pule nem apague teste.
- **RELATÓRIO:** no máximo 30 linhas, no formato do resumo de `references/sub-agents.md` (tarefas feitas com o hash de cada commit, testes, desvios e bloqueios), mais as decisões que a spec não fixava. Não cole saída de teste.

## Comandos (não mude)

```bash
OUT=$(mktemp)
codex exec --model gpt-6.1-sol -c model_reasoning_effort="medium" -c service_tier="default" --yolo --json -o "$OUT" - <"$P" 2>/dev/null | grep '"type":"thread.started"'
# conserto ou resposta a uma parada, na MESMA sessão do Codex:
codex exec resume "<thread_id>" --model gpt-6.1-sol -c model_reasoning_effort="medium" -c service_tier="default" --dangerously-bypass-approvals-and-sandbox --json -o "$OUT" - <"$P2" 2>/dev/null >/dev/null
```

- Guarde o `thread_id` da linha `thread.started`. Nunca `--last`: pega a conversa errada, e um id errado cai na última conversa sem dar erro.
- O pedido vai por `-` (arquivo na entrada); sem isso o Codex trava esperando. A resposta dele é o arquivo `$OUT`.
- Modelo, esforço e `service_tier="default"` sempre explícitos: sem eles o Codex usa o `~/.codex/config.toml`, que o app reescreve sozinho e que pode estar no modo rápido (`service_tier = "priority"`). Variantes `-codex` dão erro 400 em conta ChatGPT.
- Rode da raiz do repo. No Bash, `timeout: 600000`; lote grande → `run_in_background: true`, e quando terminar a primeira linha pro usuário é `🔔 CODEX TERMINOU — verificando`.
- Sem linha `thread.started` ou sem `$OUT`, ou permissão recusada → pare e conte ao usuário citando o erro. Não troque flags nem construa você.

## Conferir cada lote

Antes de mandar o lote, anote o commit atual (`git rev-parse HEAD`).

1. `git status --porcelain` e `git log --oneline <anotado>..HEAD`: um commit por tarefa do lote, com o `tasks.md` marcado no mesmo commit. Arquivo fora dos limites, arquivo solto ou tarefa sem commit entra na lista de conserto.
2. Rode você o gate do `tasks.md` e confira que a contagem de testes não caiu. O relato do Codex não conta como prova.
3. Algo vermelho → conserto. Tudo verde → próximo lote; depois do último, a `/build-review` (passo 9 de `references/implement.md`).

Abra código só quando precisar montar um conserto que o teste vermelho não explica, e só o trecho.

## Conserto: no máximo 2 rodadas

Mande ao Codex (resume) a lista exata: problema, arquivo, prova esperada. Depois da 2ª rodada ainda vermelho: **pare**. Não conserte você, nem com pressa do usuário, nem sendo uma linha: o combinado é que o Codex digita, e um conserto seu esconde que ele não entregou. Diga ao usuário o que falta, oferecendo: nova sessão do Codex, você consertar (só com o aval dele), ou seguir pra `/build-review`.

Fluxo: `/spec-plan` → **`/gpt-implementar`** → `/build-review`.
