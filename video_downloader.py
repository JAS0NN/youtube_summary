import os
import yt_dlp

def download_youtube_video(url: str, save_path: str):
    os.makedirs(save_path, exist_ok=True)
    ydl_opts = {
        # 檔名格式：影片標題.副檔名
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        # 選擇最高畫質影片 + 最佳音訊，自動合併成 mp4
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=PBEjlCJPXgE"
    save_path = "./downloads"
    download_youtube_video(url, save_path)
