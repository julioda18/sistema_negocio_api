from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre= models.CharField(max_length=200)
    apellido= models.CharField(max_length=200)
    correo = models.EmailField()
    ci = models.CharField(max_length=12, blank=True)
    direccion= models.TextField()
    telefono = models.CharField(max_length=20)
   