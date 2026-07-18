---
name: workflow-status
description: Check the status of recent workflows and cost usage
arguments:
  - name: task_id
    description: Optional specific workflow ID to check
    required: false
---

# Workflow Status

Check recent workflow runs and cost governance status from the platform.

## Usage

```
/workflow-status               # List recent workflows
/workflow-status <task_id>      # Get specific workflow detail
```

## Instructions

When invoked without a task_id:
1. Call `GET $AIWF_API_URL/api/v1/workflows?limit=10` 
2. Display a table: Task ID (first 8 chars), Status, Risk Level, Created, Cost
3. Call `GET $AIWF_API_URL/api/v1/cost/status` and show budget usage

When invoked with a task_id:
1. Call `GET $AIWF_API_URL/api/v1/workflows/{task_id}`
2. Display: full status, risk factors, final response, tokens used, cost
3. If human review is pending, show the review deadline and risk factors

If the API is unreachable, tell the user to start it with `docker compose up -d`
