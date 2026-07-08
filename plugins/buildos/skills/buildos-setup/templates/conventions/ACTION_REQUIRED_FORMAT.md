# Action Required Format

When the owner must do something outside of code — deploy, set a secret, configure a
service, create an account, click through a console, run an interactive command — hand it
off in this format. The goal: a non-developer (or a developer in a hurry) can execute it
without guessing, and knows immediately whether it worked.

---

## The format

```
## Action Required: <Task Name>

**What:** <one-sentence explanation>
**Why:** <why this is necessary for the project>

**Steps:**
1. <first step, exact clicks/commands>
   - Expected result: <what you should see>
2. <second step>
   - Expected result: <what you should see>

**Verification:** <how to confirm the whole thing worked — a command, a screen, a value>

**If something goes wrong:**
- Issue: <common problem> → Solution: <fix>
- Issue: <another> → Solution: <fix>
```

---

## Rules that make it actually usable

- **Exact, not approximate.** "Go to the Variables tab and add `FOO=bar`," not "set the
  env var." Name the screen, the button, the field.
- **Expected result after each step.** The person needs to know they're on track before
  moving on — this is the per-step verify.
- **One verification at the end** that proves the goal, ideally a command whose output is
  unambiguous.
- **Anticipate the top 2-3 failure modes** with their fixes. These come from having done it
  before or reasoning about what's brittle.
- **Flag prerequisites and ordering.** If step 3 needs an ID produced in step 1, say so.
- **Mark secrets handling.** Where a value is sensitive, say "treat like a password — don't
  paste into chat/commits."

## When the owner must run an interactive command themselves

Some steps can't be done for them (interactive logins, browser auth, machine-local config).
Call these out explicitly and, where the environment supports it, tell them the exact command
to run themselves rather than describing it vaguely.

## Why this format earns its keep

It removes the slowest, most error-prone part of solo + AI building: the handoff of
non-code steps. A vague handoff produces a back-and-forth ("which button?"); a precise one
with expected-results and failure-fixes gets executed once, correctly, and the build keeps
moving.
