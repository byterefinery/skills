# Integrations (docling-mcp 3.5.1)

Connect docling-mcp to MCP clients. Most clients use a common config interface; adding Docling MCP is usually a single `mcpServers` entry.

## Transport selection

The `--transport` flag must match the client:
- **`stdio`** — Claude for Desktop, LM Studio (and other local process-based clients)
- **`sse`** — Llama Stack and SSE-based clients
- **`streamable-http`** — containers and HTTP-based clients; the default transport. Serves on `http://localhost:8000` by default; customize with `--host` and `--port`.

```bash
uvx --from docling-mcp docling-mcp-server --transport stdio
```

## Claude for Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from=docling-mcp", "docling-mcp-server"]
    }
  }
}
```

An example config ships in the repo at `docs/integrations/claude_desktop_config.json`.

## LM Studio

Edit the `mcp.json` file, or use the deep-link install button on the README. For long conversions (e.g., picture description enabled), set the client `timeout` field (in milliseconds) in `mcp.json`:

```json
{
  "mcpServers": {
    "docling": {
      "url": "http://localhost:8000/mcp",
      "timeout": 300000
    }
  }
}
```

## Tool group selection

Pass tool group names to `--tools` (positional). Default is conversion, generation, manipulation. Add `llama-index-rag`, `llama-stack-rag`, or `llama-stack-ie` explicitly to load the optional RAG/extraction groups. Use `--help` to inspect all CLI options.
