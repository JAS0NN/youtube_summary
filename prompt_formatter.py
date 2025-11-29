import os
from typing import Optional


def load_system_prompt() -> str:
    """
    Load system prompt from prompt.txt file.
    
    Returns:
        System prompt string, or default prompt if file not found
    """
    prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            sys_prompt = f.read()
        return sys_prompt
    except FileNotFoundError:
        print(f"[PromptFormatter] Warning: Prompt file not found at {prompt_file_path}")
        return "Please summarize the following content."  # Fallback prompt
    except Exception as e:
        print(f"[PromptFormatter] Error reading prompt file: {e}")
        return "Please summarize the following content."  # Fallback prompt


def format_prompt(transcript_content: str, system_prompt: Optional[str] = None) -> str:
    """
    Format transcript with system prompt.
    
    Args:
        transcript_content: The transcript text
        system_prompt: Optional system prompt. If None, will load from prompt.txt
        
    Returns:
        Formatted prompt string
    """
    if system_prompt is None:
        system_prompt = load_system_prompt()
    
    formatted_prompt = f"""# System Prompt

{system_prompt}

# User Content (Transcript)

{transcript_content}
"""
    return formatted_prompt


def save_formatted_prompt(formatted_prompt: str, video_title: str, current_date: str) -> str:
    """
    Save formatted prompt to file.
    
    Args:
        formatted_prompt: The formatted prompt text
        video_title: Video title for filename
        current_date: Current date string (YYYY-MM-DD format)
        
    Returns:
        Path to saved file
    """
    prompt_filename = f"{current_date}_{video_title}_prompt.txt"
    prompt_dir = os.path.join(os.path.dirname(__file__), "formatted_prompts", current_date)
    
    if not os.path.exists(prompt_dir):
        os.makedirs(prompt_dir)
    
    prompt_path = os.path.join(prompt_dir, prompt_filename)
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(formatted_prompt)
    
    return prompt_path
