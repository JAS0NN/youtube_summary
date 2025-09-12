# YouTube 视频摘要工具

这是一个简单的工具，可以获取YouTube视频的字幕并使用AI生成摘要。

## 功能

- 从YouTube视频URL获取字幕
- 使用多种AI API生成摘要（OpenAI、Grok、OpenRouter）
- 保存摘要到本地文件

## 安装

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`

## API密钥设置

在项目根目录创建一个`.env`文件，添加以下内容：

```
# API Keys for various services
OPENAI_API_KEY=你的OpenAI密钥
GROK_API_KEY=你的Grok密钥
OPENROUTER_API_KEY=你的OpenRouter密钥
```

**注意事项：**

- OpenAI API密钥应以`sk-`开头，不是`sk-proj-`
- 确保API密钥有效且有足够的额度

## 使用方法

运行主程序：

```
python youtube_summary.py
```

1. 选择要使用的API平台（1、2或3）
2. 输入YouTube视频URL
3. 等待摘要生成

摘要将显示在控制台并保存到`summary/日期/视频标题_summary.md`文件中。

## 故障排除

- 如果遇到API密钥错误，请检查`.env`文件中的密钥是否正确
- 对于OpenAI API，确保使用的是正确格式的密钥（以`sk-`开头）
- 如果网络连接有问题，请检查您的网络设置或代理配置