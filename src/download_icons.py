import os
import json
import requests
import time
import zipfile
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def sync_icons():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "cache")
    detectable_file = os.path.join(cache_dir, "detectable.json")
    zip_path = os.path.join(cache_dir, "icons.zip")

    os.makedirs(cache_dir, exist_ok=True)

    if not os.path.exists(detectable_file):
        print("detectable.json not found.")
        return

    with open(detectable_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    win32_games = [e for e in data if any(x.get("os") == "win32" for x in e.get("executables", []))]
    
    # Read existing files in zip
    existing_icons = set()
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                existing_icons = set(zf.namelist())
        except:
            pass

    tasks = []
    for game in win32_games:
        game_id = game.get("id")
        icon_hash = game.get("icon_hash")
        if game_id and icon_hash:
            filename = f"{game_id}_{icon_hash}.webp"
            if filename not in existing_icons:
                url = f"https://cdn.discordapp.com/app-icons/{game_id}/{icon_hash}.png"
                tasks.append((url, filename))

    print(f"Total games: {len(win32_games)}. Missing icons: {len(tasks)}")
    if not tasks:
        print("All icons are up to date.")
        return

    # To write to zip file safely from multiple threads, we use a lock
    zip_lock = threading.Lock()
    success = 0
    
    # Open zip in append mode
    def fetch_and_store(url, filename, zf):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                
                # Compress to WEBP
                out_io = BytesIO()
                img.save(out_io, format="WEBP", quality=50)
                out_io.seek(0)
                
                with zip_lock:
                    zf.writestr(filename, out_io.read())
                return True
        except Exception as e:
            pass
        return False

    with zipfile.ZipFile(zip_path, 'a', compression=zipfile.ZIP_DEFLATED) as zf:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_and_store, t[0], t[1], zf): t for t in tasks}
            for i, future in enumerate(as_completed(futures)):
                if future.result():
                    success += 1
                if i % 50 == 0 and i > 0:
                    print(f"Downloaded and compressed {i}/{len(tasks)} icons...")
                    time.sleep(0.5)

    print(f"Done! Successfully added {success} compressed icons to icons.zip.")

if __name__ == "__main__":
    sync_icons()
