# Codex operator

Este arquivo mantém o operador da entrada anterior; o fluxo de programação é o da Lean.
Aplica-se à sessão que despacha o Codex. Um worker já despachado não dispara outra CLI.

## Antes do primeiro envio

Rode `codex --version` (precisa ser ≥ 0.156) e `codex login status`. Se o Codex não estiver instalado ou não estiver logado, pare e avise o usuário citando o erro, sem começar a obra. Não construa você no lugar dele.

## Contexto de cada envio Lean

Escreva num arquivo temporário (`P=$(mktemp)`) caminhos absolutos para o SKILL.md do núcleo e
suas referências Checks/Build, a feature,
o plano realmente aprovado (ou o Intent aprovado), checks.md, o intervalo Git e as instruções
pertinentes do projeto/ambiente/glossário. No conserto, inclua verification.md, os relatórios
separados de cada fonte, os achados aprovados com problema/arquivo/prova esperada e as decisões
reais do usuário. Preserve a origem e o HEAD revisado de cada achado; o executor não faz a própria
revisão independente. O Codex segue esses arquivos, registra o Handoff nativo e devolve o que
Build pede em “Then stop”: checks fechados, commits, provas e desvios. Não traduza em tasks.md,
validation.md ou uma nova lista de tarefas. Resolva check_commit.py no mesmo núcleo compartilhado.
Leia [o contrato comum de delegação](../../implementar/references/delegation-lean.md).
Inclua no arquivo realmente enviado ao Codex o brief e a exigência de retorno desse contrato,
com seus caminhos absolutos, inclusive glossário (ou ausência), baseline e decisões aplicáveis.
Aponte o Codex a esse contrato e à /implementar; pedir só o resumo de Build não substitui esses campos.
Na volta, o coordenador aplica a conferência do mesmo contrato antes de aceitar a entrega.

**Parada vira relato.** O Codex não fala com o usuário. Quando a `/implementar` manda parar e perguntar, o Codex para e relata no resumo; você leva a pergunta ao usuário no formato de [Context before asking for a decision](../../implementar/SKILL.md#context-before-asking-for-a-decision) e, com a resposta, retoma a mesma sessão do Codex.

Para resposta a uma parada ou conserto, grave o contexto atualizado em outro arquivo temporário
(`P2=$(mktemp)`) antes do resume da mesma sessão.

## Comandos (não mude)

```bash
OUT=$(mktemp)
codex exec --model gpt-6.1-sol -c model_reasoning_effort="medium" -c service_tier="fast" -c features.fast_mode=true --yolo --json -o "$OUT" - <"$P" 2>/dev/null | grep '"type":"thread.started"'
# conserto ou resposta a uma parada, na MESMA sessão do Codex:
codex exec resume "<thread_id>" --model gpt-6.1-sol -c model_reasoning_effort="medium" -c service_tier="fast" -c features.fast_mode=true --dangerously-bypass-approvals-and-sandbox --json -o "$OUT" - <"$P2" 2>/dev/null >/dev/null
```

- Guarde o `thread_id` da linha `thread.started`. Nunca `--last`: pega a conversa errada, e um id errado cai na última conversa sem dar erro.
- O pedido vai por `-` (arquivo na entrada); sem isso o Codex trava esperando. A resposta dele é o arquivo `$OUT`.
- Modelo, esforço e modo rápido (`service_tier="fast"` + `features.fast_mode=true`, nomes da documentação oficial do Codex) sempre explícitos: sem eles o Codex usa o `~/.codex/config.toml`, que o app reescreve sozinho (lá pode aparecer `"priority"`, que a OpenAI trata como o mesmo modo rápido). Variantes `-codex` dão erro 400 em conta ChatGPT.
- Rode da raiz do repo. No Bash, `timeout: 600000`; lote grande → `run_in_background: true`, e quando terminar a primeira linha pro usuário é `🔔 CODEX TERMINOU — verificando`.
- Sem linha `thread.started` ou sem `$OUT`, ou permissão recusada → pare e conte ao usuário citando o erro. Não troque flags nem construa você.

## Conserto: no máximo 2 rodadas

Mande ao Codex (resume) a lista exata: problema, arquivo, prova esperada. Depois da 2ª rodada ainda vermelho: **pare**. Não conserte você, nem com pressa do usuário, nem sendo uma linha: o combinado é que o Codex digita, e um conserto seu esconde que ele não entregou. Diga ao usuário o que falta, oferecendo: nova sessão do Codex ou você consertar (só com o aval dele). Recuperação adicional ou troca de executor depende da decisão explícita do usuário e não amplia os limites compartilhados. Enquanto vermelho, revisão e commit permanecem bloqueados. Seguir pra `/build-review` só é opção com o gate verde.
