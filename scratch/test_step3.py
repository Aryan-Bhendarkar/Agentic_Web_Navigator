
import asyncio
import logging
from pathlib import Path
import config.logger
from browser.controller import BrowserController
from browser.element_detector import ElementDetector

async def run_test():
    # 1. Create a temporary HTML form with Name and Description fields
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Form</title>
    </head>
    <body>
        <h2>Contact Form</h2>
        <form>
            <div>
                <label for="usr_name">Full Name:</label>
                <input type="text" id="usr_name" placeholder="Enter your name">
            </div>
            <div>
                <label for="desc">Brief Description:</label>
                <textarea id="desc" placeholder="Tell us about yourself"></textarea>
            </div>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    
    temp_html_path = Path("scratch/test_form.html").resolve()
    temp_html_path.parent.mkdir(parents=True, exist_ok=True)
    temp_html_path.write_text(html_content, encoding="utf-8")
    
    # 2. Start browser and load the form
    controller = BrowserController()
    detector = ElementDetector(controller)
    logger = logging.getLogger("TestStep3")

    logger.info("Starting verification run for ElementDetector...")

    try:
        await controller.start()
        file_url = f"file:///{str(temp_html_path).replace('\\', '/')}"
        await controller.navigate(file_url)

        # 3. Scan fields
        fields = await detector.scan_fillable_fields()
        logger.info(f"Scanned fields: {fields}")

        # 4. Search elements semantically
        name_input = await detector.find_input_field("Name")
        desc_input = await detector.find_input_field("Description")

        if name_input:
            logger.info("Successfully found 'Name' field!")
        else:
            logger.error("Failed to find 'Name' field.")

        if desc_input:
            logger.info("Successfully found 'Description' field!")
        else:
            logger.error("Failed to find 'Description' field.")

    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
    finally:
        await controller.close()
        # Clean up temp file
        if temp_html_path.exists():
            temp_html_path.unlink()

if __name__ == "__main__":
    asyncio.run(run_test())
