# Iterating on an MCP Server from the CLI

A practical guide for developers who want to build and test MCP servers without relying on Claude Code's UI.

---

## Project Structure

```
mcp-starter/
├── server.py          # MCP server — tools, resources, prompts
├── test_resource.py   # CLI test harness (init handshake + method call)
├── notes.json         # Persisted data (auto-created on first note)
├── pyproject.toml     # Dependencies (mcp>=1.27.1)
└── .python-version    # Python version pin (uv reads this)
```

All server logic lives in `server.py`. `notes.json` is the only runtime artifact.

---

## The Edit → Test Loop

MCP servers communicate over **stdio** using JSON-RPC. Claude Code spawns the server as a subprocess and keeps it alive for the session — so changes to `server.py` only take effect after restarting the session.

For fast iteration, bypass Claude entirely: edit `server.py`, then run `test_resource.py` directly.

### 1. Edit `server.py`

Open `server.py` and make your change. Example: adding a new tool.

```python
types.Tool(
    name="count_notes",
    description="Return the total number of saved notes.",
    inputSchema={"type": "object", "properties": {}},
),
```

Then handle it in `call_tool`:

```python
if name == "count_notes":
    return [types.TextContent(type="text", text=f"{len(notes)} notes saved.")]
```

### 2. Test from the CLI

`test_resource.py` shows the pattern: open a subprocess, send the MCP init handshake, then send your method call, and parse the response.

```python
"""Quick test: send MCP init handshake then call a tool."""
import subprocess, json

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2024-11-05",
        "capabilities":{},
        "clientInfo":{"name":"test","version":"0.1"}
    }},
    {"jsonrpc":"2.0","method":"notifications/initialized","params":{}},
    # Your actual call goes here:
    {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
        "name":"count_notes","arguments":{}
    }},
]

proc = subprocess.Popen(
    ["uv", "run", "server.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    cwd="/Users/you/mcp-starter"
)
out, _ = proc.communicate(("\n".join(json.dumps(m) for m in msgs) + "\n").encode(), timeout=5)

for line in out.decode().splitlines():
    if line.strip():
        parsed = json.loads(line)
        if parsed.get("id") == 2:
            print(json.dumps(parsed, indent=2))
```

Run it:

```bash
cd ~/mcp-starter
uv run python test_resource.py
```

---

## MCP Method Reference

| What you want to test | `method` value | `params` keys |
|---|---|---|
| List tools | `tools/list` | _(none)_ |
| Call a tool | `tools/call` | `name`, `arguments` |
| List resources | `resources/list` | _(none)_ |
| Read a resource | `resources/read` | `uri` |
| List prompts | `prompts/list` | _(none)_ |
| Get a prompt | `prompts/get` | `name`, `arguments` |

Always send `initialize` (id=1) + `notifications/initialized` first — the server ignores all other requests until the handshake completes.

---

## Concrete Examples with the Notes Tools

### Call `add_note`

```python
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
    "name":"add_note",
    "arguments":{"title":"hello","body":"world"}
}}
```

Expected response:
```json
{"result": {"content": [{"type": "text", "text": "Saved note #2: hello"}]}}
```

### Read `notes://all` resource

```python
{"jsonrpc":"2.0","id":2,"method":"resources/read","params":{"uri":"notes://all"}}
```

Expected response: JSON array of all notes in `contents[0].text`.

> **Gotcha fixed in this repo:** The MCP SDK passes `uri` as a Pydantic `AnyUrl` object, not a plain `str`. Always cast: `if str(uri) == "notes://all":` — otherwise the comparison silently fails and raises `Unknown resource`.

### Get `summarize_notes` prompt

```python
{"jsonrpc":"2.0","id":2,"method":"prompts/get","params":{"name":"summarize_notes","arguments":{}}}
```

Expected response: a `messages` array with the rendered prompt text.

---

## Restarting in Claude Code

When you're ready to test through Claude:

1. End the current session (`/exit`)
2. Open a new Claude Code session — this restarts all MCP servers
3. The updated `server.py` is now live

There is no in-session restart command.

---

## Adding Dependencies

```bash
cd ~/mcp-starter
uv add <package>        # adds to pyproject.toml + updates uv.lock
uv run server.py        # runs with the new dep available
```

---

## Next Steps

- Add a `search_notes` tool (filter by keyword in title/body)
- Add a `notes://{id}` resource for single-note reads
- Add a `draft_note` prompt that scaffolds a note from a topic
- Explore returning structured JSON inside `TextContent.text` for richer Claude responses
