import logging
from llama_index.core.tools import FunctionTool
from pydantic import BaseModel, Field
from llm_utils import load_and_initialize_llm
from llama_index.core.agent import ReActAgent
import base64
import random
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls
from PIL import Image
from llama_index.core.schema import ImageDocument
import requests
import time
from io import BytesIO
import matplotlib.pyplot as plt
import cv2  # OpenCV for capturing images from the camera
# from lib.vision_service import VisionService
# from lib import edge_tts_playback
from lib.edge_tts_playback import playTTS  # Import the playTTS function
from lib.car_controller import send_car_action  # Import the playTTS function
from lib.vision_service import vision  # Import the playTTS function
import config
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MOCK_TURN_CAR = False
MOCK_CAPTURE_IMAGE = False 
MOCK_DESCRIBE_IMAGES = False

class CarController:
    def __init__(self, use_mock=True):
        self.USE_MOCK = use_mock
        self.llm = load_and_initialize_llm()
        self.voice = config.settings.edge_tts_voice_cn
        self.turn_car_fn = self.mock_turn_car if MOCK_TURN_CAR else self.turn_car
        self.capture_image_fn = self.mock_capture_image if MOCK_CAPTURE_IMAGE else self.capture_image
        self.describe_images_fn = self.mock_describe_images if MOCK_DESCRIBE_IMAGES else self.describe_images
        self.vision = vision 

    def playTTS(self, text: str, voice: str) -> None:
        """Play text-to-speech using the specified voice."""
        try:
            logger.info("Playing TTS for text: %s", text)
            playTTS(text, voice)
        except Exception as e:
            logger.error("Failed to play TTS: %s", e)

    def turn_car(self, direction: str, duration: int) -> str:
        """Turn the car in the specified direction for a given duration."""
        if direction not in ["left", "right", "up", "down"]:
            logger.error("Invalid direction: %s", direction)
            return "Invalid direction. Please specify 'left', 'right', 'up', or 'down'."
        logger.info("Turning car %s for %d seconds", direction, duration)
        result=send_car_action(direction)
        return f"Car turned {direction} for {duration} seconds. Result: {'Success' if result else 'Failure'}"

    def mock_turn_car(self, direction: str, duration: int) -> str:
        """Mock turn the car in the specified direction for a given duration."""
        logger.info("Mock: Turning car %s for %d seconds", direction, duration)
        return f"Mock: Car would turn {direction} for {duration} seconds."

    def capture_image(self) -> str:
        """Capture an image from the car's camera."""
        cap = cv2.VideoCapture(0)  # Assuming the camera is at index 0
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            logger.error("Failed to open camera")
            return "Failed to open camera"
        
        time.sleep(3)
        
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to read frame from camera")
            cap.release()
            return "Failed to read frame from camera"
        
        if frame is None or frame.size == 0:
            logger.error("Captured frame is empty")
            cap.release()
            return "Captured frame is empty"
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_path = "captured_image.jpg"
        cv2.imwrite(image_path, frame_rgb)
        cap.release()
        return image_path

    def mock_capture_image(self) -> str:
        """Mock capture an image from the car's camera."""
        logger.info("Mock: Capturing image from camera")
        return "captured_image.jpg"

    def describe_images(self, image_path):
        """Describe images using the multi-modal LLM."""
        image_document = ImageDocument(image_path=image_path)
        try:
            response = self.llm.complete(
                prompt="Describe the images as an alternative text",
                image_documents=[image_document],
            )
        except Exception as e:
            logger.error("Failed to complete LLM request: %s", str(e))
            response = "Error: Unable to describe images."
        return response

    def mock_describe_images(self, image_path):
        """Mock describe images."""
        logger.info("Mock: Describing images")
        scenes = [
            "A sunny beach with palm trees",
            "A bustling cityscape at night",
            "A serene mountain landscape",
            "A dense forest with a flowing river",
            "A quiet village covered in snow",
            "A vibrant desert with sand dunes",
            "A peaceful countryside with rolling hills",
            "A futuristic city with flying cars",
            "A historical castle on a hill",
            "A tropical island with crystal clear water"
        ]
        return f"Mock description of the images: {random.choice(scenes)}."

    def display_image(self, image_path):
        """Display an image using matplotlib."""
        img = Image.open(image_path)
        plt.imshow(img)
        plt.show()

    def car_init(self):
        turn_car_tool = FunctionTool.from_defaults(
            self.turn_car_fn,
            name="TurnCarTool",
            description="A tool to turn the car in specified direction for a given duration."
        )

        capture_image_tool = FunctionTool.from_defaults(
            self.capture_image_fn,
            name="CaptureImageTool",
            description="A tool to capture an image from the car's camera."
        )

        describe_image_tool = FunctionTool.from_defaults(
            self.describe_images_fn,
            name="DescribeImageTool",
            description="A tool to describe images captured by the car's camera."
        )
        tools = [turn_car_tool, capture_image_tool, describe_image_tool]

        chat_store = SimpleChatStore()
        chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=chat_store,
            chat_store_key="user1",
        )

        agent = ReActAgent.from_tools(tools, llm=self.llm, memory=chat_memory, verbose=True)
        return agent


    def save_chat_store(self):
        """Save the chat store to disk."""
        self.chat_store.persist(persist_path="chat_store.json")
        print("Chat history saved.")

    def load_chat_store(self):
        """Load the chat store from disk."""
        try:
            self.chat_store = SimpleChatStore.from_persist_path(persist_path="chat_store.json")
            self.chat_memory = ChatMemoryBuffer.from_defaults(
                token_limit=3000,
                chat_store=self.chat_store,
                chat_store_key="user1",
            )
            print("Chat history loaded.")
        except FileNotFoundError:
            print("No previous chat history found. Starting fresh.")


if __name__ == "__main__":
    logger.info("Main")
    # chatbot_interface()
    # vision.start()