# Security-sensitive work

Identify assets, identities, trust boundaries, flows, and intended public behavior. Document
public routes (including login, callbacks, webhooks), rationale, validation, and abuse controls.
Protected operations need authentication AND authorization; test cross-user/tenant denial
where those boundaries exist.

Use approved secret storage/injection. Exclude secrets from logs, responses, fixtures, and
bundles. Validate inputs, parameterize data access, escape output, and assess CSRF by credential
transport rather than an API label. Check inbound authenticity and replay requirements.

Classify data; approve external processing deliberately. Review dependency provenance/updates.
Prioritize by impact, likelihood, and exposure, not one severity for every defect. Surface
material out-of-scope findings without silently expanding implementation scope.

Tie claims to deployed paths and negative tests; name untested boundaries. These prompts aid
judgment, not a complete security audit or sandbox.
