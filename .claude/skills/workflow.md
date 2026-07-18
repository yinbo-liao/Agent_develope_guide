---
name: workflow
description: Submit a task to the AI Workflow Platform for governed, cost-tracked execution
arguments:
  - name: query
    description: Natural language task description
    required: true
---

# Workflow

Use this skill to invoke the AI Workflow Platform's governed execution pipeline.

## Usage

```
/workflow "your natural language task here"
```

## What happens

1. Your query is sent to the platform's risk assessment engine
2. Risk level is determined (LOW / MEDIUM / HIGH / CRITICAL)
3. The best model is selected based on complexity and your budget tier
4. The task is executed and results streamed back
5. Cost is tracked and governance rules are enforced

## Configuration

The platform API must be running at `$AIWF_API_URL` (default: http://localhost:8000).

## Instructions

When invoked, do the following:

1. Parse the user's query from the arguments
2. Call `POST $AIWF_API_URL/api/v1/workflows` with JSON body:
   ```json
   {
     "input_query": "<user query>",
     "token_budget": 10000,
     "cost_budget_usd": 5.0
   }
   ```
3. Extract the `id` from the response
4. Stream results via `GET $AIWF_API_URL/api/v1/events/sse/{id}` (Server-Sent Events)
5. Display each step as it arrives: step name, status, current step
6. When workflow completes (`current_status: "completed"` or `"failed"`):
   - Display the final response or error
   - Show risk level, model used, tokens consumed, and estimated cost
   - If human review is needed, instruct the user to use the dashboard
7. If the API is unreachable, tell the user to start it with `docker compose up -d`
