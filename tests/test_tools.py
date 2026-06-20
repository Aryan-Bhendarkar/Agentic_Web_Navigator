import pytest
import asyncio
from pathlib import Path
from browser.controller import BrowserController
# Make sure this import matches your filename (browser_tools if renamed, or tools if not)
from tools.browser_tools import (
    open_browser,
    close_browser,
    navigate_to_url,
    find_element,
    fill_field,
    scroll,
    take_screenshot
)

# Test HTML content
TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tool Testing</title>
</head>
<body>
    <label for="name-input">Full Name</label>
    <input type="text" id="name-input" placeholder="Name placeholder">
    <div style="height: 1000px;">Scroll spacer</div>
    <button id="btn" onclick="alert('clicked')">Submit</button>
</body>
</html>
"""

@pytest.fixture(scope="session")
def temp_html_file():
    """Fixture that builds a session-level temp HTML file."""
    path = Path("scratch/pytest_tools_bench.html").resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEST_HTML, encoding="utf-8")
    yield path
    if path.exists():
        path.unlink()

@pytest.mark.asyncio
async def test_tools_end_to_end_flow(temp_html_file):
    """
    Test that navigates, finds element, fills it, scrolls, and takes screenshot
    using the LangChain tool interface (.ainvoke).
    """
    # 1. Open browser tool
    open_res = await open_browser.ainvoke({})
    assert "Launched Successfully" in open_res or "browser successfully" in open_res.lower()

    try:
        # 2. Navigate tool
        file_url = f"file:///{str(temp_html_file).replace('\\', '/')}"
        nav_res = await navigate_to_url.ainvoke({"url": file_url})
        assert "Successfully navigated to" in nav_res

        # 3. Find element tool
        find_res = await find_element.ainvoke({"label_or_name": "Full Name"})
        assert "Found field matching" in find_res
        assert "#name-input" in find_res

        # 4. Fill field tool
        fill_res = await fill_field.ainvoke({"selector": "#name-input", "text": "AI Tools Tester"})
        assert "Successfully typed text" in fill_res

        # 5. Screenshot tool
        screenshot_res = await take_screenshot.ainvoke({"filename": "pytest_tool_capture"})
        assert "Screenshot successfully saved" in screenshot_res
        
        # Verify screenshot file exists and clean it up
        screenshot_path = Path("screenshots/pytest_tool_capture.png")
        assert screenshot_path.exists()
        screenshot_path.unlink()

        # 6. Scroll tool
        scroll_res = await scroll.ainvoke({"direction": "down", "amount": 200})
        assert "Successfully scrolled page" in scroll_res

    finally:
        # 7. Close browser tool (run always to prevent leaving orphan browser instances)
        close_res = await close_browser.ainvoke({})
        assert "successfully closed" in close_res.lower()
