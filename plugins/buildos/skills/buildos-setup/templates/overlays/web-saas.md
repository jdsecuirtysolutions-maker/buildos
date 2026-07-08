# Overlay: Web SaaS / Deploy Pipeline

Include this overlay when the project is a deployed web app with a build step and a hosting
platform. Paste the relevant rules into your project `CLAUDE.md` (or reference this file
from it) and fill the placeholders. These rules exist because each one, when skipped, has
shipped a broken production deploy.

---

## Deployment pipeline — know exactly what builds what

Before touching any deploy artifact, write down (and keep current in CLAUDE.md):

- **What builds the frontend, and when.** Does the host build it, or do you ship a
  pre-built bundle? <FILL>
- **What serves what in production.** Which process serves the app; which static dir it
  serves from. <FILL>
- **Which env vars are needed at BUILD time vs RUNTIME.** This distinction causes the most
  outages. <FILL>
- **What takes effect on next deploy vs requires a rebuild.** Backend changes vs frontend
  source changes often differ. <FILL>

## Build-time env var trap (the #1 silent breaker)

Many bundlers (Vite, CRA, Next public vars, etc.) **inline** environment variables at
**build time**. A build missing them compiles broken clients (e.g. an auth client that's
`null`) with **no runtime fallback** and no error — it just doesn't work in production.

- **Rule:** NEVER rebuild the production bundle without first confirming the build-time env
  file contains every required var. <FILL: exact file + var names, e.g. `frontend/.env`
  must have `VITE_*` keys.>
- A build without them is not "a build with a bug" — it's a silently broken artifact.

## Built-artifact discipline

- If the build output dir is gitignored, **force-add** it after rebuilding
  (`git add -f <dist-dir>`), or new bundle filenames get silently ignored and the deploy
  serves stale code.
- After any frontend *source* change, the bundle MUST be rebuilt for the change to reach
  production. Source change ≠ deployed change.
- <FILL: any host-specific build behavior, e.g. "the host does NOT build the frontend; the
  start command serves whatever bundle exists at deploy time.">

## Route shadowing

If a server framework and a client-side SPA router both claim paths, server routes can
**shadow** SPA routes (a hard refresh hits the server handler, not the app). Audit for this
when adding/moving routes. <FILL: known shadowed routes in this project, if any.>

## Pre-deploy verification (mandatory, not optional)

1. Build succeeds locally with build-time env present.
2. The thing you changed is actually in the built artifact (grep the bundle if unsure).
3. The app starts and the changed flow works end-to-end — not "it compiles."
4. If you changed source, the artifact was rebuilt + force-added + committed.

## If a deploy breaks production

**Revert first, investigate second.** Restore the last-working artifact, commit, push to
stop the bleeding — *then* debug forward on a branch. Don't leave prod broken while you
root-cause.

## Database / migrations

- <FILL: schema-version mechanism, how migrations run (startup? manual?), and how to verify
  a migration applied in prod.>
- Dev DB ≠ prod DB. <FILL: the migration path from dev store to prod store.>
- Confirm the managed DB isn't paused/asleep (some free tiers auto-pause) before debugging
  "everything is down" symptoms — it's often infra, not code.
