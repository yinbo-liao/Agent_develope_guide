# AI Workflow Platform — User Guidance

## What Is This Project?

The **AI Workflow Platform** is a production-grade multi-agent AI orchestration system. It accepts natural language tasks from users, routes them through a risk-assessment pipeline, executes them using the most cost-effective LLM (Claude Haiku, Sonnet, Opus, or GPT-4o), and streams real-time progress to a monitoring dashboard. High-risk operations are automatically paused for human review before execution.

### Core Purpose

Turn natural language requests into governed, auditable, cost-controlled AI workflows — without requiring users to know which model to use, how much it costs, or whether the request is safe.

### What It's NOT

- A chatbot or conversational agent — it processes structured workflow tasks
- A model playground — models are selected and routed automatically based on task complexity, budget, and risk
- A code generation tool — it orchestrates operations, analysis, and review workflows

---

## Architecture at a Glance

```
User Request ──► API (FastAPI) ──► Risk Engine ──► Model Router ──► LLM Generation
                      │                  │               │               │
                      ▼                  ▼               ▼               ▼
              Real-time Dashboard   Human Review    Cost Governor    Semantic Cache
              (WebSocket + SSE)    (Critical ops)   (Budget tiers)   (Query reuse)
```

### Workflow Pipeline (5 Stages)

| Stage | What Happens |
|---|---|
| 1. **Validate Input** | Rejects empty or malformed queries |
| 2. **Retrieve Context** | Fetches relevant background information |
| 3. **Assess Risk** | Scores the query against 6 risk patterns → LOW / MEDIUM / HIGH / CRITICAL |
| 4. **Execute** | Routes based on risk: LOW → auto-generate, MEDIUM/HIGH → cascade routing, CRITICAL → human review |
| 5. **Review & Refine** | ReAct iteration loop, meta-cognitive adversarial review, human approval if needed |

### Risk Classification

| Risk Level | Threshold | Behavior |
|---|---|---|
| **LOW** | Score 0–9 | Auto-generated response, cheapest model |
| **MEDIUM** | Score 10–29 | Cascade routing with confidence scoring, ReAct refinement |
| **HIGH** | Score 30–49 | Cascade with powerful models, meta-review |
| **CRITICAL** | Score 50+ | Paused for human review, 30-minute deadline |

Risk patterns detect: payment data, destructive operations, privilege escalation, deletion requests, credential access, and data modification — with adaptive weights that learn from reviewer decisions.

---

## How to Set Up

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Quick Start (5 minutes)

```bash
# 1. Clone and enter
git clone git@github.com:yinbo-liao/Agent_develope_guide.git
cd Agent_develope_guide

# 2. Start all services (PostgreSQL, Redis, OPA, Backend, Frontend)
docker compose up -d

# 3. Verify health
curl http://localhost:8000/health
# → {"status":"ok","service":"AI Workflow Platform","environment":"development"}

# 4. Open the dashboard
# Visit http://localhost:5173 in your browser
```

### Development Setup

```bash
# Backend
cd api
pip install -e ".[dev]"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Run tests
cd api && pytest tests/ -v     # 62 tests
cd frontend && npm run typecheck
```

### Environment Configuration

Copy `api/.env.example` to `api/.env` and set:

| Variable | Purpose | Required in Production? |
|---|---|---|
| `SECRET_KEY` | JWT signing key (min 32 chars in prod) | YES |
| `DATABASE_URL` | PostgreSQL connection string | YES |
| `REDIS_URL` | Redis connection string | YES |
| `ENVIRONMENT` | `development` / `staging` / `production` | YES |
| `OPA_URL` | Open Policy Agent endpoint | No (default: http://opa:8181) |

The platform **refuses to start** in production mode with insecure default values.

---

## API Reference

### Authentication

All protected endpoints require a JWT Bearer token:

```bash
# Get a token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Use the token
curl http://localhost:8000/api/v1/workflows \
  -H "Authorization: Bearer <access_token>"
```

### Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/token` | Login — get access + refresh tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh an expired access token |
| `POST` | `/api/v1/workflows` | Create and queue a new workflow |
| `GET` | `/api/v1/workflows` | List your workflows (paginated: `?offset=0&limit=20`) |
| `GET` | `/api/v1/workflows/{id}` | Get workflow detail + results |
| `POST` | `/api/v1/human-review/decide` | Approve or reject a paused workflow |
| `WS` | `/api/v1/events/ws/{id}` | Real-time WebSocket event stream |
| `GET` | `/api/v1/events/sse/{id}` | Server-Sent Events stream (fallback) |
| `GET` | `/api/v1/cost/status` | Your current cost & usage |
| `GET` | `/api/v1/cost/optimization-insights` | Cost savings from caching & cascade routing |
| `GET` | `/api/v1/analytics/insights` | Pattern analysis & improvement suggestions (admin) |
| `GET` | `/api/v1/mcp/health` | MCP tool server status |
| `POST` | `/api/v1/mcp/invoke/{server}/{tool}` | Invoke an MCP tool |

### Creating a Workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "input_query": "Review the deployment change plan for security impact.",
    "token_budget": 10000,
    "cost_budget_usd": 5.0
  }'
```

Response (202 Accepted):
```json
{
  "id": "a1b2c3d4-...",
  "user_id": "your-user-id",
  "current_status": "pending",
  "risk_level": "low",
  "is_human_review_needed": false
}
```

### Monitoring a Workflow

**Option 1: Dashboard** — Open `http://localhost:5173`, enter your user ID, create a workflow, and watch it progress in real-time.

**Option 2: WebSocket** — Connect to `ws://localhost:8000/api/v1/events/ws/{task_id}` to receive step-by-step progress events.

**Option 3: REST polling** — `GET /api/v1/workflows/{task_id}` returns the current state.

---

## Key Features

### Cost Optimization ("Reasonix")

| Feature | How It Saves |
|---|---|
| **Semantic Cache** | Identical or similar queries reuse cached responses — zero LLM cost |
| **Cascade Routing** | Tries cheapest model first, escalates to more expensive only if confidence is low |
| **Prompt Compression** | Truncates low-relevance context, caps snippet length at 200 chars |
| **Confidence Scoring** | Stops escalation at 70% confidence — avoids unnecessary expensive calls |

### Budget Tiers

| Tier | Daily Tokens | Daily Cost | Concurrent Workflows | Models |
|---|---|---|---|---|
| Free | 10K | $1.00 | 1 | Haiku |
| Starter | 100K | $10.00 | 3 | Haiku, Sonnet |
| Professional | 1M | $100.00 | 10 | Haiku, Sonnet, Opus |
| Enterprise | 10M | $1,000.00 | 50 | Haiku, Sonnet, Opus, GPT-4o |

Alerts fire at 50%, 80%, and 100% of daily budget. Budget-exceeded workflows go to the Dead Letter Queue for later replay.

### Security Layers

| Layer | What It Protects |
|---|---|
| **JWT Authentication** | All API endpoints require valid tokens; WebSocket auth via query params |
| **Cross-User Isolation** | Users can only see their own workflows — 404 for others' data |
| **OPA Policy Engine** | Agent-level read/write/execute/network permission enforcement |
| **Security Firewall** | Blocks dangerous shell commands, destructive SQL, hardcoded secrets, protected path access |
| **Production Secret Validation** | Refuses to start if insecure defaults are detected in production mode |
| **Rate Limiting** | Per-IP sliding window with Redis-backed shared state |
| **Audit Logging** | Structured JSONL logs with sensitive data redaction |

### Reliability

| Feature | What It Does |
|---|---|
| **Exponential Backoff Retry** | Failed workflows retry up to 3 times with `2^n` second delays |
| **Per-Model Circuit Breakers** | Opens after 3 consecutive failures, half-open probe after 30s |
| **Dead Letter Queue** | Failed workflows are preserved for inspection and replay |
| **Auto-Remediation** | Timeout → longer wait, Circuit open → queue, Budget exceeded → defer to DLQ |
| **WebSocket Auto-Reconnect** | Exponential backoff with jitter, SSE fallback after 5 WS attempts |
| **Memory Leak Protection** | Periodic cleanup of orphaned WebSocket connections (every 5 min) |

### Self-Improvement

| Feature | How It Learns |
|---|---|
| **Adaptive Risk Assessment** | Adjusts pattern weights based on human reviewer approve/reject decisions |
| **ReAct Iteration Loop** | Evaluates output quality, refines with better prompts up to 3 iterations |
| **Meta-Cognitive Review** | Adversarial review using a different model to catch hallucinations |
| **Feedback Analyzer** | Mines audit logs for failure patterns, false positive rates, and improvement suggestions |
| **Confidence Scoring** | 6-dimension heuristic that improves routing decisions over time |

---

## Monitoring Dashboard

The React dashboard at `http://localhost:5173` provides:

- **Workflow Creator** — Submit natural language tasks with budget controls
- **Step Timeline** — Real-time visualization of each pipeline stage
- **Risk Factors** — See why a workflow was classified at its risk level
- **Human Review Panel** — Approve/reject paused workflows with comments
- **Cost Widget** — Live usage vs. budget, per-model breakdown, alert notifications
- **Transport Indicator** — Shows WebSocket/SSE connection status
- **Recent Runs** — Quick access to past workflows

---

## Claude Code Agent Plugin

The platform integrates as a **Claude Code agent plugin** — invoke governed workflows, check cost status, and use MCP tools directly from Claude Code.

### What the Plugin Provides

| Integration | Location | What It Does |
|---|---|---|
| **Slash Commands** | `.claude/skills/` | `/workflow` and `/workflow-status` |
| **MCP Server** | `api/app/mcp/server.py` | 4 MCP tools: `create_workflow`, `get_workflow_status`, `list_workflows`, `get_cost_status` |
| **Security Hooks** | `.claude/hooks/` | Blocks dangerous commands, destructive SQL, hardcoded secrets |
| **Audit Logging** | `.claude/hooks/` | JSONL audit trail with sensitive data redaction |
| **Agent Roles** | `.claude/agents/` | 5 scoped agent definitions enforced by OPA |
| **CLI** | `python -m app.cli` | Run workflows from command line without HTTP server |

### Slash Commands

#### `/workflow` — Submit a Governed Task

```
/workflow "analyze security impact of deployment PR #42"
```

What happens: query is risk-assessed → best model selected → results streamed back with step progress, cost, and model info. Critical queries pause for human review.

#### `/workflow-status` — Check Status

```
/workflow-status                    # List 10 most recent workflows
/workflow-status <task-id>          # Full detail for a specific workflow
```

### MCP Server Setup

Registered automatically via `.claude/settings.json`. The platform must be running (`docker compose up -d`).

**MCP tools exposed:**

| Tool | Parameters | Purpose |
|---|---|---|
| `mcp__aiwf_platform__create_workflow` | `query`, `token_budget`, `cost_budget_usd` | Create + execute governed workflow |
| `mcp__aiwf_platform__get_workflow_status` | `task_id` | Get workflow status and results |
| `mcp__aiwf_platform__list_workflows` | `limit` | List recent workflow runs |
| `mcp__aiwf_platform__get_cost_status` | `user_id` | Show budget and usage |

Claude Code launches `python -m app.mcp.server` as a subprocess and communicates via JSON-RPC 2.0 over stdio.

### CLI Usage

```bash
# Basic
python -m app.cli "review deployment security"

# With options
python -m app.cli "analyze migration risks" --user-id demo-user --budget 20000 --cost-limit 10.0
```

### Security Hooks

**PreToolUse — Security Firewall** (`.claude/hooks/security_firewall_v2.py`):
- Runs before Bash, Edit, Write tool calls
- Blocks: `rm -rf /`, `curl | bash`, destructive SQL, `~/.ssh`, `~/.aws`, `.env`
- Detects: hardcoded secrets (GitHub tokens, API keys, AWS keys)

**PostToolUse — Audit Logger** (`.claude/hooks/audit_logger_v2.py`):
- Runs after every tool call, logs to `.claude/audit.jsonl`
- Auto-redacts: passwords, secrets, tokens, keys

### Agent Definitions

| Agent | Read | Write | Execute | Network |
|---|---|---|---|---|
| **governor** | `/` | `.claude`, `docs` | `git` | Yes |
| **frontend-dev** | `frontend`, `docs` | `frontend` | `npm`, `node`, `vitest` | No |
| **backend-dev** | `api`, `infrastructure` | `api`, `docker` | `python`, `pytest`, `alembic` | Yes |
| **security-auditor** | `/` | _(none)_ | `grep`, `bandit`, `safety` | No |
| **design-director** | `frontend`, `docs` | `design-tokens.json` | `node`, `npx` | No |

Fail-closed: if OPA is unreachable, access is denied.

### Activating the Plugin

1. Start platform: `docker compose up -d`
2. Verify: `curl http://localhost:8000/health`
3. Restart Claude Code — it reads `.claude/settings.json` on startup
4. Test: type `/workflow "hello world"` in Claude Code

### Plugin File Structure

```
.claude/
  settings.json              MCP server + hook registration
  skills/workflow.md         /workflow slash command
  skills/workflow-status.md  /workflow-status slash command
  agents/*.md                5 agent role definitions
  hooks/security_firewall_v2.py  PreToolUse hook
  hooks/audit_logger_v2.py       PostToolUse hook
api/app/
  mcp/server.py              MCP JSON-RPC server (4 tools)
  mcp/backends/postgres.py   Real Postgres backend
  mcp/backends/github.py     Real GitHub backend
  cli.py                     CLI entry point
```

---

## Expected Results

### For End Users

1. **Submit a task** → Get an AI-generated response within seconds for low-risk queries
2. **Cost visibility** → See exactly how much each workflow costs before it runs
3. **Risk awareness** → Understand which queries trigger security review and why
4. **No model decisions** → The platform picks the right model automatically

### For Operators / Administrators

1. **Cost governance** — Per-user budget tiers with automatic enforcement and alerts
2. **Audit trail** — Every decision, MCP tool call, and human review is logged
3. **Failure recovery** — Dead Letter Queue preserves failed workflows for replay
4. **Improvement insights** — `/api/v1/analytics/insights` provides data-driven optimization suggestions

### Performance Benchmarks (Development Environment)

| Metric | Expected |
|---|---|
| Workflow creation latency | < 50ms |
| Low-risk workflow completion | < 1s (simulated LLM) |
| WebSocket event delivery | < 100ms |
| Budget check | < 10ms |
| Test suite execution | < 70s (62 tests) |

---

## Common Operations

### Check System Health

```bash
curl http://localhost:8000/health        # Basic health
curl http://localhost:8000/health/ready  # DB + Redis + OPA readiness
```

### View Your Cost Status

```bash
curl http://localhost:8000/api/v1/cost/status \
  -H "Authorization: Bearer <token>"
```

### Replay a Failed Workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows/dlq/{dlq_id}/replay \
  -H "Authorization: Bearer <token>"
```

### List Dead-Lettered Workflows

```bash
curl http://localhost:8000/api/v1/workflows/dlq/entries \
  -H "Authorization: Bearer <token>"
```

### Run Database Migrations

```bash
cd api
# Set DATABASE_URL for your environment, then:
alembic upgrade head
```

### Run All Tests

```bash
cd api && pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Project Structure

```
api/                         FastAPI backend (Python 3.11+)
  app/
    api/v1/                  REST + WebSocket endpoints
    core/                    Config, DB, cache, circuit breaker, MCP, tracing
    middleware/               Auth, rate limiting, correlation IDs
    models/                  SQLAlchemy ORM (workflows, users, audits)
    security/                JWT auth, OPA client
    services/                Cost governor, model router, LLM client, semantic cache
    workflows/               Graph engine, nodes, runner, human review
  tests/unit/                62 unit tests
  alembic/                   Database migrations
frontend/                    React 19 SPA (TypeScript 5, Vite 5, Tailwind 3)
infrastructure/
  docker/                    Dev + production Dockerfiles
  opa/                       Agent policy definitions (Rego)
  prometheus/                Alert rules + Alertmanager config
  grafana/                   Pre-built dashboards
helm/aiwf/                   Kubernetes Helm chart
.claude/
  settings.json              MCP server + hook registration
  skills/                    /workflow + /workflow-status slash commands
  agents/                    5 agent role definitions
  hooks/                     Security firewall + audit logger
api/app/
  mcp/                       MCP server + real backends (Postgres, GitHub)
  cli.py                     CLI entry point
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "no such table: workflow_runs" | Run `alembic upgrade head` |
| 401 Unauthorized | Get a new token via `/api/v1/auth/token` |
| Redis connection refused | Start Redis: `docker compose up -d redis` |
| Circuit breaker open | Wait 30s for automatic half-open probe |
| WebSocket disconnects | Auto-reconnect with backoff; check browser console |
| Budget exceeded | Wait for next day's window, or replay from DLQ |
