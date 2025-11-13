from django.db import models

class Provincia(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="ciudades")

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"


class Canton(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name="cantones")

    def __str__(self):
        return f"{self.nombre} - {self.ciudad.nombre}"
