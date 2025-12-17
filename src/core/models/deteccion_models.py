from django.db import models
from core.models.tacho_models import Tacho

class Deteccion(models.Model):

    CLASIFICACION_CHOICES = [
        ("organico", "Orgánico"),
        ("inorganico", "Inorgánico"),
        ("reciclable", "Reciclable"),
        ("ninguno","No clasificado")
    ]

    tacho = models.ForeignKey(
        Tacho,
        on_delete=models.CASCADE,
        related_name="detecciones"
    )

    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detecciones"
    )
    # 👆 SOLO SE USA EN TACHOS PERSONALES

    clasificacion = models.CharField(
        max_length=20,
        choices=CLASIFICACION_CHOICES,
        default="ninguno"
    )

    confianza_ia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    imagen = models.ImageField(
        upload_to="detecciones/%Y/%m/%d/"
    )

    ubicacion_lat = models.DecimalField(max_digits=9, decimal_places=6)
    ubicacion_lon = models.DecimalField(max_digits=9, decimal_places=6)

    descripcion = models.TextField(blank=True, null=True)

    procesado = models.BooleanField(default=True)

    activo = models.BooleanField(default=True)  # 🔴 borrado lógico
    created_at = models.DateTimeField(auto_now_add=True)
