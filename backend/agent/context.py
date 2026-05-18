"""Agent execution context — everything the agent knows and has done."""
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentThought:
    """The LLM's decision at a single step."""
    action: str
    args: dict
    reasoning: str
    confidence: float = 0.8
    raw_response: str = ""


@dataclass
class StepRecord:
    step_num: int
    thought: AgentThought
    result_output: str
    result_data: Any
    success: bool
    latency_ms: float
    token_count: int = 0


@dataclass
class AgentContext:
    task: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: list[StepRecord] = field(default_factory=list)
    focus_mode: str = "research"
    model_override: str | None = None

    def add_step(self, step: StepRecord):
        self.steps.append(step)

    def to_prompt_history(self, max_steps: int = 6) -> str:
        """Render recent steps as text for the LLM context window."""
        if not self.steps:
            return "No steps taken yet."
        recent = self.steps[-max_steps:]
        lines = []
        for s in recent:
            lines.append(
                f"Step {s.step_num}: [{s.thought.action}] {s.thought.reasoning[:200]}\n"
                f"Result: {s.result_output[:300]}\n"
                f"{'✓ Success' if s.success else '✗ Failed'}"
            )
        return "\n\n".join(lines)

    @property
    def last_result(self) -> str:
        return self.steps[-1].result_output if self.steps else ""

    @property
    def is_finished(self) -> bool:
        return bool(self.steps) and self.steps[-1].thought.action == "finish"


@dataclass
class AgentResult:
    context: AgentContext
    final_answer: str
    total_steps: int
    success: bool
    quality_score: float = 0.0
    failure_pattern: str | None = None
