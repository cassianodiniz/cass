---
name: ask-me
description: Use when the user invokes /ask-me, asks to be interviewed before a task ("me pergunta antes", "me entrevista", "vamos alinhar o que eu quero"), or wants help explaining a still-vague goal before execution. Do not use for a clear execution request that does not ask for this conversation.
---

# /ask-me

Ajude a pessoa a descobrir e explicar o que quer, até chegar a um único prompt fiel e executável. A entrevista, a exploração de possibilidades e a organização do pedido acontecem nesta skill, em qualquer domínio. Outras skills são candidatas à execução final, escolhida pelo usuário.

## Investigar o contexto

Leia o pedido, o histórico e os materiais indicados antes de perguntar. Busque você os fatos acessíveis no projeto, nos arquivos e nas ferramentas; pergunte ao usuário sobre intenção e preferências. Uma fonte ainda não verificada bloqueia apenas as perguntas que dependem dela.

## Descobrir antes de fechar escolhas

Adapte a conversa ao que já está claro:

| Ponto de partida | Próximo movimento |
|---|---|
| O pedido já está suficientemente definido | Reflita o entendimento e prepare o fechamento, sem repetir perguntas. |
| Há uma lacuna importante | Pergunte pelo ponto cuja resposta mais mudaria o resultado. |
| Há apenas um tema ou uma vontade vaga | Comece com uma pergunta aberta, concreta e fácil de responder sobre o que motivou o pedido ou o que a pessoa quer mudar. |
| A pessoa diz "não sei" ou trava | Ajude com situações, exemplos diferentes ou pequenas amostras para ela reagir. As sugestões continuam provisórias. |

Investigue motivos, experiências, dificuldades, referências, limites ou o que tornaria o resultado bom ou frustrante conforme o caso. Cada pergunta nasce do contexto ou da última resposta; isso é território de investigação, não um questionário obrigatório. Explique brevemente o que a resposta muda. "Não sei" e "só tenho o tema" são respostas úteis.

Exemplo: diante de "quero melhorar minhas aulas", descubra o que hoje acontece nas aulas e a pessoa gostaria de mudar, antes de oferecer formatos de aula. Se ela não souber, apresente situações distintas para reconhecer, rejeitar ou acrescentar às suas próprias experiências.

Use perguntas abertas sempre que possam revelar algo que suas opções esconderiam; elas não têm um limite por entrevista. Use alternativas para facilitar uma comparação que já faça sentido ou ajudar quem pediu sugestões. Diga que a pessoa pode responder livremente, combinar sugestões, rejeitar todas ou pedir outros caminhos. Não transforme exemplos numa lista fechada do que ela pode querer.

Compare opções da mesma dimensão: público com público, finalidade com finalidade. Se as opções puderem coexistir, deixe isso explícito. Dê consequências concretas. Recomende uma resposta quando houver fundamento no objetivo, nas restrições ou em fatos; explique o motivo. Quando a preferência ainda for desconhecida, investigue em vez de marcar um palpite como a resposta certa.

## Rodadas curtas

Mantenha perguntas numeradas com alternativas A/B/C como formato principal. Use perguntas abertas para descobrir a intenção e aprofundar o que as alternativas não esclarecerem.

Escreva as perguntas em português e em palavras simples. Faça uma pergunta por vez durante a exploração, ou até quatro perguntas independentes quando isso facilitar responder. Numere todas; alternativas usam letras. Perguntas abertas não precisam de letras nem de recomendação. A pessoa pode responder "1a 2c" ou em suas palavras.

Trabalhe as dependências: uma pergunta cuja resposta depende de outra ainda aberta fica para depois. Preserve decisões confirmadas. Uma reação a uma sugestão pode indicar interesse sem encerrar a decisão; esclareça essa diferença antes de usá-la como compromisso. Novas evidências podem justificar revisitar uma preferência provisória.

A partir da segunda rodada, confira o combinado e os limites já definidos. Interprete-os literalmente. Mostre um lembrete curto dos relevantes à rodada; conflitos vêm primeiro como perguntas numeradas, nomeando o combinado anterior e a informação nova. Resolva o conflito antes das perguntas que dependeriam dele. Não reabra decisões confirmadas sem um motivo concreto.

Separe o que a pessoa disse das suas propostas e suposições. Não trate silêncio como confirmação de uma preferência importante. Deixe escolhas menores e reversíveis para o executor quando não alterarem o resultado combinado; pergunte sobre escolhas que mudem objetivo, escopo, limites ou critérios de sucesso.

## Tornar o pedido concreto

Quando ver um exemplo ajudar mais que uma explicação, mostre uma amostra curta e provisória e peça uma reação livre. Use-a para descobrir preferências, sem produzir a tarefa inteira nem presumir que gostar de uma parte aprova todas as outras.

Organize aqui o necessário para executar: entregas, ordem e dependências relevantes, materiais de entrada e como avaliar o resultado. Para pedidos simples, basta uma descrição curta. Não crie um plano separado ou detalhe cada ação operacional por padrão.

Devolva o entendimento em poucas linhas ao longo da conversa quando houver algo importante a conferir. Encerre quando objetivo, contexto necessário, limites e critérios de sucesso estiverem claros o suficiente para seguir sem inventar decisões importantes. A entrevista não precisa esgotar todos os detalhes. Se a pessoa quiser parar antes, registre as incertezas e respeite o que ela deixou a seu critério.

## Investigar e sugerir skills

Assim que o pedido estiver delimitado e decidido o que o usuário quer fazer, verifique nas skills instaladas se existe alguma que corresponde ao trabalho do usuário: caso haja, sugira a canditada, se houver mais de uma sugira no máximo duas. Não sugira skills caso nenhuma das instaladas se adequar a o pedido. Não procure por skills que não estejam instaladas.

## Fechamento

Entregue, nesta ordem, na mesma mensagem:

1. **Conferi o combinado:** síntese curta do resultado esperado, dos limites e das suposições restantes.
2. **O prompt pra essa tarefa seria:** um único bloco pronto para copiar. Use os campos abaixo conforme a tarefa, omitindo os que não acrescentam informação.
3. As skills de execução verificadas, com uma frase sobre por que se encaixam e o que muda entre elas, seguida do menu de execução ou ajuste.

```text
Objetivo: <resultado pretendido>
Contexto: <para quem, motivação e materiais relevantes>
Pronto quando: <critérios de sucesso combinados>
Fazer: <entregas e decisões confirmadas; ordem e dependências se necessárias>
Preservar: <restrições, valores exatos e referências que precisam acompanhar a execução>
NÃO fazer: <exclusões concretas estabelecidas pelo usuário>
A seu critério: <escolhas que o executor pode resolver sem mudar o combinado>
Suposições: <somente as ainda relevantes, identificadas como tais>
Parar e perguntar: se precisar mudar o objetivo, o escopo, os limites ou os critérios combinados, ou faltar uma informação indispensável; respeitar as autorizações já dadas.
Ao terminar: resumir a entrega e indicar o que não foi possível confirmar.
```

Antes de mostrar o prompt, confira cobertura do combinado, consistência e ambiguidades importantes. Preserve nomes, números, fontes e limites com precisão. Considere situações comuns da tarefa que possam frustrar o objetivo; não invente novas exigências. Corrija o que já estiver resolvido no contexto e pergunte apenas pelas lacunas importantes. O prompt deve carregar as decisões necessárias, sem repetir a conversa inteira ou antecipar toda a execução.

Com uma skill adequada, o menu final é:

```text
📝 Como quer seguir?
 a) Executar este prompt com a skill <nome verificado>
 b) Executar com outra skill — diga qual
 c) Ajustar o prompt — diga o que quer mudar
```

Se houver mais de uma adequada, dê uma letra a cada candidata, seguida de "Executar com outra skill — diga qual" e "Ajustar o prompt — diga o que quer mudar". Recomende com base na compatibilidade verificada; não preencha opções com skills que só tangenciam o pedido.

Se a busca ficar incompleta, mantenha no menu as candidatas adequadas já verificadas e informe a limitação. Se nenhuma candidata adequada tiver sido confirmada, diga exatamente o que foi verificado e ofereça: executar aqui sem skill específica, indicar outra skill ou ajustar o prompt. Diferencie "não encontrei" de "não consegui verificar"; não invente uma candidata nem instale nada automaticamente.

Ao escolher executar, leia a skill escolhida e use o prompt como entrada, preservando as decisões já tomadas, sem pedir uma segunda confirmação da mesma ação. Se o usuário indicar outra skill, localize e confira essa skill antes de executar; se não estiver disponível ou contrariar o pedido, explique o impedimento e peça apenas a escolha necessária.

Um pedido de ajuste reabre somente as decisões afetadas e suas dependências; atualize o prompt, confira de novo a adequação das skills e reapresente o menu. "Pode fechar" pede o fechamento, não a execução. Execute apenas quando a resposta autorizar claramente uma das opções.
