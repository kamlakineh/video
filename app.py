from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os, uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/download', methods=['POST'])
def download_videos():
    data = request.get_json()
    links = data.get("links", [])
    result = []

    for url in links:
        try:
            filename = str(uuid.uuid4()) + ".mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': filepath,
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': 'mp4',
                'force_generic_extractor': False,
                # You can optionally use:
                # 'cookiesfrombrowser': ('chrome',),  # for Instagram login-required videos
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                thumbnail = info.get("thumbnail", "")

            result.append({
                "link": url,
                "file": request.host_url + "video/" + filename,
                "thumbnail": thumbnail
            })

        except Exception as e:
            result.append({
                "link": url,
                "error": str(e)
            })

    return jsonify(result)

@app.route("/video/<filename>")
def get_video(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path, mimetype="video/mp4")
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render-compatible
    app.run(host="0.0.0.0", port=port)
