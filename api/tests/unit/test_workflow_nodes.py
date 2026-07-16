from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.models.workflow import WorkflowRun
from app.workflows.nodes import assess_risk, human_review_node
from app.workflows.state import RiskLevel, WorkflowStatus


def make_run(query: str) -> WorkflowRun:
    return WorkflowRun(
        id="test-id",
        user_id="user-1",
        session_id=None,
        input_query=query,
    )


def test_assess_risk_marks_destructive_queries_critical() -> None:
    run = make_run("drop all database tables and escalate to root")

    updates = asyncio.run(assess_risk(run))

    assert updates["risk_level"] == RiskLevel.CRITICAL.value
    assert updates["current_status"] == WorkflowStatus.REVIEWING.value


def test_human_review_pending_sets_review_state() -> None:
    run = make_run("review this change request")

    updates = asyncio.run(human_review_node(run))

    assert updates["is_human_review_needed"] is True
    assert updates["current_status"] == WorkflowStatus.REVIEWING.value
