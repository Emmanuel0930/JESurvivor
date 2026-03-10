from django.db import models
from django.contrib.auth.models import User

class KitEspecializado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class ReservaKit(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    kit = models.ForeignKey(KitEspecializado, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, default="pendiente")

    def __str__(self):
        return f"Reserva de {self.kit} por {self.usuario}"
