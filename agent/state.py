from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Logs the execution of a tool in the agent history.
class ToolExecution(BaseModel):
    tool: str = Field(description = "The name of tool called")
    args: Dict[str, Any] = Field(description = "Argument passed to the tool")
    observation: str= Field(description = "The outcome returned by the tool")

# Defines the state structure flowing through the LangGraph agent loop. Represents the agent's short-term memory and workspace.
class AgentState(TypedDict):
    
    # The user's main objective
    objective: str

    # History of steps executed
    history: List[ToolExecution]

    # Active browser state
    current_url : Optional[str]
    screenshot_path: Optional[str]

    # Decided action details (filled by Planner)
    next_tool: Optional[str]
    next_tool_args: Optional[Dict[str, Any]]

    # The planner's reasoning thought for the current step
    thought: Optional[str]

    # Safety iteration tracker
    attempts: int

    # Status tracking: running, success, failed
    status: str
