---
name: issue
description: Use when the user asks to save a follow-up or deferred task as an issue, including work discovered during implementation, or to break a plan, spec, issue, or conversation into tickets.
---

# Issue (Tarefa/Problema)

Registre o trabalho a ser realizado posteriormente como uma *issue* (tarefa), de modo que qualquer pessoa possa assumi-la com base no contexto fornecido na própria tarefa. Para solicitações de detalhamento (quebra de tarefas), utilize a abordagem de "fatias verticais" (*tracer bullets*) e especifique quais tarefas bloqueiam cada item.

## Processo

### 1. Reunir contexto

Baseie-se no que já está presente no contexto da conversa. Se o usuário fornecer uma referência (caminho de especificação, número de *issue* ou URL), acesse-a e leia todo o seu conteúdo, incluindo comentários.

No caso de um desdobramento, registre onde a questão surgiu (git, branch ou outra fonte), o que foi observado, o que ainda precisa ser feito e, se já for conhecido, como verificar a conclusão. Inclua links relevantes, capturas de tela, logs ou resultados de testes disponíveis. Diferencie observações de possíveis causas.

### 2. Explorar o projeto

Antes de redigir, faça uma busca rápida por issues e PRs abertos que tratem da pendência. Se uma issue já cobrir o mesmo trabalho, use-a para registrar o contexto ou as evidências novas. Se ela já tiver tudo, devolva o link. Se houver trabalho adicional com escopo próprio, prepare uma nova issue e vincule a anterior.
Analise o código relevante sempre que isso ajudar a tornar a *issue* mais precisa. Os títulos e as descrições das tarefas devem utilizar o vocabulário do glossary de domínio do projeto (quando disponível ~/docs/glossary.md) e respeitar as ADRs (*Architecture Decision Records*) pertinentes à área em questão.
Ao elaborar o detalhamento, busque oportunidades para realizar refatorações prévias que facilitem a implementação. "Torne a mudança fácil; depois, faça a mudança fácil."

### 3. Elaborar as tarefas (*tickets*)

Crie uma *issue* para cada desdobramento distinto. Para o detalhamento de uma demanda maior, utilize tarefas no formato de **fatias verticais** (*tracer bullets*).

<vertical-slice-rules>

- Cada fatia percorre um caminho estreito, porém COMPLETO, através de todas as camadas (schema, API, interface, testes), ou seja, uma fatia vertical, e não uma fatia horizontal restrita a uma única camada.
- Uma fatia concluída deve ser passível de demonstração ou verificação de forma independente.
- O escopo de cada fatia deve ser dimensionado para caber em uma única janela de contexto.
- Inclua eventuais refatorações preparatórias antes das tarefas que elas desbloqueiam.

</vertical-slice-rules>

Defina as **dependências de bloqueio** (*blocking edges*) para cada tarefa: indique quais outras tarefas precisam ser concluídas antes que esta possa começar. Uma tarefa sem bloqueios pode ser iniciada imediatamente. **Refatorações de amplo escopo são a exceção à estratégia de fatiamento vertical.** Uma **refatoração de amplo escopo** consiste em uma alteração mecânica (renomear uma coluna, alterar o tipo de um símbolo compartilhado) cujo **raio de impacto** se estende por toda a base de código; assim, uma única modificação quebra milhares de pontos de chamada simultaneamente, impedindo que qualquer fatia vertical seja concluída com sucesso (ou seja, com os testes passando). Não tente forçar isso em uma "tarefa exploratória" (*tracer bullet*); utilize, em vez disso, a sequência **expansão-contração** (*expand-contract*). 
1. Primeiro, a expansão: adicione a nova estrutura ao lado da antiga, garantindo que nada seja quebrado. 
2. Em seguida, migre os pontos de chamada em lotes, definidos pelo raio de impacto (por exemplo, por pacote ou por diretório). Cada lote deve ser uma tarefa própria, dependente da etapa de expansão; isso mantém o CI (Integração Contínua) estável entre um lote e outro, já que a estrutura antiga ainda permanece disponível. 
3. Por fim, a contração: remova a estrutura antiga assim que não restarem mais referências a ela — essa etapa deve ser uma tarefa que depende da conclusão de todos os lotes de migração. Caso não seja possível manter o CI estável nem mesmo nos lotes individuais, mantenha a sequência, mas utilize um *branch* de integração compartilhado. Todas essas tarefas devem, por sua vez, bloquear uma tarefa final de "integração e verificação"; é apenas nessa etapa final que se garante que o sistema esteja funcionando corretamente.

### 4. Revise com o usuário, quando necessário

Quando o usuário solicitar o salvamento de um item específico e o destino estiver claro, prossiga diretamente para a publicação. Considere comandos como "$issue, guarde isso para depois" como uma solicitação de salvamento. Se o usuário pedir um rascunho, apresente-o e interrompa o processo. Caso o item ou o destino sejam ambíguos, faça uma pergunta específica para esclarecer.

Ao propor um detalhamento (quebra de tarefas), apresente-o como uma lista numerada. Para cada tarefa, indique:

- **Título**: um nome curto e descritivo.
- **Dependências** (*Blocked by*): quais outras tarefas (se houver) precisam ser concluídas primeiro.
- **O que entrega**: o comportamento de ponta a ponta que essa tarefa viabiliza.

Pergunte ao usuário:

- A granularidade está adequada? (está muito abrangente ou muito detalhada?)
- As dependências estão corretas? Cada tarefa depende apenas daquelas que são, de fato, pré-requisitos necessários?
- Alguma tarefa deveria ser mesclada ou subdividida ainda mais?

Realize iterações até que o usuário aprove o detalhamento.

### 5. Publique as tarefas

Utilize o repositório remoto (remote) do Git do projeto, desde que ele aponte claramente para um destino no GitHub. Se o destino não estiver claro, solicite confirmação antes de publicar.

- **Arquivos locais** → crie um arquivo por tarefa (ticket) no diretório `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numerando-os a partir de `01` conforme a ordem de dependência (priorizando os bloqueadores). No campo "Blocked by" (Bloqueado por) de cada arquivo, liste os números ou títulos das tarefas das quais ele depende. Utilize o modelo de arquivo por tarefa apresentado abaixo: um arquivo para cada tarefa; nunca agrupe várias tarefas em um único arquivo.
- **Sistema de gerenciamento de tarefas (GitHub, Linear, etc.)** → Se já houver uma issue que cubra a pendência, acrescente o contexto ou as evidências novas. Se ela já tiver tudo, devolva o link. Se nenhuma issue cobrir a pendência, publique uma nova. Ao publicar várias, crie primeiro as que bloqueiam as demais para poder referenciá-las, de modo que as relações de bloqueio possam referenciar identificadores reais. Utilize o recurso nativo de bloqueio da plataforma, caso exista; caso contrário, indique as tarefas bloqueadoras no campo "Blocked by" de cada item. Se estiver subdividindo uma tarefa existente, configure as novas tarefas resultantes como subtarefas (conforme a documentação da plataforma utilizada). Ao publicar uma pendência que ainda precisa ser avaliada, aplique needs-triage ou a etiqueta equivalente do projeto. Se essa etiqueta não existir, publique a issue sem etiqueta de triagem.

Inclua evidências relevantes por meio de links ou breves trechos. Insira capturas de tela disponíveis no corpo da tarefa, utilizando os recursos nativos de anexo da plataforma ou links acessíveis aos leitores. No GitHub, caso a ferramenta de linha de comando `gh` não ofereça suporte a anexos, utilize a interface web (se disponível). Se nenhuma dessas opções for viável, descreva o conteúdo da captura de tela e mencione que ela poderia...