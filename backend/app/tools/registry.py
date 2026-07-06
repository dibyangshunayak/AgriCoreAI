# =====================================================================
# FILE: backend/app/tools/registry.py
# DESCRIPTION: Unified Tool Registry for AgriCore AI.
# =====================================================================

import logging
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel
from app.tools.base import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Registry for tools available to the Planner Agent.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting already registered tool: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} - {tool.description}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieve a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_tools_metadata(self) -> List[Dict[str, Any]]:
        """Get list of tool schemas for the LLM prompt."""
        metadata = []
        for name, tool in self._tools.items():
            schema = {
                "name": tool.name,
                "description": tool.description,
            }
            if tool.args_schema:
                schema["parameters"] = tool.args_schema.model_json_schema()
            else:
                schema["parameters"] = {}
            metadata.append(schema)
        return metadata

    def run_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool synchronously by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' is not registered.")
        logger.info(f"Running tool synchronously: {name} with args {kwargs}")
        return tool.run(**kwargs)

    async def arun_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool asynchronously by name."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' is not registered.")
        logger.info(f"Running tool asynchronously: {name} with args {kwargs}")
        return await tool.arun(**kwargs)

# Global Tool Registry instance
registry = ToolRegistry()
