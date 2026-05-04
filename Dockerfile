FROM python:3.9-slim

# FFmpeg install karna zaroori hai
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Force install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Koyeb port 8000 expect karta hai
EXPOSE 8000

CMD ["python", "app.py"]