import json

from openai import AsyncOpenAI

from app.config import settings
from app.schemas import AgentFindings

aclient = AsyncOpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)

SYSTEM_PROMPT = """You are a root cause analysis engine for production incidents.
You receive findings from multiple investigation agents (deployments, logs, metrics, git history).
Correlate the evidence and produce a JSON report with exactly these fields:

{
  "root_cause": "One sentence describing the probable root cause",
  "confidence": 0.0-1.0,
  "timeline": [
    {"time": "ISO timestamp or relative", "event": "description"}
  ],
  "recommendations": ["actionable recommendation 1", "..."]
}

Respond ONLY with valid JSON. No markdown, no explanation."""


async def build_prompt(findings: list[AgentFindings]) -> str:
    sections = []
    for f in findings:
        sections.append(f"## {f.agent_name.upper()} Agent\n{f.summary}\n\nData:\n{json.dumps(f.data, default=str)[:3000]}")
    return "\n\n".join(sections)


class CorrelationAgent:
    name = "correlation"

    async def correlate(self, findings: list[AgentFindings]) -> dict:
        prompt = await build_prompt(findings)
        response = await aclient.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
