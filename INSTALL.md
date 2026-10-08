# Instalar o plugin `cass` (e o que ele usa por fora)

O plugin `cass` (skills `ask-me`, `spec-plan`, `auto-think`, `implementar`, `gpt-implementar`, `search`, `build-review`, `handoff`, `gpt-optimizer`, `otimizar-arquitetura`, `aprender-com-a-sessao`, `writin-skills`) **orquestra** ferramentas externas —
ele não empacota elas. Este arquivo reúne tudo que precisa instalar pra ele rodar completo.

As dependências variam por skill. Sem Codex, a `gpt-implementar` para e informa o erro;
`auto-think` e `gpt-optimizer` podem seguir com garantia menor, como suas instruções explicam.

---

## 0. Autoinstall — um comando

O `install.sh` instala **tudo que dá** sozinho, via a CLI `claude` (`claude plugin install`) e
`npm`: o próprio plugin cass e o **Codex CLI** (se faltar). Não precisa colar `/plugin` na mão.

**Numa máquina que ainda não tem o plugin** (bootstrap direto do GitHub):
```bash
curl -fsSL https://raw.githubusercontent.com/cassianodiniz/cass/main/install.sh | bash
```

**Se já tem o plugin** (roda da pasta dele, ou peça pro Claude *"roda o install.sh do cass"*):
```bash
bash install.sh                # instala tudo que dá
SKIP_PLUGIN=1 bash install.sh  # só as dependências (não reinstala o cass)
```

**Só sobra o que depende de chave/conta sua** (o script avisa no fim):
- `codex login` — uma vez, interativo (se ele instalou o Codex agora)
- conexão com o **Exa** — pra `search`; conta/chave aumenta o limite do acesso anônimo
- MCP `context7` — conforme seu provedor (opcional)

Depois, **reinicie o Claude Code** pra carregar o plugin. As tabelas abaixo são a referência
item-por-item, caso queira instalar na mão.

---

## 1. Instalar o próprio plugin `cass`

Pelo `/plugin`, adicione o marketplace e instale:

```
/plugin marketplace add cassianodiniz/cass
/plugin install cass@cass
```

Depois as skills ficam disponíveis como `/cass:ask-me`, `/cass:gpt-implementar`, `/cass:handoff` e assim por diante.

> Instalou o antigo `Titan` pelo catálogo `cassiano.diniz`? Esse catálogo saiu do ar. Remova com
> `/plugin uninstall Titan@cassiano.diniz` e `/plugin marketplace remove cassiano.diniz`, e instale o `cass` acima.

---

## 2. Críticas (a skill que usa perde a função principal sem elas)

| Ferramenta | Quem usa | Como instalar |
|---|---|---|
| **Codex CLI** ≥ 0.156 (constrói + revisor `gpt-6.1-sol`) | `gpt-implementar` (constrói a partir da spec), `gpt-optimizer` e `auto-think` (confronto) | Instalar o Codex CLI da OpenAI e logar. Sem ele, a `gpt-implementar` para e informa o erro; não troca o construtor automaticamente. |
| **Exa** (busca web com procedência) | `search` (pesquisa profunda) | Conta Exa: OAuth no MCP do Exa, ou variável `EXA_API_KEY` (chave grátis em https://dashboard.exa.ai/api-keys). Acesso anônimo também funciona, com limite de chamadas. Erro de autenticação ou limite é informado; não há troca automática por outra busca. |

---

## 3. Opcional

| Ferramenta | Quem usa | Como instalar |
|---|---|---|
| **GitHub CLI** (`gh`, logado com `gh auth login`) | `spec-plan`, `implementar`, `gpt-implementar` e `build-review`, só em projeto que mora no GitHub (plano e partes como issues, PR do plano) | Instalar em https://cli.github.com e logar. Sem ele, use o plano em arquivos, como antes. |
| **context7** (MCP) | `auto-think` e `gpt-optimizer` (documentação oficial atualizada da tecnologia em questão) | Adicionar o MCP context7 conforme seu provedor |

O renderizador opcional `node skills/writin-skills/render-graphs.js <pasta-da-skill>` usa Node.js e Graphviz (`dot`). Eles só são necessários para gerar SVGs a partir de blocos DOT. Os testes de pressão da skill usam subagentes disponíveis no agente anfitrião.
