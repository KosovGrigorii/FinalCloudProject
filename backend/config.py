import os

DB_URL = os.environ.get("DOCUMENT_API_ENDPOINT", "")
REGION = "ru-central1" 
ACCESS_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
BACKEND_VERSION = os.environ.get("APP_VERSION", "1")
