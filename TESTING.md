# 🚀 Backend Levantado - Guía de Prueba

## ✅ Estado Actual
- **Server**: Running en `http://localhost:8000`
- **Python**: 3.14 (Virtual Environment)
- **Base de datos**: SQLite local
- **Firebase**: Configurado correctamente

## 🧪 Credenciales de Prueba para Login

```
Email: test@example.com
Contraseña: test123456
```

## 📝 Endpoints Principales

### Autenticación
- `POST /api/usuarios/auth/login/` - Login con email/contraseña
- `POST /api/usuarios/auth/register/` - Registro nuevo usuario
- `POST /api/usuarios/auth/google/` - Login con Google (requiere Firebase)
- `POST /api/usuarios/auth/password-reset/` - Solicitar reset de contraseña

### Usuarios
- `GET /api/usuarios/` - Listar usuarios (requiere autenticación)
- `GET /api/usuarios/{id}/` - Obtener usuario
- `POST /api/usuarios/` - Crear usuario
- `PUT /api/usuarios/{id}/` - Actualizar usuario
- `DELETE /api/usuarios/{id}/` - Eliminar usuario

## 🔐 Headers para Autenticación

Después de login, recibirás un token JWT. Incluye en todos los requests autenticados:

```
Authorization: Bearer {tu_token_jwt}
```

## 🔧 Troubleshooting

### Error 400 en login
- Verifica que el email y contraseña sean correctos
- Asegúrate que el usuario está activo (`activo=True`)

### Error 403 Forbidden
- Probablemente falta el header `Authorization`
- Verifica que el token no ha expirado

### Error CORS
- Revisa que tu frontend esté en una URL permitida en `CORS_ALLOWED_ORIGINS`
- Por defecto: `http://localhost:5174`

## 📄 Archivos de Configuración

- `.env` - Variables de entorno
- `firebase_credentials.json` - Credenciales de Firebase (ya configurado)
- `settings.py` - Configuración de Django

## 🆘 Crear Más Usuarios de Prueba

```bash
cd src
$env:DJANGO_SETTINGS_MODULE="ecotachostec_backend.settings"
python -c "
import django
django.setup()
from core.models.usuario_models import Usuario
user = Usuario.objects.create_user(
    email='otro@example.com',
    nombre='Otro Usuario',
    password='test123456',
    rol='user',
    activo=True
)
print(f'✅ Usuario creado: {user.email}')
"
```

¡Listo para testing! 🎉
