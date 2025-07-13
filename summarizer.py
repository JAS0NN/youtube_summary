import json
import requests
from typing import Optional, Dict


def get_summary(transcript_content: str, api_key: str, grok: bool = False) -> Optional[Dict]:
    """
    Generate a summary from the transcript content using the selected API.
    Returns the API response JSON as a dict, or None on failure.
    """
    url = "https://api.x.ai/v1/chat/completions" if grok else "https://openrouter.ai/api/v1/chat/completions"
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

### 2. 主要觀點與精華內容（600-800字）
- 提取影片中最重要、最有價值的論點和內容
- 按照邏輯結構（而非時間順序）組織這些觀點
- 對於複雜概念，提供簡潔但完整的解釋
- 保留原始內容中的關鍵數據、統計資料、引用和案例研究
- 識別並強調內容中最具啟發性或轉化性的部分

### 3. 核心洞見深度分析（500-700字）
- 深入分析影片中最有價值的5-7個關鍵洞見
- 解釋每個洞見的實際應用價值和潛在影響
- 將這些洞見與更廣泛的領域知識或趨勢聯繫起來
- 評估這些洞見的獨特性、創新性或實用性
- 探討這些洞見如何改變思維模式或行為方式

### 4. 思維模式與底層原理（400-600字）
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

    model = "grok-4" if grok else "gpt-4o"
    # model = "meta-llama/llama-4-maverick:free"
    data = {
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": transcript_content}
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
        print(f"[Summarizer] Error calling API: {e}")
        return None
