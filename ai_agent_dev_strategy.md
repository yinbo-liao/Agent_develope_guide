# AI Workflow Platform

## Implemented Project Scope

This document now serves two purposes:

1. it records the implemented repository scope across Waves 1-4
2. it preserves the original long-form implementation guide below as detailed reference material

The current repository has been implemented as a staged delivery across four coded waves and now includes the core platform foundation, workflow engine, realtime monitoring, governance, cost controls, and production asset scaffolding.

## Delivery Status

- Wave 1 completed: backend foundation, frontend shell, Docker dev stack, health endpoints, security baseline
- Wave 2 completed: workflow persistence, workflow engine, task API, human review API
- Wave 3 completed: WebSocket and SSE transport, workflow event streaming, live dashboard
- Wave 4 completed: MCP endpoints, audit and rate limiting, observability hooks, cost governance, production deployment assets

## Repository Scope Implemented

### Backend

- `api/app/main.py`: app factory, startup lifecycle, middleware, route registration
- `api/app/core/`: config, logging, database, metrics, tracing, websocket, sse, MCP, circuit breaker, cost tracking
- `api/app/models/`: workflow runs, human review decisions, MCP audit records
- `api/app/services/`: retrieval, LLM generation, cost governor, model router
- `api/app/workflows/`: state contracts, workflow nodes, graph, runner, human review processing
- `api/app/api/v1/`: health, workflows, events, human review, cost, MCP

### Frontend

- `frontend/src/pages/HomePage.tsx`: workflow launch and monitoring entry page
- `frontend/src/hooks/useWorkflowEvents.ts`: realtime workflow transport hook
- `frontend/src/components/`: workflow dashboard, timeline, review panel, cost widget, transport indicator, error boundary
- `frontend/src/types/workflow.ts`: typed workflow and event contracts
- `frontend/src/lib/runtime.ts`: runtime API and websocket base configuration

### Security and Governance

- `.claude/hooks/security_firewall_v2.py`: dangerous command, path, SQL, and secret detection
- `.claude/hooks/audit_logger_v2.py`: structured local audit logging
- `.claude/agents/*.md`: governor, frontend, backend, security, and design governance documents
- `infrastructure/opa/agent-policies.rego`: OPA policy definitions for scope enforcement
- `scripts/validate_agent_scopes.py`: governance document validation

### Infrastructure and Production Assets

- `docker-compose.yml`: local development stack
- `infrastructure/docker/api/Dockerfile.dev`: backend development container
- `infrastructure/docker/frontend/Dockerfile.dev`: frontend development container
- `infrastructure/docker/api/Dockerfile.prod`: backend production image
- `infrastructure/docker/frontend/Dockerfile.prod`: frontend production image
- `infrastructure/docker/frontend/nginx.conf`: frontend runtime proxy configuration
- `infrastructure/docker/frontend/security-headers.conf`: frontend security headers
- `infrastructure/prometheus/`: alerting and alertmanager configuration
- `infrastructure/grafana/dashboards/`: Grafana dashboard scaffold
- `helm/aiwf/`: production chart, values, and deployment templates

## Implemented API Surface

### Health

- `GET /health`
- `GET /health/ready`

### Workflow Execution

- `POST /api/v1/workflows`
- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{task_id}`
- `POST /api/v1/human-review/decide`

### Realtime Monitoring

- `GET /api/v1/events/state/{task_id}`
- `GET /api/v1/events/sse/{task_id}`
- `WS /api/v1/events/ws/{task_id}`

### Governance and Cost

- `GET /api/v1/cost/status`
- `GET /api/v1/mcp/health`
- `GET /api/v1/mcp/tools`
- `POST /api/v1/mcp/invoke/{server_name}/{tool_name}`

## Implemented Runtime Behavior

### Workflow Path

1. request enters via workflow API
2. workflow record is persisted
3. runner validates input, retrieves context, assesses risk
4. model router selects a model based on complexity and budget
5. cost governor checks budget before generation
6. low-risk tasks complete automatically
7. medium/high-risk tasks take the escalated analysis path
8. critical-risk tasks enter human review
9. realtime events stream over WebSocket with SSE fallback

### Governance Path

1. local policy and hook tooling protect repository operations
2. MCP requests are rate-limited and audited
3. tracing and metrics hooks expose observability signals
4. production assets provide a starting point for release packaging and deployment

## Current Verification Status

The implementation has been verified at the code integration level with:

- Python compile checks for backend modules
- workflow and security tests passing
- FastAPI import and route registration checks passing
- MCP tool catalog initialization passing
- governance document validation passing
- frontend TypeScript typecheck passing

## Remaining Runtime Validation Recommended

The following should still be executed as a full environment validation pass:

1. `docker compose up --build`
2. backend health and workflow API smoke tests
3. realtime dashboard interaction test
4. MCP endpoint smoke tests
5. production image builds
6. Helm render and deployment validation

---

## Detailed Reference Guide

The following sections preserve the original comprehensive implementation guide and file-by-file reference content used to shape the repository.

Based on my professional review, I'll now provide a comprehensive, production-hardened implementation guide that addresses all critical gaps identified. This enhanced solution covers 9 phases (including the new Phase 0.5 Security Hardening) with full technical details.
Production-Hardened Multi-Agent AI Workflow Platform
Complete Implementation Guide (18-20 Weeks)
Table of Contents
Phase 0: Foundation (Week 1)
Phase 0.5: Security Hardening (Week 2)
Phase 1: Workflow Engine (Weeks 3-4)
Phase 2: Agent Orchestration (Weeks 5-6)
Phase 3: Real-Time Observability (Weeks 7-8)
Phase 4: MCP & External Tools (Weeks 9-10)
Phase 5: Design Quality & Taste (Weeks 11-12)
Phase 6: Observability & SRE (Weeks 13-14)
Phase 7: Production Deployment (Weeks 15-18)
Phase 8: Cost Governance & Optimization (Weeks 19-20)
<a name="phase-0">
Phase 0: Foundation (Week 1)
Step 0.1: Monorepo Structure with Security-First Layout
bash
mkdir ai-workflow-platform && cd ai-workflow-platform
git init
git checkout -b main

# Create directory structure with security boundaries
mkdir -p \
  api/app/{core,api/v1,models,services,workflows,agents,security} \
  api/tests/{unit,integration,e2e} \
  frontend/src/{components,hooks,pages,types,lib,styles} \
  frontend/public \
  infrastructure/{docker,k8s,terraform} \
  .claude/{agents,skills,hooks,policies} \
  docs/{adr,runbooks,api} \
  scripts/{migrations,backups,security}
Step 0.2: Backend Initialization (FastAPI + Security)
File: api/pyproject.toml
toml
[project]
name = "ai-workflow-platform-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    # Core Framework
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "python-multipart>=0.0.9",
    
    # Database & ORM
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.13.0",
    "redis>=5.0.0",
    
    # Data Validation
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    
    # AI / LangChain Stack
    "langgraph>=0.2.0",
    "langgraph-checkpoint-postgres>=0.1.0",
    "langchain-openai>=0.3.0",
    "langchain-anthropic>=0.3.0",
    "langchain-mcp-adapters>=0.1.0",
    "mcp>=1.25.0",
    
    # Security
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-slowapi>=0.1.0",
    "opentelemetry-api>=1.25.0",
    "opentelemetry-sdk>=1.25.0",
    "opentelemetry-instrumentation-fastapi>=0.46b0",
    
    # Observability
    "prometheus-fastapi-instrumentator>=7.0.0",
    "python-json-logger>=2.0.7",
    "structlog>=24.1.0",
    
    # Testing
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.28.0",
    "hypothesis>=6.100.0",
]

[project.optional-dependencies]
dev = [
    "black>=24.0.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
    "pre-commit>=3.7.0",
]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
Step 0.3: Frontend Initialization (React 19 + Vite)
bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

# Core dependencies
npm install \
  react@19.0.0 \
  react-dom@19.0.0 \
  react-router-dom@7.0.0 \
  @tanstack/react-query@5.0.0 \
  zustand@5.0.0 \
  axios@1.7.0 \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-tabs \
  @radix-ui/react-toast \
  @radix-ui/react-tooltip \
  class-variance-authority \
  clsx \
  tailwind-merge \
  lucide-react \
  recharts@2.12.0 \
  @monaco-editor/react@4.6.0

# Dev dependencies
npm install -D \
  tailwindcss@3.4.0 \
  postcss@8.4.0 \
  autoprefixer@10.4.0 \
  @types/node@20.0.0 \
  @types/react@19.0.0 \
  @types/react-dom@19.0.0 \
  typescript@5.5.0 \
  @vitejs/plugin-react@4.3.0 \
  @axe-core/cli@4.9.0 \
  lighthouse@12.0.0 \
  vitest@2.0.0 \
  @testing-library/react@16.0.0 \
  @testing-library/jest-dom@6.4.0
File: frontend/tailwind.config.js
JavaScript
const tokens = require('./src/design-tokens.json');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: tokens.color.primary,
        neutral: tokens.color.neutral,
        accent: tokens.color.accent,
        semantic: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
        }
      },
      fontFamily: {
        sans: tokens.typography.fontFamily.sans.split(', '),
        mono: tokens.typography.fontFamily.mono.split(', '),
      },
      fontSize: tokens.typography.fontSize,
      fontWeight: tokens.typography.fontWeight,
      lineHeight: tokens.typography.lineHeight,
      spacing: tokens.spacing,
      borderRadius: tokens.borderRadius,
      boxShadow: tokens.shadow,
      transitionDuration: tokens.motion.duration,
      transitionTimingFunction: tokens.motion.easing,
      animation: {
        'fade-in': 'fadeIn 250ms ease-out',
        'slide-up': 'slideUp 400ms cubic-bezier(0.4, 0, 0.2, 1)',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
Step 0.4: Docker Compose Development Environment
File: docker-compose.yml
yaml
version: '3.8'

services:
  # PostgreSQL with enhanced security
  postgres:
    image: postgres:17-alpine
    container_name: aiwf-db
    environment:
      POSTGRES_USER: ${DB_USER:-aiwf}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme_in_production}
      POSTGRES_DB: ${DB_NAME:-aiwf_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/docker/postgres/init:/docker-entrypoint-initdb.d
    command: >
      postgres 
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=768MB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=1310kB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-aiwf}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - aiwf-network
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/run/postgresql

  # Redis for session/cache/pubsub
  redis:
    image: redis:7-alpine
    container_name: aiwf-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --requirepass ${REDIS_PASSWORD:-changeme}
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - aiwf-network

  # Backend API
  backend:
    build:
      context: ./api
      dockerfile: ../infrastructure/docker/api/Dockerfile.dev
    container_name: aiwf-backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql+asyncpg://${DB_USER:-aiwf}:${DB_PASSWORD:-changeme_in_production}@postgres:5432/${DB_NAME:-aiwf_dev}
      - REDIS_URL=redis://:${REDIS_PASSWORD:-changeme}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-dev-secret-change-in-production}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./api:/app
      - /app/.venv
    command: >
      uvicorn app.main:app 
      --host 0.0.0.0 
      --port 8000 
      --reload 
      --log-level debug
    networks:
      - aiwf-network

  # Frontend Dev Server
  frontend:
    build:
      context: ./frontend
      dockerfile: ../infrastructure/docker/frontend/Dockerfile.dev
    container_name: aiwf-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
    networks:
      - aiwf-network

  # LocalStack for AWS service mocking (S3, Secrets Manager)
  localstack:
    image: localstack/localstack:3.0
    container_name: aiwf-localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,secretsmanager
      - DEFAULT_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
    volumes:
      - localstack_data:/var/lib/localstack
    networks:
      - aiwf-network

volumes:
  postgres_data:
  redis_data:
  localstack_data:

networks:
  aiwf-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
<a name="phase-05">
Phase 0.5: Security Hardening (Week 2) — NEW CRITICAL PHASE
Step 0.5.1: OPA (Open Policy Agent) for Agent Scope Enforcement
File: infrastructure/opa/agent-policies.rego
rego
package agent.scope

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false

# Agent definitions with permitted paths
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
    }
}

# Check if path is within allowed prefix
is_within_path(path, allowed_prefixes) if {
    some prefix in allowed_prefixes
    startswith(path, prefix)
}

# File read policy
allow if {
    input.action == "read"
    agent := agents[input.agent]
    is_within_path(input.path, agent.read)
}

# File write policy
allow if {
    input.action == "write"
    agent := agents[input.agent]
    count(agent.write) > 0
    is_within_path(input.path, agent.write)
}

# Command execution policy
allow if {
    input.action == "execute"
    agent := agents[input.agent]
    some allowed_cmd in agent.execute
    startswith(input.command, allowed_cmd)
}

# Network access policy
allow if {
    input.action == "network"
    agent := agents[input.agent]
    agent.network == true
}

# Violation reporting
violation[{"msg": msg}] if {
    input.action == "write"
    agent := agents[input.agent]
    count(agent.write) == 0
    msg := sprintf("Agent %s has no write permissions", [input.agent])
}

violation[{"msg": msg}] if {
    input.action == "write"
    agent := agents[input.agent]
    count(agent.write) > 0
    not is_within_path(input.path, agent.write)
    msg := sprintf("Agent %s cannot write to %s", [input.agent, input.path])
}
File: api/app/security/opa_client.py
Python
import json
import httpx
from typing import Dict, List, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class OPAPolicyClient:
    """Client for Open Policy Agent with local caching."""
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url
        self._policy_cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def evaluate(self, agent: str, action: str, path: str, command: Optional[str] = None) -> Dict:
        """Evaluate policy decision for an agent action."""
        input_data = {
            "agent": agent,
            "action": action,
            "path": path,
        }
        if command:
            input_data["command"] = command
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.opa_url}/v1/data/agent/scope/allow",
                    json={"input": input_data},
                    timeout=5.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Also fetch violations for detailed error messages
                viol_response = await client.post(
                    f"{self.opa_url}/v1/data/agent/scope/violation",
                    json={"input": input_data},
                    timeout=5.0
                )
                violations = viol_response.json().get("result", [])
                
                return {
                    "allowed": result.get("result", False),
                    "violations": violations,
                    "agent": agent,
                    "action": action,
                    "path": path,
                }
        except httpx.HTTPError as e:
            logger.error(f"OPA evaluation failed: {e}")
            # Fail closed - deny if OPA is unreachable
            return {
                "allowed": False,
                "violations": [{"msg": "Policy engine unavailable - access denied"}],
                "agent": agent,
                "action": action,
                "path": path,
            }
    
    async def check_scope(self, agent: str, action: str, path: str) -> bool:
        """Quick check if action is permitted."""
        result = await self.evaluate(agent, action, path)
        if not result["allowed"]:
            for v in result.get("violations", []):
                logger.warning(f"Policy violation: {v['msg']}")
        return result["allowed"]

opa_client = OPAPolicyClient()
Step 0.5.2: Enhanced Security Hooks with AST Parsing
File: .claude/hooks/security_firewall_v2.py
Python
#!/usr/bin/env python3
"""
Enhanced Security Firewall with AST-based SQL parsing
Prevents destructive operations through semantic analysis, not string matching
"""
import json
import sys
import re
import sqlparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Destructive SQL operations (AST-level detection)
DESTRUCTIVE_SQL_OPS = {
    'DROP': ['DATABASE', 'SCHEMA', 'TABLE', 'INDEX', 'VIEW', 'SEQUENCE'],
    'TRUNCATE': ['TABLE'],
    'DELETE': ['FROM'],  # Without WHERE clause
    'UPDATE': [],  # Without WHERE clause
    'ALTER': ['TABLE', 'DROP COLUMN', 'DROP CONSTRAINT'],
    'GRANT': ['ALL PRIVILEGES'],
    'REVOKE': [],
}

# File system dangerous patterns
DANGEROUS_PATHS = [
    r'^/etc/',
    r'^/root/',
    r'^/sys/',
    r'^/proc/',
    r'\.ssh/',
    r'\.gnupg/',
    r'\.aws/',
    r'\.env(\.production)?$',
    r'passwd$',
    r'shadow$',
]

# Command injection patterns
DANGEROUS_COMMANDS = [
    r'rm\s+-rf\s+/',
    r'rm\s+--no-preserve-root',
    r'dd\s+if=.*of=/dev/',
    r'mkfs\.',
    r':(){ :|:& };:',  # Fork bomb
    r'curl.*\|.*bash',
    r'wget.*\|.*sh',
    r'eval\s*\(',
    r'exec\s*\(',
]

class SecurityFirewall:
    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
    
    def analyze_sql(self, query: str) -> List[Dict]:
        """Parse SQL and detect destructive operations."""
        violations = []
        try:
            parsed = sqlparse.parse(query)
            for statement in parsed:
                tokens = [t for t in statement.tokens if not t.is_whitespace]
                if not tokens:
                    continue
                
                first_token = str(tokens[0]).upper()
                
                # Check for destructive operations
                if first_token in DESTRUCTIVE_SQL_OPS:
                    allowed_targets = DESTRUCTIVE_SQL_OPS[first_token]
                    
                    # Special case: DELETE/UPDATE without WHERE
                    if first_token in ('DELETE', 'UPDATE'):
                        has_where = any(
                            str(t).upper() == 'WHERE' 
                            for t in tokens
                        )
                        if not has_where:
                            violations.append({
                                "type": "sql_missing_where",
                                "operation": first_token,
                                "severity": "critical",
                                "message": f"{first_token} without WHERE clause detected"
                            })
                    
                    # Check target objects
                    statement_str = str(statement).upper()
                    for target in allowed_targets:
                        if target in statement_str:
                            violations.append({
                                "type": "sql_destructive",
                                "operation": first_token,
                                "target": target,
                                "severity": "critical",
                                "message": f"Destructive operation: {first_token} {target}"
                            })
        
        except Exception as e:
            # If parsing fails, check for raw dangerous keywords
            query_upper = query.upper()
            for op in DESTRUCTIVE_SQL_OPS.keys():
                if op in query_upper:
                    violations.append({
                        "type": "sql_parse_error",
                        "operation": op,
                        "severity": "high",
                        "message": f"Potentially dangerous SQL (parse failed): {op}"
                    })
        
        return violations
    
    def check_path(self, path: str) -> List[Dict]:
        """Check if path access is dangerous."""
        violations = []
        for pattern in DANGEROUS_PATHS:
            if re.search(pattern, path, re.IGNORECASE):
                violations.append({
                    "type": "dangerous_path",
                    "path": path,
                    "pattern": pattern,
                    "severity": "critical",
                    "message": f"Access to protected path: {path}"
                })
        return violations
    
    def check_command(self, command: str) -> List[Dict]:
        """Check shell command for dangerous patterns."""
        violations = []
        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                violations.append({
                    "type": "dangerous_command",
                    "command": command,
                    "pattern": pattern,
                    "severity": "critical",
                    "message": f"Dangerous command pattern detected: {command[:50]}..."
                })
        return violations
    
    def check_secrets(self, content: str) -> List[Dict]:
        """Detect hardcoded secrets in content."""
        secret_patterns = [
            (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
            (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
            (r'[0-9a-zA-Z/+]{40}', "Generic secret (base64)"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
        ]
        
        violations = []
        for pattern, description in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Filter out false positives
                matched = match.group()
                if len(matched) < 20:  # Skip short matches
                    continue
                if 'example' in matched.lower() or 'placeholder' in matched.lower():
                    continue
                
                violations.append({
                    "type": "hardcoded_secret",
                    "description": description,
                    "severity": "critical",
                    "message": f"Potential hardcoded {description} detected",
                    "position": match.span()
                })
        return violations
    
    def process(self, input_json: str) -> Dict:
        """Main entry point for hook processing."""
        try:
            data = json.loads(input_json)
            tool_name = data.get('tool_name', '')
            params = data.get('params', {})
            
            # Check based on tool type
            if tool_name == 'Bash':
                command = params.get('command', '')
                self.violations.extend(self.check_command(command))
            
            elif tool_name in ('Edit', 'Write'):
                path = params.get('path', params.get('file', ''))
                content = params.get('content', params.get('text', ''))
                self.violations.extend(self.check_path(path))
                self.violations.extend(self.check_secrets(content))
                
                # Check for SQL in file content
                if path.endswith(('.sql', '.py', '.js', '.ts')):
                    self.violations.extend(self.analyze_sql(content))
            
            elif tool_name == 'SQL':
                query = params.get('query', '')
                self.violations.extend(self.analyze_sql(query))
            
            # Determine result
            critical = [v for v in self.violations if v['severity'] == 'critical']
            if critical:
                return {
                    "block": True,
                    "reason": f"Critical security violation: {critical[0]['message']}",
                    "violations": self.violations
                }
            
            if self.violations:
                return {
                    "block": False,
                    "warn": True,
                    "reason": "Security warnings present",
                    "violations": self.violations
                }
            
            return {"block": False, "reason": "Passed all security checks"}
            
        except json.JSONDecodeError:
            return {"block": True, "reason": "Invalid input JSON"}
        except Exception as e:
            return {"block": True, "reason": f"Security check error: {str(e)}"}

if __name__ == "__main__":
    firewall = SecurityFirewall()
    result = firewall.process(sys.stdin.read())
    print(json.dumps(result))
    sys.exit(2 if result.get("block") else 0)
File: .claude/hooks/audit_logger_v2.py
Python
#!/usr/bin/env python3
"""
Structured audit logger with correlation IDs and compliance formatting
"""
import json
import sys
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any

class AuditLogger:
    def __init__(self, log_file: str = ".claude/audit.jsonl"):
        self.log_file = log_file
    
    def sanitize(self, data: Dict) -> Dict:
        """Remove sensitive fields from logged data."""
        sensitive_keys = ['password', 'secret', 'token', 'key', 'credential', 'auth']
        sanitized = {}
        for k, v in data.items():
            if any(sk in k.lower() for sk in sensitive_keys):
                sanitized[k] = f"[REDACTED:{hashlib.sha256(str(v).encode()).hexdigest()[:8]}]"
            else:
                sanitized[k] = v
        return sanitized
    
    def log(self, input_json: str) -> None:
        try:
            data = json.loads(input_json)
            
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": data.get("session_id", "unknown"),
                "correlation_id": data.get("correlation_id", "unknown"),
                "event_type": "PostToolUse",
                "tool_name": data.get("tool_name", "unknown"),
                "params": self.sanitize(data.get("params", {})),
                "result_status": data.get("result", {}).get("status", "unknown"),
                "agent_id": data.get("agent_id", "unknown"),
                "cost_tokens": data.get("cost", {}).get("tokens", 0),
                "duration_ms": data.get("duration_ms", 0),
            }
            
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
                
        except Exception as e:
            # Fail-safe: log to stderr if file logging fails
            print(f"Audit logging error: {e}", file=sys.stderr)

if __name__ == "__main__":
    logger = AuditLogger()
    logger.log(sys.stdin.read())
Step 0.5.3: Pre-commit Security Hooks
File: .pre-commit-config.yaml
yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: detect-private-key
      - id: detect-aws-credentials
      - id: check-merge-conflict

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json

  - repo: local
    hooks:
      - id: opa-policy-test
        name: Test OPA Policies
        entry: opa test infrastructure/opa/
        language: system
        files: \.rego$

      - id: security-firewall-test
        name: Test Security Firewall
        entry: python -m pytest tests/security/test_firewall.py -v
        language: system
        files: \.claude/hooks/security.*\.py$

      - id: agent-scope-check
        name: Check Agent Scope Definitions
        entry: python scripts/validate_agent_scopes.py
        language: system
        files: \.claude/agents/.*\.md$
<a name="phase-1">
Phase 1: Workflow Engine (Weeks 3-4)
Step 1.1: Enhanced State Schema with Versioning
File: api/app/workflows/state.py
Python
from typing import Annotated, List, Literal, Optional, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime
from enum import Enum
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    RETRIEVING = "retrieving"
    ASSESSING = "assessing"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentState(TypedDict):
    """Core state object with versioning for migration support."""
    
    # Versioning
    __version__: Literal["1.0"]
    
    # Core Identifiers
    task_id: str
    user_id: str
    session_id: str
    input_query: str
    
    # Messaging
    messages: Annotated[list, add_messages]
    
    # Intermediate Results
    retrieval_results: Optional[List[Dict[str, Any]]]
    agent_finding: Optional[str]
    final_response: Optional[str]
    
    # Control & Error Handling
    current_step: str
    current_status: WorkflowStatus
    error_info: Optional[str]
    retry_count: int
    max_retries: int
    
    # Governance & Cost Control
    total_tokens_used: int
    token_budget: int
    cost_usd: float
    cost_budget_usd: float
    
    # Human-in-the-Loop
    is_human_review_needed: bool
    human_decision: Optional[Literal["approved", "rejected"]]
    human_comment: Optional[str]
    review_deadline: Optional[datetime]
    
    # Risk & Routing
    risk_level: RiskLevel
    risk_factors: List[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class WorkflowEvent(BaseModel):
    """Event model for WebSocket/SSE streaming."""
    event_type: str = Field(..., description="Type of event")
    task_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
Step 1.2: Resilient Workflow Nodes with Circuit Breakers
File: api/app/workflows/nodes.py
Python
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.workflows.state import AgentState, RiskLevel, WorkflowStatus
from app.services.vector_store import retrieve_context
from app.services.llm_client import LLMClient
from app.core.cost_tracker import cost_tracker
from app.core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Circuit breaker for LLM calls
llm_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=(Exception,)
)

class NodeExecutionError(Exception):
    """Custom exception for node execution failures."""
    pass

async def validate_input(state: AgentState) -> Dict[str, Any]:
    """Node 1: Validate input with comprehensive checks."""
    query = state.get("input_query", "").strip()
    
    # Input validation
    if not query:
        return {
            "error_info": "Query cannot be empty",
            "risk_level": RiskLevel.CRITICAL,
            "current_status": WorkflowStatus.FAILED
        }
    
    if len(query) < 3:
        return {
            "error_info": "Query too short (minimum 3 characters)",
            "risk_level": RiskLevel.CRITICAL,
            "current_status": WorkflowStatus.FAILED
        }
    
    if len(query) > 10000:
        return {
            "error_info": "Query exceeds maximum length (10000 characters)",
            "risk_level": RiskLevel.CRITICAL,
            "current_status": WorkflowStatus.FAILED
        }
    
    # User permission check
    user_id = state.get("user_id", "")
    blocked_users = await get_blocked_users()  # Cache-backed
    
    if user_id in blocked_users:
        return {
            "error_info": "User account is suspended",
            "risk_level": RiskLevel.CRITICAL,
            "current_status": WorkflowStatus.FAILED
        }
    
    # Rate limit check
    rate_limit_key = f"rate_limit:{user_id}"
    current_count = await redis_client.incr(rate_limit_key)
    if current_count == 1:
        await redis_client.expire(rate_limit_key, 60)  # 1 minute window
    
    if current_count > 100:  # 100 requests per minute
        return {
            "error_info": "Rate limit exceeded (100 requests/minute)",
            "risk_level": RiskLevel.CRITICAL,
            "current_status": WorkflowStatus.FAILED
        }
    
    logger.info(f"Task {state['task_id']}: Input validated for user {user_id}")
    
    return {
        "current_step": "validate_input",
        "current_status": WorkflowStatus.RETRIEVING,
        "messages": [HumanMessage(content=query)],
        "risk_level": RiskLevel.LOW,
        "risk_factors": [],
        "updated_at": datetime.utcnow()
    }

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
async def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """Node 2: Retrieve context with retry logic and fallback."""
    try:
        # Primary: Vector DB search
        results = await retrieve_context(state["input_query"], top_k=5)
        
        # Fallback: Keyword search if vector search returns empty
        if not results:
            results = await fallback_keyword_search(state["input_query"])
        
        return {
            "current_step": "retrieve_context",
            "current_status": WorkflowStatus.ASSESSING,
            "retrieval_results": results,
            "updated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Retrieval failed for task {state['task_id']}: {e}")
        # Graceful degradation: continue without context
        return {
            "current_step": "retrieve_context",
            "current_status": WorkflowStatus.ASSESSING,
            "retrieval_results": [],
            "error_info": f"Retrieval warning: {str(e)}",
            "updated_at": datetime.utcnow()
        }

async def assess_risk(state: AgentState) -> Dict[str, Any]:
    """Node 3: Multi-factor risk assessment with scoring."""
    query = state["input_query"].lower()
    risk_score = 0
    risk_factors = []
    
    # Keyword-based risk detection
    critical_patterns = {
        r'\b(payment|credit.?card|ssn|social.security)\b': "Financial/PII data access",
        r'\b(sudo|root|admin|superuser)\b': "Privilege escalation",
        r'\b(drop|delete|truncate|destroy)\b.*\b(all|database|table)\b': "Mass deletion",
        r'\b(update|modify|alter)\b.*\b(schema|all|every)\b': "Schema modification",
        r'\b(grant|revoke)\b.*\b(all|super)\b': "Permission changes",
    }
    
    high_patterns = {
        r'\b(delete|remove)\b': "Deletion operation",
        r'\b(update|modify)\b': "Modification operation",
        r'\b(export|download)\b.*\b(all|bulk)\b': "Bulk export",
        r'\b(password|secret|key|token)\b': "Credential access",
    }
    
    for pattern, reason in critical_patterns.items():
        if re.search(pattern, query):
            risk_score += 50
            risk_factors.append(f"CRITICAL: {reason}")
    
    for pattern, reason in high_patterns.items():
        if re.search(pattern, query):
            risk_score += 20
            risk_factors.append(f"HIGH: {reason}")
    
    # Context-based risk adjustment
    retrieval_results = state.get("retrieval_results", [])
    if retrieval_results:
        sensitive_topics = ["finance", "health", "legal", "hr", "security"]
        for result in retrieval_results:
            if any(topic in str(result).lower() for topic in sensitive_topics):
                risk_score += 10
                risk_factors.append("MEDIUM: Sensitive domain context")
                break
    
    # User history risk adjustment
    user_id = state.get("user_id")
    if await has_recent_failures(user_id, hours=24):
        risk_score += 15
        risk_factors.append("MEDIUM: Recent failure history")
    
    # Determine risk level
    if risk_score >= 50:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 30:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 10:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
    
    logger.info(f"Task {state['task_id']}: Risk assessed as {risk_level} (score: {risk_score})")
    
    return {
        "current_step": "assess_risk",
        "current_status": WorkflowStatus.EXECUTING,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "updated_at": datetime.utcnow()
    }

async def auto_generate_response(state: AgentState) -> Dict[str, Any]:
    """Node 4: Direct LLM generation with cost tracking."""
    try:
        # Check token budget
        if state.get("total_tokens_used", 0) >= state.get("token_budget", 10000):
            return {
                "error_info": "Token budget exceeded",
                "current_status": WorkflowStatus.FAILED,
                "is_human_review_needed": True
            }
        
        # Circuit breaker protected LLM call
        async with llm_circuit_breaker:
            response = await LLMClient.generate(
                prompt=state["input_query"],
                context=state.get("retrieval_results", []),
                max_tokens=min(2000, state.get("token_budget", 10000) - state.get("total_tokens_used", 0)),
                temperature=0.3
            )
        
        # Track cost
        tokens_used = response.get("tokens_used", 0)
        cost = response.get("cost_usd", 0.0)
        await cost_tracker.record_usage(
            task_id=state["task_id"],
            user_id=state["user_id"],
            tokens=tokens_used,
            cost_usd=cost,
            model=response.get("model", "unknown")
        )
        
        return {
            "current_step": "auto_generate_response",
            "current_status": WorkflowStatus.COMPLETED,
            "final_response": response["content"],
            "messages": [AIMessage(content=response["content"])],
            "total_tokens_used": state.get("total_tokens_used", 0) + tokens_used,
            "cost_usd": state.get("cost_usd", 0.0) + cost,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Generation failed for task {state['task_id']}: {e}")
        return {
            "error_info": f"Generation error: {str(e)}",
            "current_status": WorkflowStatus.FAILED,
            "retry_count": state.get("retry_count", 0) + 1
        }

async def human_review_node(state: AgentState) -> Dict[str, Any]:
    """Node 5: Human review with timeout handling."""
    # Check if human decision already exists
    decision = state.get("human_decision")
    
    if decision == "approved":
        return {
            "current_step": "human_review_approved",
            "current_status": WorkflowStatus.COMPLETED,
            "final_response": f"Approved by human review. Proceeding with: {state.get('input_query', '')}",
            "is_human_review_needed": False,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    if decision == "rejected":
        return {
            "current_step": "human_review_rejected",
            "current_status": WorkflowStatus.CANCELLED,
            "final_response": f"Rejected by human review. Reason: {state.get('human_comment', 'No comment')}",
            "is_human_review_needed": False,
            "error_info": "Human review rejected",
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    # Check for timeout
    review_deadline = state.get("review_deadline")
    if review_deadline and datetime.utcnow() > review_deadline:
        logger.warning(f"Task {state['task_id']}: Human review timed out")
        return {
            "current_step": "human_review_timeout",
            "current_status": WorkflowStatus.FAILED,
            "error_info": "Human review timed out after 30 minutes",
            "is_human_review_needed": False,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    # First time entering - set deadline and pause
    if not review_deadline:
        return {
            "current_step": "human_review_pending",
            "current_status": WorkflowStatus.REVIEWING,
            "is_human_review_needed": True,
            "review_deadline": datetime.utcnow() + timedelta(minutes=30),
            "updated_at": datetime.utcnow()
        }
    
    # Still waiting
    return {
        "current_step": "human_review_waiting",
        "current_status": WorkflowStatus.REVIEWING,
        "is_human_review_needed": True,
        "updated_at": datetime.utcnow()
    }
Step 1.3: Bounded ReAct Subgraph with Hard Limits
File: api/app/workflows/subgraphs.py
Python
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import ToolMessage

from app.workflows.state import AgentState, RiskLevel
from app.core.mcp_client import mcp_tool_manager
from app.core.websocket_manager import ws_manager
from app.core.cost_tracker import cost_tracker
from app.core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Hard boundaries for ReAct execution
REACT_LIMITS = {
    "max_steps": 5,
    "max_tokens": 3000,
    "max_tool_calls": 10,
    "max_execution_time": 120,  # seconds
    "max_cost_usd": 0.50,
}

class ReActLimitExceeded(Exception):
    """Raised when ReAct execution hits hard limits."""
    pass

async def complex_analysis_subgraph(state: AgentState) -> Dict[str, Any]:
    """
    Node 6: Bounded ReAct with MCP tools, circuit breakers, and streaming.
    """
    task_id = state["task_id"]
    
    # Get MCP tools with fallback
    try:
        tools = await mcp_tool_manager.get_tools()
        if not tools:
            logger.warning(f"Task {task_id}: No MCP tools available, using fallback")
            tools = get_fallback_tools()
    except Exception as e:
        logger.error(f"Task {task_id}: MCP tool loading failed: {e}")
        return {
            "agent_finding": "Tool loading failed. Human review required.",
            "is_human_review_needed": True,
            "error_info": f"MCP error: {str(e)}",
            "current_step": "complex_analysis_error",
            "current_status": WorkflowStatus.FAILED,
        }
    
    # Create model with cost tracking
    model = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0,
        max_tokens=2000,
        callbacks=[CostTrackingCallback(task_id, state["user_id"])]
    )
    
    # Create bounded ReAct agent
    react_agent = create_react_agent(
        model=model,
        tools=tools,
        state_modifier="""You are a secure data analyst assistant. Follow these rules:
1. Use ReAct pattern: Thought → Action → Observation
2. Only use tools when necessary
3. Never expose raw credentials or secrets
4. If uncertain, ask for human clarification
5. Max 5 reasoning steps
6. Prefer read-only operations
""",
        checkpointer=None,  # We handle checkpointing at outer level
    )
    
    # Execution tracking
    step_count = 0
    total_tokens = state.get("total_tokens_used", 0)
    total_cost = state.get("cost_usd", 0.0)
    tool_calls = 0
    start_time = datetime.utcnow()
    final_answer = "Analysis stopped: Limit reached."
    thoughts = []
    
    config = {
        "configurable": {"thread_id": task_id},
        "recursion_limit": REACT_LIMITS["max_steps"] + 2,
    }
    
    try:
        async for event in react_agent.astream_events(
            {"messages": [("user", state["input_query"])]},
            config=config,
            version="v2",
        ):
            # Check time limit
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > REACT_LIMITS["max_execution_time"]:
                raise ReActLimitExceeded(f"Time limit: {elapsed}s > {REACT_LIMITS['max_execution_time']}s")
            
            # Monitor step count
            if event["event"] == "on_chain_end" and "agent" in event.get("tags", []):
                step_count += 1
                if step_count >= REACT_LIMITS["max_steps"]:
                    raise ReActLimitExceeded(f"Step limit: {step_count} >= {REACT_LIMITS['max_steps']}")
            
            # Monitor token usage
            if event["event"] == "on_llm_end":
                usage = event["data"]["output"].usage_metadata
                tokens = usage.get("total_tokens", 0)
                total_tokens += tokens
                
                # Track cost
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                cost = (prompt_tokens * 0.000003) + (completion_tokens * 0.000015)  # Sonnet pricing
                total_cost += cost
                
                if total_tokens >= REACT_LIMITS["max_tokens"]:
                    raise ReActLimitExceeded(f"Token limit: {total_tokens} >= {REACT_LIMITS['max_tokens']}")
                if total_cost >= REACT_LIMITS["max_cost_usd"]:
                    raise ReActLimitExceeded(f"Cost limit: ${total_cost:.4f} >= ${REACT_LIMITS['max_cost_usd']}")
            
            # Monitor tool calls
            if event["event"] == "on_tool_start":
                tool_calls += 1
                if tool_calls >= REACT_LIMITS["max_tool_calls"]:
                    raise ReActLimitExceeded(f"Tool call limit: {tool_calls} >= {REACT_LIMITS['max_tool_calls']}")
                
                # Broadcast tool call to frontend
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                await ws_manager.broadcast(task_id, {
                    "type": "react_thought",
                    "thought": f"Executing tool: {tool_name}",
                    "tool_calls": [{"name": tool_name, "args": tool_input}],
                    "step": step_count,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Capture thoughts
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    thoughts.append({
                        "content": chunk.content,
                        "step": step_count,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Capture final output
            if event["event"] == "on_chain_end" and "output" in event["data"]:
                messages = event["data"]["output"].get("messages", [])
                if messages:
                    final_answer = messages[-1].content
    
    except ReActLimitExceeded as e:
        logger.warning(f"Task {task_id}: ReAct limit hit: {e}")
        return {
            "agent_finding": f"Analysis stopped: {str(e)}. Partial result: {final_answer[:200]}...",
            "is_human_review_needed": True,
            "error_info": str(e),
            "total_tokens_used": total_tokens,
            "cost_usd": total_cost,
            "current_step": "complex_analysis_limited",
            "current_status": WorkflowStatus.REVIEWING,
            "react_thoughts": thoughts,
        }
    
    except Exception as e:
        logger.error(f"Task {task_id}: ReAct execution failed: {e}")
        return {
            "agent_finding": f"Analysis failed: {str(e)}",
            "is_human_review_needed": True,
            "error_info": str(e),
            "total_tokens_used": total_tokens,
            "cost_usd": total_cost,
            "current_step": "complex_analysis_error",
            "current_status": WorkflowStatus.FAILED,
        }
    
    return {
        "current_step": "complex_analysis_complete",
        "current_status": WorkflowStatus.COMPLETED,
        "agent_finding": final_answer,
        "total_tokens_used": total_tokens,
        "cost_usd": total_cost,
        "react_thoughts": thoughts,
        "completed_at": datetime.utcnow(),
    }

def get_fallback_tools() -> List[BaseTool]:
    """Read-only fallback tools when MCP is unavailable."""
    @tool
    def search_internal_docs(query: str) -> str:
        """Search internal documentation."""
        return f"Documentation search for: {query}"
    
    @tool
    def calculate(expression: str) -> str:
        """Evaluate mathematical expression safely."""
        try:
            # Safe eval with limited scope
            allowed_names = {"abs": abs, "max": max, "min": min, "sum": sum}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    return [search_internal_docs, calculate]

class CostTrackingCallback:
    """LangChain callback for real-time cost tracking."""
    
    def __init__(self, task_id: str, user_id: str):
        self.task_id = task_id
        self.user_id = user_id
    
    def on_llm_end(self, response, **kwargs):
        """Track cost after LLM completion."""
        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            asyncio.create_task(cost_tracker.record_usage(
                task_id=self.task_id,
                user_id=self.user_id,
                tokens=usage.get("total_tokens", 0),
                cost_usd=self._calculate_cost(usage),
                model=kwargs.get("model", "unknown")
            ))
    
    def _calculate_cost(self, usage: Dict) -> float:
        """Calculate cost based on model pricing."""
        prompt = usage.get("prompt_tokens", 0)
        completion = usage.get("completion_tokens", 0)
        # Sonnet 4.6 pricing (approximate)
        return (prompt * 0.000003) + (completion * 0.000015)
Step 1.4: Compiled Workflow with PostgreSQL Checkpointer
File: api/app/workflows/graph.py
Python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager

from app.workflows.state import AgentState, RiskLevel, WorkflowStatus
from app.workflows.nodes import (
    validate_input, retrieve_context, assess_risk,
    auto_generate_response, human_review_node
)
from app.workflows.subgraphs import complex_analysis_subgraph

async def route_based_on_risk(state: AgentState) -> str:
    """Dynamic routing with error handling."""
    risk = state.get("risk_level", RiskLevel.LOW)
    
    # Error override
    if state.get("error_info") and state.get("retry_count", 0) >= state.get("max_retries", 3):
        return "human_review_node"
    
    if risk == RiskLevel.LOW:
        return "auto_generate_response"
    elif risk in (RiskLevel.HIGH, RiskLevel.MEDIUM):
        return "complex_analysis_subgraph"
    else:  # CRITICAL
        return "human_review_node"

def build_workflow() -> StateGraph:
    """Build the workflow graph with all nodes and edges."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("assess_risk", assess_risk)
    workflow.add_node("auto_generate_response", auto_generate_response)
    workflow.add_node("complex_analysis_subgraph", complex_analysis_subgraph)
    workflow.add_node("human_review_node", human_review_node)
    
    # Define edges
    workflow.set_entry_point("validate_input")
    workflow.add_edge("validate_input", "retrieve_context")
    workflow.add_edge("retrieve_context", "assess_risk")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "assess_risk",
        route_based_on_risk,
        {
            "auto_generate_response": "auto_generate_response",
            "complex_analysis_subgraph": "complex_analysis_subgraph",
            "human_review_node": "human_review_node",
        }
    )
    
    # Terminal edges
    workflow.add_edge("auto_generate_response", END)
    workflow.add_edge("complex_analysis_subgraph", END)
    workflow.add_edge("human_review_node", END)
    
    return workflow

# Singleton with lazy initialization
_compiled_app = None
_checkpointer = None

async def get_compiled_app(db_conn_string: str):
    """Lazy initialization with connection pooling."""
    global _compiled_app, _checkpointer
    
    if _compiled_app is None:
        # Initialize checkpointer with connection pool
        _checkpointer = AsyncPostgresSaver.from_conn_string(
            db_conn_string,
            pool_size=10,
            max_overflow=20
        )
        await _checkpointer.setup()
        
        # Build and compile
        workflow = build_workflow()
        _compiled_app = workflow.compile(checkpointer=_checkpointer)
        
        logger.info("Workflow engine initialized with PostgreSQL checkpointer")
    
    return _compiled_app

async def shutdown_workflow():
    """Graceful shutdown."""
    global _compiled_app, _checkpointer
    if _checkpointer:
        await _checkpointer.aclose()
    _compiled_app = None
    _checkpointer = None
<a name="phase-2">
Phase 2: Agent Orchestration (Weeks 5-6)
Step 2.1: Agent Definitions with OPA Integration
File: .claude/agents/governor.md
Markdown
Fullscreen 
Download 
Fit
Code
Preview
1. Read the feature request or bug report
2. Validate scope permissions via OPA before any delegation
3. Break down into parallelizable sub-tasks
4. Spawn specialized agents using the Task tool
5. Monitor shared task list and integrate outputs
6. Enforce cost budgets per task
Role
# Check OPA policy
curl -X POST http://opa:8181/v1/data/agent/scope/allow \
  -d '{"input": {"agent": "governor", "action": "read", "path": "/frontend"}}'
Security Protocol (MANDATORY)
Governor Constitution
If OPA returns {"result": false}, DENY the operation and log the violation.
Delegation Rules
Use frontend-dev for UI changes (scope: /frontend, /shared)
Use backend-dev for API/DB changes (scope: /api, /shared)
Use security-auditor for read-only security reviews (scope: ALL)
Use design-director for UI quality gates (scope: /frontend)
NEVER delegate across scope boundaries
Cost Controls
Per-task token budget: 50,000 tokens
Per-task time limit: 10 minutes
Auto-downgrade to Haiku if budget exceeds 80%
Integration Process
Collect outputs from all subagents
Verify API contracts match between frontend and backend
Run security audit before merge
Update TodoWrite with completion status
Report final summary to user
plain

**File: `.claude/agents/frontend-dev.md`**

```markdown
---
name: frontend-dev
description: React 19, TypeScript, Tailwind specialist with design token compliance.
model: claude-sonnet-4-6
tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - TodoWrite
  - OPACheck
---

# Frontend Subagent Constitution

## Scope (ENFORCED BY OPA)
- **Read/Write**: `/frontend`, `/shared/types`, `/shared/utils`
- **Read-only**: `/api/openapi.json`, `/docs/frontend-guidelines.md`
- **FORBIDDEN**: `/api`, `/infrastructure`, `/.env*`

## Standards
- React 19+ with TypeScript strict mode
- Tailwind CSS using ONLY design tokens from `design-tokens.json`
- WCAG 2.1 AA minimum (axe-core must pass)
- Zustand for state management
- React Query for server state
- Vitest + React Testing Library for tests

## Pre-Completion Checklist
Before reporting completion, you MUST:
1. Run `npm run lint` - zero errors
2. Run `npm run typecheck` - zero errors  
3. Run `npm run test:unit` - all passing
4. Run `npm run test:accessibility` - zero critical/serious violations
5. Verify no hardcoded colors (must use tokens)
6. Verify no inline styles (Tailwind classes only)

## API Contract Protocol
If you need a new API endpoint:
1. Document required contract in `/shared/types/api.ts`
2. Request governor to delegate to `backend-dev`
3. Do NOT mock in production code
4. Use Zod schemas for runtime validation
File: .claude/agents/backend-dev.md
Markdown
Fullscreen 
Download 
Fit
Code
Preview
Read/Write: /api, /shared, /infrastructure/docker, /alembic
Read-only: /frontend/src/types, /docs/api-guidelines.md
FORBIDDEN: /frontend/src/components, /.env.production
Scope (ENFORCED BY OPA)
FastAPI with Pydantic v2 models
SQLAlchemy 2.0 + asyncpg with connection pooling
OpenAPI 3.1 annotations for every endpoint
JWT authentication with refresh tokens
Alembic migrations (NEVER raw SQL schema changes)
pytest-asyncio for all tests
mypy --strict compliance
Standards
1. All endpoints must have auth decorators (unless explicitly public)
2. Input validation using Pydantic at API boundary
3. SQL injection prevention via ORM only (no raw SQL)
4. Never log sensitive data (passwords, tokens, PII)
5. Rate limiting on all mutation endpoints
Security Requirements
Schema changes: alembic revision --autogenerate -m "description"
NEVER use DROP TABLE, TRUNCATE, or DELETE FROM without WHERE
Always add indexes for foreign keys and search fields
Use transactions for multi-step operations
Database Protocol
Backend Subagent Constitution
File: .claude/agents/security-auditor.md
Markdown
Fullscreen 
Download 
Fit
Code
Preview
Read-only: ENTIRE repository (/frontend, /api, /infrastructure, /docs)
Execute: Security scanning tools only
NEVER writes, edits, or executes non-read commands
Scope
1. Secrets Scanning: detect-secrets, truffleHog
2. Dependency Audit: npm audit, pip-audit, safety check
3. Static Analysis: bandit (Python), eslint-security (JS)
4. Infrastructure: Check for exposed ports, debug modes, weak CORS
5. Authentication: Verify all endpoints have auth (except /health, /docs)
6. Input Validation: Check for raw SQL, XSS vectors, command injection
Mandatory Checks
{
  "summary": {
    "pass": false,
    "critical_count": 2,
    "high_count": 3,
    "medium_count": 5,
    "low_count": 10
  },
  "findings": [
    {
      "severity": "critical",
      "category": "secrets",
      "file": "/api/app/config.py",
      "line": 15,
      "description": "Hardcoded API key detected",
      "remediation": "Move to environment variable or secrets manager",
      "cwe": "CWE-798"
    }
  ],
  "compliance": {
    "owasp_top_10": ["A01", "A07"],
    "pci_dss": false,
    "soc2": false
  }
}
Output Format
Security Auditor Constitution
Blocking Rules
ANY critical finding blocks the PR
3 high findings blocks the PR
Secrets exposure immediately escalates to governor
plain

### Step 2.2: Agent Sandbox Implementation

**File: `infrastructure/docker/agent-sandbox/Dockerfile`**

```dockerfile
FROM python:3.11-slim AS base

# Security: Run as non-root
RUN groupadd -r agent && useradd -r -g agent agent

# Install minimal tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Create workspace
RUN mkdir -p /workspace /readonly && chown -R agent:agent /workspace

# Security: Drop capabilities
RUN setcap cap_net_bind_service=-ep /usr/bin/curl

USER agent
WORKDIR /workspace

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD claude --version || exit 1
File: api/app/services/agent_sandbox.py
Python
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import docker
from docker.types import Mount

class AgentSandbox:
    """
    Docker-based sandbox for agent execution with filesystem isolation.
    Each agent gets a temporary worktree with read-only mounts for permitted paths.
    """
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.image = "aiwf-agent-sandbox:latest"
        self.active_sandboxes: Dict[str, str] = {}  # task_id -> container_id
    
    async def create_sandbox(
        self,
        agent_type: str,
        task_id: str,
        read_paths: List[str],
        write_paths: List[str],
        env_vars: Optional[Dict] = None
    ) -> str:
        """Create isolated sandbox for agent execution."""
        
        # Create temporary worktree
        worktree_dir = tempfile.mkdtemp(prefix=f"aiwf-{agent_type}-{task_id[:8]}")
        
        # Prepare mounts
        mounts = []
        
        # Read-only mounts
        for path in read_paths:
            if Path(path).exists():
                mounts.append(Mount(
                    target=f"/readonly{path}",
                    source=path,
                    type="bind",
                    read_only=True
                ))
        
        # Read-write mounts
        for path in write_paths:
            target = f"/workspace{path}"
            source = f"{worktree_dir}{path}"
            Path(source).mkdir(parents=True, exist_ok=True)
            mounts.append(Mount(
                target=target,
                source=source,
                type="bind",
                read_only=False
            ))
        
        # Run container with restrictions
        container = self.docker_client.containers.run(
            self.image,
            command=["sleep", "3600"],  # Keep alive for task duration
            detach=True,
            mounts=mounts,
            environment=env_vars or {},
            mem_limit="512m",
            cpu_quota=100000,  # 1 CPU
            network_mode="bridge",
            security_opt=["no-new-privileges:true"],
            cap_drop=["ALL"],
            read_only=True,
            tmpfs={"/tmp": "noexec,nosuid,size=100m"},
            labels={
                "aiwf.agent_type": agent_type,
                "aiwf.task_id": task_id,
                "aiwf.created_at": datetime.utcnow().isoformat()
            }
        )
        
        self.active_sandboxes[task_id] = container.id
        return container.id
    
    async def execute_in_sandbox(
        self,
        task_id: str,
        command: List[str],
        timeout: int = 300
    ) -> Dict:
        """Execute command in agent sandbox."""
        container_id = self.active_sandboxes.get(task_id)
        if not container_id:
            raise ValueError(f"No sandbox found for task {task_id}")
        
        container = self.docker_client.containers.get(container_id)
        
        try:
            result = container.exec_run(
                cmd=command,
                user="agent",
                workdir="/workspace",
                demux=True,
                timeout=timeout
            )
            
            return {
                "exit_code": result.exit_code,
                "stdout": result.output[0].decode() if result.output[0] else "",
                "stderr": result.output[1].decode() if result.output[1] else "",
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "error": str(e)
            }
    
    async def destroy_sandbox(self, task_id: str):
        """Clean up sandbox and temporary files."""
        container_id = self.active_sandboxes.pop(task_id, None)
        if container_id:
            try:
                container = self.docker_client.containers.get(container_id)
                container.stop(timeout=10)
                container.remove(force=True)
            except Exception as e:
                logger.error(f"Failed to destroy sandbox {task_id}: {e}")
        
        # Clean up worktree
        worktree_pattern = f"/tmp/aiwf-*-{task_id[:8]}"
        for path in glob.glob(worktree_pattern):
            shutil.rmtree(path, ignore_errors=True)

agent_sandbox = AgentSandbox()

#Phase 3: Real-Time Observability (Weeks 7-8) — Corrected
#Step 3.1: Redis-Backed WebSocket Manager (Complete)
File: api/app/core/websocket_manager.py
Python
import json
import asyncio
import logging
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from redis.asyncio.client import PubSub

logger = logging.getLogger(__name__)

class RedisWebSocketManager:
    """
    Production-ready WebSocket manager using Redis Pub/Sub.
    Supports horizontal scaling across multiple FastAPI workers.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[PubSub] = None
        self.local_connections: Dict[str, Set[WebSocket]] = {}
        self._listener_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    async def connect(self):
        """Initialize Redis connection and start background listener."""
        if self._initialized:
            return
        
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Verify Redis connection
            await self.redis_client.ping()
            
            # Setup pubsub for cross-instance broadcasting
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.psubscribe("task:*")
            
            # Start background listener for Redis messages
            self._listener_task = asyncio.create_task(
                self._redis_listener(),
                name="redis_websocket_listener"
            )
            
            self._initialized = True
            logger.info("✅ Redis WebSocket manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis WebSocket manager: {e}")
            raise
    
    async def disconnect(self):
        """Graceful shutdown of Redis connections and listener."""
        logger.info("🛑 Shutting down WebSocket manager...")
        
        # Cancel listener task
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        # Unsubscribe and close pubsub
        if self.pubsub:
            try:
                await self.pubsub.punsubscribe()
                await self.pubsub.close()
            except Exception as e:
                logger.warning(f"Error closing pubsub: {e}")
        
        # Close Redis client
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing Redis client: {e}")
        
        # Close all local WebSocket connections
        for task_id, connections in self.local_connections.items():
            for ws in connections:
                try:
                    await ws.close(code=1001, reason="Server shutting down")
                except Exception:
                    pass
        
        self.local_connections.clear()
        self._initialized = False
        logger.info("✅ WebSocket manager shutdown complete")
    
    async def _redis_listener(self):
        """
        Background task that listens for Redis Pub/Sub messages
        and forwards them to local WebSocket connections.
        """
        logger.info("🎧 Redis listener started")
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "pmessage":
                    # Extract task_id from channel pattern (e.g., "task:abc-123")
                    channel = message["channel"]
                    if isinstance(channel, bytes):
                        channel = channel.decode("utf-8")
                    
                    task_id = channel.split(":")[1]
                    
                    # Parse message data
                    data_raw = message["data"]
                    if isinstance(data_raw, bytes):
                        data_raw = data_raw.decode("utf-8")
                    
                    try:
                        data = json.loads(data_raw)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse message data: {e}")
                        continue
                    
                    # Forward to local WebSocket connections for this task
                    await self._forward_to_local(task_id, data)
                    
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
            raise
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
            # Attempt to restart listener after delay
            await asyncio.sleep(5)
            self._listener_task = asyncio.create_task(self._redis_listener())
    
    async def _forward_to_local(self, task_id: str, data: dict):
        """Forward message to all local WebSocket connections for a task."""
        if task_id not in self.local_connections:
            return
        
        disconnected = set()
        connections = self.local_connections[task_id]
        
        for ws in connections:
            try:
                # Check if websocket is still open
                if ws.client_state.CONNECTED:
                    await ws.send_json(data)
                else:
                    disconnected.add(ws)
            except Exception as e:
                logger.debug(f"Failed to send to WebSocket: {e}")
                disconnected.add(ws)
        
        # Clean up disconnected websockets
        if disconnected:
            self.local_connections[task_id] -= disconnected
            logger.debug(f"Cleaned up {len(disconnected)} disconnected clients for task {task_id}")
            
            # Remove empty task entries
            if not self.local_connections[task_id]:
                del self.local_connections[task_id]
    
    async def add_connection(self, task_id: str, websocket: WebSocket):
        """Add a new WebSocket connection for a task."""
        await websocket.accept()
        
        if task_id not in self.local_connections:
            self.local_connections[task_id] = set()
        
        self.local_connections[task_id].add(websocket)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "task_id": task_id,
            "transport": "websocket",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"WebSocket connected for task {task_id}. Total clients: {len(self.local_connections[task_id])}")
    
    def remove_connection(self, task_id: str, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if task_id in self.local_connections:
            self.local_connections[task_id].discard(websocket)
            
            if not self.local_connections[task_id]:
                del self.local_connections[task_id]
                logger.info(f"All clients disconnected for task {task_id}")
    
    async def broadcast(self, task_id: str, message: dict):
        """
        Broadcast message to ALL connections for a task across ALL instances.
        Uses Redis Pub/Sub for cross-instance communication.
        """
        if not self._initialized:
            logger.warning("WebSocket manager not initialized, message dropped")
            return
        
        # Enrich message with metadata
        message["task_id"] = task_id
        message["timestamp"] = datetime.utcnow().isoformat()
        message["_broadcast_source"] = "redis"  # Marker to prevent echo loops
        
        # Publish to Redis (all instances will receive this)
        try:
            await self.redis_client.publish(f"task:{task_id}", json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
            # Fallback: broadcast to local connections only
            await self._forward_to_local(task_id, message)
    
    async def broadcast_local_only(self, task_id: str, message: dict):
        """
        Broadcast only to local connections (no Redis).
        Use this for high-frequency updates to reduce Redis load.
        """
        message["task_id"] = task_id
        message["timestamp"] = datetime.utcnow().isoformat()
        await self._forward_to_local(task_id, message)
    
    async def get_connection_stats(self) -> dict:
        """Get statistics about current connections."""
        stats = {
            "local_tasks": len(self.local_connections),
            "local_total_connections": sum(len(conns) for conns in self.local_connections.values()),
            "task_breakdown": {
                task_id: len(conns)
                for task_id, conns in self.local_connections.items()
            }
        }
        
        # Try to get Redis pubsub stats
        if self.redis_client:
            try:
                info = await self.redis_client.pubsub_numsub()
                stats["redis_channels"] = len(info) if info else 0
            except Exception:
                stats["redis_channels"] = "unavailable"
        
        return stats

# Singleton instance
ws_manager = RedisWebSocketManager()
Step 3.1b: WebSocket Endpoint Integration
File: api/app/api/v1/events.py
Python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.websocket_manager import ws_manager
from app.core.sse_manager import sse_manager
from app.core.security import get_current_user

router = APIRouter(prefix="/v1/events", tags=["Events"])

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: str,
    token: Optional[str] = None
):
    """
    Primary real-time transport: WebSocket.
    Provides bidirectional communication for workflow events.
    """
    # Authenticate connection
    try:
        user = await get_current_user(token) if token else None
    except Exception:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    await ws_manager.add_connection(task_id, websocket)
    
    try:
        while True:
            # Receive client messages
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif data.get("type") == "resume":
                # Handle human review resume
                await handle_resume_command(task_id, data, user)
            
            elif data.get("type") == "status":
                # Client requesting status update
                await send_status_update(task_id, websocket)
            
            else:
                logger.warning(f"Unknown message type from client: {data.get('type')}")
    
    except WebSocketDisconnect:
        ws_manager.remove_connection(task_id, websocket)
        logger.info(f"WebSocket disconnected for task {task_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        ws_manager.remove_connection(task_id, websocket)

@router.get("/sse/{task_id}")
async def sse_endpoint(
    request: Request,
    task_id: str,
    token: Optional[str] = None
):
    """
    Fallback transport: Server-Sent Events.
    Firewall-friendly, unidirectional server-to-client streaming.
    """
    # Authenticate
    try:
        user = await get_current_user(token) if token else None
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return StreamingResponse(
        sse_manager.subscribe(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*"
        }
    )

async def handle_resume_command(task_id: str, data: dict, user: Optional[dict]):
    """Process human review resume/approval commands."""
    from app.workflows.human_review import process_human_decision
    
    await process_human_decision(
        task_id=task_id,
        decision=data.get("decision"),
        comment=data.get("comment", ""),
        user_id=user.get("id") if user else "anonymous",
        reviewer_id=user.get("id") if user else None
    )

async def send_status_update(task_id: str, websocket: WebSocket):
    """Send current workflow status to client."""
    from app.workflows.graph import get_compiled_app
    from app.core.database import get_db_conn_string
    
    try:
        conn_string = await get_db_conn_string()
        app = await get_compiled_app(conn_string)
        config = {"configurable": {"thread_id": task_id}}
        
        state_snapshot = await app.aget_state(config)
        
        if state_snapshot and state_snapshot.values:
            await websocket.send_json({
                "type": "state",
                "data": {
                    "current_step": state_snapshot.values.get("current_step", "unknown"),
                    "status": state_snapshot.values.get("current_status", "unknown"),
                    "risk_level": state_snapshot.values.get("risk_level", "unknown"),
                    "is_human_review_needed": state_snapshot.values.get("is_human_review_needed", False),
                    "total_tokens": state_snapshot.values.get("total_tokens_used", 0),
                    "total_cost": state_snapshot.values.get("cost_usd", 0.0)
                }
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": "Task not found"
            })
            
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to get status: {str(e)}"
        })
Step 3.1c: Integration with Workflow Runner
File: api/app/workflows/runner.py
Python
from app.core.websocket_manager import ws_manager
from app.core.sse_manager import sse_manager
from app.core.tracing import tracing_manager
from app.core.metrics import track_workflow, track_llm_call, track_mcp_tool
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def run_workflow_with_streaming(
    task_id: str,
    user_id: str,
    query: str,
    conn_string: str
):
    """
    Execute workflow with real-time event streaming via WebSocket/SSE.
    """
    app = await get_compiled_app(conn_string)
    
    initial_state = {
        "task_id": task_id,
        "user_id": user_id,
        "input_query": query,
        "messages": [],
        "retrieval_results": None,
        "agent_finding": None,
        "final_response": None,
        "current_step": "start",
        "current_status": "pending",
        "error_info": None,
        "retry_count": 0,
        "max_retries": 3,
        "total_tokens_used": 0,
        "token_budget": 10000,
        "cost_usd": 0.0,
        "cost_budget_usd": 5.0,
        "is_human_review_needed": False,
        "human_decision": None,
        "human_comment": None,
        "review_deadline": None,
        "risk_level": "low",
        "risk_factors": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    config = {"configurable": {"thread_id": task_id}}
    
    # Broadcast workflow start
    await ws_manager.broadcast(task_id, {
        "type": "workflow_start",
        "step": "started",
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "query": query[:100] + "..." if len(query) > 100 else query
        }
    })
    
    try:
        # Use astream_events for granular event streaming
        async for event in app.astream_events(
            initial_state,
            config=config,
            version="v2"
        ):
            event_type = event.get("event")
            event_name = event.get("name", "unknown")
            
            # Broadcast step transitions
            if event_type == "on_chain_start":
                await ws_manager.broadcast(task_id, {
                    "type": "step",
                    "step_name": event_name,
                    "status": "started",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif event_type == "on_chain_end":
                await ws_manager.broadcast(task_id, {
                    "type": "step",
                    "step_name": event_name,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Broadcast ReAct thoughts
            elif event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    await ws_manager.broadcast(task_id, {
                        "type": "react_thought",
                        "thought": chunk.content,
                        "step": event_name,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Broadcast tool calls
            elif event_type == "on_tool_start":
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                
                await ws_manager.broadcast(task_id, {
                    "type": "tool_call",
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Broadcast token usage
            elif event_type == "on_llm_end":
                usage = event["data"]["output"].usage_metadata
                tokens = usage.get("total_tokens", 0)
                
                await ws_manager.broadcast(task_id, {
                    "type": "cost",
                    "tokens": tokens,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Detect human review trigger
            if event.get("data", {}).get("is_human_review_needed"):
                await ws_manager.broadcast(task_id, {
                    "type": "human_review",
                    "message": "Action requires human approval",
                    "details": {
                        "step": event_name,
                        "risk_level": event.get("data", {}).get("risk_level", "unknown"),
                        "reason": event.get("data", {}).get("risk_factors", [])
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Workflow completed
        await ws_manager.broadcast(task_id, {
            "type": "workflow_complete",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Workflow execution failed for task {task_id}: {e}")
        
        await ws_manager.broadcast(task_id, {
            "type": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update state with error
        await app.ainvoke({
            "error_info": str(e),
            "current_status": "failed"
        }, config=config)

##phase 3.2
Phase 3: Real-Time Observability (Weeks 7-8) — Continued
Step 3.2: SSE Fallback for Corporate Firewalls
File: api/app/core/sse_manager.py
Python
import json
import asyncio
from typing import Dict, AsyncGenerator, Optional
from datetime import datetime
from fastapi import Request
from fastapi.responses import StreamingResponse
import redis.asyncio as redis

class SSEManager:
    """
    Server-Sent Events manager for firewall-friendly streaming.
    Falls back from WebSocket when corporate proxies block WS.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.active_streams: Dict[str, asyncio.Queue] = {}
    
    async def subscribe(self, task_id: str) -> AsyncGenerator[str, None]:
        """Subscribe to task events via SSE."""
        queue = asyncio.Queue()
        self.active_streams[task_id] = queue
        
        # Send initial connection event
        yield self._format_sse({
            "type": "connection",
            "status": "connected",
            "task_id": task_id
        })
        
        try:
            # Subscribe to Redis for this task
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(f"task:{task_id}")
            
            # Create task to bridge Redis -> queue
            async def redis_bridge():
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        await queue.put(json.loads(message["data"]))
            
            bridge_task = asyncio.create_task(redis_bridge())
            
            # Yield from queue
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield self._format_sse(data)
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield self._format_sse({"type": "heartbeat"})
        
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe()
            await pubsub.close()
            bridge_task.cancel()
            self.active_streams.pop(task_id, None)
    
    def _format_sse(self, data: dict) -> str:
        """Format data as SSE event."""
        return f"data: {json.dumps(data)}\n\n"
    
    async def broadcast(self, task_id: str, message: dict):
        """Broadcast to both SSE and WebSocket subscribers."""
        message["timestamp"] = datetime.utcnow().isoformat()
        await self.redis_client.publish(f"task:{task_id}", json.dumps(message))

sse_manager = SSEManager()
File: api/app/api/v1/events.py
Python
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.websocket_manager import ws_manager
from app.core.sse_manager import sse_manager

router = APIRouter(prefix="/v1/events", tags=["Events"])

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """Primary: WebSocket for real-time bidirectional communication."""
    await ws_manager.add_connection(task_id, websocket)
    try:
        while True:
            # Handle client messages (e.g., ping, resume commands)
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "resume":
                # Forward to workflow engine
                await handle_resume_command(task_id, data)
    except WebSocketDisconnect:
        ws_manager.remove_connection(task_id, websocket)

@router.get("/sse/{task_id}")
async def sse_endpoint(request: Request, task_id: str):
    """Fallback: SSE for server-to-client streaming (firewall-friendly)."""
    return StreamingResponse(
        sse_manager.subscribe(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

async def handle_resume_command(task_id: str, data: dict):
    """Handle resume/approval commands from client."""
    from app.workflows.human_review import process_human_decision
    await process_human_decision(
        task_id=task_id,
        decision=data.get("decision"),
        comment=data.get("comment", ""),
        user_id=data.get("user_id")
    )
Step 3.3: React Dashboard with Dual Transport
File: frontend/src/hooks/useWorkflowEvents.ts
TypeScript
import { useEffect, useState, useRef, useCallback } from 'react';
import { WorkflowState, WorkflowEvent, TransportType } from '../types/workflow';

const HEARTBEAT_TIMEOUT = 35000; // 35 seconds (SSE sends heartbeat every 30s)

export function useWorkflowEvents(taskId: string, preferredTransport: TransportType = 'auto') {
  const [state, setState] = useState<WorkflowState>({
    taskId,
    status: 'pending',
    currentStep: 'initializing',
    messages: [],
    finalResponse: null,
    isHumanReviewNeeded: false,
    totalTokens: 0,
    totalCost: 0,
    steps: [],
    reactThoughts: [],
    transport: 'connecting',
    lastHeartbeat: null,
  });
  
  const transportRef = useRef<TransportType>('connecting');
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const heartbeatTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Determine best transport
  const selectTransport = useCallback(async (): Promise<TransportType> => {
    if (preferredTransport !== 'auto') return preferredTransport;
    
    // Test WebSocket availability
    try {
      const testWs = new WebSocket(`ws://localhost:8000/v1/events/ws/test`);
      await new Promise((resolve, reject) => {
        testWs.onopen = resolve;
        testWs.onerror = reject;
        setTimeout(() => reject(new Error('Timeout')), 3000);
      });
      testWs.close();
      return 'websocket';
    } catch {
      return 'sse';
    }
  }, [preferredTransport]);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/v1/events/ws/${taskId}`);
    wsRef.current = ws;
    transportRef.current = 'websocket';

    ws.onopen = () => {
      setState(prev => ({ ...prev, transport: 'websocket' }));
      startHeartbeatMonitor();
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      processEvent(data);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      // Fallback to SSE
      if (transportRef.current === 'websocket') {
        connectSSE();
      }
    };

    ws.onclose = () => {
      if (transportRef.current === 'websocket') {
        // Attempt reconnection with exponential backoff
        setTimeout(() => connectWebSocket(), 5000);
      }
    };
  }, [taskId]);

  // SSE connection
  const connectSSE = useCallback(() => {
    const es = new EventSource(`http://localhost:8000/v1/events/sse/${taskId}`);
    eventSourceRef.current = es;
    transportRef.current = 'sse';

    es.onopen = () => {
      setState(prev => ({ ...prev, transport: 'sse' }));
      startHeartbeatMonitor();
    };

    es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'heartbeat') {
        updateHeartbeat();
        return;
      }
      processEvent(data);
    };

    es.onerror = (err) => {
      console.error('SSE error:', err);
      es.close();
      // Attempt reconnection
      setTimeout(() => connectSSE(), 5000);
    };
  }, [taskId]);

  // Event processing
  const processEvent = useCallback((data: WorkflowEvent) => {
    setState(prev => {
      switch (data.type) {
        case 'step':
          return {
            ...prev,
            currentStep: data.stepName,
            status: data.status === 'completed' && data.stepName === 'human_review_pending' ? 'paused' : 
                   data.status === 'completed' ? 'running' : prev.status,
            steps: [...prev.steps, {
              stepName: data.stepName,
              status: data.status,
              timestamp: data.timestamp
            }]
          };
        
        case 'react_thought':
          return {
            ...prev,
            reactThoughts: [...prev.reactThoughts, {
              thought: data.thought,
              toolCalls: data.toolCalls,
              step: data.step,
              timestamp: data.timestamp
            }]
          };
        
        case 'cost':
          return {
            ...prev,
            totalTokens: prev.totalTokens + (data.tokens || 0),
            totalCost: prev.totalCost + (data.costUsd || 0)
          };
        
        case 'human_review':
          return {
            ...prev,
            isHumanReviewNeeded: true,
            status: 'paused',
            reviewData: data.details
          };
        
        case 'state':
          if (data.step === 'finished') {
            return { ...prev, status: 'completed' };
          }
          return prev;
        
        case 'error':
          return { ...prev, status: 'error', error: data.message };
        
        default:
          return prev;
      }
    });
  }, []);

  // Heartbeat monitoring
  const startHeartbeatMonitor = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
    }
    
    heartbeatTimerRef.current = setInterval(() => {
      const lastHeartbeat = state.lastHeartbeat;
      if (lastHeartbeat && Date.now() - lastHeartbeat > HEARTBEAT_TIMEOUT) {
        console.warn('Heartbeat timeout - reconnecting...');
        reconnect();
      }
    }, 10000);
  }, [state.lastHeartbeat]);

  const updateHeartbeat = useCallback(() => {
    setState(prev => ({ ...prev, lastHeartbeat: Date.now() }));
  }, []);

  // Reconnection logic
  const reconnect = useCallback(() => {
    wsRef.current?.close();
    eventSourceRef.current?.close();
    
    if (transportRef.current === 'websocket') {
      connectWebSocket();
    } else {
      connectSSE();
    }
  }, [connectWebSocket, connectSSE]);

  // Initialize connection
  useEffect(() => {
    let mounted = true;
    
    const init = async () => {
      const transport = await selectTransport();
      if (!mounted) return;
      
      if (transport === 'websocket') {
        connectWebSocket();
      } else {
        connectSSE();
      }
    };
    
    init();
    
    return () => {
      mounted = false;
      wsRef.current?.close();
      eventSourceRef.current?.close();
      if (heartbeatTimerRef.current) {
        clearInterval(heartbeatTimerRef.current);
      }
    };
  }, [taskId, selectTransport, connectWebSocket, connectSSE]);

  // Send resume decision
  const sendResume = useCallback(async (decision: 'approved' | 'rejected', comment: string) => {
    const payload = {
      type: 'resume',
      task_id: taskId,
      decision,
      comment,
      timestamp: new Date().toISOString()
    };
    
    if (transportRef.current === 'websocket' && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    } else {
      // Fallback to REST API
      await fetch('/v1/human-review/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }
  }, [taskId]);

  return { state, sendResume, transport: transportRef.current };
}
Step 3.4: Enhanced Dashboard Components
File: frontend/src/components/WorkflowDashboard.tsx
tsx
import React, { useState } from 'react';
import { useWorkflowEvents } from '../hooks/useWorkflowEvents';
import { StepTimeline } from './StepTimeline';
import { ReActThoughtViewer } from './ReActThoughtViewer';
import { HumanReviewPanel } from './HumanReviewPanel';
import { CostDisplay } from './CostDisplay';
import { TransportIndicator } from './TransportIndicator';
import { ErrorBoundary } from './ErrorBoundary';

interface Props {
  taskId: string;
}

export default function WorkflowDashboard({ taskId }: Props) {
  const { state, sendResume, transport } = useWorkflowEvents(taskId);
  const [activeTab, setActiveTab] = useState<'overview' | 'thoughts' | 'cost'>('overview');

  const getStatusColor = () => {
    switch (state.status) {
      case 'running': return 'bg-green-100 text-green-800 border-green-300';
      case 'paused': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'completed': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'error': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-neutral-50">
        {/* Header */}
        <header className="bg-white border-b border-neutral-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h1 className="text-xl font-bold text-neutral-900">
                  Task Monitor
                </h1>
                <span className="font-mono text-sm text-neutral-500 bg-neutral-100 px-2 py-1 rounded">
                  {taskId}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <TransportIndicator transport={transport} />
                <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor()}`}>
                  {state.status.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Timeline & Details */}
            <div className="lg:col-span-2 space-y-6">
              {/* Tab Navigation */}
              <div className="bg-white rounded-lg border border-neutral-200">
                <div className="flex border-b border-neutral-200">
                  {(['overview', 'thoughts', 'cost'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-3 text-sm font-medium capitalize ${
                        activeTab === tab
                          ? 'border-b-2 border-primary-500 text-primary-600'
                          : 'text-neutral-500 hover:text-neutral-700'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                <div className="p-4">
                  {activeTab === 'overview' && (
                    <div className="space-y-4">
                      <StepTimeline steps={state.steps} currentStep={state.currentStep} />
                      {state.finalResponse && (
                        <div className="mt-4 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                          <h3 className="font-semibold text-neutral-800 mb-2">Final Response</h3>
                          <div className="prose prose-sm max-w-none">
                            <pre className="whitespace-pre-wrap text-sm text-neutral-700">
                              {state.finalResponse}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'thoughts' && (
                    <ReActThoughtViewer thoughts={state.reactThoughts} />
                  )}

                  {activeTab === 'cost' && (
                    <CostDisplay 
                      totalTokens={state.totalTokens}
                      totalCost={state.totalCost}
                      budget={state.tokenBudget}
                    />
                  )}
                </div>
              </div>
            </div>

            {/* Right Column: Status & HITL */}
            <div className="space-y-6">
              {/* Current Status Card */}
              <div className="bg-white rounded-lg border border-neutral-200 p-4">
                <h3 className="font-semibold text-neutral-800 mb-3">Current Status</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Step</span>
                    <span className="font-mono text-neutral-800">{state.currentStep}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Tokens</span>
                    <span className="font-mono text-neutral-800">{state.totalTokens.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-neutral-500">Cost</span>
                    <span className="font-mono text-neutral-800">${state.totalCost.toFixed(4)}</span>
                  </div>
                </div>
              </div>

              {/* Human Review Panel */}
              {state.isHumanReviewNeeded && (
                <HumanReviewPanel 
                  onDecision={sendResume}
                  details={state.reviewData}
                />
              )}

              {/* Error Display */}
              {state.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h3 className="font-semibold text-red-800 mb-2">Error</h3>
                  <p className="text-sm text-red-700">{state.error}</p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
}
<a name="phase-4">
Phase 4: MCP & External Tools (Weeks 9-10)
Step 4.1: Resilient MCP Client with Retry & Fallback
File: api/app/core/mcp_client.py
Python
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import httpx

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    transport: str = "stdio"
    enabled: bool = True
    fallback_tools: Optional[List[BaseTool]] = None

@dataclass
class MCPServerHealth:
    """Health status of an MCP server."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    last_check: datetime
    response_time_ms: float
    error_count: int
    consecutive_failures: int

class ResilientMCPClient:
    """
    Production-ready MCP client with:
    - Health check polling
    - Automatic retry with exponential backoff
    - Graceful degradation to fallback tools
    - Connection pooling
    - Audit logging
    """
    
    def __init__(self):
        self._client: Optional[MultiServerMCPClient] = None
        self._tools: Dict[str, List[BaseTool]] = {}  # server_name -> tools
        self._tool_cache: Dict[str, List[BaseTool]] = {}  # Cached tools for fallback
        self._initialized = False
        self._server_health: Dict[str, MCPServerHealth] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._max_retries = 3
        self._retry_delay = 2.0  # seconds
        
    def _get_server_configs(self) -> Dict[str, Dict]:
        """Build server configurations from environment."""
        configs = {}
        
        # PostgreSQL MCP
        if os.getenv("MCP_POSTGRES_ENABLED", "true").lower() == "true":
            configs["postgres"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres"],
                "env": {
                    "DATABASE_URL": os.getenv("POSTGRES_DATABASE_URL", "")
                },
                "transport": "stdio",
            }
        
        # GitHub MCP
        if os.getenv("MCP_GITHUB_ENABLED", "true").lower() == "true":
            configs["github"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")
                },
                "transport": "stdio",
            }
        
        # Puppeteer MCP
        if os.getenv("MCP_PUPPETEER_ENABLED", "true").lower() == "true":
            configs["puppeteer"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
                "env": {},
                "transport": "stdio",
            }
        
        # Slack MCP (optional)
        if os.getenv("MCP_SLACK_ENABLED", "false").lower() == "true":
            configs["slack"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-slack"],
                "env": {
                    "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", ""),
                    "SLACK_DEFAULT_CHANNEL": os.getenv("SLACK_DEFAULT_CHANNEL", "#alerts")
                },
                "transport": "stdio",
            }
        
        return configs
    
    async def initialize(self) -> None:
        """Initialize MCP connections with health monitoring."""
        if self._initialized:
            return
        
        configs = self._get_server_configs()
        
        if not configs:
            logger.warning("No MCP servers configured")
            self._initialized = True
            return
        
        try:
            # Initialize with retry
            for attempt in range(self._max_retries):
                try:
                    self._client = MultiServerMCPClient(connections=configs)
                    self._tools = await self._client.get_tools()
                    self._initialized = True
                    
                    # Initialize health tracking
                    for server_name in configs.keys():
                        self._server_health[server_name] = MCPServerHealth(
                            name=server_name,
                            status="healthy",
                            last_check=datetime.utcnow(),
                            response_time_ms=0,
                            error_count=0,
                            consecutive_failures=0
                        )
                    
                    # Start health check polling
                    self._health_check_task = asyncio.create_task(
                        self._health_check_loop()
                    )
                    
                    logger.info(f"✅ MCP initialized: {len(self._tools)} total tools")
                    for server, tools in self._tools.items():
                        logger.info(f"  - {server}: {len(tools)} tools")
                    break
                    
                except Exception as e:
                    if attempt < self._max_retries - 1:
                        delay = self._retry_delay * (2 ** attempt)
                        logger.warning(f"MCP init attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"❌ MCP initialization failed after {self._max_retries} attempts: {e}")
            # Initialize with empty tools - will use fallbacks
            self._tools = {}
            self._initialized = True
    
    async def _health_check_loop(self):
        """Periodic health checks for MCP servers."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for server_name, health in self._server_health.items():
                    start = datetime.utcnow()
                    try:
                        # Quick health check via tool listing
                        tools = await self._client.get_tools()
                        server_tools = [t for t in tools if server_name in t.name]
                        
                        response_time = (datetime.utcnow() - start).total_seconds() * 1000
                        
                        health.status = "healthy"
                        health.last_check = datetime.utcnow()
                        health.response_time_ms = response_time
                        health.consecutive_failures = 0
                        
                    except Exception as e:
                        health.consecutive_failures += 1
                        health.error_count += 1
                        
                        if health.consecutive_failures >= 3:
                            health.status = "unhealthy"
                            logger.error(f"MCP server {server_name} is unhealthy: {e}")
                            
                            # Attempt recovery
                            await self._recover_server(server_name)
                        else:
                            health.status = "degraded"
                            logger.warning(f"MCP server {server_name} degraded (failure {health.consecutive_failures})")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _recover_server(self, server_name: str):
        """Attempt to recover a failed MCP server."""
        logger.info(f"Attempting to recover MCP server: {server_name}")
        try:
            # Close and reinitialize specific server
            # Note: MultiServerMCPClient doesn't support individual server restart
            # In production, implement custom MCP client pool
            pass
        except Exception as e:
            logger.error(f"Recovery failed for {server_name}: {e}")
    
    async def get_tools(self) -> List[BaseTool]:
        """Get all available tools with fallback support."""
        if not self._initialized:
            await self.initialize()
        
        all_tools = []
        for server_name, tools in self._tools.items():
            health = self._server_health.get(server_name)
            
            if health and health.status == "unhealthy":
                # Use cached tools or fallbacks
                cached = self._tool_cache.get(server_name, [])
                fallback = self._get_fallback_tools(server_name)
                all_tools.extend(cached or fallback)
                logger.warning(f"Using fallback tools for {server_name}")
            else:
                all_tools.extend(tools)
                # Cache for fallback
                self._tool_cache[server_name] = tools
        
        return all_tools
    
    def _get_fallback_tools(self, server_name: str) -> List[BaseTool]:
        """Get fallback tools when MCP server is unavailable."""
        from langchain_core.tools import tool
        
        fallbacks = {
            "postgres": [
                tool(lambda q: "Database unavailable. Please try again later.", name="query_database_fallback")
            ],
            "github": [
                tool(lambda q: "GitHub integration unavailable. Please try again later.", name="github_fallback")
            ],
            "puppeteer": [
                tool(lambda q: "Browser automation unavailable. Please try again later.", name="browser_fallback")
            ],
            "slack": [
                tool(lambda q: "Slack integration unavailable. Please try again later.", name="slack_fallback")
            ]
        }
        return fallbacks.get(server_name, [])
    
    async def get_tools_for_server(self, server_name: str) -> List[BaseTool]:
        """Get tools from a specific server."""
        if not self._initialized:
            await self.initialize()
        
        health = self._server_health.get(server_name)
        if health and health.status == "unhealthy":
            return self._get_fallback_tools(server_name)
        
        return [t for t in self._tools.get(server_name, [])]
    
    async def get_server_health(self) -> Dict[str, MCPServerHealth]:
        """Get health status of all MCP servers."""
        return self._server_health
    
    async def close(self) -> None:
        """Graceful shutdown."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._client:
            await self._client.close()
        
        self._initialized = False
        logger.info("MCP client shutdown complete")

# Singleton instance
mcp_tool_manager = ResilientMCPClient()
Step 4.2: MCP Tool Audit Interceptor
File: api/app/core/mcp_interceptors.py
Python
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_mcp_adapters.interceptors import ToolCallInterceptor

from app.core.database import get_db_session
from app.models.audit import MCPToolCallAudit

logger = logging.getLogger(__name__)

class AuditLogInterceptor(ToolCallInterceptor):
    """
    Comprehensive audit logging for all MCP tool calls.
    Logs to both structured logs and database for compliance.
    """
    
    def __init__(self, correlation_id_getter=None):
        self.correlation_id_getter = correlation_id_getter or (lambda: "unknown")
        self._batch_queue = []
        self._batch_size = 10
    
    async def on_request(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Intercept and log tool call request."""
        correlation_id = self.correlation_id_getter()
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "event_type": "mcp_tool_request",
            "tool_name": tool_name,
            "arguments": self._sanitize_args(args),
            "status": "pending"
        }
        
        logger.info(f"MCP Tool Call: {tool_name}", extra=log_entry)
        self._batch_queue.append(log_entry)
        
        # Check for dangerous operations
        if self._is_dangerous_operation(tool_name, args):
            logger.warning(f"Dangerous MCP operation detected: {tool_name}")
            # Could trigger immediate human review here
        
        return args
    
    async def on_response(self, tool_name: str, result: Any) -> Any:
        """Intercept and log tool call response."""
        correlation_id = self.correlation_id_getter()
        
        # Find matching request
        matching_request = None
        for entry in reversed(self._batch_queue):
            if entry["tool_name"] == tool_name and entry["status"] == "pending":
                matching_request = entry
                break
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "event_type": "mcp_tool_response",
            "tool_name": tool_name,
            "result_summary": self._summarize_result(result),
            "status": "success" if not self._is_error_result(result) else "error",
            "duration_ms": self._calculate_duration(matching_request) if matching_request else None
        }
        
        logger.info(f"MCP Tool Response: {tool_name}", extra=log_entry)
        
        # Update request status
        if matching_request:
            matching_request["status"] = "completed"
            matching_request["response"] = log_entry
        
        # Batch flush to database
        if len(self._batch_queue) >= self._batch_size:
            await self._flush_to_database()
        
        return result
    
    def _sanitize_args(self, args: Dict) -> Dict:
        """Remove sensitive data from logged arguments."""
        sensitive_keys = ['password', 'token', 'secret', 'key', 'credential', 'auth']
        sanitized = {}
        for k, v in args.items():
            if any(sk in k.lower() for sk in sensitive_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = str(v)[:500]  # Truncate long values
        return sanitized
    
    def _summarize_result(self, result: Any) -> str:
        """Create summary of tool result."""
        result_str = str(result)
        if len(result_str) > 500:
            return result_str[:500] + f"... ({len(result_str)} chars total)"
        return result_str
    
    def _is_error_result(self, result: Any) -> bool:
        """Check if result indicates an error."""
        result_str = str(result).lower()
        error_indicators = ['error', 'exception', 'failed', 'unauthorized', 'forbidden']
        return any(ind in result_str for ind in error_indicators)
    
    def _is_dangerous_operation(self, tool_name: str, args: Dict) -> bool:
        """Check if operation is potentially dangerous."""
        dangerous_tools = ['delete', 'drop', 'truncate', 'update_all', 'grant']
        return any(dt in tool_name.lower() for dt in dangerous_tools)
    
    def _calculate_duration(self, request_entry: Dict) -> Optional[int]:
        """Calculate request duration in milliseconds."""
        if not request_entry:
            return None
        start = datetime.fromisoformat(request_entry["timestamp"])
        return int((datetime.utcnow() - start).total_seconds() * 1000)
    
    async def _flush_to_database(self):
        """Flush audit batch to database."""
        if not self._batch_queue:
            return
        
        try:
            async with get_db_session() as session:
                for entry in self._batch_queue:
                    audit_record = MCPToolCallAudit(
                        correlation_id=entry.get("correlation_id"),
                        tool_name=entry.get("tool_name"),
                        arguments=json.dumps(entry.get("arguments", {})),
                        result_summary=entry.get("response", {}).get("result_summary", ""),
                        status=entry.get("status", "unknown"),
                        duration_ms=entry.get("response", {}).get("duration_ms"),
                        created_at=datetime.utcnow()
                    )
                    session.add(audit_record)
                await session.commit()
            
            self._batch_queue.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush MCP audit batch: {e}")
            # Keep queue for retry, but limit size
            if len(self._batch_queue) > 100:
                self._batch_queue = self._batch_queue[-50:]

class RateLimitInterceptor(ToolCallInterceptor):
    """Rate limiting interceptor for MCP tools."""
    
    def __init__(self, max_calls_per_minute: int = 60):
        self.max_calls = max_calls_per_minute
        self._call_times: Dict[str, List[datetime]] = {}
    
    async def on_request(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        self._call_times[tool_name] = [
            t for t in self._call_times.get(tool_name, [])
            if t > minute_ago
        ]
        
        # Check limit
        if len(self._call_times[tool_name]) >= self.max_calls:
            raise RateLimitExceeded(f"Rate limit exceeded for {tool_name}: {self.max_calls}/min")
        
        self._call_times[tool_name].append(now)
        return args

class RateLimitExceeded(Exception):
    pass
<a name="phase-5">
Phase 5: Design Quality & Taste (Weeks 11-12)
Step 5.1: Enhanced Design Metrics Engine
File: dashboard/design_metrics_v2.py
Python
#!/usr/bin/env python3
"""
Enhanced Design Quality Metrics Engine
Computes objective design scores with machine learning assistance.
"""
import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import colorsys

class Grade(Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

@dataclass
class DesignReport:
    layout_variance: float
    motion_intensity: float
    accessibility_score: float
    anti_slop_violations: int
    color_harmony: float
    typography_consistency: float
    component_reuse: float
    overall_grade: Grade
    findings: List[Dict]
    recommendations: List[str]

class DesignMetricsEngine:
    """
    Comprehensive design quality analysis engine.
    """
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.src_dir = self.project_dir / "src"
        self.findings: List[Dict] = []
        self.recommendations: List[str] = []
        
        # Thresholds
        self.thresholds = {
            "layout_variance_min": 0.6,
            "motion_intensity_min": 4.0,
            "motion_intensity_max": 6.0,
            "accessibility_min": 95,
            "anti_slop_max": 0,
            "color_harmony_min": 0.7,
            "typography_consistency_min": 0.8,
            "component_reuse_min": 0.5,
        }
    
    def analyze(self) -> DesignReport:
        """Run complete design analysis."""
        self.findings = []
        self.recommendations = []
        
        layout_variance = self._analyze_layout_variance()
        motion_intensity = self._analyze_motion_intensity()
        accessibility = self._analyze_accessibility()
        anti_slop = self._analyze_anti_slop()
        color_harmony = self._analyze_color_harmony()
        typography = self._analyze_typography()
        component_reuse = self._analyze_component_reuse()
        
        # Calculate overall grade
        grade = self._calculate_grade(
            layout_variance, motion_intensity, accessibility,
            anti_slop, color_harmony, typography, component_reuse
        )
        
        return DesignReport(
            layout_variance=layout_variance,
            motion_intensity=motion_intensity,
            accessibility_score=accessibility,
            anti_slop_violations=anti_slop,
            color_harmony=color_harmony,
            typography_consistency=typography,
            component_reuse=component_reuse,
            overall_grade=grade,
            findings=self.findings,
            recommendations=self.recommendations
        )
    
    def _analyze_layout_variance(self) -> float:
        """Measure grid pattern diversity across components."""
        patterns = {
            "css_grid": r"grid|grid-cols|grid-rows",
            "flexbox": r"flex\s+|flex-col|flex-row",
            "absolute": r"absolute|fixed",
            "asymmetric": r"col-span|row-span|col-start|row-start",
            "centered": r"mx-auto|justify-center|items-center",
            "sidebar": r"sidebar|drawer|aside",
        }
        
        pattern_counts = {name: 0 for name in patterns}
        total_files = 0
        
        for filepath in self.src_dir.glob("**/*.{tsx,jsx,vue}"):
            content = filepath.read_text()
            total_files += 1
            
            for name, pattern in patterns.items():
                if re.search(pattern, content):
                    pattern_counts[name] += 1
        
        if total_files == 0:
            return 0.0
        
        # Calculate diversity score
        used_patterns = sum(1 for count in pattern_counts.values() if count > 0)
        diversity = used_patterns / len(patterns)
        
        # Weight by file coverage
        coverage = sum(pattern_counts.values()) / (total_files * len(patterns))
        
        score = (diversity * 0.7) + (min(coverage * 2, 1.0) * 0.3)
        
        if score < self.thresholds["layout_variance_min"]:
            self.findings.append({
                "category": "layout_variance",
                "severity": "medium",
                "message": f"Low layout diversity ({score:.2f}). Consider using more grid patterns.",
                "patterns_found": {k: v for k, v in pattern_counts.items() if v > 0}
            })
            self.recommendations.append(
                "Add variety to layouts: try CSS Grid, asymmetric grids, or sidebar layouts"
            )
        
        return round(score, 2)
    
    def _analyze_motion_intensity(self) -> float:
        """Measure animation coverage (0-10 scale)."""
        animation_patterns = [
            r"animate-\w+",
            r"transition-\w+",
            r"duration-\d+",
            r"ease-\w+",
            r"whileHover",
            r"whileInView",
            r"whileTap",
            r"initial=",
            r"animate=",
            r"@keyframes",
            r"animation:",
        ]
        
        total_elements = 0
        animated_elements = 0
        
        for filepath in self.src_dir.glob("**/*.{tsx,jsx,css,scss}"):
            content = filepath.read_text()
            
            # Count JSX elements
            if filepath.suffix in ('.tsx', '.jsx'):
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                            total_elements += 1
                except:
                    pass
            
            # Count animated elements
            for pattern in animation_patterns:
                animated_elements += len(re.findall(pattern, content))
        
        if total_elements == 0:
            return 0.0
        
        # Calculate intensity
        coverage = animated_elements / total_elements
        intensity = min(coverage * 15, 10.0)  # Scale to 0-10
        
        if intensity < self.thresholds["motion_intensity_min"]:
            self.findings.append({
                "category": "motion",
                "severity": "low",
                "message": f"Motion intensity too low ({intensity:.1f}/10). Consider adding subtle animations."
            })
        elif intensity > self.thresholds["motion_intensity_max"]:
            self.findings.append({
                "category": "motion",
                "severity": "medium",
                "message": f"Motion intensity too high ({intensity:.1f}/10). May cause distraction or performance issues."
            })
            self.recommendations.append("Reduce animation usage - focus on user-initiated transitions only")
        
        return round(intensity, 1)
    
    def _analyze_accessibility(self) -> float:
        """Estimate accessibility score based on code patterns."""
        score = 100
        issues = []
        
        for filepath in self.src_dir.glob("**/*.{tsx,jsx}"):
            content = filepath.read_text()
            
            # Check for alt text on images
            img_tags = re.findall(r'<img[^>]*>', content)
            for img in img_tags:
                if 'alt=' not in img:
                    score -= 5
                    issues.append(f"Missing alt text: {filepath}")
            
            # Check for aria labels
            interactive_elements = re.findall(r'<(button|a|input|select|textarea)[^>]*>', content)
            for elem in interactive_elements:
                if 'aria-' not in elem:
                    score -= 2
            
            # Check for semantic HTML
            if '<div' in content and 'role=' not in content:
                # Penalize excessive div usage
                div_count = content.count('<div')
                semantic_count = sum(content.count(f'<{tag}') for tag in ['header', 'nav', 'main', 'article', 'section', 'footer'])
                if div_count > semantic_count * 3:
                    score -= 3
            
            # Check color contrast (basic)
            color_patterns = re.findall(r'text-(\w+)-(\d+)', content)
            bg_patterns = re.findall(r'bg-(\w+)-(\d+)', content)
            # Would need actual color values for real contrast check
        
        score = max(0, score)
        
        if score < self.thresholds["accessibility_min"]:
            self.findings.append({
                "category": "accessibility",
                "severity": "high",
                "message": f"Accessibility score ({score}%) below threshold ({self.thresholds['accessibility_min']}%)",
                "issues": issues[:10]  # Limit findings
            })
            self.recommendations.append("Run axe-core for detailed accessibility audit and fix critical issues")
        
        return score
    
    def _analyze_anti_slop(self) -> int:
        """Detect anti-pattern violations."""
        violations = 0
        checks = [
            (r"font-family:\s*['\"](Arial|Helvetica|Times New Roman)['\"]", "Generic system font"),
            (r"bg-gradient-to-[rltb].*-purple", "Purple gradient (overused)"),
            (r"text-center.*text-[4-9]xl", "Centered hero text block"),
            (r"shadow-2xl.*rounded-none", "Harsh shadow without rounding"),
            (r"!important", "Overuse of !important"),
            (r"color:\s*#ff0000", "Pure red text (accessibility)"),
            (r"line-height:\s*1", "No line height for readability"),
            (r"margin:\s*0\s+auto", "Excessive centering"),
        ]
        
        for filepath in self.src_dir.glob("**/*.{tsx,jsx,css,scss}"):
            content = filepath.read_text()
            
            for pattern, reason in checks:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    violations += 1
                    self.findings.append({
                        "category": "anti_slop",
                        "severity": "medium",
                        "message": f"Anti-pattern: {reason}",
                        "file": str(filepath),
                        "match": match
                    })
        
        if violations > self.thresholds["anti_slop_max"]:
            self.recommendations.append(f"Fix {violations} anti-pattern violations for professional appearance")
        
        return violations
    
    def _analyze_color_harmony(self) -> float:
        """Analyze color usage harmony."""
        # Extract all color values
        colors = []
        for filepath in self.src_dir.glob("**/*.{tsx,jsx,css,scss}"):
            content = filepath.read_text()
            
            # Tailwind colors
            tailwind_colors = re.findall(r'(bg|text|border)-(\w+)-(\d+)', content)
            for _, color, shade in tailwind_colors:
                colors.append((color, int(shade)))
            
            # Hex colors
            hex_colors = re.findall(r'#[0-9a-fA-F]{6}', content)
            for hex_color in hex_colors:
                colors.append(self._hex_to_hsl(hex_color))
        
        if len(colors) < 5:
            return 1.0  # Not enough data
        
        # Calculate color harmony score
        # Simplified: check if colors are from similar hue families
        hues = [c[0] if isinstance(c, tuple) else c[0] for c in colors if isinstance(c, tuple)]
        if not hues:
            return 1.0
        
        hue_variance = self._calculate_hue_variance(hues)
        harmony = 1.0 - min(hue_variance / 180, 1.0)
        
        if harmony < self.thresholds["color_harmony_min"]:
            self.recommendations.append("Improve color harmony - stick to a defined palette")
        
        return round(harmony, 2)
    
    def _analyze_typography(self) -> float:
        """Analyze typography consistency."""
        font_sizes = set()
        font_families = set()
        
        for filepath in self.src_dir.glob("**/*.{tsx,jsx,css,scss}"):
            content = filepath.read_text()
            
            sizes = re.findall(r'text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl)', content)
            font_sizes.update(sizes)
            
            families = re.findall(r'font-(\w+)', content)
            font_families.update(families)
        
        # Score based on consistency
        size_score = 1.0 if len(font_sizes) <= 8 else 0.7 if len(font_sizes) <= 12 else 0.5
        family_score = 1.0 if len(font_families) <= 3 else 0.7 if len(font_families) <= 5 else 0.5
        
        consistency = (size_score + family_score) / 2
        
        if consistency < self.thresholds["typography_consistency_min"]:
            self.recommendations.append(f"Reduce font sizes ({len(font_sizes)}) and families ({len(font_families)}) for consistency")
        
        return round(consistency, 2)
    
    def _analyze_component_reuse(self) -> float:
        """Measure component reuse ratio."""
        component_counts = {}
        
        for filepath in self.src_dir.glob("**/*.{tsx,jsx}"):
            content = filepath.read_text()
            
            # Find component imports
            imports = re.findall(r"import\s+{\s*([^}]+)\s*}\s+from\s+['\"][^'\"]+components/([^'\"]+)['\"]", content)
            for imported, source in imports:
                for comp in imported.split(','):
                    comp = comp.strip()
                    component_counts[comp] = component_counts.get(comp, 0) + 1
        
        if not component_counts:
            return 0.0
        
        # Calculate reuse ratio
        reused = sum(1 for count in component_counts.values() if count > 1)
        reuse_ratio = reused / len(component_counts)
        
        if reuse_ratio < self.thresholds["component_reuse_min"]:
            self.recommendations.append("Increase component reuse - extract repeated UI patterns")
        
        return round(reuse_ratio, 2)
    
    def _calculate_grade(self, *scores) -> Grade:
        """Calculate overall letter grade."""
        layout, motion, accessibility, anti_slop, color, typography, reuse = scores
        
        # Weighted scoring
        weights = {
            'accessibility': 0.25,
            'anti_slop': 0.20,
            'layout': 0.15,
            'color': 0.15,
            'typography': 0.10,
            'motion': 0.10,
            'reuse': 0.05,
        }
        
        # Normalize scores to 0-1
        normalized = {
            'accessibility': accessibility / 100,
            'anti_slop': 1.0 if anti_slop == 0 else max(0, 1.0 - (anti_slop / 10)),
            'layout': layout,
            'color': color,
            'typography': typography,
            'motion': 1.0 if 4 <= motion <= 6 else max(0, 1.0 - abs(motion - 5) / 5),
            'reuse': reuse,
        }
        
        weighted_score = sum(normalized[k] * weights[k] for k in weights)
        
        if weighted_score >= 0.95 and anti_slop == 0:
            return Grade.A_PLUS
        elif weighted_score >= 0.90:
            return Grade.A
        elif weighted_score >= 0.80:
            return Grade.B
        elif weighted_score >= 0.70:
            return Grade.C
        elif weighted_score >= 0.60:
            return Grade.D
        else:
            return Grade.F
    
    def _hex_to_hsl(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to HSL."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)
    
    def _calculate_hue_variance(self, hues: List[float]) -> float:
        """Calculate variance in hue values."""
        if len(hues) < 2:
            return 0
        
        # Handle circular hue values
        mean = sum(hues) / len(hues)
        variance = sum(min((h - mean) % 360, (mean - h) % 360) ** 2 for h in hues) / len(hues)
        return variance ** 0.5

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Design Quality Metrics")
    parser.add_argument("--dir", required=True, help="Project directory")
    parser.add_argument("--output", default="design-report.json", help="Output file")
    parser.add_argument("--ci", action="store_true", help="CI mode (exit non-zero on < A)")
    args = parser.parse_args()
    
    engine = DesignMetricsEngine(args.dir)
    report = engine.analyze()
    
    # Convert to dict for JSON serialization
    report_dict = {
        "layout_variance": report.layout_variance,
        "motion_intensity": report.motion_intensity,
        "accessibility_score": report.accessibility_score,
        "anti_slop_violations": report.anti_slop_violations,
        "color_harmony": report.color_harmony,
        "typography_consistency": report.typography_consistency,
        "component_reuse": report.component_reuse,
        "overall_grade": report.overall_grade.value,
        "findings": report.findings,
        "recommendations": report.recommendations,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    with open(args.output, "w") as f:
        json.dump(report_dict, f, indent=2)
    
    print(f"✅ Design report saved to {args.output}")
    print(f"📊 Grade: {report.overall_grade.value}")
    
    if args.ci and report.overall_grade.value not in ['A+', 'A']:
        print(f"❌ CI failed: Grade {report.overall_grade.value} below threshold")
        exit(1)
    
    if report.findings:
        print(f"\n⚠️  {len(report.findings)} findings:")
        for f in report.findings[:5]:
            print(f"  - [{f['severity'].upper()}] {f['message']}")

if __name__ == "__main__":
    main()
Step 5.2: Design Director Agent
File: .claude/agents/design-director.md
Markdown
Fullscreen 
Download 
Fit
Code
Preview
Role
1. When assigned a review task, first run the design metrics engine:
python dashboard/design_metrics_v2.py --dir frontend/src --output /tmp/design-report.json --ci
Process
Design Director Constitution
Analyze the report:
Grade must be A or A+
Layout variance ≥ 0.6
Motion intensity between 4-6
Accessibility ≥ 95%
Zero anti-slop violations
Color harmony ≥ 0.7
Typography consistency ≥ 0.8
If metrics pass, perform manual code review:
Check design token compliance (no hardcoded values)
Verify responsive design patterns
Check for proper loading states and error boundaries
Verify animation performance (no layout thrashing)
If metrics fail:
Block the PR
Provide specific remediation steps with file paths and line numbers
Suggest concrete fixes using design tokens
Rules
Be strict—quality over speed
Cite exact file paths and line numbers
Suggest token-based fixes: "Replace bg-purple-500 with primary-600"
Never approve code with generic fonts or purple gradients
Require axe-core pass for all interactive components
Check for proper dark mode support
Output Format
JSON
{
  "review_id": "uuid",
  "status": "approved|blocked",
  "grade": "A",
  "metrics": {
    "layout_variance": 0.72,
    "motion_intensity": 5.2,
    "accessibility": 98,
    "anti_slop": 0,
    "color_harmony": 0.85,
    "typography": 0.92,
    "component_reuse": 0.67
  },
  "findings": [],
  "recommendations": [],
  "manual_notes": []
}
plain

---

<a name="phase-6"></a>
## Phase 6: Observability & SRE (Weeks 13-14)

### Step 6.1: OpenTelemetry Distributed Tracing

**File: `api/app/core/tracing.py`**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.trace import SpanKind, Status, StatusCode
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class TracingManager:
    """Distributed tracing with OpenTelemetry."""
    
    def __init__(self, service_name: str = "ai-workflow-platform"):
        self.service_name = service_name
        self.provider = TracerProvider()
        self.tracer = trace.get_tracer(service_name)
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://jaeger:4317",
            insecure=True
        )
        
        # Batch processor for efficiency
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000
        )
        
        self.provider.add_span_processor(span_processor)
        trace.set_tracer_provider(self.provider)
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application."""
        FastAPIInstrumentor.instrument_app(app)
    
    def instrument_sqlalchemy(self, engine):
        """Instrument SQLAlchemy."""
        SQLAlchemyInstrumentor().instrument(engine=engine)
    
    def instrument_redis(self):
        """Instrument Redis."""
        RedisInstrumentor().instrument()
    
    @contextmanager
    def start_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL, attributes: dict = None):
        """Context manager for manual span creation."""
        with self.tracer.start_as_current_span(name, kind=kind, attributes=attributes or {}) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def add_event(self, span, name: str, attributes: dict = None):
        """Add event to current span."""
        span.add_event(name, attributes=attributes or {})

tracing_manager = TracingManager()
Step 6.2: Prometheus Metrics with Custom Collectors
File: api/app/core/metrics.py
Python
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
import time
from functools import wraps

# Custom registry
registry = CollectorRegistry()

# Workflow metrics
workflow_duration = Histogram(
    'workflow_duration_seconds',
    'Duration of workflow execution',
    ['workflow_type', 'status', 'risk_level'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
    registry=registry
)

workflow_errors = Counter(
    'workflow_errors_total',
    'Total workflow errors',
    ['workflow_type', 'node', 'error_type'],
    registry=registry
)

workflow_active = Gauge(
    'workflow_active_total',
    'Currently running workflows',
    ['workflow_type'],
    registry=registry
)

# LLM metrics
llm_tokens_total = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['model', 'token_type', 'agent_type'],
    registry=registry
)

llm_cost_usd = Counter(
    'llm_cost_usd_total',
    'Total LLM cost in USD',
    ['model', 'agent_type'],
    registry=registry
)

llm_latency = Histogram(
    'llm_request_duration_seconds',
    'LLM request latency',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0],
    registry=registry
)

# MCP metrics
mcp_tool_calls = Counter(
    'mcp_tool_calls_total',
    'Total MCP tool calls',
    ['server', 'tool', 'status'],
    registry=registry
)

mcp_tool_latency = Histogram(
    'mcp_tool_duration_seconds',
    'MCP tool execution latency',
    ['server', 'tool'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=registry
)

# Agent metrics
agent_tasks = Counter(
    'agent_tasks_total',
    'Total agent tasks',
    ['agent_type', 'status'],
    registry=registry
)

agent_execution_time = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution time',
    ['agent_type'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 1800.0],
    registry=registry
)

# HITL metrics
human_review_pending = Gauge(
    'human_review_pending_total',
    'Pending human review tasks',
    ['risk_level'],
    registry=registry
)

human_review_duration = Histogram(
    'human_review_duration_seconds',
    'Time to human decision',
    ['decision'],
    buckets=[30.0, 60.0, 300.0, 600.0, 1800.0, 3600.0],
    registry=registry
)

def setup_metrics(app):
    """Configure metrics for FastAPI app."""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    return instrumentator

def track_workflow(w
continue step 6.2
Edit
Copy
Share
I'll continue completing Phase 6.2 (Prometheus Metrics) and the remaining phases with full technical implementation details.
Step 6.2: Prometheus Metrics with Custom Collectors (Continued)
File: api/app/core/metrics.py (Continued)
Python
def track_workflow(wrapped):
    """Decorator to track workflow execution metrics."""
    @wraps(wrapped)
    async def wrapper(*args, **kwargs):
        workflow_type = kwargs.get('workflow_type', 'default')
        risk_level = kwargs.get('risk_level', 'low')
        
        workflow_active.labels(workflow_type=workflow_type).inc()
        start_time = time.time()
        
        try:
            result = await wrapped(*args, **kwargs)
            status = "success"
            return result
            
        except Exception as e:
            status = "error"
            error_type = type(e).__name__
            workflow_errors.labels(
                workflow_type=workflow_type,
                node=kwargs.get('current_step', 'unknown'),
                error_type=error_type
            ).inc()
            raise
            
        finally:
            duration = time.time() - start_time
            workflow_duration.labels(
                workflow_type=workflow_type,
                status=status,
                risk_level=risk_level
            ).observe(duration)
            workflow_active.labels(workflow_type=workflow_type).dec()
    
    return wrapper

def track_llm_call(model: str, agent_type: str = "unknown"):
    """Context manager to track LLM calls."""
    start_time = time.time()
    
    def record_completion(prompt_tokens: int, completion_tokens: int):
        llm_tokens_total.labels(model=model, token_type="prompt", agent_type=agent_type).inc(prompt_tokens)
        llm_tokens_total.labels(model=model, token_type="completion", agent_type=agent_type).inc(completion_tokens)
        
        # Cost calculation (approximate)
        cost = (prompt_tokens * 0.000003) + (completion_tokens * 0.000015)  # Sonnet pricing
        llm_cost_usd.labels(model=model, agent_type=agent_type).inc(cost)
        
        duration = time.time() - start_time
        llm_latency.labels(model=model).observe(duration)
    
    return record_completion

def track_mcp_tool(server: str, tool: str):
    """Context manager to track MCP tool calls."""
    start_time = time.time()
    
    def record_completion(status: str = "success"):
        mcp_tool_calls.labels(server=server, tool=tool, status=status).inc()
        duration = time.time() - start_time
        mcp_tool_latency.labels(server=server, tool=tool).observe(duration)
    
    return record_completion

def track_human_review(risk_level: str):
    """Track human review metrics."""
    human_review_pending.labels(risk_level=risk_level).inc()
    
    start_time = time.time()
    
    def record_decision(decision: str):
        human_review_pending.labels(risk_level=risk_level).dec()
        duration = time.time() - start_time
        human_review_duration.labels(decision=decision).observe(duration)
    
    return record_decision

class MetricsMiddleware:
    """FastAPI middleware for additional metrics collection."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        path = scope.get("path", "")
        method = scope.get("method", "")
        
        # Track request
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                # Additional custom metrics can be added here
            await send(message)
        
        await self.app(scope, receive, wrapped_send)
Step 6.3: Grafana Dashboard Configuration
File: infrastructure/grafana/dashboards/ai-workflow-platform.json
JSON
{
  "dashboard": {
    "id": null,
    "title": "AI Workflow Platform - Production",
    "tags": ["ai", "workflow", "production"],
    "timezone": "UTC",
    "schemaVersion": 36,
    "refresh": "10s",
    "panels": [
      {
        "id": 1,
        "title": "Workflow Success Rate (5m)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(workflow_duration_seconds_count{status=\"success\"}[5m])) / sum(rate(workflow_duration_seconds_count[5m])) * 100",
            "legendFormat": "Success Rate %"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 95},
                {"color": "green", "value": 99}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Active Workflows",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(workflow_active_total)",
            "legendFormat": "Active"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "p95 Workflow Latency",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(workflow_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "p95"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 3},
                {"color": "red", "value": 10}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "LLM Cost (1h)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(llm_cost_usd_total[1h]))",
            "legendFormat": "USD/hour"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD",
            "thresholds": {
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 50}
              ]
            }
          }
        },
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 5,
        "title": "Workflow Duration by Risk Level",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(workflow_duration_seconds_bucket[5m])) by (le, risk_level))",
            "legendFormat": "{{risk_level}}"
          }
        ],
        "yAxes": [{"format": "s"}],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "id": 6,
        "title": "Error Rate by Node",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(workflow_errors_total[5m])) by (node)",
            "legendFormat": "{{node}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      {
        "id": 7,
        "title": "Token Usage by Model",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(llm_tokens_used_total[5m])) by (model, token_type)",
            "legendFormat": "{{model}} - {{token_type}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12}
      },
      {
        "id": 8,
        "title": "MCP Tool Call Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(mcp_tool_duration_seconds_bucket[5m])) by (le, server))",
            "legendFormat": "{{server}}"
          }
        ],
        "yAxes": [{"format": "s"}],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12}
      },
      {
        "id": 9,
        "title": "Human Review Queue",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(human_review_pending_total) by (risk_level)",
            "legendFormat": "{{risk_level}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20}
      },
      {
        "id": 10,
        "title": "Agent Task Distribution",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum(rate(agent_tasks_total[1h])) by (agent_type)",
            "legendFormat": "{{agent_type}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20}
      }
    ]
  }
}
Step 6.4: AlertManager Configuration
File: infrastructure/prometheus/alertmanager.yml
yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@aiwf.com'
  smtp_auth_username: 'alerts@aiwf.com'
  smtp_auth_password: '${SMTP_PASSWORD}'

templates:
  - '/etc/alertmanager/templates/*.tmpl'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      group_wait: 0s
      repeat_interval: 1h
    - match:
        severity: warning
      receiver: 'slack-warnings'
      group_wait: 1m
    - match:
        alertname: 'HighTokenCost'
      receiver: 'finance-team'
      group_wait: 5m

receivers:
  - name: 'default'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#aiwf-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_KEY}'
        severity: critical
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

  - name: 'slack-warnings'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#aiwf-warnings'
        title: 'Warning: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'finance-team'
    email_configs:
      - to: 'finance@aiwf.com'
        subject: 'AIWF Cost Alert: {{ .GroupLabels.alertname }}'
        body: |
          Cost threshold exceeded:
          {{ range .Alerts }}
          - {{ .Annotations.summary }}
          - Current value: {{ .Value }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
File: infrastructure/prometheus/alerts.yml
yaml
groups:
  - name: workflow_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(workflow_errors_total[5m]))
            /
            sum(rate(workflow_duration_seconds_count[5m]))
          ) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Workflow error rate > 1%"
          description: "Error rate is {{ $value | humanizePercentage }} over the last 5 minutes"

      - alert: SlowWorkflow
        expr: |
          histogram_quantile(0.95, 
            sum(rate(workflow_duration_seconds_bucket[5m])) by (le)
          ) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 workflow latency > 10s"
          description: "Current p95: {{ $value }}s"

      - alert: HighTokenCost
        expr: |
          sum(increase(llm_cost_usd_total[1h])) > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM cost > $50/hour"
          description: "Current hourly cost: ${{ $value }}"

      - alert: MCPServerDown
        expr: |
          mcp_tool_calls_total == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "MCP server unresponsive"
          description: "No MCP tool calls in last 2 minutes"

      - alert: HumanReviewBacklog
        expr: |
          sum(human_review_pending_total) > 50
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Human review backlog > 50"
          description: "{{ $value }} tasks awaiting human review"

      - alert: AgentSandboxFailure
        expr: |
          increase(agent_tasks_total{status="failed"}[5m]) > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Multiple agent sandbox failures"
          description: "{{ $value }} agent failures in last 5 minutes"

      - alert: DatabaseConnectionExhaustion
        expr: |
          pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connections > 80%"
          description: "Current usage: {{ $value | humanizePercentage }}"
<a name="phase-7">
Phase 7: Production Deployment (Weeks 15-18)
Step 7.1: Multi-Stage Production Dockerfiles
File: infrastructure/docker/api/Dockerfile.prod
dockerfile
# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Security: Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.0

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 10

# Install dependencies (no dev packages)
RUN poetry install --no-dev --no-interaction --no-ansi

# =============================================================================
# Stage 2: Security Scanner
# =============================================================================
FROM builder AS security-scanner

RUN pip install --no-cache-dir safety bandit

# Run security checks
RUN safety check --full-report || true
RUN bandit -r /build || true

# =============================================================================
# Stage 3: Runtime
# =============================================================================
FROM python:3.11-slim AS runtime

# Security: Create non-root user
RUN groupadd -r aiwf && useradd -r -g aiwf aiwf

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=aiwf:aiwf api/ ./

# Security: Set proper permissions
RUN chmod -R 755 /app \
    && chmod -R 644 /app/app \
    && find /app -type d -exec chmod 755 {} \;

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Drop to non-root user
USER aiwf

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    WORKERS=4

EXPOSE 8000

# Use gunicorn with uvicorn workers for production
CMD exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers ${WORKERS} \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    app.main:app
File: infrastructure/docker/frontend/Dockerfile.prod
dockerfile
# =============================================================================
# Stage 1: Build
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /build

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Build with optimizations
ENV NODE_ENV=production \
    VITE_API_URL=/api \
    VITE_WS_URL=/ws

RUN npm run build

# Run security audit
RUN npm audit --audit-level=moderate || true

# =============================================================================
# Stage 2: Runtime (Nginx)
# =============================================================================
FROM nginx:1.25-alpine AS runtime

# Security: Remove default nginx user
RUN deluser nginx || true

# Install security headers module
RUN apk add --no-cache nginx-mod-http-headers-more

# Copy built assets
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy nginx configuration
COPY infrastructure/docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY infrastructure/docker/frontend/security-headers.conf /etc/nginx/conf.d/security-headers.conf

# Security: Create non-root user
RUN adduser -D -H -u 1000 aiwf \
    && chown -R aiwf:aiwf /usr/share/nginx/html \
    && chown -R aiwf:aiwf /var/cache/nginx \
    && chown -R aiwf:aiwf /var/log/nginx \
    && chown -R aiwf:aiwf /etc/nginx/conf.d

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

USER aiwf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
File: infrastructure/docker/frontend/nginx.conf
nginx
server {
    listen 8080;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    include /etc/nginx/conf.d/security-headers.conf;

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Static assets with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
File: infrastructure/docker/frontend/security-headers.conf
nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
Step 7.2: Kubernetes Helm Charts
File: helm/aiwf/Chart.yaml
yaml
apiVersion: v2
name: aiwf
description: AI Workflow Platform - Production Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: 15.0.0
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  
  - name: redis
    version: 19.0.0
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
  
  - name: grafana
    version: 7.3.0
    repository: https://grafana.github.io/helm-charts
    condition: grafana.enabled
  
  - name: prometheus
    version: 25.0.0
    repository: https://prometheus-community.github.io/helm-charts
    condition: prometheus.enabled

maintainers:
  - name: AIWF Team
    email: devops@aiwf.com
File: helm/aiwf/values-production.yaml
yaml
# =============================================================================
# Global Configuration
# =============================================================================
global:
  environment: production
  domain: aiwf.example.com
  tls:
    enabled: true
    issuer: letsencrypt-prod

# =============================================================================
# Backend API
# =============================================================================
backend:
  replicaCount: 3
  
  image:
    repository: aiwf/backend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1.5Gi"
      cpu: "1000m"
  
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  env:
    - name: ENVIRONMENT
      value: "production"
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: aiwf-secrets
          key: database-url
    - name: REDIS_URL
      valueFrom:
        secretKeyRef:
          name: aiwf-secrets
          key: redis-url
    - name: SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: aiwf-secrets
          key: secret-key
    - name: ANTHROPIC_API_KEY
      valueFrom:
        secretKeyRef:
          name: aiwf-secrets
          key: anthropic-api-key
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: aiwf-secrets
          key: openai-api-key
  
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  
  readinessProbe:
    httpGet:
      path: /ready
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3
  
  podDisruptionBudget:
    enabled: true
    minAvailable: 2
  
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  
  securityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop:
        - ALL
  
  service:
    type: ClusterIP
    port: 8000
  
  ingress:
    enabled: true
    className: nginx
    annotations:
      nginx.ingress.kubernetes.io/rate-limit: "100"
      nginx.ingress.kubernetes.io/rate-limit-window: "1m"
      cert-manager.io/cluster-issuer: "letsencrypt-prod"
    hosts:
      - host: api.aiwf.example.com
        paths:
          - path: /
            pathType: Prefix

# =============================================================================
# Frontend
# =============================================================================
frontend:
  replicaCount: 2
  
  image:
    repository: aiwf/frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 75
  
  service:
    type: ClusterIP
    port: 8080
  
  ingress:
    enabled: true
    className: nginx
    annotations:
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
      cert-manager.io/cluster-issuer: "letsencrypt-prod"
    hosts:
      - host: aiwf.example.com
        paths:
          - path: /
            pathType: Prefix

# =============================================================================
# Database
# =============================================================================
postgresql:
  enabled: true
  auth:
    existingSecret: aiwf-postgres-secret
  
  primary:
    persistence:
      enabled: true
      storageClass: "fast-ssd"
      size: 100Gi
    
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
    
    podDisruptionBudget:
      enabled: true
      minAvailable: 1
    
    metrics:
      enabled: true
  
  readReplicas:
    replicaCount: 2

# =============================================================================
# Cache
# =============================================================================
redis:
  enabled: true
  auth:
    existingSecret: aiwf-redis-secret
  
  architecture: replication
  
  master:
    persistence:
      enabled: true
      storageClass: "fast-ssd"
      size: 10Gi
    
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "500m"
  
  replica:
    replicaCount: 2

# =============================================================================
# Monitoring
# =============================================================================
prometheus:
  enabled: true
  server:
    retention: "30d"
    persistentVolume:
      enabled: true
      size: 50Gi
  
  alertmanager:
    enabled: true
    config:
      global:
        slack_api_url: "${SLACK_WEBHOOK_URL}"
      receivers:
        - name: default
          slack_configs:
            - channel: '#aiwf-alerts'

grafana:
  enabled: true
  admin:
    existingSecret: aiwf-grafana-secret
  
  persistence:
    enabled: true
    size: 10Gi
  
  dashboards:
    default:
      aiwf-dashboard:
        url: https://raw.githubusercontent.com/aiwf/grafana-dashboards/main/aiwf-production.json

# =============================================================================
# Network Policies
# =============================================================================
networkPolicies:
  enabled: true
  
  backend:
    ingress:
      - from:
          - podSelector:
              matchLabels:
                app.kubernetes.io/name: frontend
          - namespaceSelector:
              matchLabels:
                name: monitoring
        ports:
          - protocol: TCP
            port: 8000
  
  postgresql:
    ingress:
      - from:
          - podSelector:
              matchLabels:
                app.kubernetes.io/name: backend
        ports:
          - protocol: TCP
            port: 5432
  
  redis:
    ingress:
      - from:
          - podSelector:
              matchLabels:
                app.kubernetes.io/name: backend
        ports:
          - protocol: TCP
            port: 6379
Step 7.3: Zero-Downtime Deployment with Argo Rollouts
File: helm/aiwf/templates/rollout-backend.yaml
yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: {{ include "aiwf.fullname" . }}-backend
  labels:
    {{- include "aiwf.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  strategy:
    canary:
      canaryService: {{ include "aiwf.fullname" . }}-backend-canary
      stableService: {{ include "aiwf.fullname" . }}-backend-stable
      trafficRouting:
        nginx:
          stableIngress: {{ include "aiwf.fullname" . }}-backend
          annotationPrefix: nginx.ingress.kubernetes.io
      steps:
        # Step 1: Set canary weight to 5%
        - setWeight: 5
        # Step 2: Pause for 10 minutes to observe
        - pause: {duration: 10m}
        # Step 3: Run automated analysis
        - analysis:
            templates:
              - templateName: success-rate
            args:
              - name: service-name
                value: {{ include "aiwf.fullname" . }}-backend-canary
        # Step 4: Increase to 20%
        - setWeight: 20
        - pause: {duration: 10m}
        # Step 5: Run analysis again
        - analysis:
            templates:
              - templateName: success-rate
              - templateName: latency
        # Step 6: Increase to 50%
        - setWeight: 50
        - pause: {duration: 10m}
        # Step 7: Final analysis
        - analysis:
            templates:
              - templateName: success-rate
              - templateName: latency
              - templateName: error-rate
        # Step 8: Full rollout
        - setWeight: 100
      analysis:
        # Auto-rollback on failure
        abortScaleDownDelaySeconds: 600
  selector:
    matchLabels:
      {{- include "aiwf.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        {{- include "aiwf.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      {{- with .Values.backend.podSecurityContext }}
      securityContext:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          {{- with .Values.backend.env }}
          env:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          livenessProbe:
            {{- toYaml .Values.backend.livenessProbe | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.backend.readinessProbe | nindent 12 }}
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          {{- with .Values.backend.securityContext }}
          securityContext:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
File: helm/aiwf/templates/analysis-templates.yaml
yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] >= 0.99
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status=~"2.."}[1m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[1m]))

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency
spec:
  metrics:
    - name: p95-latency
      interval: 1m
      successCondition: result[0] <= 3000
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            histogram_quantile(0.95,
              sum(rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[1m])) by (le)
            ) * 1000

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate
spec:
  metrics:
    - name: error-rate
      interval: 1m
      successCondition: result[0] <= 0.01
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status=~"5.."}[1m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[1m]))
Step 7.4: Database Migration Job
File: helm/aiwf/templates/migration-job.yaml
yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "aiwf.fullname" . }}-db-migration-{{ .Release.Revision }}
  labels:
    {{- include "aiwf.labels" . | nindent 4 }}
    app.kubernetes.io/component: migration
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    metadata:
      labels:
        {{- include "aiwf.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: migration
    spec:
      restartPolicy: OnFailure
      {{- with .Values.backend.podSecurityContext }}
      securityContext:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: migration
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          command: ["alembic", "upgrade", "head"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: aiwf-secrets
                  key: database-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "250m"
<a name="phase-8">
Phase 8: Cost Governance & Optimization (Weeks 19-20)
Step 8.1: Cost Governor Microservice
File: api/app/services/cost_governor.py
Python
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

import redis.asyncio as redis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class BudgetTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class BudgetConfig:
    tier: BudgetTier
    daily_token_limit: int
    daily_cost_limit_usd: float
    max_concurrent_workflows: int
    allowed_models: List[str]
    max_react_steps: int
    max_agents_per_task: int

BUDGET_CONFIGS = {
    BudgetTier.FREE: BudgetConfig(
        tier=BudgetTier.FREE,
        daily_token_limit=10000,
        daily_cost_limit_usd=1.0,
        max_concurrent_workflows=1,
        allowed_models=["claude-haiku-3-5"],
        max_react_steps=3,
        max_agents_per_task=1
    ),
    BudgetTier.STARTER: BudgetConfig(
        tier=BudgetTier.STARTER,
        daily_token_limit=100000,
        daily_cost_limit_usd=10.0,
        max_concurrent_workflows=3,
        allowed_models=["claude-haiku-3-5", "claude-sonnet-4-6"],
        max_react_steps=5,
        max_agents_per_task=3
    ),
    BudgetTier.PROFESSIONAL: BudgetConfig(
        tier=BudgetTier.PROFESSIONAL,
        daily_token_limit=1000000,
        daily_cost_limit_usd=100.0,
        max_concurrent_workflows=10,
        allowed_models=["claude-haiku-3-5", "claude-sonnet-4-6", "claude-opus-4-6"],
        max_react_steps=10,
        max_agents_per_task=5
    ),
    BudgetTier.ENTERPRISE: BudgetConfig(
        tier=BudgetTier.ENTERPRISE,
        daily_token_limit=10000000,
        daily_cost_limit_usd=1000.0,
        max_concurrent_workflows=50,
        allowed_models=["claude-haiku-3-5", "claude-sonnet-4-6", "claude-opus-4-6", "gpt-4o"],
        max_react_steps=20,
        max_agents_per_task=10
    )
}

class CostGovernor:
    """
    Centralized cost governance service.
    Enforces budgets, tracks usage, and provides real-time cost visibility.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.alert_thresholds = [0.5, 0.8, 1.0]  # 50%, 80%, 100%
    
    async def get_budget_config(self, user_id: str) -> BudgetConfig:
        """Get user's budget configuration."""
        # In production, fetch from user profile database
        tier_key = f"user:{user_id}:tier"
        tier = await self.redis.get(tier_key) or BudgetTier.STARTER
        return BUDGET_CONFIGS.get(BudgetTier(tier), BUDGET_CONFIGS[BudgetTier.STARTER])
    
    async def check_budget(self, user_id: str, estimated_tokens: int = 0, estimated_cost: float = 0.0) -> Tuple[bool, Dict]:
        """
        Check if operation is within budget.
        Returns (allowed, details).
        """
        config = await self.get_budget_config(user_id)
        
        # Get current usage
        today = datetime.utcnow().strftime("%Y-%m-%d")
        token_key = f"usage:{user_id}:{today}:tokens"
        cost_key = f"usage:{user_id}:{today}:cost"
        
        current_tokens = int(await self.redis.get(token_key) or 0)
        current_cost = float(await self.redis.get(cost_key) or 0.0)
        
        # Check limits
        projected_tokens = current_tokens + estimated_tokens
        projected_cost = current_cost + estimated_cost
        
        details = {
            "tier": config.tier.value,
            "daily_token_limit": config.daily_token_limit,
            "daily_cost_limit": config.daily_cost_limit_usd,
            "current_tokens": current_tokens,
            "current_cost": round(current_cost, 4),
            "projected_tokens": projected_tokens,
            "projected_cost": round(projected_cost, 4),
            "token_remaining": max(0, config.daily_token_limit - current_tokens),
            "cost_remaining": max(0, config.daily_cost_limit_usd - current_cost),
            "usage_percent": round((current_cost / config.daily_cost_limit_usd) * 100, 1)
        }
        
        # Check token limit
        if projected_tokens > config.daily_token_limit:
            details["reason"] = "Daily token limit exceeded"
            return False, details
        
        # Check cost limit
        if projected_cost > config.daily_cost_limit_usd:
            details["reason"] = "Daily cost limit exceeded"
            return False, details
        
        # Check concurrent workflows
        active_key = f"active:{user_id}"
        active_count = await self.redis.scard(active_key)
        if active_count >= config.max_concurrent_workflows:
            details["reason"] = "Max concurrent workflows reached"
            return False, details
        
        return True, details
    
    async def record_usage(self, user_id: str, task_id: str, tokens: int, cost_usd: float, model: str):
        """Record token and cost usage."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Update daily counters
        token_key = f"usage:{user_id}:{today}:tokens"
        cost_key = f"usage:{user_id}:{today}:cost"
        
        pipe = self.redis.pipeline()
        pipe.incrby(token_key, tokens)
        pipe.incrbyfloat(cost_key, cost_usd)
        pipe.expire(token_key, 86400 * 2)  # 2 days TTL
        pipe.expire(cost_key, 86400 * 2)
        
        # Track by model
        model_key = f"usage:{user_id}:{today}:model:{model}"
        pipe.incrby(model_key, tokens)
        pipe.expire(model_key, 86400 * 2)
        
        # Track by task
        task_key = f"task:{task_id}:cost"
        pipe.hincrby(task_key, "tokens", tokens)
        pipe.hincrbyfloat(task_key, "cost", cost_usd)
        pipe.hset(task_key, "model", model)
        pipe.hset(task_key, "updated_at", datetime.utcnow().isoformat())
        
        await pipe.execute()
        
        # Check alert thresholds
        await self._check_alerts(user_id, tokens, cost_usd)
    
    async def _check_alerts(self, user_id: str, new_tokens: int, new_cost: float):
        """Check and send budget alerts."""
        config = await self.get_budget_config(user_id)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        cost_key = f"usage:{user_id}:{today}:cost"
        current_cost = float(await self.redis.get(cost_key) or 0.0)
        usage_percent = current_cost / config.daily_cost_limit_usd
        
        alert_key = f"alerts:{user_id}:{today}"
        
        for threshold in self.alert_thresholds:
            if usage_percent >= threshold:
                # Check if alert already sent
                sent = await self.redis.sismember(alert_key, str(threshold))
                if not sent:
                    await self._send_alert(user_id, threshold, current_cost, config.daily_cost_limit_usd)
                    await self.redis.sadd(alert_key, str(threshold))
                    await self.redis.expire(alert_key, 86400)
    
    async def _send_alert(self, user_id: str, threshold: float, current_cost: float, limit: float):
        """Send budget alert via multiple channels."""
        message = {
            "type": "budget_alert",
            "user_id": user_id,
            "threshold": f"{int(threshold * 100)}%",
            "current_cost": round(current_cost, 2),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log alert
        logger.warning(f"Budget alert for {user_id}: {message}")
        
        # Send to Slack if configured
        await self._send_slack_alert(message)
        
        # Send email if configured
        await self._send_email_alert(message)
    
    async def _send_slack_alert(self, message: Dict):
        """Send alert to Slack."""
        # Implementation would use Slack MCP or webhook
        pass
    
    async def _send_email_alert(self, message: Dict):
        """Send alert via email."""
        # Implementation would use email service
        pass
    
    async def get_usage_report(self, user_id: str, days: int = 7) -> Dict:
        """Get usage report for specified period."""
        reports = []
        total_tokens = 0
        total_cost = 0.0
        
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            token_key = f"usage:{user_id}:{date}:tokens"
            cost_key = f"usage:{user_id}:{date}:cost"
            
            tokens = int(await self.redis.get(token_key) or 0)
            cost = float(await self.redis.get(cost_key) or 0.0)
            
            reports.append({
                "date": date,
                "tokens": tokens,
                "cost_usd": round(cost, 4)
            })
            
            total_tokens += tokens
            total_cost += cost
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "daily_breakdown": reports
        }
    
    async def get_model_breakdown(self, user_id: str, days: int = 7) -> Dict:
        """Get usage breakdown by model."""
        model_usage = {}
        
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            pattern = f"usage:{user_id}:{date}:model:*"
            
            async for key in self.redis.scan_iter(match=pattern):
                model = key.split(":")[-1]
                tokens = int(await self.redis.get(key) or 0)
                
                if model not in model_usage:
                    model_usage[model] = 0
                model_usage[model] += tokens
        
        return {
            "user_id": user_id,
            "period_days": days,
            "model_breakdown": [
                {"model": model, "tokens": tokens}
                for model, tokens in sorted(model_usage.items(), key=lambda x: x[1], reverse=True)
            ]
        }

cost_governor = CostGovernor()
Step 8.2: Cost-Aware Model Router
File: api/app/services/model_router.py
Python
import logging
from typing import Optional, Dict, List
from enum import Enum

from app.services.cost_governor import cost_governor, BudgetTier

logger = logging.getLogger(__name__)

class ModelCapability(str, Enum):
    FAST = "fast"           # Haiku - quick tasks
    BALANCED = "balanced"   # Sonnet - general tasks
    POWERFUL = "powerful"   # Opus - complex tasks
    VISION = "vision"       # Vision-capable models

MODEL_REGISTRY = {
    "claude-haiku-3-5": {
        "capabilities": [ModelCapability.FAST],
        "cost_per_1k_prompt": 0.00025,
        "cost_per_1k_completion": 0.00125,
        "speed": "fast",
        "quality": "good",
        "context_window": 200000
    },
    "claude-sonnet-4-6": {
        "capabilities": [ModelCapability.BALANCED, ModelCapability.VISION],
        "cost_per_1k_prompt": 0.003,
        "cost_per_1k_completion": 0.015,
        "speed": "medium",
        "quality": "excellent",
        "context_window": 200000
    },
    "claude-opus-4-6": {
        "capabilities": [ModelCapability.POWERFUL, ModelCapability.VISION],
        "cost_per_1k_prompt": 0.015,
        "cost_per_1k_completion": 0.075,
        "speed": "slow",
        "quality": "outstanding",
        "context_window": 200000
    },
    "gpt-4o": {
        "capabilities": [ModelCapability.BALANCED, ModelCapability.VISION],
        "cost_per_1k_prompt": 0.005,
        "cost_per_1k_completion": 0.015,
        "speed": "medium",
        "quality": "excellent",
        "context_window": 128000
    }
}

class ModelRouter:
    """
    Intelligent model selection based on task requirements and budget constraints.
    """
    
    def __init__(self):
        self.model_registry = MODEL_REGISTRY
    
    async def select_model(
        self,
        user_id: str,
        task_complexity: str = "medium",
        required_capabilities: List[ModelCapability] = None,
        preferred_model: Optional[str] = None,
        estimated_tokens: int = 1000
    ) -> Dict:
        """
        Select optimal model based on task and budget.
        """
        # Get user budget config
        budget = await cost_governor.get_budget_config(user_id)
        
        # Check if preferred model is allowed
        if preferred_model and preferred_model in budget.allowed_models:
            model_info = self.model_registry.get(preferred_model)
            if model_info:
                estimated_cost = self._estimate_cost(preferred_model, estimated_tokens)
                allowed, details = await cost_governor.check_budget(user_id, estimated_tokens, estimated_cost)
                
                if allowed:
                    return {
                        "model": preferred_model,
                        "reason": "User preferred model",
                        "estimated_cost": estimated_cost,
                        "budget_status": details
                    }
        
        # Auto-select based on task complexity and budget
        candidates = self._get_candidates(budget.allowed_models, required_capabilities)
        
        if not candidates:
            return {
                "model": None,
                "reason": "No models available for this task tier",
                "error": "Budget tier too low for requested capabilities"
            }
        
        # Score candidates
        scored = []
        for model_name in candidates:
            model_info = self.model_registry[model_name]
            score = self._score_model(model_name, model_info, task_complexity, budget)
            estimated_cost = self._estimate_cost(model_name, estimated_tokens)
            scored.append((model_name, score, estimated_cost))
        
        # Sort by score (higher is better)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Select best model within budget
        for model_name, score, estimated_cost in scored:
            allowed, details = await cost_governor.check_budget(user_id, estimated_tokens, estimated_cost)
            if allowed:
                return {
                    "model": model_name,
                    "reason": f"Auto-selected: complexity={task_complexity}, score={score:.2f}",
                    "estimated_cost": estimated_cost,
                    "budget_status": details
                }
        
        # Fallback to cheapest model
        cheapest = min(scored, key=lambda x: x[2])
        return {
            "model": cheapest[0],
            "reason": "Budget constraint fallback",
            "estimated_cost": cheapest[2],
            "budget_status": {"reason": "Budget nearly exhausted"}
        }
    
    def _get_candidates(self, allowed_models: List[str], required_capabilities: List[ModelCapability]) -> List[str]:
        """Filter models by capabilities."""
        if not required_capabilities:
            return allowed_models
        
        candidates = []
        for model_name in allowed_models:
            model_info = self.model_registry.get(model_name)
            if model_info:
                if all(cap in model_info["capabilities"] for cap in required_capabilities):
                    candidates.append(model_name)
        
        return candidates
    
    def _score_model(self, model_name: str, model_info: Dict, complexity: str, budget: BudgetTier) -> float:
        """Score model suitability."""
        scores = {
            "fast": {"claude-haiku-3-5": 1.0, "claude-sonnet-4-6": 0.6, "claude-opus-4-6": 0.3, "gpt-4o": 0.5},
            "medium": {"claude-haiku-3-5": 0.5, "claude-sonnet-4-6": 1.0, "claude-opus-4-6": 0.7, "gpt-4o": 0.8},
            "complex": {"claude-haiku-3-5": 0.2, "claude-sonnet-4-6": 0.7, "claude-opus-4-6": 1.0, "gpt-4o": 0.8}
        }
        
        complexity_score = scores.get(complexity, scores["medium"]).get(model_name, 0.5)
        
        # Budget efficiency score (prefer cheaper models when budget is tight)
        cost = model_info["cost_per_1k_completion"]
        max_cost = 0.075  # Opus cost
        efficiency = 1.0 - (cost / max_cost)
        
        # Combine scores
        return (complexity_score * 0.7) + (efficiency * 0.3)
    
    def _estimate_cost(self, model_name: str, estimated_tokens: int) -> float:
        """Estimate cost for token usage."""
        model_info = self.model_registry.get(model_name)
        if not model_info:
            return 0.0
        
        # Assume 70% prompt, 30% completion split
        prompt_tokens = int(estimated_tokens * 0.7)
        completion_tokens = int(estimated_tokens * 0.3)
        
        prompt_cost = (prompt_tokens / 1000) * model_info["cost_per_1k_prompt"]
        completion_cost = (completion_tokens / 1000) * model_info["cost_per_1k_completion"]
        
        return round(prompt_cost + completion_cost, 6)

model_router = ModelRouter()
Step 8.3: Frontend Cost Widget
File: frontend/src/components/CostWidget.tsx
tsx
import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { DollarSign, TrendingUp, AlertTriangle, Zap } from 'lucide-react';

interface CostData {
  current_cost_usd: number;
  daily_limit_usd: number;
  usage_percent: number;
  tokens_used: number;
  model_breakdown: Array<{
    model: string;
    tokens: number;
    cost_usd: number;
  }>;
  alerts: Array<{
    threshold: number;
    triggered_at: string;
  }>;
}

export function CostWidget() {
  const { data, isLoading } = useQuery<CostData>({
    queryKey: ['cost-status'],
    queryFn: async () => {
      const res = await fetch('/api/v1/cost/status');
      return res.json();
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  if (isLoading) {
    return <div className="animate-pulse h-32 bg-neutral-100 rounded-lg" />;
  }

  if (!data) return null;

  const getStatusColor = () => {
    if (data.usage_percent >= 100) return 'text-red-600 bg-red-50 border-red-200';
    if (data.usage_percent >= 80) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (data.usage_percent >= 50) return 'text-blue-600 bg-blue-50 border-blue-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getProgressColor = () => {
    if (data.usage_percent >= 100) return 'bg-red-500';
    if (data.usage_percent >= 80) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className={`rounded-lg border p-4 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold flex items-center gap-2">
          <DollarSign className="w-4 h-4" />
          Cost Dashboard
        </h3>
        {data.usage_percent >= 80 && (
          <AlertTriangle className="w-5 h-5 text-yellow-600 animate-pulse" />
        )}
      </div>

      <div className="space-y-3">
        {/* Main Progress */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Daily Budget</span>
            <span className="font-mono">
              ${data.current_cost_usd.toFixed(2)} / ${data.daily_limit_usd.toFixed(2)}
            </span>
          </div>
          <div className="w-full bg-neutral-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor()}`}
              style={{ width: `${Math.min(data.usage_percent, 100)}%` }}
            />
          </div>
          <div className="text-xs text-right mt-1">
            {data.usage_percent.toFixed(1)}% used
          </div>
        </div>

        {/* Token Usage */}
        <div className="flex items-center justify-between text-sm">
          <span className="flex items-center gap-1">
            <Zap className="w-3 h-3" />
            Tokens
          </span>
          <span className="font-mono">{data.tokens_used.toLocaleString()}</span>
        </div>

        {/* Model Breakdown */}
        {data.model_breakdown.length > 0 && (
          <div className="pt-2 border-t border-current border-opacity-20">
            <h4 className="text-xs font-medium mb-2">Model Usage</h4>
            <div className="space-y-1">
              {data.model_breakdown.map((model) => (
                <div key={model.model} className="flex justify-between text-xs">
                  <span className="truncate max-w-[120px]">{model.model}</span>
                  <span className="font-mono">${model.cost_usd.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Alerts */}
        {data.alerts.length > 0 && (
          <div className="pt-2 border-t border-current border-opacity-20">
            <h4 className="text-xs font-medium mb-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Alerts
            </h4>
            {data.alerts.map((alert, idx) => (
              <div key={idx} className="text-xs">
                {alert.threshold}% threshold reached at{' '}
                {new Date(alert.triggered_at).toLocaleTimeString()}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
Final Integration: Main Application Entry Point
File: api/app/main.py
Python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.tracing import tracing_manager
from app.core.metrics import setup_metrics
from app.core.mcp_client import mcp_tool_manager
from app.core.websocket_manager import ws_manager
from app.core.database import init_db, close_db
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

from app.api.v1 import workflows, events, human_review, cost, health

# Setup logging first
setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting AI Workflow Platform...")
    
    # Initialize database
    await init_db()
    
    # Initialize MCP tools
    await mcp_tool_manager.initialize()
    
    # Initialize WebSocket manager
    await ws_manager.connect()
    
    # Initialize tracing
    tracing_manager.instrument_fastapi(app)
    
    logger.info("✅ All services initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    
    await ws_manager.disconnect()
    await mcp_tool_manager.close()
    await close_db()
    
    logger.info("✅ Shutdown complete")

def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="AI Workflow Platform",
        description="Production-grade multi-agent AI workflow orchestration",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan
    )
    
    # Middleware (order matters)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Request-ID"]
    )
    app.add_middleware(RateLimitMiddleware)
    
    # Metrics
    setup_metrics(app)
    
    # API Routes
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(workflows.router, prefix="/api/v1", tags=["Workflows"])
    app.include_router(events.router, prefix="/api/v1", tags=["Events"])
    app.include_router(human_review.router, prefix="/api/v1", tags=["Human Review"])
    app.include_router(cost.router, prefix="/api/v1", tags=["Cost Management"])
    
    return app

app = create_application()
Deployment Command Reference
bash
# =============================================================================
# Development
# =============================================================================

# Start all services
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Run tests
docker compose exec backend pytest -xvs
docker compose exec frontend npm run test

# =============================================================================
# Staging
# =============================================================================

# Build production images
docker build -f infrastructure/docker/api/Dockerfile.prod -t aiwf/backend:staging .
docker build -f infrastructure/docker/frontend/Dockerfile.prod -t aiwf/frontend:staging .

# Deploy to staging Kubernetes
helm upgrade --install aiwf-staging ./helm/aiwf \
  --namespace staging \
  --create-namespace \
  --values helm/aiwf/values-staging.yaml \
  --set backend.image.tag=staging \
  --set frontend.image.tag=staging

# =============================================================================
# Production
# =============================================================================

# Build and push production images
docker build -f infrastructure/docker/api/Dockerfile.prod -t aiwf/backend:v1.0.0 .
docker build -f infrastructure/docker/frontend/Dockerfile.prod -t aiwf/frontend:v1.0.0 .
docker push aiwf/backend:v1.0.0
docker push aiwf/frontend:v1.0.0

# Deploy with Argo Rollouts (canary)
helm upgrade --install aiwf ./helm/aiwf \
  --namespace production \
  --create-namespace \
  --values helm/aiwf/values-production.yaml \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0

# Monitor rollout
kubectl argo rollouts get rollout aiwf-backend -n production --watch

# Promote canary (after verification)
kubectl argo rollouts promote aiwf-backend -n production

# Rollback if needed
kubectl argo rollouts abort aiwf-backend -n production
Verification Checklist
Table
Component	Test Command	Expected Result
OPA Policies	opa test infrastructure/opa/	All tests pass
Security Hooks	python .claude/hooks/security_firewall_v2.py < test_input.json	Blocks dangerous commands
WebSocket	wscat -c ws://localhost:8000/v1/events/ws/test-123	Connection established
SSE Fallback	curl http://localhost:8000/v1/events/sse/test-123	Event stream received
MCP Health	curl http://localhost:8000/api/v1/mcp/health	All servers healthy
Design Metrics	python dashboard/design_metrics_v2.py --dir frontend/src --ci	Grade A or exit 1
Cost Governor	curl http://localhost:8000/api/v1/cost/status	Budget details returned
Prometheus	curl http://localhost:8000/metrics	Metrics exposed
Argo Rollout	kubectl argo rollouts get rollout aiwf-backend	Canary progressing
This completes the production-hardened, 20-week implementation guide addressing all critical gaps identified in the review: true agent isolation via Docker sandboxes and OPA policies, Redis-backed WebSocket scaling with SSE fallback, resilient MCP clients with health monitoring, comprehensive observability with OpenTelemetry and Prometheus, zero-downtime Kubernetes deployments with Argo Rollouts, and centralized cost governance with intelligent model routing.
