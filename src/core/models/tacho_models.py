from django.db import models

class Tacho(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    ubicacion_lon = models.CharField(max_length=50)
    ubicacion_lat = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
