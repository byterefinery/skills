# MCP Server

The `docling-serve` container image ships the full MCP (Model Context Protocol) stack — no custom builds or extra installs. Override the entrypoint to run `docling-mcp-server` instead of the API.

## Launching

```sh
podman run -p 8000:8000 quay.io/docling-project/docling-serve \
  -- docling-mcp-server --transport streamable-http --port 8000 --host 0.0.0.0
```

The MCP endpoint is then at `http://localhost:8000/mcp`. Key arguments: `--transport streamable-http`, `--port <PORT>`, `--host <HOST>` (`0.0.0.0` to accept external connections).

## Client configuration

Standard MCP client JSON (LM Studio, Claude Desktop, Continue, etc.):

```json
{
  "mcpServers": {
    "docling": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Update the URL/port to match your deployment. See the [Docling MCP docs](https://github.com/docling-project/docling-mcp/tree/main/docs/integrations) for client-specific instructions.
