from flask import Flask, request, jsonify, send_from_directory
import yt_dlp, os, uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get("url")
    dtype = data.get("type", "mp4")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    filename = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_FOLDER, filename + ".%(ext)s")

    ydl_opts = {
        "quiet": True,
        "outtmpl": outtmpl,
        "merge_output_format": "mp4" if dtype == "mp4" else None
    }

    if dtype == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # find the actual file
        for f in os.listdir(DOWNLOAD_FOLDER):
            if f.startswith(filename):
                return jsonify({"file": f"/{DOWNLOAD_FOLDER}/{f}"})
        return jsonify({"error": "File not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
