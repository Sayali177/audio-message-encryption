# EchoCrypt

**Secure Audio Encryption & Decryption System**

EchoCrypt is a zero-knowledge, end-to-end encrypted web application that lets you securely encrypt and decrypt secret messages and audio files directly in your browser. All processing happens locally on your device without communicating with any external server.

---

## 🔒 Features

- **Send Encrypted Messages/Audio**: Type a secret text message or drag-and-drop an audio file (`.wav`, `.mp3`, `.ogg`) to securely lock it down.
- **Read Encrypted Messages**: Paste your encrypted cipher blob or upload an `.enc`/audio file along with your shared password to unlock and read/listen.
- **In-Memory Vault**: Keep a live registry of the files you have encrypted or decrypted during the active session.
- **Zero-Knowledge Architecture**: The Web Crypto API handles everything locally. Your password, unencrypted files, and plain text never leave your device.
- **Secure Exit**: Safely wipe all temporary data, derived keys, and decrypted content from the browser memory instantly.

---

## 🛡️ Technical Specifications & Cryptography

EchoCrypt uses state-of-the-art encryption algorithms available in the modern browser via the Web Crypto API:

- **Cipher**: `AES-256-GCM` (Provides authenticated encryption, tampering automatically detected)
- **Key Derivation (KDF)**: `PBKDF2-HMAC-SHA-256`
- **Iterations**: `100,000` computation rounds
- **Salt Size**: `128-bit` (Random salt generated per encryption)
- **Initialization Vector (IV/Nonce)**: `96-bit` (Randomly generated per message)
- **Authentication Tag**: `128-bit` (GCM)

---

## 🚀 How to Run

Because of browser security policies (especially regarding the Web Crypto API module), it is best to run this file via a local web server rather than opening it as a static `file://`.

### Running Locally

1. Open your terminal in the project directory.
2. Start a simple Python local web server:
   ```bash
   python3 -m http.server 8000
   ```
3. Open your favorite web browser and navigate to:
   ```text
   http://localhost:8000/
   ```

### Requirements

- A modern browser that supports the **Web Crypto API** (Chrome, Firefox, Safari 15+, Edge).

---

## 📖 How It Works

1. **Compose**: You input a message or attach an audio file. Everything stays local.
2. **Key Derivation**: Your chosen passphrase is mixed with a randomly generated 16-byte salt and put through PBKDF2 (100,000 rounds) to generate a robust 256-bit AES key.
3. **Encryption (AES-GCM)**: The data is encrypted using the derived key and a unique, random 12-byte IV for every message. 
4. **Transport Mode**: The result is packaged into a Base64-encoded string prefixed with `EC1:`. This string (or the downloadable `.enc` file) is perfectly safe to be transferred over emails, chats, or unencrypted mediums.
5. **Decryption**: To read the message or listen to the file, the recipient provides the ciphertext and the passphrase, reversing the process natively and securely within their browser.
