import argparse
import json

# Create a configuration container
class Settings:
    pass

settings = None
def load_config(config_file):
    global settings

    # Load the JSON config file
    with open(config_file, "r") as f:
        config_data = json.load(f)

    # Save the values to the configuration variables
    settings = Settings()
    settings.cohere_api_key = config_data["cohere_api_key"]
    settings.openai_api_key = config_data["openai_api_key"]
    settings.enable_openai = config_data["enable_openai"]
    settings.enable_mps = config_data["enable_mps"]
    settings.edge_tts_enable = config_data["edge_tts_enable"]
    settings.edge_tts_voice = config_data["edge_tts_voice"]
    settings.openai_api_base_url = config_data["openai_api_base_url"]
    settings.blip_model = config_data["blip_model"]
    settings.whisper_cpp_path = config_data["whisper_cpp_path"]
    settings.car_api_url = config_data["car_api_url"]
    settings.car_camera_stream_url = config_data["car_camera_stream_url"]
    settings.car_camera_stream_enable = config_data["car_camera_stream_enable"]

    return settings
