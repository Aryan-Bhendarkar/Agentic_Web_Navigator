# CortexWeb: Autonomous Web Navigation Agent

## What We Have Built
CortexWeb is a smart, autonomous AI agent that can browse the internet for you. You give it a high-level objective (like "Search for the latest news on AI" or "Fill out a contact form"), and it will independently open a web browser, read the page, click buttons, type text, and navigate through websites to achieve your goal. 

To make it easy to follow along, we built a live web dashboard. This allows you to watch the AI's "thoughts" as it plans its next move, view detailed activity logs, and see live screenshots of exactly what the AI is looking at in the browser in real-time.

---

## How It Works (The System Flow)
We designed the system to think and act like a human browsing the web. Here is the step-by-step flow in simple language:

1. **The Request**: You enter your desired goal into the web dashboard.
2. **The Planner (The Brain)**: The AI looks at the current state of the webpage and its memory of past actions. It thinks about what to do next and decides on a specific tool to use (e.g., "I need to click the 'Login' button" or "I should type 'OpenAI' into the search bar").
3. **The Executor (The Hands)**: The system takes the AI's planned action and physically performs it in a real Chromium browser in the background.
4. **The Resilient Eyes (Vision Fallback)**: Modern websites can be tricky. If the AI struggles to find a button using the website's underlying code, CortexWeb doesn't give up. It takes a screenshot of the page, uses AI computer vision to find the exact visual coordinates of the button on the screen, and physically moves the mouse to click it.
5. **The Feedback Loop**: After taking an action, the agent captures a new screenshot of the updated webpage and sends it back to the Planner. This cycle repeats until the agent determines that your objective has been successfully completed.

---

## What We Have Used (Tech Stack)
* **Large Language Model (LLM)**: **Google Gemini 2.5 Flash** (via OpenRouter) acts as both the reasoning brain and the visual eyes of the agent.
* **Orchestration**: **LangGraph** manages the continuous thinking loop, keeping track of the agent's short-term memory and state flow.
* **Browser Automation**: **Playwright** (Python API) handles the actual web browsing, element detection, and simulated user interactions.
* **Backend Server**: **FastAPI** provides a robust, fast backend server. It uses a multithreaded architecture to ensure the web server and the browser automation run smoothly alongside each other, especially on Windows.
* **Live Updates**: **Server-Sent Events (SSE)** instantly stream the AI's thoughts, logs, and live viewport screenshots directly to your screen without needing to refresh.
* **Frontend Dashboard**: Built with **HTML5 and Vanilla CSS3**, featuring a modern, responsive, and interactive design.
## Key Engineering Highlights
This project was built to tackle the inherent unreliability of standard web automation, showcasing advanced problem-solving:

* **Multithreaded Event Loop Isolation**: Solved complex asyncio loop conflicts on Windows. The FastAPI server runs on a separate thread from the Playwright browser automation. They communicate seamlessly via thread-safe queues and Server-Sent Events (SSE).
* **4-Level Resilient Element Detection**: Modern UI frameworks hide elements behind shadow DOMs, dynamic classes, and complex `div` structures. CortexWeb's `ElementDetector` solves this with a robust fallback pipeline:
  1. **Standard Input & Placeholder Search**: First checks for standard text inputs using `get_by_label` and `get_by_placeholder`.
  2. **Semantic Role Mapping**: If not a standard input, it checks for accessibility roles like `button`, `link`, or `checkbox` matching the description.
  3. **Direct Selector Query**: Evaluates the requested name to see if it's a valid CSS attribute or XPath selector and attempts to locate it directly in the DOM.
  4. **Multimodal Vision Fallback**: If all DOM methods fail, it takes a temporary screenshot and sends it to the `ScreenshotAnalyzer`. The Gemini Vision model locates the exact visual `(x, y)` coordinates of the element on the screen, allowing Playwright to perform a raw physical mouse click.
* **Self-Correcting LLM Loop**: LLMs occasionally return broken JSON. The LangGraph planner is built with a resilient retry loop. If the output fails validation, the error is caught and fed back to the LLM so it can fix its own syntax error without crashing the application.

---

## Project Structure & Architecture
Here is a breakdown of the codebase and what each file is responsible for:

```text
CortexWeb/
├── app.py                      # Web server entry point (FastAPI + Agent worker thread)
├── main.py                     # CLI entry point (Run without dashboard)
├── agent/                      # The "Brain" (Decision making & state)
│   ├── planner.py              # LLM integration & auto-correcting decision loop
│   ├── executor.py             # Executes planned actions
│   ├── memory.py               # Short-term action & thought history
│   └── state.py                # LangGraph state schema definition
├── browser/                    # The "Hands" (Web interaction)
│   ├── controller.py           # Playwright browser lifecycle management
│   ├── actions.py              # Physical web actions (click, type, scroll)
│   └── element_detector.py     # 4-layer robust element targeting (CSS/XPath/Vision)
├── vision/                     # The "Eyes" (Visual fallback)
│   └── screenshot_analyzer.py  # Calculates (x, y) from screenshots for visual clicks
├── tools/                      
│   └── browser_tools.py        # Exposes browser actions to the LLM as tools
└── static/                     # Frontend UI
    └── index.html              # Live dashboard interface
```
