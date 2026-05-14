# mcp-starter — Claude Code context

## Project purpose
Minimal MCP server teaching the three core capability types (Tools, Resources, Prompts) via a notes app.
Used as a learning template and distribution-ready starter for building MCP servers.

## Tech stack
- Python 3.12+, `uv` for dependency management
- `mcp` SDK (`mcp>=1.27.1`)
- stdio transport (Claude Code registers via `claude mcp add`)

## Key files
| File | Role |
|---|---|
| `server.py` | MCP server — all tools, resources, and prompts |
| `test_resource.py` | CLI test harness (no Claude needed) |
| `pyproject.toml` | Dependencies |
| `install.sh` | Bash one-liner installer |
| `Dockerfile` / `docker-compose.yml` | Containerized distribution |
| `DEV_GUIDE.md` | Dev iteration guide |

## Commands
```bash
uv sync                        # install deps
uv run server.py               # run server directly (for debugging)
uv run python test_resource.py # run CLI tests
ruff check .                   # lint
pytest                         # tests
```

## Register with Claude Code
```bash
claude mcp add mcp-starter -- uv --directory ~/mcp-starter run server.py
```

## Runtime data
`notes.json` is auto-created at runtime and is gitignored — do not commit it.

## Distribution
- **Bash**: `curl -fsSL https://raw.githubusercontent.com/ejoliet/mcp-starter/main/install.sh | bash`
- **Docker**: `docker compose up` (stdio bridge via `docker-compose.yml`)

## Extending the server
1. Add a `types.Tool(...)` entry in `list_tools()`
2. Handle the new name in `call_tool()`
3. Verify with `test_resource.py` before restarting Claude Code

## What to ignore in future sessions
`.omc/`, `.claude/`, `.agents/`, `.venv/`, `notes.json` are all local/runtime — never commit them.
