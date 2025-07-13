import json
import os
import requests
from typing import Optional, Dict


def get_summary(transcript_content: str, api_key: str, grok: bool = False) -> Optional[Dict]:
    """
    Generate a summary from the transcript content using the selected API.
    Returns the API response JSON as a dict, or None on failure.
    """
    url = "https://api.x.ai/v1/chat/completions" if grok else "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Load system prompt from external file
    prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            sys_prompt = f.read()
    except FileNotFoundError:
        print(f"[Summarizer] Warning: Prompt file not found at {prompt_file_path}")
        sys_prompt = "Please summarize the following content."  # Fallback prompt
    except Exception as e:
        print(f"[Summarizer] Error reading prompt file: {e}")
        sys_prompt = "Please summarize the following content."  # Fallback prompt

    model = "grok-3" if grok else "gpt-4o"
    # model = "meta-llama/llama-4-maverick:free"
    data = {
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": transcript_content}
        ],
        "model": model,
        "stream": False,
        "temperature": 0.01
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[Summarizer] Error calling API: {e}")
        return None
