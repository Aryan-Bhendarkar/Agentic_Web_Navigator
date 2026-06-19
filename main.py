import asyncio
import logging 
from pathlib import Path
from config.settings import settings
import config.logger
from browser.controller import BrowserController
from browser.actions import BrowserActions
from browser.element_detector import ElementDetector

logger = logging.getLogger("AgenticWebNavigator")

TEST_HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>CortexWeb Test Bench</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .form-container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 500px;
            margin-bottom: 600px; /* Force scrolling space */
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .double-click-box {
            width: 200px;
            height: 100px;
            background-color: #28a745;
            color: white;
            text-align: center;
            line-height: 100px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            user-select: none;
            margin-top: 40px;
        }
        .double-click-box.active {
            background-color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>CortexWeb Automation Form</h2>
        <form id="test-form" onsubmit="event.preventDefault(); alert('Form Submitted!');">
            <div class="form-group">
                <label for="full-name">Name</label>
                <input type="text" id="full-name" placeholder="Enter your full name">
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" rows="4" placeholder="Enter description details"></textarea>
            </div>
            <!-- Submit Button (will click by coordinates) -->
            <button type="submit" id="submit-btn" style="position: relative;">Submit Form</button>
        </form>
    </div>
    <!-- Scroll target space -->
    <div style="height: 500px; background-color: #e9ecef; margin: 40px 0; padding: 20px; border-radius: 8px;">
        <h3>Scroll Target Area</h3>
        <p>This section is visible only after scrolling down the webpage.</p>
        
        <!-- Double Click Area -->
        <div id="double-click-target" class="double-click-box" 
             ondblclick="this.classList.toggle('active'); this.innerText = this.classList.contains('active') ? 'Double Clicked!' : 'Double Click Me';">
            Double Click Me
        </div>
    </div>
</body>
</html>
"""

async def run_agentic_flow():
    logger.info("Initializing agentic web navigator workflow")

    temp_form_path = Path("scratch/cortexweb_test_bench.html").resolve()
    temp_form_path.parent.mkdir(parents=True, exist_ok=True)
    temp_form_path.write_text(TEST_HTML_CONTENT, encoding="utf-8")


    controller = BrowserController()
    actions = BrowserActions(controller)
    detector = ElementDetector(controller)

    try:
        # Start browser
        await controller.start()
        
        # Navigate to the local form file URL
        file_url = f"file:///{str(temp_form_path).replace('\\', '/')}"
        
        await controller.navigate(file_url)

        # Capture initial screenshot
        await controller.take_screenshot("01_initial_page")

        # Detect inputs semantically
        name_input = await detector.find_input_field("Name")
        desc_input = await detector.find_input_field("Description")

        # Fill form automatically
        if name_input:
            await name_input.fill("Agentic Web Browser")
            logger.info("Successfully filled Name field.")

        if desc_input:
            await desc_input.fill("A modular, high-reliability autonomous web navigator built from scratch.")
            logger.info("Successfully filled Description field.")

        # Take screenshot of filled form
        await controller.take_screenshot("02_filled_form")
        await asyncio.sleep(1)

        # First, retrieve coordinates of the submit button to demonstrate coordinate clicking
        submit_btn = controller.page.locator("#submit-btn")
        box = await submit_btn.bounding_box()
        if box:
            # Click the center of the bounding box
            click_x = int(box["x"] + box["width"] / 2)
            click_y = int(box["y"] + box["height"] / 2)
            logger.info(f"Targeting Submit button bounding box: x={click_x}, y={click_y}")

         # Dismiss the alert automatically so playwright doesn't hang
            controller.page.once("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
            
            await actions.click_coordinates(click_x, click_y)
            await controller.take_screenshot("03_after_submit_click")
        
        else:
            logger.error("Could not determine Submit button bounding box.")

        # Scroll the webpage
        logger.info("Scrolling page down...")
        await actions.scroll(direction="down", amount=500)
        await controller.take_screenshot("04_scrolled_down")
        await asyncio.sleep(1)

        # Perform double click actions
        double_click_target = controller.page.locator("#double-click-target")
        # Scroll the element into view if not fully visible
        await double_click_target.scroll_into_view_if_needed()
        
        logger.info("Performing double click on target element...")
        await actions.double_click_element("#double-click-target")
        await controller.take_screenshot("05_after_double_click")
        await asyncio.sleep(1)

        # Keyboard input simulation
        logger.info("Simulating tab navigation and focus typing...")
        await actions.send_keys("Tab")
        await asyncio.sleep(0.5)

        logger.info("Integration run completed successfully.")

    except Exception as e:
        logger.error(f"Error during CortexWeb workflow: {e}", exc_info=True)

    finally:
        # Tear down resources
        await controller.close()
        # Clean up temp file
        if temp_form_path.exists():
            temp_form_path.unlink()


if __name__ == "__main__":
    asyncio.run(run_agentic_flow())