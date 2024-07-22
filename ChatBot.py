import threading
import logging
import config
from car_control import CarController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarControlChatBot:
    def __init__(self):
        self.car_controller = CarController()
        self.voice = config.settings.edge_tts_voice_cn
        self.agent = self.car_controller.car_init()

    def start_chat(self):
        """ChatBot interface for car control."""
        logger.info("Welcome to the Car Control ChatBot!")
        while True:
            user_input = input("Enter command (turn/capture/describe/exit): ").strip().lower()
            if user_input == "exit":
                logger.info("Exiting Car Control ChatBot. Goodbye!")
                break
            else:
                try:
                    response = self.agent.chat(user_input)
                    self.car_controller.playTTS(response, self.voice)
                    logger.info(response)
                except ValueError as e:
                    logger.error(f"Error: {e}")

if __name__ == "__main__":
    bot = CarControlChatBot()
    threading.Thread(target=bot.start_chat).start()  # start thread to wait for user input
    bot.car_controller.vision.start()