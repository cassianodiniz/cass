---
name: build-review
description: "Use quando uma feature já construída vai ser revisada antes do merge e já existem a checklist do que foi prometido (`.checks/<feature>.md`), o diff `<base>..HEAD` e a issue/spec original; também com /build-review ou com o sim ao convite do /implementar ou do /gpt-implementar. Não use pra planejar nem construir, nem quando ainda não há checklist."
license: matt-code-review.md e verify.md são cópias verbatim — Matt Pocock (CC-BY-4.0, github.com/mattpocock) e Tech Leads Club (CC-BY-4.0); as demais referências são adaptações locais do TLC Implement (CC-BY-4.0)
---

# Build Review — três revisores sobre o mesmo diff

**Onde entra no fluxo:** roda depois de `/implementar` ou `/gpt-implementar` — que já deixam a checklist `.checks/<feature>.md` e o diff prontos. É o pente-fino final; não planeja nem constrói.

## O que é

Um maestro. Ele **não revisa com texto próprio**: dispara três subagentes independentes sobre o mesmo diff e junta os relatórios sem misturá-los. Os textos que cada subagente segue são cópias verbatim, em `references/` — este arquivo só conduz.

Os três revisores respondem perguntas diferentes, e por isso não se substituem:

- **Standards** (`references/matt-code-review.md`, eixo Standards) — o código segue os padrões documentados da casa + a base fixa de "maus cheiros"? Smell ou preferência é conselho; defeito demonstrado entra no portão.
- **Spec** (`references/matt-code-review.md`, eixo Spec) — o código faz o que a issue pediu? Falta algo, sobrou algo, ou implementou errado?
- **Fiscal** (`references/verify.md`) — cada item da checklist está *provado*? Roda a prova, confere a asserção, e **injeta defeito** pra provar que os testes pegam uma regressão. Devolve PASS/FAIL.

Por que os três juntos: um modelo esperto acha bugs sozinho, mas de forma não-determinística e sem os dentes. Standards e Spec pegam o que o Fiscal não olha (qualidade e escopo); o Fiscal pega o que eles não tocam (prova executável, item a item, à prova de teste decorativo).

## Roda na sessão principal

Os três SÃO subagentes, e subagente não abre subagente. Quem dispara e junta é a **sessão principal**. Se você está dentro de um subagente, pare e devolva pra sessão.

## Antes de tudo: as entradas (portão)

Reúna uma vez, e reparta pra cada revisor a fatia que o texto dele pede:

| Entrada | Quem usa | Como obter |
|---|---|---|
| Ponto fixo `<base>..HEAD` | os três | o commit-marco que a construção deixou: `git log --format=%H --grep="^chore(checks): start <nome do checklist, sem .md>"`. A base é esse commit; confirme com `git rev-parse`. Nenhum marco, ou mais de um → pare e pergunte a base ao usuário. Não deduza pelo histórico: três leituras do mesmo `git log` dão três bases |
| Issue / spec original | Spec, Fiscal | o caminho que o usuário deu, ou a referência no commit |
| Docs de padrão da casa | Standards | `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `CLAUDE.md`/`AGENTS.md` |
| Checklist `.checks/<feature>.md` | Fiscal | a checklist que a construção deixou |

**Sem checklist, o Fiscal não tem o que provar.** Não invente uma nem deixe o Fiscal virar revisão genérica: pare e diga ao usuário que falta a checklist. Sem issue/spec, o eixo Spec e o passo 1 do Fiscal ficam sem âncora — siga com os outros e registre a ausência no relatório.

## Dispara os três em paralelo

Um subagente por revisor, no mesmo turno, cada um com o briefing **verbatim** do seu texto de referência. Não resuma o texto no prompt — aponte o arquivo e passe as entradas.

1. **Standards** — siga `references/matt-code-review.md`, eixo Standards, com a base de maus cheiros colada por inteiro (o subagente não tem outro acesso a ela).
2. **Spec** — siga `references/matt-code-review.md`, eixo Spec, com a issue/spec.
3. **Fiscal** — siga `references/verify.md` do começo ao fim, **todos os passos, incluindo a injeção de defeito**, e inclua verbatim no briefing a resolução local abaixo. Ele recebe a checklist, o diff, a fonte, e roda só leitura (a injeção acontece num `git worktree` isolado, nunca na árvore real).
   - **Force o perfil `standard` no mínimo** (`ui` se a feature tem telas). O `verify.md` assume `light` por padrão, e `light` pula exatamente a injeção de defeito, a enumeração de cobertura e as regras de teste — que são o motivo de existir a build-review. Diga o perfil no prompt do Fiscal; não deixe ele cair no padrão.
   - Ao julgar uma prova entre camadas, esta regra local prevalece sobre instruções ou exemplos contrários de `verify.md`: inspecione somente as dependências necessárias para confirmar o caminho real e o isolamento do comportamento; mutante só morre quando a asserção relevante falha, não quando setup ou outra causa encerra o comando; política explícita e aplicável do repositório continua obrigatória junto da checklist, mas o formato histórico da suíte sozinho não cria uma regra de nível. No relatório, registre `Claim | caminho real (file:line) | input isolado | asserção (file:line) | falha dirigida e saída | branches/entradas exigidas (origem, total e mapa n/n) | veredito`. Inclua todas as linhas de resultado de uma decisão adicionada ou tocada pelo diff, contratos alterados, fontes vinculantes e checklist; decisão preexistente fora desse conjunto não cria prova nova.

O Fiscal faz julgamento pesado (mutação, cobertura) — não rode ele no modelo econômico. Standards e Spec também são julgamento.

## Junta sem misturar

Os três relatórios vão **inteiros**, cada um sob seu título (`## Standards`, `## Spec`, `## Fiscal`), para `.checks/<feature>.review.md`. É lá que os eixos ficam separados e completos.

A mensagem ao usuário É estas quatro partes, nesta ordem, na língua e no nível de quem vai ler:

```
## Veredito
<PASS ou FAIL> — <uma frase: por quê>

## O que não trava
<uma linha por eixo: quantos conselhos e o maior deles>

## O que trava
- <cada defeito que a pessoa veria no uso, UM por linha, em palavras; entre parênteses, quem achou>
- Sem teste que avise se parar de funcionar: <todas as partes que ficam sem proteção, numa linha só, separadas por ponto e vírgula> (<quem achou>)

Relatórios completos: .checks/<feature>.review.md

## O que preciso de você
1. <cada decisão que os relatórios deixaram para o usuário: o que é, em uma frase; (a) … → o que acontece; (b) … → o que acontece; Recomendo (x), porque …> — sem decisão, este item não existe: não escreva "não há decisão"
2. <por último, a próxima ação — ver abaixo>
```

"O que trava" leva todo motivo de FAIL que os relatórios trazem: cada defeito demonstrado por Spec ou Standards e cada lacuna do Fiscal (item sem prova ou com prova parcial, mutante sobrevivente, linha de test-policy não atendida, contradição com o desenho). Um motivo achado por mais de um revisor aparece uma vez, com os nomes de todos. As lacunas de proteção entram todas na linha "Sem teste que avise se parar de funcionar", cada uma nomeada: juntar é só para caber, nenhuma some. O conserto recebe a lista completa do arquivo.

Códigos de item (C21, C33…) e caminhos de arquivo ficam no arquivo e no pedido de conserto, não na mensagem: quem lê a mensagem decide pelo que acontece no app, não pelo número do item.

"O que preciso de você" leva toda decisão que um relatório deixou para o usuário. A única exceção é correção com um só jeito certo e que não muda o app (texto da checklist, nome, comentário): essa vai no conserto sem pergunta; cite em uma linha em "O que não trava" ("vai junto no conserto: …").

A linha "Sem teste que avise…" leva toda lacuna da lista de lacunas do Fiscal (item não provado, prova parcial, mutante sobrevivente, caso sem teste, ponto do desenho que nada confere), esteja ou não ligada a um item da checklist. Sugestão de teste de Spec ou Standards, sem falha apontada ("provavelmente passa"), é conselho e fica em "O que não trava". O que já está listado como defeito de uso não se repete nessa linha.

O último item de "O que preciso de você" é a próxima ação, dizendo quem vai fazer:
- PASS → "Posso subir e abrir a PR?"
- FAIL, construído nesta sessão (`/implementar`; a vistoria roda na mesma sessão por decisão do usuário) → "Posso consertar aqui mesmo, nesta sessão que construiu, numa rodada de conserto?"
- FAIL, construído pelo Codex (`/gpt-implementar`) → "Posso devolver ao Codex, num pedido novo com a lista, para uma rodada de conserto?" — mesmo que as rodadas de conserto dele já tenham acabado.
- FAIL e nada diz quem construiu → pergunte quem construiu, no lugar da pergunta de sim/não.
- FAIL numa vistoria que vem depois de uma rodada de conserto pós-vistoria → não repita a oferta. Pare e dê as saídas como decisão: (a) mais uma rodada com quem construiu → …; (b) consertar nesta sessão → …; (c) aceitar e registrar o que falta → …; Recomendo (x), porque … Esta regra prevalece sobre o limite de três rodadas do `verify.md`.

Só age com o sim. Se não há decisão a tomar, "O que preciso de você" tem só a próxima ação. Nada vem antes do "## Veredito" nem depois da última pergunta: aviso, nota ou resumo extra entram numa das quatro partes ou saem.

Regras da junção:

- **O portão parte do Fiscal e incorpora defeitos demonstrados pelos outros eixos.** É FAIL se o Fiscal falha ou se Spec ou Standards demonstra, com evidência, requisito ausente ou contradito, bug, risco de segurança ou regressão concreta. Smell, preferência, nit, recomendação ou teste adicional sem comportamento distinto ficam não bloqueantes. Na dúvida de classificação, não promova opinião a bloqueio: registre a incerteza e peça decisão.
- **Os eixos ficam separados no arquivo.** Na mensagem, cada defeito que trava diz quem o achou, e "O que não trava" dá o maior conselho de cada eixo, sem eleger um vencedor entre eles.
- **Spec e o passo 1 do Fiscal se encostam** (código×pedido vs checklist×fonte). Achado dobrado às vezes é cobertura, não erro — no arquivo, os dois falam; na mensagem, ele aparece uma vez com os dois nomes.

## Erros comuns

| Erro | Por que quebra |
|---|---|
| Reescrever os três relatórios num só, sem dizer quem achou o quê | apaga a separação de eixos do Matt; é o que um agente sozinho faz por padrão |
| Deixar o Fiscal pular a injeção de defeito | vira uma revisão que aceita teste decorativo (verde que não prova nada) |
| Um smell do Standards reprovar o merge | só defeito demonstrado entra no portão; preferência continua conselho |
| Rodar dentro de um subagente | subagente não abre subagente; os três nascem mortos |
| Resumir os textos de `references/` no prompt | o valor está no texto verbatim; resumir é reintroduzir o buraco |

## Red flags — pare

- "Vou reescrever os três relatórios num texto meu e não guardar os originais"
- "Os testes já passam, não preciso injetar defeito"
- "Não tem commit-marco, mas dá pra deduzir a base pelo git log"
- "Não tem checklist, mas dá pra o Fiscal revisar mesmo assim"
- "Rodo os três em sequência, um de cada vez" (são paralelos, e na sessão principal)
