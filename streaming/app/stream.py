import os
import socket
from flask import Flask, request, Response, Blueprint, current_app, jsonify
from werkzeug.exceptions import NotFound, RequestedRangeNotSatisfiable


stream_bp = Blueprint('stream', __name__)

CHUNK_SIZE = 1024 * 128


@stream_bp.route("/stream/<path:filename>", methods=["GET"])
def stream_file(filename):
    current_app.logger.info(f"Serving from {socket.gethostname()}")
    audio_dir = current_app.config['AUDIO_PATH']
    file_path = os.path.join(audio_dir, filename)
    if not os.path.isfile(file_path):
        raise NotFound("File not found")
    file_size = os.path.getsize(file_path)

    range_header = request.headers.get("Range")

    if not range_header:
        # send entire file
        return Response(
            generate(file_path, 0, file_size),
            status=200,
            mimetype="audio/mpeg",
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes"
            }
        )
    
    # send range of bytes
    try:
        # parse range header: "bytes=start-end"
        unit, range = range_header.split("=", 1)
        if unit.strip() != "bytes":
            raise RequestedRangeNotSatisfiable
        
        s, e = range.split("-", 1)
        start = int(s) if s else 0
        end = int(e) if e else file_size - 1

        if start < 0 or end < start or end >= file_size:
            raise RequestedRangeNotSatisfiable

    except Exception:
        raise RequestedRangeNotSatisfiable

    length = end - start + 1

    return Response(
        generate(file_path, start, length),
        status=206, # partial content
        mimetype="audio/mpeg",
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length)
        }
    )


def generate(file_path, start, length):
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = length
        while remaining > 0:
            chunk = f.read(min(CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk
