import os
import requests
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

AUTH_TOKEN = "WORLD2BOLD_SECRET_786"


@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    video_url = data.get('url')
    user_token = data.get('token')

    if user_token != AUTH_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    ydl_opts = {
        'format':
        'best',
        'quiet':
        True,
        'no_warnings':
        True,
        'user_agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": info.get('url')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    # Koyeb ke default port 8000 ke sath match karne ke liye
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
