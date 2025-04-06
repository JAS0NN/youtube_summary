import argparse
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(url):
    # Clean the URL first
    url = url.strip().strip('"\'')
    
    try:
        # Handle different YouTube URL formats
        parsed_url = urlparse(url)
        
        # Handle standard youtube.com URLs
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
            elif 'embed' in parsed_url.path or 'v' in parsed_url.path:
                return parsed_url.path.split('/')[-1]
        # Handle youtu.be URLs
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        
        raise ValueError("Could not extract video ID from URL")
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {str(e)}")

def get_transcript(video_id):
    try:
        # Try English transcript first
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception as e:
            # If English transcript is not available, try Chinese
            if 'Could not retrieve a transcript' in str(e):
                print("English transcript not available, trying Chinese transcript...")
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'zh-CN', 'zh-TW'])
            else:
                raise e
        
        # Format the transcript to readable text
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        
        # Save to file with sanitized filename
        output_file = 'transcript.txt'
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_transcript)
            
        print(f"Transcript has been saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred while getting transcript: {str(e)}")
        if 'Subtitles are disabled for this video' in str(e):
            print("Please make sure the video has subtitles enabled.")
        elif 'Could not retrieve a transcript' in str(e):
            print("No transcript available in English or Chinese.")


def main():
    while True:
        try:
            # Get URL from user input
            url = input("Please enter a YouTube video URL (or 'q' to quit): ")
            
            # Check if user wants to quit
            if url.lower() == 'q':
                print("Goodbye!")
                break
            
            # Extract video ID and get transcript
            video_id = extract_video_id(url)
            get_transcript(video_id)
            
            # Ask if user wants to continue
            continue_choice = input("\nDo you want to process another video? (y/n): ")
            if continue_choice.lower() != 'y':
                print("Goodbye!")
                break
                
        except ValueError as e:
            print(f"Error: {str(e)}")
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()