import os
import sys
import json
import re
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import datetime

def load_api_keys():
    """
    Load API keys from environment variables or fallback to config/config.json.
    Returns a dict with keys: openai_api_key, grok_api_key, openrouter_api_key.
    """
    keys = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "grok_api_key": os.getenv("GROK_API_KEY"),
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY")
    }

    # Check if any key is missing
    if not all(keys.values()):
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            # Fill missing keys from config file
            for key in keys:
                if not keys[key]:
                    keys[key] = config_data.get(key)
        except FileNotFoundError:
            print(f"Config file not found at {config_path}")
        except json.JSONDecodeError:
            print(f"Config file {config_path} is not valid JSON")
        except Exception as e:
            print(f"Error loading config file: {e}")

    return keys

def extract_video_id(url):
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

def sanitize_filename(filename):
    # Remove invalid characters from filename
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    # Replace spaces with underscores and limit length
    filename = filename.replace(' ', '_')[:200]
    return filename

def get_video_title(video_id):
    try:
        response = requests.get(f'https://www.youtube.com/watch?v={video_id}')
        response.raise_for_status()
        # Extract title from meta tag
        title_match = re.search(r'<meta name="title" content="([^"]+)"', response.text)
        if title_match:
            return sanitize_filename(title_match.group(1))
        return video_id  # Fallback to video ID if title not found
    except requests.exceptions.RequestException as e:
        print(f"Error fetching video page: {e}")
        return video_id
    except Exception as e:
        print(f"Could not get video title: {e}")
        return video_id

def get_transcript(video_id):
    try:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception as e:
            if 'Could not retrieve a transcript' in str(e):
                print("English transcript not available, trying Chinese transcript...")
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'zh-CN', 'zh-TW', 'zh-Hant', 'zh-Hans'])
            else:
                raise e
        
        # Get video title and create filenames
        video_title = get_video_title(video_id)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        transcript_filename = f"{video_title}_{current_date}_transcript.txt"
        
        # Format transcript with timestamps
        formatted_lines = [f"# {video_title}\n\n"]  # Add title as header
        for entry in transcript:
            minutes = int(entry['start'] // 60)
            seconds = int(entry['start'] % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}] "
            formatted_lines.append(f"{timestamp}{entry['text']}\n")
        
        formatted_transcript = ''.join(formatted_lines)
        
        # Create transcript directory if it doesn't exist
        transcript_dir = os.path.join(os.path.dirname(__file__), "transcript")
        if not os.path.exists(transcript_dir):
            os.makedirs(transcript_dir)
            
        transcript_path = os.path.join(transcript_dir, transcript_filename)
        with open(transcript_path, 'w', encoding='utf-8') as file:
            file.write(formatted_transcript)
            
        print(f"Transcript has been saved to {transcript_path}")
        return formatted_transcript, video_title
        
    except Exception as e:
        print(f"An error occurred while getting transcript: {str(e)}")
        if 'Subtitles are disabled for this video' in str(e):
            print("Please make sure the video has subtitles enabled.")
        elif 'Could not retrieve a transcript' in str(e):
            print("No transcript available in English or Chinese.")
        return None, None

def main():
    # Load API keys from env or config
    api_keys = load_api_keys()
    openai_api_key = api_keys.get("openai_api_key")
    grok_api_key = api_keys.get("grok_api_key")
    openrouter_api_key = api_keys.get("openrouter_api_key")

    # 选择 API 平台
    print("请选择要使用的 API 平台：")
    print("1. OpenAI (GPT-4o)")
    print("2. Grok (grok-2-latest)")
    print("3. OpenRouter (openrouter API)")

    while True:
        try:
            choice = input("请输入选择 (1、2 或 3): ")
            if choice == '1':
                use_grok = False
                api_key = openai_api_key
                if not api_key:
                    print("请设置 OpenAI API 密钥")
                    sys.exit(1)
                print("已选择 OpenAI API")
                break
            elif choice == '2':
                use_grok = True
                api_key = grok_api_key
                if not api_key:
                    print("请设置 Grok API 密钥")
                    sys.exit(1)
                print("已选择 Grok API")
                break
            elif choice == '3':
                use_grok = False  # treat as OpenAI-compatible endpoint
                api_key = openrouter_api_key
                if not api_key:
                    print("请设置 OpenRouter API 密钥")
                    sys.exit(1)
                print("已选择 OpenRouter API")
                break
            else:
                print("无效选择，请输入 1、2 或 3")
        except KeyboardInterrupt:
            print("\n程序已退出")
            sys.exit(0)

    while True:
        try:
            url = input("請輸入YouTube影片網址 (或輸入 'q' 退出): ")
            
            if url.lower() == 'q':
                print("程式結束！")
                break
            
            video_id = extract_video_id(url)
            transcript_content, video_title = get_transcript(video_id)
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            if transcript_content and video_title:
                print("\n正在生成摘要...")
                result = get_summary(transcript_content, api_key, grok=use_grok)
                
                if result:
                    try:
                        summary = result['choices'][0]['message']['content']
                        print("\n摘要：")
                        print(summary)
                        
                        summary_filename = f"{current_date}_{video_title}_summary.md"
                        
                        # Create summary directory if it doesn't exist
                        summary_dir = os.path.join(os.path.dirname(__file__), "summary")
                        if not os.path.exists(summary_dir):
                            os.makedirs(summary_dir)
                            
                        summary_path = os.path.join(summary_dir, summary_filename)
                        with open(summary_path, 'w', encoding='utf-8') as f:
                            f.write(summary)
                        print(f"\n摘要已保存到 {summary_path}")
                    except KeyError as e:
                        print(f"Error parsing API response: {e}")
                        print("API response:", json.dumps(result, indent=2, ensure_ascii=False))
            
            print("\n請輸入下一個影片網址，或輸入 'q' 退出")
                
        except ValueError as e:
            print(f"錯誤: {str(e)}")
        except KeyboardInterrupt:
            print("\n程式被使用者中斷。")
            break
        except Exception as e:
            print(f"發生意外錯誤: {str(e)}")

def get_summary(transcript_content, api_key, grok=False):
    if grok:
        url = "https://api.x.ai/v1/chat/completions"
    else:
        url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    sys_prompt = '''
    "# 影片核心洞見與精髓提取專家指南
你是一位頂尖的內容分析專家，擅長從影片文字記錄中提煉核心價值和關鍵洞見，並以結構化、易讀的方式呈現。你的目標是捕捉影片的精髓，而非機械地記錄時間軸。請根據以下指南，對提供的YouTube影片文字記錄進行深度分析和精華提取：

## 分析框架

### 1. 影片核心概述（150-200字）
- 精確識別影片的核心主題和創作意圖
- 簡明扼要地概述影片的主要論點和價值主張
- 識別影片的風格、語調和表達方式
- 如果適用，提及影片的背景脈絡和重要性

### 2. 主要觀點與精華內容（400-600字）
- 提取影片中最重要、最有價值的論點和內容
- 按照邏輯結構（而非時間順序）組織這些觀點
- 對於複雜概念，提供簡潔但完整的解釋
- 保留原始內容中的關鍵數據、統計資料、引用和案例研究
- 識別並強調內容中最具啟發性或轉化性的部分

### 3. 核心洞見深度分析（300-400字）
- 深入分析影片中最有價值的3-5個關鍵洞見
- 解釋每個洞見的實際應用價值和潛在影響
- 將這些洞見與更廣泛的領域知識或趨勢聯繫起來
- 評估這些洞見的獨特性、創新性或實用性
- 探討這些洞見如何改變思維模式或行為方式

### 4. 思維模式與底層原理（200-300字）
- 分析影片中呈現的思維框架和底層原理
- 識別創作者的思考方式和解決問題的方法
- 提取可以應用於不同情境的通用原則
- 探討這些原則如何與其他領域或概念連結

### 5. 實用價值與應用指南（200-300字）
- 基於影片內容，提出具體、可行的應用方法
- 將抽象概念轉化為實際行動步驟
- 提供如何將這些洞見整合到日常生活或工作中的建議
- 推薦相關的延伸資源和進一步探索的方向

## 格式與風格指南

- **語言要求**：使用正式但易懂的繁體中文，避免過度使用專業術語，必要時提供解釋
- **標題格式**：使用Markdown格式，主標題使用#，副標題使用##，小標題使用###
- **段落組織**：使用短段落和項目符號增強可讀性，每個段落聚焦於單一觀點
- **引用處理**：直接引用應使用>符號標記
- **專業性**：保持客觀、中立的語氣，避免過度讚美或批評
- **完整性**：確保摘要能獨立存在，即使讀者沒有觀看原影片也能理解內容
- **深度優先**：優先提供深度洞見和實用價值，而非表面內容的廣泛覆蓋

請記住，你的目標是創建一個有深度、有洞見且實用的影片精華提取，幫助讀者獲取影片中最有價值的思想和知識，而不必關注時間戳或完整的內容時間軸。"
'''
    # 根据选择的 API 平台设置模型
    model = "grok-2-latest" if grok else "gpt-4o"
    
    data = {
        "messages": [
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": transcript_content
            }
        ],
        "model": model,
        "stream": False,
        "temperature": 0.01
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

if __name__ == '__main__':
    main()
