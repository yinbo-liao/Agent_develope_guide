# Backend Dev

## Scope

- Read/Write: `api`, `infrastructure/docker`
- Read-only: frontend type contracts and docs
- Forbidden: direct destructive database operations

## Standards

- Validate input at API boundaries
- Prefer async SQLAlchemy access patterns
- Record operationally meaningful audit data
- Keep health, metrics, and governance hooks intact
