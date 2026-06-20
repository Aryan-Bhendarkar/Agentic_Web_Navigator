import asyncio
import sys
import threading
import queue
from playwright.async_api import async_playwright

def run_playwright_in_thread(q):
    # Create new Proactor event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def run():
        try:
            print("Thread loop started. Launching Playwright...")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://example.com")
                title = await page.title()
                await browser.close()
                q.put(("SUCCESS", title))
        except Exception as e:
            q.put(("ERROR", str(e)))
            
    loop.run_until_complete(run())
    loop.close()

async def main():
    # Force SelectorEventLoop in main thread to simulate uvicorn reload
    if sys.platform == 'win32':
        main_loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(main_loop)
    
    print("Main thread running on:", asyncio.get_event_loop().__class__.__name__)
    
    q = queue.Queue()
    t = threading.Thread(target=run_playwright_in_thread, args=(q,))
    t.start()
    
    # Wait for thread to finish
    while t.is_alive():
        await asyncio.sleep(0.1)
        
    status, result = q.get()
    print(f"Result from thread: status={status}, result={result}")

if __name__ == "__main__":
    # Run main using standard asyncio
    asyncio.run(main())
