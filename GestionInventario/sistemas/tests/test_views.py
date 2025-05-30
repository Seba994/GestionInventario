from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from sistemas.models import Personal, Rol, Consola, Juego, Ubicacion, Estado, Distribucion, Clasificacion, Stock
from sistemas.forms import JuegoForm, PersonalForm

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear rol
        self.rol = Rol.objects.create(
            rol='Administrador'
        )
        
        # Crear personal 
        self.personal = Personal.objects.create(
            nombre='Test User',
            usuario=self.user,
            rol=self.rol,
            telefono='123456789'
        )
        
        # Crear consola
        self.consola = Consola.objects.create(
            idConsola=1,
            nombreConsola='PlayStation 5',
            marcaConsola='Sony' 
        )
        
        # Crear ubicación
        self.ubicacion = Ubicacion.objects.create(
            idUbicacion=1,
            nombreUbicacion='Almacén Principal',
            descripcionUbicacion='Ubicación de prueba' 
        )
        
        # Crear estado
        self.estado = Estado.objects.create(
            idEstado=1,
            nombreEstado='Disponible'
        )
        
        # Crear distribución
        self.distribucion = Distribucion.objects.create(
            idDistribucion=1,
            localidadDistribucion='Europa',
            siglaDistribucion='EUR'  
        )
        
        # Crear clasificación
        self.clasificacion = Clasificacion.objects.create(
            idClasificacion=1,
            descripcionClasificacion='Acción',
            distribucion=self.distribucion
        )
        
        # Crear juego
        self.juego = Juego.objects.create(
            nombreJuego='Test Game',
            consola=self.consola,
            estado=self.estado,
            distribucion=self.distribucion,
            clasificacion=self.clasificacion,
            codigoDeBarra='123456789' 
        )

        self.stock = Stock.objects.create(
            idStock=1,
            juego=self.juego,
            ubicacion=self.ubicacion,
            cantidad=10
        )

    def test_lista_consolas(self):
        """Test vista lista_consolas"""
        url = reverse('lista_consolas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'consolas/lista.html')

    def test_registrar_ubicacion(self):
        """Test vista registrar_ubicacion"""
        url = reverse('registrar_ubicacion')
        data = {
            'nombreUbicacion': 'Nueva Ubicación'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertTrue(Ubicacion.objects.filter(nombreUbicacion='Nueva Ubicación').exists())

    def test_lista_ubicaciones(self):
        """Test vista lista_ubicaciones"""
        url = reverse('lista_ubicaciones') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ubicaciones/lista.html')

    def test_buscar_juego_consola(self):
        """Test vista buscar_consola"""
        url = reverse('buscar_consola')
        response = self.client.get(url, {'consola': 'PlayStation'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'juegos/buscar_consola.html')
        
    def test_detalle_juego(self):
        """Test vista detalle_juego"""
        url = reverse('detalle_juego', args=[self.juego.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Editar/detalle_juego.html')

    def test_editar_juego_post(self):
        """Test editar juego con POST"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('editar_juego', args=[self.juego.pk])
        data = {
            'nombreJuego': 'Test Game Updated',
            'consola': self.consola.pk,
            'ubicacion': self.ubicacion.pk,
            'estado': self.estado.pk,
            'distribucion': self.distribucion.pk,
            'clasificacion': self.clasificacion.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.juego.refresh_from_db()
        self.assertEqual(self.juego.nombreJuego, 'Test Game Updated')
        
        # Crear ubicación
        self.ubicacion = Ubicacion.objects.create(
            nombreUbicacion='Almacén Principal'
        )
        
        # Crear estado
        self.estado = Estado.objects.create(
            estado='Disponible'
        )
        
        # Crear distribución
        self.distribucion = Distribucion.objects.create(
            descripcionDistribucion='Digital'
        )
        
        # Crear clasificación
        self.clasificacion = Clasificacion.objects.create(
            descripcionClasificacion='Acción',
            distribucion=self.distribucion
        )
        
        # Crear juego
        self.juego = Juego.objects.create(
            nombreJuego='Test Game',
            consola=self.consola,
            ubicacion=self.ubicacion,
            estado=self.estado,
            distribucion=self.distribucion,
            clasificacion=self.clasificacion,
            codigoDeBarra='123456758'
        )

    def test_lista_juegos(self):
        """Test vista lista_juegos"""
        url = reverse('lista_juegos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Editar/lista_juegos_con_stock.html')
        
    def test_crear_personal(self):
        """Test vista crear_personal"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('crear_usuario')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Registros/crear_personal.html')

    def test_registrar_juego(self):
        """Test vista registrar_juego"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('registrar_juego')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Registros/registrar_juego.html')

    def test_editar_juego(self):
        """Test vista editar_juego"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('editar_juego', args=[self.juego.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Editar/editar_juego.html')

    def test_eliminar_juego(self):
        """Test vista eliminar_juego"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('eliminar_juego', args=[self.juego.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirección después de eliminar
        
    def test_buscar_juego(self):
        """Test vista buscar_juego"""
        url = reverse('buscar_juego')
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'juegos/buscar.html')

    def test_buscar_juego_ubicacion(self):
        """Test vista buscar_juego_ubicacion"""
        url = reverse('buscar_juego_ubicacion')
        response = self.client.get(url, {'ubicacion': 'Almacén'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'juegos/buscar_ubicacion.html')

    def test_obtener_clasificaciones(self):
        """Test vista obtener_clasificaciones"""
        url = reverse('ajax_clasificaciones')
        response = self.client.get(url, {'distribucion_id': self.distribucion.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_listar_juegos_con_stock_filtros(self):
        """Test filtros en listar_juegos_con_stock"""
        url = reverse('listar_juegos_con_stock')
        
        # Probar filtro por búsqueda
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        
        # Probar filtro por consola
        response = self.client.get(url, {'consola': self.consola.pk})
        self.assertEqual(response.status_code, 200)
        
        # Probar filtro por estado
        response = self.client.get(url, {'estado': self.estado.pk})
        self.assertEqual(response.status_code, 200)