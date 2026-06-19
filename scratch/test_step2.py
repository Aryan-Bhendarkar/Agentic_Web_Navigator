import asyncio
import logging
from config.settings import settings
import config.logger
from browser.controller import BrowserController
from browser.actions import BrowserActions

async def run_verification():
    # Force headless = False so we can see the browser open (if executing locally)
    # settings.BROWSER_HEADLESS = False

    controller = BrowserController()
    actions = BrowserActions(controller)

    logger = logging.getLogger("TestStep2")
    logger.info("Starting verification run for BrowserController & BrowserActions...")

    try:
        # 1. Start browser
        await controller.start()

        # 2. Navigate to Google
        await controller.navigate("https://www.google.com")

        # 3. Take screenshot
        screenshot_path = await controller.take_screenshot("step2_initial")
        logger.info(f"Saved initial screenshot to {screenshot_path}")

        # 4. Perform scrolling
        logger.info("Testing scroll actions...")
        await actions.scroll(direction="down", amount=300)
        await asyncio.sleep(1)
        await actions.scroll(direction="up", amount=300)
        await asyncio.sleep(1)

        # 5. Coordinate Click test (click near top left corner safely as a dummy click)
        logger.info("Testing coordinate click...")
        await actions.click_coordinates(10, 10)

        # 6. Take final screenshot
        final_path = await controller.take_screenshot("step2_final")
        logger.info(f"Saved final screenshot to {final_path}")

    except Exception as e:
        logger.error(f"Verification test failed: {e}", exc_info=True)
    finally:
        # 7. Close controller
        await controller.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
