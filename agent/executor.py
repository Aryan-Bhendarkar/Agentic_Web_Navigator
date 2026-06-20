import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from agent.state import AgentState, ToolExecution
from agent.planner import AgentPlanner
from tools.browser_tools import (
    open_browser,
    close_browser,
    navigate_to_url,
    take_screenshot,
    click_on_screen,
    click_element,
    double_click,
    double_click_coordinates,
    send_keys,
    fill_field,
    scroll,
    find_element,
    get_browser_resources
)

logger = logging.getLogger(__name__)


TOOL_MAP = {
    "open_browser": open_browser,
    "close_browser": close_browser,
    "navigate_to_url": navigate_to_url,
    "take_screenshot": take_screenshot,
    "click_on_screen": click_on_screen,
    "click_element": click_element,
    "double_click": double_click,
    "double_click_coordinates": double_click_coordinates,
    "send_keys": send_keys,
    "fill_field": fill_field,
    "scroll": scroll,
    "find_element": find_element
}

planner = AgentPlanner()

# Graph node that runs the planner to decide the next step. Implements a safety limit of 15 attempts.
async def planner_node(state: AgentState) -> Dict[str, Any]:
    if state["attempts"] >= 15:
        logger.warning("Max execution steps reached (15). Halting agent.")
        return {"status": "failed", "next_tool": "finish"}

    plan_result = await planner.plan(state)
    return plan_result

# Graph node that executes the decided tool, records the observation, takes a screenshot, and increments attempts.
async def action_node(state: AgentState) -> Dict[str, Any]:

    tool_name = state["next_tool"]
    tool_args = state["next_tool_args"] or {}
    history = state["history"] or []
    attempts = state["attempts"]

    if not tool_name or tool_name == "finish":
        return {"attempts": attempts + 1}

    logger.info(f"Executing tool '{tool_name}' with args {tool_args}...")

    if tool_name not in TOOL_MAP:
        observation = f"Error: Tool '{tool_name}' is not a registered browser tool."

    else:
        try:
            observation = await TOOL_MAP[tool_name].ainvoke(tool_args)
        except Exception as e:
            observation = f"Error executing tool: {str(e)}"
        
    logger.info(f"Tool observation: '{observation}'")

    step = ToolExecution(tool=tool_name, args=tool_args, observation=observation)
    updated_history = list(history) + [step]

    current_url = state.get("current_url")
    screenshot_path = state.get("screenshot_path")
    
    controller, _, _ = get_browser_resources()

    if controller and controller.page:
        try:
            current_url = controller.page.url
            # Auto-take screen captures to document progress
            scr_path = await controller.take_screenshot(f"step_{attempts + 1}")
            screenshot_path = str(scr_path)
        except Exception:
            pass  # Browser might not be loaded yet

    return {
        "history": updated_history,
        "current_url": current_url,
        "screenshot_path": screenshot_path,
        "attempts": attempts + 1,
        "next_tool": None,
        "next_tool_args": None
    }


# Routing function to determine if the graph should loop or end.
def should_continue(state: AgentState) -> str:
    if state["status"] in ["success", "failed"]:
        return "end"
    return "continue"


workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("action", action_node)

workflow.add_edge(START, "planner")

workflow.add_conditional_edges(
    "planner",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)

workflow.add_edge("action", "planner")

agent_app = workflow.compile()


