from typing import Optional, Type

# from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool

from lib import car_controller
from lib.vision_caption import VisionPositionScheme
from lib.vision_caption import VisionCaptionTool


class VisionControl(BaseTool):
    name = "camera_position_control_tool"
    description = "A tool that allows you to control the camera position and view. You can move the camera in four directions: " \
                  "'up', 'down', 'left', 'right', 'stop'. Any other actions will be forbidden."

    args_schema: Type[VisionPositionScheme] = VisionPositionScheme

    def _run(self, position: str) -> str:
    # def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        fake = True
        vision = VisionCaptionTool()
        if fake:
            success = True
        else:
            success = car_controller.send_car_action(position)

        if success:
            result = "success"
        else:
            result = "failed"
        # vision.run(position)
        return f"The camera have turn {position}: {result}, {vision.run(position)}"


    async def _arun(self) -> str:
        # async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("camera_position_control_tool does not support async")