from django.db import models

class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

class Canton(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
