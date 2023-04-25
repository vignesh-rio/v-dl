import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-goes-here'
    DOWNLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
