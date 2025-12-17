from django.db import models
from core.models.tacho_models import Tacho

class Deteccion(models.Model):

    CLASIFICACION_CHOICES = [
        ("organico", "Orgánico"),
        ("inorganico", "Inorgánico"),
        ("reciclable", "Reciclable"),
    ]

    tacho = models.ForeignKey(
        Tacho,
        on_delete=models.CASCADE,
        related_name="detecciones"
    )

    codigo = models.CharField(max_length=50)

    clasificacion = models.CharField(
        max_length=20,
        choices=CLASIFICACION_CHOICES,
        default="No definido"
    )

    confianza_ia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje de certeza de la IA",
        default=0.00
    )

    imagen = models.ImageField(
        upload_to="detecciones/%Y/%m/%d/",
        null=True,  # Añade esto si no es obligatorio
        blank=True
    )

    ubicacion_lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.00)
    ubicacion_lon = models.DecimalField(max_digits=9, decimal_places=6, default=0.00)

    descripcion = models.TextField(blank=True, null=True)

    procesado = models.BooleanField(default=True)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.clasificacion}"
