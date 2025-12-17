from django.db import models

class Tacho(models.Model):

    TIPO_CHOICES = [
        ("publico", "Público / Empresa"),
        ("personal", "Personal"),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="publico"
    )

    propietario = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tachos"
    )

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

    nivel_llenado = models.IntegerField(default=0)

    activo = models.BooleanField(default=True)   # 🔴 borrado lógico
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
