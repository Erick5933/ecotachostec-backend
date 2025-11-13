from django.db import models
from core.models.tacho_models import Tacho

class Deteccion(models.Model):
    tacho = models.ForeignKey(Tacho, on_delete=models.CASCADE, related_name="detecciones")
    codigo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    ubicacion_lon = models.CharField(max_length=50)
    ubicacion_lat = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Detección {self.codigo} - {self.nombre}"
