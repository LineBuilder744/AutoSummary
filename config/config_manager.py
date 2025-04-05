import os
import json

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_api_config():
    
    cfg = {}

    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Warning: Config file not found at {CONFIG_FILE_PATH}")
        return None
    
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
            cfg['api_token'] = config.get('api_token')
            cfg['model'] = config.get('model')
            cfg['max_tokens'] = config.get('max_tokens')
            cfg['temperature'] = config.get('temperature')

            
            if not (cfg['api_token'] or cfg['model'] or cfg['max_tokens'] or cfg['temperature']):
                print("Warning: API token/model/max_tokens/temperature not found in config file")
                # Check for legacy key name
                cfg['api_token'] = config.get('api_key')
                if cfg['api_token']:
                    print("Found token in legacy 'api_key' field - please update your config")
            
            return cfg
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None