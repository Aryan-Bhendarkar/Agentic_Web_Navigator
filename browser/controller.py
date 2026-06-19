import logging 
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from config.settings import settings

logger = logging.getLogger(__name__)


# Manages the lifecycle of a Playwright browser session. Provides methods to start/stop the browser, navigate URLs, and take screenshots of the active page
class BrowserController:

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None


    # Launch playwright, open chrome 
    async def start(self) -> None:
        if self.playwright:
            logger.warning("BrowserController session is already active")
            return 

        logger.info("Initializing Playwright browser context...")
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless = settings.BROWSER_HEADLESS, timeout = settings.BROWSER_TIMEOUT)

            # Create Browser Context 
            self.context = await self.browser.new_context(
                viewport = {"width": 1280, "height": 720},
                device_scale_factor = 1.0
            )

            self.page = await self.context.new_page()

            logger.info("Playwright browser context launched successfully.")

        except Exception as e:
            logger.error(f"Failed to launch browser: {e}", exc_info=True)
            await self.close()
            raise   

    
    # Navigate active page to given url 
    async def navigate(self, url:str) -> None:

        if not self.page:
            raise RuntimeError("Browser session not initialized. Call start() before navigate().")

        logger.info(f"Navigating page to: {url}")

        try:
            await self.page.goto(url, timeout=settings.BROWSER_TIMEOUT, wait_until="networkidle")
            logger.info(f"Successfully navigated to page. Current URL: {self.page.url}")
        
        except Exception as e:
            logger.error(f"Navigation to {url} failed: {e}", exc_info=True)
            raise

    
    # Take screenshot of active browser viewport and save inside screenshot directory 
    async def take_screenshot(self, filename:Optional[str] = None) -> Path:
        if not self.page:
            raise RuntimeError("Browser page not initialized. Cannot take screenshot.")

        screenshots_dir = settings.get_absolute_screenshots_dir()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        elif not filename.endswith(".png"):
            filename = f"{filename}.png"
        
        screenshot_path = screenshots_dir / filename
        logger.info(f"Capturing screenshot to: {screenshot_path}")

        
        try:
            await self.page.screenshot(path=str(screenshot_path))
            logger.info("Screenshot successfully captured and saved.")
            return screenshot_path

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}", exc_info=True)
            raise

    # Safely disposes of the active page, context, browser, and Playwright instances.
    async def close(self) -> None:
        logger.info("Closing the browser resourse")

        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

        except Exception as e:
            logger.warning(f"Error encountered while closing browser handles: {e}")

        finally:
            self.page = None
            self.context = None
            self.browser = None


        try:
            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.warning(f"Error encountered while stopping Playwright driver: {e}")
        
        finally:
            self.playwright = None
            logger.info("Browser session shutdown complete.")