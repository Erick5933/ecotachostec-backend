#!/usr/bin/env python
"""
Script para crear un usuario de prueba en la base de datos
Uso: python manage.py shell < create_user.py
"""

from core.models.usuario_models import Usuario

# Datos del usuario de prueba
email = "test@example.com"
password = "test123456"
nombre = "Usuario de Prueba"

# Eliminar usuario si ya existe
Usuario.objects.filter(email=email).delete()

# Crear nuevo usuario
user = Usuario.objects.create_user(
    email=email,
    nombre=nombre,
    password=password,
    rol="user",
    activo=True
)

print(f"✅ Usuario creado exitosamente")
print(f"   Email: {email}")
print(f"   Contraseña: {password}")
print(f"   Nombre: {nombre}")
print(f"\nPrueba el login en: http://localhost:5174/")
