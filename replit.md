# YouTube Video Summarizer

## Overview
This is a YouTube video summarizer web application imported from GitHub that extracts video transcripts and generates AI-powered summaries. The application supports multiple AI platforms (OpenAI, Grok, and OpenRouter) and provides structured summaries in Traditional Chinese through a user-friendly web interface.

## Current State
- **Setup**: Complete and functional web application
- **Dependencies**: Python 3.11 with Flask and all required packages installed
- **Workflow**: Configured as Flask web app running on port 5000
- **Status**: Ready for use via web interface

## Project Architecture
This is a command-line Python application with the following structure:

### Core Components
- `app.py` - Flask web application entry point
- `services/summarize_service.py` - Web service adapter connecting UI to summarization logic
- `web/templates/` - HTML templates for the web interface
- `web/static/` - CSS styling for the web application
- `config/config_manager.py` - Handles API key loading from environment variables or config files
- `transcript_handler.py` - Downloads YouTube video transcripts (English/Chinese)
- `summarizer.py` - Generates AI summaries using various APIs
- `youtube_utils.py` - Utility functions for URL parsing and video title extraction
- `prompt.txt` - Contains the Chinese system prompt for structured summarization
- `youtube_summary.py` - Original CLI version (still available)

### Dependencies
- `flask` - Web framework for the user interface
- `markdown` - Markdown rendering for summaries
- `requests` - HTTP requests for API calls
- `youtube-transcript-api` - YouTube transcript extraction
- `python-dotenv` - Environment variable management
- `ytpy` - YouTube utilities

### Data Flow
1. User visits web interface and enters YouTube video URL
2. User selects AI platform (auto-detected from available API keys)
3. Application extracts video ID and fetches transcript
4. Transcript is sent to selected AI API for summarization
5. Summary is displayed on web page with download options
6. Optional: Files saved to `summary/[date]/[video_title]_summary.md`

## Recent Changes
- **2025-09-12**: Converted CLI application to Flask web application
- **2025-09-12**: Created web interface with URL input form and summary display
- **2025-09-12**: Added download functionality for summaries and transcripts
- **2025-09-12**: Fixed filename sanitization and OpenRouter model configuration
- **2025-09-12**: Set up web workflow running on port 5000

## Configuration
The application requires API keys for the chosen AI service:
- Set environment variables: `OPENAI_API_KEY`, `GROK_API_KEY`, or `OPENROUTER_API_KEY`
- Or create `config/config.json` with the API keys

## Usage
Access the web application through the Replit webview:
1. Open the web interface in your browser
2. Enter a YouTube video URL
3. Select AI platform (auto-detected from available API keys)
4. View the generated summary and transcript
5. Download files or copy content as needed

The original CLI version is still available by running `python youtube_summary.py`