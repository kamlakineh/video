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
                'format': 'mp4',
                'outtmpl': filepath,
                'quiet': True,
                'noplaylist': True
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            result.append({
                "link": url,
                "file": request.host_url + "video/" + filename
            })
        except Exception as e:
            result.append({"link": url, "error": str(e)})

    return jsonify(result)

@app.route("/video/<filename>")
def get_video(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    return send_file(path, mimetype="video/mp4")

if __name__ == "__main__":
    app.run(debug=True)
