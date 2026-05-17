"""Responder Agent — finalises and delivers the customer-facing response."""

import anthropic

from alignguard.sample_system.prompts import RESPONDER_SYSTEM as _SYSTEM
from alignguard.types import AgentTrace

_TOOL = {
    "name": "finalize_response",
    "description": "Submit the final customer-facing response.",
    "input_schema": {
        "type": "object",
        "properties": {
            "final_response": {"type": "string"},
            "escalated": {"type": "boolean"},
            "reasoning": {"type": "string", "description": "What you changed from the draft and why."},
        },
        "required": ["final_response", "escalated", "reasoning"],
    },
}


class ResponderAgent:
    def __init__(self, client: anthropic.AsyncAnthropic, model: str) -> None:
        self.client = client
        self.model = model

    async def run(self, knowledge_draft: str, compliance_output: str) -> AgentTrace:
        user_content = (
            f"Knowledge agent draft:\n{knowledge_draft}\n\n"
            f"Compliance verdict: {compliance_output}"
        )
        result = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "finalize_response"},
        )
        inp = next(
            (dict(b.input) for b in result.content if getattr(b, "type", None) == "tool_use"),
            {"final_response": knowledge_draft, "escalated": False, "reasoning": "fallback"},
        )
        return AgentTrace(
            agent_name="responder",
            input=f"draft={knowledge_draft[:120]} | compliance={compliance_output[:120]}",
            reasoning=inp.get("reasoning", ""),
            output=inp.get("final_response", ""),
        )
