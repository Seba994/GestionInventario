from multiprocessing import context
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .forms import PersonalForm, RolForm, ConsolaForm, UbicacionForm, JuegoForm, ModificarJuegoForm, ModificarRolUsuarioForm, ModificarPersonalForm
from .models import Personal, Consola, Ubicacion, Juego, Stock, Rol, Estado, Distribucion, Clasificacion
from .decorators import rol_requerido
import os


def crear_personal(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_usuarios')  # Asegúrate que esa URL esté definida
    
    else:
        form = PersonalForm()

    return render(request, 'Registros/crear_personal.html', 
                  {'form': form})

def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RolForm()
    return render(request, 'Registros/crear_rol.html', {'form': form})

@login_required(login_url='login')
@rol_requerido('dueño')  # Solo permite acceso a usuarios con rol "dueño"
def gestion_usuarios(request):
    usuarios_data = []

    for user in User.objects.all():
        try:
            personal = Personal.objects.get(usuario=user)
            usuarios_data.append({
                'id': user.id,           
                'nombre': personal.nombre,
                'rol': personal.rol.rol,
                'usuario': user.username,
                'telefono': personal.telefono,
                'estado': user.is_active,
                'ultimo_ingreso': user.last_login,
            })
        except Personal.DoesNotExist:
            continue

    return render(request, 'usuarios/gestion_usuarios.html', {
        'usuarios': usuarios_data
    })

def modificar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    try:
        personal = Personal.objects.get(usuario=usuario)
    except Personal.DoesNotExist:
        messages.error(request, "El usuario no tiene un perfil asociado.")
        return redirect('gestion_usuarios')

    if request.method == 'POST':
        form = PersonalForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario modificado correctamente.")
            return redirect('gestion_usuarios')
    else:
        form = PersonalForm(instance=personal)

    return render(request, 'Registros/crear_personal.html', {'form': form, 'usuario': usuario})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    try:
        personal = Personal.objects.get(usuario=usuario)
        # Crear un diccionario con la información combinada
        datos_usuario = {
            'id': usuario.id,
            'username': usuario.username,
            'is_active': usuario.is_active,
            'nombre': personal.nombre,
            'telefono': personal.telefono,
            'rol': personal.rol,
            'personal': personal,  # Agregamos el objeto personal completo
            'usuario': usuario     # Agregamos el objeto usuario completo
        }
    except Personal.DoesNotExist:
        messages.error(request, "El usuario no tiene un perfil asociado.")
        return redirect('gestion_usuarios')

    if request.method == 'POST':
        personal.delete()
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('gestion_usuarios')

    return render(request, 'Editar/confirmar_eliminacion_usuario.html', {
        'datos': datos_usuario  # Pasamos el diccionario con todos los datos
    })

def modificar_rol(request, id):
    # Obtener el personal directamente
    personal = get_object_or_404(Personal, usuario_id=id)
    
    if request.method == 'POST':
        form = ModificarRolUsuarioForm(request.POST, instance=personal)
        if form.is_valid():
            form.save()
            messages.success(request, "Rol modificado correctamente.")
            return redirect('gestion_usuarios')
    else:
        form = ModificarRolUsuarioForm(instance=personal)
        # Debugging
        print("Roles disponibles:", list(Rol.objects.all()))
        print("Rol actual:", personal.rol)

    return render(request, 'Registros/modificar_rol.html', {
        'form': form,
        'personal': personal
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
            return redirect('listar_juegos_con_stock')
        else:
            messages.error(request, '❌ Error al registrar el juego. Revisa el formulario.') 

    else:
        form = JuegoForm()
    return render(request, 'Registros/registrar_juego.html', {'form': form})
 

# Vista para listar juegos
def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos/lista_con_stock.html', {'juegos': juegos})


def listar_juegos_con_stock(request):
    # Obtener parámetros de filtrado
    search_query = request.GET.get('search', '')
    consola_id = request.GET.get('consola')
    estado_id = request.GET.get('estado')
    
    # Obtener todos los juegos con sus relaciones
    juegos_list = Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado'
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
    return render(request, 'juegos/lista_juegos_con_stock.html', context)

@login_required(login_url='login')
def principal(request):
    return render(request, 'principal/index.html')

def detalle_juego(request, pk):
    juego = get_object_or_404(Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado'
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
    juegos = []
    
    if ubicacion:
        juegos = Juego.objects.filter(
            stocks__ubicacion__nombreUbicacion__icontains=ubicacion
        ).distinct()
    
    context = {
        'juegos': juegos,
        'busqueda': ubicacion,
        'total_resultados': juegos.count() if ubicacion else 0
    }
    return render(request, 'juegos/buscar_ubicacion.html', context)

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

def modificar_juego_id(request, id):
    juego = get_object_or_404(Juego, id=id)
 
    if request.method == 'POST':
        form = ModificarJuegoForm(request.POST, instance=juego)
        if form.is_valid():
            form.save()
            return redirect('listar_juegos_con_stock')  # manda a la lista de juegos
    else:
        form = ModificarJuegoForm(instance=juego)
    
    return render(request, 'juegos/modificar_juego.html', {
        'form': form,
        'juego': juego
    })

def modificar_juego_codbarra(request, codigoDeBarra):
    # Obtiene el juego por su código de barra
    juego = get_object_or_404(Juego, codigoDeBarra=codigoDeBarra)
    
    if request.method == 'POST':
        form = ModificarJuegoForm(request.POST, instance=juego)
        if form.is_valid():
            form.save()
            return redirect('con_stock')  # manda a la lista de juegos
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

@login_required(login_url='login')
def gestionar_stock(request, id):
    juego = get_object_or_404(Juego, pk=id)
    stocks = Stock.objects.filter(juego=juego)

    return render(request, 'Registros/gestionar_stock.html', {
        'juego': juego,
        'stocks': stocks
    })

@login_required(login_url='login')
def agregar_stock(request, juego_id):
    juego = get_object_or_404(Juego, id=juego_id)
    ubicaciones = Ubicacion.objects.all()

    if request.method == 'POST':
        ubicacion_id = request.POST.get('ubicacion')
        cantidad = request.POST.get('cantidad')

        if not ubicacion_id or not cantidad:
            messages.error(request, "Debes seleccionar una ubicación y una cantidad.")
        else:
            ubicacion = get_object_or_404(Ubicacion, idUbicacion=ubicacion_id)
            cantidad = int(cantidad)

            # Verifica si ya existe un stock para esa ubicación
            stock, created = Stock.objects.get_or_create(juego=juego, ubicacion=ubicacion)
            stock.cantidad += cantidad
            stock.save()

            messages.success(request, f"Se agregaron {cantidad} unidades al stock.")
            return redirect('gestionar_stock', id=juego.id)

    return render(request, 'Registros/agregar_stock.html', {
        'juego': juego,
        'ubicaciones': ubicaciones
    })