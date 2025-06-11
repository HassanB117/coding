from mitmproxy import http
import os
import requests

DOWNLOAD_DIR = "downloaded_mp3s"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

downloaded_files = []

def response(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    if url.lower().endswith(".mp3"):
        filename = os.path.basename(url.split("?")[0])
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        if not os.path.exists(filepath):
            print(f"[+] MP3 Found: {url}")
            try:
                r = requests.get(url, stream=True)
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_files.append(filename)
                print(f"[✓] Downloaded: {filename}")
            except Exception as e:
                print(f"[!] Failed to download {url} - {e}")

def done():
    if downloaded_files:
        print("\n[✓] Download summary:")
        for file in downloaded_files:
            print(f"  - {file}")
    else:
        print("\n[!] No MP3s were downloaded.")
