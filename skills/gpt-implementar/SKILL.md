---
name: gpt-implementar
description: "Use when the user invokes /gpt-implementar (old name /gpt-builder), or answers the final yes of /spec-plan with \"sim, codex\", to build a feature already approved in `.specs/features/<feature>/` with OpenAI Codex writing the code instead of Claude. Not for work whose spec still needs decisions (/spec-plan first), for reviewing a finished feature (/build-review), or for tasks that need Claude-session tools (MCP, secrets, browser)."
---

# gpt-implementar — a /implementar com o Codex construindo

Siga a skill `/implementar` inteira (`../implementar/SKILL.md` e os arquivos que ela manda ler), com uma troca só: **quem constrói cada lote é o Codex**, sempre, no papel do ajudante de lote de `../implementar/references/sub-agents.md`. Esta sessão é o orquestrador desse mesmo arquivo. Abaixo está só o que muda por ser o Codex; o resto vale como está na `/implementar`.

## O que muda na /implementar (vale por cima dela)

1. **Sempre delega, sem oferecer.** Não valem aqui a construção na própria sessão até ~8 tarefas nem a oferta de ajudantes: o usuário escolheu o Codex ao chamar esta skill. Monte os lotes como em `sub-agents.md` (fases inteiras, ~7 tarefas; obra de até ~8 tarefas é um lote só) e mande cada lote ao Codex, um depois do outro, sem pedir sim antes do primeiro.
2. **Parada vira relato.** O Codex não fala com o usuário. Quando a `/implementar` manda parar e perguntar, o Codex para e relata no resumo; você leva a pergunta ao usuário no formato do item 7 do SKILL.md da `/implementar` e, com a resposta, retoma a mesma sessão do Codex.
3. **Conserto é do Codex.** Os consertos de cada lote e as tarefas de conserto aprovadas na `/build-review` vão para o Codex (ver Conserto, abaixo).

## Antes do primeiro lote

Rode `codex --version` (precisa ser ≥ 0.156) e `codex login status`. Se o Codex não estiver instalado ou não estiver logado, pare e avise o usuário citando o erro, sem começar a obra. Não construa você no lugar dele.

## Pedido de cada lote

Escreva num arquivo temporário (`P=$(mktemp)`) o que `sub-agents.md` lista em "What a batch worker receives", com caminhos absolutos, mais o caminho do glossário do projeto (item 1 do SKILL.md da `/implementar`). Diga ao Codex que ele é o ajudante de lote de `sub-agents.md`: faz o que está em "What a batch worker does", segue `implement.md` em cada tarefa, confere a mensagem de cada commit com `python3 <caminho absoluto de ../implementar/scripts/check_commit.py> --message "<msg>"` e, nos casos de parada da `/implementar`, para e relata no resumo.

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

Faça o papel do orquestrador em `sub-agents.md` ("The orchestrating agent's role during Execute", passos 3 a 6). O relato do Codex não conta como prova.

## Conserto: no máximo 2 rodadas

Mande ao Codex (resume) a lista exata: problema, arquivo, prova esperada. Depois da 2ª rodada ainda vermelho: **pare**. Não conserte você, nem com pressa do usuário, nem sendo uma linha: o combinado é que o Codex digita, e um conserto seu esconde que ele não entregou. Diga ao usuário o que falta, oferecendo: nova sessão do Codex, você consertar (só com o aval dele), ou seguir pra `/build-review`.

Fluxo: `/spec-plan` → **`/gpt-implementar`** → `/build-review`.
