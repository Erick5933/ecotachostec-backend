# Guía de Configuración de Firebase

## Opción 1: Usando archivo JSON (Recomendado para desarrollo local)

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto **ecotachostec**
3. Ve a **Project Settings** → **Service Accounts**
4. Haz clic en **Generate New Private Key**
5. Se descargará un archivo JSON
6. Renómbralo a `firebase_credentials.json`
7. Colócalo en la carpeta `src/` (misma carpeta que `manage.py`)

## Opción 2: Usando variables de entorno (Para Docker/Producción)

En tu archivo `.env` en la carpeta `src/`, agrega:

```env
GOOGLE_CLOUD_PROJECT=ecotachostec
FIREBASE_PROJECT_ID=ecotachostec
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@ecotachostec.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789
FIREBASE_DATABASE_URL=https://ecotachostec.firebaseio.com
```

Nota: La FIREBASE_PRIVATE_KEY debe tener `\n` para saltos de línea.

## Verificar que Firebase está funcionando

Una vez configurado, el backend debería:
- No mostrar errores de "project ID is required"
- Permitir login con Google
- Verificar tokens de Firebase correctamente

## Problemas comunes

**Error: "A project ID is required"**
- Solución: Asegúrate de tener `firebase_credentials.json` en `src/` O configurar `GOOGLE_CLOUD_PROJECT` en `.env`

**Error: "Permission denied"**
- Solución: Verifica que tu JSON tenga los permisos correctos en Firebase Console

**Error CORS**
- Solución: Revisa que `CORS_ALLOWED_ORIGINS` en `.env` incluya tu frontend (ej: http://localhost:5174)
