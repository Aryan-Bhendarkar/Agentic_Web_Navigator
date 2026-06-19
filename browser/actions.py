import logging
from typing import Optional, Dict
from browser.controller import BrowserController

logger = logging.getLogger(__name__)

# Implement interaction actions includig clicking, typing, double-clicking, scrolling, and key presses.
class BrowserActions:
    
    def __init__(self, controller: BrowserController) -> None:
        self.controller = controller

    @property
    # Helper property to access the active page object dynamically
    def page(self):
        if not self.controller or not self.controller.page:
            raise RuntimeError("Active page is not available. Ensure BrowserController has been started.")

        return self.controller.page


    # Clicks an element matched by a selector.Waits for the element to be visible and enabled.
    async def click_element(self, selector: str, timeout: Optional[int] = None) -> None:
        logger.info(f"Clicking element with selector: '{selector}'")

        try:
            await self.page.click(selector, timeout=timeout)
        
        except Exception as e:
            logger.error(f"Failed to click element '{selector}': {e}", exc_info=True)
            raise


    # Performs a mouse click at specific viewport coordinates (x, y).
    async def click_coordinates(self, x:int, y:int) -> None:
        logger.info(f"Clicking viewport coordinates: ({x}, {y})")
       
        try:
            await self.page.mouse.click(x, y)
        
        except Exception as e:
            logger.error(f"Failed to click coordinates ({x}, {y}): {e}", exc_info=True)
            raise


    # Performs a double-click action on an element matched by a selector
    async def double_click_element(self, selector: str, timeout: Optional[int] = None) -> None:
        logger.info(f"Double-clicking element with selector: '{selector}'")

        try:
            await self.page.dblclick(selector, timeout=timeout)

        except Exception as e:
            logger.error(f"Failed to double-click element '{selector}': {e}", exc_info=True)
            raise

    # Performs a mouse double-click at specific viewport coordinates (x, y).
    async def double_click_coordinates(self, x: int, y: int) -> None:
        logger.info(f"Double-clicking viewport coordinates: ({x}, {y})")
        
        try:
            await self.page.mouse.dblclick(x, y)

        except Exception as e:
            logger.error(f"Failed to double-click coordinates ({x}, {y}): {e}", exc_info=True)
            raise


    # Fills a text field matched by a selector with the given text value.
    async def type_text(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        logger.info(f"Typing text into element '{selector}' (length: {len(text)})")
        
        try:
            await self.page.fill(selector, text, timeout=timeout)

        except Exception as e:
            logger.error(f"Failed to type text into element '{selector}': {e}", exc_info=True)
            raise

    # Simulates pressing a specific keyboard key (e.g., 'Enter', 'Tab', 'ArrowDown').
    async def send_keys(self, key:str) -> None:
        logger.info(f"Pressing keyboard key: '{key}'")
        
        try:
            await self.page.keyboard.press(key)

        except Exception as e:
            logger.error(f"Failed to press key '{key}': {e}", exc_info=True)
            raise


    # Scrolls the page in the specified direction ('up' or 'down'). If amount is not specified, scrolls by the height of the viewport.
    async def scroll(self, direction: str = "down", amount: Optional[int] = None) -> None:
        logger.info(f"Scrolling page: direction='{direction}', amount={amount if amount is not None else 'viewport_height'}")

        try:
            scroll_amount = amount if amount is not None else "window.innerHeight"
            if direction.lower() == "down":
                script = f"window.scrollBy(0, {scroll_amount});"
            elif direction.lower() == "up":
                script = f"window.scrollBy(0, -{scroll_amount});"
            else:
                raise ValueError(f"Invalid scroll direction: '{direction}'. Must be 'up' or 'down'.")

            await self.page.evaluate(script)

        except Exception as e:
            logger.error(f"Failed to scroll page {direction}: {e}", exc_info=True)
            raise

    
    # Fills multiple fields at once, where field_data is a dictionary
    async def fill_form_fields(self, field_data: Dict[str, str], timeout: Optional[int] = None) -> None:
        logger.info(f"Filling multiple form fields: {list(field_data.keys())}")
        
        for selector, value in field_data.items():
            await self.type_text(selector, value, timeout=timeout)
        