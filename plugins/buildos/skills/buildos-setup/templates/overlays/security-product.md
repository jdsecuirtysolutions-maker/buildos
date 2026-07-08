# Overlay: Security-Sensitive Product

Include this overlay when the project handles credentials, customer data, or is itself a
security tool. The bar is higher than a typical app: a security bug in a security product
is a P0, and overclaiming a protection you don't have is a credibility (and liability) risk.

---

## Elevated security requirements

| Threat | Prevention | Priority |
|--------|------------|----------|
| Secret/credential exposure | All secrets in env vars. Never log full keys/tokens. Never return them in responses. Audit every endpoint that could leak one. | CRITICAL |
| Unauthenticated endpoints | Every endpoint requires auth (token/JWT/session). No exceptions except a health check. | CRITICAL |
| Injection (SQL/command/etc.) | Parameterized queries only. Never string-concat user input into queries or shells. | HIGH |
| XSS / output injection | Framework escaping by default. Never render unsanitized user content. | HIGH |
| CSRF | Protect state-changing form endpoints; token-auth APIs exempt by design (document which and why). | HIGH |
| Sending sensitive data to third parties | Off by default. Any external transmission is opt-in, configured by the owner, and clearly disclosed. | CRITICAL |
| Webhook/inbound tampering | Verify signatures (HMAC or equivalent) on all inbound webhooks. | HIGH |
| Dependency supply chain | Pin versions. Vet new deps for reputation. Minimize dependency count. | MEDIUM |

## Before any commit in a security context

1. No secrets in code, logs, or test fixtures.
2. Every touched endpoint still requires auth (prove the unauthenticated case is rejected).
3. No sensitive data leaves the system without explicit, disclosed opt-in.
4. Run the test suite.

## Flag security issues immediately

If you spot one, surface it with **severity (Critical/High/Medium/Low)** and a suggested
fix, even if it's outside the current task. In a security product, this is never "out of scope."

## Honesty about coverage (the overclaim trap)

Security products live or die on trust. Do not let docs, demos, or pitches claim a
protection the code doesn't actually deliver.

- **"Engine built" ≠ "feature live."** If a capability exists as a library/API but isn't
  wired into the real flow, it does NOT protect anyone yet. Say so. (Classic example: an
  attribution/watermark engine that exists but is never invoked during the real operation.)
- **State the honest boundary.** What the system does NOT defend against is part of the
  spec, not a weakness to hide. ("We raise the bar and ensure attribution; we don't claim
  to stop a root-level attacker.")
- When validating a demo or pitch claim, **verify it against the actual code path**, not the
  commit message or the design doc. Move anything unverified into "roadmap," framed plainly.

## Threat-model the user, not just the attacker

If the product constrains a user (contractor, employee, agent), remember they're a user too:
overly invasive controls get bypassed or refused. The most secure control is one people
actually keep installed. Coverage that ships beats perfect coverage nobody adopts.
