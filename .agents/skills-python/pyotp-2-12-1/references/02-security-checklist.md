# pyotp 2.12.1 — Security Checklist

## Table of Contents

- [Secret Strength and Storage](#secret-strength-and-storage)
- [Transport Security](#transport-security)
- [Replay Protection](#replay-protection)
- [Brute-Force Protection](#brute-force-protection)
- [Clock Synchronization](#clock-synchronization)
- [Secret Generation](#secret-generation)
- [Provisioning Best Practices](#provisioning-best-practices)
- [Alternative: WebAuthn](#alternative-webauthn)

---

## Secret Strength and Storage

- **Enforce at least 112 bits** — since 2.12.0, pyotp rejects secrets that decode to fewer than 112 bits (NIST SP 800-63B-4, section 3.1.4.1). The check runs at construction and on every OTP generation/verification. Require 128 bits (RFC 4226 recommendation) or 160 bits by subclassing and overriding `min_secret_length_bits`.
- **Prefer 160-bit secrets** — `pyotp.random_base32()` generates 32-character (160-bit) base32 secrets by default.
- **Never store raw secrets in plaintext** — store hashed or encrypted. A recommended approach: encrypt with a KMS-managed key, or store an HMAC of the secret under a server-side key if the secret only needs to be reconstructable from a backup.
- **Use a controlled-access database** — secrets should live in a database with strict access controls, separate from general application data where possible.
- **Never log secrets** — ensure secrets never appear in application logs, error traces, or debug output.
- **Backup recovery codes** — provide users with one-time backup codes in case they lose access to their authenticator app. Store these hashed, not plaintext.

## Transport Security

- **Always use HTTPS** — OTP codes must be transmitted over encrypted connections. The RFCs explicitly require transport confidentiality.
- **Set Secure and HttpOnly flags on session cookies** — prevent JavaScript access and non-HTTPS transmission of session identifiers.
- **HSTS** — enable HTTP Strict Transport Security to prevent downgrade attacks.

## Replay Protection

pyotp does not track which codes have been used. Implement replay protection at the application layer:

> **Warning (NFKC normalization):** pyotp normalizes submitted OTPs with Unicode NFKC before comparison — `123456` and `１２３４５６` are treated as the same code. Do **not** use the raw submitted OTP, or a hash of that raw value, as the replay-detection key: an attacker could submit another spelling of an already-used code to bypass such a check. Track the accepted counter/timecode instead.

### For TOTP

Use `TOTP.verify_and_get_timecode()` — it returns the matching timecode (the interval the OTP belongs to, not the wall-clock verification time) and raises `pyotp.OTPVerificationError` on mismatch. Persist the timecode per credential in a database shared by all workers; reject timecodes ≤ the last accepted one.

The check and update must be **atomic**, so two concurrent requests cannot both accept the same timecode. Example from the project README (SQLite, table `totp_credentials` with one row per credential, an `id` primary key, and a nullable integer `last_timecode` column initialized to `NULL`):

```python
import pyotp

def verify_totp_once(db, credential_id, totp, otp):
    try:
        matched_timecode = totp.verify_and_get_timecode(otp)
    except pyotp.OTPVerificationError:
        return False

    with db:
        updated = db.execute(
            "UPDATE totp_credentials SET last_timecode = ? "
            "WHERE id = ? AND (last_timecode IS NULL OR last_timecode < ?)",
            (matched_timecode, credential_id, matched_timecode),
        )
    return updated.rowcount == 1
```

Grant authentication only when this returns `True`, after the transaction commits. If you enable `valid_window`, persist the returned matching timecode, which may differ from the server's current timecode.

- **Use `valid_window` conservatively** — a window of 1 (±30 seconds) is sufficient for normal clock drift. Larger windows increase replay risk.

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

- **Throttle login attempts** — per RFC 4226 section 7.3 and NIST SP 800-63B section 3.2.2, rate-limit (and ideally lock out or challenge) failed verification attempts per credential.
- **Add delays on failure** — exponential backoff on failed verification attempts.
- **Monitor for distributed attacks** — track attempts across multiple IPs for the same account.
- **Use 8-digit codes for high-value accounts** — increases search space to 100 million (digits 6–10 are accepted by the library; standard authenticator apps support 6–8).

## Clock Synchronization

TOTP depends on accurate server time:

- **Use NTP** — keep server clocks synchronized with NTP (e.g., `chronyd`, `ntpd`).
- **Prefer Unix timestamps or UTC** — `at()`, `verify()`, and `timecode()` accept Unix timestamps (int/float) and datetimes. Prefer Unix timestamps or timezone-aware UTC datetimes; naive datetimes are interpreted as local time (with `fold` for DST ambiguity).
- **Use `valid_window`** — a window of 1 (±1 interval) handles minor clock drift between server and client.
- **Range limits** — timestamps before the Unix epoch or at/after year 10000 UTC raise `ValueError`.

```python
import time

# Preferred — Unix timestamp (always UTC)
totp.at(1234567890)
totp.verify(code, for_time=int(time.time()))

# Fine — explicit UTC datetime
import datetime
totp.at(datetime.datetime.now(datetime.timezone.utc))

# Risky — naive datetime uses the server's local timezone
totp.at(datetime.datetime.now())
```

## Secret Generation

- **Use `pyotp.random_base32()`** — generates cryptographically secure 160-bit secrets via `secrets.SystemRandom`.
- **Minimum 32 characters from the generator** — `random_base32(length < 32)` raises `ValueError`. The construction floor is 112 bits after decoding; the generator minimum (160 bits) is stricter on purpose.
- **No padding in generated secrets** — the `otpauth://` scheme does not use base32 padding. `random_base32()` returns unpadded strings; `byte_secret()` adds padding internally when decoding.
- **Avoid predictable secrets** — never use hardcoded, sequential, or user-derived secrets.

## Provisioning Best Practices

- **Include issuer name** — always set `issuer_name` in `provisioning_uri()` so users can identify the app in their authenticator.
- **Use descriptive account names** — include the user's email or username: `name="alice@example.com"`.
- **Validate QR codes before enrollment** — have users enter the code from their authenticator app before marking enrollment complete.
- **Use `valid_window=1` during enrollment** — the user's phone clock may not be perfectly synced.
- **Support multiple authenticators** — allow users to add backup authenticator apps by generating new secrets.
- **Deactivate old secrets on re-enrollment** — when a user re-enrolls, invalidate previous secrets.
- **Cap OTP input length** — pyotp's comparison already rejects strings over 1024 code points, but validating `len(otp) <= 10` at the API boundary is still good hygiene.

## Alternative: WebAuthn

For new applications, consider WebAuthn (FIDO2) instead of or in addition to OTP:

- **Phishing-resistant** — credentials are scoped to the originating domain.
- **No shared secret** — uses asymmetric cryptography, eliminating server-side secret compromise risk.
- **Hardware-backed** — supports security keys, platform authenticators (Touch ID, Windows Hello).
- **PyWARP** — the sister project to pyotp, implementing WebAuthn in Python: <https://github.com/pyauth/pywarp>

## Further Reading

- [RFC 4226 — HOTP Security Requirements](https://tools.ietf.org/html/rfc4226#section-7)
- [RFC 6238 — TOTP Security Considerations](https://tools.ietf.org/html/rfc6238#section-5)
- [NIST SP 800-63 Digital Identity Guidelines (800-63-4), incl. 3.1.4/3.1.5](https://pages.nist.gov/800-63-4/)
- [OWASP Authentication Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md)
- [OWASP Multifactor Authentication Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md)
