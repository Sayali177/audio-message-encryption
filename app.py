from flask import Flask, request, jsonify,send_file
from chaos_audio import encrypt_message_to_audio, decrypt_audio_to_message
import os


app = Flask(__name__)

UPLOAD_FOLDER = "/tmp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return send_file("index.html")

# Encrypt API
@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    message = data.get("message")
    x0 = float(data.get("x0"))
    r = float(data.get("r"))

    filename = os.path.join(UPLOAD_FOLDER, "output.wav")

    encrypt_message_to_audio(message, filename, x0, r)

    return send_file(filename, as_attachment=True)

# Decrypt API
@app.route("/decrypt", methods=["POST"])
def decrypt():
    file = request.files.get("file")
    x0 = float(request.form.get("x0"))
    r = float(request.form.get("r"))

    filepath = os.path.join(UPLOAD_FOLDER, f"input_{os.getpid()}.wav")
    file.save(filepath)

    message, info = decrypt_audio_to_message(filepath, x0, r)

    return jsonify({
        "message": message,
        "info": info
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)