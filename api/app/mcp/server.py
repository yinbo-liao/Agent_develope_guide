"""
MCP (Model Context Protocol) server for the AI Workflow Platform.

Exposes platform capabilities as MCP tools that Claude Code can invoke.
Communicates via JSON-RPC 2.0 over stdio.
"""

from __future__ import annotations

import json
import sys
from typing import Any

# Tool definitions
TOOLS = [
    {
        "name": "create_workflow",
        "description": "Create a governed AI workflow. The query is assessed for risk, routed to the best model, and executed with cost tracking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language task description",
                    "minLength": 3,
                },
                "token_budget": {
                    "type": "integer",
                    "description": "Maximum tokens to use (default: 10000)",
                    "default": 10000,
                },
                "cost_budget_usd": {
                    "type": "number",
                    "description": "Maximum cost in USD (default: 5.0)",
                    "default": 5.0,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_workflow_status",
        "description": "Get the status and results of a specific workflow.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The workflow task ID",
                },
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "list_workflows",
        "description": "List recent workflow runs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Max workflows to return (default: 10, max: 100)",
                    "default": 10,
                },
            },
        },
    },
    {
        "name": "get_cost_status",
        "description": "Get current cost and budget usage for a user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID (default: demo-user)",
                    "default": "demo-user",
                },
            },
        },
    },
]


def _call_api(endpoint: str, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call the platform API and return JSON response. Uses urllib to avoid heavy deps."""
    import urllib.request
    import urllib.error

    base_url = "http://localhost:8000"
    url = f"{base_url}{endpoint}"

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    """Handle a single JSON-RPC request. Returns a response dict or None for notifications."""
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ai-workflow-platform", "version": "0.1.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        result: dict[str, Any] = {}
        if tool_name == "create_workflow":
            result = _call_api(
                "/api/v1/workflows",
                method="POST",
                body={
                    "user_id": "demo-user",
                    "input_query": arguments.get("query", ""),
                    "token_budget": arguments.get("token_budget", 10000),
                    "cost_budget_usd": arguments.get("cost_budget_usd", 5.0),
                },
            )
        elif tool_name == "get_workflow_status":
            result = _call_api(f"/api/v1/workflows/{arguments.get('task_id', '')}")
        elif tool_name == "list_workflows":
            limit = arguments.get("limit", 10)
            result = _call_api(f"/api/v1/workflows?limit={limit}")
        elif tool_name == "get_cost_status":
            user_id = arguments.get("user_id", "demo-user")
            result = _call_api(f"/api/v1/cost/status?user_id={user_id}")
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        content = json.dumps(result, indent=2)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": content}],
            },
        }

    if method == "notifications/initialized":
        return None  # No response for notifications

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main() -> int:
    """Run the MCP server over stdio (JSON-RPC 2.0)."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            sys.stderr.write(f"Invalid JSON: {line}\n")
            sys.stderr.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
