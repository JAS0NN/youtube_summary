import os
import argparse
import datetime
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_utils import extract_video_id, get_video_title


def download_youtube_video(url: str, save_path: str):
    """
    Download YouTube video with fallback format options.

    Args:
        url: YouTube video URL
        save_path: Directory to save the downloaded video

    Returns:
        bool: True if download succeeded, False otherwise
    """
    os.makedirs(save_path, exist_ok=True)

    # More flexible format selection with fallbacks
    ydl_opts = {
        "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
        # Try multiple format options in order of preference:
        # 1. Best video (<=1080p) + best audio, merged to mp4
        # 2. Best combined format up to 1080p
        # 3. Best available format
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "merge_output_format": "mp4",
        # Add user agent to avoid some restrictions
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        # Allow IPv6 to avoid some network restrictions
        "allow_unplayable_formats": False,
        # Don't fail on unavailable formats
        "ignoreerrors": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First, get video info to check availability
            info = ydl.extract_info(url, download=False)
            print(f"\n✓ Found video: {info['title']}")
            print(
                f"  Duration: {info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}"
            )
            print(f"  Uploader: {info.get('uploader', 'Unknown')}")

            # Now download
            print(f"\nDownloading to: {save_path}")
            ydl.download([url])
            print("\n✓ Download completed!")
            return True

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        print(f"\n✗ Download failed: {error_msg}")

        # If format error, try to list available formats
        if (
            "Requested format is not available" in error_msg
            or "format" in error_msg.lower()
        ):
            print("\nAttempting to list available formats...")
            try:
                list_opts = ydl_opts.copy()
                list_opts["listformats"] = True
                with yt_dlp.YoutubeDL(list_opts) as ydl_list:
                    ydl_list.extract_info(url, download=False)
            except Exception as list_error:
                print(f"Could not list formats: {list_error}")

            # Try a simpler format as last resort
            print("\nAttempting download with simplified format selection...")
            try:
                simple_opts = ydl_opts.copy()
                simple_opts["format"] = "best"
                with yt_dlp.YoutubeDL(simple_opts) as ydl_simple:
                    ydl_simple.download([url])
                print("\n✓ Download completed with simplified format!")
                return True
            except Exception as simple_error:
                print(f"\n✗ Simplified download also failed: {simple_error}")
                print("\nThis video may not be available for download.")
                print("Possible reasons:")
                print("  - Video is age-restricted or private")
                print("  - Geographic restrictions")
                print("  - YouTube API changes require yt-dlp update")
                print("\nTry updating yt-dlp: pip install -U yt-dlp")
        return False


def download_transcript(video_id: str, save_path: str, language: str = "en"):
    """
    Download English transcript for a YouTube video.

    Args:
        video_id: YouTube video ID
        save_path: Directory to save the transcript
        language: Language code (default: 'en' for English)

    Returns:
        bool: True if download succeeded, False otherwise
    """
    os.makedirs(save_path, exist_ok=True)

    try:
        print(f"\n📝 Fetching {language.upper()} transcript...")
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        # Try to get transcript in requested language
        try:
            transcript = transcript_list.find_transcript([language])
            fetched_transcript = transcript.fetch()
            transcript_data = fetched_transcript.to_raw_data()
            print(
                f"✓ Found {language.upper()} transcript ({'auto-generated' if transcript.is_generated else 'manual'})"
            )
        except Exception as e:
            print(f"✗ {language.upper()} transcript not available: {e}")
            return False

        # Get video title and format transcript
        video_title = get_video_title(video_id)
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transcript_filename = f"{video_title}_{current_date}_transcript_{language}.txt"

        formatted_lines = [f"# {video_title}\n"]
        formatted_lines.append(f"# Language: {language.upper()}\n")
        formatted_lines.append(f"# Date: {current_date}\n\n")

        for entry in transcript_data:
            minutes = int(entry["start"] // 60)
            seconds = int(entry["start"] % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            formatted_lines.append(f"{timestamp} {entry['text']}\n")

        formatted_transcript = "".join(formatted_lines)

        # Save transcript
        transcript_path = os.path.join(save_path, transcript_filename)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(formatted_transcript)

        print(f"✓ Transcript saved to: {transcript_path}")
        return True

    except Exception as e:
        print(f"\n✗ Error fetching transcript: {e}")
        if "Subtitles are disabled for this video" in str(e):
            print("  → Subtitles are disabled for this video")
        elif "Could not retrieve a transcript" in str(e):
            print(f"  → No transcript available in {language.upper()}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and/or transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download video only
  python video_downloader.py https://youtube.com/watch?v=VIDEO_ID

  # Download video with English transcript
  python video_downloader.py https://youtube.com/watch?v=VIDEO_ID --transcript

  # Download only English transcript
  python video_downloader.py https://youtube.com/watch?v=VIDEO_ID --transcript-only

  # Download with Chinese transcript
  python video_downloader.py https://youtube.com/watch?v=VIDEO_ID --transcript --lang zh
        """,
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--save-path",
        default="./downloads",
        help="Directory to save downloads (default: ./downloads)",
    )
    parser.add_argument(
        "--transcript", action="store_true", help="Also download transcript"
    )
    parser.add_argument(
        "--transcript-only",
        action="store_true",
        help="Download only transcript, skip video",
    )
    parser.add_argument(
        "--lang", default="en", help="Transcript language code (default: en)"
    )

    args = parser.parse_args()

    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        print("✗ Invalid YouTube URL")
        return

    print(f"Video ID: {video_id}")

    # Download transcript if requested
    if args.transcript or args.transcript_only:
        download_transcript(video_id, args.save_path, args.lang)

    # Download video unless transcript-only mode
    if not args.transcript_only:
        download_youtube_video(args.url, args.save_path)


if __name__ == "__main__":
    main()
