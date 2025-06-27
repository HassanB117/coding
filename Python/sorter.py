import os
import re
import shutil
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC
from PIL import Image
from io import BytesIO


def sanitize_folder_name(name):
    return re.sub(r'[\\/:*?"<>|]', '', name)

def extract_and_save_cover(audio, folder_path, album_name):
    images = [frame for frame in audio.values() if isinstance(frame, APIC)]
    if not images:
        print(f"[NO COVER] No APIC frames found for album '{album_name}'")
        return False

    for idx, apic in enumerate(images):
        try:
            img_data = apic.data
            img = Image.open(BytesIO(img_data))
            img_format = img.format if img.format in ["JPEG", "PNG"] else "JPEG"
            ext = ".png" if img_format == "PNG" else ".jpg"
            img_path = os.path.join(folder_path, f"{album_name}{ext}")
            img.save(img_path, format=img_format)
            print(f"[COVER] Saved album cover for '{album_name}' as {ext.upper()}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save image from APIC frame #{idx} for '{album_name}': {e}")
    return False

def organize_tracks_by_album(folder_path):
    album_tracks = {}

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith('.mp3'):
            continue
        track_path = os.path.join(folder_path, filename)
        try:
            audio = ID3(track_path)
        except Exception as e:
            print(f"[SKIP] Cannot read tags from '{filename}': {e}")
            continue

        album_tag = audio.get('TALB')
        if not album_tag:
            print(f"[SKIP] No album tag in '{filename}'")
            continue

        album_name = album_tag.text[0]
        safe_album_name = sanitize_folder_name(album_name)
        album_tracks.setdefault(safe_album_name, []).append(track_path)

    for album_name, tracks in album_tracks.items():
        album_folder = os.path.join(folder_path, album_name)
        if not os.path.exists(album_folder):
            try:
                os.makedirs(album_folder)
                print(f"[CREATE] Folder '{album_folder}'")
            except Exception as e:
                print(f"[ERROR] Cannot create folder '{album_folder}': {e}")
                continue

        for track in tracks:
            dest = os.path.join(album_folder, os.path.basename(track))
            try:
                if not os.path.exists(dest):
                    shutil.move(track, dest)
                    print(f"[MOVE] '{os.path.basename(track)}' -> '{album_folder}'")
                else:
                    print(f"[SKIP] '{os.path.basename(track)}' already exists in '{album_folder}'")
            except Exception as e:
                print(f"[ERROR] Failed to move '{os.path.basename(track)}': {e}")

        try:
            first_track_path = os.path.join(album_folder, os.path.basename(tracks[0]))
            audio = ID3(first_track_path)
            extracted = extract_and_save_cover(audio, album_folder, album_name)
            if not extracted:
                print(f"[NO COVER] No cover art extracted for album '{album_name}'")
        except Exception as e:
            print(f"[ERROR] Cannot process cover for '{album_name}': {e}")


folder_path = r"C:\Users\Hassan\Music\gg\MMM\M3" # music folder path
organize_tracks_by_album(folder_path)
