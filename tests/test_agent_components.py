import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from agent.planner import AgentPlanner, AgentAction
from agent.state import AgentState, ToolExecution
from vision.screenshot_analyzer import ScreenshotAnalyzer, ElementCoordinates

@pytest.mark.asyncio
async def test_agent_planner_decision():
    """Verifies that AgentPlanner formulates valid tool decisions using mocked LLM outputs."""
    planner = AgentPlanner()
    
    # Mock structured response
    mock_action = AgentAction(
        thought="I need to open the browser.",
        tool="open_browser",
        args={}
    )
    
    # Replace structured_llm on the plain Python instance to bypass Pydantic patching restrictions
    planner.structured_llm = AsyncMock()
    planner.structured_llm.ainvoke.return_value = mock_action
    
    state = AgentState(
        objective="Search for agentic browser automation tools",
        history=[],
        current_url=None,
        screenshot_path=None,
        attempts=0,
        status="running",
        next_tool=None,
        next_tool_args=None
    )
    
    result = await planner.plan(state)
    
    assert result["next_tool"] == "open_browser"
    assert result["next_tool_args"] == {}
    assert result["status"] == "running"
    planner.structured_llm.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_agent_planner_finish():
    """Verifies that AgentPlanner returns a success state when finishing the run."""
    planner = AgentPlanner()
    
    mock_action = AgentAction(
        thought="The task is complete.",
        tool="finish",
        args={}
    )
    
    planner.structured_llm = AsyncMock()
    planner.structured_llm.ainvoke.return_value = mock_action
    
    state = AgentState(
        objective="Navigate to target URL",
        history=[ToolExecution(tool="open_browser", args={}, observation="Success")],
        current_url="https://google.com",
        screenshot_path="screenshots/step_1.png",
        attempts=1,
        status="running",
        next_tool=None,
        next_tool_args=None
    )
    
    result = await planner.plan(state)
    assert result["next_tool"] == "finish"
    assert result["status"] == "success"
    planner.structured_llm.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_screenshot_analyzer_locate():
    """Verifies coordinate detection conversion and visual element parsing with mocked vision calls."""
    analyzer = ScreenshotAnalyzer()
    
    mock_coords = ElementCoordinates(x=640, y=360)
    mock_image_path = Path("scratch/test_dummy.png")
    
    analyzer.structured_llm = AsyncMock()
    analyzer.structured_llm.ainvoke.return_value = mock_coords
    
    with patch("builtins.open", MagicMock()), \
         patch("base64.b64encode", return_value=b"dGVzdA=="):
         
        coords = await analyzer.locate_element_visually(mock_image_path, "login button")
        
        assert coords == (640, 360)
        analyzer.structured_llm.ainvoke.assert_called_once()
