import sys
import numpy as np
from PIL import Image
import struct
import os

OUTPUT_DIR = "output/"

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def bytes_to_bits(data):
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))

def bits_to_bytes(bits):
    return np.packbits(bits).tobytes()

# -----------------------------
# HIDE FILE
# -----------------------------
def hide_file(image_path, file_path, output_image_name):
    ensure_output_dir()

    img = Image.open(image_path).convert("RGB")
    img_arr = np.array(img)

    with open(file_path, "rb") as f:
        payload = f.read()

    filename = os.path.basename(file_path).encode()
    header = struct.pack(">I", len(filename)) + filename + struct.pack(">I", len(payload))
    data = header + payload

    bits = bytes_to_bits(data)

    capacity = img_arr.size  # 1 bit per channel
    if len(bits) > capacity:
        raise ValueError("❌ File too large for this image.")

    flat = img_arr.flatten()

    for i, bit in enumerate(bits):
        if i % 2 == 0:
            # even bit → 2nd LSB
            flat[i] &= 0b11111101
            flat[i] |= (bit << 1)
        else:
            # odd bit → LSB
            flat[i] &= 0b11111110
            flat[i] |= bit

    stego = flat.reshape(img_arr.shape)

    output_path = os.path.join(OUTPUT_DIR, output_image_name)
    Image.fromarray(stego.astype(np.uint8)).save(output_path)

    print(f"✅ File hidden in {output_path}")

# -----------------------------
# EXTRACT FILE
# -----------------------------
def extract_file(stego_path):
    ensure_output_dir()

    img = Image.open(stego_path).convert("RGB")
    flat = np.array(img).flatten()

    bits = np.zeros(flat.size, dtype=np.uint8)

    for i, px in enumerate(flat):
        if i % 2 == 0:
            bits[i] = (px >> 1) & 1
        else:
            bits[i] = px & 1

    idx = 0

    name_len = struct.unpack(">I", bits_to_bytes(bits[idx:idx+32]))[0]
    idx += 32

    name_bits = bits[idx:idx + name_len * 8]
    filename = bits_to_bytes(name_bits).decode()
    idx += name_len * 8

    file_size = struct.unpack(">I", bits_to_bytes(bits[idx:idx+32]))[0]
    idx += 32

    file_bits = bits[idx:idx + file_size * 8]
    data = bits_to_bytes(file_bits)

    output_file_path = os.path.join(OUTPUT_DIR, "extracted_" + filename)
    with open(output_file_path, "wb") as f:
        f.write(data)

    print(f"✅ Extracted file: {output_file_path}")

# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("""
Usage:
  Hide:    python stego.py hide input.png secret.txt stego.png
  Extract: python stego.py extract stego.png
""")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "hide":
        hide_file(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "extract":
        extract_file(sys.argv[2])
    else:
        print("Unknown mode.")
