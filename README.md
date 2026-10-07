# cass — pensar antes de fazer, construir com prova, conferir antes de confiar

Onze skills pra trabalhar com IA no Claude Code sem cair nas armadilhas de sempre: a IA que
sai construindo antes de entender o pedido, que diz "pronto" sem ter testado, que inventa
número de pesquisa. Cada skill resolve um desses momentos e pode ser chamada sozinha.

<p align="center">
  <img src="docs/qual-sua-situacao.svg" width="680" alt="Mapa de porta de entrada, com três jornadas. Sei onde ajustar: direto na spec-plan. Pesquisar ideias: ask-me e depois search. Feature nova: ask-me e depois auto-think. As três seguem pra spec-plan. Com o plano pronto, se ele for grande e complexo, a gpt-optimizer pode atacá-lo antes da obra; em mudança simples, pule direto. Depois, implementar ou gpt-implementar constroem e build-review confere, com volta ao construtor quando reprova. A qualquer momento, handoff. Depois de uma sessão, aprender-com-a-sessao.">
</p>

## Como eu uso no dia a dia

Começo pela situação, não pelo nome da skill ([como instalar](#instalar)):

- 🔧 **Sei onde ajustar:** direto na `/cass:spec-plan`.
- 🔎 **Pesquisar ideias:** `/cass:ask-me` → `/cass:search` → `/cass:spec-plan`.
- 🌱 **Feature nova:** `/cass:ask-me` → `/cass:auto-think` → `/cass:spec-plan`.

Com o plano pronto: `/cass:gpt-optimizer` se o plano for grande (opcional), depois
`/cass:implementar` ou `/cass:gpt-implementar` pra construir e `/cass:build-review` pra
conferir antes de publicar. Conversa ficou longa? `/cass:handoff`. Sessão terminou e a IA
tropeçou? `/cass:aprender-com-a-sessao`.

---

## As skills

Na ordem em que entram no trabalho. Nos desenhos, verde marca onde a skill para e espera você.

### `/cass:ask-me` — antes de mandar uma tarefa

Te entrevista até o pedido ficar claro e entrega um pedido pronto pro agente: o que fazer, o
que não fazer e quando parar e perguntar. Serve pra qualquer tarefa, não só código.

<p align="center"><img src="docs/skill-ask-me.svg" width="520" alt="A ask-me busca os fatos sozinha, faz rodadas de até 4 perguntas com a resposta recomendada, espera você responder e confere cada resposta com os limites que você já deu; enquanto houver decisão em aberto, faz nova rodada. Depois pergunta se fechamos, entrega o pedido pronto pra colar e pergunta se executa ali ou leva pra spec-plan."></p>

<details><summary>Detalhe técnico</summary>

Árvore de decisões resolvida por fronteira, no máximo 4 perguntas por rodada; fatos do ambiente ela busca sozinha; pedido final com Objetivo / Pronto quando / Fazer / NÃO fazer / Parar e perguntar.

</details>

### `/cass:spec-plan` — quando você já sabe o que quer

Transforma uma mudança ou ideia num plano fatiado em partes pequenas, sem dúvida em aberto.
Com um sim, publica o plano: se o projeto está no GitHub, vira uma issue do plano e uma por
parte, ligadas; senão, fica em arquivos. Depois oferece construir o plano inteiro numa sessão.
Se você ainda não sabe a resposta, comece pela `auto-think`.

<p align="center"><img src="docs/skill-spec-plan.svg" width="520" alt="A spec-plan entrevista em rodadas, passa pelos 9 requisitos que ninguém escreve e só segue com o seu sim. Escreve o plano fatiado em partes num rascunho; a mensagem diz em quantas partes, traz as três perguntas de tamanho e onde o plano vai morar. Um sim publica: no GitHub, uma issue do plano e uma por parte, ligadas; sem GitHub, em docs/plans. Depois oferece construir o plano inteiro numa sessão."></p>

<details><summary>Detalhe técnico</summary>

Projeto no GitHub (ou com `docs/agents/issue-tracker.md`): issue do plano + uma por parte como sub-issue, com bloqueio nativo e etiquetas `ready-for-agent`/`ready-for-human`, via `gh`. Sem GitHub: spec + issues em `docs/plans/<plano>/issues/`. Cenários de comportamento; varredura dos "9 esquecidos" (validação, falhas, idempotência...).

</details>

### `/cass:gpt-optimizer` — revisão opcional de um plano grande

O GPT tenta derrubar um plano ou uma decisão que você já tomou e volta com Seguir, Ajustar ou
Bloquear, só com os furos que procedem. Vale em plano grande e complexo; em mudança simples,
pule.

<p align="center"><img src="docs/skill-gpt-optimizer.svg" width="520" alt="A gpt-optimizer monta o alvo com a decisão, o porquê e o estado do código; o GPT tenta derrubar; o Claude filtra cada ponto com prova. Só se o Claude descartou algum ponto, o GPT audita esse filtro numa segunda rodada, e nunca há terceira. Sai Seguir, Ajustar ou Bloquear; se Seguir, oferece levar pra construção com o seu sim."></p>

<details><summary>Detalhe técnico</summary>

Codex `gpt-6.1-sol` esforço `high`, só leitura; a 2ª rodada audita o filtro que o Claude fez dos pontos.

</details>

### `/cass:implementar` e `/cass:gpt-implementar` — construir o plano

As duas entregam o mesmo: o trabalho testado, com a prova de cada item, salvo no seu
computador. Muda quem digita o código. Na `implementar`, o agente da própria conversa
(Claude, Codex ou outro). Na `gpt-implementar`, subagentes GPT no Codex, com o Claude
orquestrando: sai mais barato, porque o trabalho pesado não gasta a sua cota do Claude.

Com uma tarefa só, nada vai pro GitHub sem o seu OK. Com o plano inteiro no GitHub
(`/cass:implementar #<plano>`), um sim cobre tudo: cada parte passa na vistoria e sobe sozinha
pra uma PR em rascunho, e no fim uma revisão do plano inteiro tira a PR do rascunho. O merge é
sempre seu.

<p align="center"><img src="docs/skill-construtoras.svg" width="720" alt="As duas construtoras começam iguais: seu sim pra tarefa, pasta limpa com marco de início e a lista de provas escrita pelo Claude antes do código. Na implementar, o agente da conversa constrói com teste antes do código, anota decisões novas, faz commits e não há fiscal no meio. Na gpt-implementar, o Claude escreve a ordem de serviço, subagentes GPT constroem no Codex, o Claude roda as provas e commita, e um fiscal confere cada asserção; se reprova, volta ao Codex até 2 vezes e depois para e pergunta. As duas terminam no relatório final e oferecem a vistoria com o seu sim."></p>

<details><summary>Detalhe técnico</summary>

- `implementar`: TDD vermelho→verde; checklist em `.checks/` com teste nomeado por item; commits na branch atual; push e PR só com OK.
- `gpt-implementar`: `codex exec` com `gpt-6.1-sol` esforço `medium`; fiscal prova cada item no HEAD; até 2 rodadas de correção, depois o Claude para e pergunta a você, sem consertar sozinho.

</details>

<p align="center"><img src="docs/skill-plano-inteiro.svg" width="520" alt="Com o plano publicado no GitHub, um sim cobre todas as partes. A sessão cria o ramo do plano e, parte por parte, em ordem: marca dono, constrói como uma tarefa, passa na build-review (reprovou: conserta até 2 vezes) e sobe na PR rascunho com bilhete na issue, sem perguntar. Para e chama você numa parte só sua, depois de 2 consertos falhos ou numa decisão fora do plano. No fim, revisão final do plano inteiro; reprovou, volta a quem fez. Aprovada, a PR sai do rascunho e o merge é sempre seu."></p>

<details><summary>Detalhe técnico do plano inteiro</summary>

`/cass:implementar #<plano>` ou `/cass:gpt-implementar #<plano>` lê o plano e as partes com `gh`; ramo `plano/<n>-<nome>`; dono marcado com `gh issue edit --add-assignee @me`; uma PR em rascunho por plano, com `Closes #` do plano e de cada parte; bilhete "Construída e aprovada na vistoria" em cada parte; revisão final desde `git merge-base main HEAD`; `gh pr ready` quando passa. Retomar outro dia: os donos e bilhetes nas issues são pista, o git decide.

</details>

### `/cass:build-review` — vistoria antes de publicar

Três revisores independentes conferem a obra pronta, não a ideia. Volta Aprovado ou
Reprovado, com a prova de cada item.

<p align="center"><img src="docs/skill-build-review.svg" width="600" alt="A build-review reúne o marco de início, o pedido original, a lista de provas e as regras do projeto; sem lista de provas, para. Três revisores trabalham em paralelo sem conversar: Standards confere as regras do projeto, Spec confere se fez o que foi pedido e o Fiscal prova cada item, inclusive estragando o código de propósito. Os relatórios vão inteiros pra um arquivo e sai o veredito. Aprovado: pergunta se pode subir e abrir a PR. Reprovado: pergunta se devolve a quem construiu pra uma rodada de conserto."></p>

<details><summary>Detalhe técnico</summary>

3 subagentes (Standards, Spec, Fiscal) sobre `<marco>..HEAD`; injeção de defeito em `git worktree`; o veredito parte do Fiscal. Quando a issue mora no GitHub: a PR leva `Closes #` do plano e da parte, e a parte aprovada ganha um comentário de bilhete; a issue só fecha no merge.

</details>

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
pronto pra colar na sessão nova.

<p align="center"><img src="docs/skill-handoff.svg" width="520" alt="A handoff confere o git: se algum arquivo desta conversa está sem commit, pede o seu OK pra commitar antes de seguir. Escolhe a âncora, varre a conversa inteira, marca a origem de cada afirmação, salva o documento em .claude/handoffs e entrega um texto pronto pra colar na sessão nova."></p>

<details><summary>Detalhe técnico</summary>

Ancorado num commit: se o trabalho da conversa estiver sem commit, para e pede o commit antes; ao começar do zero algo que surgiu, ancora no ramo principal; cada afirmação marcada `[GIT]`/`[ARQUIVO]`/`[CHAT]`/`[SUPOSIÇÃO]`.

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
- **GitHub CLI (`gh`, logado)** — só quando o projeto mora no GitHub: a `spec-plan` publica o plano e as partes como issues, e a `implementar`, a `gpt-implementar` e a `build-review` leem as issues, marcam dono, deixam o bilhete e cuidam da PR do plano.

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
