import os
import yt_dlp
import random
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv() # .env load karega

app = Flask(__name__)
CORS(app)

AUTH_TOKEN = os.getenv("AUTH_TOKEN") # Vault se token uthayega

def keep_alive():
    while True:
        try:
            # Render ko jagaye rakhne ke liye self-ping
            time.sleep(600) 
        except: pass

threading.Thread(target=keep_alive, daemon=True).start()

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    video_url = data.get('url')
    user_token = data.get('token')

    if user_token != AUTH_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Referer': 'https://www.tiktok.com/',
        },
        'extractor_args': {
            'tiktok': {
                'web_id': f"{random.randint(7000000000000000000, 7999999999999999999)}"
            }
        }
    }

    # Agar GitHub pe cookies.txt dali hai toh ye usay use karega
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # TikTok/Insta ke liye best direct link nikalna
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                # Filter to get the best video format with audio
                formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                download_url = formats[-1]['url'] if formats else info['formats'][-1]['url']

            return jsonify({
                "success": True,
                "title": info.get('title', 'Super-D Media'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url
            })

    except Exception as e:
        return jsonify({"success": False, "error": f"Platform Blocked or Link Invalid"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))