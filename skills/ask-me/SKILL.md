---
name: ask-me
description: Use when user invokes /ask-me, or asks to be interviewed before a task ("me pergunta antes", "me entrevista", "vamos alinhar o que eu quero"), especially before handing work to an agent that tends to drift or overdo what was asked.
---

# /ask-me

Interview the user relentlessly until you reach a shared understanding. Map this as a design tree: every decision branches into the decisions that hang off it.

## Rounds

Work the tree in rounds. The frontier is every decision whose prerequisites are already settled: the questions you can ask now without guessing at answers you haven't heard yet. Number each question and give your recommended answer. Then wait for the user's answers before the next round.

A round has at most 4 questions. If the frontier is bigger, ask the 4 whose answers unblock the most of the tree; the rest go to the next round. A decision with an obvious default is not a question: state it as an assumption in one line under the round, and the user corrects it only if wrong. At most one question per interview may be open: a numbered block with no letters and no ✅, where "nada" is a fine answer. Use it for the sample in Shared understanding; if no sample fits the task and you can't write options for what makes the result good without guessing, use it for that, with 2 or 3 examples from what you found.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a later round, not this one. A settled decision is not asked again unless the user reopens it.

From the second round on, every round opens with a check: list each limit the user already set ("nada", "nunca", "só", "fixo", "sem", "fica como está") and, next to it, whether any new answer touches it (✓ or ⚠️). Read limits literally: "nada pode ser apagado" covers empty folders too. When unsure, mark ⚠️ — asking costs one line. Each ⚠️ becomes a numbered question naming both and asking which holds. Before adding any other question to a round with a ⚠️, ask yourself: "if the user picks option a (keep the old rule), does this question still make sense?" If not, it waits for the next round.

Finding facts is your job, never the user's. When a frontier question needs a fact from the environment, repository, tools, or other available sources, find it yourself; don't ask the user for anything you could look up once access is available. Don't block on it: an unresolved fact is an unsettled prerequisite, so only the questions downstream of it wait; ask the rest of the frontier now. The decisions are the user's: put each to them and wait.

Simplicity must never remove required behavior, input validation at trust boundaries, error handling needed to prevent data loss, security requirements, accessibility basics, or anything explicitly agreed with the user.

Write the questions in Portuguese, in plain words (the user is not a programmer).

## Shared understanding

The outcome of the interview is an understanding the user can recognize and correct, grounded in what they want to accomplish.

1. **Discover intent.** Use the request and available context to identify the intended outcome, who it is for, and what success looks like. When that information is missing, ask one focused question about it before proposing features or an approach. Knowing the kind of task does not tell you what the user will accept.
2. **Present a short design.** When the user will judge the result by looking at it (content, design, a rewrite), show in chat a small concrete sample of how it will come out and ask, as the interview's open question, what they would change in it. The test: would the user understand this better by seeing it than reading it?
3. **Write back your understanding.** Summarize the intended outcome, relevant constraints, and success criteria in a short note the user can assess. Separate what they said from assumptions. Invite correction and incorporate their answer before treating this as the brief.
4. **Carry intent into the brief.** Preserve the agreed understanding in the brief, with the success criteria in "Pronto quando". Check every item of the brief against that understanding.

When the request already supplies the purpose and constraints, reflect that understanding instead of asking the same questions again. Keep the note concise; its accuracy and the opportunity to correct it matter.

## Round format

```
Conferi com o combinado:
 ✓ "<limite 1>"
 ⚠️ "<limite 2>" × "<resposta nova>"

⚠️ 1 - Antes você disse "<decisão anterior>", agora "<resposta nova>". Qual vale?
 a) <a anterior>
 b) <a nova>
 c) <as duas, combinadas assim: …>
 ✅ <letra> — <por quê>

📝 2 - <pergunta>
 a) <opção>
 b) <opção>
 c) <opção>
 ✅ <letra recomendada> — <por quê, em uma frase>

📝 3 - <pergunta>
 a) <opção>
 b) <opção>
 ✅ <letra recomendada> — <por quê, em uma frase>

Assumindo (corrija se estiver errado): <padrões óbvios, uma linha cada>
```

Every block that offers lettered options carries a number, the ⚠️ ones included, in one sequence per round (⚠️ first, then 📝). The user answers in short form ("1a 2c") or in their own words, and a block without a number leaves them with a bare letter that could belong to any question.

## Closing

When the frontier is empty and no ⚠️ is open, ask one last question, in a message of its own (after the check, if any, and the note from Shared understanding):

```
📝 Fechamos? Quer que eu transforme isso no pedido pronto pra IA?
 a) Sim, pode gerar
 b) Se quiser alterar ou adicionar algo, é só me falar
```

Use this text as is: two options, no number (it is the only question in the message) and no ✅ line, since the frontier is already empty and there is nothing left to recommend. The closing question goes alone and ends the message; the brief comes only after the user answers "a" to it. If the user answers with a change or an addition instead, the interview is open again: a change is a new answer, and it usually brings decisions of its own that nobody has discussed yet. Recompute the frontier, run the check against the limits already set, and ask as many rounds as it takes, in the usual format, until the frontier is empty again; only then ask the closing question again. Don't fill in what the change implies by guessing just because the interview seemed finished. A "pode fechar" said earlier means it's time to ask the closing question, not to skip it. Then deliver it in one block, ready to paste to the agent. Every item comes from an answer or a stated assumption the user did not correct: if you can't point to where the user said it, it stays out.

```
Objetivo: <o que é pra fazer, em uma frase>
Pronto quando: <linha de chegada verificável, com os critérios de sucesso da nota>
Fazer: <o que foi decidido, em tópicos>
NÃO fazer: <lista específica do que ficou de fora — itens concretos, não "não exagere">
Parar e perguntar: sempre que surgir uma decisão que não está neste pedido, antes de algo irreversível, e quando não der pra seguir sem mim. Na dúvida, pergunte.
Antes de começar: diga em uma linha o que vai fazer.
Se tomar alguma decisão que não está neste pedido, diga em uma linha em que se baseou.
Ao terminar: um resumo curto do que fez; marque o que não conseguiu confirmar e diga onde procurou.
```

Before delivering the brief, look at it with fresh eyes:

1. **Placeholder scan:** Any vague requirement? Fix it.
2. **Internal consistency:** Does any item contradict another, or the agreed understanding?
3. **Ambiguity check:** Could any requirement be interpreted two different ways? If the user's answers settle it, make it explicit; if they don't, ask before delivering.

Fix any issues inline. No need to re-review — just fix and move on.

If the task depends on information spread across several places (Drive, WhatsApp, e-mail, spreadsheets), add this line before "Parar e perguntar":

```
Antes de mexer em qualquer coisa: olhe tudo que pode ser relevante (<os lugares desta tarefa>), inclusive o que o pedido não cita. Se o que encontrar contradisser este pedido, pare e me pergunte.
```

Right after the brief, in the same message, end with one execution question. Pick it with this check: does the brief change code in a repository **and** its "Fazer" list name two or more separate features (for example: login, a trash bin and an export)?

- **No** (one feature, a small edit, or any task outside code: files, spreadsheets, messages, research): ask "Executo aqui agora?"
- **Yes**: ask the question below, because an agent that builds several features in one go tends to skip steps, and /spec-plan slices them into tasks built and tested one at a time:

```
Executo aqui agora, ou levo pra /spec-plan fatiar em tarefas?
 a) Executa aqui
 b) Leva pra /spec-plan
```

Execute only on a yes (or a). On b, invoke /spec-plan and hand it the brief as its input.
