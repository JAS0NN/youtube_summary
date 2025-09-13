"""
Web service adapter for YouTube summarization functionality.
Wraps existing CLI logic for web interface use.
"""
import os
import datetime
from typing import Dict, Optional, Tuple
from config.config_manager import load_api_keys
from youtube_utils import extract_video_id, sanitize_filename
from transcript_handler import get_transcript
from summarizer import get_summary


def get_available_providers() -> Dict[str, bool]:
    """Check which AI providers are available based on API keys."""
    api_keys = load_api_keys()
    return {
        'openai': bool(api_keys.get('openai_api_key')),
        'grok': bool(api_keys.get('grok_api_key')),
        'openrouter': bool(api_keys.get('openrouter_api_key'))
    }


def summarize_youtube_url(url: str, provider: str, save_files: bool = False, custom_model: str = None) -> Dict:
    """
    Summarize a YouTube video from URL.
    
    Args:
        url: YouTube video URL
        provider: AI provider ('openai', 'grok', 'openrouter')
        save_files: Whether to save transcript and summary files
        custom_model: Custom model name for OpenRouter (optional)
        
    Returns:
        Dict with success status, data, and error information
    """
    try:
        # Validate URL and extract video ID
        video_id = extract_video_id(url)
        
        # Get API keys
        api_keys = load_api_keys()
        
        # Determine API configuration
        if provider == 'openai':
            api_key = api_keys.get('openai_api_key')
            use_openai = True
            use_grok = False
        elif provider == 'grok':
            api_key = api_keys.get('grok_api_key')
            use_openai = False
            use_grok = True
        elif provider == 'openrouter':
            api_key = api_keys.get('openrouter_api_key')
            use_openai = False
            use_grok = False
        else:
            return {
                'success': False,
                'error': f'Invalid provider: {provider}',
                'error_type': 'validation'
            }
        
        if not api_key:
            return {
                'success': False,
                'error': f'{provider.title()} API key not found. Please configure your API keys in Replit Secrets.',
                'error_type': 'configuration'
            }
        
        # Get transcript
        transcript_content, video_title = get_transcript(video_id)
        
        if not transcript_content or not video_title:
            return {
                'success': False,
                'error': 'Unable to fetch video transcript. Please ensure the video has subtitles enabled.',
                'error_type': 'transcript'
            }
        
        # Generate summary
        result = get_summary(transcript_content, api_key, grok=use_grok, use_openai=use_openai, custom_model=custom_model)
        
        if not result:
            return {
                'success': False,
                'error': f'Failed to generate summary using {provider.title()} API. Please check your API key and try again.',
                'error_type': 'api'
            }
        
        try:
            summary = result['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            return {
                'success': False,
                'error': f'Unexpected response format from {provider.title()} API.',
                'error_type': 'parsing'
            }
        
        # Prepare file paths (but don't save unless requested)
        transcript_path = None
        summary_path = None
        
        if save_files:
            # Save transcript and summary files following the same pattern as CLI version
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Save transcript file (similar to transcript_handler.py pattern)
            transcript_filename = sanitize_filename(f"{video_title}_{current_date}_transcript.txt")
            transcript_dir = os.path.join(os.path.dirname(__file__), "..", "transcript")
            if not os.path.exists(transcript_dir):
                os.makedirs(transcript_dir)
            
            transcript_path = os.path.join(transcript_dir, transcript_filename)
            # Format transcript with title header and timestamps (same as CLI version)
            formatted_lines = [f"# {video_title}\n\n"]
            # Extract timestamps from the original transcript_content if possible
            # For web version, we'll save the content as provided
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(transcript_content)
            
            # Save summary file (following youtube_summary.py pattern)
            summary_filename = sanitize_filename(f"{current_date}_{video_title}_summary.md")
            summary_dir = os.path.join(os.path.dirname(__file__), "..", "summary", current_date)
            if not os.path.exists(summary_dir):
                os.makedirs(summary_dir)
            
            summary_path = os.path.join(summary_dir, summary_filename)
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"# {video_title}\n\n")
                f.write(f"**Provider:** {provider.title()}\n")
                if provider == 'openrouter' and custom_model:
                    f.write(f"**Model:** {custom_model}\n")
                f.write(f"**Date:** {current_date}\n")
                f.write(f"**Video URL:** https://www.youtube.com/watch?v={video_id}\n\n")
                f.write("## Summary\n\n")
                f.write(summary)
            
            print(f"[WebService] Files saved:")
            print(f"  Transcript: {transcript_path}")
            print(f"  Summary: {summary_path}")
        
        return {
            'success': True,
            'data': {
                'video_title': video_title,
                'video_id': video_id,
                'summary': summary,
                'provider': provider,
                'model': custom_model if provider == 'openrouter' and custom_model else None,
                'transcript_content': transcript_content,
                'transcript_path': transcript_path,
                'summary_path': summary_path
            }
        }
        
    except ValueError as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': 'validation'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}',
            'error_type': 'system'
        }