FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source
COPY server.py ./

# notes.json is written to /app/notes.json at runtime
# Mount a host directory to persist notes across container restarts:
#   docker run -v $(pwd)/data:/app mcp-starter
VOLUME ["/app"]

# stdio transport — Claude Code talks to this via stdin/stdout
ENTRYPOINT ["uv", "run", "server.py"]
