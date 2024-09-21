# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

class Config:
    API_BASE_URL = os.getenv('API_BASE_URL')
    APP_TITLE = os.getenv('APP_TITLE', 'REQUIEM Panel')
    SESSION_COOKIE_SAMESITE=os.getenv('SESSION_COOKIE_SAMESITE', 'None')
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'True')
    SECRET_KEY = os.getenv('SECRET_KEY')