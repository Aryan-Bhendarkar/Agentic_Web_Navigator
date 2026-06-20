import asyncio
import logging
from pathlib import Path
import config.logger
from agent.executor import agent_app

logger = logging.getLogger("TestAgent")

# HTML page with Name and Description fields, plus a submit alert
AGENT_TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Agent Autonomous Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #fafafa;
        }
        .container {
            max-width: 500px;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 10px 15px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Autonomous Form</h2>
        <form onsubmit="event.preventDefault(); alert('Success!');">
            <div class="form-group">
                <label for="usr-name">Name</label>
                <input type="text" id="usr-name" placeholder="Name placeholder">
            </div>
            <div class="form-group">
                <label for="usr-desc">Description</label>
                <textarea id="usr-desc" rows="4" placeholder="Description placeholder"></textarea>
            </div>
            <button type="submit" id="submit-btn">Submit Form</button>
        </form>
    </div>
</body>
</html>
"""

async def main():
    # 1. Create local test form
    temp_form_path = Path("scratch/test_agent_bench.html").resolve()
    temp_form_path.parent.mkdir(parents=True, exist_ok=True)
    temp_form_path.write_text(AGENT_TEST_HTML, encoding="utf-8")

    file_url = f"file:///{str(temp_form_path).replace('\\', '/')}"

    # 2. Define initial state mapping
    initial_state = {
        "objective": (
            f"Open the browser, navigate to '{file_url}', find the 'Name' and 'Description' fields, "
            f"fill Name with 'LangGraph Autonomous Agent' and Description with 'I am powered by LangGraph!', "
            f"click the Submit button to submit the form, and finish."
        ),
        "history": [],
        "current_url": None,
        "screenshot_path": None,
        "next_tool": None,
        "next_tool_args": None,
        "attempts": 0,
        "status": "running"
    }

    logger.info("Starting autonomous LangGraph execution loop...")

    try:
        # 3. Invoke the compiled LangGraph workflow app
        final_state = await agent_app.ainvoke(initial_state)

        # 4. Review the results
        logger.info(f"Execution finished with status: {final_state['status']}")
        logger.info(f"Total steps taken: {final_state['attempts']}")
        logger.info("Steps history executed:")
        for idx, step in enumerate(final_state["history"], 1):
            logger.info(f"Step {idx}: tool={step.tool}, args={step.args} -> {step.observation}")

    except Exception as e:
        logger.error(f"Agent test run failed: {e}", exc_info=True)
    finally:
        # Clean up local form
        if temp_form_path.exists():
            temp_form_path.unlink()

if __name__ == "__main__":
    asyncio.run(main())
