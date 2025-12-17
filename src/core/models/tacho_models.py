from django.db import models

class Tacho(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)

    ubicacion_lat = models.DecimalField(max_digits=9, decimal_places=6)
    ubicacion_lon = models.DecimalField(max_digits=9, decimal_places=6)

    descripcion = models.TextField(blank=True, null=True)

    estado = models.CharField(
        max_length=20,
        choices=[
            ("activo", "Activo"),
            ("mantenimiento", "Mantenimiento"),
            ("fuera_servicio", "Fuera de servicio"),
        ],
        default="activo"
    )

    nivel_llenado = models.IntegerField(default=0)  # % (IoT futuro)
    ultima_deteccion = models.DateTimeField(null=True, blank=True)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
