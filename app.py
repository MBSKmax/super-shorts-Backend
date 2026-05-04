import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

AUTH_TOKEN = "WORLD2BOLD_SECRET_786"

# RapidAPI Details (Apne Dashboard se copy karein)
RAPIDAPI_KEY = "AAP_KI_RAPIDAPI_KEY_YAHAN_LIKHEIN"
RAPIDAPI_HOST = "tikwm-tiktok-downloader.p.rapidapi.com" # Example host

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    video_url = data.get('url')
    user_token = data.get('token')

    if user_token != AUTH_TOKEN:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if not video_url:
        return jsonify({"success": False, "error": "Link missing!"}), 400

    # RapidAPI Integration
    url = "https://tikwm-tiktok-downloader.p.rapidapi.com/api"
    querystring = {"url": video_url}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        res_data = response.json()

        if res_data.get('code') == 0:
            video_info = res_data.get('data')
            return jsonify({
                "success": True,
                "title": video_info.get('title', 'Super-D Video'),
                "thumbnail": video_info.get('cover', ''),
                "download_url": video_info.get('play', '') # No-watermark link
            })
        else:
            return jsonify({"success": False, "error": "API could not find the video."})

    except Exception as e:
        return jsonify({"success": False, "error": "RapidAPI Connection Failed."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)