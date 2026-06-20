import asyncio
import logging
from typing import Dict, Any, List 
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from agent.state import AgentState, ToolExecution

logger = logging.getLogger(__name__)

# The structured decision output returned by the planner LLM.
class AgentAction(BaseModel):
    thought: str = Field(description="Reasoning about the current state, progress made, and why this next step is chosen.")
    tool: str = Field( description="The name of the tool to invoke. Must be one of: "
                    "'open_browser', 'close_browser', 'navigate_to_url', 'take_screenshot', "
                    "'click_on_screen', 'click_element', 'double_click', 'double_click_coordinates', "
                    "'send_keys', 'fill_field', 'scroll', 'find_element', or 'finish'."
                )
    args: Dict[str, Any] = Field(default_factory=dict,
        description="Key-value dictionary of arguments for the chosen tool. Use empty dict {} if no args are needed."
    )


#  Decides the next action for the agent to execute by analyzing the overall objective, previous execution steps, and active browser state.
class AgentPlanner:

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL,
            temperature=0.0,
            max_tokens=1000
        )

        self.structured_llm = self.llm.with_structured_output(AgentAction)


    # Constructs the system guidelines and tool schemas for the LLM.
    def _build_system_prompt(self) -> str:
         return (
            "You are an autonomous browser automation agent\n"
            "Your task is to achieve the user's objective step-by-step using the tools available.\n\n"
            
            "Available tools and their parameters:\n"
            "- open_browser: Parameters: {}\n"
            "  Launches the web browser. Call this tool first.\n"
            "- close_browser: Parameters: {}\n"
            "  Terminates the browser session.\n"
            "- navigate_to_url: Parameters: {'url': string}\n"
            "  Navigates the browser to the specified URL.\n"
            "- take_screenshot: Parameters: {'filename': Optional[string]}\n"
            "  Captures a screenshot of the current page viewport.\n"
            "- click_on_screen: Parameters: {'x': integer, 'y': integer}\n"
            "  Clicks coordinates (x, y) on the screen. Use this when direct selectors fail.\n"
            "- click_element: Parameters: {'selector': string}\n"
            "  Clicks an element matched by CSS/XPath selector.\n"
            "- double_click: Parameters: {'selector': string}\n"
            "  Double-clicks an element matched by selector.\n"
            "- double_click_coordinates: Parameters: {'x': integer, 'y': integer}\n"
            "  Double-clicks coordinates (x, y) on the screen.\n"
            "- send_keys: Parameters: {'key': string}\n"
            "  Simulates pressing a keyboard key (e.g., 'Enter', 'Tab', 'Backspace').\n"
            "- fill_field: Parameters: {'selector': string, 'text': string}\n"
            "  Fills/types text into the input field matched by selector.\n"
            "- scroll: Parameters: {'direction': 'up' or 'down', 'amount': Optional[integer]}\n"
            "  Scrolls the page down or up.\n"
            "- find_element: Parameters: {'label_or_name': string}\n"
            "  Locates an input field, button, or link semantically. "
            "  Returns a CSS selector if found in DOM, or (x, y) coordinates visually.\n"
            "- finish: Parameters: {}\n"
            "  Declare this tool only when the objective is fully completed.\n\n"
            
            "Guidelines:\n"
            "1. Review history of executed actions to avoid repeating failing calls.\n"
            "2. Think step-by-step. Break the objective into concrete interactions.\n"
            "3. If standard element finding/selectors fail, use 'find_element' to locate coordinates visually "
            "   and click using 'click_on_screen'.\n"
            "4. Be concise and precise."
        )

    # Formats the list of previous execution steps into readable text.
    def _format_history(self, history: List[ToolExecution]) -> str:
        if not history:
            return " No actions executed yet"

        formatted = []
        for i,step in enumerate(history, 1):
            formatted.append( 
                f"Step {i}:\n"
                f"  Tool: {step.tool}\n"
                f"  Args: {step.args}\n"
                f"  Observation: {step.observation}"
            )
        return "\n".join(formatted)

    
    # Invokes the LLM to inspect the state and output the next structured action. Updates the next_tool, next_tool_args, and status state fields.
    async def plan(self, state: AgentState) -> Dict[str, Any]:
        
        logger.info(f"Planner reviewing agent state. Current attempts: {state['attempts']}")

        history_text = self._format_history(state["history"])
        system_content = self._build_system_prompt()

        user_content = (
            f"Objective: {state['objective']}\n"
            f"Current URL: {state.get('current_url') or 'N/A'}\n"
            f"Previous Steps:\n{history_text}\n"
        )

        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=user_content)
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                # Call the structured LLM
                action: AgentAction = await self.structured_llm.ainvoke(messages)

                logger.info(f"Planner thought: '{action.thought}'")
                logger.info(f"Planner action: {action.tool}({action.args})")

                if action.tool == "finish":
                    return {
                        "next_tool": "finish",
                        "next_tool_args": {},
                        "status": "success",
                        "thought": action.thought
                    }

                return {
                    "next_tool": action.tool,
                    "next_tool_args": action.args,
                    "status": "running",
                    "thought": action.thought
                }

            except Exception as e:
                last_error = e
                logger.warning(f"Planner LLM attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    # Add a correction hint and retry
                    messages = messages + [
                        HumanMessage(content=(
                            "Your previous response could not be parsed as valid JSON. "
                            "Please respond ONLY with a valid JSON object matching the required schema. "
                            "Ensure all string values are properly quoted and all required fields "
                            "(thought, tool, args) are present."
                        ))
                    ]
                    await asyncio.sleep(1.0)

        logger.error(f"Planner LLM failed after {max_retries} retries: {last_error}", exc_info=True)
        return {
            "next_tool": None,
            "next_tool_args": None,
            "status": "failed",
            "thought": None
        }