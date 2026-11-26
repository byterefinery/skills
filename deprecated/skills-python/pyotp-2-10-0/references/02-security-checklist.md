# pyotp 2.10.0 — Security Checklist

## Table of Contents

- [Secret Storage](#secret-storage)
- [Transport Security](#transport-security)
- [Replay Protection](#replay-protection)
- [Brute-Force Protection](#brute-force-protection)
- [Clock Synchronization](#clock-synchronization)
- [Secret Generation](#secret-generation)
- [Provisioning Best Practices](#provisioning-best-practices)
- [Alternative: WebAuthn](#alternative-webauthn)

---

## Secret Storage

- **Never store raw secrets in plaintext** — hash or encrypt secrets before persisting. A recommended approach: compute `HMAC(server_key, secret)` and store the hash. During verification, reconstruct the OTP from the stored secret (if encrypted) or re-derive from the hash.
- **Use a controlled-access database** — secrets should be in a database with strict access controls, separate from general application data where possible.
- **Encrypt at rest** — if storing raw secrets (e.g., for backup/recovery), use AES-256 or similar with keys managed by a KMS.
- **Never log secrets** — ensure secrets never appear in application logs, error traces, or debug output.
- **Backup recovery codes** — provide users with one-time backup codes in case they lose access to their authenticator app. Store these hashed, not plaintext.

## Transport Security

- **Always use HTTPS** — OTP codes must be transmitted over encrypted connections. The RFCs explicitly require transport confidentiality.
- **Set Secure and HttpOnly flags on session cookies** — prevent JavaScript access and non-HTTPS transmission of session identifiers.
- **HSTS** — enable HTTP Strict Transport Security to prevent downgrade attacks.

## Replay Protection

pyotp does not track which codes have been used. Implement replay protection at the application layer:

### For TOTP

- **Track verified timestamps** — store the most recent verified timestamp (or timecode) per user. Reject any verification attempt with a timecode ≤ the stored value.
- **Store code hashes** — hash verified OTPs and store them. Reject if a submitted code's hash matches a recently verified one.
- **Use `valid_window` conservatively** — a window of 1 (±30 seconds) is sufficient for normal clock drift. Larger windows increase replay risk.

```python
# Example: track last verified timecode
def verify_totp(totp, otp, user_id):
    current_timecode = totp.timecode(datetime.datetime.utcnow())
    last_timecode = get_last_verified_timecode(user_id)

    if current_timecode <= last_timecode:
        return False  # replay attempt

    if totp.verify(otp, valid_window=1):
        save_last_verified_timecode(user_id, current_timecode)
        return True
    return False
```

### For HOTP

- **Track counter state** — store the last accepted counter value per user. Reject any code at a counter ≤ the stored value.
- **Allow a small forward window** — accept codes within a window (e.g., +10 from last counter) to handle out-of-order submissions, but reject anything at or below the last accepted counter.

```python
# Example: HOTP counter tracking
def verify_hotp(hotp, otp, user_id, window=10):
    last_counter = get_last_counter(user_id)

    for i in range(1, window + 1):
        if hotp.verify(otp, last_counter + i):
            save_last_counter(user_id, last_counter + i)
            return True
    return False
```

## Brute-Force Protection

A 6-digit OTP has 1,000,000 possibilities. Brute-force is feasible without rate limiting.

- **Rate-limit verification attempts** — lock the account or require CAPTCHA after N failed attempts (e.g., 5 failures in 5 minutes).
- **Add delays on failure** — exponential backoff on failed verification attempts.
- **Monitor for distributed attacks** — track attempts across multiple IPs for the same account.
- **Use 8-digit codes for high-value accounts** — increases search space to 100 million.

## Clock Synchronization

TOTP depends on accurate server time:

- **Use NTP** — keep server clocks synchronized with NTP (e.g., `chronyd`, `ntpd`).
- **Prefer UTC** — use timezone-aware datetimes with UTC to avoid DST/local time issues.
- **Use `valid_window`** — a window of 1 (±1 interval) handles minor clock drift between server and client.
- **Avoid `datetime.datetime.now()`** — use `datetime.datetime.now(datetime.timezone.utc)` or `datetime.datetime.utcnow()` for UTC-based timecodes.

```python
import datetime

# Correct — UTC-aware
totp.at(datetime.datetime.now(datetime.timezone.utc))

# Correct — explicit UTC timestamp
totp.at(int(time.time()))

# Risky — naive datetime uses local time
totp.at(datetime.datetime.now())
```

## Secret Generation

- **Use `pyotp.random_base32()`** — generates cryptographically secure 160-bit secrets via `secrets.SystemRandom` (or `random.SystemRandom` on older Python).
- **Minimum 32 characters** — shorter secrets reduce entropy. The library enforces this.
- **No padding in secrets** — the `otpauth://` scheme does not use base32 padding. `random_base32()` returns unpadded strings.
- **Avoid predictable secrets** — never use hardcoded, sequential, or user-derived secrets.

## Provisioning Best Practices

- **Include issuer name** — always set `issuer_name` in `provisioning_uri()` so users can identify the app in their authenticator.
- **Use descriptive account names** — include the user's email or username: `name="alice@example.com"`.
- **Validate QR codes before enrollment** — have users enter the code from their authenticator app before marking enrollment complete.
- **Use `valid_window=1` during enrollment** — the user's phone clock may not be perfectly synced.
- **Support multiple authenticators** — allow users to add backup authenticator apps by generating new secrets.
- **Deactivate old secrets on re-enrollment** — when a user re-enrolls, invalidate previous secrets.

## Alternative: WebAuthn

For new applications, consider WebAuthn (FIDO2) instead of or in addition to OTP:

- **Phishing-resistant** — credentials are scoped to the originating domain.
- **No shared secret** — uses asymmetric cryptography, eliminating server-side secret compromise risk.
- **Hardware-backed** — supports security keys, platform authenticators (Touch ID, Windows Hello).
- **PyWARP** — the sister project to pyotp, implementing WebAuthn in Python: <https://github.com/pyauth/pywarp>

## Further Reading

- [RFC 4226 — HOTP Security Requirements](https://tools.ietf.org/html/rfc4226#section-7)
- [RFC 6238 — TOTP Security Considerations](https://tools.ietf.org/html/rfc6238#section-5)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST SP 800-63-3 — Digital Authentication Guidelines](https://pages.nist.gov/800-63-3/)
