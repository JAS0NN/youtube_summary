import os
import json
from typing import Dict, Optional
from pathlib import Path
import re


def load_dotenv(dotenv_path=None):
    """
    Load environment variables from .env file
    """
    if dotenv_path is None:
        # 查找项目根目录的.env文件
        project_root = Path(__file__).parent.parent
        dotenv_path = project_root / ".env"
    
    if not os.path.isfile(dotenv_path):
        return
    
    with open(dotenv_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            # 移除引号
            if value and (value[0] == value[-1] == '"' or value[0] == value[-1] == "'"):
                value = value[1:-1]
            
            os.environ[key] = value


def load_api_keys() -> Dict[str, Optional[str]]:
    """
    Load API keys from environment variables or fallback to config/config.json.
    Returns a dict with keys: openai_api_key, grok_api_key, openrouter_api_key.
    """
    # 先加载.env文件
    load_dotenv()
    
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
