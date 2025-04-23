from django.contrib.auth.models import User #Clase preestablecida de Django
#permite crear los usuarios almacenando de forma segura sus contraseñas
from django.db import models

#Modelo Rol

class Rol(models.Model):
    rol = models.CharField(max_length=50)

    def __str__(self):
        return self.rol
    
#Modelo Usuario

class Personal(models.Model):
    nombre = models.CharField(max_length=100)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre
