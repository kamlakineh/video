from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os, uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Embed your cookies content as a multi-line string inside the code
cookies_content = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.instagram.com	TRUE	/	TRUE	1780324231	mid	aA4_gAAEAAEVYNNnTW672jqpGR1z
.instagram.com	TRUE	/	TRUE	1780324236	datr	gD8OaJMjm6j4Rs64uTRs-2_-
.instagram.com	TRUE	/	TRUE	1777300276	ig_did	B0C531C9-A11A-4863-A0DC-B638E436A9BD
.instagram.com	TRUE	/	TRUE	1777300240	ig_nrcb	1
.instagram.com	TRUE	/	TRUE	1784300644	ps_l	1
.instagram.com	TRUE	/	TRUE	1784300644	ps_n	1
.instagram.com	TRUE	/	TRUE	1751051700	wd	1366x612
.instagram.com	TRUE	/	TRUE	1785006976	csrftoken	iA6fSf5pSUoHtx5nEA2XEjkGuNTPHzQb
.instagram.com	TRUE	/	TRUE	1781982882	sessionid	75041012555%3Ak7KqUd7ph09vKa%3A18%3AAYcl-Lmklm0bdJ17UBks39ftr0Sc7z5XDM4QEyU-Kg
.instagram.com	TRUE	/	TRUE	1758222976	ds_user_id	75041012555
.instagram.com	TRUE	/	TRUE	0	rur	"ODN\05475041012555\0541781982975:01fe5a959c9508f0d0fd8d6dcc52e12381d2df54522e0151e342982415dcaa9d7756f08e"""

# Write the cookies content to cookies.txt when the app starts
with open("cookies.txt", "w") as f:
    f.write(cookies_content)

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
                'cookiefile': 'cookies.txt',
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
