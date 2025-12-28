import os
from mutagen.mp3 import MP3
from uuid import uuid4

ACCEPT = {'.mp3'}

def save_audio_file(in_file, album_id, out_dir):
    file_ext = os.path.splitext(in_file.filename)[1]
    if file_ext not in ACCEPT:
        raise Exception('Unsupported file type')

    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, f"audio-{album_id}-{uuid4().hex}{file_ext}")
    in_file.save(out_path)

    saved_file = MP3(out_path)
    duration = int(saved_file.info.length)

    return out_path, duration
