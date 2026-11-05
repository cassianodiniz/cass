# cass — pensar antes de fazer, construir com prova, conferir antes de confiar

Treze skills pra trabalhar com IA no Claude Code sem cair nas armadilhas de sempre: a IA que
sai construindo antes de entender o pedido, que diz "pronto" sem ter testado, que inventa
número de pesquisa. Cada skill resolve um desses momentos e pode ser chamada sozinha.

O fluxo de código usa o contrato aprovado: Lean para planos nativos; compatibilidade
com `spec.md` e `tasks.md` para features antigas. Veja as entradas abaixo.

## Como eu uso no dia a dia

Começo pela situação, não pelo nome da skill ([como instalar](#instalar)):

- 🔧 **Mudança a esclarecer:** direto na `/cass:spec-plan`.
- 🔎 **Pesquisar ideias:** `/cass:ask-me` → `/cass:search` → `/cass:spec-plan`.
- 🌱 **Feature nova:** `/cass:ask-me` → `/cass:auto-think` → `/cass:spec-plan`.

O fluxo atual é `/cass:spec-plan` → `/cass:implementar` → `/cass:build-review`:
uma feature inteira numa PR. A construção e a revisão começam automaticamente nas passagens
entre essas skills. Se quiser um ataque extra a uma decisão grande antes de aprová-la,
chame a `gpt-optimizer`. Conversa ficou longa? `/cass:handoff`. Sessão terminou e a IA
tropeçou? `/cass:aprender-com-a-sessao`.

---

## As skills

Na ordem em que entram no trabalho. Nos desenhos, verde marca onde a skill para e espera você.

### `/cass:ask-me` — antes de mandar uma tarefa

Te entrevista até o pedido ficar claro e entrega um pedido pronto pro agente: o que fazer, o
que não fazer e quando parar e perguntar. Serve pra qualquer tarefa, não só código.
No fechamento, mostra o combinado e o prompt antes de uma única confirmação: executar aqui,
ajustar algo ou acionar outra skill.

<p align="center"><img src="docs/skill-ask-me.svg" width="520" alt="A ask-me busca os fatos sozinha, faz rodadas de até 4 perguntas com a resposta recomendada, espera você responder e confere cada resposta com os limites que você já deu; enquanto houver decisão em aberto, faz nova rodada. No fechamento, apresenta o combinado e o prompt em caixa de código na mesma mensagem, e faz uma única pergunta para executar, ajustar ou escolher outra skill."></p>

<details><summary>Detalhe técnico</summary>

Árvore de decisões resolvida por fronteira, no máximo 4 perguntas por rodada; fatos do ambiente ela busca sozinha; pedido final com Objetivo / Pronto quando / Fazer / NÃO fazer / Parar e perguntar.

</details>

### `/cass:spec-plan` — transformar uma ideia em plano aprovado

Esclarece o pedido em rodadas e usa o vocabulário do projeto. No fluxo Lean, registra o
plano em `plan.md` e os critérios verificáveis em `checks.md`. A mensagem final explica
as ações autorizadas pelo seu sim: registrar a aprovação, publicar a branch, criar a issue
e abrir a PR em rascunho. “Sim, codex” escolhe a `gpt-implementar`.

Features antigas com `spec.md`/`tasks.md` aprovados seguem o contrato existente, sem migração
automática. O núcleo Lean, as referências e os validadores acompanham a skill.

[Instruções](skills/spec-plan/SKILL.md) · [Contrato antigo](skills/spec-plan/LEGACY.md)

### `/cass:gpt-optimizer` — revisão opcional de um plano grande

O GPT tenta derrubar um plano ou uma decisão que você já tomou e volta com Seguir, Ajustar ou
Bloquear, só com os furos que procedem. Vale em plano grande e complexo; em mudança simples,
pule.

<p align="center"><img src="docs/skill-gpt-optimizer.svg" width="520" alt="A gpt-optimizer monta o alvo com a decisão, o porquê e o estado do código; o GPT tenta derrubar; o Claude filtra cada ponto com prova. Só se o Claude descartou algum ponto, o GPT audita esse filtro numa segunda rodada, e nunca há terceira. Sai Seguir, Ajustar ou Bloquear; se Seguir, oferece levar pra construção com o seu sim."></p>

<details><summary>Detalhe técnico</summary>

Codex `gpt-6.1-sol` esforço `high`, só leitura; a 2ª rodada audita o filtro que o Claude fez dos pontos.

</details>

### `/cass:implementar` — construir a feature aprovada

Escolhe o contrato aprovado pela `spec-plan`. No Lean, constrói uma fatia por vez,
com testes e evidências; atualiza os checks antes do commit e inclui tudo no mesmo commit.
Segue para a próxima fatia sem pedir outro sim. Na delegação, prepara o contexto e confere
as evidências devolvidas. Quando a feature está pronta para verificação, inicia `build-review`.

[Instruções](skills/implementar/SKILL.md) · [Contrato antigo](skills/implementar/LEGACY.md)

### `/cass:gpt-implementar` — construir com o Codex

Segue o contrato da `implementar`, com o Codex escrevendo o código e o coordenador
conferindo as evidências. O contexto enviado usa os arquivos nativos do contrato escolhido.
O operador Codex e as regras de delegação acompanham o pacote. Depois da construção,
o coordenador inicia `build-review`.

[Instruções](skills/gpt-implementar/SKILL.md) · [Operador Codex](skills/gpt-implementar/references/codex-runner.md)

### `/cass:build-review` — conferir a feature inteira

No Lean, reúne Verifier, Standards e Spec em contextos independentes. Usa os relatórios
nativos, capturas e teste guiado quando aplicável; pede a decisão sobre cada correção e
o sim final. As correções aprovadas voltam ao executor escolhido. Uma feature Lean não
precisa do `validation.md` antigo; features antigas mantêm sua própria verificação.

[Instruções](skills/build-review/SKILL.md) · [Contrato antigo](skills/build-review/LEGACY.md)

### `/cass:design-critique` — avaliar uma tela ou proposta visual

Recebe uma captura ou descrição, o contexto e o estágio do design. Aponta o que funciona,
os problemas de usabilidade, hierarquia, consistência e acessibilidade, com gravidade,
recomendações e prioridades. O foco pode ser uma tela, navegação ou fluxo específico.

[Instruções](skills/design-critique/SKILL.md)

### `/cass:auto-think` — quando você ainda não sabe a resposta

Estuda um problema difícil e volta com a opção recomendada e as alternativas, cada uma com o
porquê. Não executa nada. Leva bem mais tempo que a `gpt-optimizer`, que só testa uma decisão
já tomada.

<p align="center"><img src="docs/skill-auto-think.svg" width="520" alt="A auto-think confirma o alvo com você e, daí em diante, não interrompe: enquadra o problema, estuda por vários ângulos, manda o GPT tentar derrubar as candidatas, passa cada uma por um portão de 4 perguntas e cava de novo só o que muda a decisão. O GPT confronta os finalistas numa segunda rodada e ela entrega a recomendada e as alternativas, sem executar nada."></p>

<details><summary>Detalhe técnico</summary>

Confronto adversarial com Codex `gpt-6.1-sol` em 2 rodadas; pesquisa via `search`; nomes e dados pessoais trocados por etiquetas antes de qualquer coisa sair.

</details>

### `/cass:search` — pesquisa com a fonte de cada número

Cada dado volta com a página, a frase exata e a data; o que não achar, ela diz que não achou.
Também serve pra atacar um plano: peça "ataca o plano com /search".

<p align="center"><img src="docs/skill-search.svg" width="520" alt="A search mede o tamanho da pergunta e só pergunta a profundidade quando ela é ambígua. Subagentes buscam em paralelo no Exa; ela confere o relato de cada um antes de confiar e faz nova passada se faltou cobertura. Cada número sai com página, frase e data, tudo fica guardado em search-findings e a resposta traz a fonte de cada dado."></p>

<details><summary>Detalhe técnico</summary>

Orquestrador Exa com subagentes; registro de procedência por número; arquivo em `search-findings/`. Precisa de conta Exa (tem plano grátis).

</details>

### `/cass:handoff` — continuar numa conversa nova

Escreve um documento de passagem, com o que foi decidido e o que falta, e te dá um texto
pronto pra colar na sessão nova. Se houver mudanças deste trabalho, oferece commit: com
seu sim, commita antes; com seu não, entrega o handoff sem commit.

<p align="center"><img src="docs/skill-handoff.svg" width="520" alt="A handoff oferece commit das mudanças deste trabalho e respeita a resposta. Registra branch, HEAD e mudanças locais pendentes, preserva decisões e motivos da conversa, referencia arquivos existentes, salva em .claude/handoffs e entrega uma frase com o caminho completo para retomar."></p>

<details><summary>Detalhe técnico</summary>

Registra branch e HEAD conferidos, distinguindo as mudanças locais fora desse commit. Se
o commit falhar, registra a falha e entrega o handoff com as pendências. Preserva trabalho
de outra frente, inclusive o que já estava staged. Usa apenas as seções necessárias e
uma frase colável com o caminho absoluto do documento. Sem Git ou sem primeiro commit,
informa a ausência de âncora.

</details>

### `/cass:aprender-com-a-sessao` — depois de uma sessão de código

Revê como a IA trabalhou numa sessão que terminou e sugere ajustes no projeto e nas instruções
pra ela errar menos da próxima vez. Não mexe no código; você decide o que aplicar. Cada revisão fica
guardada em `docs/aprendizados/` do repositório, e `/cass:aprender-com-a-sessao revisar` retoma o que
ficou pendente. Só roda quando você chama.

<p align="center"><img src="docs/skill-aprender-com-a-sessao.svg" width="520" alt="A aprender-com-a-sessao entra quando uma sessão de código terminou. Lê o manual de escrita que vem dentro dela e o registro da sessão, o caminho inteiro e não só o resultado. Procura onde o ambiente falhou: achar arquivos, checagens automáticas, regras do revisor, CLAUDE.md inchado, ferramenta cara, frase inútil e falta de informação. Guarda a lista, do mais grave ao menos grave, em docs/aprendizados/ do repositório, e você decide o que resolver agora; o resto fica pendente pra revisar depois."></p>

<details><summary>Detalhe técnico</summary>

Sete frentes: navegação, checagens automáticas (lint, tipos, testes, trava antes do commit ou no GitHub), regras do revisor (erro mecânico vira checagem; julgamento vira `CODING_STANDARDS.md`), `CLAUDE.md`/`AGENTS.md` inchado, ferramenta cara, instrução que não muda nada e falta de informação. Depois de compactar, rode numa conversa nova apontando a sessão: o registro completo continua salvo no computador. Criada por Matt Pocock (`retro`); aqui o nome foi traduzido e o guia `writing-for-agents` vai junto (veja [Créditos](#créditos)).

</details>

### `/cass:otimizar-arquitetura` — quando o código precisa de uma estrutura melhor

Dá ao agente um vocabulário único e poucas regras pra reorganizar código: juntar peças que só
repassam chamada num módulo que esconde o trabalho atrás de uma porta pequena, mais fácil de
testar e de mexer. Se você pedir, desenha essa porta de três jeitos diferentes e recomenda um.

<p align="center"><img src="docs/skill-otimizar-arquitetura.svg" width="520" alt="A otimizar-arquitetura entra quando o código vai ser desenhado ou reorganizado. Fixa um vocabulário único, faz o teste da deleção em cada módulo, classifica as dependências em quatro tipos e só cria uma costura quando há dois adaptadores de verdade. Se você quiser ver alternativas, subagentes desenham a interface de três ou mais jeitos bem diferentes e ela compara e recomenda um; senão, segue direto. No fim, os testes passam a morar na interface e os antigos dos módulos rasos saem."></p>

<details><summary>Detalhe técnico</summary>

Módulos fundos (Ousterhout) e costuras (Feathers); 4 categorias de dependência (em processo, substituível local, remota própria com portas e adaptadores, externa com mock); "Design It Twice" com 3+ subagentes em paralelo. Criada por Matt Pocock; aqui só o nome foi traduzido (veja [Créditos](#créditos)).

</details>

### `/cass:writin-skills` — criar, ajustar e testar skills

Ajuda a transformar um processo em skill, acertar quando ela deve ser chamada e testar
se o agente segue suas instruções. Traz as referências e ferramentas da versão local.
É uma ferramenta para cuidar das próprias skills; fica fora do mapa principal de trabalho.

<p align="center"><img src="docs/skill-writin-skills.svg" width="650" alt="A writin-skills entende uso, gatilhos, limites e resultado esperado. Mudanças mecânicas recebem verificação objetiva. Para nova skill ou mudança de comportamento, define cenários, critérios, repetições e limite de correções e congela a versão. RED demonstra uma falha sem a skill ou uma contradição comprovada em skill existente. Escreve ou ajusta, congela a candidata e testa. Falhas voltam ao ajuste dentro do limite; se ele chegar, relata pendências sem aprovar. Depois dos critérios passarem, uma revisão independente confere a candidata; achados procedentes voltam ao ajuste e aos testes afetados. A entrega registra arquivos, resultados e limites."></p>

<details><summary>Detalhe técnico</summary>

RED–GREEN–REFACTOR aplicado a instruções: cenários sem a skill e com ela, versões congeladas
e testes de pressão. Referências de entrevista, formato, descrição e testes acompanham a
skill. Mudanças mecânicas usam verificações objetivas; mudanças de comportamento passam
por testes com critérios e limite de rodadas definidos, mais uma revisão independente.
O renderizador opcional de fluxogramas usa Node.js e Graphviz (`dot`).

</details>

---

## Instalar

**1. O plugin.** No Claude Code, uma linha por vez:

```
/plugin marketplace add cassianodiniz/cass
/plugin install cass@cass
```

Reinicie o Claude Code. As skills aparecem como `/cass:ask-me`, `/cass:spec-plan` etc.

**2. As ferramentas que algumas skills usam por fora.** Um comando no terminal instala o que
dá automático (Mac/Linux; no Windows, pelo Git Bash):

```bash
curl -fsSL https://raw.githubusercontent.com/cassianodiniz/cass/main/install.sh | SKIP_PLUGIN=1 bash
```

Fica manual só o que depende de conta sua: o **`codex login`** (as skills que usam o GPT) e a
conta no **Exa** (a `search`). Detalhe item a item no **[INSTALL.md](INSTALL.md)**.

### Do que cada skill depende

- **Claude Code** — onde as skills rodam.
- **Codex CLI** (≥ 0.156, com `codex login`) — `gpt-implementar`, `gpt-optimizer` e `auto-think`. Sem ele, a `gpt-implementar` para e avisa; a `gpt-optimizer` e a `auto-think` avisam e seguem sem o olhar do GPT, com garantia menor.
- **Exa** — a `search` (e a pesquisa de quem chama a `search`).
- **git** — `implementar`, `gpt-implementar` e `build-review` trabalham num repositório git; o `handoff` se ancora nele quando existe.
- **Python 3** — executa os validadores e o registro de aprendizados de `spec-plan`, `implementar` e `build-review`.
- **GitHub CLI (`gh`, logado)** — a `spec-plan` publica a pasta da feature na branch, cria sua issue e abre a PR em rascunho; a `build-review` marca essa PR pronta com sua autorização.

---

📚 Estas skills nasceram de estudo, não de palpite: o
**[comparativo de modelos de IA](https://claude.ai/artifact/UeTaqkfwazmmBcgRvtFAiM)** que eu uso
pra decidir qual modelo serve pra quê.

**Autoria:** Cassiano Diniz · **Co-autoria:** Tech Club, que forneceu insumos para as skills de
revisão e de implementação (`build-review`, `implementar` e `gpt-implementar`). Histórico de
versões em [CHANGELOG.md](CHANGELOG.md).

## Créditos

A **`otimizar-arquitetura`** é a skill `codebase-design` de **[Matt Pocock](https://github.com/mattpocock/skills)**.
Aqui só o nome foi traduzido. O conteúdo é o original, sob a licença MIT dele
([licença](skills/otimizar-arquitetura/LICENSE) · [créditos](skills/otimizar-arquitetura/CREDITOS.md)).

A **`aprender-com-a-sessao`** é a skill `retro` de **[Matt Pocock](https://github.com/mattpocock/skills)**,
com o guia `writing-for-agents` dele nas referências. Aqui o nome foi traduzido e a skill lê o guia
de dentro da própria pasta. O resto é o original, sob a licença MIT dele
([licença](skills/aprender-com-a-sessao/LICENSE) · [créditos](skills/aprender-com-a-sessao/CREDITOS.md)).

Auditoria anterior do plugin: [achados, verificações e sugestões](docs/auditoria-plugin.md).

A **`spec-plan`**, a **`implementar`** e a **`build-review`** adaptam o fluxo
`tlc-spec-driven v3.3.0` e o núcleo `tlc-spec-lean` de **Felipe Rodrigues (Tech Leads Club)**, sob CC BY 4.0,
e incorporam material de **Matt Pocock**, sob MIT. Créditos e licenças acompanham cada
pasta: [spec-plan](skills/spec-plan/LICENSE), [implementar](skills/implementar/LICENSE)
e [build-review](skills/build-review/LICENSE).
