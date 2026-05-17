"""Triage Agent — classifies and prioritises incoming customer queries."""

import anthropic

from alignguard.sample_system.prompts import TRIAGE_SYSTEM as _SYSTEM
from alignguard.types import AgentTrace

_TOOL = {
    "name": "classify_query",
    "description": "Classify the customer query by category and urgency.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["billing", "technical", "account", "refund", "privacy", "general"],
            },
            "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
            "key_intent": {"type": "string", "description": "One-sentence summary of what the customer actually wants."},
            "reasoning": {"type": "string", "description": "Why you chose this category and urgency."},
        },
        "required": ["category", "urgency", "key_intent", "reasoning"],
    },
}


class TriageAgent:
    def __init__(self, client: anthropic.AsyncAnthropic, model: str) -> None:
        self.client = client
        self.model = model

    async def run(self, query: str) -> AgentTrace:
        result = await self.client.messages.create(
            model=self.model,
            max_tokens=512,
            system=_SYSTEM,
            messages=[{"role": "user", "content": query}],
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "classify_query"},
        )
        inp = next(
            (dict(b.input) for b in result.content if getattr(b, "type", None) == "tool_use"),
            {"category": "general", "urgency": "low", "key_intent": query, "reasoning": "fallback"},
        )
        return AgentTrace(
            agent_name="triage",
            input=query,
            reasoning=inp.get("reasoning", ""),
            output=f"category={inp['category']} urgency={inp['urgency']} intent={inp['key_intent']}",
        )
