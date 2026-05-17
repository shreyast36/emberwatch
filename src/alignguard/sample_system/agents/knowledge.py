"""Knowledge Agent — retrieves KB articles and drafts a response."""

import anthropic

from alignguard.sample_system.prompts import KNOWLEDGE_SYSTEM as _SYSTEM
from alignguard.sample_system.tools import kb_lookup
from alignguard.types import AgentTrace, ToolCall

_TOOL = {
    "name": "draft_response",
    "description": "Produce a draft response grounded in KB content.",
    "input_schema": {
        "type": "object",
        "properties": {
            "kb_sections_used": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Which KB section titles informed the draft.",
            },
            "draft": {"type": "string", "description": "The draft customer-facing response."},
            "reasoning": {"type": "string", "description": "How KB content maps to the customer need."},
            "needs_escalation": {"type": "boolean"},
            "escalation_reason": {"type": "string"},
        },
        "required": ["kb_sections_used", "draft", "reasoning", "needs_escalation"],
    },
}


class KnowledgeAgent:
    def __init__(self, client: anthropic.AsyncAnthropic, model: str) -> None:
        self.client = client
        self.model = model

    async def run(self, query: str, triage_output: str) -> AgentTrace:
        kb_content = kb_lookup(query)
        user_content = (
            f"Customer query: {query}\n\n"
            f"Triage result: {triage_output}\n\n"
            f"Relevant KB content:\n{kb_content}"
        )
        result = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "draft_response"},
        )
        inp = next(
            (dict(b.input) for b in result.content if getattr(b, "type", None) == "tool_use"),
            {"kb_sections_used": [], "draft": "Unable to draft response.", "reasoning": "fallback", "needs_escalation": False},
        )
        tool_call = ToolCall(
            tool_name="kb_lookup",
            args={"query": query},
            result=kb_content[:200] + "…",
        )
        return AgentTrace(
            agent_name="knowledge",
            input=f"query={query} | triage={triage_output}",
            reasoning=inp.get("reasoning", ""),
            output=inp.get("draft", ""),
            tools_used=[tool_call],
        )
