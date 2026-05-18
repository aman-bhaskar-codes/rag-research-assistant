"""Base interface all tools implement."""
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    success: bool
    output: str           # human-readable result
    data: Any = None      # structured data if available
    latency_ms: float = 0.0
    token_estimate: int = 0
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    def truncate(self, max_chars: int = 2000) -> "ToolResult":
        """Return copy with output truncated — agents have small context windows."""
        return ToolResult(
            success=self.success,
            output=self.output[:max_chars] + ("…" if len(self.output) > max_chars else ""),
            data=self.data,
            latency_ms=self.latency_ms,
            token_estimate=self.token_estimate,
            error=self.error,
            metadata=self.metadata,
        )


class BaseTool(ABC):
    name: str
    description: str
    args_schema: dict  # JSON schema for args validation

    async def run(self, **kwargs) -> ToolResult:
        t0 = time.perf_counter()
        try:
            result = await self._execute(**kwargs)
            result.latency_ms = (time.perf_counter() - t0) * 1000
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Tool {self.name} failed: {str(e)}",
                error=str(e),
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    @abstractmethod
    async def _execute(self, **kwargs) -> ToolResult:
        pass
