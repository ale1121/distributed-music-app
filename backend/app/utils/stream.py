import os
import time
import hmac
import hashlib
import base64


STREAMING_URL = os.getenv('STREAMING_URL', 'http://localhost:5001')
STREAM_SECRET = os.getenv('STREAM_SECRET', '')
TTL = 30


def sign_streaming_url(filename):
    expire = int(time.time()) + TTL
    msg = f"{filename}+{expire}"

    signature_bytes = hmac.new(
        STREAM_SECRET.encode(), msg.encode(), hashlib.sha256
    ).digest()

    signature = base64.urlsafe_b64encode(signature_bytes).decode()

    return f"{STREAMING_URL}/stream/{filename}?exp={expire}&sig={signature}"
