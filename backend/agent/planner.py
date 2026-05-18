"""
LLM-based planner. Decomposes task into one action at a time.
Critical design: small models (3–5B) cannot plan 10 steps at once.
We ask ONE question per call: "What is your SINGLE next action?"
"""
import json
import re
import ollama
from loguru import logger
from backend.agent.context import AgentContext, AgentThought
from backend.app.config import get_settings

settings = get_settings()

PLANNER_SYSTEM_PROMPT = """You are a research agent. You complete tasks step-by-step using tools.

AVAILABLE TOOLS:
{tool_schemas}

RULES:
1. Choose EXACTLY ONE tool per response.
2. Output ONLY valid JSON. No prose, no markdown.
3. If you have enough information, use "finish" with your answer.
4. If stuck after 3 failed steps on same action — try a different approach.
5. Write notes using write_note before synthesizing a final answer.

OUTPUT FORMAT (strict JSON only):
{{
  "reasoning": "Brief explanation of why this action now",
  "action": "tool_name_here",
  "args": {{"arg1": "value1"}},
  "confidence": 0.85
}}

TASK: {task}

PROGRESS SO FAR:
{history}

INSTRUCTIONS FROM FAILURE MEMORY:
{failure_lessons}

YOUR KNOWN WEAKNESSES FOR THIS TASK TYPE:
{capability_hints}

What is your SINGLE next action?"""

EVALUATOR_PROMPT = """You are evaluating an agent's reasoning step.

Task: {task}
Step action: {action}
Step reasoning: {reasoning}
Step result: {result}

Score this step from 0.0 to 1.0 on:
- Relevance: did this action help the task? (0-1)
- Efficiency: was this the most direct path? (0-1)
- Quality: was the result useful? (0-1)

Output ONLY JSON:
{{"relevance": 0.8, "efficiency": 0.7, "quality": 0.9, "overall": 0.8, "note": "brief note"}}"""


class AgentPlanner:
    def __init__(self, tool_registry, model: str | None = None):
        self.tools = tool_registry
        self.model = model or settings.smart_model  # phi4-mini by default

    async def decide(
        self,
        context: AgentContext,
        failure_lessons: str = "",
        capability_hints: str = "",
    ) -> AgentThought:
        prompt = PLANNER_SYSTEM_PROMPT.format(
            tool_schemas=self.tools.get_schemas_for_prompt(),
            task=context.task,
            history=context.to_prompt_history(max_steps=5),
            failure_lessons=failure_lessons or "None",
            capability_hints=capability_hints or "None",
        )

        client = ollama.AsyncClient(host=settings.ollama_base_url)
        response = await client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": 400, "num_ctx": 3072},
        )
        raw = response["response"].strip()

        return self._parse_thought(raw, context)

    def _parse_thought(self, raw: str, context: AgentContext) -> AgentThought:
        """Parse LLM JSON output. Robust to common small-model formatting errors."""
        # Strip markdown fences
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()

        # Find first valid JSON object
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"Planner non-JSON output: {raw[:200]}")
            # Fallback: use web_search on the original task
            return AgentThought(
                action="web_search",
                args={"query": context.task[:100]},
                reasoning="Fallback: planner output was not valid JSON",
                confidence=0.4,
                raw_response=raw,
            )

        try:
            data = json.loads(match.group())
            action = data.get("action", "web_search")
            args = data.get("args", {})

            # Validate action exists
            if action not in self.tools.tool_names:
                logger.warning(f"Unknown action from planner: {action}")
                action = "web_search"
                args = {"query": context.task[:100]}

            return AgentThought(
                action=action,
                args=args,
                reasoning=data.get("reasoning", "")[:500],
                confidence=float(data.get("confidence", 0.7)),
                raw_response=raw,
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Planner parse error: {e} | raw: {raw[:300]}")
            return AgentThought(
                action="web_search",
                args={"query": context.task[:100]},
                reasoning=f"Parse error fallback: {str(e)}",
                confidence=0.3,
                raw_response=raw,
            )

    async def cross_evaluate_step(
        self,
        task: str,
        action: str,
        reasoning: str,
        result: str,
    ) -> dict:
        """Evaluate a step using a DIFFERENT model from the one that generated it."""
        # Use fast_model (llama3.2) to evaluate smart_model (phi4-mini) output
        eval_model = settings.fast_model if self.model == settings.smart_model else settings.smart_model

        prompt = EVALUATOR_PROMPT.format(
            task=task, action=action,
            reasoning=reasoning[:300], result=result[:500],
        )
        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=eval_model,
            prompt=prompt,
            options={"temperature": 0.0, "num_predict": 150},
        )
        raw = resp["response"].strip()
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"relevance": 0.5, "efficiency": 0.5, "quality": 0.5, "overall": 0.5, "note": "eval failed"}
