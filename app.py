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

.instagram.com	TRUE	/	TRUE	1786859610	csrftoken	ABCsDuwPtmIJaIpVR5lGlZ
.instagram.com	TRUE	/	TRUE	1786858678	datr	tfRxaIHyNLuIVyFQVTmXmOpF
.instagram.com	TRUE	/	TRUE	1783835605	ig_did	7E7E36B2-860D-41D7-B9C3-FEEAC0314F39
.instagram.com	TRUE	/	TRUE	1752904408	wd	1366x607
.instagram.com	TRUE	/	TRUE	1786858681	mid	aHH0tQALAAEY_JcK3chdiWSFZO5e
.instagram.com	TRUE	/	TRUE	1783834695	ig_nrcb	1
.instagram.com	TRUE	/	TRUE	1783835605	sessionid	75343963355%3Alkm8wlgRZtRWCE%3A18%3AAYcKi_wKYWsS8pFpY_3Rk-6Vah9-uyPwjPtH2lFwTg
.instagram.com	TRUE	/	TRUE	1760075610	ds_user_id	75343963355
.instagram.com	TRUE	/	TRUE	0	rur	"LDC\05475343963355\0541783835610:01fefe95b1e18a1425b5c1b1d50a6d9becc7b406851894e94532baa561a1a873a9224f5c"
"""

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
