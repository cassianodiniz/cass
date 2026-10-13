---
name: handoff
description: "Use quando o usuário disser /handoff, \"gera um handoff\", \"vou limpar o contexto\", \"passa isso pra uma sessão nova\", \"documento de continuação\", \"resume pra eu continuar depois\", \"tô chegando no limite de contexto\", ou quando uma conversa longa vai terminar e ele quer retomar o trabalho — ou começar do zero algo que surgiu nela — numa sessão nova, sem o histórico da conversa."
---

# Handoff

Escreva um documento para um agente sem o histórico desta conversa conseguir continuar o trabalho. Adapte o conteúdo ao foco pedido pelo usuário.

Se houver Git, confira o estado do repositório e separe as mudanças deste trabalho das demais. Havendo mudanças deste trabalho sem commit, mostre quais entrariam e proponha uma mensagem; pergunte se o usuário quer commitar antes do handoff e aguarde a resposta. Se ele já respondeu, siga essa decisão. Sem mudanças deste trabalho, siga direto para o handoff.

Se aceitar, faça commit somente das mudanças deste trabalho, preservando as demais, inclusive o que já estava staged. Depois faça o handoff. Se recusar, faça o handoff sem commit. Se o commit falhar, registre a falha e faça o handoff com as mudanças ainda pendentes; não contorne a falha nem entre em um ciclo de tentativas.

No documento, registre a branch e o hash do HEAD conferidos após essa decisão. Identifique as mudanças relevantes que continuam fora desse commit e o trabalho de outra frente que deve ser preservado. O hash é o ponto de referência; mudanças sem commit precisam dos arquivos locais. Se não houver Git ou ainda não existir commit, informe isso sem inventar uma âncora.

Preserve o contexto que só existe na conversa: objetivo, decisões vigentes e seus motivos relevantes, limites do usuário, ponto de parada e pendências. Referencie por caminho ou URL o que já está em planos, arquivos, issues e outros artefatos; não reproduza esse conteúdo.

Distinga fatos confirmados, decisões do usuário, sugestões do agente e lacunas. Preserve valores, nomes e comandos sem mudar seu sentido. Decisões revogadas não valem como instruções atuais. Se parte do contexto não estiver disponível, registre o que falta sem reconstruir por suposição. Não inclua segredos ou dados pessoais sensíveis.

Use somente as seções que ajudam a continuar. Antes de salvar, confira se não perdeu uma decisão relevante nem acrescentou algo sem base.

Salve na pasta do trabalho em `.claude/handoffs/handoff-AAAA-MM-DD-HHMMSS.md`. Entregue uma frase curta colável com o caminho absoluto real do arquivo e a instrução para o próximo agente lê-lo e continuar. Se não conseguir salvar, entregue o texto no chat e informe a falha.
