"""Modelos de datos de la aplicacion"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

class Rol(models.Model):
    """Modelo que define los roles de los usuarios en el sistema."""
    rol = models.CharField(max_length=50)

    def __str__(self):
        return str(self.rol)

class Personal(models.Model):
    """Modelo que define el personal del sistema."""
    nombre = models.CharField(max_length=100)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.nombre)

class Ubicacion(models.Model):
    """Modelo que define las ubicaciones de los juegos en el inventario."""
    idUbicacion = models.AutoField(primary_key=True)
    nombreUbicacion = models.CharField(max_length=100)
    descripcionUbicacion = models.CharField(max_length=255)

    @property
    def stock_total_local(self):
        """Calcula el stock total de juegos en esta ubicación."""
        return Stock.objects.filter(ubicacion=self).aggregate(total=Sum('cantidad'))['total'] or 0

    def __str__(self):
        return str(self.nombreUbicacion)

class Consola(models.Model):
    """Modelo que define las consolas de videojuegos."""
    idConsola = models.AutoField(primary_key=True)
    nombreConsola = models.CharField(max_length=100)
    marcaConsola = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombreConsola}"

class Estado(models.Model):
    """Modelo que define el estado de un juego."""
    idEstado = models.IntegerField(primary_key=True,default=None)
    nombreEstado = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombreEstado}"

class Distribucion(models.Model):
    """Modelo que define la distribución de un juego."""
    idDistribucion = models.IntegerField(primary_key=True, default=None)
    localidadDistribucion = models.CharField(max_length=80)
    siglaDistribucion = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.siglaDistribucion} : {self.localidadDistribucion}"

class Clasificacion(models.Model):
    """Modelo que define la clasificación de un juego."""
    idClasificacion = models.IntegerField(primary_key=True,default=None)
    distribucion = models.ForeignKey(Distribucion,on_delete=models.CASCADE)
    descripcionClasificacion = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.descripcionClasificacion}"

class Descripcion(models.Model):
    """Modelo descripcion tipo de edicion juego"""
    idDescripcion = models.IntegerField(primary_key=True,default=None)
    detallesDescripcion= models.CharField(max_length=100)

    def __str__(self):
        return str(self.detallesDescripcion)

class Juego(models.Model):
    """Modelo que define los juegos de video."""
    codigoDeBarra = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombreJuego = models.CharField(max_length=250)
    consola = models.ForeignKey(Consola, on_delete=models.CASCADE)
    distribucion = models.ForeignKey(Distribucion, on_delete=models.CASCADE)
    clasificacion = models.ForeignKey(Clasificacion, on_delete=models.CASCADE)
    descripcion = models.ForeignKey(Descripcion, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    imagen = models.URLField(max_length=500, blank=True, null=True)  # Cambiado a URLField

    @property
    def stock_total(self):
        """Calcula el stock total de este juego en todas las ubicaciones."""
        return Stock.objects.filter(juego=self).aggregate(
            total=models.Sum('cantidad'))['total'] or 0
    def __str__(self):
        return str(self.nombreJuego)

class Stock(models.Model):
    """Modelo que define el stock de juegos en ubicaciones."""
    idStock = models.AutoField(primary_key=True)
    juego = models.ForeignKey('Juego', on_delete=models.CASCADE, related_name='stocks')
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.juego.nombreJuego} - {self.ubicacion.nombreUbicacion}: {self.cantidad}"