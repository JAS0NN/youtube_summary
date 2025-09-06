import json
import os
import requests
from typing import Optional, Dict, Union


def get_summary(transcript_content: str, api_key: str, grok: bool = False, use_openai: bool = False) -> Optional[Dict]:
    """
    Generate a summary from the transcript content using the selected API.
    Returns the API response JSON as a dict, or None on failure.
    
    Args:
        transcript_content: The transcript text to summarize
        api_key: API key for the selected service
        grok: Whether to use Grok API
        use_openai: Whether to use OpenAI API
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
        model = "gpt-4o"
    elif grok:
        model = "grok-3"
    else:
        model = "gpt-4o"  # Default for OpenRouter
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
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            if use_openai:
                print(f"[Summarizer] 错误: OpenAI API密钥无效或未设置。请检查您的API密钥。")
                print(f"[Summarizer] OpenAI API密钥应以'sk-'开头，而不是'sk-proj-'。")
            elif grok:
                print(f"[Summarizer] 错误: Grok API密钥无效或未设置。请检查您的API密钥。")
            else:
                print(f"[Summarizer] 错误: OpenRouter API密钥无效或未设置。请检查您的API密钥。")
        else:
            print(f"[Summarizer] HTTP错误: {e}")
            if response.text:
                print(f"[Summarizer] 响应内容: {response.text}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[Summarizer] 连接错误: {e}")
        print("[Summarizer] 请检查您的网络连接或API端点是否正确。")
        return None
    except requests.exceptions.Timeout as e:
        print(f"[Summarizer] 请求超时: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Summarizer] 请求错误: {e}")
        return None
    except Exception as e:
        print(f"[Summarizer] 未预期的错误: {e}")
        return None
