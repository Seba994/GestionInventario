from django.contrib.auth.models import User #Clase preestablecida de Django
#permite crear los usuarios almacenando de forma segura sus contraseñas
from django.db import models 
from django.db.models import Sum
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

#Modelo Ubicacion

class Ubicacion(models.Model):
    
    idUbicacion = models.AutoField(primary_key=True)
    nombreUbicacion = models.CharField(max_length=100)
    descripcionUbicacion = models.CharField(max_length=255)

    @property
    def stock_total_local(self):
        return self.stock.aggregate(total=Sum('cantidad'))['total'] or 0

    def __str__(self):
        return self.nombreUbicacion
    


#modelo consola

class Consola(models.Model):

    idConsola1 = models.IntegerField(primary_key=True, default=None)
    nombreConsola = models.CharField(max_length=100)
    marcaConsola = models.CharField(max_length=100)

    def __str__(self):
        return "{}".format(self.nombreConsola)

#Modelo Estado (si esta activo o descontinuado )

class Estado(models.Model):
    idEstado = models.IntegerField(primary_key=True,default=None)
    nombreEstado = models.CharField(max_length=100)

    def __str__(self):
        return "{}".format(self.nombreEstado) 

#Modelo Distribucion (si es distriucion europea americana o global)

class Distribucion(models.Model):
    
    idDistribucion = models.IntegerField(primary_key=True, default=None)
    localidadDistribucion = models.CharField(max_length=80)
    siglaDistribucion = models.CharField(max_length=5)

    def __str__(self):
        return "{}".format(self.siglaDistribucion+" : "+self.localidadDistribucion)

#modelo Clasificaion, el pegi

class Clasificacion(models.Model):
    idClasificacion = models.IntegerField(primary_key=True,default=None)
    distribucion = models.ForeignKey(Distribucion,on_delete=models.CASCADE)
    descripcionClasificacion = models.CharField(max_length=10)

    def __str__(self):
        return "{}".format(self.descripcionClasificacion)
 
#modelos Descripcion
class Descripcion(models.Model):
    idDescripcion = (models.IntegerField(primary_key=True,default=None))
    detallesDescripcion= models.CharField(max_length=100)

    def __str__(self):
        return self.detallesDescripcion

#modelo Juego
class Juego(models.Model):
    
    codigoDeBarra = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombreJuego = models.CharField(max_length=250)
    consola = models.ForeignKey(Consola, on_delete=models.CASCADE)
    distribucion = models.ForeignKey(Distribucion, on_delete=models.CASCADE)
    clasificacion = models.ForeignKey(Clasificacion, on_delete=models.CASCADE)
    descripcion = models.ForeignKey(Descripcion, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='juegos/')

    @property
    def stock_total(self):
        from .models import Stock
        return Stock.objects.filter(juego=self).aggregate(total=models.Sum('cantidad'))['total'] or 0

    def __str__(self):
        return self.nombreJuego   

#modelos Stock (relaciona una ubicacion con una cantidad)
         
class Stock(models.Model):
    idStock = models.AutoField(primary_key=True)
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE, related_name='stocks')
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)

    class Meta:
        unique_together = ['juego', 'ubicacion']

    def __str__(self):
        return f"{self.juego.nombreJuego} en {self.ubicacion.nombreUbicacion} - {self.cantidad} unidades"