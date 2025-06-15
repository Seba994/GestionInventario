import os
from multiprocessing import context
from pyexpat.errors import messages
from re import search
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import  JsonResponse
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from .forms import PersonalForm, RolForm, ConsolaForm, UbicacionForm, JuegoForm, ModificarJuegoForm
from .models import Personal, Consola, Ubicacion, Juego, Stock, Rol, Estado, Distribucion, Clasificacion, MovimientoStock, CambioJuego
from .forms import  ModificarJuegoForm, ModificarRolUsuarioForm
from .decorators import rol_requerido
from rest_framework.decorators import api_view
from rest_framework.response import Response
from supabase import create_client, Client
from GestionInventario.settings import SUPABASE_URL, SUPABASE_KEY

# Inicializar el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def crear_personal(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Personal creado correctamente.")
            return redirect('gestion_usuarios')  
    
    else:
        form = PersonalForm()

    return render(request, 'Registros/crear_personal.html', 
                  {'form': form})

def crear_rol(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rol creado correctamente.")
            return redirect('gestion_usuarios')  
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
        
        if not form.is_valid():
            # Mostrar errores específicos
            for field in form:
                for error in field.errors:
                    messages.error(request, f'Error en {field.label}: {error}')
            for error in form.non_field_errors():
                messages.error(request, f'Error: {error}')
        
        if form.is_valid():
            try:
                # Si hay imagen, la procesamos
                if 'imagen' in request.FILES:
                    imagen = request.FILES['imagen']
                    nombre = f"{imagen.name}"
                    resultado = upload_image_to_supabase(imagen, nombre)
                    
                    if resultado["success"]:
                        url_imagen = f"https://{SUPABASE_URL.split('//')[1]}/storage/v1/object/public/img-juegos/{nombre}"
                        juego = form.save(commit=False)
                        juego.imagen = url_imagen
                        juego.save()
                    else:
                        messages.error(request, f'❌ Error al subir la imagen: {resultado["error"]}')
                        return render(request, 'Registros/registrar_juego.html', {'form': form})
                else:
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
            
            except Exception as e:
                messages.error(request, f'❌ Error al guardar: {str(e)}')
                print(f"Error: {str(e)}")
    else:
        form = JuegoForm()

    return render(request, 'Registros/registrar_juego.html', {
        'form': form,
        'form_errors': form.errors.items() if hasattr(form, 'errors') else None
    })

  # Vista para listar juegos
def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos/lista_con_stock.html', {'juegos': juegos})

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
        #observacion = request.POST.get('observacion', '')

        if not ubicacion_id or not cantidad:
            messages.error(request, "Debes seleccionar una ubicación y una cantidad.")
        else:
            ubicacion = get_object_or_404(Ubicacion, idUbicacion=ubicacion_id)
            cantidad = int(cantidad)

            # Registrar el movimiento
            MovimientoStock.objects.create(
                juego=juego,
                ubicacion=ubicacion,
                usuario=request.user.personal,
                tipo_movimiento='ENTRADA',
                cantidad=cantidad,
                observacion="Entrada de stock manual"
            )

            # Actualizar stock
            stock, created = Stock.objects.get_or_create(juego=juego, ubicacion=ubicacion)
            stock.cantidad += cantidad
            stock.save()

            messages.success(request, f"Se agregaron {cantidad} unidades al stock.")
            return redirect('gestionar_stock', id=juego.id)

    return render(request, 'Registros/agregar_stock.html', {
        'juego': juego,
        'ubicaciones': ubicaciones
    })

def subir_imagen(request):
    if request.method == 'POST' and request.FILES['imagen']:
        imagen = request.FILES['imagen']
        nombre = f"{imagen.name}"
        resultado = upload_image_to_supabase(imagen, nombre)
        if resultado.get('error') is None:
            return JsonResponse({"url": resultado.get('path')})
        else:
            return JsonResponse({"error": resultado['error']['message']})

#subir imagenes al bucket de supabase
def upload_image_to_supabase(file_obj, file_name, bucket='img-juegos'):
    try:
        # Lee el archivo en memoria
        file_data = file_obj.read()
        file_obj.seek(0)  # Regresa al inicio del archivo
        
        # Sube el archivo a Supabase
        response = supabase.storage.from_(bucket).upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": file_obj.content_type}
        )
        
        # Verifica si la respuesta es exitosa (no lanza excepción)
        return {
            "success": True,
            "path": supabase.storage.from_(bucket).get_public_url(file_name)
        }
        
    except Exception as e:
        print(f"Error al subir imagen: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@login_required(login_url='login')
def restar_stock(request, juego_id, stock_id):
    stock = get_object_or_404(Stock, idStock=stock_id, juego__id=juego_id)

    if stock.cantidad > 0:
        # Registrar el movimiento de salida
        MovimientoStock.objects.create(
            juego=stock.juego,
            ubicacion=stock.ubicacion,
            usuario=request.user.personal,
            tipo_movimiento='SALIDA',
            cantidad=1,  # Se resta una unidad
            observacion='Salida de stock manual'
        )

        # Actualizar el stock
        stock.cantidad -= 1
        stock.save()

        stock_total = obtener_stock_total_juego(juego_id)

        # Alertas de stock bajo
        if stock_total == 5:
            # TODO: Enviar alerta por correo: stock bajo (5 unidades)
            print("ALERTA: El stock total ha bajado a 5 unidades.")
            messages.warning(request, '⚠️ ALERTA: El stock total ha bajado a 5 unidades.')

        if stock_total == 0:
            # TODO: Enviar alerta por correo: stock agotado (0 unidades)
            print("ALERTA: El stock total ha llegado a 0.")
            messages.warning(request, '⚠️ ALERTA: El stock total ha llegado a 0.')

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
            return redirect('lista_ubicaciones') 
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

@login_required(login_url='login')
def ver_movimientos_stock(request):
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo = request.GET.get('tipo')
    juego_id = request.GET.get('juego')

    movimientos = MovimientoStock.objects.select_related('juego', 'ubicacion', 'usuario')

    if fecha_inicio:
        movimientos = movimientos.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        movimientos = movimientos.filter(fecha__lte=fecha_fin)
    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)
    if juego_id:
        movimientos = movimientos.filter(juego_id=juego_id)

    # Estadísticas
    total_entradas = movimientos.filter(tipo_movimiento='ENTRADA').aggregate(
        total=Sum('cantidad'))['total'] or 0
    total_salidas = movimientos.filter(tipo_movimiento='SALIDA').aggregate(
        total=Sum('cantidad'))['total'] or 0

    context = {
        'movimientos': movimientos,
        'total_entradas': total_entradas,
        'total_salidas': total_salidas,
        'juegos': Juego.objects.all(),
    }
    return render(request, 'reportes/movimientos_stock.html', context)

@login_required(login_url='login')
def ver_cambios_juegos(request):
    cambios = CambioJuego.objects.select_related('juego', 'usuario').order_by('-fecha')
    return render(request, 'reportes/cambios_juegos.html', {'cambios': cambios})

@login_required(login_url='login')
def estadisticas_stock(request):
    # Período de tiempo (últimos 30 días por defecto)
    dias = int(request.GET.get('dias', 30))
    fecha_inicio = datetime.now() - timedelta(days=dias)

    # Movimientos por día
    movimientos_diarios = MovimientoStock.objects.filter(
        fecha__gte=fecha_inicio
    ).annotate(
        fecha_dia=TruncDate('fecha')
    ).values('fecha_dia', 'tipo_movimiento').annotate(
        total=Sum('cantidad')
    ).order_by('fecha_dia', 'tipo_movimiento')

    context = {
        'movimientos_diarios': movimientos_diarios,
        'dias_seleccionados': dias,
    }
    return render(request, 'reportes/estadisticas_stock.html', context)
