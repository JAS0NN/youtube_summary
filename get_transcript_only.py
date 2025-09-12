#!/usr/bin/env python3
"""
Simple script to get YouTube transcript only (no summarization).
Usage: python get_transcript_only.py <youtube_url>
"""

import sys
import os
from transcript_handler import get_transcript
from youtube_utils import extract_video_id


def main():
    if len(sys.argv) != 2:
        print("Usage: python get_transcript_only.py <youtube_url>")
        print("Example: python get_transcript_only.py https://www.youtube.com/watch?v=VIDEO_ID")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)
        print(f"Video ID: {video_id}")
        
        # Get transcript
        print("Fetching transcript...")
        transcript, title = get_transcript(video_id)
        
        if transcript and title:
            print(f"\nTranscript for: {title}")
            print("=" * 50)
            print(transcript)
            print("=" * 50)
            print(f"Transcript saved to transcript/{title}_transcript.txt")
        else:
            print("Failed to get transcript.")
            sys.exit(1)
            
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
