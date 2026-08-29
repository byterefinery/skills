# pocketbase 0.39.11 — Authentication

All auth routes live under `/api/collections/{collectionIdOrName}/records` and are only available on **auth collections** (including `_superusers`). Available methods depend on the collection's auth options (identity/password, OTP, OAuth2, MFA), viewable via `GET .../auth-methods`.

## Token model

- Authenticated = valid `Authorization: <JWT>` header (raw token, no `Bearer` prefix needed with the SDKs).
- Stateless: tokens are **not stored server-side**; no logout/revocation endpoints. Token = HS256 JWT signed with the collection's shared secret (`tokenKey` per record). To invalidate issued tokens: change the user's password or the collection's shared auth token secret.
- Successful auth responses: `{"token": "...", "record": {...}}` (record is enriched with the collection's default expands).
- Default auth token duration is **30 min** (per collection `options.authToken.duration`); tokens refresh via `auth-refresh` or SDK `autoRefreshThreshold`.
- Verify an existing token by calling `auth-refresh`.

## Auth endpoints

| Method | Path | Body | Notes |
|---|---|---|---|
| GET | `/records/auth-methods` | — | lists enabled auth methods |
| POST | `/records/auth-with-password` | `identity`, `password`, optional `mfaId` | identity = the configured unique field (default `email`) |
| POST | `/records/auth-with-otp` | `otpId`, `password` (the code), optional `mfaId` | code from the OTP email |
| POST | `/records/request-otp` | `identity` | returns `{"otpId": ...}` even for unknown identity (enumeration protection) |
| POST | `/records/auth-with-oauth2` | `provider`, `code`, `redirectUrl` (server-side flow) | or use the redirect flow below (client-side) |
| GET/POST | `/records/oauth2-redirect` | query: `code`, `state` (client-side redirect flow) | SDKs handle it; the `state` embeds the subscribing realtime client id |
| POST | `/records/auth-refresh` | — (or current token) | returns new token + latest record |
| POST | `/records/{id}/impersonate` | optional `duration` (seconds) | **superuser only**; non-renewable token |

### Email workflows (all on `/records/`)

| Request | Confirm | Body fields |
|---|---|---|
| `request-password-reset` | `confirm-password-reset` | `{identity}` / `{token, password, passwordConfirm}` |
| `request-verification` | `confirm-verification` | `{email}` / `{token}` |
| `request-email-change` | `confirm-email-change` | `{identity, password, email}` / `{token}` |

Email templates are configurable per collection with placeholders (`{{USER_EMAIL}}`, `{{OTP_ID}}`, `{{OTP}}`, token URLs, etc.). On successful OTP login the email is auto-verified.

## MFA (v0.23+)

If enabled, the user must authenticate with **two different** methods (order free):

1. First method (e.g. password) succeeds → **401** with `{"mfaId": "..."}` (MFA session stored in `_mfas`).
2. Second method (e.g. OTP) with `mfaId` added to the body/query → normal auth response.

```js
try {
    await pb.collection('users').authWithPassword(email, pass);
} catch (e) {
    const mfaId = e.response?.mfaId;
    if (!mfaId) throw e;
    const { otpId } = await pb.collection('users').requestOTP(email);
    await pb.collection('users').authWithOTP(otpId, codeFromEmail, { mfaId });
}
```

## Superusers & "API keys"

- `_superusers` bypass all collection rules; OAuth2 is **not** an option for them.
- No traditional API keys. For server-to-server superuser access, generate a **non-renewable impersonate token** (Dashboard > `_superusers` > record > "Impersonate", or `POST /api/collections/_superusers/records/{id}/impersonate`) and store it as a static token. Use with extreme care (full access).
- SDK pattern for a long-lived server superuser client: `pb.authStore.save('YOUR_TOKEN')` or `authWithPassword` with `autoRefreshThreshold`.
