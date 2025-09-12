"""
YouTube Video Summarizer Web Application
Flask web interface for the YouTube summarization tool.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import markdown
import bleach
from services.summarize_service import summarize_youtube_url, get_available_providers

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

# Security: Require SECRET_KEY environment variable in production
if os.environ.get('FLASK_ENV') == 'production' and not os.environ.get('SECRET_KEY'):
    raise ValueError("SECRET_KEY environment variable must be set in production")

app.secret_key = os.environ.get('SECRET_KEY', 'youtube-summarizer-dev-key')

# Configure bleach for safe HTML sanitization
# Allow common markdown HTML tags while preventing XSS
ALLOWED_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'br', 'strong', 'em', 'u', 'code', 'pre',
    'ul', 'ol', 'li', 'blockquote',
    'a', 'img'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title']
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks while preserving markdown formatting."""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )

@app.route('/')
def index():
    """Main page with YouTube URL input form."""
    providers = get_available_providers()
    
    # Determine default provider (prefer OpenAI, then Grok, then OpenRouter)
    default_provider = None
    if providers['openai']:
        default_provider = 'openai'
    elif providers['grok']:
        default_provider = 'grok'
    elif providers['openrouter']:
        default_provider = 'openrouter'
    
    return render_template('index.html', 
                         providers=providers, 
                         default_provider=default_provider)

@app.route('/summarize', methods=['POST'])
def summarize():
    """Process YouTube URL and generate summary."""
    url = request.form.get('url', '').strip()
    provider = request.form.get('provider', '').strip()
    save_files = 'save_files' in request.form
    
    # Basic validation
    if not url:
        flash('Please enter a YouTube URL', 'error')
        return redirect(url_for('index'))
    
    if not provider:
        flash('Please select an AI provider', 'error')
        return redirect(url_for('index'))
    
    # Check if provider is available
    providers = get_available_providers()
    if not providers.get(provider, False):
        flash(f'{provider.title()} API key not configured', 'error')
        return redirect(url_for('index'))
    
    # Process the summarization
    result = summarize_youtube_url(url, provider, save_files)
    
    if result['success']:
        # Convert summary markdown to HTML and sanitize to prevent XSS
        raw_html = markdown.markdown(result['data']['summary'])
        summary_html = sanitize_html(raw_html)
        
        return render_template('result.html',
                             video_title=result['data']['video_title'],
                             video_id=result['data']['video_id'],
                             summary_html=summary_html,
                             summary_text=result['data']['summary'],
                             provider=result['data']['provider'],
                             transcript_content=result['data']['transcript_content'])
    else:
        # Handle different error types with appropriate messages
        error_type = result.get('error_type', 'system')
        error_message = result['error']
        
        if error_type == 'validation':
            flash(f'Invalid URL: {error_message}', 'error')
        elif error_type == 'configuration':
            flash(error_message, 'error')
        elif error_type == 'transcript':
            flash(error_message, 'warning')
        elif error_type == 'api':
            flash(error_message, 'error')
        else:
            flash(f'Error: {error_message}', 'error')
        
        return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'youtube-summarizer'})

if __name__ == '__main__':
    # Configure for Replit environment
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting YouTube Summarizer Web App on {host}:{port}")
    app.run(host=host, port=port, debug=debug)