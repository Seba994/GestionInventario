"""
URL configuration for GestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sistemas import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('nuevo_usuario/',views.crear_personal, name="crear_usuario"),
    path('nuevo_rol/', views.crear_rol),
    path('usuarios/', views.gestion_usuarios, name="gestion_usuarios"),
    path('usuarios/editar/<int:id>/', views.modificar_usuario, name='modificar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/modificar-rol/<int:id>/', views.modificar_rol, name='modificar_rol_usuario'),
    path('consolas/registrar/', views.registrar_consola, name='registrar_consola'),
    path('consolas/', views.lista_consolas, name='lista_consolas'),
    path('ubicaciones/registrar/', views.registrar_ubicacion, name='registrar_ubicacion'),
    path('ubicaciones/', views.lista_ubicaciones, name='lista_ubicaciones'),
    path('ubicaciones/agregar-multiples/', views.agregar_varias_ubicaciones, name='agregar_varias_ubicaciones'),
    path('ubicaciones/editar/<int:id>/', views.editar_ubicacion, name='editar_ubicacion'),
    path('ubicaciones/eliminar/<int:id>/', views.eliminar_ubicacion, name='eliminar_ubicacion'),
    path('juegos/registrar/', views.registrar_juego, name='registrar_juego'),
    path('juegos/con-stock/', views.listar_juegos_con_stock, name='listar_juegos_con_stock'),
    path('juegos/editar/<int:id>/', views.modificar_juego_id, name='modificar_juego_id'),
    path('juegos/editar/<str:codigoDeBarra>/', views.modificar_juego_codbarra, name='modificar_juego_codbarra'),
    path('juegos/eliminar/<int:pk>/', views.eliminar_juego, name='eliminar_juego'),
    path('juegos/detalle/<int:pk>/', views.detalle_juego, name='detalle_juego'),
    path('juegos/buscar/', views.buscar_juego, name='buscar_juego'),
    path('juegos/buscar-ubicacion/', views.buscar_juego_ubicacion, name='buscar_juego_ubicacion'),
    path('juegos/buscar-consola/', views.buscar_juego_consola, name='buscar_consola'),
    path('juegos/buscar-rol/', views.buscar_juego_rol, name='buscar_juego_rol'),
    path('juegos/gestionar-stock/<int:id>/', views.gestionar_stock, name='gestionar_stock'),
    path('juegos/agregar-stock/<int:juego_id>/', views.agregar_stock, name='agregar_stock'),
    path('juegos/restar-stock/<int:juego_id>/<int:stock_id>/', views.restar_stock, name='restar_stock'),
    path('principal/', views.principal, name='inicio'),
    path('', RedirectView.as_view(url='principal/')),
    path('juegos/', views.lista_juegos, name='lista_juegos'),
    path('ajax/clasificaciones/', views.obtener_clasificaciones, name='ajax_clasificaciones'),
    path('juego/<int:juego_id>/cambiar-ubicacion/', views.cambiar_ubicacion_juego, name='cambiar_ubicacion_juego'),
    path('reportes/movimientos/', views.ver_movimientos_stock, name='movimientos_stock'),
    path('reportes/cambios-juegos/', views.ver_cambios_juegos, name='cambios_juegos'),
    path('reportes/estadisticas/', views.estadisticas_stock, name='estadisticas_stock'),
    path('reportes/movimientos/pdf/', views.generar_pdf_movimientos, name='generar_pdf_movimientos'),
    path('reportes/inventario/pdf/', views.generar_pdf_inventario, name='generar_pdf_inventario'),
    path('eliminar_alerta_stock/<int:juego_id>/', views.eliminar_alerta_stock, name='eliminar_alerta_stock'),



]
