import logging
from typing import Optional
from langchain_core.tools import tool
from browser.controller import BrowserController
from browser.actions import BrowserActions
from browser.element_detector import ElementDetector

logger = logging.getLogger(__name__)

# Global instances to maintain browser session state across tool executions
_controller: Optional[BrowserController] = None
_actions : Optional[BrowserActions] = None
_detector: Optional[ElementDetector] = None


# Singleton getter to retrieve browser controller, actions, and element detector instances.
def get_browser_resources():
    global _controller, _actions, _detector
    if _controller is None:
        _controller = BrowserController()
        _actions = BrowserActions(_controller)
        _detector = ElementDetector(_controller)

    return _controller, _actions, _detector


# Launches a Chromium browser instance and sets up a default desktop viewport.Call this tool first before trying to navigate or interact.
@tool
async def open_browser() -> str:
    """
    Launches a Chromium browser instance and sets up a default desktop viewport.
    Call this tool first before trying to navigate or interact.
    """

    controller, _, _ = get_browser_resources()
    try:
        await controller.start()
        return "Browser Launched Successfully"
    except Exception as e:
        return f"Failed to launch browser: {str(e)}"



# Closes the current page, browser context, and terminates the Playwright session.
@tool
async def close_browser() -> str:
    """
    Closes the current page, browser context, and terminates the Playwright session.
    """

    controller, _, _ = get_browser_resources()
    try:
        await controller.close()
        return "Browser successfully closed"
    except Exception as e:
        return f"Failed to close browser: {str(e)}"


#  Navigates the browser to the specified URL.
@tool
async def navigate_to_url(url: str) -> str:
    """
    Navigates the browser to the specified URL.
    Input: url (e.g. 'https://www.google.com')
    """

    controller, _, _ = get_browser_resources()
    try:
        await controller.navigate(url)
        return f"Successfully navigated to: {url}"
    except Exception as e:
        return f"Failed to navigate to {url}: {str(e)}"


# Captures a screenshot of the current page viewport.
@tool
async def take_screenshot(filename: Optional[str] = None) -> str:
    """
    Captures a screenshot of the current page viewport.
    Input: Optional filename (saves to screenshots/ folder).
    """
    controller, _, _ = get_browser_resources() 
    try:
        path = await controller.take_screenshot(filename)
        return f"Screenshot successfully saved to: {path}"
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"


# Clicks at the absolute coordinates (x, y) on the screen.
@tool
async def click_on_screen(x:int, y:int) -> str:
    """
    Clicks at the absolute coordinates (x, y) on the screen.
    Use this when element selectors are unavailable or for coordinate clicking.
    """

    _, actions, _ = get_browser_resources()
    try:
        await actions.click_coordinates(x, y)
        return f"Successfully clicked screen coordinates: ({x}, {y})"
    except Exception as e:
        return f"Failed to click coordinates ({x}, {y}): {str(e)}"



@tool
async def click_element(selector: str) -> str:
    """
    Clicks the HTML element matched by the given CSS or XPath selector.
    """
    _, actions, _ = get_browser_resources()
    try:
        await actions.click_element(selector)
        return f"Successfully clicked element: '{selector}'"
    except Exception as e:
        return f"Failed to click element '{selector}': {str(e)}"


@tool
async def double_click(selector: str) -> str:
    """
    Double-clicks the HTML element matched by the given selector.
    """
    _, actions, _ = get_browser_resources()
    try:
        await actions.double_click_element(selector)
        return f"Successfully double-clicked element: '{selector}'"
    except Exception as e:
        return f"Failed to double-click element '{selector}': {str(e)}"


@tool
async def double_click_coordinates(x: int, y: int) -> str:
    """
    Double-clicks at the absolute coordinates (x, y) on the screen.
    """
    _, actions, _ = get_browser_resources()
    try:
        await actions.double_click_coordinates(x, y)
        return f"Successfully double-clicked screen coordinates: ({x}, {y})"
    except Exception as e:
        return f"Failed to double-click coordinates ({x}, {y}): {str(e)}"


@tool
async def send_keys(key: str) -> str:
    """
    Simulates pressing a specific keyboard key (e.g. 'Enter', 'Tab', 'Backspace').
    """
    _, actions, _ = get_browser_resources()
    try:
        await actions.send_keys(key)
        return f"Successfully sent keyboard key press: '{key}'"
    except Exception as e:
        return f"Failed to press key '{key}': {str(e)}"


@tool
async def fill_field(selector: str, text: str) -> str:
    """
    Fills/types text into the field matched by the CSS/XPath selector.
    """
    _, actions, _ = get_browser_resources()
    try:
        await actions.type_text(selector, text)
        return f"Successfully typed text into element: '{selector}'"
    except Exception as e:
        return f"Failed to type text into element '{selector}': {str(e)}"


@tool
async def scroll(direction: str, amount: Optional[int] = None) -> str:
    """
    Scrolls the page. 
    Inputs:
        direction: 'up' or 'down'
        amount: Optional integer pixel amount to scroll (defaults to viewport height)
    """
    _, actions, _ = get_browser_resources()
    try:
        await actions.scroll(direction, amount)
        return f"Successfully scrolled page: direction='{direction}', amount={amount or 'viewport_height'}"
    except Exception as e:
        return f"Failed to scroll page: {str(e)}"

        
@tool
async def find_element(label_or_name: str) -> str:
    """
    Searches semantically for an input/textarea element on the page matching a label or placeholder.
    Returns details of the element if found.
    """
    _, _, detector = get_browser_resources()
    try:
        locator = await detector.find_input_field(label_or_name)
        if locator:
            # Construct a helper description to let the agent know where it is
            el_id = await locator.get_attribute("id") or ""
            el_name = await locator.get_attribute("name") or ""
            
            selector = f"#{el_id}" if el_id else f"[name='{el_name}']" if el_name else "Detected locator"
            return f"Found field matching '{label_or_name}' with selector: '{selector}'"
        else:
            return f"No fillable field found matching '{label_or_name}'"
    except Exception as e:
        return f"Error while trying to detect element matching '{label_or_name}': {str(e)}"