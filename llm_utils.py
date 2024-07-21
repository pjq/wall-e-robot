import json
import logging
from llama_index.llms.openai import OpenAI
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from config import load_config, Settings  # Import the necessary functions and classes

CONFIG_PATH = 'config.json'

# Remove the old load_config function as we will use the one from config.py
# def load_config(config_path=CONFIG_PATH):
#     logging.info(f"Loading configuration from {config_path}")
#     with open(config_path, 'r') as config_file:
#         return json.load(config_file)

def initialize_llm(settings: Settings, use_multi_modal=False):
    logging.info("Initializing LLM with provided settings")
    
    if use_multi_modal:
        return OpenAIMultiModal(
            model=settings.llm_model, 
            api_key=settings.llm_api_key, 
            api_base=settings.llm_api_base,
            max_new_tokens=getattr(settings, 'llm_max_new_tokens', 300)  # Use getattr to handle optional settings
        )
    else:
        return OpenAI(
            temperature=settings.llm_temperature, 
            model=settings.llm_model, 
            api_key=settings.llm_api_key, 
            api_base=settings.llm_api_base
        )

def load_and_initialize_llm(config_path=CONFIG_PATH):
    settings = load_config(config_path)
    llm = initialize_llm(settings, use_multi_modal=True)
    
    return llm