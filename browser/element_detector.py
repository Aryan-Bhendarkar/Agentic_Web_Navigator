import logging
from typing import Optional, List, Dict, Any
from playwright.async_api import Locator
from browser.controller import BrowserController

logger = logging.getLogger(__name__)

#  Handles locating interactive elements on the page using semantic search, placeholder analysis, and CSS/XPath fallbacks.
class ElementDetector:

    def __init__ (self, controller: BrowserController) -> None:
        self.controller = controller

    @property
    # Helper property to access the active Page object dynamically.
    def page(self):

        if not self.controller or not self.controller.page:
            raise RuntimeError("Active page is not available. Ensure BrowserController has been started.")
            
        return self.controller.page

    # Locates an input or textarea element matching a semantic name 
    async def find_input_field(self, label_or_name: str, timeout: float = 5000) -> Optional[Locator]:
        logger.info(f"Attempting to detect input field for: '{label_or_name}'")

        # Semantic Label Search 
        try:
            locator = self.page.get_by_label(label_or_name, exact=False)
            if await locator.count() > 0:
                first_loc = locator.first
                logger.info(f"Found input field by label matching: '{label_or_name}'")
                return first_loc

        except Exception as e:
             logger.debug(f"Label locator check failed: {e}")


        # Placeholder search 
        try:
            locator = self.page.get_by_placeholder(label_or_name, exact=False)
            if await locator.count() > 0:
                logger.info(f"Found input field by placeholder matching: '{label_or_name}'")
                return locator.first

        except Exception as e:
            logger.debug(f"Placeholder locator check failed: {e}")


        # Direct attribute search using common indicators - case-insensitive CSS selector match
        clean_name = label_or_name.lower().strip()
        selectors = [
            f"input[name*='{clean_name}' i]",
            f"textarea[name*='{clean_name}' i]",
            f"input[id*='{clean_name}' i]",
            f"textarea[id*='{clean_name}' i]",
            f"input[placeholder*='{clean_name}' i]",
            f"textarea[placeholder*='{clean_name}' i]",
        ]

        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                if await locator.count() > 0:
                    logger.info(f"Found input field by attribute selector: '{selector}'")
                    return locator.first

            except Exception as e:
                logger.debug(f"Attribute selector '{selector}' search failed: {e}")

        logger.warning(f"Could not locate any input field matching: '{label_or_name}'")
        return None

    
    #  Scans the page DOM for all fillable input fields and textareas.
    async def scan_fillable_fields(self) -> List[Dict[str, Any]]:
        
        logger.info("Scanning DOM for all fillable elements...")
        fillable_elements = []

        try:
            locators = self.page.locator("input:not([type='submit']):not([type='button']):not([type='hidden']), textarea")
            count = await locators.count()

            for i in range(count):
                loc = locators.nth(i)
                
                # Verify element visibility
                if not await loc.is_visible():
                    continue
                # Retrieve attributes to describe the element
                el_id = await loc.get_attribute("id") or ""
                el_name = await loc.get_attribute("name") or ""
                el_type = await loc.evaluate("el => el.tagName.toLowerCase()")
                placeholder = await loc.get_attribute("placeholder") or ""

                # Attempt to retrieve associated label text
                label_text = ""

                if el_id:
                    label_element = self.page.locator(f"label[for='{el_id}']")
                    
                    if await label_element.count() > 0:
                        label_text = await label_element.first.inner_text()

                fillable_elements.append({
                    "index": i,
                    "type": el_type,
                    "id": el_id,
                    "name": el_name,
                    "placeholder": placeholder,
                    "label": label_text.strip(),
                })

        except Exception as e:
            logger.error(f"Error occurred during form scan: {e}", exc_info=True)
        
        logger.info(f"Found {len(fillable_elements)} visible fillable elements on the page.")
        return fillable_elements