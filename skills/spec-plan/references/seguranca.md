# Segurança

Segurança entra em dois momentos: **no plano**, para o que precisa ser verdade ficar escrito antes do código, e **na construção**, para o código já nascer seguro. A base é a OWASP: a ASVS 5.0 (a lista de verificação de segurança de aplicações web), mais o que o projeto já faz.

## Precedência

O que o projeto decidiu de propósito, registrado no `AGENTS.md`, vence as skills e a ASVS. Um requisito que bate numa dessas decisões é registrado como "decisão do projeto", com a linha do `AGENTS.md`, e não é corrigido. Quem achar que a decisão está errada aponta; não muda sozinho.

## As skills

| Skill | Onde | Momento |
|---|---|---|
| [security-guidance](skills/security-guidance/SKILL.md) | OWASP Agent Skills Project | Plano e construção |

A `security-guidance` cita as referências da ASVS como `references/ASVS/V<capítulo>.md`. Nesta skill elas ficam em [skills/owasp-asvs/references/ASVS/](skills/owasp-asvs/references/ASVS/): leia dali.

## No plano

A coluna `Who` da `Surface` já diz quem pode chamar o quê. O plano acrescenta uma linha de **dados sensíveis**: que dados pessoais ou sensíveis o produto guarda (num CRM, nome, telefone e anotações dos clientes) e onde. É o inventário que a ASVS pede (14.1.1).

O plano que toca entrada de dados, login, autorização, arquivos, API ou dado sensível lê a `security-guidance`: pelo índice dela, acha os capítulos da ASVS que a feature toca e lê só esses. Vale o nível 1 inteiro e o nível 2 de autorização (V8) e proteção de dados (V14). Cada requisito vira um critério, uma pergunta ao usuário, ou "não se aplica" com o motivo. Plano que não toca nada disso não lê.

## Na construção

A fatia que toca entrada de dados, login, autorização, arquivos, API ou dado sensível manda quem constrói ler a `security-guidance`: pelo índice dela, ele acha os capítulos da ASVS que a fatia toca, lê só esses e aplica o nível 1 como mínimo. Requisitos de nível 2 que se aplicam e não foram feitos ficam anotados na fatia. Fatia que não toca nada disso não lê.

A `security-guidance` diz o que cumprir, não como fazer nesta stack: o como vem do `AGENTS.md` e das skills do projeto.
