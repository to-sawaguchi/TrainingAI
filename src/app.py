# coding: utf-8

#　必要なモジュールのインポート
from flask import Flask, render_template, Response
from camera import Camera  # カメラ制御コードのインポート
import cv2

# app という変数でFlaskオブジェクトをインスタンス化
app = Flask(__name__)

# --- View側の設定 ---
# ルートディレクトリにアクセスした場合の挙動
@app.route('/')
# def以下がアクセス後の操作
def index():
    return render_template('index.html')

@app.route('/run_python_file')
def run_python_file():
    # result = subprocess.run(['python', 'training.py'], capture_output=True, text=True)
    # output = result.stdout
    # return f'Pythonファイルを実行しました\n出力: {output}'
    message = 'Pythonファイルを実行しました'
    return message

@app.route("/stream")
def stream():
    return render_template("stream.html")

def gen(camera):
    while True:
        frame = camera.get_frame()

        if frame is not None:
            yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame.tobytes() + b"\r\n")
        else:
            print("frame is none")

@app.route("/video_feed")
def video_feed():
    return Response(gen(Camera()),
            mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    app.run()