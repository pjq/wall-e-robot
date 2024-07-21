import argparse
import json

# Create a configuration container
class Settings:
    pass

settings = None
def load_config(config_file, section="Settings"):
    global settings

    # Load the JSON config file
    with open(config_file, "r") as f:
        config_data = json.load(f)

    # Ensure the section exists in the config data
    if section not in config_data:
        raise ValueError(f"Section '{section}' not found in the configuration file.")

    # Save the values to the configuration variables
    settings = Settings()
    
    # LLM settings
    settings.llm_temperature = config_data[section]["llm"]["temperature"]
    settings.llm_model = config_data[section]["llm"]["model"]
    settings.llm_api_key = config_data[section]["llm"]["api_key"]
    settings.llm_api_base = config_data[section]["llm"]["api_base"]

    # Other settings
    settings.cohere_api_key = config_data[section]["others"]["cohere_api_key"]
    settings.openai_api_key = config_data[section]["others"]["openai_api_key"]
    settings.enable_openai = config_data[section]["others"]["enable_openai"]
    settings.openai_api_base_url = config_data[section]["others"]["openai_api_base_url"]
    settings.openai_api_base_url2 = config_data[section]["others"]["openai_api_base_url2"]
    settings.enable_mps = config_data[section]["others"]["enable_mps"]
    settings.whisper_cpp_path = config_data[section]["others"]["whisper_cpp_path"]
    settings.edge_tts_enable = config_data[section]["others"]["edge_tts_enable"]
    settings.edge_tts_voice = config_data[section]["others"]["edge_tts_voice"]
    settings.edge_tts_voice_cn = config_data[section]["others"]["edge_tts_voice_cn"]
    settings.car_api_url = config_data[section]["others"]["car_api_url"]
    settings.car_camera_stream_enable = config_data[section]["others"]["car_camera_stream_enable"]
    settings.car_camera_stream_url = config_data[section]["others"]["car_camera_stream_url"]
    settings.blip_model = config_data[section]["others"]["blip_model"]
    settings.blip_model2 = config_data[section]["others"]["blip_model2"]

    return settings