import os
import yt_dlp
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Security Token
AUTH_TOKEN = "WORLD2BOLD_SECRET_786"

# Advanced Browser Masks (User-Agents)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1"
]

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    video_url = data.get('url')
    user_token = data.get('token')

    if user_token != AUTH_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized Access"}), 403

    # Dynamic Masking Settings
    selected_ua = random.choice(USER_AGENTS)
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extract_flat': True,
        'skip_download': True,
        # Proxy Masking (Agar aapke paas proxy ho toh yahan add hoti hai)
        'http_headers': {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraction logic with error retry mask
            info = ydl.extract_info(video_url, download=False)
            
            # Formats selection mask
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                # Filter for best quality mp4
                formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                download_url = formats[-1]['url'] if formats else info['formats'][-1]['url']

            return jsonify({
                "success": True,
                "title": info.get('title', 'Super-D Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url,
                "mask_used": "Global-Secure-V2"
            })
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            return jsonify({"success": False, "error": "Platform Blocked Request. Try again in 1 minute."})
        return jsonify({"success": False, "error": "Invalid Link or Server Timeout."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)