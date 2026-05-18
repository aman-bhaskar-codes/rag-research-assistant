"""
Agent scratchpad — lets the agent write intermediate notes to itself.
Critical for multi-hop reasoning: agent accumulates findings before synthesizing.
"""
from backend.agent.tools.base import BaseTool, ToolResult


class NotepadTool(BaseTool):
    name = "write_note"
    description = (
        "Write a note to your research scratchpad. Use this to accumulate findings "
        "step-by-step before writing the final answer. "
        "Args: note (str), category (str: finding|hypothesis|evidence|question, default finding)"
    )
    args_schema = {
        "note": {"type": "string", "required": True},
        "category": {"type": "string", "required": False, "default": "finding"},
    }

    def __init__(self):
        self._notes: list[dict] = []

    async def _execute(self, note: str, category: str = "finding") -> ToolResult:
        self._notes.append({"category": category, "note": note})
        return ToolResult(
            success=True,
            output=f"Note saved [{category}]. Total notes: {len(self._notes)}",
            data={"notes_count": len(self._notes), "last_note": note},
        )

    def get_all_notes(self) -> str:
        if not self._notes:
            return "No notes yet."
        sections: dict[str, list[str]] = {}
        for n in self._notes:
            sections.setdefault(n["category"], []).append(n["note"])
        lines = []
        for cat, notes in sections.items():
            lines.append(f"## {cat.upper()}")
            lines.extend(f"- {n}" for n in notes)
        return "\n".join(lines)


class ReadNotepadTool(BaseTool):
    name = "read_notes"
    description = "Read all notes from your research scratchpad. No args needed."
    args_schema = {}

    def __init__(self, notepad: NotepadTool):
        self.notepad = notepad

    async def _execute(self) -> ToolResult:
        content = self.notepad.get_all_notes()
        return ToolResult(success=True, output=content, data={"notes": self.notepad._notes})


class FinishTool(BaseTool):
    name = "finish"
    description = (
        "Signal that you have completed the research task and are ready to write the final answer. "
        "Args: answer (str) — your complete, cited research answer."
    )
    args_schema = {"answer": {"type": "string", "required": True}}

    async def _execute(self, answer: str) -> ToolResult:
        return ToolResult(
            success=True,
            output=answer,
            data={"final_answer": answer},
            metadata={"is_final": True},
        )
