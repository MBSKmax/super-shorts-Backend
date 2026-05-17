import os
import yt_dlp
import random
import threading
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "WORLD2BOLD_SECRET_786")
SELF_URL = os.getenv("RENDER_EXTERNAL_URL", "")

# ─── Keep-Alive (Render ko jagaye rakhne ke liye) ───────────────────────────
def keep_alive():
    while True:
        try:
            time.sleep(600)
            if SELF_URL:
                requests.get(f"{SELF_URL}/health", timeout=10)
        except Exception:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ─── Health Check ────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive", "service": "Super-D Hub Backend"})

# ─── Platform Detection ───────────────────────────────────────────────────────
def detect_platform(url):
    url = url.lower()
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'tiktok.com' in url or 'vm.tiktok' in url:
        return 'tiktok'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'facebook.com' in url or 'fb.watch' in url or 'fb.com' in url:
        return 'facebook'
    elif 'twitter.com' in url or 'x.com' in url or 't.co' in url:
        return 'twitter'
    elif 'pinterest.com' in url or 'pin.it' in url:
        return 'pinterest'
    elif 'snapchat.com' in url:
        return 'snapchat'
    elif 'linkedin.com' in url:
        return 'linkedin'
    else:
        return 'generic'

# ─── yt-dlp Options (Platform ke hisaab se) ─────────────────────────────────
def get_ydl_opts(platform):
    base = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
    }

    # Cookies add karo agar file exist karti hai
    if os.path.exists('cookies.txt'):
        base['cookiefile'] = 'cookies.txt'

    if platform == 'youtube':
        base.update({
            'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
            'http_headers': {
                'User-Agent': (
                    'com.google.ios.youtube/19.29.1 '
                    '(iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X)'
                ),
            },
        })

    elif platform == 'tiktok':
        base.update({
            'format': 'best',
            'http_headers': {
                'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
                'Referer': 'https://www.tiktok.com/',
            },
            'extractor_args': {
                'tiktok': {
                    'web_id': str(random.randint(7_000_000_000_000_000_000,
                                                 7_999_999_999_999_999_999))
                }
            },
        })

    elif platform == 'instagram':
        base.update({
            'format': 'best',
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                ),
                'Referer': 'https://www.instagram.com/',
            },
        })

    elif platform == 'facebook':
        base.update({
            'format': 'best[ext=mp4]/best',
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                ),
            },
        })

    elif platform == 'twitter':
        base.update({
            'format': 'best[ext=mp4]/best',
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                ),
            },
        })

    elif platform == 'pinterest':
        base.update({
            'format': 'best',
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                ),
            },
        })

    else:
        # Generic / Snapchat / LinkedIn / baaki sab
        base.update({
            'format': 'best[ext=mp4]/best',
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                ),
            },
        })

    return base

# ─── Best Download URL Extract Karna ─────────────────────────────────────────
def get_best_url(info):
    # Direct URL
    if info.get('url'):
        return info['url']

    formats = info.get('formats', [])
    if not formats:
        return None

    # Video + Audio dono wale (combined) formats prefer karo
    combined = [
        f for f in formats
        if f.get('vcodec') not in (None, 'none')
        and f.get('acodec') not in (None, 'none')
        and f.get('url')
    ]

    if combined:
        # Height ke hisaab se best
        best = max(combined, key=lambda f: f.get('height', 0) or 0)
        return best['url']

    # Koi bhi URL wala format
    with_url = [f for f in formats if f.get('url')]
    return with_url[-1]['url'] if with_url else None

# ─── Main Extract Endpoint ────────────────────────────────────────────────────
@app.route('/extract', methods=['POST'])
def extract():
    data = request.json or {}
    video_url = data.get('url', '').strip()
    user_token = data.get('token', '')

    # Auth check
    if user_token != AUTH_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if not video_url:
        return jsonify({"success": False, "error": "URL required"}), 400

    platform = detect_platform(video_url)
    base_opts = get_ydl_opts(platform)
    last_error = None

    # YouTube ke liye teen alag clients try karo (iOS → Android → Web)
    if platform == 'youtube':
        client_list = [
            ['ios'],
            ['android'],
            ['web'],
        ]
    else:
        client_list = [None]  # Baaki platforms ke liye ek hi try

    for client in client_list:
        try:
            opts = base_opts.copy()

            if client:
                opts['extractor_args'] = {
                    'youtube': {
                        'player_client': client,
                        'player_skip': ['webpage'],
                    }
                }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                download_url = get_best_url(info)

                if download_url:
                    return jsonify({
                        "success": True,
                        "title": info.get('title', 'Super-D Media'),
                        "thumbnail": info.get('thumbnail', ''),
                        "download_url": download_url,
                        "platform": platform,
                        "duration": info.get('duration', 0),
                    })

        except Exception as e:
            last_error = str(e)
            continue  # Agla client try karo

    # Sab try ho gaye, ab bhi fail
    return jsonify({
        "success": False,
        "error": "Link extract nahi ho saka. Dobara try karein.",
        "detail": last_error
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
