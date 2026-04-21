import numpy as np
from scipy.io import wavfile
import os
import sys
import datetime

# =====================================================
#           CORE ENCRYPTION ENGINE
# =====================================================

def generate_logistic_map(length, x0, r):
    """
    Generates chaotic sequence using Logistic Map.
    Even tiny key differences produce completely different sequences.
    """
    x = np.zeros(length)
    x[0] = x0
    for i in range(length - 1):
        x[i+1] = r * x[i] * (1 - x[i])
    return x

def generate_chaotic_key(length, x0, r):
    """
    Converts logistic map output into usable XOR key bytes.
    """
    raw_key = generate_logistic_map(length, x0, r)
    key = (raw_key * 255).astype(np.uint8)
    return key

# =====================================================
#           ENCRYPTION FUNCTIONS
# =====================================================

def encrypt_message_to_audio(message, output_filename, x0, r):
    """
    Takes a text message and encrypts it into a WAV audio file.
    
    HOW IT WORKS:
    1. Convert text → bytes
    2. Add metadata (timestamp + length info)
    3. Generate chaotic key using x0 and r
    4. XOR message bytes with chaotic key
    5. Embed encrypted bytes into audio samples
    6. Save as WAV file (sounds like random noise)
    
    Parameters:
        message         : The secret text message to encrypt
        output_filename : Name of output WAV file
        x0              : Secret key part 1 (0.0 to 1.0)
        r               : Secret key part 2 (3.57 to 4.0)
    """
    
    # ── Step 1: Prepare the message with metadata ──
    timestamp   = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    full_message = f"CHAOS_MSG|{timestamp}|{message}|END_CHAOS"
    
    # ── Step 2: Convert message to bytes ──
    message_bytes = np.frombuffer(
        full_message.encode('utf-8'), 
        dtype=np.uint8
    )
    msg_length = len(message_bytes)
    
    # ── Step 3: Generate chaotic key ──
    key = generate_chaotic_key(msg_length, x0, r)
    
    # ── Step 4: XOR encrypt ──
    encrypted_bytes = np.bitwise_xor(message_bytes, key)
    
    # ── Step 5: Create audio carrier ──
    # Add padding to make it look like real audio
    # Minimum size = 44100 samples (1 second of audio)
    min_audio_size = 44100
    
    if len(encrypted_bytes) < min_audio_size:
        # Pad with random noise to fill 1 second
        np.random.seed(int(x0 * 10000))  # Deterministic padding
        padding = np.random.randint(0, 256, 
                                    min_audio_size - len(encrypted_bytes), 
                                    dtype=np.uint8)
        audio_data = np.concatenate([encrypted_bytes, padding])
    else:
        audio_data = encrypted_bytes
    
    # ── Step 6: Store message length in first 4 bytes ──
    # This tells the decryptor where the message ends
    length_bytes = np.array(
        [(msg_length >> 24) & 0xFF,
         (msg_length >> 16) & 0xFF,
         (msg_length >> 8)  & 0xFF,
          msg_length        & 0xFF],
        dtype=np.uint8
    )
    
    # Final audio = [4 length bytes] + [encrypted message] + [padding]
    final_audio = np.concatenate([length_bytes, audio_data])
    
    # ── Step 7: Save as WAV file ──
    wavfile.write(output_filename, 44100, final_audio)
    
    return msg_length

def decrypt_audio_to_message(input_filename, x0, r):
    """
    Reads an encrypted WAV file and decrypts it back to text.
    
    HOW IT WORKS:
    1. Read WAV file
    2. Extract message length from first 4 bytes
    3. Regenerate exact same chaotic key
    4. XOR to reverse encryption
    5. Decode bytes back to text
    6. Validate and extract original message
    
    Parameters:
        input_filename : Path to encrypted WAV file
        x0             : Secret key part 1 (MUST match encryption)
        r              : Secret key part 2 (MUST match encryption)
    
    Returns:
        Decrypted message string or error message
    """
    
    # ── Step 1: Read encrypted audio ──
    try:
        sample_rate, audio_data = wavfile.read(input_filename)
    except FileNotFoundError:
        return None, "ERROR: File not found!"
    except Exception as e:
        return None, f"ERROR: Cannot read file - {str(e)}"
    
    # ── Step 2: Extract message length from first 4 bytes ──
    if len(audio_data) < 4:
        return None, "ERROR: File too small - not a valid encrypted file!"
    
    length_bytes = audio_data[:4]
    msg_length = (int(length_bytes[0]) << 24 | 
                  int(length_bytes[1]) << 16 | 
                  int(length_bytes[2]) << 8  | 
                  int(length_bytes[3]))
    
    # ── Step 3: Extract encrypted message bytes ──
    if len(audio_data) < 4 + msg_length:
        return None, "ERROR: File corrupted or wrong key!"
    
    encrypted_bytes = audio_data[4:4 + msg_length]
    
    # ── Step 4: Regenerate same chaotic key ──
    key = generate_chaotic_key(msg_length, x0, r)
    
    # ── Step 5: XOR decrypt ──
    decrypted_bytes = np.bitwise_xor(encrypted_bytes, key)
    
    # ── Step 6: Convert bytes to string ──
    try:
        full_message = decrypted_bytes.tobytes().decode('utf-8')
    except UnicodeDecodeError:
        return None, "ERROR: Wrong decryption key - cannot decode message!"
    
    # ── Step 7: Validate and extract message ──
    if not full_message.startswith("CHAOS_MSG|"):
        return None, "ERROR: Wrong key or not a valid encrypted message!"
    
    if not full_message.endswith("|END_CHAOS"):
        return None, "ERROR: Message corrupted!"
    
    # Extract: CHAOS_MSG|timestamp|YOUR_MESSAGE|END_CHAOS
    try:
        parts     = full_message.split("|")
        timestamp = parts[1]
        message   = "|".join(parts[2:-1])  # Handle messages with | in them
        
        # Format timestamp for display
        dt = datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        return message, formatted_time
    except Exception:
        return None, "ERROR: Message format invalid!"

# =====================================================
#           DISPLAY / UI FUNCTIONS  
# =====================================================

def print_banner():
    """Prints the application banner."""
    print("\n" + "="*60)
    print("   🔐  CHAOS THEORY SECURE MESSAGING SYSTEM  🔐")
    print("="*60)
    print("   Encrypt messages into audio files using")
    print("   the Logistic Map chaos equation")
    print("="*60)

def print_menu():
    """Prints the main menu."""
    print("\n" + "-"*60)
    print("   MAIN MENU")
    print("-"*60)
    print("   [1] 📝  Send Encrypted Message  (Encrypt)")
    print("   [2] 🔓  Read Encrypted Message  (Decrypt)")
    print("   [3] 📋  List Encrypted Files")
    print("   [4] ℹ️   How It Works")
    print("   [5] 🚪  Exit")
    print("-"*60)

def print_how_it_works():
    """Explains the encryption process."""
    print("\n" + "="*60)
    print("   HOW CHAOS ENCRYPTION WORKS")
    print("="*60)
    print("""
   1️⃣  TEXT TO BYTES
      Your message is converted into a sequence
      of numbers (bytes).

   2️⃣  LOGISTIC MAP (CHAOS EQUATION)
      Using your secret key (x0 and r), we generate
      a chaotic number sequence:
      
      x(n+1) = r × x(n) × (1 - x(n))
      
      Even a 0.0001 difference in key = completely
      different sequence (Butterfly Effect!)

   3️⃣  XOR ENCRYPTION
      Each message byte is XOR'd with key byte:
      
      Encrypted = Message XOR Key
      Decrypted = Encrypted XOR Key (same key!)

   4️⃣  AUDIO DISGUISE
      Encrypted bytes are saved as a .WAV audio file.
      It sounds like random white noise - no one
      knows it contains a secret message!

   5️⃣  DECRYPTION
      Receiver uses same key to regenerate identical
      chaotic sequence and XOR back to get message.
      
   🔑  SECURITY:
      • Key Space: Infinite real numbers
      • Wrong key = Garbage output
      • Looks like innocent audio file
      • No patterns visible in encrypted data
    """)
    print("="*60)

def get_secret_key():
    """
    Prompts user to enter their secret encryption key.
    Returns (x0, r) tuple.
    """
    print("\n" + "-"*60)
    print("   🔑  ENTER YOUR SECRET KEY")
    print("-"*60)
    print("   The key has TWO parts:")
    print("   • x0 : Initial value (any number between 0.01 and 0.99)")
    print("   • r  : Chaos rate   (any number between 3.57 and 4.0)")
    print("   ⚠️  BOTH values must be IDENTICAL to decrypt!")
    print("-"*60)
    
    while True:
        try:
            x0_input = input("\n   Enter x0 (e.g. 0.5): ").strip()
            x0 = float(x0_input)
            
            if not (0.01 <= x0 <= 0.99):
                print("   ❌ x0 must be between 0.01 and 0.99")
                continue
                
            r_input = input("   Enter r  (e.g. 3.99): ").strip()
            r = float(r_input)
            
            if not (3.57 <= r <= 4.0):
                print("   ❌ r must be between 3.57 and 4.0")
                continue
                
            print(f"\n   ✅ Key accepted: x0={x0}, r={r}")
            return x0, r
            
        except ValueError:
            print("   ❌ Invalid input. Please enter a number.")

def list_wav_files():
    """Lists all WAV files in current directory."""
    print("\n" + "-"*60)
    print("   📋  ENCRYPTED FILES IN CURRENT DIRECTORY")
    print("-"*60)
    
    wav_files = [f for f in os.listdir('.') if f.endswith('.wav')]
    
    if not wav_files:
        print("   No .wav files found in current directory.")
    else:
        for i, filename in enumerate(wav_files, 1):
            size = os.path.getsize(filename)
            print(f"   [{i}] {filename:<30} ({size:,} bytes)")
    
    print("-"*60)
    return wav_files

# =====================================================
#           SENDER WORKFLOW
# =====================================================

def sender_workflow():
    """
    Complete workflow for encrypting a message.
    Called when user selects 'Send Message'.
    """
    print("\n" + "="*60)
    print("   📝  ENCRYPT YOUR MESSAGE")
    print("="*60)
    
    # ── Get the message ──
    print("\n   Type your secret message below.")
    print("   (Press Enter twice when done)\n")
    
    lines = []
    print("   Message: ", end='')
    
    while True:
        line = input()
        if line == "":
            if lines:
                break
            else:
                print("   ⚠️  Message cannot be empty. Try again: ", end='')
        else:
            lines.append(line)
            print("            ", end='')  # Indent continuation lines
    
    message = "\n".join(lines)
    
    print(f"\n   📄 Message preview ({len(message)} characters):")
    print(f"   '{message[:50]}{'...' if len(message) > 50 else ''}'")
    
    # ── Get output filename ──
    print("\n" + "-"*60)
    default_name = f"encrypted_{datetime.datetime.now().strftime('%H%M%S')}.wav"
    filename_input = input(f"   Save as (press Enter for '{default_name}'): ").strip()
    
    if filename_input == "":
        output_filename = default_name
    else:
        # Auto-add .wav extension if missing
        output_filename = filename_input if filename_input.endswith('.wav') \
                         else filename_input + '.wav'
    
    # ── Get secret key ──
    x0, r = get_secret_key()
    
    # ── Perform encryption ──
    print("\n" + "-"*60)
    print("   🔄  ENCRYPTING...")
    print("-"*60)
    
    try:
        msg_length = encrypt_message_to_audio(message, output_filename, x0, r)
        
        print(f"\n   ✅  ENCRYPTION SUCCESSFUL!")
        print(f"\n   📊  Encryption Summary:")
        print(f"   {'─'*40}")
        print(f"   Original message  : {len(message)} characters")
        print(f"   Encrypted bytes   : {msg_length} bytes")
        print(f"   Output file       : {output_filename}")
        print(f"   File size         : {os.path.getsize(output_filename):,} bytes")
        print(f"   Secret key        : x0={x0}, r={r}")
        print(f"   {'─'*40}")
        print(f"\n   📤  SEND THIS TO RECEIVER:")
        print(f"   1. File    → '{output_filename}'")
        print(f"   2. Key x0  → {x0}")
        print(f"   3. Key r   → {r}")
        print(f"\n   ⚠️  Share the key through a SEPARATE secure channel!")
        
    except Exception as e:
        print(f"\n   ❌ Encryption failed: {str(e)}")

# =====================================================
#           RECEIVER WORKFLOW
# =====================================================

def receiver_workflow():
    """
    Complete workflow for decrypting a message.
    Called when user selects 'Read Message'.
    """
    print("\n" + "="*60)
    print("   🔓  DECRYPT A MESSAGE")
    print("="*60)
    
    # ── Show available files ──
    wav_files = list_wav_files()
    
    # ── Get filename ──
    print("\n   Enter the encrypted audio filename:")
    filename_input = input("   Filename: ").strip()
    
    if filename_input == "":
        print("   ❌ No filename entered.")
        return
    
    # Auto-add .wav if missing
    input_filename = filename_input if filename_input.endswith('.wav') \
                    else filename_input + '.wav'
    
    if not os.path.exists(input_filename):
        print(f"\n   ❌ File '{input_filename}' not found!")
        print(f"   Make sure the file is in: {os.getcwd()}")
        return
    
    print(f"   ✅ File found: {input_filename}")
    print(f"   File size: {os.path.getsize(input_filename):,} bytes")
    
    # ── Get secret key ──
    x0, r = get_secret_key()
    
    # ── Perform decryption ──
    print("\n" + "-"*60)
    print("   🔄  DECRYPTING...")
    print("-"*60)
    
    message, info = decrypt_audio_to_message(input_filename, x0, r)
    
    if message is None:
        print(f"\n   ❌  DECRYPTION FAILED!")
        print(f"   Reason: {info}")
        print(f"\n   Common causes:")
        print(f"   • Wrong x0 or r value")
        print(f"   • File was corrupted")
        print(f"   • This is not a valid encrypted file")
    else:
        print(f"\n   ✅  DECRYPTION SUCCESSFUL!")
        print(f"\n   {'='*50}")
        print(f"   📨  DECRYPTED MESSAGE:")
        print(f"   {'='*50}")
        print(f"\n   Sent at   : {info}")
        print(f"   Message   :")
        print(f"   {'─'*50}")
        # Print message with indentation
        for line in message.split('\n'):
            print(f"   {line}")
        print(f"   {'─'*50}")
        print(f"\n   Message length: {len(message)} characters")
    
    print("="*60)

# =====================================================
#                    MAIN APPLICATION
# =====================================================

def main():
    """
    Main application loop.
    Displays menu and handles user choices.
    """
    print_banner()
    
    while True:
        print_menu()
        
        choice = input("   Enter your choice (1-5): ").strip()
        
        if choice == '1':
            # ── Encrypt a message ──
            sender_workflow()
            input("\n   Press Enter to continue...")
            
        elif choice == '2':
            # ── Decrypt a message ──
            receiver_workflow()
            input("\n   Press Enter to continue...")
            
        elif choice == '3':
            # ── List encrypted files ──
            list_wav_files()
            input("\n   Press Enter to continue...")
            
        elif choice == '4':
            # ── How it works ──
            print_how_it_works()
            input("\n   Press Enter to continue...")
            
        elif choice == '5':
            # ── Exit ──
            print("\n" + "="*60)
            print("   👋  Thank you for using Chaos Encryption!")
            print("   Your messages are safe with chaos theory.")
            print("="*60 + "\n")
            sys.exit(0)
            
        else:
            print("\n   ❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")

# =====================================================
#              RUN THE APPLICATION
# =====================================================

if __name__ == "__main__":
    main()