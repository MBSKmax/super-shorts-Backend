# Python ka lightweight version use kar rahe hain
FROM python:3.9-slim

# FFmpeg install karna zaroori hai taake yt-dlp video/audio ko merge kar sakay
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Server ke andar folder banana
WORKDIR /app

# Sab files ko server mein copy karna
COPY . .

# Libraries install karna
RUN pip install --no-cache-dir -r requirements.txt

# Koyeb default port 8080 use karta hai
EXPOSE 8000

# App ko start karne ki command
CMD ["python", "app.py"]