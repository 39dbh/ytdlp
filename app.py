import os
import re
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import yt_dlp

app = FastAPI()

# Dockerコンテナ内のマウント先パス
DOWNLOAD_DIR = "/app/downloads"

templates = Jinja2Templates(directory="templates")

def get_yt_dlp_options():
    """
    yt-dlpのオプションを設定
    """
    return {
        # 最高画質の動画と最高音質をマージ、拡張子はmp4を選択
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        
        # 字幕設定
        'writesubtitles': True,             # 字幕をダウンロードする
        'subtitleslangs': ['ja'],           # 日本語字幕を指定
        'subtitlesformat': 'srt/vtt',       # 字幕フォーマット
        
        # 後処理（FFmpegによるマージ）
        'postprocessors': [
            {
                # 動画・音声・字幕をmp4に組み込む（ソフトサブ）
                'key': 'FFmpegEmbedSubtitle',
                'already_have_subtitle': False,
            },
            {
                # 必要に応じてコンテナをmp4に修正
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }
        ],
    }

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": None})

@app.post("/download", response_class=HTMLResponse)
async def download(request: Request, urls: str = Form(...)):
    url_list = [url.strip() for url in re.split(r'[\n,\r]+', urls) if url.strip()]
    
    if not url_list:
        return templates.TemplateResponse("index.html", {"request": request, "message": "URLが入力されていません。"})

    ydl_opts = get_yt_dlp_options()
    success_count = 0
    failed_urls = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in url_list:
            try:
                ydl.download([url])
                success_count += 1
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                failed_urls.append(url)

    result_message = f"処理完了: {success_count}件のダウンロードに成功しました。"
    if failed_urls:
        result_message += f" (失敗: {len(failed_urls)}件)"

    return templates.TemplateResponse("index.html", {"request": request, "message": result_message})
