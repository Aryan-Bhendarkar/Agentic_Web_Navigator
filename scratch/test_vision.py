import asyncio
import logging
from pathlib import Path
import config.logger
from browser.controller import BrowserController
from browser.element_detector import ElementDetector
from config.settings import settings

logger = logging.getLogger("TestVision")

# HTML page containing a button with NO text or label attributes (pure visual shape)
VISION_TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Vision Test Area</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 50px;
            background-color: #fafafa;
        }
        .container {
            width: 400px;
            height: 300px;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        /* Pure visual shape with NO text or semantic tags to bypass DOM selectors */
        .visual-button {
            width: 120px;
            height: 45px;
            background-color: #007bff;
            border-radius: 6px;
            margin-top: 50px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Enter Details</h2>
        <input type="text" placeholder="Write username">
        
        <!-- Only a visual blue box. DOM selectors cannot match this to 'blue button' -->
        <div class="visual-button"></div>
    </div>
</body>
</html>
"""

async def run_vision_test():
    # Verify OpenRouter key exists
    if not settings.OPENROUTER_API_KEY or "your_openrouter_api_key_here" in settings.OPENROUTER_API_KEY:
        logger.error("Please add a valid OPENROUTER_API_KEY to your .env file to run the vision test!")
        return

    logger.info("Initializing Vision Fallback test...")

    # Write HTML file
    temp_path = Path("scratch/test_vision_bench.html").resolve()
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(VISION_TEST_HTML, encoding="utf-8")

    controller = BrowserController()
    detector = ElementDetector(controller)

    try:
        await controller.start()
        file_url = f"file:///{str(temp_path).replace('\\', '/')}"
        await controller.navigate(file_url)

        # Let's ask the detector to find the "blue button"
        # Levels 1, 2, and 3 will fail because there is no text or attributes.
        # It should trigger Level 4 vision and ask OpenRouter to locate it on the screenshot.
        result = await detector.detect_element_location("blue button")
        logger.info(f"Final Detection Result: {result}")

    except Exception as e:
        logger.error(f"Vision test failed: {e}", exc_info=True)
    finally:
        await controller.close()
        if temp_path.exists():
            temp_path.unlink()

if __name__ == "__main__":
    asyncio.run(run_vision_test())
