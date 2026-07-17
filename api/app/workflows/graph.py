from __future__ import annotations

from app.models.workflow import WorkflowRun
from app.workflows.nodes import (
    assess_risk,
    auto_generate_response,
    complex_analysis,
    evaluate_output_quality,
    human_review_node,
    meta_review_node,
    retrieve_context_node,
    validate_input,
)
from app.workflows.state import RiskLevel, WorkflowStatus

MAX_REACT_ITERATIONS = 3


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
            # ReAct loop: evaluate quality, refine if needed
            for iteration in range(MAX_REACT_ITERATIONS):
                last = steps[-1]
                run.final_response = str(last.get("final_response", ""))
                run.current_status = str(last.get("current_status", ""))

                if run.current_status == WorkflowStatus.FAILED.value:
                    break

                quality = await evaluate_output_quality(run)
                steps.append(quality)

                if not quality.get("needs_refinement"):
                    break

                # Refine: re-run analysis with quality feedback
                refinement_step = await complex_analysis(run)
                steps.append(refinement_step)

            # Meta-cognitive review: adversarial check on final output
            last = steps[-1]
            run.final_response = str(last.get("final_response", ""))
            run.current_status = str(last.get("current_status", ""))
            if run.current_status != WorkflowStatus.FAILED.value:
                review = await meta_review_node(run)
                steps.append(review)
                if review.get("needs_regeneration"):
                    regen = await complex_analysis(run)
                    steps.append(regen)
        else:
            steps.append(await human_review_node(run))

        return steps


workflow_graph = WorkflowGraph()
