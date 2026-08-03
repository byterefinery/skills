# MCP Server

## Overview

Docling Serve includes a built-in MCP (Model Communication Protocol) server starting from v1.1.0. The container image provides the `docling-mcp-server` executable — no custom image builds or additional installations needed.

## Starting the MCP server

Override the container entrypoint:

```bash
podman run -p 8000:8000 quay.io/docling-project/docling-serve \
  -- docling-mcp-server --transport streamable-http --port 8000 --host 0.0.0.0
```

The MCP server is accessible at `http://localhost:8000/mcp`.

Key arguments:

| Argument | Description |
|----------|-------------|
| `--transport streamable-http` | HTTP transport for client connections |
| `--port <PORT>` | Port to listen on |
| `--host <HOST>` | Bind address (use `0.0.0.0` for external access) |

## MCP client configuration

Standard JSON configuration for MCP-compatible clients:

```json
{
  "mcpServers": {
    "docling": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Insert this in your client's MCP server configuration section.

### LM Studio

Add the MCP server in LM Studio's MCP configuration settings. Paste the JSON block above into the MCP servers section.

### Claude Desktop

Add the MCP server in the "Custom Model" or "MCP Server" configuration section of Claude Desktop.

### Continue Coding Assistant

Use the same configuration pattern — provide the MCP server URL ending with `/mcp` and ensure the port matches your container setup.

## Docker Compose

```yaml
services:
  docling-mcp:
    image: quay.io/docling-project/docling-serve:1.29.0
    command: ["docling-mcp-server", "--transport", "streamable-http", "--port", "8000", "--host", "0.0.0.0"]
    ports:
      - "8000:8000"
    environment:
      - DOCLING_SERVE_ARTIFACTS_PATH=/models
    volumes:
      - ./models:/models
```

## Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docling-mcp
spec:
  template:
    spec:
      containers:
        - name: mcp
          image: quay.io/docling-project/docling-serve:1.29.0
          command:
            - docling-mcp-server
            - --transport
            - streamable-http
            - --port
            - "8000"
            - --host
            - 0.0.0.0
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: docling-mcp
spec:
  selector:
    app: docling-mcp
  ports:
    - port: 8000
      targetPort: 8000
```

## More information

See the [Docling MCP repository](https://github.com/docling-project/docling-mcp) for the dedicated MCP server implementation and [integration docs](https://github.com/docling-project/docling-mcp/tree/main/docs/integrations).
