FROM python:3.11-slim

# FFmpeg install karna zaroori hai
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Dependencies install karo
RUN pip install --no-cache-dir -r requirements.txt

# Render / Koyeb dono ke liye flexible port
EXPOSE 10000

CMD ["python", "app.py"]
