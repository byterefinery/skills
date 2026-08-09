# Authorization

MCP provides an authorization framework for HTTP-based transports. Implementations using HTTP SHOULD conform to this specification. STDIO transport implementations SHOULD NOT follow this specification and should retrieve credentials from the environment instead.

## Overview

MCP's authorization framework is built on OAuth 2.0 and OpenID Connect. It supports:

- OAuth 2.0 authorization code flow with PKCE
- OpenID Connect discovery
- Client registration (Client ID Metadata Documents, with RFC 7591 as fallback)
- Token management and refresh

## Authorization Flow

### Step 1: Discover Authorization Server

The client discovers the authorization server via the MCP server's metadata:

```
GET /.well-known/mcp-authorize
```

Response includes:

- `issuer` — authorization server issuer identifier
- `authorization_endpoint` — OAuth authorization endpoint
- `token_endpoint` — OAuth token endpoint
- `registration_endpoint` — optional dynamic client registration endpoint
- Other standard OIDC discovery fields

### Step 2: Client Registration

**Preferred**: Client ID Metadata Documents — the client provides a metadata document URL, and the authorization server fetches it.

**Fallback**: OAuth 2.0 Dynamic Client Registration (RFC 7591) — remains available for authorization servers that don't support Client ID Metadata Documents.

Clients MUST specify an appropriate `application_type` during registration to avoid OpenID Connect redirect URI conflicts.

### Step 3: Authorization Request

The client redirects the user to the authorization endpoint:

```
GET {authorization_endpoint}?
  response_type=code&
  client_id={client_id}&
  redirect_uri={redirect_uri}&
  scope={scopes}&
  code_challenge={pkce_challenge}&
  code_challenge_method=S256&
  state={random_state}
```

### Step 4: Token Exchange

After user authorization, the client exchanges the code for tokens:

```
POST {token_endpoint}
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code={authorization_code}&
redirect_uri={redirect_uri}&
code_verifier={pkce_verifier}&
client_id={client_id}
```

### Issuer Validation

- Authorization servers SHOULD include the `iss` parameter in authorization responses per RFC 9207
- MCP clients MUST validate a present `iss` against the recorded issuer before redeeming the authorization code

## Credential Management

- Client credentials are bound to the authorization server that issued them
- Clients MUST key persisted credentials by the issuer identifier
- Clients MUST NOT reuse credentials with a different authorization server
- Clients MUST re-register when the authorization server changes

## Token Refresh

MCP supports token refresh via the standard OAuth 2.0 refresh token flow. Clients should implement automatic token refresh to maintain seamless connectivity.

## STDIO Transport

For STDIO transport, credentials are retrieved from the environment rather than through the OAuth flow. The client is responsible for obtaining and providing credentials to the server process.

## Security Considerations

1. **PKCE is mandatory** — all authorization requests must use Proof Key for Code Exchange
2. **State parameter** — must be used to prevent CSRF attacks
3. **Issuer validation** — clients must verify the issuer matches the expected authorization server
4. **Token storage** — access tokens and refresh tokens must be stored securely
5. **Scope minimization** — request only the scopes needed for the operation
6. **Credential isolation** — credentials must not be shared between different authorization servers
