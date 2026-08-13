# A2A Security

A2A delegates security to standard web mechanisms. It does not define its own authentication or authorization protocols.

## Transport Security

- **HTTPS required** in production environments
- **TLS 1.2+** recommended with strong cipher suites
- **Server identity verification** — clients validate TLS certificates against trusted CAs

## Authentication

Authentication is handled at the HTTP layer, not within A2A protocol payloads.

### Agent Card Declaration

The server declares supported authentication schemes in its Agent Card:

```json
{
  "securitySchemes": {
    "BearerAuth": {
      "type": "HTTP",
      "scheme": "bearer",
      "bearerFormat": "JWT"
    },
    "ApiKeyAuth": {
      "type": "apiKey",
      "in": "header",
      "name": "X-API-Key"
    }
  },
  "securityRequirements": [
    {"BearerAuth": []}
  ]
}
```

### Supported Security Scheme Types

| Type | Description |
|---|---|
| `APIKeySecurityScheme` | API key in header, query, or cookie |
| `HTTPAuthSecurityScheme` | HTTP auth (Basic, Bearer, Digest) |
| `OAuth2SecurityScheme` | OAuth 2.0 (authorization code, client credentials, device code) |
| `OpenIdConnectSecurityScheme` | OpenID Connect with discovery URL |
| `MutualTlsSecurityScheme` | Mutual TLS with certificate validation |

### Credential Transmission

Credentials go in standard HTTP headers:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
X-API-Key: your-api-key-value
```

### Server-Side Validation

- Server MUST authenticate every incoming request
- Missing/invalid credentials → `401 Unauthorized` (with `WWW-Authenticate` header)
- Valid credentials but insufficient permissions → `403 Forbidden`
- Server MUST NOT reveal existence of resources the client cannot access

### In-Task Authentication

When an agent needs additional credentials during task processing:
1. Agent transitions task to `TASK_STATE_AUTH_REQUIRED`
2. Agent includes a message explaining what credentials are needed
3. Client obtains credentials through out-of-band process (e.g., OAuth flow)
4. Client provides credentials in follow-up message to continue the task

## Authorization

Authorization logic is implementation-specific. Key principles:

- **Granular control** — based on authenticated identity (user, application, or both)
- **Skill-based authorization** — per-skill access control via OAuth scopes
- **Data and action-level authorization** — agent acts as gatekeeper for backend systems
- **Principle of least privilege** — grant only necessary permissions

### Skill-Level Security

Skills can declare their own security requirements:

```json
{
  "skills": [
    {
      "id": "basic-info",
      "name": "Basic Information",
      "description": "Public information lookup",
      "tags": ["info"]
    },
    {
      "id": "financial-data",
      "name": "Financial Data",
      "description": "Access to financial records",
      "tags": ["finance"],
      "securityRequirements": [{"BearerAuth": ["finance:read"]}]
    }
  ]
}
```

## Extended Agent Cards

Authenticated clients can retrieve extended Agent Cards with additional details:

1. Client fetches public Agent Card at `/.well-known/agent-card.json`
2. Checks `capabilities.extendedAgentCard: true`
3. Authenticates using declared security schemes
4. Calls `GET /extendedAgentCard`
5. Replaces cached public card with extended card for session duration

### Session-Scoped Caching

- Extended cards are session-scoped
- Client should use extended card until session ends or card version changes
- Extended card may contain additional skills, capabilities, or configuration

## Data Privacy

- **Sensitivity awareness** — Message and Artifact parts may contain sensitive data
- **Compliance** — adhere to GDPR, CCPA, HIPAA based on domain
- **Data minimization** — avoid unnecessary sensitive information in exchanges
- **Secure handling** — protect data in transit (TLS) and at rest (enterprise policies)

## Tracing and Observability

### Distributed Tracing

- Use OpenTelemetry for trace context propagation
- Propagate W3C Trace Context headers (`traceparent`, `tracestate`)
- Enables end-to-end visibility across agent interactions

### Logging

Log on both client and server:
- `taskId`, `contextId`, correlation IDs
- Trace context for distributed tracing
- Task state changes for auditing

### Metrics

Expose operational metrics:
- Request rates, error rates
- Task processing latency
- Resource utilization

### Auditing

Audit significant events:
- Task creation
- Critical state changes
- Actions involving sensitive data

## API Management

For externally exposed A2A servers, integrate with API Management:

- **Centralized policy enforcement** — auth, rate limiting, quotas
- **Traffic management** — load balancing, routing, mediation
- **Analytics** — usage insights, performance trends
- **Developer portals** — agent discovery, documentation, onboarding

## Agent Card Signatures

Agent Cards can include JWS signatures (RFC 7515) for integrity verification:

```json
{
  "signatures": [
    {
      "protected": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImtleS0xIn0",
      "signature": "dGVzdC1zaWduYXR1cmU",
      "header": {"alg": "ES256", "kid": "key-1"}
    }
  ]
}
```

Clients can verify signatures to ensure the Agent Card hasn't been tampered with.

## Push Notification Security

See [references/04-streaming-push.md](04-streaming-push.md) for detailed push notification security patterns including JWT + JWKS flows.

## Security Best Practices Summary

1. Always use HTTPS in production
2. Validate all authentication credentials on every request
3. Use standard HTTP headers for credentials (never in A2A payloads)
4. Implement skill-level authorization for sensitive capabilities
5. Use extended Agent Cards for authenticated clients
6. Validate webhook URLs to prevent SSRF attacks
7. Implement replay attack prevention for push notifications
8. Propagate trace context for distributed observability
9. Audit significant events (task creation, state changes)
10. Follow principle of least privilege for all access controls
