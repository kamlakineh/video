from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os, uuid

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Full Instagram cookies embedded in code
cookies_content = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.instagram.com	TRUE	/	TRUE	1780324231	mid	aA4_gAAEAAEVYNNnTW672jqpGR1z
.instagram.com	TRUE	/	TRUE	1780324236	datr	gD8OaJMjm6j4Rs64uTRs-2_-
.instagram.com	TRUE	/	TRUE	1777300276	ig_did	B0C531C9-A11A-4863-A0DC-B638E436A9BD
.instagram.com	TRUE	/	TRUE	1777300240	ig_nrcb	1
.instagram.com	TRUE	/	TRUE	1784300644	ps_l	1
.instagram.com	TRUE	/	TRUE	1784300644	ps_n	1
.instagram.com	TRUE	/	TRUE	1758889095	ds_user_id	75041012555
.instagram.com	TRUE	/	TRUE	1751717885	wd	1366x612
.instagram.com	TRUE	/	TRUE	1785673095	csrftoken	94IVsrOANTbfTTmECFBhWDv2qYvq7pqw
.instagram.com	TRUE	/	TRUE	1782649080	sessionid	75041012555%3A4pNFuwQO4C88Vc%3A24%3AAYd9gs83QvatfBlD3OuUO9_VAh4isjFS0MDI_kejnw
.instagram.com	TRUE	/	TRUE	0	rur	"ODN\05475041012555\0541782649096:01fe1f8a8332fd8eb714c7ef466415db8eaa0b142619a97c260c50ef656cbf8801153a2d""""

# Write cookies.txt on startup
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
