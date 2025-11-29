import sys
import os
import datetime
import json

from config.config_manager import load_api_keys
from youtube_utils import extract_video_id
from transcript_handler import get_transcript
from summarizer import get_summary


def main():
    api_keys = load_api_keys()
    openai_api_key = api_keys.get("openai_api_key")
    grok_api_key = api_keys.get("grok_api_key")
    openrouter_api_key = api_keys.get("openrouter_api_key")

    print("Please select the API platform:")
    print("1. OpenAI (gpt-5.1)")
    print("2. Grok (grok-4-1-fast-non-reasoning)")
    print("3. OpenRouter (openrouter API)")

    selected_model = None  # Default for non-OpenRouter cases

    while True:
        try:
            choice = input("Please enter your choice (1, 2, or 3): ")
            if choice == '1':
                use_grok = False
                use_openai = True
                api_key = openai_api_key
                if not api_key:
                    print("Please set OpenAI API key")
                    print("You can add OPENAI_API_KEY=your_key in the .env file")
                    print("OpenAI API key should start with 'sk-', not 'sk-proj-'")
                    sys.exit(1)
                print("OpenAI API selected")
                break
            elif choice == '2':
                use_grok = True
                use_openai = False
                api_key = grok_api_key
                if not api_key:
                    print("Please set Grok API key")
                    print("You can add GROK_API_KEY=your_key in the .env file")
                    sys.exit(1)
                print("Grok API selected")
                break
            elif choice == '3':
                use_grok = False
                use_openai = False
                api_key = openrouter_api_key
                if not api_key:
                    print("Please set OpenRouter API key")
                    print("You can add OPENROUTER_API_KEY=your_key in the .env file")
                    sys.exit(1)
                print("OpenRouter API selected")

                # Ask user to input model name for OpenRouter
                print("\nPlease enter the model name (e.g., openai/gpt-5.1, anthropic/claude-3.5-sonnet, meta-llama/llama-3.1-405b-instruct):")
                while True:
                    try:
                        selected_model = input("Model name: ").strip()
                        if selected_model:
                            print(f"Model selected: {selected_model}")
                            break
                        else:
                            print("Please enter a valid model name")
                    except KeyboardInterrupt:
                        print("\nProgram exited")
                        sys.exit(0)
                break
            else:
                print("Invalid choice, please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nProgram exited")
            sys.exit(0)

    while True:
        try:
            url = input("Please enter YouTube video URL (or enter 'q' to quit): ")
            if url.lower() == 'q':
                print("Program ended!")
                break

            video_id = extract_video_id(url)
            transcript_content, video_title = get_transcript(video_id)
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')

            if transcript_content and video_title:
                print("\nGenerating summary...")
                result = get_summary(transcript_content, api_key, grok=use_grok, use_openai=use_openai, openrouter_model=selected_model)

                if result:
                    try:
                        summary = result['choices'][0]['message']['content']
                        print("\nSummary:")
                        print(summary)

                        summary_filename = f"{current_date}_{video_title}_summary.md"
                        summary_dir = os.path.join(os.path.dirname(__file__), "summary", current_date)
                        if not os.path.exists(summary_dir):
                            os.makedirs(summary_dir)
                        summary_path = os.path.join(summary_dir, summary_filename)
                        with open(summary_path, 'w', encoding='utf-8') as f:
                            f.write(summary)
                        print(f"\nSummary saved to {summary_path}")
                    except KeyError as e:
                        print(f"Error parsing API response: {e}")
                        print("API response:", json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print("API call failed, please check error messages and ensure your API key is correct.")
            print("\nPlease enter the next video URL, or enter 'q' to quit")

        except ValueError as e:
            print(f"Error: {str(e)}")
        except KeyboardInterrupt:
            print("\nProgram interrupted by user.")
            break
        except Exception as e:
            print(f"Unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
