import base64
import logging
from pathlib import Path
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import settings

logger = logging.getLogger(__name__)

# Pydantic model for structured output validation
class ElementCoordinates(BaseModel):
    x: int = Field(description="The X coordinate of the center of the element, from 0 to 1280")
    y: int = Field(description="The Y coordinate of the center of the element, from 0 to 720")


# Communicates with OpenRouter multimodal models to analyze screenshotsand detect element coordinates visually using LangChain.
class ScreenshotAnalyzer:
    
    def __init__(self) -> None:
        # Instantiate ChatOpenAI pointed to OpenRouter endpoint
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_LLM_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL,
            temperature=0.0
        )
        # Force the LLM to output our validated Pydantic model directly
        self.structured_llm = self.llm.with_structured_output(ElementCoordinates)


    def _encode_image(self, image_path: Path) -> str:
        """Converts an image file on disk into a base64 encoded string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    async def locate_element_visually(self, image_path: Path, element_description: str) -> Optional[Tuple[int, int]]:
        """
        Sends the screenshot to OpenRouter via LangChain and retrieves 
        the visual (x, y) coordinates of the element center.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY is not configured. Skipping vision-based detection.")
            return None

        logger.info(f"Analyzing screenshot visually for: '{element_description}' using LangChain...")

        try:
            base64_image = self._encode_image(image_path)
            
            system_prompt = (
                "You are an expert browser automation assistant. "
                "Identify the approximate center (x, y) coordinates of the requested element "
                "on the 1280x720 screenshot. Return the values in the structured output format."
            )

            user_message = HumanMessage(
                content=[
                    {"type": "text", "text": f"Locate the element: '{element_description}'"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            )

            # LangChain handles payload serialisation and returns a validated ElementCoordinates object
            result: ElementCoordinates = await self.structured_llm.ainvoke([
                SystemMessage(content=system_prompt),
                user_message
            ])

            logger.info(f"LangChain vision detected coordinates: ({result.x}, {result.y})")
            return (result.x, result.y)

        except Exception as e:
            logger.error(f"Failed during LangChain screenshot analysis: {e}", exc_info=True)
            return None
