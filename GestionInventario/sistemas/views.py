from multiprocessing import context
from pyexpat.errors import messages
from re import search
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum, Case, When, IntegerField
from django.db import models
from .forms import PersonalForm, RolForm, ConsolaForm, UbicacionForm, JuegoForm, ModificarJuegoForm, FiltroJuegoForm
from .models import Personal, Consola, Ubicacion, Juego, Stock, Rol, Estado, Distribucion, Clasificacion
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response




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

def agregar_varias_ubicaciones(request):
    if request.method == 'POST':
        nombres = request.POST.getlist('nombreUbicacion[]')
        descripciones = request.POST.getlist('descripcionUbicacion[]')
        
        for nombre, descripcion in zip(nombres, descripciones):
            if nombre.strip():
                Ubicacion.objects.create(
                    nombreUbicacion=nombre.strip(),
                    descripcionUbicacion=descripcion.strip() if descripcion else ''
                )
        messages.success(request, 'Ubicaciones agregadas correctamente.')
        return redirect('lista_ubicaciones')

    return render(request, 'ubicaciones/agregar_varias_ubicaciones.html')

def buscar_ubicaciones(termino):
    if termino:
        return Ubicacion.objects.filter(nombreUbicacion__icontains=termino)
    return Ubicacion.objects.all()

# Vista para listar ubicaciones
def lista_ubicaciones(request):
    termino_busqueda = request.GET.get('search', '')
    ubicaciones = buscar_ubicaciones(termino_busqueda)

    paginator = Paginator(ubicaciones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'ubicaciones': page_obj,
        'page_obj': page_obj,
        'search_term': termino_busqueda,
    }
    return render(request, 'ubicaciones/lista_ubicacion.html', context)

# Vista para registrar juego
@login_required(login_url='login')
def registrar_juego(request):
    if request.method == 'POST':
        form = JuegoForm(request.POST, request.FILES)
        if form.is_valid():
            juego = form.save()
            accion = request.POST.get('action')

            if accion == 'guardar_otro':
                messages.success(request, '✅ Juego registrado exitosamente. Puedes agregar otro.')
                return redirect('registrar_juego')

            elif accion == 'guardar_stock':
                messages.success(request, '✅ Juego registrado. Redirigiendo a gestión de stock.')
                return redirect('gestionar_stock', id=juego.id)

            else:
                messages.success(request, '✅ Juego registrado exitosamente.')
                return redirect('listar_juegos_con_stock')
        else:
            field_labels = {
                'codigoDeBarra': 'Código de Barra',
                'nombreJuego': 'Nombre del Juego',
                'consola': 'Consola',
                'distribucion': 'Distribución',
                'clasificacion': 'Clasificación',
                'descripcion': 'Descripción',
                'imagen': 'Imagen'
            }
            
            for field, errors in form.errors.items():
                field_name = field_labels.get(field, field)
                for error in errors:
                    messages.error(request, f"❌ Error en {field_name}: {error}")

    else:
        form = JuegoForm()

    return render(request, 'Registros/registrar_juego.html', {'form': form})
 

# Vista para listar juegos
def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos/lista_con_stock.html', {'juegos': juegos})


@login_required(login_url='login')
def listar_juegos_con_stock(request):
    # Obtener parámetros de filtrado
    search_query = request.GET.get('search', '')
    consola_id = request.GET.get('consola')
    distribucion_id = request.GET.get('distribucion')
    estado_id = request.GET.get('estado')
    stock_filter = request.GET.get('stock', '')  # empty string by default
    
    # Obtener todos los juegos con sus relaciones y stock calculado
    juegos_list = Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado'
    ).annotate(
        total_stock=Sum('stocks__cantidad', default=0)
    ).order_by('nombreJuego')
    
    # Aplicar filtros
    if search_query:
        juegos_list = juegos_list.filter(
            Q(nombreJuego__icontains=search_query) |
            Q(codigoDeBarra__icontains=search_query)
        )
    
    if consola_id and consola_id.isdigit():
        juegos_list = juegos_list.filter(consola__id=int(consola_id))
    
    if distribucion_id and distribucion_id.isdigit():
        juegos_list = juegos_list.filter(distribucion__id=int(distribucion_id))
    
    if estado_id and estado_id.isdigit():
        juegos_list = juegos_list.filter(estado__id=int(estado_id))
    
    # Filtro por stock
    if stock_filter == 'available':
        juegos_list = juegos_list.filter(total_stock__gt=0)
    elif stock_filter == 'unavailable':
        juegos_list = juegos_list.filter(Q(total_stock__lte=0) | Q(total_stock__isnull=True))
    
    # Paginación
    paginator = Paginator(juegos_list, 25)  # 25 juegos por página
    page_number = request.GET.get('page')
    juegos = paginator.get_page(page_number)
    
    # Obtener datos para los filtros
    consolas = Consola.objects.all()
    distribuciones = Distribucion.objects.all()
    estados = Estado.objects.all()
    
    context = {
        'page_obj': juegos,  # coincidir con el template
        'consolas': consolas,
        'distribuciones': distribuciones,
        'estados': estados,
        'current_filters': {
            'search': search_query,
            'consola': int(consola_id) if consola_id and consola_id.isdigit() else '',
            'distribucion': int(distribucion_id) if distribucion_id and distribucion_id.isdigit() else '',
            'estado': int(estado_id) if estado_id and estado_id.isdigit() else '',
            'stock': stock_filter,
        },
        'titulo': 'Listado de Juegos con Stock'
    }
    return render(request, 'juegos/lista_con_stock.html', context)




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

#def lista_juegos_con_stock(request):
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

#def listar_juegos_con_stock(request):
    # Obtener parámetros de filtrado del GET request
    search = request.GET.get('search', '')
    consola = request.GET.get('consola')
    distribucion = request.GET.get('distribucion')
    clasificacion = request.GET.get('clasificacion')
    estado = request.GET.get('estado')
    stock = request.GET.get('stock', 'all')  # Valor por defecto 'all'

    # Consulta base con annotate para el stock
    juegos = Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado', 'descripcion'
    ).annotate(
        stock_total=Sum('stocks__cantidad')
    ).order_by('nombreJuego')

    # Aplicar filtros
    if search:
        juegos = juegos.filter(
            Q(nombreJuego__icontains=search) |
            Q(codigoDeBarra__icontains=search) |
            Q(descripcion__detallesDescripcion__icontains=search)
        )
    
    if consola:
        juegos = juegos.filter(consola_id=consola)
    
    if distribucion:
        juegos = juegos.filter(distribucion_id=distribucion)
    
    if clasificacion:
        juegos = juegos.filter(clasificacion_id=clasificacion)
    
    if estado:
        juegos = juegos.filter(estado_id=estado)
    
    # Filtro por stock
    if stock == 'available':
        juegos = juegos.filter(stock_total__gt=0)
    elif stock == 'unavailable':
        juegos = juegos.filter(stock_total__lte=0)

    # Paginación
    paginator = Paginator(juegos, 25)  # 25 items por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtener opciones para los selects
    consolas = Consola.objects.all()
    distribuciones = Distribucion.objects.all()
    clasificaciones = Clasificacion.objects.all()
    estados = Estado.objects.all()

    context = {
        'juegos': page_obj,
        'page_obj': page_obj,
        'consolas': consolas,
        'distribuciones': distribuciones,
        'clasificaciones': clasificaciones,
        'estados': estados,
        'current_filters': {
            'search': search,
            'consola': int(consola) if consola else '',
            'distribucion': int(distribucion) if distribucion else '',
            'clasificacion': int(clasificacion) if clasificacion else '',
            'estado': int(estado) if estado else '',
            'stock': stock,
        }
    }
    return render(request, 'juegos/lista_con_stock.html', context)


#def listar_juegos_con_stock(request):
    # Obtener parámetros de filtrado
    search = request.GET.get('search', '')
    consola_id = request.GET.get('consola')
    distribucion_id = request.GET.get('distribucion')
    clasificacion_id = request.GET.get('clasificacion')
    estado_id = request.GET.get('estado')
    stock_filter = request.GET.get('stock', 'all')
    
    # Consulta base con select_related para optimización
    juegos = Juego.objects.select_related(
        'consola', 'distribucion', 'clasificacion', 'estado', 'descripcion'
    ).prefetch_related('stocks').all()

    # Aplicar filtros
    if search:
        juegos = juegos.filter(
            Q(nombreJuego__icontains=search) |
            Q(codigoDeBarra__icontains=search) |
            Q(descripcion__detallesDescripcion__icontains=search)
        )
    
    if consola_id:
        juegos = juegos.filter(consola_id=consola_id)
    
    if distribucion_id:
        juegos = juegos.filter(distribucion_id=distribucion_id)
    
    if clasificacion_id:
        juegos = juegos.filter(clasificacion_id=clasificacion_id)
    
    if estado_id:
        juegos = juegos.filter(estado_id=estado_id)
    
    # Filtro por stock - lo manejamos en Python ya que es una propiedad
    filtered_juegos = []
    for juego in juegos:
        if stock_filter == 'all' or \
           (stock_filter == 'available' and juego.stock_total > 0) or \
           (stock_filter == 'unavailable' and juego.stock_total <= 0):
            filtered_juegos.append(juego)
    
    # Paginación
    paginator = Paginator(filtered_juegos, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'consolas': Consola.objects.all(),
        'distribuciones': Distribucion.objects.all(),
        'clasificaciones': Clasificacion.objects.all(),
        'estados': Estado.objects.all(),
        'current_filters': {
            'search': search,
            'consola': int(consola_id) if consola_id else '',
            'distribucion': int(distribucion_id) if distribucion_id else '',
            'clasificacion': int(clasificacion_id) if clasificacion_id else '',
            'estado': int(estado_id) if estado_id else '',
            'stock': stock_filter,
        }
    }
    return render(request, 'juegos/lista_con_stock.html', context)



#def listar_juegos_con_stock(request):
    search = request.GET.get('search', '')
    consola = request.GET.get('consola')
    distribucion = request.GET.get('distribucion')
    clasificacion = request.GET.get('clasificacion')
    estado = request.GET.get('estado')
    stock_filter = request.GET.get('stock', 'all')

    juegos = Juego.objects.all().prefetch_related('stocks')  # Carga relacionada para eficiencia

    # Aplicar filtros directamente en la queryset
    if search:
        juegos = juegos.filter(
            models.Q(nombreJuego__icontains=search) |
            models.Q(codigoDeBarra__icontains=search) |
            models.Q(descripcion__detallesDescripcion__icontains=search)
        )
    if consola:
        juegos = juegos.filter(consola_id=consola)
    if distribucion:
        juegos = juegos.filter(distribucion_id=distribucion)
    if clasificacion:
        juegos = juegos.filter(clasificacion_id=clasificacion)
    if estado:
        juegos = juegos.filter(estado_id=estado)

    # Filtro por stock (aplicado a la queryset)
    if stock_filter == 'available':
        juegos = juegos.filter(stocks__gt=0) # Asumiendo que stock_total es una propiedad o anotación
    elif stock_filter == 'unavailable':
        juegos = juegos.filter(stocks__lte=0) # Asumiendo que stock_total es una propiedad o anotación

    # Paginación
    paginator = Paginator(juegos, 10)  # 10 juegos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto
    context = {
        'page_obj': page_obj,
        'consolas': Consola.objects.all(),
        'distribuciones': Distribucion.objects.all(),
        'clasificaciones': Clasificacion.objects.all(),
        'estados': Estado.objects.all(),
        'current_filters': {
            'search': search,
            'consola': consola,
            'distribucion': distribucion,
            'clasificacion': clasificacion,
            'estado': estado,
            'stock': stock_filter,
        }
    }

    return render(request, 'juegos/lista_con_stock.html', context)

# views.py
@login_required(login_url='login')

def listar_juegos_con_stock(request):
    # Obtén los filtros y normaliza a string para evitar None
    search = request.GET.get('search', '').strip()
    consola = request.GET.get('consola', '') 
    distribucion = request.GET.get('distribucion', '')
    clasificacion = request.GET.get('clasificacion', '')
    estado = request.GET.get('estado', '')
    stock = request.GET.get('stock', '')
    
    print("URL completa:", request.get_full_path())
    print("GET params:", dict(request.GET))

    juegos = Juego.objects.select_related('consola', 'distribucion', 'clasificacion', 'descripcion', 'estado')

    if search:
        juegos = juegos.filter(
            Q(nombreJuego__icontains=search) |
            Q(codigoDeBarra__icontains=search) |
            Q(descripcion__detallesDescripcion__icontains=search)
        )
    if consola and consola != 'all':
        juegos = juegos.filter(consola_id=consola)

    if distribucion and distribucion != 'all':
        juegos = juegos.filter(distribucion_id=distribucion)

    if clasificacion and clasificacion != 'all':
        juegos = juegos.filter(clasificacion_id=clasificacion)

    if estado and estado != 'all':
        juegos = juegos.filter(estado_id=estado)


    if stock == 'available':
        juegos = juegos.filter(stock_total__gt=0)
    elif stock == 'unavailable':
        juegos = juegos.filter(stock_total=0)

    current_filters = {
        'search': search,
        'consola': consola,
        'distribucion': distribucion,
        'clasificacion': clasificacion,
        'estado': estado,
        'stock': stock,
    }

    paginator = Paginator(juegos.order_by('nombreJuego'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'juegos/lista_con_stock.html', {
        'page_obj': page_obj,
        'consolas': Consola.objects.all(),
        'distribuciones': Distribucion.objects.all(),
        'clasificaciones': Clasificacion.objects.all(),
        'estados': Estado.objects.all(),
        'current_filters': current_filters,
    })





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

@login_required(login_url='login')
def restar_stock(request, juego_id, stock_id):
    stock = get_object_or_404(Stock, idStock=stock_id, juego__id=juego_id)

    if stock.cantidad > 0:
        stock.cantidad -= 1
        stock.save()

        stock_total = obtener_stock_total_juego(juego_id)

        # Espacio reservado: Alerta cuando stock baja a 5
        if stock_total == 5:
            # TODO: Enviar alerta por correo: stock bajo (5 unidades)
            print("ALERTA: El stock total ha bajado a 5 unidades.")
            pass

        # Espacio reservado: Alerta cuando stock baja a 0
        if stock_total == 0:
            # TODO: Enviar alerta por correo: stock agotado (0 unidades)
            print("ALERTA: El stock total ha llegado a 0.")
            pass

        messages.success(request, f'Se ha restado una unidad del stock en {stock.ubicacion.nombreUbicacion}.')
    else:
        messages.warning(request, 'No se puede restar, ya que el stock ya está en 0.')

    return redirect('gestionar_stock', id=juego_id)

def obtener_stock_total_juego(juego_id):
    total = Stock.objects.filter(juego_id=juego_id).aggregate(Sum('cantidad'))['cantidad__sum']
    return total or 0


def editar_ubicacion(request, id):
    ubicacion = get_object_or_404(Ubicacion, idUbicacion=id)

    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            return redirect('lista_ubicaciones')  # Cambia esto si tienes otro nombre en urls.py
    else:
        form = UbicacionForm(instance=ubicacion)

    return render(request, 'ubicaciones/editar_ubicacion.html', {
        'form': form,
        'ubicacion': ubicacion,
        'titulo': 'Editar Ubicación'
    })


def eliminar_ubicacion(request, id):
    ubicacion = get_object_or_404(Ubicacion, pk=id)
    
    # Obtener todos los registros de stock de esta ubicación
    stock_asociado = Stock.objects.filter(ubicacion=ubicacion)
    
    # Verificar si alguno tiene stock mayor a 0
    if any(s.cantidad > 0 for s in stock_asociado):
        messages.error(request, "No se puede eliminar la ubicación porque aún contiene stock.")
        return redirect('lista_ubicaciones')
    
    # Eliminar los registros de stock asociados (todos son 0)
    stock_asociado.delete()
    
    # Eliminar la ubicación
    ubicacion.delete()
    messages.success(request, "Ubicación eliminada correctamente.")
    return redirect('lista_ubicaciones')

def buscar_ubicaciones(termino):
    if termino:
        return Ubicacion.objects.filter(nombreUbicacion__icontains=termino)
    return Ubicacion.objects.all()