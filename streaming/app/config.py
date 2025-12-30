import os


class Config:
    AUDIO_PATH = os.getenv('AUDIO_PATH', '/audio_data')