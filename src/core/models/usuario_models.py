from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from core.models.ubicacion_models import Canton

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, rol="user", **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un email.")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nombre=nombre,
            rol=rol,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):

    ROL_CHOICES = [
        ("admin", "Administrador"),
        ("user", "Usuario"),
    ]

    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default="user"
    )

    telefono = models.CharField(max_length=20, blank=True, null=True)

    canton = models.ForeignKey(
        Canton,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔑 OBLIGATORIOS PARA DJANGO
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombre} ({self.email})"
