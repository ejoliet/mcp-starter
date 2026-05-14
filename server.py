"""
MCP Starter Server — teaches Tools, Resources, and Prompts via a simple notes app.

Run directly:  uv run server.py
Register:      claude mcp add mcp-starter -- uv --directory ~/mcp-starter run server.py
"""

import asyncio
import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

NOTES_FILE = Path(__file__).parent / "notes.json"

app = Server("mcp-starter")


# ── helpers ──────────────────────────────────────────────────────────────────

def _load() -> list[dict]:
    if not NOTES_FILE.exists():
        return []
    try:
        return json.loads(NOTES_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []

def _save(notes: list[dict]) -> None:
    NOTES_FILE.write_text(json.dumps(notes, indent=2))

def _next_id(notes: list[dict]) -> int:
    return max((n["id"] for n in notes), default=0) + 1


# ── TOOLS ─────────────────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="add_note",
            description="Save a new note with a title and body.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short title"},
                    "body":  {"type": "string", "description": "Note content"},
                },
                "required": ["title", "body"],
            },
        ),
        types.Tool(
            name="list_notes",
            description="Return all note IDs and titles.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="delete_note",
            description="Delete a note by its numeric ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Note ID to delete"},
                },
                "required": ["id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    notes = _load()

    if name == "add_note":
        note = {"id": _next_id(notes), "title": arguments["title"], "body": arguments["body"]}
        notes.append(note)
        _save(notes)
        return [types.TextContent(type="text", text=f"Saved note #{note['id']}: {note['title']}")]

    if name == "list_notes":
        if not notes:
            return [types.TextContent(type="text", text="No notes yet.")]
        lines = [f"#{n['id']} — {n['title']}" for n in notes]
        return [types.TextContent(type="text", text="\n".join(lines))]

    if name == "delete_note":
        target = int(arguments["id"])
        before = len(notes)
        notes = [n for n in notes if n["id"] != target]
        _save(notes)
        removed = before - len(notes)
        msg = f"Deleted note #{target}." if removed else f"No note with id #{target}."
        return [types.TextContent(type="text", text=msg)]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── RESOURCES ─────────────────────────────────────────────────────────────────

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="notes://all",
            name="All Notes",
            description="Full content of every saved note.",
            mimeType="application/json",
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    if str(uri) == "notes://all":
        return json.dumps(_load(), indent=2)
    raise ValueError(f"Unknown resource: {uri}")


# ── PROMPTS ───────────────────────────────────────────────────────────────────

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="summarize_notes",
            description="Asks Claude to summarize all current notes into bullet points.",
            arguments=[],
        )
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
    if name == "summarize_notes":
        notes = _load()
        if not notes:
            content = "There are no notes saved yet. Tell the user."
        else:
            dump = json.dumps(notes, indent=2)
            content = f"Summarize these notes as concise bullet points:\n\n{dump}"
        return types.GetPromptResult(
            description="Summarize all notes",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=content),
            )],
        )
    raise ValueError(f"Unknown prompt: {name}")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
