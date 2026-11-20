import sys
import os
import time
import urllib.request

MODEL_URL = "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
DEST_PATH = "d:/EduTrack/models/llama-3.2-1b-instruct-q4_k_m.gguf"

def download_model():
    os.makedirs("d:/EduTrack/models", exist_ok=True)
    if os.path.exists(DEST_PATH) and os.path.getsize(DEST_PATH) > 700 * 1024 * 1024:
        print(f"Model already downloaded at {DEST_PATH} ({os.path.getsize(DEST_PATH)/(1024*1024):.1f} MB)")
        return

    print(f"Starting download of Llama-3.2-1B-Instruct-Q4_K_M.gguf...")
    print(f"URL: {MODEL_URL}")
    print(f"Destination: {DEST_PATH}")

    req = urllib.request.Request(MODEL_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(DEST_PATH, "wb") as out_file:
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024 * 4  # 4MB chunks
        t0 = time.time()
        last_print = t0

        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if now - last_print >= 5 or downloaded == total_size:
                elapsed = now - t0
                speed_mb = (downloaded / (1024 * 1024)) / max(elapsed, 0.001)
                pct = (downloaded / total_size * 100) if total_size else 0
                print(f"Downloaded: {downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB ({pct:.1f}%) | Speed: {speed_mb:.1f} MB/s")
                last_print = now

    print(f"\nDownload finished successfully! Model saved at {DEST_PATH}")

if __name__ == "__main__":
    download_model()
