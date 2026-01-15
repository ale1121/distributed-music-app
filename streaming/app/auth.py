import os
import time
import hmac
import hashlib
import base64
from werkzeug.exceptions import Forbidden


STREAM_SECRET = os.getenv('STREAM_SECRET', '')


def verify_signature(filename, expire, signature):
    
    if time.time() > int(expire):
        raise Forbidden("expired")
    
    msg = f"{filename}+{expire}"

    expected_bytes = hmac.new(
        STREAM_SECRET.encode(), msg.encode(), hashlib.sha256
    ).digest()

    expected = base64.urlsafe_b64encode(expected_bytes).decode()
    if not hmac.compare_digest(signature, expected):
        raise Forbidden("bad signature")
