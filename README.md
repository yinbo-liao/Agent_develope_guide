# AI Agent Dev Strategy

This repository now includes the initial monorepo scaffold for the multi-agent AI workflow platform described in [ai_agent_dev_strategy.md](file:///h:/Ai-Agent_dev_strategy/ai_agent_dev_strategy.md).

The current focus is project architecture:

- `api/` for the FastAPI backend and tests
- `frontend/` for the React application
- `infrastructure/` for Docker, Kubernetes, and Terraform assets
- `.claude/` for local agent configuration, skills, hooks, and policies
- `docs/` for architecture decisions, runbooks, and API documentation
- `scripts/` for migrations, backups, and security automation

See [code_archtech.md](file:///h:/Ai-Agent_dev_strategy/code_archtech.md) for the concrete directory tree and scaffold notes.
