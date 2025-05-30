from multiprocessing import context
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .forms import PersonalForm, RolForm, ConsolaForm, UbicacionForm, JuegoForm, ModificarJuegoForm
from .models import Personal, Consola, Ubicacion, Juego, Stock, Rol, Estado, Distribucion, Clasificacion
import os


def crear_personal(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_usuarios')  # Asegúrate que esa URL esté definida
    else:
        form = PersonalForm()

    usuario_logeado = Personal.objects.get(usuario=request.user)
    
    data_user = {
        'is_authenticated': True,
        'role': usuario_logeado.rol.rol,
        'get_full_name': usuario_logeado.nombre,
        'username' : usuario_logeado.usuario
    }

    return render(request, 'Registros/crear_personal.html', 
                  {'form': form, 'user':data_user})

def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RolForm()
    return render(request, 'Registros/crear_rol.html', {'form': form})


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def gestion_usuarios(request):
    usuarios_data = []

    for user in User.objects.all():
        try:
            personal = Personal.objects.get(usuario=user)
            usuarios_data.append({
                'nombre': personal.nombre,
                'rol': personal.rol.rol,
                'usuario': user.username,
                'telefono': personal.telefono,
                'estado': user.is_active,
                'ultimo_ingreso': user.last_login,
            })
        except Personal.DoesNotExist:
            continue
    
    usuario_logeado = Personal.objects.get(usuario=request.user)
    
    data_user = {
        'is_authenticated': True,
        'role': usuario_logeado.rol.rol,
        'get_full_name': usuario_logeado.nombre,
        'username' : usuario_logeado.usuario
    }

    return render(request, 'usuarios/gestion_usuarios.html', {
        'usuarios': usuarios_data,
        'user': data_user
    })

# Vista para registrar nuevas consolas
def registrar_consola(request):
    if request.method == 'POST':
        form = ConsolaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La consola se ha registrado correctamente.")
            return redirect('registrar_consola')
    else:
        form = ConsolaForm()
    return render(request, 'Registros/registrar_consolas.html', {'form': form})


# Vista para listar consolas
def lista_consolas(request):
    consolas = Consola.objects.all()
    return render(request, 'consolas/lista.html', {'consolas': consolas})

# Vista para registrar nuevas ubicación
def registrar_ubicacion(request):
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ubicaciones')
    else:
        form = UbicacionForm()
    return render(request, 'Registros/registrar_ubicaciones.html', {'form': form})

# Vista para listar ubicaciones
def lista_ubicaciones(request):
    ubicaciones = Ubicacion.objects.all()
    return render(request, 'ubicaciones/lista.html', {'ubicaciones': ubicaciones})

# Vista para registrar juego
@login_required(login_url='login')
def registrar_juego(request):
    if request.method == 'POST':
        form = JuegoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Juego registrado exitosamente.')
            return redirect('lista_juegos')
        else:
            messages.error(request, '❌ Error al registrar el juego. Revisa el formulario.') 

    else:
        form = JuegoForm()
    return render(request, 'Registros/registrar_juego.html', {'form': form})
 

# Vista para listar juegos
def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos/lista_con_stock.html', {'juegos': juegos})


def editar_juego(request, pk):
    juego = get_object_or_404(Juego, pk=pk)
    
    if request.method == 'POST':
        form = JuegoForm(request.POST, request.FILES, instance=juego)
        if form.is_valid():
            form.save()
            return redirect('lista_juegos_con_stock')
    else:
        form = JuegoForm(instance=juego)
    
    return render(request, 'Editar/editar_juego.html', {
        'form': form,
        'juego': juego
    })
    

def listar_juegos_con_stock(request):
    # Obtener parámetros de filtrado
    search_query = request.GET.get('search', '')
    consola_id = request.GET.get('consola')
    estado_id = request.GET.get('estado')
    
    # Obtener todos los juegos con sus relaciones
    juegos_list = Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado', 'unidades', 'ubicacion'
    ).all().order_by('nombreJuego')
    
    # Aplicar filtros
    if search_query:
        juegos_list = juegos_list.filter(nombreJuego__icontains=search_query)
    
    if consola_id:
        juegos_list = juegos_list.filter(consola__id=consola_id)
    
    if estado_id:
        juegos_list = juegos_list.filter(estado__id=estado_id)
    
    # Paginación
    paginator = Paginator(juegos_list, 25)  # 25 juegos por página
    page_number = request.GET.get('page')
    juegos = paginator.get_page(page_number)
    
    # Obtener datos para los filtros
    consolas = Consola.objects.all()
    estados = Estado.objects.all()
    
    context = {
        'juegos': juegos,
        'consolas': consolas,
        'estados': estados,
        'titulo': 'Listado de Juegos con Stock'
    }
    return render(request, 'Editar/lista_juegos_con_stock.html', context)

@login_required(login_url='login')
def principal(request):
    return render(request, 'principal/index.html')

def detalle_juego(request, pk):
    juego = get_object_or_404(Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado', 'unidades', 'ubicacion'
    ), pk=pk)
    return render(request, 'Editar/detalle_juego.html', {'juego': juego})

def eliminar_juego(request, pk):
    juego = get_object_or_404(Juego, pk=pk)
    if request.method == 'POST':
        juego.delete()
        messages.success(request, 'Juego eliminado correctamente')
        return redirect('listar_juegos_con_stock')
    
    return render(request, 'Editar/confirmar_eliminacion.html', {'juego': juego})

def buscar_juego(request):
    search = request.GET.get('search', '')
    juegos = Juego.objects.filter(nombreJuego__icontains=search)
    return render(request, 'juegos/buscar.html', {'juegos': juegos})

def buscar_juego_ubicacion(request):
    ubicacion = request.GET.get('ubicacion', '')
    juegos = Juego.objects.filter(ubicacion__nombreUbicacion__icontains=ubicacion)
    return render(request, 'juegos/buscar_ubicacion.html', {'juegos': juegos})

def buscar_juego_consola(request):
    consola = request.GET.get('consola', '')
    juegos = Juego.objects.filter(consola__nombreConsola__icontains=consola)
    return render(request, 'juegos/buscar_consola.html', {'juegos': juegos})


def buscar_juego_rol(request):
    rol = request.GET.get('rol', '')
    juegos = Juego.objects.filter(rol__nombreRol__icontains=rol)
    return render(request, 'juegos/buscar_rol.html', {'juegos': juegos})

def lista_juegos_con_stock(request):
    juegos = Juego.objects.all()
    consolas = Consola.objects.all()
    distribuciones = Distribucion.objects.all()
    clasificaciones = Clasificacion.objects.all()
    estados = Estado.objects.all()
    ubicaciones = Ubicacion.objects.all()
    context = {
        'juegos': juegos,
        'consolas': consolas,
        'distribuciones': distribuciones,
        'clasificaciones': clasificaciones,
        'estados': estados,
        'ubicaciones': ubicaciones,
        'titulo': 'Listado de Juegos con Stock'
    }
    return render(request, 'juegos/lista_con_stock.html', context)


def modificar_juego(request, juego_id):
    juego = get_object_or_404(Juego, pk=juego_id)
    
    if request.method == 'POST':
        form = ModificarJuegoForm(request.POST, instance=juego)
        if form.is_valid():
            form.save()
            return redirect('lista_juegos_con_stock')  # manda a la lista de juegos
    else:
        form = ModificarJuegoForm(instance=juego)
    
    return render(request, 'juegos/modificar_juego.html', {
        'form': form,
        'juego': juego
    })

def obtener_clasificaciones(request):
    distribucion_id = request.GET.get('distribucion_id')
    clasificaciones = Clasificacion.objects.filter(distribucion_id=distribucion_id).values('idClasificacion', 'descripcionClasificacion')
    return JsonResponse(list(clasificaciones), safe=False)

