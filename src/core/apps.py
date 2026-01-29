from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Initialize Firebase Admin without importing external modules."""
        try:
            import os
            from django.conf import settings
            import firebase_admin
            from firebase_admin import credentials

            if not firebase_admin._apps:
                cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", None)

                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase Admin inicializado: {cred_path}")
                else:
                    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                    if env_path and os.path.exists(env_path):
                        cred = credentials.Certificate(env_path)
                        firebase_admin.initialize_app(cred)
                        print(f"✅ Firebase Admin inicializado (env): {env_path}")
                    else:
                        # Si no hay credenciales en archivo, intentar crear desde variables de entorno
                        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', os.getenv('FIREBASE_PROJECT_ID', 'ecotachostec'))
                        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                        
                        if private_key:
                            private_key = private_key.replace('\\n', '\n')
                            creds_dict = {
                                "type": "service_account",
                                "project_id": project_id,
                                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                                "private_key": private_key,
                                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                                "token_uri": "https://oauth2.googleapis.com/token",
                            }
                            cred = credentials.Certificate(creds_dict)
                            firebase_admin.initialize_app(cred)
                            print(f"✅ Firebase Admin inicializado (env vars): {project_id}")
                        else:
                            firebase_admin.initialize_app()
                            print("✅ Firebase Admin inicializado (default)")
        except Exception as e:
            # Don't block app startup; Google login will surface errors
            print(f"⚠️ No se pudo inicializar Firebase en ready(): {e}")
