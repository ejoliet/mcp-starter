#!/usr/bin/env bash
# mcp-starter installer
# Usage: curl -fsSL https://raw.githubusercontent.com/ejoliet/mcp-starter/main/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/ejoliet/mcp-starter.git"
INSTALL_DIR="${MCP_STARTER_DIR:-$HOME/mcp-starter}"

# ── helpers ──────────────────────────────────────────────────────────────────
info()  { printf '\033[0;34m[mcp-starter]\033[0m %s\n' "$*"; }
ok()    { printf '\033[0;32m[mcp-starter]\033[0m %s\n' "$*"; }
die()   { printf '\033[0;31m[mcp-starter] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# ── prereqs ──────────────────────────────────────────────────────────────────
command -v git >/dev/null 2>&1  || die "git is required but not found."
command -v uv  >/dev/null 2>&1  || die "uv is required. Install from https://docs.astral.sh/uv/"

# ── clone or update ──────────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    info "Found existing install at $INSTALL_DIR — pulling latest..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    info "Cloning into $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# ── install dependencies ──────────────────────────────────────────────────────
info "Installing Python dependencies..."
uv sync --project "$INSTALL_DIR"

# ── register with Claude Code ─────────────────────────────────────────────────
if command -v claude >/dev/null 2>&1; then
    info "Registering MCP server with Claude Code..."
    claude mcp add mcp-starter -- uv --directory "$INSTALL_DIR" run server.py
    ok "Registered! Start a new Claude Code session to use the server."
else
    info "Claude Code CLI not found — skipping auto-registration."
    info "Once installed, run:"
    printf '    claude mcp add mcp-starter -- uv --directory %s run server.py\n' "$INSTALL_DIR"
fi

ok "Done. mcp-starter installed at $INSTALL_DIR"
