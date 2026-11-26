# Auditoria do plugin cass — 26/11/2026

## Escopo

Pacote `cassianodiniz/cass`, branch `sync/skills-2026-11-26-readme`, a partir de `4c16bfd`
(`main`). Fonte das skills: o repositório skills-cassiano na `main` de 26/11/2026 (`de1e073cf` e
o commit seguinte, só de arquivo de revisões).

O README, o mapa de skills e os desenhos de `docs/` estavam obsoletos. Eles foram apagados e
refeitos. Esta auditoria não testou o comportamento das skills com agentes; ela confere o pacote.

## O que estava obsoleto

| Encontrado | O que mudou |
|---|---|
| 12 das 13 skills estavam atrás da fonte. A `spec-plan` tinha 29 arquivos diferentes, sem protótipo, sem `tasks.md`, sem `validate_tasks.py` e sem as regras de segurança. | As skills foram copiadas da fonte. Pastas de teste (`evals/`), caches e notas pessoais (`NOTAS.md`) ficaram de fora. |
| As skills `issue` e `oq` não estavam no plugin. | Entraram. O plugin passa a ter 15 skills. |
| O README descrevia o fluxo antigo (só `plan.md` e `checks.md`, sem protótipo, sem tarefas). | README refeito do zero, com 2 fluxogramas em Mermaid e a tabela dos scripts. |
| 15 desenhos SVG em `docs/` mostravam fluxos antigos. | Os desenhos saíram. Os fluxogramas novos estão no README, em Mermaid, e o GitHub os desenha. |
| O `INSTALL.md` pedia o Codex CLI 0.156. O `gpt-6.2-sol` exige o 0.169. | O mínimo passou a 0.169. |
| Os manifestos falavam de 13 skills. | Falam de 15. |

## Ficou de fora, de propósito

| Item | Motivo |
|---|---|
| A versão nova da `search` | A versão local usa a rotação das chaves de pesquisa pessoais e uma pasta pessoal do Google Drive. O plugin é público. A `search` fica na versão anterior. |
| `spec-plan/references/skills/tanstack-query-best-practices` | É escrita para um projeto privado e cita a estrutura interna dele. Os 2 links para ela (`spec-plan/references/investigate.md` e `implementar/references/build.md`) ficam sem destino no plugin. Esses links só valem quando o projeto usa TanStack Query. |
| `spec-plan/references/skills/cloudflare-atlas`, `supabase`, `supabase-postgres-best-practices` e `references/tlc-spec-lean` | Nenhuma instrução das skills cita essas pastas (2,9 MB a menos). |

## Verificação

| Conferência | Método | Resultado |
|---|---|---|
| Manifestos | `claude plugin validate --json .` | ✓ sem erro. Avisos antigos: o campo `contributors` é ignorado, e o plugin não tem ícone. |
| Cabeçalho das skills | `name` igual à pasta e `description` presente | ✓ 15 de 15 |
| Comandos do README | cada `/cass:<nome>` tem pasta, e cada pasta tem comando | ✓ sem diferença |
| Scripts da `spec-plan` | `selftest.py` | ✓ `143 killed, 0 survived, controls ok, tooling ok, baseline clean` |
| Shell | `bash -n` no instalador e nos scripts | ✓ |
| Links locais | busca em todo `.md`, fora dos blocos de código | 2 links da TanStack (acima) sem destino. Os outros 2 avisos são exemplos: `url` na `search` e uma imagem citada no exemplo de plano. |
| Dados pessoais | busca por e-mail, caminhos da máquina e nome do projeto privado | ✓ nada novo. O e-mail do autor nos manifestos já era público. |
| Comportamento das skills com agentes | — | não verificado nesta auditoria. A `spec-plan` nova foi testada na fonte (planejador 15 de 15 na decisão do protótipo). |

## Pendências

1. Decidir se a referência da TanStack entra no plugin numa versão sem o projeto privado, ou se
   os 2 links saem das instruções.
2. Decidir se a `search` ganha uma versão pública, sem as chaves e as pastas pessoais.
3. `writin-skills/references/independent-review.md` ainda cita `gpt-6.1-sol` como padrão do
   script. O script usa `gpt-6.2-sol`. O texto vem da fonte; corrigir lá e sincronizar.
4. Escolher a próxima versão do plugin e atualizar a descrição do repositório no GitHub depois
   do merge.
