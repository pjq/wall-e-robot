from typing import Optional, Type

# from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from pydantic import BaseModel, Extra, root_validator
import random
from lib.vision_service import VisionService,vision

class VisionPositionScheme(BaseModel):
    position: str = Field(description="should be the camera or visual position")

class VisionCaptionTool(BaseTool):
    name = "vision_caption_tool"
    description = "useful when you want to check or visual what you see in front of you, " \
                  "it ONLY show the vision in front of you, you can not see the left/right/back position."
    args_schema: Type[VisionPositionScheme] = VisionPositionScheme

    import random

    def _run(self, position: str) -> str:

        """Use the tool."""
        positions = {
            "left": [
                "A man sitting on the left side of the computer and working",
                "A person typing on the left side of the computer",
                "A coder intently typing away at their keyboard from the left side of the computer",
                "A developer working from the left side of the computer, fingers flying across the keyboard"
            ],
            "right": [
                "A man sitting on the right side of the computer and working",
                "A person typing on the right side of the computer",
                "A programmer intently coding from the right side of the computer",
                "A developer working from the right side of the computer, typing away at lightning speed"
            ],
            "front": [
                "A man sitting in front of the computer and working",
                "A person typing in front of the computer",
                "A software developer sitting at the desk, coding in front of the computer screen",
                "An engineer typing away in front of the computer monitor"
            ],
            "back": [
                "A man sitting behind the computer and working",
                "A person typing behind the computer",
                "A coder typing furiously from the back of the computer",
                "A developer coding from the back of the computer, with their head slightly tilted to one side"
            ]
        }

        if vision.sequence_list.__len__() !=0 :
            caption = vision.sequence_list.pop()
            if caption:
                return caption[1]

        if position not in positions:
            # return "Invalid position. Please use left, right, front, or back."
            return random.choice(positions["front"])
        else:
            return random.choice(positions[position])

    async def _arun(self) -> str:
        # async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("vision_caption_tool does not support async")