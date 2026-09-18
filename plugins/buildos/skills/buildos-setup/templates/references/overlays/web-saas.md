# Web deployment contract

Establish in PROJECT.md: who builds, build/runtime config, artifact location, serving process,
release publication, migrations, and running revision identity. Investigate unknowns.

When CI builds source, preserve that design and its ignore rules. Commit generated output only
when deployment explicitly consumes committed artifacts. Never force-add ignored directories
as a general rule. Validate required public build variables without exposing secrets.

Verify changed flows safely, including direct SPA navigation, and record artifact/revision.
Deploy only within authorization. During incidents follow the restoration plan and assess
schema/data compatibility before rollback. Avoid automatic reverse migrations.
