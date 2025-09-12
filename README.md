# YouTube 影片摘要工具

這是一個簡單的工具，可以獲取YouTube影片的字幕並使用AI生成摘要。

## 功能

- 從YouTube影片URL獲取字幕
- 使用多種AI API生成摘要（OpenAI、Grok、OpenRouter）
- 保存摘要到本地文件

## 安裝

1. 克隆倉庫
2. 安裝依賴：`pip install -r requirements.txt`

## API密鑰設置

在項目根目錄創建一個`.env`文件，添加以下內容：

```
# API Keys for various services
OPENAI_API_KEY=你的OpenAI密鑰
GROK_API_KEY=你的Grok密鑰
OPENROUTER_API_KEY=你的OpenRouter密鑰
```

**注意事項：**

- OpenAI API密鑰應以`sk-`開頭，不是`sk-proj-`
- 確保API密鑰有效且有足夠的額度

## 使用方法

運行主程序：

```
python youtube_summary.py
```

1. 選擇要使用的API平台（1、2或3）
2. 輸入YouTube影片URL
3. 等待摘要生成

摘要將顯示在控制台並保存到`summary/日期/影片標題_summary.md`文件中。

## 故障排除

- 如果遇到API密鑰錯誤，請檢查`.env`文件中的密鑰是否正確
- 對於OpenAI API，確保使用的是正確格式的密鑰（以`sk-`開頭）
- 如果網絡連接有問題，請檢查您的網絡設置或代理配置