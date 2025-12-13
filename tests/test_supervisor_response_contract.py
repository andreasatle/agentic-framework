from __future__ import annotations

import json

from agentic.supervisor import SupervisorResponse
from domain.writer.schemas import WriterDomainState


def test_supervisor_response_is_json_serializable():
    response = SupervisorResponse(
        plan={"task": "example"},
        result={"text": "done"},
        decision={"decision": "ACCEPT"},
        project_state={"domain_state": {"foo": "bar"}},
        trace=[{"state": "PLAN"}, {"state": "END"}],
        loops_used=1,
    )

    serialized = response.model_dump()
    json.dumps(serialized)


def test_domain_state_can_be_rehydrated_from_response():
    original_state = WriterDomainState()
    state_snapshot = original_state.model_dump()

    response = SupervisorResponse(
        plan={"task": "rehydrate"},
        result={"text": "done"},
        decision={"decision": "ACCEPT"},
        project_state={"domain_state": state_snapshot},
        trace=[{"state": "PLAN"}, {"state": "END"}],
        loops_used=1,
    )

    stored_state = response.project_state.get("domain_state")
    rehydrated_state = WriterDomainState(**stored_state)

    assert rehydrated_state.model_dump() == state_snapshot
