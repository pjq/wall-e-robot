import logging
import os
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Combine tools into a single agent
llm = load_and_initialize_llm()

# Flag to enable mock functions
USE_MOCK = True

# Real function to turn the car
def turn_car(direction: str, duration: int) -> str:
    """Turn the car in the specified direction for a given duration."""
    if direction not in ["left", "right", "up", "down"]:
        logger.error("Invalid direction: %s", direction)
        return "Invalid direction. Please specify 'left', 'right', 'up', or 'down'."
    logger.info("Turning car %s for %d seconds", direction, duration)
    return f"Car turned {direction} for {duration} seconds."

# Mock function to turn the car
def mock_turn_car(direction: str, duration: int) -> str:
    """Mock turn the car in the specified direction for a given duration."""
    logger.info("Mock: Turning car %s for %d seconds", direction, duration)
    return f"Mock: Car would turn {direction} for {duration} seconds."

# Real function to capture image from the car's camera
def capture_image() -> str:
    """Capture an image from the car's camera."""
    cap = cv2.VideoCapture(0)  # Assuming the camera is at index 0
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        logger.error("Failed to open camera")
        return "Failed to open camera"
    
    # Allow the camera to warm up
    time.sleep(3)
    
    ret, frame = cap.read()
    if not ret:
        logger.error("Failed to read frame from camera")
        cap.release()
        return "Failed to read frame from camera"
    
    # Check if the frame is empty
    if frame is None or frame.size == 0:
        logger.error("Captured frame is empty")
        cap.release()
        return "Captured frame is empty"
    
    # Convert the frame to RGB (if needed)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    image_path = "captured_image.jpg"
    # cv2.imwrite(image_path, frame)    
    cv2.imwrite(image_path, frame_rgb)

    cap.release()
    return image_path

# Mock function to capture image from the car's camera
def mock_capture_image() -> str:
    """Mock capture an image from the car's camera."""
    logger.info("Mock: Capturing image from camera")
    # return "mock_captured_image.jpg"
    return "image.png"

# Function to process image URL
def process_image_urls(image_url):
    """Process image URLs to load image documents."""
    image_documents = load_image_urls([image_url])
    return image_documents


# Real function to describe images
def describe_images(image_path):
    """Describe images using the multi-modal LLM."""
    image_document = ImageDocument(image_path=image_path)

    try:
        response = llm.complete(
            prompt="Describe the images as an alternative text",
            image_documents=[image_document],
        )
    except Exception as e:
        logger.error("Failed to complete LLM request: %s", str(e))
        response = "Error: Unable to describe images."
    return response

# Mock function to describe images
def mock_describe_images(image_path):
    """Mock describe images."""
    logger.info("Mock: Describing images")
    import random

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

# Function to display image
def display_image(image_path):
    """Display an image using matplotlib."""
    img = Image.open(image_path)
    plt.imshow(img)
    plt.show()

# Select functions based on the flag
turn_car_fn = mock_turn_car if USE_MOCK else turn_car
capture_image_fn = mock_capture_image if USE_MOCK else capture_image
capture_image_fn = capture_image
describe_images_fn = mock_describe_images if USE_MOCK else describe_images
describe_images_fn = describe_images

# Define the tools using FunctionTool
turn_car_tool = FunctionTool.from_defaults(
    turn_car_fn,
    name="TurnCarTool",
    description="A tool to turn the car in specified direction for a given duration."
)

capture_image_tool = FunctionTool.from_defaults(
    capture_image_fn,
    name="CaptureImageTool",
    description="A tool to capture an image from the car's camera."
)

describe_image_tool = FunctionTool.from_defaults(
    describe_images_fn,
    name="DescribeImageTool",
    description="A tool to describe images captured by the car's camera."
)
tools = [turn_car_tool, capture_image_tool, describe_image_tool]

agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)

# ChatBot interface for car control
def chatbot_interface():
    """ChatBot interface for car control."""
    print("Welcome to the Car Control ChatBot!")
    while True:
        user_input = input("Enter command (turn/capture/describe/exit): ").strip().lower()
        if user_input == "exit":
            print("Exiting Car Control ChatBot. Goodbye!")
            break
        elif user_input == "capture":
            image_path = capture_image_fn()
            if "Failed" not in image_path:
                display_image(image_path)
                print(f"Image captured and saved to {image_path}")
            else:
                print(image_path)
        elif user_input == "describe":
            image_path = capture_image_fn()
            if "Failed" not in image_path:
                display_image(image_path)
                response = describe_images_fn([image_path])
                print(response)
            else:
                print(image_path)
        else:
            response = agent.chat(user_input)
            print(response)

if __name__ == "__main__":
    chatbot_interface()
    # vision = VisionService()
    # vision.start()