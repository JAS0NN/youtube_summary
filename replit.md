# YouTube Video Summarizer

## Overview
This is a YouTube video summarizer tool imported from GitHub that extracts video transcripts and generates AI-powered summaries. The application supports multiple AI platforms (OpenAI, Grok, and OpenRouter) and provides structured summaries in Traditional Chinese.

## Current State
- **Setup**: Complete and functional
- **Dependencies**: Python 3.11 with all required packages installed
- **Workflow**: Configured for CLI execution with console output
- **Status**: Ready for use

## Project Architecture
This is a command-line Python application with the following structure:

### Core Components
- `youtube_summary.py` - Main application entry point and user interface
- `config/config_manager.py` - Handles API key loading from environment variables or config files
- `transcript_handler.py` - Downloads YouTube video transcripts (English/Chinese)
- `summarizer.py` - Generates AI summaries using various APIs
- `youtube_utils.py` - Utility functions for URL parsing and video title extraction
- `prompt.txt` - Contains the Chinese system prompt for structured summarization

### Dependencies
- `requests` - HTTP requests for API calls
- `youtube-transcript-api` - YouTube transcript extraction
- `python-dotenv` - Environment variable management
- `ytpy` - YouTube utilities

### Data Flow
1. User selects AI platform (OpenAI/Grok/OpenRouter)
2. User inputs YouTube video URL
3. Application extracts video ID and fetches transcript
4. Transcript is sent to selected AI API for summarization
5. Summary is displayed and saved to `summary/[date]/[video_title]_summary.md`

## Recent Changes
- **2025-09-12**: Fixed variable scoping issues in summarizer.py
- **2025-09-12**: Set up Python environment and dependencies
- **2025-09-12**: Configured workflow for CLI execution

## Configuration
The application requires API keys for the chosen AI service:
- Set environment variables: `OPENAI_API_KEY`, `GROK_API_KEY`, or `OPENROUTER_API_KEY`
- Or create `config/config.json` with the API keys

## Usage
Run the application through the configured workflow:
1. Select AI platform (1-3)
2. Enter YouTube video URL
3. Generated summaries are saved to the `summary/` directory