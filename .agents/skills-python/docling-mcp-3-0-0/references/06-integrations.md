# Integrations

## Overview

Docling MCP integrates with any MCP-compatible client. This reference covers the most common integration patterns and transport selection.

## Transport Selection

Choose the transport based on how the client connects to the server:

| Transport | Protocol | Use Case | Clients |
|---|---|---|---|
| `stdio` | Standard I/O | Local process, parent-child communication | Claude Desktop, LM Studio, Cursor |
| `sse` | Server-Sent Events | Event stream over HTTP | Llama Stack, custom SSE clients |
| `streamable-http` | HTTP with streaming | Containers, remote services, HTTP clients | Custom HTTP clients, containers |

### stdio

The server reads from stdin and writes to stdout. Used when the MCP client spawns the server as a child process.

```bash
uvx --from docling-mcp docling-mcp-server --transport stdio
```

This is the most common setup for desktop clients. The client manages the process lifecycle.

### SSE

The server exposes an SSE endpoint. The client connects via HTTP and receives events.

```bash
uvx --from docling-mcp docling-mcp-server --transport sse --host localhost --port 8000
```

### Streamable HTTP

Full HTTP server with streaming support. The default transport.

```bash
uvx --from docling-mcp docling-mcp-server --transport streamable-http --host 0.0.0.0 --port 8000
```

## Claude Desktop

1. Install `docling-mcp` or use `uvx` directly
2. Edit `claude_desktop_config.json` (location varies by OS):
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from=docling-mcp", "docling-mcp-server"],
      "env": {
        "DOCLING_MCP_CONVERSION_MODE": "remote",
        "DOCLING_MCP_SERVICE_URL": "https://your-docling-service.example.com",
        "DOCLING_MCP_SERVICE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

3. Restart Claude Desktop

## LM Studio

1. Open LM Studio
2. Go to the MCP settings
3. Add a new MCP server with:
   - Command: `uvx`
   - Args: `--from=docling-mcp docling-mcp-server`
   - Env: add `DOCLING_MCP_*` variables as needed

Alternatively, use the direct install button from the MCP registry page.

## Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from=docling-mcp", "docling-mcp-server"],
      "env": {
        "DOCLING_MCP_CONVERSION_MODE": "local"
      }
    }
  }
}
```

## Container Deployment

```dockerfile
FROM python:3.12-slim
RUN pip install docling-mcp[local]
ENV DOCLING_MCP_CONVERSION_MODE=local
CMD ["docling-mcp-server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
```

## Gotchas

- **`uvx` must be on PATH** — the MCP client spawns `uvx` as a subprocess. Ensure `uv` is installed and accessible.
- **`stdio` transport is process-bound** — the server lives as long as the client process. If the client crashes, the server dies too.
- **`streamable-http` binds to localhost by default** — use `--host 0.0.0.0` for container/network access.
- **Environment variables must reach the server** — when using `uvx`, env vars are passed through the MCP client's `env` block or inherited from the parent process.
- **`--transport` is positional** — it must come before other arguments or use `--transport <type>` syntax.
- **Port conflicts** — if `localhost:8000` is in use, change with `--port <number>`.
- **MCP SDK version mismatch** — ensure your MCP client supports SDK v2+. Docling MCP v3 requires `mcp>=2.0.0`.
