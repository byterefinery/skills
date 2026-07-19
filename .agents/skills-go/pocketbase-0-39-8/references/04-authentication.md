# 04 — Authentication

## Overview

PocketBase authentication is fully stateless. Tokens are JWTs signed with HS256, not stored on the server. No logout endpoint — clearing the token client-side is logout.

Auth methods per collection (configurable):
- **Password** — email/username + password
- **OTP** — one-time password sent via email
- **OAuth2** — Google, GitHub, Microsoft, etc.
- **MFA** — requires 2 different auth methods

## Password Authentication

```javascript
// JS SDK
const authData = await pb.collection("users").authWithPassword(
    'test@example.com',
    '1234567890'
)
console.log(pb.authStore.isValid)
console.log(pb.authStore.token)
console.log(pb.authStore.record.id)

// Logout
pb.authStore.clear()
```

```go
// Go
user, err := app.FindAuthRecordByEmail("users", "test@example.com")
if err != nil {
    return err
}
token, err := user.NewAuthToken()
```

Identity field defaults to `email` but can be any unique field with a UNIQUE index.

## OTP Authentication

```javascript
// Request OTP
const result = await pb.collection('users').requestOTP('test@example.com')
// result.otpId returned even if user doesn't exist (enumeration protection)

// Authenticate with OTP
const authData = await pb.collection('users').authWithOTP(result.otpId, "EMAIL_CODE")
```

Email template has `{OTP}` and `{OTP_ID}` placeholders.

## OAuth2 Authentication

```javascript
// All-in-one handler (client-side)
const authData = await pb.collection("users").authWithOAuth2({
    provider: "github",       // google, github, microsoft, apple, discord, etc.
    createProfile: true,       // auto-create user if not exists
    redirectUrl: "https://myapp.com/callback",
})
// Redirects user to OAuth2 provider

// Code exchange (server-side or custom flow)
const authData = await pb.collection("users").authWithOAuth2Code(
    "provider",
    "AUTH_CODE",
    "redirectUrl",
    "state",
    true  // createProfile
)
```

OAuth2 providers are configured per auth collection in Dashboard or programmatically. Microsoft provider has extra hardening options for safe email extraction.

## Multi-Factor Authentication (MFA)

```javascript
try {
    await pb.collection('users').authWithPassword('test@example.com', '1234567890')
} catch (err) {
    const mfaId = err.response?.mfaId
    if (!mfaId) throw err  // not MFA

    // Second factor: OTP
    const result = await pb.collection('users').requestOTP('test@example.com')
    await pb.collection('users').authWithOTP(result.otpId, 'EMAIL_CODE', { mfaId })
}
```

MFA stores sessions in `_mfas` system collection. Any 2 different auth methods work.

## Auth Token Refresh

```javascript
// Refresh token (also verifies validity)
const authData = await pb.collection("users").authRefresh()
```

Does not invalidate previously issued tokens. Safe to call from third-party apps.

## User Impersonation

```javascript
// Authenticate as superuser first
await pb.collection("_superusers").authWithPassword("admin@example.com", "pass")

// Impersonate a user (token duration in seconds, optional)
const impersonateClient = await pb.collection("users").impersonate("USER_ID", 3600)
console.log(impersonateClient.authStore.token)
console.log(impersonateClient.authStore.record)

// Use impersonated client
const items = await impersonateClient.collection("articles").getFullList()
```

Impersonate tokens are non-renewable with custom duration.

## API Keys

Use superuser impersonate tokens as API keys for server-to-server communication:

```javascript
// Generate from Dashboard or via API
const pb = new PocketBase('https://example.com')
pb.authStore.save('YOUR_SUPERUSER_TOKEN')

// Or via impersonation API
const token = await pb.collection("_superusers").impersonate("SUPERUSER_ID", 86400)
```

To invalidate: change the superuser password or the shared auth token secret from `_superusers` collection options.

## Verification & Password Reset

```javascript
// Email verification
await pb.collection('users').requestVerification('test@example.com')
await pb.collection('users').confirmVerification(token)

// Password reset
await pb.collection('users').requestPasswordReset('test@example.com')
await pb.collection('users').confirmPasswordReset(token, 'newPassword')

// Email change
await pb.collection('users').requestEmailChange('new@email.com')
await pb.collection('users').confirmEmailChange(token)
```

## Token Types

| Type | Purpose |
|---|---|
| `auth` | Regular auth token |
| `passwordReset` | Password reset |
| `emailChange` | Email change confirmation |
| `verification` | Email verification |
| `file` | Protected file access |

## Auth Collection Options

```go
collection := core.NewAuthCollection("users")

// Password auth
collection.PasswordAuth.Enabled = true
collection.PasswordAuth.IdentityStrictEmail = true

// OTP
collection.OTP.Enabled = true
collection.OTP.Duration = 10 * 60  // 10 minutes

// MFA
collection.MFA.Enabled = true
collection.MFA.Alias = "2fa"

// OAuth2
collection.OAuth2.Enabled = true
collection.OAuth2.Providers = map[string]core.OAuth2ProviderConfig{
    "github": {
        Name:        "GitHub",
        ClientId:    "...",
        ClientSecret: "...",
    },
}

// Tokens
collection.AuthToken.Duration = 21 * 24 * 60 * 60  // 21 days
collection.PasswordResetToken.Duration = 1 * 60 * 60
collection.EmailChangeToken.Duration = 15 * 60
collection.VerificationToken.Duration = 168 * 60 * 60  // 7 days
collection.FileToken.Duration = 5 * 60

// Email templates
collection.VerificationTemplate.Subject = "Verify your email"
collection.VerificationTemplate.Body = "Your code: {verification_code}"
```

## Auth State Access

```go
// In route handlers
isGuest := e.Auth == nil
isSuperuser := e.HasSuperuserAuth()

// Via request info
info, _ := e.RequestInfo()
authRecord := info.Auth
```

```javascript
// In JS hooks
e.requestInfo.auth       // authenticated record or null
e.requestInfo.auth.id    // authenticated user ID
e.hasSuperuserAuth()     // is superuser
```
