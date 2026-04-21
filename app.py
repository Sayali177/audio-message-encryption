from flask import Flask, request, jsonify
from chaos_audio import encrypt_message_to_audio, decrypt_audio_to_message
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "EchoCrypt Backend Running"

# Encrypt API
@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    message = data.get("message")
    x0 = float(data.get("x0"))
    r = float(data.get("r"))

    filename = os.path.join(UPLOAD_FOLDER, "output.wav")

    encrypt_message_to_audio(message, filename, x0, r)

    return jsonify({"status": "success", "file": "output.wav"})

# Decrypt API
@app.route("/decrypt", methods=["POST"])
def decrypt():
    data = request.json
    x0 = float(data.get("x0"))
    r = float(data.get("r"))

    filepath = os.path.join(UPLOAD_FOLDER, "output.wav")

    message, info = decrypt_audio_to_message(filepath, x0, r)

    return jsonify({"message": message, "info": info})

if __name__ == "__main__":
    app.run(debug=True)