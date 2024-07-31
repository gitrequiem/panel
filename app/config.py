# config.py
import os

class Config:
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    APP_TITLE = os.getenv('APP_TITLE', 'REQUIEM Panel')
    SESSION_COOKIE_SAMESITE=os.getenv('SESSION_COOKIE_SAMESITE', 'None')
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'True')