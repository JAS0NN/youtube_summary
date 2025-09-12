"""
Simple module to get YouTube transcript only (no summarization).
"""

from transcript_handler import get_transcript
from youtube_utils import extract_video_id


def get_youtube_transcript(url: str) -> tuple[str, str] | tuple[None, None]:
    """
    Get YouTube transcript from URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        Tuple of (transcript_text, video_title) or (None, None) on failure
    """
    try:
        video_id = extract_video_id(url)
        transcript, title = get_transcript(video_id)
        return transcript, title
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None, None


def print_transcript(url: str) -> bool:
    """
    Get and print YouTube transcript from URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        True if successful, False otherwise
    """
    transcript, title = get_youtube_transcript(url)
    
    if transcript and title:
        print(f"Transcript for: {title}")
        print("=" * 50)
        print(transcript)
        print("=" * 50)
        return True
    else:
        print("Failed to get transcript.")
        return False


# Example usage
if __name__ == "__main__":
    # Test with a URL
    test_url = input("Enter YouTube URL: ")
    print_transcript(test_url)
