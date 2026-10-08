# Auditoria do plugin cass — 2026-10-08

## Escopo e origem

Auditoria do pacote `cassianodiniz/cass`, branch `codex/atualizar-skills-auditar-plugin`, a partir de `d4a163b9d42a981dc6dd3a4611fb2d2fbaeb194f`.
As fontes de `implementar` e `writin-skills` são as pastas locais de `/Users/cassianodiniz/Skills`, no HEAD `1f7bd31a2fc9985d45f00c042bceeb5d64ed0605`, sem alterações locais nessas duas pastas no momento da cópia.

Foram inspecionados os manifestos, README, instalação, changelog, as 12 skills com suas referências/scripts e os 12 SVGs de `docs/`. Pastas, identidade, versões publicadas, créditos e referências originais foram preservados. A atualização consta como **Não lançado**; não houve instalação, release ou merge.

## Claims

1. As duas skills distribuídas correspondem às versões locais, incluindo arquivos auxiliares.
2. O pacote tem 12 skills, seus comandos documentados existem e seus links locais resolvem.
3. O mapa mantém o fluxo central e inclui os três cartões aprovados, sem a skill de autoria.
4. O guia auxiliar removido não existe mais no pacote nem deixa menções.
5. As verificações de formato e sintaxe passam; o comportamento das skills não é apresentado como testado nesta auditoria.

Risco baixo: cópia de instruções existentes, metadados e artefatos; sem execução dos instaladores ou das rotinas operacionais das skills.

## Ajustes realizados

| Encontrado | Ajuste |
|---|---|
| `implementar` sem a regra local mais recente | Cópia idêntica dos 8 arquivos; decisões do usuário no chat são registradas em `Sources`. |
| `writin-skills` ausente | Inclusão dos 10 arquivos da versão local, sem reescrever suas regras ou reorganizar suas referências. Arquivos `.DS_Store` excluídos. |
| README com 11 skills e catálogo com 10 | Ambos passam a refletir as 12 skills. A skill nova tem seção textual, sem entrar no primeiro infográfico. |
| Handoff e retrospectiva em notas de rodapé; arquitetura ausente do mapa | Três cartões laterais, com os momentos de uso, mantendo os elementos centrais, cores e tipografia. |
| Desenho das construtoras atribuía sempre a checklist ao Claude | Texto passa a dizer agente coordenador, conforme a `implementar` permite. |
| Borda do cartão final de `auto-think` começava fora do SVG | Ajuste de três unidades na posição e seis na largura; fluxo e textos preservados. |
| Instalação dizia que o Claude assumiria o trabalho sem Codex | Documentação e aviso do instalador alinhados ao contrato atual: a `gpt-implementar` para e informa o erro. |
| Instalação tratava conta Exa como obrigatória | Texto esclarece o acesso anônimo limitado já previsto na `search`. |
| Referência original de revisão mandava chamar uma skill não empacotada | Resolução local em `build-review/SKILL.md`: usar a configuração do rastreador do projeto ou pedir a informação faltante. O texto original atribuído a Matt foi preservado. |
| Guia auxiliar fora do escopo atual | Arquivo removido e menção histórica de divulgação retirada. |

## Skills e comandos que parecem ausentes

- Os comandos `/cass:<nome>` da documentação correspondem a pastas presentes.
- A chamada a `/setup-matt-pocock-skills` na referência original não deve ser executada: a resolução local no maestro acompanha o briefing dos revisores. Outras menções a esse nome identificam a origem de citações, não uma dependência operacional.
- `code-review`, `implement-spec`, `to-tickets`, `retro` e `writing-for-agents` aparecem como origem de conteúdo ou nomes históricos. O conteúdo necessário usado pelo fluxo está nas referências empacotadas. Não são comandos adicionais do catálogo.
- `/gpt-builder` continua na descrição de `gpt-implementar` como nome antigo. Não há pasta ou comando independente com esse nome. A lista pública usa `/cass:gpt-implementar`; retirar a compatibilidade semântica da descrição alteraria a ativação da skill e fica pendente.
- Os nomes `superpowers:*`, os arquivos fictícios dos exemplos de organização de skills e `[url]` são exemplos em blocos de código. Não foram tratados como dependências ou links de navegação reais.
- O changelog mantém nomes de skills e arquivos retirados em versões anteriores: é registro histórico, não catálogo de comandos atuais.

## Descrição do GitHub

A descrição consultada no GitHub ainda informa **9 skills**. Esse campo é configuração do repositório e não faz parte do diff; não foi alterado diretamente.

Texto proposto para aplicar após o merge:

> Plugin de Claude Code com 12 skills para planejar, pesquisar, construir com provas, revisar código e criar skills. Por Cassiano Diniz.

A descrição do manifesto foi atualizada na PR para incluir `writin-skills`.

## Verificação

| Claim ou check | Método | Status | Resultado |
|---|---|---|---|
| Cópias completas | Comparação byte a byte de cada arquivo, incluindo inventário | ✓ passed | `implementar`: 8/8; `writin-skills`: 10/10. |
| Manifestos do pacote | `claude plugin validate --json .` | ✓ passed | Exit 0, sem erros. Aviso preexistente: `contributors` é ignorado pelo Claude Code; preservado para manter autoria. |
| Frontmatter | Ruby `YAML.safe_load`, nome igual ao diretório e descrição presente | ✓ passed | 12/12 arquivos válidos; exit 0. |
| Links e imagens locais | Scanner Python de Markdown/HTML, excluindo exemplos em blocos de código, links externos e placeholders | ✓ passed | 61 referências locais válidas antes de adicionar este relatório; nenhuma quebrada. |
| SVGs | Parser XML em todos os SVGs | ✓ passed | 12/12 válidos; exit 0. |
| Infográfico principal | Renderização offline com Sharp, temas claro e escuro, seguida de inspeção visual | ✓ passed | Cartões e textos sem cortes; fluxo central preservado. Renderizações temporárias fora do pacote. |
| Comandos do catálogo | Comparação de cada `/cass:<nome>` documentado com as pastas de skills | ✓ passed | Todos os comandos públicos resolvem. |
| Guia retirado | Ausência do arquivo e busca textual no pacote, excluindo `.git` | ✓ passed | Arquivo e menções ausentes. |
| Bash | `bash -n install.sh skills/_shared/scripts/verify-selo.sh skills/gpt-optimizer/scripts/run-gpt.sh` | ✓ passed | Exit 0; os scripts não foram executados. |
| JavaScript | `node --check skills/writin-skills/render-graphs.js` | ✓ passed | Exit 0. |
| Integridade do diff | `git diff --check` | ✓ passed | Exit 0. |
| Funcionamento das skills com agentes | Cenários de pressão/execução real | ? not verified | Não executados; esta entrega sincroniza conteúdo existente e audita o pacote. Não afirma aprovação comportamental ou revisão independente. |
| Serviços externos e instalação | Codex, Exa, GitHub de um projeto-alvo, instalação em sessão limpa | ? not verified | Não executados. Links externos não tiveram varredura de disponibilidade. |

O validador do Claude Code valida o manifesto; chamar esse comando sobre uma pasta de skills retorna inventário vazio, portanto essa saída não foi usada como prova de frontmatter. A inspeção visual foi offline: abrir o SVG por `file://` no navegador foi bloqueado pela política do navegador. Não houve contorno do bloqueio.

## Sugestões pendentes

1. Criar uma checagem automática de contagem, links e frontmatter no CI, para impedir que README e catálogo fiquem diferentes de novo.
2. Resolver explicitamente a relação entre `otimizar-arquitetura` (substituir testes antigos de módulos rasos) e `implementar` (não apagar/enfraquecer testes sem renegociar). As duas regras permanecem como estão; usar ambas exige autorização clara sobre testes substituídos.
3. Decidir se o nome antigo `/gpt-builder` deve continuar reconhecido na descrição de `gpt-implementar`.
4. Avaliar o papel de `build-review/references/PR.md`, que já constava como não consumido no changelog. Mantido como artefato; conectá-lo ao fluxo é mudança de funcionamento.
5. Depois do merge, escolher a próxima versão do plugin e atualizar a descrição do GitHub. A versão `4.7.0` do manifesto foi preservada, embora o changelog já tenha `4.7.1`; essa discrepância é preexistente e não foi convertida em release por esta PR.
