import os
import sys
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from openai import OpenAI
from dotenv import load_dotenv
import uuid
from flask import g
import subprocess  # ExifTool用

# original ディレクトリを PYTHONPATH に追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# これで同じフォルダ内の db.py をインポート可能
from db import init_db, insert_report, get_all_reports, close_db

# 環境変数ロード
load_dotenv("/Users/project-t4/Desktop/llmdev/.env")
os.environ['OPENAI_API_KEY'] = os.environ.get('API_KEY')

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Flask終了時にDB接続を閉じる
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

# DB初期化
init_db()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL_NAME = "gpt-4o-mini"

# --- ExifToolでGPS取得（HEIC/JPEG対応） ---
def get_exif_gps(photo_path):
    try:
        result = subprocess.run(
            ["exiftool", "-n", "-GPSLatitude", "-GPSLongitude", photo_path],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip().split("\n")
        lat = lon = None
        for line in output:
            if "GPS Latitude" in line:
                lat = float(line.split(":")[1].strip())
            if "GPS Longitude" in line:
                lon = float(line.split(":")[1].strip())
        if lat is not None and lon is not None:
            return lat, lon
    except Exception as e:
        print(f"ExifTool GPS取得失敗: {photo_path} / {e}")
    return None, None

# --- トップページ ---
@app.route("/")
def index():
    return render_template("index.html")

# --- AIチャット ---
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.form.get("message", "")
    if not user_msg:
        return jsonify({"reply": "メッセージが空です。"})
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": user_msg}],
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

# --- 現場報告（チャット＋写真＋GPS） ---
@app.route("/report_chat", methods=["POST"])
def report_chat():
    message = request.form.get("message", "")
    latitude = request.form.get("latitude", None)
    longitude = request.form.get("longitude", None)
    photo_file = request.files.get("photo")
    photo_url = None
    unique_name = None

    if photo_file:
        filename = secure_filename(photo_file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(app.root_path, "static", "uploads", unique_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        photo_file.save(save_path)
        photo_url = f"/static/uploads/{unique_name}"

        if not latitude or not longitude:
            lat, lon = get_exif_gps(save_path)
            if lat is not None and lon is not None:
                latitude = str(lat)
                longitude = str(lon)

    insert_report(unique_name if unique_name else None,
                  latitude if latitude else None,
                  longitude if longitude else None)

    map_link = f"https://www.google.com/maps?q={latitude},{longitude}" \
               if latitude and longitude else None

    if message:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": message}],
        )
        reply = response.choices[0].message.content
    else:
        reply = "報告を受け付けました。"

    return jsonify({
        "reply": reply,
        "photo_path": photo_url,
        "map_link": map_link
    })

# --- 管理画面 ---
@app.route("/admin")
def admin():
    reports = get_all_reports()
    return render_template("admin.html", reports=reports)

if __name__ == "__main__":
    import socket
    import sys

    # カレントディレクトリを PYTHONPATH に追加
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

    def find_free_port(start=5000, end=5100):
        for port in range(start, end):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("空いているポートが見つかりません")

    port = find_free_port()
    print(f"Flask をポート {port} で起動します")
    app.run(debug=True, port=port)