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

    print("请选择要使用的 API 平台：")
    print("1. OpenAI (GPT-4o)")
    print("2. Grok (grok-3)")
    print("3. OpenRouter (openrouter API)")

    selected_model = None  # Default for non-OpenRouter cases

    while True:
        try:
            choice = input("请输入选择 (1、2 或 3): ")
            if choice == '1':
                use_grok = False
                use_openai = True
                api_key = openai_api_key
                if not api_key:
                    print("请设置 OpenAI API 密钥")
                    print("您可以在 .env 文件中添加 OPENAI_API_KEY=您的密钥")
                    print("OpenAI API 密钥应以 'sk-' 开头，不是 'sk-proj-'")
                    sys.exit(1)
                print("已选择 OpenAI API")
                break
            elif choice == '2':
                use_grok = True
                use_openai = False
                api_key = grok_api_key
                if not api_key:
                    print("请设置 Grok API 密钥")
                    print("您可以在 .env 文件中添加 GROK_API_KEY=您的密钥")
                    sys.exit(1)
                print("已选择 Grok API")
                break
            elif choice == '3':
                use_grok = False
                use_openai = False
                api_key = openrouter_api_key
                if not api_key:
                    print("请设置 OpenRouter API 密钥")
                    print("您可以在 .env 文件中添加 OPENROUTER_API_KEY=您的密钥")
                    sys.exit(1)
                print("已选择 OpenRouter API")

                # Ask user to input model name for OpenRouter
                print("\n请输入要使用的模型名称 (例如: openai/gpt-4o, anthropic/claude-3.5-sonnet, meta-llama/llama-3.1-405b-instruct):")
                while True:
                    try:
                        selected_model = input("模型名称: ").strip()
                        if selected_model:
                            print(f"已选择模型: {selected_model}")
                            break
                        else:
                            print("请输入有效的模型名称")
                    except KeyboardInterrupt:
                        print("\n程序已退出")
                        sys.exit(0)
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
                result = get_summary(transcript_content, api_key, grok=use_grok, use_openai=use_openai, openrouter_model=selected_model)

                if result:
                    try:
                        summary = result['choices'][0]['message']['content']
                        print("\n摘要：")
                        print(summary)

                        summary_filename = f"{current_date}_{video_title}_summary.md"
                        summary_dir = os.path.join(os.path.dirname(__file__), "summary", current_date)
                        if not os.path.exists(summary_dir):
                            os.makedirs(summary_dir)
                        summary_path = os.path.join(summary_dir, summary_filename)
                        with open(summary_path, 'w', encoding='utf-8') as f:
                            f.write(summary)
                        print(f"\n摘要已保存到 {summary_path}")
                    except KeyError as e:
                        print(f"解析API响应时出错: {e}")
                        print("API响应:", json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print("API调用失败，请检查错误信息并确保您的API密钥正确。")
            print("\n請輸入下一個影片網址，或輸入 'q' 退出")

        except ValueError as e:
            print(f"錯誤: {str(e)}")
        except KeyboardInterrupt:
            print("\n程式被使用者中斷。")
            break
        except Exception as e:
            print(f"發生意外錯誤: {str(e)}")


if __name__ == "__main__":
    main()
