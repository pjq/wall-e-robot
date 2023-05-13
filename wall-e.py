import argparse
import os
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import lib.utils as proxy
import config
from lib import edge_tts_playback
from lib import vision_service
import openai
import threading

class ChatBot:
    def __init__(self):
        # Set up tools
        search = proxy.createGoogleSerper()
        bash = proxy.createBash()
        wolfram = proxy.createWolfram()
        human = proxy.createHuman()
        weather = proxy.createOpenWeatherMap()
        vision_caption = proxy.createVisionCaption()
        vision_control = proxy.createVisionControl()

        self.tools = [
            Tool(
                name="Google Search",
                func=search.run,
                description="Useful for answering questions about current events or the current state of the world. The input should be a single search term."
            ),
            Tool(
                name="Wolfram",
                func=wolfram.run,
                description="Computational knowledge engine."
            ),
            Tool(
                name="Human",
                func=human.run,
                description="Human agent for difficult questions."
            ),
            Tool(
                name="Weather",
                func=weather.run,
                description="Provides weather information."
            ),
            # vision_caption,
            vision_control,
            Tool(
                name="Bash Process",
                func=bash.run,
                description="Useful for controlling or getting information from the current system."
            )
        ]

        # Set up the chatbot
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.llm = ChatOpenAI(temperature=1.0)
        self.agent_chain = initialize_agent(self.tools, self.llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=self.memory)

    def start_chat(self):
        # Start chatting with the user
        print('Bot: Hello! How can I assist you today?')
        while True:
            try:
                user_input = input('You: ')
                if user_input.lower() in ['exit', 'bye', 'quit']:
                    print('Bot: Goodbye!')
                    break
                response = self.agent_chain.run(user_input)
                print(f'Bot: {response}')
                if config.settings.edge_tts_enable:
                    edge_tts_playback.playTTS(response, config.settings.edge_tts_voice)
            except Exception as e:
                print(f'An error occurred: {e}')

def setup_config(config_file):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")

    settings = config.load_config(config_file)

    # print("OpenAI API Key:", settings.openai_api_key)
    print("Enable OpenAI:", settings.enable_openai)
    print("Enable enable_mps:", settings.enable_mps)
    print("openai_api_base_url:", settings.openai_api_base_url)
    print("blip_model:", settings.blip_model)
    print("whisper_cpp_path:", settings.whisper_cpp_path)
    print("car_api_url:", settings.car_api_url)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = config.settings.openai_api_key
    openai.api_key = api_key
    if config.settings.openai_api_base_url:
        openai.api_base = config.settings.openai_api_base_url

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Example with config file support.")
    parser.add_argument("--config", dest="config", default="myconfig.json", help="Path to the config file")
    args = parser.parse_args()
    setup_config(args.config)

    bot = ChatBot()
    threading.Thread(target=bot.start_chat).start()  # start thread to wait for user input
    vision_service.vision.start()
