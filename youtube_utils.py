import re
import requests
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    """
    Extract the YouTube video ID from a URL.
    Raises ValueError if the URL is invalid or ID cannot be found.
    """
    url = url.strip().strip('"\'')
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
            elif 'embed' in parsed_url.path or 'v' in parsed_url.path:
                return parsed_url.path.split('/')[-1]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        raise ValueError("Could not extract video ID from URL")
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {str(e)}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be a safe filename by removing invalid characters,
    replacing spaces with underscores, and limiting length.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    filename = filename.replace(' ', '_')[:200]
    return filename


def get_video_title(video_id: str) -> str:
    """
    Fetch the YouTube video title using the video ID.
    Returns sanitized title or video ID as fallback.
    """
    try:
        response = requests.get(f'https://www.youtube.com/watch?v={video_id}')
        response.raise_for_status()
        title_match = re.search(r'<meta name="title" content="([^"]+)"', response.text)
        if title_match:
            return sanitize_filename(title_match.group(1))
        return video_id
    except requests.exceptions.RequestException as e:
        print(f"[YouTubeUtils] Error fetching video page: {e}")
        return video_id
    except Exception as e:
        print(f"[YouTubeUtils] Could not get video title: {e}")
        return video_id
