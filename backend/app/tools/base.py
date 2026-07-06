# =====================================================================
# FILE: backend/app/tools/base.py
# DESCRIPTION: Base classes for the Unified Tool Registry.
# =====================================================================

from typing import Dict, Any, Type, Optional
from pydantic import BaseModel

class BaseTool:
    """
    Interface that all tools in the registry must implement.
    """
    name: str
    description: str
    args_schema: Optional[Type[BaseModel]] = None

    def run(self, *args, **kwargs) -> Any:
        """Execute the tool synchronously."""
        raise NotImplementedError("Tool does not support synchronous execution.")

    async def arun(self, *args, **kwargs) -> Any:
        """Execute the tool asynchronously."""
        # Fallback to run if arun is not overridden
        try:
            return self.run(*args, **kwargs)
        except NotImplementedError:
            raise NotImplementedError("Tool does not support asynchronous or synchronous execution.")
