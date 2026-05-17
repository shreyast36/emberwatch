"""Compliance Agent — validates the draft response against CloudBase policies."""

import anthropic

from alignguard.sample_system.prompts import COMPLIANCE_SYSTEM as _SYSTEM
from alignguard.sample_system.tools import check_policy_compliance
from alignguard.types import AgentTrace, ToolCall

_TOOL = {
    "name": "compliance_verdict",
    "description": "Submit your policy compliance verdict.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "fail", "escalate"]},
            "violations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of policy violations found (empty if pass).",
            },
            "corrected_draft": {
                "type": "string",
                "description": "Corrected version of the draft if verdict is fail, else empty string.",
            },
            "reasoning": {"type": "string"},
        },
        "required": ["verdict", "violations", "corrected_draft", "reasoning"],
    },
}


class ComplianceAgent:
    def __init__(self, client: anthropic.AsyncAnthropic, model: str) -> None:
        self.client = client
        self.model = model

    async def run(self, draft_response: str, original_query: str) -> AgentTrace:
        rule_check = check_policy_compliance(draft_response)
        user_content = (
            f"Original customer query: {original_query}\n\n"
            f"Draft response to evaluate:\n{draft_response}\n\n"
            f"Rule-based pre-check result: {rule_check}"
        )
        result = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "compliance_verdict"},
        )
        inp = next(
            (dict(b.input) for b in result.content if getattr(b, "type", None) == "tool_use"),
            {"verdict": "pass", "violations": [], "corrected_draft": "", "reasoning": "fallback"},
        )
        tool_call = ToolCall(
            tool_name="check_policy_compliance",
            args={"response_draft": draft_response[:100]},
            result=str(rule_check),
        )
        output = (
            f"verdict={inp['verdict']} "
            f"violations={inp['violations']} "
            f"corrected={'<yes>' if inp.get('corrected_draft') else '<none>'}"
        )
        return AgentTrace(
            agent_name="compliance",
            input=draft_response,
            reasoning=inp.get("reasoning", ""),
            output=output,
            tools_used=[tool_call],
        )
