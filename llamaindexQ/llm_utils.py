import json
import logging
from llama_index.llms.openai import OpenAI
from llama_index.multi_modal_llms.openai import OpenAIMultiModal

CONFIG_PATH = 'llamaindexQconfig.json'

def load_config(config_path=CONFIG_PATH):
    logging.info(f"Loading configuration from {config_path}")
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def initialize_llm(settings, use_multi_modal=False):
    logging.info("Initializing LLM with provided settings")
    llm_settings = settings['llm']
    
    if use_multi_modal:
        return OpenAIMultiModal(
            model=llm_settings['model'], 
            api_key=llm_settings['api_key'], 
            api_base=llm_settings['api_base'],
            max_new_tokens=llm_settings.get('max_new_tokens', 300)
        )
    else:
        return OpenAI(
            temperature=llm_settings['temperature'], 
            model=llm_settings['model'], 
            api_key=llm_settings['api_key'], 
            api_base=llm_settings['api_base']
        )

def load_and_initialize_llm(config_path=CONFIG_PATH):
    config = load_config(config_path)
    llm = initialize_llm(config['Settings'], use_multi_modal=True)
    
    return llm