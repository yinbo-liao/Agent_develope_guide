from __future__ import annotations

from app.models.workflow import WorkflowRun
from app.workflows.nodes import (
    assess_risk,
    auto_generate_response,
    complex_analysis,
    human_review_node,
    retrieve_context_node,
    validate_input,
)
from app.workflows.state import RiskLevel, WorkflowStatus


class WorkflowGraph:
    async def execute(self, run: WorkflowRun) -> list[dict[str, object]]:
        steps: list[dict[str, object]] = []

        steps.append(await validate_input(run))
        if steps[-1].get("current_status") == WorkflowStatus.FAILED.value:
            return steps

        run.current_status = str(steps[-1]["current_status"])
        run.current_step = str(steps[-1]["current_step"])

        steps.append(await retrieve_context_node(run))
        run.retrieval_results = steps[-1].get("retrieval_results")  # type: ignore[assignment]
        run.current_status = str(steps[-1]["current_status"])
        run.current_step = str(steps[-1]["current_step"])

        steps.append(await assess_risk(run))
        run.risk_level = str(steps[-1]["risk_level"])
        run.risk_factors = steps[-1].get("risk_factors", [])  # type: ignore[assignment]
        run.current_status = str(steps[-1]["current_status"])
        run.current_step = str(steps[-1]["current_step"])

        if run.risk_level == RiskLevel.LOW.value:
            steps.append(await auto_generate_response(run))
        elif run.risk_level in {RiskLevel.MEDIUM.value, RiskLevel.HIGH.value}:
            steps.append(await complex_analysis(run))
        else:
            steps.append(await human_review_node(run))

        return steps


workflow_graph = WorkflowGraph()
