import threading
import config
import car_control

class CarControlChatBot:
    def __init__(self):
        self.voice = config.settings.edge_tts_voice_cn
        self.agent = car_control.car_init()

    def start_chat(self):
        """ChatBot interface for car control."""
        print("Welcome to the Car Control ChatBot!")
        while True:
            user_input = input("Enter command (turn/capture/describe/exit): ").strip().lower()
            if user_input == "exit":
                print("Exiting Car Control ChatBot. Goodbye!")
                break
            else:
                try:
                    response = self.agent.chat(user_input)
                    car_control.playTTS(response, self.voice)
                    print(response)
                except ValueError as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    bot = CarControlChatBot()
    threading.Thread(target=bot.start_chat).start()  # start thread to wait for user input
    car_control.vision.start()