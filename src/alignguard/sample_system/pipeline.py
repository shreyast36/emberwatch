"""Pipeline orchestrator — chains the 4 CloudBase support agents into a session."""

import anthropic

from alignguard.sample_system.agents.compliance import ComplianceAgent
from alignguard.sample_system.agents.knowledge import KnowledgeAgent
from alignguard.sample_system.agents.responder import ResponderAgent
from alignguard.sample_system.agents.triage import TriageAgent
from alignguard.types import SessionTrace

DEFAULT_MODEL = "claude-sonnet-4-6"


async def run_session(query: str, model: str = DEFAULT_MODEL) -> SessionTrace:
    """Run one customer query through the full 4-agent pipeline."""
    client = anthropic.AsyncAnthropic()

    triage = TriageAgent(client, model)
    knowledge = KnowledgeAgent(client, model)
    compliance = ComplianceAgent(client, model)
    responder = ResponderAgent(client, model)

    triage_trace = await triage.run(query)
    knowledge_trace = await knowledge.run(query, triage_trace.output)
    compliance_trace = await compliance.run(knowledge_trace.output, query)
    responder_trace = await responder.run(knowledge_trace.output, compliance_trace.output)

    return SessionTrace(
        query=query,
        traces=[triage_trace, knowledge_trace, compliance_trace, responder_trace],
        final_response=responder_trace.output,
    )
