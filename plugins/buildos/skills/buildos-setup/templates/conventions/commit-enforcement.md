# Commit Enforcement (opt-in)

This is the **one place** BuildOS uses real automation instead of written discipline. It is
a single `commit-msg` git hook that blocks a commit unless its message carries a `Verified:`
trailer naming the flow that was run to verify the change.

It exists because **unenforced discipline degrades the moment a session cuts the corner.**
Every other rule in BuildOS is honored by intention; this one is honored by a hard block.

> Opt-in per project. Pure discipline projects can skip it. Projects that will run sessions
> unattended, or where you don't fully trust every session to self-police, should install it.

---

## What it does — and what it does NOT do (read this; it's the point)

This hook follows BuildOS's own don't-overclaim rule about *itself*:

- **What it does:** forces a conscious attestation at commit time. To commit, you must write a
  `Verified:` line naming the flow you ran. Skipping verification is no longer a silent
  omission — it requires either typing a hollow trailer or explicitly bypassing the hook.
  Both are *conscious choices*, which is exactly the state we want: not "the corner got cut
  silently" but "someone chose to cut it."
- **What it does NOT do:** confirm the verification actually happened. A `commit-msg` hook can
  only check that the *string is present*, not that the work behind it is *true*. `Verified: nothing`
  passes. `git commit --no-verify` skips the hook entirely. Self-attestation is weak.

**So why keep it?** Because converting a silent skip into a conscious lie (or a conscious
bypass) is a real, cheap gain. It's the same shape as the Entry Gate: the gate forces you to
*confront* the floor question without making your answer correct; this hook forces you to
*attest* without making the attestation true. Neither guarantees correctness — both convert
silent skipping into conscious choice. That's the most a commit-time check can honestly claim.

Do not document or describe this hook as more than that. Overclaiming enforcement you don't
have is worse than no hook, because it manufactures false confidence — which is precisely the
failure BuildOS exists to prevent.

---

## The marker

Add a trailer line to the commit message:

```
Verified: <the flow you actually ran>
```

Examples:

```
Verified: ran the end-to-end onboarding flow; new contractor reached /set-password, set a
          password, logged back in with email+password
```
```
Verified: full test suite green (142 passed); manually hit the changed endpoint, 401 on no-auth
```

For changes where there is genuinely nothing to run (pure docs, a comment), say so honestly:

```
Verified: docs only — no executable change
```

---

## Install (opt-in, per project)

The hook ships at `conventions/hooks/commit-msg` (wherever BuildOS placed the conventions
dir in your project — often `docs/buildos/conventions/hooks/commit-msg`).

### Option A — shareable, travels with the repo (recommended)

Point git at a tracked hooks directory so every clone gets it:

```bash
mkdir -p .githooks
cp <path-to>/conventions/hooks/commit-msg .githooks/commit-msg
chmod +x .githooks/commit-msg
git config core.hooksPath .githooks
git add .githooks/commit-msg
```

Commit `.githooks/commit-msg`. Note: each contributor still runs
`git config core.hooksPath .githooks` once locally (git won't auto-trust a hooks path from a
clone — by design).

### Option B — local only, fastest

```bash
cp <path-to>/conventions/hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

Not shared with other clones; lives only in your local `.git/`.

---

## Honest bypass

`git commit --no-verify` skips the hook. That's intentional and fine — it's a *conscious*
bypass, which is the whole design goal. The hook is a speed-bump that makes the choice
explicit, not a wall that makes verification true. If you find yourself reflexively reaching
for `--no-verify`, that's a signal worth heeding, not a workaround to normalize.

---

## Auto-generated commits

The hook skips merge commits (messages beginning with `Merge `) so routine merges aren't
blocked. Everything else requires the marker.
