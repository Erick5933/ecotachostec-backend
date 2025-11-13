from django.db import models
from core.models.usuario_models import Usuario

class Tacho(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="tachos")
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    ubicacion_lon = models.CharField(max_length=50)
    ubicacion_lat = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Tacho {self.codigo} - {self.nombre}"
