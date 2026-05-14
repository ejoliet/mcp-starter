# mcp-starter

A minimal MCP (Model Context Protocol) server that demonstrates the three core capability types — **Tools**, **Resources**, and **Prompts** — through a simple notes app.

Use this as a learning template or starting point for building your own MCP server.

## What's inside

| Capability | Name | What it does |
|---|---|---|
| Tool | `add_note` | Save a note with a title and body |
| Tool | `list_notes` | List all note IDs and titles |
| Tool | `delete_note` | Delete a note by ID |
| Resource | `notes://all` | Read full content of all notes as JSON |
| Prompt | `summarize_notes` | Ask Claude to summarize all notes as bullet points |

Notes are persisted to `notes.json` alongside `server.py`.

## Install

### One-liner (bash)

Requires [uv](https://docs.astral.sh/uv/) and [Claude Code](https://claude.ai/code).

```bash
curl -fsSL https://raw.githubusercontent.com/ejoliet/mcp-starter/main/install.sh | bash
```

This clones the repo to `~/mcp-starter`, installs dependencies, and registers the server with Claude Code automatically. Start a new Claude Code session and it's ready.

To install to a custom path:

```bash
MCP_STARTER_DIR=~/dev/mcp-starter curl -fsSL https://raw.githubusercontent.com/ejoliet/mcp-starter/main/install.sh | bash
```

### Docker

Requires [Docker](https://docs.docker.com/get-docker/).

```bash
git clone https://github.com/ejoliet/mcp-starter.git
cd mcp-starter
docker compose up --build
```

Notes are persisted in a named Docker volume (`notes-data`). Register the containerized server with Claude Code:

```bash
claude mcp add mcp-starter -- docker compose -f ~/mcp-starter/docker-compose.yml run --rm mcp-starter
```

### Manual setup

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/), Claude Code.

```bash
git clone https://github.com/ejoliet/mcp-starter.git ~/mcp-starter
cd ~/mcp-starter
uv sync
claude mcp add mcp-starter -- uv --directory ~/mcp-starter run server.py
```

Then start a new Claude Code session — the server will be available automatically.

## Usage in Claude

Once registered, Claude can call tools directly:

> "Add a note titled 'standup' with body 'review PR #42'"  
> "List my notes"  
> "Delete note #1"

Or read the resource and prompt via the MCP panel (`/mcp`).

## CLI development & testing

See [DEV_GUIDE.md](DEV_GUIDE.md) for how to iterate on the server from the terminal without relying on Claude Code.

Quick test:

```bash
uv run python test_resource.py
```

## Project structure

```
mcp-starter/
├── server.py          # MCP server implementation
├── test_resource.py   # CLI test harness
├── install.sh         # Bash one-liner installer
├── Dockerfile         # Container image
├── docker-compose.yml # Compose config
├── pyproject.toml     # Dependencies
└── DEV_GUIDE.md       # Developer iteration guide
```

## Extending

Add a new tool in `server.py`:
1. Append a `types.Tool(...)` entry in `list_tools()`
2. Handle `name == "your_tool"` in `call_tool()`
3. Test with `test_resource.py` before restarting Claude Code
