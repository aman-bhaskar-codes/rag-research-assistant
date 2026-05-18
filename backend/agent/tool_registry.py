"""
Central tool registry. Manages tool lookup, execution, and schema validation.
Each AgentRunner gets its own registry instance (some tools are stateful).
"""
import json
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.tools.base import BaseTool, ToolResult
from backend.agent.tools.rag_tool import RAGSearchTool
from backend.agent.tools.web_search_tool import WebSearchTool
from backend.agent.tools.arxiv_tool import ArxivTool
from backend.agent.tools.wikipedia_tool import WikipediaTool
from backend.agent.tools.semantic_scholar_tool import SemanticScholarTool
from backend.agent.tools.notepad_tool import NotepadTool, ReadNotepadTool, FinishTool


class ToolRegistry:
    def __init__(self, db_session: AsyncSession):
        notepad = NotepadTool()
        self._tools: dict[str, BaseTool] = {
            "search_knowledge_base": RAGSearchTool(db_session),
            "web_search": WebSearchTool(),
            "arxiv_search": ArxivTool(),
            "wikipedia_search": WikipediaTool(),
            "semantic_scholar_search": SemanticScholarTool(),
            "write_note": notepad,
            "read_notes": ReadNotepadTool(notepad),
            "finish": FinishTool(),
        }

    def get_schemas_for_prompt(self) -> str:
        """Returns tool descriptions formatted for the LLM system prompt."""
        lines = []
        for name, tool in self._tools.items():
            schema_str = json.dumps(tool.args_schema, indent=2)
            lines.append(f"Tool: {name}\nDescription: {tool.description}\nArgs: {schema_str}")
        return "\n\n".join(lines)

    async def execute(self, tool_name: str, args: dict) -> ToolResult:
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=f"Unknown tool: '{tool_name}'. Available: {list(self._tools.keys())}",
                error="ToolNotFound",
            )
        logger.debug(f"Executing tool: {tool_name} | args: {args}")
        result = await tool.run(**args)
        return result.truncate(max_chars=2000)  # protect small model context

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
