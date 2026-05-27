FROM python:3.11-slim

# FFmpegのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存ライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY app.py .
COPY templates/ ./templates/

# ダウンロード先のディレクトリを作成
RUN mkdir -p /app/downloads

EXPOSE 8080

# 起動時に常にyt-dlpを最新に更新してからサーバーを立ち上げる
CMD ["sh", "-c", "pip install -U yt-dlp && uvicorn app.py:app --host 0.0.0.0 --port 8080"]
