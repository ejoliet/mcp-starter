"""Quick test: send MCP init handshake then read notes://all resource."""
import subprocess, json

msgs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2024-11-05",
        "capabilities":{},
        "clientInfo":{"name":"test","version":"0.1"}
    }},
    {"jsonrpc":"2.0","method":"notifications/initialized","params":{}},
    {"jsonrpc":"2.0","id":2,"method":"resources/read","params":{"uri":"notes://all"}},
]

proc = subprocess.Popen(
    ["uv", "run", "server.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    cwd="/Users/ejoliet/mcp-starter"
)

stdin = "\n".join(json.dumps(m) for m in msgs) + "\n"
out, _ = proc.communicate(stdin.encode(), timeout=5)

for line in out.decode().splitlines():
    if line.strip():
        parsed = json.loads(line)
        if parsed.get("id") == 2:
            print("RESULT:", json.dumps(parsed, indent=2))
