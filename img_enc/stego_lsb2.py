import sys
import numpy as np
from PIL import Image
import struct
import os

# -----------------------------
# Utility
# -----------------------------
def bytes_to_bits(data):
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))

def bits_to_bytes(bits):
    return np.packbits(bits).tobytes()

# -----------------------------
# HIDE FILE
# -----------------------------
def hide_file(image_path, file_path, output_path):
    img = Image.open(image_path).convert("RGB")
    img_arr = np.array(img)

    with open(file_path, "rb") as f:
        payload = f.read()

    filename = os.path.basename(file_path).encode()
    header = struct.pack(">I", len(filename)) + filename + struct.pack(">I", len(payload))
    data = header + payload

    bits = bytes_to_bits(data)

    capacity = img_arr.size * 2
    if len(bits) > capacity:
        raise ValueError("❌ File too large for this image.")

    flat = img_arr.flatten()

    for i in range(len(bits) // 2):
        flat[i] &= 0b11111100
        flat[i] |= (bits[2*i] << 1) | bits[2*i + 1]

    if len(bits) % 2:
        flat[len(bits)//2] &= 0b11111110
        flat[len(bits)//2] |= bits[-1]

    stego = flat.reshape(img_arr.shape)
    Image.fromarray(stego.astype(np.uint8)).save(output_path)
    print(f"✅ File hidden in {output_path}")

# -----------------------------
# EXTRACT FILE
# -----------------------------
def extract_file(stego_path):
    img = Image.open(stego_path).convert("RGB")
    arr = np.array(img).flatten()

    bits = []
    for px in arr:
        bits.append((px >> 1) & 1)
        bits.append(px & 1)

    bits = np.array(bits, dtype=np.uint8)

    # Read filename length
    idx = 0
    name_len = struct.unpack(">I", bits_to_bytes(bits[idx:idx+32]))[0]
    idx += 32

    # Read filename
    name_bits = bits[idx:idx + name_len * 8]
    filename = bits_to_bytes(name_bits).decode()
    idx += name_len * 8

    # Read file size
    file_size = struct.unpack(">I", bits_to_bytes(bits[idx:idx+32]))[0]
    idx += 32

    # Read file data
    file_bits = bits[idx:idx + file_size * 8]
    data = bits_to_bytes(file_bits)

    with open("extracted_" + filename, "wb") as f:
        f.write(data)

    print(f"✅ Extracted file: extracted_{filename}")

# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("""
Usage:
  Hide:    python stego_lsb2.py hide input.png secret.txt output.png
  Extract: python stego_lsb2.py extract stego.png
""")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "hide":
        hide_file(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "extract":
        extract_file(sys.argv[2])
    else:
        print("Unknown mode.")
