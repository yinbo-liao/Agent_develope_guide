package agent.scope

import future.keywords.if
import future.keywords.in

default allow := false

agents := {
    "frontend-dev": {
        "read": ["/frontend", "/shared", "/docs"],
        "write": ["/frontend", "/shared"],
        "execute": ["npm", "node", "vitest", "eslint"],
        "network": false,
    },
    "backend-dev": {
        "read": ["/api", "/shared", "/infrastructure", "/docs"],
        "write": ["/api", "/shared", "/infrastructure/docker"],
        "execute": ["python", "pytest", "alembic", "uvicorn", "docker"],
        "network": true,
    },
    "security-auditor": {
        "read": ["/", "/frontend", "/api", "/infrastructure", "/docs"],
        "write": [],
        "execute": ["grep", "find", "npm", "python", "bandit", "safety"],
        "network": false,
    },
    "design-director": {
        "read": ["/frontend", "/shared", "/docs"],
        "write": ["/frontend/src/design-tokens.json"],
        "execute": ["node", "python", "npx"],
        "network": false,
    },
    "governor": {
        "read": ["/"],
        "write": ["/.claude", "/docs"],
        "execute": ["git", "claude"],
        "network": true,
    },
}

is_within_path(path, allowed_prefixes) if {
    some prefix in allowed_prefixes
    startswith(path, prefix)
}

allow if {
    input.action == "read"
    agent := agents[input.agent]
    is_within_path(input.path, agent.read)
}

allow if {
    input.action == "write"
    agent := agents[input.agent]
    count(agent.write) > 0
    is_within_path(input.path, agent.write)
}

allow if {
    input.action == "execute"
    agent := agents[input.agent]
    some allowed_cmd in agent.execute
    startswith(input.command, allowed_cmd)
}

allow if {
    input.action == "network"
    agent := agents[input.agent]
    agent.network
}

violation contains {"msg": msg} if {
    agent := agents[input.agent]
    input.action == "write"
    not is_within_path(input.path, agent.write)
    msg := sprintf("Agent %s cannot write to %s", [input.agent, input.path])
}
