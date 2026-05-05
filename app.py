import os
import yt_dlp
import random
import threading
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

AUTH_TOKEN = "WORLD2BOLD_SECRET_786"

# 1. SLEEP ISSUE FIX: Self-Ping Logic
def keep_alive():
    while True:
        try:
            # Apni hi URL ko ping karo (Render URL yahan daal dena)
            # Example: requests.get("https://your-app-name.onrender.com/")
            time.sleep(600) # Har 10 min baad
        except:
            pass

# Backend start hote hi pinging shuru
threading.Thread(target=keep_alive, daemon=True).start()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

# 2. DURATION FILTER (Up to 100 seconds)
def shorts_filter(info_dict, *, incomplete):
    duration = info_dict.get('duration')
    if duration and duration > 100: # 1:40 tak allow hai
        return "Video is too long. Max 100s allowed!"
    return None

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    video_url = data.get('url')
    user_token = data.get('token')

    if user_token != AUTH_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    ydl_opts = {
        'format': 'best',
        'match_filter': shorts_filter,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }
    }

    # Cookies Check
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "Extraction Failed"})

            # Link Extraction Logic
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                combined = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                download_url = combined[-1]['url'] if combined else info['formats'][-1]['url']

            return jsonify({
                "success": True,
                "title": info.get('title', 'Super-D Media'),
                "thumbnail": info.get('thumbnail', ''),
                "duration": info.get('duration'),
                "download_url": download_url
            })

    except Exception as e:
        error_str = str(e)
        if "too long" in error_str:
            return jsonify({"success": False, "error": "Video lambi hai (Max 1:40 mins)!"})
        return jsonify({"success": False, "error": "Link blocked or Invalid."})

# Home route for Self-Ping
@app.route('/')
def home():
    return "Server is Awake! 🚀"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)