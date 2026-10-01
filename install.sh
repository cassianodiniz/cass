#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════════
# install.sh — AUTOINSTALL do plugin `cass` e de tudo que ele usa por fora.
#
# Instala SOZINHO (via a CLI `claude` + `npm`):
#   • o próprio plugin cass (marketplace + install)
#   • o Codex CLI (o crítico), se faltar
#
# Uso:
#   bash install.sh                          # instala tudo que dá
#   SKIP_PLUGIN=1 bash install.sh            # não instala o cass (só as deps)
#
# Bootstrap direto do GitHub (numa máquina sem o plugin ainda):
#   curl -fsSL https://raw.githubusercontent.com/cassianodiniz/cass/main/install.sh | bash
#
# Mac/Linux nativo; no Windows, via Git Bash. NÃO roda em PowerShell/cmd.
# ════════════════════════════════════════════════════════════════════════
set -uo pipefail

say()  { printf '%s\n' "$*"; }
ok()   { printf '  ✅ %s\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*"; }
run()  { local d="$1"; shift; say "→ $d"; if "$@"; then ok "$d"; else warn "$d — falhou; veja o INSTALL.md"; fi; say ""; }

say "=== AUTOINSTALL do plugin cass ==="
say ""

# ── Pré-requisitos ──────────────────────────────────────────────────────
HAS_CLAUDE=1; HAS_NPM=1
command -v claude >/dev/null 2>&1 || { HAS_CLAUDE=0; warn "CLI 'claude' não encontrada no PATH — instale o Claude Code primeiro (o /plugin depende dela)."; }
command -v npm    >/dev/null 2>&1 || { HAS_NPM=0;    warn "npm (Node.js) não encontrado — instale o Node (https://nodejs.org). O Codex não vai instalar."; }
say ""

# ── 1. O próprio plugin cass ─────────────────────────────────────────────
if [ "${SKIP_PLUGIN:-0}" != "1" ] && [ "$HAS_CLAUDE" = "1" ]; then
  run "Marketplace cass" claude plugin marketplace add cassianodiniz/cass
  run "Plugin cass"      claude plugin install cass@cass -s user
fi

# ── 2. Codex CLI (o GPT: gpt-6.1-sol) ─────────────────────────────────────
if command -v codex >/dev/null 2>&1; then
  ok "Codex CLI já instalado"; say ""
elif [ "$HAS_NPM" = "1" ]; then
  run "Codex CLI (@openai/codex)" npm install -g @openai/codex
  warn "Falta logar uma vez: rode 'codex login' (interativo). Sem login, auto-think/gpt-optimizer/gpt-implementar caem pro modo reduzido."
  say ""
fi

# ── 3. O que NÃO dá pra automatizar (chave/conta/provedor) ───────────────
say "════════════════════════════════════════════════════════════════"
say "FALTA SÓ O QUE DEPENDE DE CHAVE/CONTA SUA:"
say "  • codex login   → uma vez, interativo (se instalei o Codex agora)"
say "  • conta no Exa  → pra search (chave grátis em https://dashboard.exa.ai/api-keys)"
say "  • MCP context7  → conforme seu provedor (opcional)"
say "════════════════════════════════════════════════════════════════"
say ""
say "Reinicie o Claude Code (ou abra sessão nova) pra carregar o plugin."
