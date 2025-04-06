import os
import datetime
from typing import Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_utils import get_video_title


def get_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch the transcript for a YouTube video.
    Tries English first, then Chinese if English is unavailable.
    Saves the formatted transcript to a file.
    Returns (formatted_transcript, video_title) or (None, None) on failure.
    """
    try:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception as e:
            if 'Could not retrieve a transcript' in str(e):
                print("[TranscriptHandler] English transcript not available, trying Chinese...")
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=['zh', 'zh-CN', 'zh-TW', 'zh-Hant', 'zh-Hans']
                )
            else:
                raise e

        video_title = get_video_title(video_id)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        transcript_filename = f"{video_title}_{current_date}_transcript.txt"

        formatted_lines = [f"# {video_title}\n\n"]
        for entry in transcript:
            minutes = int(entry['start'] // 60)
            seconds = int(entry['start'] % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}] "
            formatted_lines.append(f"{timestamp}{entry['text']}\n")

        formatted_transcript = ''.join(formatted_lines)

        transcript_dir = os.path.join(os.path.dirname(__file__), "transcript")
        if not os.path.exists(transcript_dir):
            os.makedirs(transcript_dir)

        transcript_path = os.path.join(transcript_dir, transcript_filename)
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(formatted_transcript)

        print(f"[TranscriptHandler] Transcript saved to {transcript_path}")
        return formatted_transcript, video_title

    except Exception as e:
        print(f"[TranscriptHandler] Error fetching transcript: {e}")
        if 'Subtitles are disabled for this video' in str(e):
            print("[TranscriptHandler] Please ensure the video has subtitles enabled.")
        elif 'Could not retrieve a transcript' in str(e):
            print("[TranscriptHandler] No transcript available in English or Chinese.")
        return None, None
