from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from core.models.ubicacion_models import Provincia, Canton

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, rol="usuario", **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un email.")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=30, default="usuario")   # usuario | admin
    telefono = models.CharField(max_length=20, null=True, blank=True)

    canton = models.ForeignKey(Canton, on_delete=models.SET_NULL, null=True)

    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.email})"
