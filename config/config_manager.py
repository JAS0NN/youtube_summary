import os
import json
from typing import Dict, Optional


def load_api_keys() -> Dict[str, Optional[str]]:
    """
    Load API keys from environment variables or fallback to config/config.json.
    Returns a dict with keys: openai_api_key, grok_api_key, openrouter_api_key.
    """
    keys = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "grok_api_key": os.getenv("GROK_API_KEY"),
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY")
    }

    # Check if any key is missing
    if not all(keys.values()):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            # Fill missing keys from config file
            for key in keys:
                if not keys[key]:
                    keys[key] = config_data.get(key)
        except FileNotFoundError:
            print(f"[ConfigManager] Config file not found at {config_path}")
        except json.JSONDecodeError:
            print(f"[ConfigManager] Config file {config_path} is not valid JSON")
        except Exception as e:
            print(f"[ConfigManager] Error loading config file: {e}")

    return keys
