import json
import os
import requests
from typing import Optional, Dict, Union


def get_summary(transcript_content: str, api_key: str, grok: bool = False, use_openai: bool = False, openrouter_model: str = None) -> Optional[Dict]:
    """
    Generate a summary from the transcript content using the selected API.
    Returns the API response JSON as a dict, or None on failure.

    Args:
        transcript_content: The transcript text to summarize
        api_key: API key for the selected service
        grok: Whether to use Grok API
        use_openai: Whether to use OpenAI API
        openrouter_model: Model name for OpenRouter (e.g., "openai/gpt-4o")
    """
    if use_openai:
        url = "https://api.openai.com/v1/chat/completions"
    elif grok:
        url = "https://api.x.ai/v1/chat/completions"
    else:
        url = "https://openrouter.ai/api/v1/chat/completions"
        
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

    if use_openai:
        model = "gpt-5.1"
    elif grok:
        model = "grok-4-1-fast-non-reasoning"
    else:
        # OpenRouter - use the model name provided by user
        model = openrouter_model if openrouter_model else "openai/gpt-5.1"  # Default to gpt-5.1 if no model specified
    # model = "meta-llama/llama-4-maverick:free"
    data = {
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": transcript_content}
        ],
        "model": model,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            if use_openai:
                print(f"[Summarizer] Error: OpenAI API key is invalid or not set. Please check your API key.")
                print(f"[Summarizer] OpenAI API key should start with 'sk-', not 'sk-proj-'.")
            elif grok:
                print(f"[Summarizer] Error: Grok API key is invalid or not set. Please check your API key.")
            else:
                print(f"[Summarizer] Error: OpenRouter API key is invalid or not set. Please check your API key.")
        else:
            print(f"[Summarizer] HTTP error: {e}")
            if response.text:
                print(f"[Summarizer] Response content: {response.text}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[Summarizer] Connection error: {e}")
        print("[Summarizer] Please check your network connection or if the API endpoint is correct.")
        return None
    except requests.exceptions.Timeout as e:
        print(f"[Summarizer] Request timeout: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Summarizer] Request error: {e}")
        return None
    except Exception as e:
        print(f"[Summarizer] Unexpected error: {e}")
        return None
