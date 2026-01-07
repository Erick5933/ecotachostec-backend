import firebase_admin
from firebase_admin import credentials
import os
import json
from django.conf import settings

# Verifica si ya está inicializada para evitar errores de reinicio
if not firebase_admin._apps:
    
    # Intenta cargar desde archivo JSON si existe
    creds_path = os.path.join(settings.BASE_DIR, 'firebase_credentials.json')
    
    if os.path.exists(creds_path):
        cred = credentials.Certificate(creds_path)
    else:
        # Si no hay archivo, usa las variables de entorno (Render/Heroku/Docker)
        # Nota: La private_key necesita reemplazo de saltos de línea si viene de .env
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        if private_key:
            private_key = private_key.replace('\\n', '\n')

        creds_dict = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID', 'ecotachostec'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": private_key,
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        cred = credentials.Certificate(creds_dict)

    firebase_admin.initialize_app(cred)