import os
from mutagen.mp3 import MP3
from uuid import uuid4
from werkzeug.exceptions import UnsupportedMediaType

ACCEPT = {'.mp3'}

def save_audio_file(in_file, out_dir, file_name):
    # check file extension
    file_ext = os.path.splitext(in_file.filename)[1]
    if file_ext not in ACCEPT:
        raise UnsupportedMediaType('Unsupported file type')

    # save file
    os.makedirs(out_dir, exist_ok=True)
    out_file = f"{file_name}-{uuid4().hex}{file_ext}"
    out_path = os.path.join(out_dir, out_file)
    in_file.save(out_path)

    # get audio duration
    saved_file = MP3(out_path)
    duration = int(saved_file.info.length)

    return out_file, duration
