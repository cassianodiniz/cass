# Instalar o plugin `cass` (e o que ele usa por fora)

O plugin `cass` (skills `ask-me`, `spec-plan`, `auto-think`, `implementar`, `gpt-implementar`, `search`, `build-review`, `handoff`, `gpt-optimizer`) **orquestra** ferramentas externas —
ele não empacota elas. Este arquivo reúne tudo que precisa instalar pra ele rodar completo.

A boa notícia: nada disso trava o plugin. Se faltar alguma ferramenta, a skill que depende dela
avisa e segue do jeito que dá.

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
- conta no **Exa** — pra `search`
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
| **Codex CLI** ≥ 0.156 (constrói + revisor `gpt-6.1-sol`) | `gpt-implementar` (constrói a partir da spec), `gpt-optimizer` e `auto-think` (confronto) | Instalar o Codex CLI da OpenAI e logar. Sem ele, o `gpt-implementar` não constrói (o Claude assume, com garantia menor); em risco alto, fica BLOQUEADO até voltar. |
| **Exa** (busca web com procedência) | `search` (pesquisa profunda) | Conta Exa: OAuth no MCP do Exa, ou variável `EXA_API_KEY` (chave grátis em https://dashboard.exa.ai/api-keys). Sem ela, a `search` não roda. |

---

## 3. Opcional

| Ferramenta | Quem usa | Como instalar |
|---|---|---|
| **GitHub CLI** (`gh`, logado com `gh auth login`) | `spec-plan`, `implementar`, `gpt-implementar` e `build-review`, só em projeto que mora no GitHub (plano e partes como issues, PR do plano) | Instalar em https://cli.github.com e logar. Sem ele, use o plano em arquivos, como antes. |
| **context7** (MCP) | `auto-think` e `gpt-optimizer` (documentação oficial atualizada da tecnologia em questão) | Adicionar o MCP context7 conforme seu provedor |
