import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
from browser.controller import BrowserController
from browser.actions import BrowserActions
from browser.element_detector import ElementDetector
from config.settings import settings

# Sample HTML for checking browser controller, actions, and detector behaviors
TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Pytest Target</title>
</head>
<body>
    <label for="username">User Name</label>
    <input type="text" id="username" placeholder="Write username">
    <div id="double-click-me" ondblclick="this.innerText='Success'">Double Click</div>
    <div style="height: 1000px;">Scrolling space</div>
    <div id="bottom-marker">Bottom</div>
</body>
</html>
"""

@pytest.fixture(scope="session")
def temp_html_file():
    """Session fixture that creates a temporary test HTML file."""
    path = Path("scratch/pytest_bench.html").resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEST_HTML, encoding="utf-8")
    yield path
    if path.exists():
        path.unlink()

@pytest_asyncio.fixture
async def browser_controller():
    """Fixture that manages BrowserController launch and cleanup for each test."""
    controller = BrowserController()
    await controller.start()
    yield controller
    await controller.close()

@pytest.mark.asyncio
async def test_browser_lifecycle(browser_controller):
    """Verifies that the browser launches, page context is open, and settings load."""
    assert browser_controller.page is not None
    assert browser_controller.browser is not None
    assert browser_controller.context is not None

@pytest.mark.asyncio
async def test_browser_navigation_and_screenshot(browser_controller, temp_html_file):
    """Verifies page navigation and screen capturing."""
    file_url = f"file:///{str(temp_html_file).replace('\\', '/')}"
    await browser_controller.navigate(file_url)
    
    assert "pytest_bench.html" in browser_controller.page.url
    
    # Assert screenshot saves correctly
    screenshot_path = await browser_controller.take_screenshot("pytest_capture")
    assert screenshot_path.exists()
    assert screenshot_path.suffix == ".png"
    # Clean up screenshot
    screenshot_path.unlink()

@pytest.mark.asyncio
async def test_element_detector_and_actions(browser_controller, temp_html_file):
    """Verifies element locator strategies, typing text, and double clicking."""
    file_url = f"file:///{str(temp_html_file).replace('\\', '/')}"
    await browser_controller.navigate(file_url)
    
    detector = ElementDetector(browser_controller)
    actions = BrowserActions(browser_controller)

    # 1. Test semantic field detection
    username_input = await detector.find_input_field("User Name")
    assert username_input is not None

    # 2. Test typing interaction
    await actions.type_text("#username", "Tester")
    val = await username_input.input_value()
    assert val == "Tester"

    # 3. Test double click action
    await actions.double_click_element("#double-click-me")
    db_text = await browser_controller.page.locator("#double-click-me").inner_text()
    assert db_text == "Success"

@pytest.mark.asyncio
async def test_scroll_actions(browser_controller, temp_html_file):
    """Verifies page scrolling triggers scroll executions."""
    file_url = f"file:///{str(temp_html_file).replace('\\', '/')}"
    await browser_controller.navigate(file_url)
    
    actions = BrowserActions(browser_controller)
    
    # Retrieve current scroll position
    initial_scroll_y = await browser_controller.page.evaluate("window.scrollY")
    assert initial_scroll_y == 0
    
    # Scroll page down
    await actions.scroll(direction="down", amount=400)
    await asyncio.sleep(0.5)
    
    scrolled_y = await browser_controller.page.evaluate("window.scrollY")
    assert scrolled_y > 0
